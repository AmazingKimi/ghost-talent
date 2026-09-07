from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK_SCHEMA_VERSION = "0.1"
OUTCOME_DEFINITION_VERSION = "0.1"
DEFAULT_HORIZONS = [30, 90, 180]


def _slugify(value: str) -> str:
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "query"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_snapshot(root: Path, query: str) -> tuple[Path, dict[str, Any]]:
    query_slug = _slugify(query)
    matches = sorted((root / "snapshots").glob(f"*/{query_slug}/*.json"))
    if not matches:
        raise FileNotFoundError(f"No snapshot found for query: {query}")
    path = matches[-1]
    payload = _load_json(path)
    if payload.get("query_slug") != query_slug:
        raise ValueError("Latest snapshot query does not match requested cohort query")
    return path, payload


def _baseline_values(row: dict[str, Any]) -> dict[str, float]:
    drivers = row.get("drivers") or {}
    visibility = drivers.get("visibility") or {}
    capability = drivers.get("capability") or {}
    top_repo = capability.get("top_repository") or {}
    return {
        "followers": float(visibility.get("followers") or 0),
        "stars": float(top_repo.get("stars") or 0),
        "raw_contributions": float(top_repo.get("contributions") or 0),
    }


def freeze_cohort(
    root: Path,
    query: str,
    benchmark_id: str,
    top_k: int = 20,
    horizons: list[int] | None = None,
) -> dict[str, Any]:
    _, snapshot = _latest_snapshot(root, query)
    ranking = list(snapshot.get("ranking") or [])[: max(1, top_k)]
    if not ranking:
        raise ValueError("Cannot freeze an empty benchmark cohort")

    benchmark_dir = root / "benchmarks" / benchmark_id
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    cohort_path = benchmark_dir / "cohort.json"
    if cohort_path.exists():
        raise FileExistsError(f"Benchmark cohort already frozen: {cohort_path}")

    members = []
    for row in ranking:
        members.append({
            "rank": row.get("rank"),
            "login": row.get("login"),
            "name": row.get("name"),
            "profile_url": row.get("profile_url"),
            "ghost_score": row.get("ghost_score"),
            "radar_score": row.get("radar_score"),
            "capability": row.get("capability"),
            "momentum": row.get("momentum"),
            "visibility_gap": row.get("visibility_gap"),
            "evidence_confidence": row.get("evidence_confidence"),
            "score_version": row.get("score_version"),
            "first_detected_at": row.get("first_detected_at"),
            "baselines": _baseline_values(row),
        })

    payload = {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "benchmark_id": benchmark_id,
        "status": "frozen",
        "query": snapshot.get("query"),
        "query_slug": snapshot.get("query_slug"),
        "source_snapshot_id": snapshot.get("snapshot_id"),
        "as_of_date": snapshot.get("observed_at"),
        "frozen_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "cohort_size": len(members),
        "score_versions": snapshot.get("score_versions", []),
        "evaluation_horizons_days": horizons or DEFAULT_HORIZONS,
        "outcome_definition_version": OUTCOME_DEFINITION_VERSION,
        "members": members,
    }
    with cohort_path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return payload


def outcome_template(root: Path, benchmark_id: str, horizon_days: int) -> dict[str, Any]:
    cohort_path = root / "benchmarks" / benchmark_id / "cohort.json"
    cohort = _load_json(cohort_path)
    return {
        "schema_version": "0.1",
        "benchmark_id": benchmark_id,
        "horizon_days": horizon_days,
        "outcome_definition_version": cohort.get("outcome_definition_version"),
        "evaluated_at": None,
        "members": [
            {
                "login": member.get("login"),
                "breakout": None,
                "breakout_date": None,
                "outcome_types": [],
                "evidence_urls": [],
                "notes": "",
            }
            for member in cohort.get("members", [])
        ],
    }


def _precision(labels: list[bool], k: int) -> float | None:
    if not labels:
        return None
    subset = labels[: min(k, len(labels))]
    if not subset:
        return None
    return round(sum(bool(value) for value in subset) / len(subset), 4)


def evaluate(root: Path, benchmark_id: str, outcomes_path: Path, ks: list[int] | None = None) -> dict[str, Any]:
    cohort = _load_json(root / "benchmarks" / benchmark_id / "cohort.json")
    outcomes = _load_json(outcomes_path)
    outcome_by_login = {str(item.get("login")): item for item in outcomes.get("members", [])}

    adjudicated = []
    for member in cohort.get("members", []):
        item = outcome_by_login.get(str(member.get("login")))
        if not item or item.get("breakout") is None:
            continue
        adjudicated.append((member, bool(item.get("breakout")), item))

    if not adjudicated:
        return {
            "benchmark_id": benchmark_id,
            "status": "pending_outcomes",
            "adjudicated": 0,
            "cohort_size": cohort.get("cohort_size", 0),
        }

    by_ghost = sorted(adjudicated, key=lambda item: float(item[0].get("ghost_score") or 0), reverse=True)
    baselines = {
        "followers": sorted(adjudicated, key=lambda item: float((item[0].get("baselines") or {}).get("followers") or 0), reverse=True),
        "stars": sorted(adjudicated, key=lambda item: float((item[0].get("baselines") or {}).get("stars") or 0), reverse=True),
        "raw_contributions": sorted(adjudicated, key=lambda item: float((item[0].get("baselines") or {}).get("raw_contributions") or 0), reverse=True),
    }
    ks = ks or [5, 10, 20]
    metrics = {
        "ghost_score": {f"precision_at_{k}": _precision([label for _, label, _ in by_ghost], k) for k in ks}
    }
    for name, rows in baselines.items():
        metrics[name] = {f"precision_at_{k}": _precision([label for _, label, _ in rows], k) for k in ks}

    lead_times = []
    as_of = datetime.fromisoformat(str(cohort["as_of_date"]).replace("Z", "+00:00"))
    for _, label, item in adjudicated:
        if not label or not item.get("breakout_date"):
            continue
        breakout_date = datetime.fromisoformat(str(item["breakout_date"]).replace("Z", "+00:00"))
        lead_times.append((breakout_date - as_of).total_seconds() / 86400.0)

    return {
        "benchmark_id": benchmark_id,
        "status": "evaluated",
        "cohort_size": cohort.get("cohort_size", 0),
        "adjudicated": len(adjudicated),
        "breakouts": sum(label for _, label, _ in adjudicated),
        "breakout_rate": round(sum(label for _, label, _ in adjudicated) / len(adjudicated), 4),
        "metrics": metrics,
        "breakout_lead_time_days_mean": round(sum(lead_times) / len(lead_times), 2) if lead_times else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ghost Talent Benchmark v0.1")
    sub = parser.add_subparsers(dest="command", required=True)

    freeze = sub.add_parser("freeze", help="Freeze the latest local snapshot into an immutable benchmark cohort")
    freeze.add_argument("--query", required=True)
    freeze.add_argument("--benchmark-id", required=True)
    freeze.add_argument("--top-k", type=int, default=20)

    template = sub.add_parser("outcome-template", help="Create an adjudication template for a frozen cohort")
    template.add_argument("--benchmark-id", required=True)
    template.add_argument("--horizon-days", type=int, required=True)

    evaluate_cmd = sub.add_parser("evaluate", help="Evaluate adjudicated outcomes")
    evaluate_cmd.add_argument("--benchmark-id", required=True)
    evaluate_cmd.add_argument("--outcomes", required=True)

    args = parser.parse_args()
    if args.command == "freeze":
        result = freeze_cohort(ROOT, args.query, args.benchmark_id, args.top_k)
    elif args.command == "outcome-template":
        result = outcome_template(ROOT, args.benchmark_id, args.horizon_days)
    else:
        result = evaluate(ROOT, args.benchmark_id, Path(args.outcomes))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
