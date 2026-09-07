from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SNAPSHOT_SCHEMA_VERSION = "0.1"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "query"


def save_snapshot(root: Path, query: str, results: list[dict[str, Any]]) -> dict[str, str]:
    observed = datetime.now(timezone.utc)
    observed_at = observed.isoformat().replace("+00:00", "Z")
    query_slug = _slugify(query)
    fingerprint = hashlib.sha256(f"{query}|{observed_at}".encode("utf-8")).hexdigest()[:8]
    snapshot_id = f"{observed.strftime('%Y%m%dT%H%M%S%fZ')}-{fingerprint}"

    directory = root / "snapshots" / observed.strftime("%Y-%m-%d") / query_slug
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{snapshot_id}.json"

    payload = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "snapshot_id": snapshot_id,
        "observed_at": observed_at,
        "query": query,
        "query_slug": query_slug,
        "count": len(results),
        "score_versions": sorted({str(row.get("score_version", "unknown")) for row in results}),
        "ranking": [
            {
                "rank": index,
                "login": row.get("candidate", {}).get("login"),
                "name": row.get("candidate", {}).get("name"),
                "ghost_score": row.get("ghost_score"),
                "capability": row.get("capability"),
                "momentum": row.get("momentum"),
                "visibility_gap": row.get("visibility_gap"),
                "evidence_confidence": row.get("evidence_confidence"),
                "trend": row.get("trend"),
                "score_version": row.get("score_version"),
                "drivers": row.get("drivers"),
                "evidence": row.get("candidate", {}).get("evidence", []),
                "profile_url": row.get("candidate", {}).get("profile_url"),
            }
            for index, row in enumerate(results, start=1)
        ],
    }

    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    return {
        "snapshot_id": snapshot_id,
        "observed_at": observed_at,
        "path": str(path.relative_to(root)),
    }
