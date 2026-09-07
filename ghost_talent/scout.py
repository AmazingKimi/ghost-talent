from __future__ import annotations

import os

from .models import Candidate, Evidence
from .scoring import score_candidate
from .sources.github import GitHubSource
from .sources.openalex import OpenAlexSource


async def scout(query: str, limit: int = 20) -> list[dict]:
    github = GitHubSource(os.getenv("GITHUB_TOKEN"))
    openalex = OpenAlexSource()
    try:
        github_candidates = await github.discover(query)
        works = await openalex.works(query)

        scored = []
        for item in github_candidates:
            paper_matches = openalex.match_author(item.get("name"), works)
            evidence = []

            for repo in item["repositories"]:
                evidence.append(
                    Evidence(
                        type="repository_contribution",
                        source="github",
                        source_url=repo["url"],
                        value={
                            "repository": repo["name"],
                            "contributions": repo["contributions"],
                            "stars": repo["stars"],
                        },
                    )
                )

            for paper in paper_matches:
                evidence.append(
                    Evidence(
                        type="paper",
                        source="openalex",
                        source_url=paper["url"],
                        observed_at=paper.get("publication_date"),
                        value={
                            "title": paper["title"],
                            "citations": paper["cited_by_count"],
                            "author": paper["author"],
                        },
                        confidence=0.8,
                    )
                )

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
                paper_matches=paper_matches,
                evidence=evidence,
            )
            scored.append(score_candidate(candidate))

        scored.sort(key=lambda row: row["ghost_score"], reverse=True)
        return scored[:limit]
    finally:
        await github.close()
        await openalex.close()
