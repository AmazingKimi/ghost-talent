import unittest
from ghost_talent.models import Candidate, Evidence
from ghost_talent.scoring import score_candidate

class GhostScoreTests(unittest.TestCase):
    def make_candidate(self, **overrides):
        data=dict(login="sample",name="Sample Engineer",profile_url="https://github.com/sample",followers=20,repositories=[{"name":"sample/project","url":"https://github.com/sample/project","stars":20,"contributions":800,"owner_login":"sample"}],recent_events_7d=12,recent_events_30d=24,recent_events_90d=36,active_days_30d=12,observed_event_span_days=24.0,contribution_quality={"available":False},paper_matches=[],evidence=[Evidence(type="repository_contribution",source="github",source_url="https://github.com/sample/project",subject_id="github:1")],noise={"status":"clear"},identity={"subject_id":"github:1"},external_validation={"available":True,"external_merged_prs":0,"substantive_external_prs":0,"verified_external_project_prs":0,"recognized_upstream_prs":0,"core_path_prs":0,"maintainer_accepted_prs":0,"maintainer_accepted_core_path_prs":0,"recent_window_days":180,"recent_external_merged_prs":0,"recent_verified_external_project_prs":0,"recent_recognized_upstream_prs":0,"recent_core_path_prs":0,"recent_maintainer_accepted_prs":0,"recent_maintainer_accepted_core_path_prs":0,"prs":[]},momentum_coverage={"history_sufficient":True,"sample_truncated":False})
        data.update(overrides);return Candidate(**data)
    def strong_external(self):
        return {"available":True,"external_merged_prs":5,"substantive_external_prs":5,"verified_external_project_prs":4,"recognized_upstream_prs":3,"core_path_prs":3,"maintainer_accepted_prs":3,"maintainer_accepted_core_path_prs":2,"recent_window_days":180,"recent_external_merged_prs":4,"recent_verified_external_project_prs":3,"recent_recognized_upstream_prs":2,"recent_core_path_prs":2,"recent_maintainer_accepted_prs":2,"recent_maintainer_accepted_core_path_prs":1,"prs":[]}
    def open_project_external(self):
        return {"available":True,"external_merged_prs":4,"substantive_external_prs":4,"verified_external_project_prs":4,"recognized_upstream_prs":0,"core_path_prs":3,"maintainer_accepted_prs":2,"maintainer_accepted_core_path_prs":1,"recent_window_days":180,"recent_external_merged_prs":4,"recent_verified_external_project_prs":3,"recent_recognized_upstream_prs":0,"recent_core_path_prs":2,"recent_maintainer_accepted_prs":2,"recent_maintainer_accepted_core_path_prs":0,"prs":[]}
    def test_score_is_bounded_and_current(self):
        r=score_candidate(self.make_candidate());self.assertEqual(r["score_version"],"0.2.8");self.assertTrue(0<=r["ghost_score"]<=100);self.assertIn(r["recommendation_status"],{"STRONG SIGNAL","EARLY SIGNAL","WATCH","DISCOVERED","PROVEN / ALREADY VISIBLE","LOW CONFIDENCE"})
    def test_self_owned_activity_alone_cannot_be_early(self):
        r=score_candidate(self.make_candidate());self.assertFalse(r["early_signal"]);self.assertNotIn(r["recommendation_status"],{"EARLY SIGNAL","STRONG SIGNAL"});self.assertTrue(r["drivers"]["confidence"]["evidence_concentration_risk"])
    def test_unchecked_external_validation_is_low_confidence(self):
        r=score_candidate(self.make_candidate(external_validation={"available":False}));self.assertEqual(r["recommendation_status"],"LOW CONFIDENCE");self.assertLessEqual(r["evidence_confidence"],35)
    def test_verified_recent_upstream_can_create_strong_signal(self):
        r=score_candidate(self.make_candidate(repositories=[{"name":"org/project","url":"https://github.com/org/project","stars":10000,"contributions":40,"owner_login":"org"}],external_validation=self.strong_external()));self.assertEqual(r["recommendation_status"],"STRONG SIGNAL");self.assertTrue(r["early_signal"])
    def test_non_curated_external_project_can_create_early_signal(self):
        r=score_candidate(self.make_candidate(repositories=[{"name":"new-lab/emerging-runtime","url":"https://github.com/new-lab/emerging-runtime","stars":40,"contributions":25,"owner_login":"new-lab"}],external_validation=self.open_project_external()));self.assertEqual(r["recommendation_status"],"EARLY SIGNAL");self.assertEqual(r["drivers"]["radar"]["requirements"]["credible_recent_external_project"],True)
    def test_curated_upstream_name_alone_is_not_enough(self):
        ext={"available":True,"external_merged_prs":3,"substantive_external_prs":0,"verified_external_project_prs":0,"recognized_upstream_prs":0,"core_path_prs":0,"maintainer_accepted_prs":0,"maintainer_accepted_core_path_prs":0,"recent_window_days":180,"recent_external_merged_prs":3,"recent_verified_external_project_prs":0,"recent_recognized_upstream_prs":0,"recent_core_path_prs":0,"recent_maintainer_accepted_prs":0,"recent_maintainer_accepted_core_path_prs":0,"prs":[]}
        r=score_candidate(self.make_candidate(external_validation=ext));self.assertNotIn(r["recommendation_status"],{"EARLY SIGNAL","STRONG SIGNAL"})
    def test_high_visibility_is_proven_not_emerging(self):
        r=score_candidate(self.make_candidate(followers=4100,repositories=[{"name":"sgl-project/sglang","url":"https://github.com/sgl-project/sglang","stars":35000,"contributions":100,"owner_login":"sgl-project"}],external_validation=self.strong_external()));self.assertEqual(r["recommendation_status"],"PROVEN / ALREADY VISIBLE");self.assertFalse(r["early_signal"])
    def test_no_history_does_not_infer_acceleration(self):
        r=score_candidate(self.make_candidate(external_validation=self.strong_external(),recent_events_7d=20,recent_events_30d=30,recent_events_90d=30,observed_event_span_days=7,momentum_coverage={"history_sufficient":False,"sample_truncated":False}));self.assertLessEqual(r["momentum"],58);self.assertNotIn(r["recommendation_status"],{"EARLY SIGNAL","STRONG SIGNAL"});self.assertFalse(r["drivers"]["momentum"]["history_sufficient"])
    def test_truncated_public_event_sample_caps_momentum(self):
        r=score_candidate(self.make_candidate(momentum_coverage={"history_sufficient":True,"sample_truncated":True}));self.assertLessEqual(r["momentum"],65);self.assertTrue(r["drivers"]["momentum"]["sample_truncated"])
    def test_noise_blocks_emerging_recommendation(self):
        r=score_candidate(self.make_candidate(noise={"status":"flagged","reasons":["course_or_exercise_repository_pattern"]},external_validation=self.strong_external()));self.assertNotIn(r["recommendation_status"],{"STRONG SIGNAL","EARLY SIGNAL"})

if __name__=="__main__":unittest.main()
