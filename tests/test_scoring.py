import unittest

from ghost_talent.models import Candidate, Evidence
from ghost_talent.scoring import score_candidate


class GhostScoreTests(unittest.TestCase):
    def make_candidate(self, **overrides):
        data = dict(
            login="sample",
            name="Sample Engineer",
            profile_url="https://github.com/sample",
            followers=42,
            repositories=[
                {"name": "org/project", "url": "https://github.com/org/project", "stars": 1200, "contributions": 18}
            ],
            recent_events_7d=8,
            recent_events_30d=18,
            recent_events_90d=27,
            active_days_30d=9,
            observed_event_span_days=24.0,
            contribution_quality={"available": False, "repository": "org/project", "merged_pr_count": 0, "top_pr": None},
            paper_matches=[],
            evidence=[Evidence(type="repository_contribution", source="github", source_url="https://github.com/org/project")],
        )
        data.update(overrides)
        return Candidate(**data)

    def quality(self):
        return {
            "available": True,
            "repository": "org/project",
            "merged_pr_count": 3,
            "sampled_pr_count": 3,
            "top_pr": {
                "number": 42,
                "title": "Optimize CUDA attention kernel",
                "url": "https://github.com/org/project/pull/42",
                "changed_files_sampled": 6,
                "core_files": ["csrc/attention.cu", "benchmarks/attention.py"],
                "core_file_count": 5,
                "keyword_hits": ["cuda", "attention", "kernel", "benchmark"],
                "additions": 320,
                "deletions": 80,
            },
        }

    def test_score_is_bounded_and_explainable(self):
        result = score_candidate(self.make_candidate())
        self.assertGreaterEqual(result["ghost_score"], 0)
        self.assertLessEqual(result["ghost_score"], 100)
        self.assertEqual(result["score_version"], "0.1.4")
        self.assertIn(result["trend"], {"accelerating", "stable", "decelerating"})
        self.assertIn("radar", result["drivers"])

    def test_quality_evidence_increases_capability(self):
        baseline = score_candidate(self.make_candidate())
        enriched = score_candidate(self.make_candidate(contribution_quality=self.quality()))
        self.assertGreater(enriched["capability"], baseline["capability"])
        self.assertGreater(enriched["drivers"]["contribution_quality"]["score"], 0)
        self.assertIn("merged PR quality evidence", enriched["drivers"]["confidence"]["reasons"])

    def test_early_signal_requires_quality_momentum_and_visibility_gap(self):
        candidate = self.make_candidate(
            followers=3,
            contribution_quality=self.quality(),
            recent_events_7d=12,
            recent_events_30d=24,
            recent_events_90d=36,
            active_days_30d=12,
            observed_event_span_days=24.0,
        )
        result = score_candidate(candidate)
        self.assertTrue(result["early_signal"])
        self.assertGreaterEqual(result["radar_score"], 65)

    def test_activity_without_quality_evidence_is_not_early_signal(self):
        result = score_candidate(self.make_candidate(
            followers=1,
            recent_events_7d=20,
            recent_events_30d=30,
            recent_events_90d=35,
            active_days_30d=12,
        ))
        self.assertFalse(result["early_signal"])

    def test_momentum_changes_with_recent_acceleration(self):
        accelerating = score_candidate(self.make_candidate(recent_events_7d=12, recent_events_30d=20, recent_events_90d=30))
        slowing = score_candidate(self.make_candidate(recent_events_7d=1, recent_events_30d=20, recent_events_90d=60))
        self.assertGreater(accelerating["momentum"], slowing["momentum"])

    def test_single_repo_contribution_volume_does_not_force_capability_to_100(self):
        result = score_candidate(self.make_candidate(
            repositories=[{"name": "org/project", "url": "https://github.com/org/project", "stars": 1200, "contributions": 856}]
        ))
        self.assertLess(result["capability"], 100)


if __name__ == "__main__":
    unittest.main()
