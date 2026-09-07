import json
import tempfile
import unittest
from pathlib import Path

from ghost_talent.snapshot import save_snapshot


class SnapshotTests(unittest.TestCase):
    def test_snapshot_is_written_with_rank_and_score_version(self):
        results = [
            {
                "ghost_score": 61.2,
                "capability": 63.0,
                "momentum": 70.0,
                "visibility_gap": 52.0,
                "evidence_confidence": 44.0,
                "trend": "accelerating",
                "score_version": "0.1.3",
                "drivers": {"capability": {"base_capability": 55.0}},
                "candidate": {
                    "login": "sample",
                    "name": "Sample Engineer",
                    "profile_url": "https://github.com/sample",
                    "evidence": [
                        {
                            "type": "repository_contribution",
                            "source": "github",
                            "source_url": "https://github.com/org/project",
                            "value": {"repository": "org/project"},
                        }
                    ],
                },
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            meta = save_snapshot(root, "LLM inference CUDA Triton", results)
            snapshot_path = root / meta["path"]
            self.assertTrue(snapshot_path.exists())

            payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["query"], "LLM inference CUDA Triton")
            self.assertEqual(payload["score_versions"], ["0.1.3"])
            self.assertEqual(payload["ranking"][0]["rank"], 1)
            self.assertEqual(payload["ranking"][0]["login"], "sample")
            self.assertEqual(payload["ranking"][0]["ghost_score"], 61.2)

    def test_repeated_runs_create_distinct_immutable_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = save_snapshot(root, "CUDA kernels", [])
            second = save_snapshot(root, "CUDA kernels", [])
            self.assertNotEqual(first["snapshot_id"], second["snapshot_id"])
            self.assertTrue((root / first["path"]).exists())
            self.assertTrue((root / second["path"]).exists())


if __name__ == "__main__":
    unittest.main()
