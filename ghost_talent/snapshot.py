from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SNAPSHOT_SCHEMA_VERSION = "0.4"
LEDGER_SCHEMA_VERSION = "0.1"
HISTORY_SCHEMA_VERSION = "0.1"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "query"


def _person_key(login: str) -> str:
    return _slugify(login)[:80]


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _record_first_detected(root: Path, observed_at: str, query: str, snapshot_id: str, results: list[dict[str, Any]]) -> dict[str, str]:
    directory = root / "ledger" / "people"
    directory.mkdir(parents=True, exist_ok=True)
    first_detected: dict[str, str] = {}
    for rank, row in enumerate(results, start=1):
        candidate = row.get("candidate", {})
        login = str(candidate.get("login") or "").strip()
        if not login:
            continue
        path = directory / f"{_person_key(login)}.json"
        payload = {
            "schema_version": LEDGER_SCHEMA_VERSION,
            "login": login,
            "name": candidate.get("name"),
            "profile_url": candidate.get("profile_url"),
            "first_detected_at": observed_at,
            "first_query": query,
            "first_snapshot_id": snapshot_id,
            "first_rank": rank,
            "first_score_version": row.get("score_version"),
            "first_scores": {key: row.get(key) for key in ("ghost_score", "capability", "momentum", "visibility_gap", "evidence_confidence")},
        }
        try:
            with path.open("x", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.write("\n")
            first_detected[login] = observed_at
        except FileExistsError:
            existing = json.loads(path.read_text(encoding="utf-8"))
            first_detected[login] = str(existing.get("first_detected_at") or observed_at)
    return first_detected


def _previous_snapshot(root: Path, query_slug: str) -> dict[str, Any] | None:
    snapshots = root / "snapshots"
    if not snapshots.exists():
        return None
    matches = sorted(snapshots.glob(f"*/{query_slug}/*.json"))
    for path in reversed(matches):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("query_slug") == query_slug:
            return payload
    return None


def _history(previous: dict[str, Any] | None, login: str, ghost_score: float | None, rank: int, score_version: str | None) -> dict[str, Any]:
    if not previous:
        return {"status": "building_history"}
    prior = next((row for row in previous.get("ranking", []) if str(row.get("login", "")).lower() == login.lower()), None)
    if not prior or prior.get("ghost_score") is None or ghost_score is None:
        return {"status": "building_history", "previous_snapshot_id": previous.get("snapshot_id")}
    if str(prior.get("score_version")) != str(score_version):
        return {
            "status": "building_history",
            "reason": "score_version_changed",
            "previous_snapshot_id": previous.get("snapshot_id"),
        }
    previous_score = float(prior["ghost_score"])
    score_delta = round(float(ghost_score) - previous_score, 1)
    previous_rank = int(prior.get("rank") or rank)
    rank_delta = previous_rank - rank
    return {
        "status": "comparable",
        "previous_snapshot_id": previous.get("snapshot_id"),
        "previous_observed_at": previous.get("observed_at"),
        "previous_score": previous_score,
        "score_delta": score_delta,
        "previous_rank": previous_rank,
        "rank_delta": rank_delta,
        "rising_fast": score_delta >= 3.0 or rank_delta >= 5,
    }


def _history_path(root: Path, query_slug: str, login: str) -> Path:
    return root / "ledger" / "history" / query_slug / f"{_person_key(login)}.jsonl"


def _read_observations(root: Path, query_slug: str, login: str) -> list[dict[str, Any]]:
    path = _history_path(root, query_slug, login)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _window_delta(observations: list[dict[str, Any]], observed: datetime, current_score: float | None, current_rank: int, score_version: str | None, days: int) -> dict[str, Any]:
    cutoff = observed - timedelta(days=days)
    eligible = []
    for item in observations:
        ts = _parse_time(str(item.get("observed_at") or ""))
        if ts is None or ts > cutoff:
            continue
        if str(item.get("score_version")) != str(score_version):
            continue
        if item.get("ghost_score") is None:
            continue
        eligible.append((ts, item))
    if not eligible or current_score is None:
        return {"status": "building_history", "days": days}
    _, baseline = max(eligible, key=lambda pair: pair[0])
    baseline_rank = int(baseline.get("rank") or current_rank)
    score_delta = round(float(current_score) - float(baseline["ghost_score"]), 1)
    return {
        "status": "comparable",
        "days": days,
        "baseline_observed_at": baseline.get("observed_at"),
        "baseline_score": float(baseline["ghost_score"]),
        "score_delta": score_delta,
        "baseline_rank": baseline_rank,
        "rank_delta": baseline_rank - current_rank,
    }


def _trajectory(root: Path, query_slug: str, login: str, observed: datetime, row: dict[str, Any], rank: int) -> dict[str, Any]:
    observations = _read_observations(root, query_slug, login)
    return {
        "observation_count": len(observations) + 1,
        "d7": _window_delta(observations, observed, row.get("ghost_score"), rank, row.get("score_version"), 7),
        "d30": _window_delta(observations, observed, row.get("ghost_score"), rank, row.get("score_version"), 30),
    }


def _append_observation(root: Path, query: str, query_slug: str, snapshot_id: str, observed_at: str, row: dict[str, Any], rank: int) -> None:
    login = str(row.get("candidate", {}).get("login") or "").strip()
    if not login:
        return
    path = _history_path(root, query_slug, login)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "observed_at": observed_at,
        "snapshot_id": snapshot_id,
        "query": query,
        "query_slug": query_slug,
        "login": login,
        "rank": rank,
        "score_version": row.get("score_version"),
        "ghost_score": row.get("ghost_score"),
        "radar_score": row.get("radar_score"),
        "capability": row.get("capability"),
        "momentum": row.get("momentum"),
        "visibility_gap": row.get("visibility_gap"),
        "evidence_confidence": row.get("evidence_confidence"),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def save_snapshot(root: Path, query: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    observed = datetime.now(timezone.utc)
    observed_at = observed.isoformat().replace("+00:00", "Z")
    query_slug = _slugify(query)
    previous = _previous_snapshot(root, query_slug)
    fingerprint = hashlib.sha256(f"{query}|{observed_at}".encode("utf-8")).hexdigest()[:8]
    snapshot_id = f"{observed.strftime('%Y%m%dT%H%M%S%fZ')}-{fingerprint}"
    first_detected = _record_first_detected(root, observed_at, query, snapshot_id, results)
    histories: dict[str, dict[str, Any]] = {}
    trajectories: dict[str, dict[str, Any]] = {}
    ranking = []
    for index, row in enumerate(results, start=1):
        candidate = row.get("candidate", {})
        login = str(candidate.get("login") or "")
        history = _history(previous, login, row.get("ghost_score"), index, row.get("score_version"))
        trajectory = _trajectory(root, query_slug, login, observed, row, index)
        histories[login] = history
        trajectories[login] = trajectory
        ranking.append({
            "rank": index,
            "login": candidate.get("login"),
            "name": candidate.get("name"),
            "first_detected_at": first_detected.get(login),
            "ghost_score": row.get("ghost_score"),
            "capability": row.get("capability"),
            "momentum": row.get("momentum"),
            "visibility_gap": row.get("visibility_gap"),
            "evidence_confidence": row.get("evidence_confidence"),
            "trend": row.get("trend"),
            "score_version": row.get("score_version"),
            "history": history,
            "trajectory": trajectory,
            "drivers": row.get("drivers"),
            "evidence": candidate.get("evidence", []),
            "profile_url": candidate.get("profile_url"),
        })
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
        "ranking": ranking,
    }
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    for index, row in enumerate(results, start=1):
        _append_observation(root, query, query_slug, snapshot_id, observed_at, row, index)
    return {
        "snapshot_id": snapshot_id,
        "observed_at": observed_at,
        "path": str(path.relative_to(root)),
        "first_detected": first_detected,
        "history": histories,
        "trajectory": trajectories,
    }
