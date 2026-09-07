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
            paper_matches=[],
            evidence=[Evidence(type="repository_contribution", source="github", source_url="https://github.com/org/project")],
        )
        data.update(overrides)
        return Candidate(**data)

    def test_score_is_bounded_and_explainable(self):
        result = score_candidate(self.make_candidate())
        self.assertGreaterEqual(result["ghost_score"], 0)
        self.assertLessEqual(result["ghost_score"], 100)
        self.assertEqual(result["score_version"], "0.1.1")
        self.assertIn(result["trend"], {"accelerating", "stable", "decelerating"})
        self.assertIn("capability", result)
        self.assertIn("momentum", result)
        self.assertIn("visibility_gap", result)
        self.assertIn("evidence_confidence", result)

    def test_momentum_changes_with_recent_acceleration(self):
        accelerating = score_candidate(
            self.make_candidate(recent_events_7d=12, recent_events_30d=20, recent_events_90d=30)
        )
        slowing = score_candidate(
            self.make_candidate(recent_events_7d=1, recent_events_30d=20, recent_events_90d=60)
        )
        self.assertGreater(accelerating["momentum"], slowing["momentum"])

    def test_single_repo_contribution_volume_does_not_force_capability_to_100(self):
        result = score_candidate(
            self.make_candidate(
                repositories=[
                    {"name": "org/project", "url": "https://github.com/org/project", "stars": 1200, "contributions": 856}
                ]
            )
        )
        self.assertLess(result["capability"], 100)


if __name__ == "__main__":
    unittest.main()
