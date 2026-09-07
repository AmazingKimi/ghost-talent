import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ghost_talent.snapshot import save_snapshot


class SnapshotTests(unittest.TestCase):
    def sample_results(self, ghost_score=61.2, radar_score=66.0, score_version="0.1.5"):
        return [
            {
                "ghost_score": ghost_score,
                "radar_score": radar_score,
                "capability": 63.0,
                "momentum": 70.0,
                "visibility_gap": 52.0,
                "evidence_confidence": 44.0,
                "trend": "accelerating",
                "score_version": score_version,
                "drivers": {"capability": {"base_capability": 55.0}},
                "candidate": {
                    "login": "sample",
                    "name": "Sample Engineer",
                    "profile_url": "https://github.com/sample",
                    "evidence": [{
                        "type": "repository_contribution",
                        "source": "github",
                        "source_url": "https://github.com/org/project",
                        "subject_id": "github:sample",
                        "value": {"repository": "org/project"},
                    }],
                },
            }
        ]

    def test_snapshot_is_written_with_rank_and_score_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            meta = save_snapshot(root, "LLM inference CUDA Triton", self.sample_results())
            payload = json.loads((root / meta["path"]).read_text(encoding="utf-8"))
            self.assertEqual(payload["query"], "LLM inference CUDA Triton")
            self.assertEqual(payload["score_versions"], ["0.1.5"])
            self.assertEqual(payload["ranking"][0]["rank"], 1)
            self.assertEqual(payload["ranking"][0]["login"], "sample")
            self.assertEqual(payload["ranking"][0]["ghost_score"], 61.2)
            self.assertEqual(meta["trajectory"]["sample"]["d7"]["status"], "building_history")
            self.assertEqual(meta["trajectory"]["sample"]["rising_fast_v2"]["status"], "building_history")

    def test_repeated_runs_create_distinct_immutable_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = save_snapshot(root, "CUDA kernels", [])
            second = save_snapshot(root, "CUDA kernels", [])
            self.assertNotEqual(first["snapshot_id"], second["snapshot_id"])
            self.assertTrue((root / first["path"]).exists())
            self.assertTrue((root / second["path"]).exists())

    def test_first_detected_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = save_snapshot(root, "CUDA kernels", self.sample_results())
            second = save_snapshot(root, "Triton inference", self.sample_results())
            self.assertEqual(first["first_detected"]["sample"], second["first_detected"]["sample"])

    def test_score_version_change_is_not_compared(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            save_snapshot(root, "CUDA kernels", self.sample_results(score_version="0.1.4"))
            second = save_snapshot(root, "CUDA kernels", self.sample_results(score_version="0.1.5"))
            history = second["history"]["sample"]
            self.assertEqual(history["status"], "building_history")
            self.assertEqual(history["reason"], "score_version_changed")

    def test_7d_trajectory_includes_radar_delta_and_rising_fast_v2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            history_path = root / "ledger" / "history" / "cuda-kernels" / "sample.jsonl"
            history_path.parent.mkdir(parents=True, exist_ok=True)
            old = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat().replace("+00:00", "Z")
            history_path.write_text(json.dumps({
                "schema_version": "0.1",
                "observed_at": old,
                "snapshot_id": "old",
                "query": "CUDA kernels",
                "query_slug": "cuda-kernels",
                "login": "sample",
                "rank": 6,
                "score_version": "0.1.5",
                "ghost_score": 55.0,
                "radar_score": 60.0,
            }) + "\n", encoding="utf-8")
            meta = save_snapshot(root, "CUDA kernels", self.sample_results(ghost_score=61.2, radar_score=66.0))
            d7 = meta["trajectory"]["sample"]["d7"]
            rising = meta["trajectory"]["sample"]["rising_fast_v2"]
            self.assertEqual(d7["status"], "comparable")
            self.assertEqual(d7["score_delta"], 6.2)
            self.assertEqual(d7["rank_delta"], 5)
            self.assertEqual(d7["radar_delta"], 6.0)
            self.assertEqual(rising["status"], "rising")
            self.assertGreaterEqual(rising["signal_count"], 2)

    def test_rising_fast_v2_does_not_trigger_on_single_weak_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            history_path = root / "ledger" / "history" / "cuda-kernels" / "sample.jsonl"
            history_path.parent.mkdir(parents=True, exist_ok=True)
            old = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat().replace("+00:00", "Z")
            history_path.write_text(json.dumps({
                "schema_version": "0.1", "observed_at": old, "snapshot_id": "old",
                "query": "CUDA kernels", "query_slug": "cuda-kernels", "login": "sample",
                "rank": 1, "score_version": "0.1.5", "ghost_score": 59.0, "radar_score": 64.0,
            }) + "\n", encoding="utf-8")
            meta = save_snapshot(root, "CUDA kernels", self.sample_results(ghost_score=61.2, radar_score=66.0))
            self.assertEqual(meta["trajectory"]["sample"]["rising_fast_v2"]["status"], "not_rising")


if __name__ == "__main__":
    unittest.main()
