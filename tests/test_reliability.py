import hashlib
import json
from pathlib import Path

from ghost_talent.app import snapshot_allowed, validation_registry


def test_snapshot_gate_rejects_incomplete_source():
    allowed, reason = snapshot_allowed(
        {
            "complete": False,
            "sources": {"github": {"status": "rate_limited"}},
            "results": [],
        }
    )
    assert allowed is False
    assert reason == "source_incomplete"


def test_snapshot_gate_rejects_non_healthy_github():
    allowed, reason = snapshot_allowed(
        {
            "complete": True,
            "sources": {"github": {"status": "unavailable"}},
            "results": [],
        }
    )
    assert allowed is False
    assert reason == "github_not_healthy"


def test_snapshot_gate_allows_healthy_empty_result():
    allowed, reason = snapshot_allowed(
        {
            "complete": True,
            "sources": {"github": {"status": "ok"}, "openalex": {"status": "ok"}},
            "results": [],
        }
    )
    assert allowed is True
    assert reason is None


def test_validation_registry_reports_current_artifact_hash(tmp_path: Path):
    cohort_dir = tmp_path / "benchmarks" / "2026-09-08-distributed-training-systems-v028"
    cohort_dir.mkdir(parents=True)
    payload = {
        "benchmark_id": "2026-09-08-distributed-training-systems-v028",
        "cohort_size": 20,
        "frozen_at": "2026-09-08T03:32:59Z",
        "members": [{"score_version": "0.2.8"}],
    }
    raw = (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8")
    (cohort_dir / "cohort.json").write_bytes(raw)

    rows = validation_registry(tmp_path)
    row = next(item for item in rows if item["id"] == payload["benchmark_id"])

    assert row["artifact_status"] == "public-frozen"
    assert row["artifact_sha256_current"] == hashlib.sha256(raw).hexdigest()
    assert row["freeze_time_commitment"] is None
    assert row["size"] == 20
    assert row["score_version"] == "0.2.8"
