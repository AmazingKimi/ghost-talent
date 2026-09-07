import unittest

from ghost_talent.models import Candidate, Evidence
from ghost_talent.scoring import score_candidate


class GhostScoreTests(unittest.TestCase):
    def test_score_is_bounded_and_explainable(self):
        candidate = Candidate(
            login="sample",
            name="Sample Engineer",
            profile_url="https://github.com/sample",
            followers=42,
            repositories=[
                {"name": "org/project", "url": "https://github.com/org/project", "stars": 1200, "contributions": 18}
            ],
            recent_events_30d=18,
            recent_events_90d=27,
            paper_matches=[],
            evidence=[Evidence(type="repository_contribution", source="github", source_url="https://github.com/org/project")],
        )
        result = score_candidate(candidate)
        self.assertGreaterEqual(result["ghost_score"], 0)
        self.assertLessEqual(result["ghost_score"], 100)
        self.assertIn(result["trend"], {"accelerating", "stable", "decelerating"})
        self.assertIn("capability", result)
        self.assertIn("momentum", result)
        self.assertIn("visibility_gap", result)
        self.assertIn("evidence_confidence", result)


if __name__ == "__main__":
    unittest.main()
