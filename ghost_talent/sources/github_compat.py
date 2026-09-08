from __future__ import annotations

import asyncio
import time

import httpx

from ..github_auth import load_connected_token
from .github import GitHubSource as _BaseGitHubSource, _CACHE


class GitHubSource(_BaseGitHubSource):
    def __init__(self, token: str | None = None):
        # Environment GITHUB_TOKEN remains supported, but the normal product path
        # is the locally connected GitHub account stored outside the repository.
        super().__init__(token or load_connected_token())

    @staticmethod
    def _empty_response_value(url: str):
        if "/search/" in url:
            return {}
        if "/users/" in url and not url.endswith("/events/public"):
            return {}
        return []

    async def _get(self, url: str, **params):
        key = f"{url}?{sorted(params.items())}"
        cached = _CACHE.get(key)
        now = time.monotonic()
        if cached and now - cached[0] < 300:
            return cached[1]

        last_error = None
        for attempt in range(3):
            try:
                async with self._semaphore:
                    response = await self.client.get(url, params=params or None)
                    response.raise_for_status()
                if response.status_code == 204:
                    data = self._empty_response_value(url)
                    _CACHE[key] = (time.monotonic(), data)
                    return data
                if not response.text.strip():
                    raise ValueError("empty response body")
                data = response.json()
                _CACHE[key] = (time.monotonic(), data)
                return data
            except httpx.HTTPStatusError:
                raise
            except (httpx.TransportError, ValueError) as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(1.5 * (attempt + 1))
                    continue
                detail = (
                    f" status={response.status_code}"
                    f" content_type={response.headers.get('content-type', '')}"
                    f" body_prefix={response.text[:120]!r}"
                ) if 'response' in locals() else ""
                raise RuntimeError(
                    f"GitHub transient/non-JSON response after 3 attempts:{detail} error={exc}"
                ) from exc
        raise RuntimeError(f"GitHub request failed: {last_error}")
