from __future__ import annotations

import asyncio
import os
from typing import Any

from .identity import resolve_openalex_identity, stable_subject_id
from .models import Candidate, Evidence
from .scoring import score_candidate
from .sources.github_compat import GitHubSource
from .sources.openalex import OpenAlexSource

RATE_LIMIT_URL = "https://api.github.com/rate_limit"


def _source_status(result: Any) -> dict[str, Any]:
    if not isinstance(result, Exception):
        return {"status": "ok"}
    message = str(result).lower()
    return {
        "status": "rate_limited" if any(x in message for x in ("rate limit", "429", "403")) else "unavailable",
        "detail": str(result),
    }


async def _github_rate_state(github: GitHubSource) -> dict[str, Any]:
    """Read GitHub core/search budget without turning missing telemetry into success."""
    try:
        response = await github.client.get(RATE_LIMIT_URL)
        response.raise_for_status()
        payload = response.json()
        resources = payload.get("resources") or {}
        core = resources.get("core") or {}
        search = resources.get("search") or {}
        return {
            "available": True,
            "authenticated": bool(getattr(github, "authenticated", False)),
            "core_remaining": core.get("remaining"),
            "core_limit": core.get("limit"),
            "core_reset": core.get("reset"),
            "search_remaining": search.get("remaining"),
            "search_limit": search.get("limit"),
        }
    except Exception as exc:
        return {
            "available": False,
            "authenticated": bool(getattr(github, "authenticated", False)),
            "detail": str(exc),
        }


def _github_health(before: dict[str, Any], after: dict[str, Any], result: Any) -> dict[str, Any]:
    status = _source_status(result)
    status.update({"authenticated": bool(after.get("authenticated", before.get("authenticated", False)))})
    if before.get("available"):
        status["core_remaining_before"] = before.get("core_remaining")
        status["search_remaining_before"] = before.get("search_remaining")
    if after.get("available"):
        status["core_remaining_after"] = after.get("core_remaining")
        status["search_remaining_after"] = after.get("search_remaining")

    # GitHubSource intentionally tolerates some inner 403/429 responses. A depleted
    # budget therefore has to be promoted back to a top-level incomplete state.
    remaining = after.get("core_remaining") if after.get("available") else None
    if remaining is not None and int(remaining) <= 0:
        status["status"] = "rate_limited"
        status["detail"] = "GitHub core API quota is exhausted; discovery evidence is incomplete."
    return status


async def scout_preview(query: str, limit: int = 6) -> dict:
    github = GitHubSource(os.getenv("GITHUB_TOKEN"))
    try:
        before = await _github_rate_state(github)
        remaining = before.get("core_remaining") if before.get("available") else None
        if remaining is not None and int(remaining) <= 2:
            return {
                "query": query,
                "count": 0,
                "results": [],
                "complete": False,
                "sources": {"github": {"status": "rate_limited", **before}},
                "error": {
                    "code": "github_rate_limited",
                    "message": "GitHub API quota is exhausted. Configure GITHUB_TOKEN or wait for reset.",
                },
            }
        items = await github.discover(
            query,
            repo_limit=6,
            candidate_limit=max(1, min(limit, 6)),
            contributor_limit=12,
            quality_budget=0,
            pr_repo_budget=0,
        )
        after = await _github_rate_state(github)
        health = _github_health(before, after, items)
        rows = []
        for item in items[:limit]:
            rows.append(
                {
                    "provisional": True,
                    "candidate": {
                        "login": item.get("login"),
                        "name": item.get("name"),
                        "profile_url": item.get("profile_url"),
                        "followers": item.get("followers", 0),
                        "primary_repository": item.get("primary_repository"),
                    },
                    "activity": {
                        "events_7d": item.get("recent_events_7d", 0),
                        "events_30d": item.get("recent_events_30d", 0),
                    },
                    "status": "VALIDATING",
                }
            )
        complete = health.get("status") == "ok"
        return {"query": query, "count": len(rows), "results": rows, "complete": complete, "sources": {"github": health}}
    finally:
        await github.close()


async def scout(query: str, limit: int = 20) -> dict:
    github = GitHubSource(os.getenv("GITHUB_TOKEN"))
    openalex = OpenAlexSource()
    try:
        before = await _github_rate_state(github)
        remaining = before.get("core_remaining") if before.get("available") else None
        if remaining is not None and int(remaining) <= 2:
            return {
                "results": [],
                "sources": {
                    "github": {"status": "rate_limited", **before},
                    "openalex": {"status": "not_run"},
                },
                "complete": False,
                "error": {
                    "code": "github_rate_limited",
                    "message": "GitHub API quota is exhausted. Configure GITHUB_TOKEN or wait for reset.",
                },
            }

        github_result, openalex_result = await asyncio.gather(
            github.discover(query), openalex.works(query), return_exceptions=True
        )
        after = await _github_rate_state(github)
        github_status = _github_health(before, after, github_result)
        openalex_status = _source_status(openalex_result)
        sources = {"github": github_status, "openalex": openalex_status}

        items = [] if isinstance(github_result, Exception) else github_result
        works = [] if isinstance(openalex_result, Exception) else openalex_result
        github_complete = github_status.get("status") == "ok"

        if not github_complete:
            return {
                "results": [],
                "sources": sources,
                "complete": False,
                "error": {
                    "code": "discovery_incomplete",
                    "message": github_status.get("detail") or "GitHub discovery did not complete.",
                },
            }

        # A truly empty healthy search is allowed, but only if quota remains and the
        # top-level GitHub request completed. It will not be confused with rate-limit failure.
        scored = []
        for item in items:
            subject_id = stable_subject_id(item)
            matches = []
            if not isinstance(openalex_result, Exception):
                matches = [
                    {**match, **resolve_openalex_identity(item, match)}
                    for match in openalex.match_author(item.get("name"), works)
                ]

            evidence = []
            for repo in item["repositories"]:
                evidence.append(
                    Evidence(
                        type="repository_contribution",
                        source="github",
                        source_url=repo["url"],
                        subject_id=subject_id,
                        value={
                            "repository": repo["name"],
                            "contributions": repo["contributions"],
                            "stars": repo["stars"],
                            "owner_login": repo.get("owner_login"),
                        },
                    )
                )

            quality = item.get("contribution_quality") or {}
            top = quality.get("top_pr") or {}
            if quality.get("available") and top.get("url"):
                evidence.append(
                    Evidence(
                        type="merged_pull_request",
                        source="github",
                        source_url=top["url"],
                        subject_id=subject_id,
                        observed_at=top.get("merged_or_closed_at"),
                        value={
                            "repository": quality.get("repository"),
                            "number": top.get("number"),
                            "title": top.get("title"),
                            "core_file_count": top.get("core_file_count", 0),
                            "core_files": top.get("core_files", []),
                            "keyword_hits": top.get("keyword_hits", []),
                            "additions": top.get("additions", 0),
                            "deletions": top.get("deletions", 0),
                            "substantive": top.get("substantive", False),
                        },
                    )
                )

            external = item.get("external_validation") or {}
            for pr in external.get("prs", []):
                evidence.append(
                    Evidence(
                        type="external_merged_pull_request",
                        source="github",
                        source_url=pr.get("url") or "",
                        subject_id=subject_id,
                        value=pr,
                    )
                )
            for paper in matches:
                evidence.append(
                    Evidence(
                        type="paper",
                        source="openalex",
                        source_url=paper["url"],
                        subject_id=subject_id,
                        observed_at=paper.get("publication_date"),
                        value={
                            "title": paper["title"],
                            "citations": paper["cited_by_count"],
                            "author": paper["author"],
                            "openalex_author_id": paper.get("openalex_author_id"),
                            "identity_status": paper.get("identity_status"),
                        },
                        confidence=float(paper.get("identity_confidence", 0.35)),
                    )
                )

            identity = {
                "subject_id": subject_id,
                "github_user_id": item.get("github_user_id"),
                "login": item.get("login"),
                "blog": item.get("blog"),
                "company": item.get("company"),
                "location": item.get("location"),
                "cross_source_status": "verified"
                if any(paper.get("identity_status") == "verified_external_link" for paper in matches)
                else "uncertain"
                if matches
                else "github_only",
            }
            candidate = Candidate(
                login=item["login"],
                name=item.get("name"),
                profile_url=item["profile_url"],
                followers=item["followers"],
                repositories=item["repositories"],
                recent_events_7d=item["recent_events_7d"],
                recent_events_30d=item["recent_events_30d"],
                recent_events_90d=item["recent_events_90d"],
                active_days_30d=item["active_days_30d"],
                observed_event_span_days=item["observed_event_span_days"],
                contribution_quality=quality,
                paper_matches=matches,
                evidence=evidence,
                noise=item.get("noise") or {},
                identity=identity,
                external_validation=external,
                momentum_coverage=item.get("momentum_coverage") or {},
            )
            scored.append(score_candidate(candidate))

        scored.sort(
            key=lambda row: (row.get("discovery_priority", 0), row["radar_score"], row["ghost_score"]),
            reverse=True,
        )
        return {
            "results": scored[:limit],
            "sources": sources,
            "complete": True,
            "source_health": {
                "github_authenticated": bool(github_status.get("authenticated")),
                "github_core_remaining": github_status.get("core_remaining_after"),
                "openalex_status": openalex_status.get("status"),
            },
        }
    finally:
        await github.close()
        await openalex.close()
