from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

FIELDS = (
    "internal_capability",
    "external_validation",
    "capability",
    "momentum",
    "visibility_gap",
    "evidence_confidence",
    "ghost_score",
    "radar_score",
)


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denom == 0:
        return None
    return round(sum(x * y for x, y in zip(dx, dy)) / denom, 3)


def _extract(row: dict[str, Any], field: str) -> float | None:
    value = row.get(field)
    if value is None and field == "internal_capability":
        value = (row.get("drivers") or {}).get("capability", {}).get("internal")
    if value is None and field == "external_validation":
        value = (row.get("drivers") or {}).get("external_validation", {}).get("score")
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def correlation_report(rows: list[dict[str, Any]], high_correlation: float = 0.85) -> dict[str, Any]:
    pairs = []
    for i, left in enumerate(FIELDS):
        for right in FIELDS[i + 1 :]:
            paired = []
            for row in rows:
                x = _extract(row, left)
                y = _extract(row, right)
                if x is not None and y is not None:
                    paired.append((x, y))
            corr = _pearson([x for x, _ in paired], [y for _, y in paired])
            pairs.append({
                "left": left,
                "right": right,
                "n": len(paired),
                "pearson": corr,
                "high_correlation": bool(corr is not None and abs(corr) >= high_correlation),
            })
    return {
        "row_count": len(rows),
        "high_correlation_threshold": high_correlation,
        "pairs": pairs,
        "warnings": [p for p in pairs if p["high_correlation"]],
    }


def snapshot_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for row in payload.get("ranking", []):
        rows.append({
            **row,
            "internal_capability": (row.get("drivers") or {}).get("capability", {}).get("internal"),
            "external_validation": (row.get("drivers") or {}).get("external_validation", {}).get("score"),
        })
    return rows


def latest_snapshot(root: Path, score_version: str | None = None) -> Path | None:
    paths = sorted((root / "snapshots").glob("*/*/*.json")) if (root / "snapshots").exists() else []
    for path in reversed(paths):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        versions = {str(v) for v in payload.get("score_versions", [])}
        if score_version is None or score_version in versions:
            return path
    return None


def run_latest(root: Path, score_version: str | None = None) -> dict[str, Any]:
    path = latest_snapshot(root, score_version=score_version)
    if path is None:
        return {"status": "no_snapshot", "score_version": score_version}
    rows = snapshot_rows(path)
    return {
        "status": "ok",
        "snapshot": str(path.relative_to(root)),
        "score_version": score_version,
        "report": correlation_report(rows),
    }
