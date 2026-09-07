from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

import httpx


API = "https://api.github.com"


class GitHubSource:
    def __init__(self, token: str | None = None) -> None:
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.client = httpx.AsyncClient(headers=headers, timeout=20.0)

    async def close(self) -> None:
        await self.client.aclose()

    async def _get(self, url: str, **params):
        response = await self.client.get(url, params=params or None)
        response.raise_for_status()
        return response.json()

    async def discover(self, query: str, repo_limit: int = 5, candidate_limit: int = 8) -> list[dict]:
        search = await self._get(
            f"{API}/search/repositories",
            q=query,
            sort="stars",
            order="desc",
            per_page=repo_limit,
        )

        candidates: dict[str, dict] = defaultdict(lambda: {"repositories": []})
        for repo in search.get("items", []):
            try:
                contributors = await self._get(repo["contributors_url"], per_page=15)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in {403, 429}:
                    break
                raise

            for contributor in contributors:
                if contributor.get("type") != "User":
                    continue
                login = contributor["login"]
                candidates[login]["login"] = login
                candidates[login]["profile_url"] = contributor.get("html_url") or f"https://github.com/{login}"
                candidates[login]["repositories"].append(
                    {
                        "name": repo["full_name"],
                        "url": repo["html_url"],
                        "stars": repo.get("stargazers_count", 0),
                        "contributions": contributor.get("contributions", 0),
                    }
                )

        ranked = sorted(
            candidates.values(),
            key=lambda c: sum(r["contributions"] for r in c["repositories"]),
            reverse=True,
        )[:candidate_limit]

        enriched = []
        rate_limited = False
        for item in ranked:
            profile = None
            events: list[dict] = []

            if not rate_limited:
                try:
                    profile = await self._get(f"{API}/users/{item['login']}")
                    events = await self._get(f"{API}/users/{item['login']}/events/public", per_page=100)
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code in {403, 429}:
                        rate_limited = True
                    else:
                        raise

            counts = self._event_counts(events)
            enriched.append(
                {
                    **item,
                    "name": profile.get("name") if profile else None,
                    "profile_url": profile.get("html_url") if profile else item["profile_url"],
                    "followers": profile.get("followers", 0) if profile else 0,
                    "github_enrichment_complete": profile is not None,
                    **counts,
                }
            )
        return enriched

    @staticmethod
    def _event_counts(events: list[dict]) -> dict[str, int | float]:
        now = datetime.now(timezone.utc)
        d7 = now - timedelta(days=7)
        d30 = now - timedelta(days=30)
        d90 = now - timedelta(days=90)
        count_7 = 0
        count_30 = 0
        count_90 = 0
        active_days_30: set[str] = set()
        timestamps: list[datetime] = []

        for event in events:
            created = event.get("created_at")
            if not created:
                continue
            ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
            timestamps.append(ts)
            if ts >= d90:
                count_90 += 1
            if ts >= d30:
                count_30 += 1
                active_days_30.add(ts.date().isoformat())
            if ts >= d7:
                count_7 += 1

        span_days = 0.0
        if len(timestamps) >= 2:
            newest = max(timestamps)
            oldest = min(timestamps)
            span_days = max((newest - oldest).total_seconds() / 86400.0, 0.0)

        return {
            "recent_events_7d": count_7,
            "recent_events_30d": count_30,
            "recent_events_90d": count_90,
            "active_days_30d": len(active_days_30),
            "observed_event_span_days": round(span_days, 2),
        }
