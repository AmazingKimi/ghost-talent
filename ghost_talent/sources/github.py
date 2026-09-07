from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import httpx


API = "https://api.github.com"
CORE_TERMS = (
    "cuda", "triton", "kernel", "kernels", "compiler", "inference", "attention",
    "gemm", "moe", "quant", "quantization", "nvfp", "fp8", "int8", "runtime",
    "backend", "gpu", "csrc", "ops", "benchmark", "benchmarks",
)
_CACHE: dict[str, tuple[float, object]] = {}
_CACHE_TTL_SECONDS = 300


class GitHubSource:
    def __init__(self, token: str | None = None) -> None:
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.authenticated = bool(token)
        self.client = httpx.AsyncClient(headers=headers, timeout=20.0)
        self._semaphore = asyncio.Semaphore(6)

    async def close(self) -> None:
        await self.client.aclose()

    async def _get(self, url: str, **params):
        key = f"{url}?{sorted(params.items())}"
        cached = _CACHE.get(key)
        now = time.monotonic()
        if cached and now - cached[0] < _CACHE_TTL_SECONDS:
            return cached[1]
        async with self._semaphore:
            response = await self.client.get(url, params=params or None)
            response.raise_for_status()
            data = response.json()
        _CACHE[key] = (now, data)
        return data

    @staticmethod
    def _candidate(candidates: dict[str, dict], login: str, profile_url: str | None = None) -> dict:
        item = candidates[login]
        item["login"] = login
        item["profile_url"] = profile_url or item.get("profile_url") or f"https://github.com/{login}"
        item.setdefault("repositories", [])
        item.setdefault("discovery_sources", [])
        item.setdefault("merged_pr_discoveries", [])
        return item

    @staticmethod
    def _primary_repo(item: dict) -> str:
        repositories = item.get("repositories", [])
        if not repositories:
            return "unknown"
        return max(
            repositories,
            key=lambda repo: (
                int(repo.get("contributions", 0)),
                int(repo.get("stars", 0)),
            ),
        ).get("name", "unknown")

    @classmethod
    def _diversify(cls, ranked: list[dict], limit: int, max_per_repo: int) -> list[dict]:
        selected: list[dict] = []
        overflow: list[dict] = []
        repo_counts: dict[str, int] = defaultdict(int)

        for item in ranked:
            primary = cls._primary_repo(item)
            if repo_counts[primary] < max_per_repo:
                selected.append(item)
                repo_counts[primary] += 1
            else:
                overflow.append(item)
            if len(selected) >= limit:
                return selected

        # If the query genuinely has too few distinct repositories, fill remaining
        # slots from the original ranking rather than returning fewer candidates.
        for item in overflow:
            selected.append(item)
            if len(selected) >= limit:
                break
        return selected

    async def discover(
        self,
        query: str,
        repo_limit: int = 15,
        candidate_limit: int = 20,
        contributor_limit: int = 25,
        quality_budget: int = 12,
        pr_repo_budget: int = 10,
        pr_limit: int = 20,
    ) -> list[dict]:
        """Wide Scout with bounded concurrency, caching, and repository diversity."""
        search = await self._get(
            f"{API}/search/repositories", q=query, sort="stars", order="desc", per_page=repo_limit,
        )
        repositories = search.get("items", [])
        candidates: dict[str, dict] = defaultdict(dict)

        async def load_contributors(repo: dict):
            try:
                rows = await self._get(repo["contributors_url"], per_page=contributor_limit)
                return repo, rows
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in {403, 404, 429}:
                    return repo, []
                raise

        contributor_results = await asyncio.gather(*(load_contributors(repo) for repo in repositories))
        for repo, contributors in contributor_results:
            for contributor in contributors:
                if contributor.get("type") != "User":
                    continue
                login = contributor["login"]
                item = self._candidate(candidates, login, contributor.get("html_url"))
                if "contributors" not in item["discovery_sources"]:
                    item["discovery_sources"].append("contributors")
                item["repositories"].append({
                    "name": repo["full_name"], "url": repo["html_url"],
                    "stars": repo.get("stargazers_count", 0),
                    "contributions": contributor.get("contributions", 0),
                })

        async def load_pulls(repo: dict):
            try:
                rows = await self._get(
                    f"{API}/repos/{repo['full_name']}/pulls", state="closed", sort="updated",
                    direction="desc", per_page=pr_limit,
                )
                return repo, rows
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in {403, 404, 429}:
                    return repo, []
                raise

        if self.authenticated:
            pull_results = await asyncio.gather(*(load_pulls(repo) for repo in repositories[:pr_repo_budget]))
            for repo, pulls in pull_results:
                for pull in pulls:
                    if not pull.get("merged_at"):
                        continue
                    user = pull.get("user") or {}
                    login = user.get("login")
                    if not login or user.get("type") == "Bot" or login.endswith("[bot]"):
                        continue
                    item = self._candidate(candidates, login, user.get("html_url"))
                    if "merged_pr_author" not in item["discovery_sources"]:
                        item["discovery_sources"].append("merged_pr_author")
                    item["merged_pr_discoveries"].append({
                        "repository": repo["full_name"], "repository_url": repo["html_url"],
                        "repository_stars": repo.get("stargazers_count", 0), "number": pull.get("number"),
                        "title": pull.get("title"), "url": pull.get("html_url"), "merged_at": pull.get("merged_at"),
                    })
                    if not any(r["name"] == repo["full_name"] for r in item["repositories"]):
                        item["repositories"].append({
                            "name": repo["full_name"], "url": repo["html_url"],
                            "stars": repo.get("stargazers_count", 0), "contributions": 0,
                        })

        raw_ranked = sorted(
            candidates.values(),
            key=lambda c: (
                len(c.get("merged_pr_discoveries", [])) > 0,
                sum(r["contributions"] for r in c.get("repositories", [])),
                len(c.get("repositories", [])),
                sum(r["stars"] for r in c.get("repositories", [])),
            ), reverse=True,
        )

        # For a Top 20, no single primary repository should normally occupy more
        # than four slots. We retain overflow only if diversity is genuinely scarce.
        max_per_repo = max(2, candidate_limit // 5)
        ranked = self._diversify(raw_ranked, candidate_limit, max_per_repo)

        async def enrich(index: int, item: dict) -> dict:
            profile = None
            events: list[dict] = []
            try:
                profile, events = await asyncio.gather(
                    self._get(f"{API}/users/{item['login']}"),
                    self._get(f"{API}/users/{item['login']}/events/public", per_page=100),
                )
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in {403, 404, 429}:
                    raise
            counts = self._event_counts(events)
            quality = self._empty_quality()
            if self.authenticated and index < quality_budget:
                quality = await self._contribution_quality(item)
            return {
                **item,
                "primary_repository": self._primary_repo(item),
                "name": profile.get("name") if profile else None,
                "profile_url": profile.get("html_url") if profile else item["profile_url"],
                "followers": profile.get("followers", 0) if profile else 0,
                "github_enrichment_complete": profile is not None,
                "contribution_quality": quality,
                **counts,
            }

        return await asyncio.gather(*(enrich(index, item) for index, item in enumerate(ranked)))

    async def _contribution_quality(self, item: dict) -> dict:
        repositories = sorted(item.get("repositories", []), key=lambda repo: int(repo.get("contributions", 0)), reverse=True)
        if not repositories:
            return self._empty_quality()
        repo = repositories[0]
        repo_name = repo["name"]
        login = item["login"]
        try:
            search = await self._get(
                f"{API}/search/issues", q=f"repo:{repo_name} author:{login} type:pr is:merged",
                sort="updated", order="desc", per_page=3,
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {403, 422, 429}:
                return self._empty_quality(repo_name)
            raise
        prs = search.get("items", [])[:3]
        if not prs:
            return self._empty_quality(repo_name)
        top_pr = prs[0]
        files: list[dict] = []
        try:
            files = await self._get(f"{API}/repos/{repo_name}/pulls/{top_pr['number']}/files", per_page=30)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in {403, 404, 429}:
                raise
        filenames = [str(file.get("filename", "")) for file in files]
        core_files = [name for name in filenames if self._is_core_path(name)]
        title = str(top_pr.get("title") or "")
        keyword_hits = sorted({term for term in CORE_TERMS if term in title.lower() or any(term in name.lower() for name in filenames)})
        return {
            "available": True, "repository": repo_name,
            "merged_pr_count": int(search.get("total_count", len(prs))), "sampled_pr_count": len(prs),
            "top_pr": {
                "number": top_pr.get("number"), "title": title, "url": top_pr.get("html_url"),
                "merged_or_closed_at": top_pr.get("closed_at"), "changed_files_sampled": len(files),
                "core_files": core_files[:8], "core_file_count": len(core_files), "keyword_hits": keyword_hits,
                "additions": sum(int(file.get("additions", 0)) for file in files),
                "deletions": sum(int(file.get("deletions", 0)) for file in files),
            },
        }

    @staticmethod
    def _is_core_path(filename: str) -> bool:
        lower = filename.lower()
        return any(term in lower for term in CORE_TERMS) or lower.endswith((".cu", ".cuh", ".cc", ".cpp"))

    @staticmethod
    def _empty_quality(repository: str | None = None) -> dict:
        return {"available": False, "repository": repository, "merged_pr_count": 0, "sampled_pr_count": 0, "top_pr": None}

    @staticmethod
    def _event_counts(events: list[dict]) -> dict[str, int | float]:
        now = datetime.now(timezone.utc)
        d7, d30, d90 = now - timedelta(days=7), now - timedelta(days=30), now - timedelta(days=90)
        count_7 = count_30 = count_90 = 0
        active_days_30: set[str] = set()
        timestamps: list[datetime] = []
        for event in events:
            created = event.get("created_at")
            if not created:
                continue
            ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
            timestamps.append(ts)
            if ts >= d90: count_90 += 1
            if ts >= d30:
                count_30 += 1
                active_days_30.add(ts.date().isoformat())
            if ts >= d7: count_7 += 1
        span_days = 0.0
        if len(timestamps) >= 2:
            span_days = max((max(timestamps) - min(timestamps)).total_seconds() / 86400.0, 0.0)
        return {
            "recent_events_7d": count_7, "recent_events_30d": count_30, "recent_events_90d": count_90,
            "active_days_30d": len(active_days_30), "observed_event_span_days": round(span_days, 2),
        }
