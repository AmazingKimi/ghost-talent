from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .scout import scout
from .snapshot import save_snapshot

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WATCHLIST = ROOT / "watchlist.json"


def load_watchlist(path: Path = DEFAULT_WATCHLIST) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("queries", []) if isinstance(payload, dict) else []
    return [row for row in rows if isinstance(row, dict) and row.get("enabled", True) and str(row.get("query", "")).strip()]


async def run_watch(path: Path = DEFAULT_WATCHLIST) -> dict[str, Any]:
    watched = load_watchlist(path)
    report: list[dict[str, Any]] = []
    for item in watched:
        query = str(item["query"]).strip()
        limit = max(1, min(int(item.get("limit", 20)), 20))
        try:
            scout_result = await scout(query, limit=limit)
            results = scout_result["results"]
            snapshot = save_snapshot(ROOT, query, results)
            report.append({
                "query": query,
                "status": "ok",
                "count": len(results),
                "snapshot_id": snapshot["snapshot_id"],
                "observed_at": snapshot["observed_at"],
                "sources": scout_result["sources"],
            })
        except Exception as exc:
            report.append({"query": query, "status": "failed", "error": str(exc)})
    return {
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "watch_count": len(watched),
        "runs": report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Ghost Talent watched queries once and append real history.")
    parser.add_argument("--watchlist", default=str(DEFAULT_WATCHLIST), help="Path to watchlist JSON")
    args = parser.parse_args()
    report = asyncio.run(run_watch(Path(args.watchlist)))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
