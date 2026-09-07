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

    async def discover(self, query: str, repo_limit: int = 8, candidate_limit: int = 30) -> list[dict]:
        search = await self._get(
            f"{API}/search/repositories",
            q=query,
            sort="stars",
            order="desc",
            per_page=repo_limit,
        )

        candidates: dict[str, dict] = defaultdict(lambda: {"repositories": []})
        for repo in search.get("items", []):
            contributors = await self._get(repo["contributors_url"], per_page=20)
            for contributor in contributors:
                if contributor.get("type") != "User":
                    continue
                login = contributor["login"]
                candidates[login]["login"] = login
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
        for item in ranked:
            profile = await self._get(f"{API}/users/{item['login']}")
            events = await self._get(f"{API}/users/{item['login']}/events/public", per_page=100)
            counts = self._event_counts(events)
            enriched.append(
                {
                    **item,
                    "name": profile.get("name"),
                    "profile_url": profile["html_url"],
                    "followers": profile.get("followers", 0),
                    **counts,
                }
            )
        return enriched

    @staticmethod
    def _event_counts(events: list[dict]) -> dict[str, int]:
        now = datetime.now(timezone.utc)
        d30 = now - timedelta(days=30)
        d90 = now - timedelta(days=90)
        count_30 = 0
        count_90 = 0
        for event in events:
            created = event.get("created_at")
            if not created:
                continue
            ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if ts >= d90:
                count_90 += 1
            if ts >= d30:
                count_30 += 1
        return {"recent_events_30d": count_30, "recent_events_90d": count_90}
