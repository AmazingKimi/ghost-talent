import json
import tempfile
import unittest
from pathlib import Path

from ghost_talent.benchmark import evaluate, freeze_cohort, outcome_template


class BenchmarkTests(unittest.TestCase):
    def _write_snapshot(self, root: Path, score_version="0.1.5", current_driver_shape=False):
        path = root / "snapshots" / "2026-09-08" / "cuda-triton" / "snap.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        capability_a = (
            {"top_repositories": [{"stars": 1000, "contributions": 12}]}
            if current_driver_shape
            else {"top_repository": {"stars": 1000, "contributions": 12}}
        )
        capability_b = (
            {"top_repositories": [{"stars": 100, "contributions": 30}]}
            if current_driver_shape
            else {"top_repository": {"stars": 100, "contributions": 30}}
        )
        payload = {
            "schema_version": "0.5",
            "snapshot_id": "snap-001",
            "observed_at": "2026-09-08T00:00:00Z",
            "query": "CUDA Triton",
            "query_slug": "cuda-triton",
            "score_versions": [score_version],
            "ranking": [
                {
                    "rank": 1,
                    "login": "alpha",
                    "name": "Alpha",
                    "profile_url": "https://github.com/alpha",
                    "ghost_score": 70.0,
                    "radar_score": 72.0,
                    "capability": 68.0,
                    "momentum": 80.0,
                    "visibility_gap": 75.0,
                    "evidence_confidence": 55.0,
                    "score_version": score_version,
                    "first_detected_at": "2026-09-08T00:00:00Z",
                    "drivers": {"visibility": {"followers": 20}, "capability": capability_a},
                },
                {
                    "rank": 2,
                    "login": "beta",
                    "name": "Beta",
                    "profile_url": "https://github.com/beta",
                    "ghost_score": 60.0,
                    "radar_score": 55.0,
                    "capability": 60.0,
                    "momentum": 58.0,
                    "visibility_gap": 70.0,
                    "evidence_confidence": 50.0,
                    "score_version": score_version,
                    "first_detected_at": "2026-09-08T00:00:00Z",
                    "drivers": {"visibility": {"followers": 200}, "capability": capability_b},
                },
            ],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

    def test_freeze_is_immutable_and_keeps_baselines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_snapshot(root)
            cohort = freeze_cohort(root, "CUDA Triton", "bench-v01", top_k=2)
            self.assertEqual(cohort["status"], "frozen")
            self.assertEqual(cohort["source_snapshot_id"], "snap-001")
            self.assertEqual(cohort["members"][0]["baselines"]["followers"], 20.0)
            with self.assertRaises(FileExistsError):
                freeze_cohort(root, "CUDA Triton", "bench-v01", top_k=2)

    def test_current_driver_shape_keeps_nonzero_star_and_contribution_baselines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_snapshot(root, score_version="0.2.8", current_driver_shape=True)
            cohort = freeze_cohort(
                root,
                "CUDA Triton",
                "bench-v028",
                top_k=2,
                required_score_version="0.2.8",
            )
            self.assertEqual(cohort["members"][0]["baselines"]["stars"], 1000.0)
            self.assertEqual(cohort["members"][0]["baselines"]["raw_contributions"], 12.0)
            self.assertEqual(cohort["score_versions"], ["0.2.8"])

    def test_required_score_version_blocks_wrong_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_snapshot(root, score_version="0.1.5")
            with self.assertRaises(ValueError):
                freeze_cohort(
                    root,
                    "CUDA Triton",
                    "wrong-model",
                    top_k=2,
                    required_score_version="0.2.8",
                )

    def test_outcome_template_starts_unadjudicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_snapshot(root)
            freeze_cohort(root, "CUDA Triton", "bench-v01", top_k=2)
            template = outcome_template(root, "bench-v01", 90)
            self.assertEqual(template["horizon_days"], 90)
            self.assertIsNone(template["members"][0]["breakout"])

    def test_evaluate_compares_ghost_score_with_baselines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_snapshot(root)
            freeze_cohort(root, "CUDA Triton", "bench-v01", top_k=2)
            outcomes = outcome_template(root, "bench-v01", 90)
            outcomes["members"][0].update({"breakout": True, "breakout_date": "2026-10-08T00:00:00Z"})
            outcomes["members"][1].update({"breakout": False})
            path = root / "outcomes.json"
            path.write_text(json.dumps(outcomes), encoding="utf-8")
            result = evaluate(root, "bench-v01", path, ks=[1, 2])
            self.assertEqual(result["status"], "evaluated")
            self.assertEqual(result["metrics"]["ghost_score"]["precision_at_1"], 1.0)
            self.assertEqual(result["metrics"]["followers"]["precision_at_1"], 0.0)
            self.assertEqual(result["breakout_lead_time_days_mean"], 30.0)


if __name__ == "__main__":
    unittest.main()
