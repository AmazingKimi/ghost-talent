import unittest

from ghost_talent.credibility import correlation_report
from ghost_talent.models import Candidate
from ghost_talent.scoring import score_candidate


class CredibilityTests(unittest.TestCase):
    def candidate(self, **overrides):
        data = dict(
            login="sample",
            name="Sample",
            profile_url="https://github.com/sample",
            followers=10,
            repositories=[{"name":"sample/project","url":"https://github.com/sample/project","stars":10,"contributions":20,"owner_login":"sample"}],
            recent_events_7d=8,
            recent_events_30d=20,
            recent_events_90d=40,
            active_days_30d=10,
            observed_event_span_days=30,
            contribution_quality={},
            paper_matches=[],
            evidence=[],
            noise={"status":"clear"},
            identity={},
            external_validation={"available":True,"external_merged_prs":0,"recognized_upstream_prs":0,"core_path_prs":0,"maintainer_accepted_prs":0,"maintainer_accepted_core_path_prs":0,"recent_external_merged_prs":0,"recent_recognized_upstream_prs":0,"recent_core_path_prs":0,"recent_maintainer_accepted_prs":0,"recent_maintainer_accepted_core_path_prs":0,"recent_window_days":180,"prs":[]},
        )
        data.update(overrides)
        return Candidate(**data)

    def test_activity_only_cannot_be_early_or_strong(self):
        c = self.candidate(
            followers=1,
            repositories=[{"name":"sample/project","url":"https://github.com/sample/project","stars":50,"contributions":1200,"owner_login":"sample"}],
            recent_events_7d=40,
            recent_events_30d=80,
            recent_events_90d=100,
            active_days_30d=25,
        )
        result = score_candidate(c)
        self.assertNotIn(result["recommendation_status"], {"EARLY SIGNAL", "STRONG SIGNAL"})

    def test_recent_maintainer_approved_core_path_can_unlock_strong_gate(self):
        external = {
            "available":True,
            "external_merged_prs":8,
            "recognized_upstream_prs":5,
            "core_path_prs":5,
            "maintainer_accepted_prs":5,
            "maintainer_accepted_core_path_prs":4,
            "recent_external_merged_prs":6,
            "recent_recognized_upstream_prs":5,
            "recent_core_path_prs":4,
            "recent_maintainer_accepted_prs":4,
            "recent_maintainer_accepted_core_path_prs":3,
            "recent_window_days":180,
            "prs":[],
        }
        c = self.candidate(
            followers=20,
            repositories=[{"name":"org/project","url":"https://github.com/org/project","stars":5000,"contributions":120,"owner_login":"org"}],
            recent_events_7d=20,
            recent_events_30d=35,
            recent_events_90d=50,
            active_days_30d=15,
            external_validation=external,
        )
        result = score_candidate(c)
        self.assertIn(result["recommendation_status"], {"EARLY SIGNAL", "STRONG SIGNAL"})

    def test_already_visible_routes_to_proven(self):
        external = {
            "available":True,
            "external_merged_prs":10,
            "recognized_upstream_prs":6,
            "core_path_prs":5,
            "maintainer_accepted_prs":5,
            "maintainer_accepted_core_path_prs":4,
            "recent_external_merged_prs":5,
            "recent_recognized_upstream_prs":4,
            "recent_core_path_prs":4,
            "recent_maintainer_accepted_prs":4,
            "recent_maintainer_accepted_core_path_prs":3,
            "recent_window_days":180,
            "prs":[],
        }
        result = score_candidate(self.candidate(followers=4100, external_validation=external))
        self.assertEqual(result["recommendation_status"], "PROVEN / ALREADY VISIBLE")

    def test_noise_blocks_recommendation(self):
        result = score_candidate(self.candidate(noise={"status":"flagged","reasons":["course_or_exercise_repository_pattern"]}))
        self.assertEqual(result["recommendation_status"], "LOW CONFIDENCE")

    def test_correlation_report_flags_dimension_collapse(self):
        rows = []
        for i in range(1, 8):
            rows.append({
                "internal_capability":i*10,
                "external_validation":i*5,
                "capability":i*10,
                "momentum":i*10,
                "visibility_gap":100-i*3,
                "evidence_confidence":50+i,
                "ghost_score":i*10,
                "radar_score":i*10,
            })
        report = correlation_report(rows)
        pairs = {(p["left"],p["right"]):p for p in report["pairs"]}
        self.assertTrue(pairs[("internal_capability","momentum")]["high_correlation"])
        self.assertGreater(len(report["warnings"]), 0)


if __name__ == "__main__":
    unittest.main()
