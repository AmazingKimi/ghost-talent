import unittest
from datetime import datetime, timezone

from ghost_talent.sources.github import GitHubSource


class GitHubEvidenceTests(unittest.TestCase):
    def test_docs_kernel_name_is_not_core_path(self):
        self.assertFalse(GitHubSource._is_core_path("docs/source/design/kernel.md"))

    def test_test_cpp_is_not_core_path(self):
        self.assertFalse(GitHubSource._is_core_path("tests/runtime/test_kernel.cpp"))

    def test_real_cuda_runtime_file_is_core_path(self):
        self.assertTrue(GitHubSource._is_core_path("csrc/runtime/attention_kernel.cu"))

    def test_watch_and_fork_events_do_not_count_as_momentum(self):
        now=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        events=[
            {"type":"WatchEvent","created_at":now},
            {"type":"ForkEvent","created_at":now},
            {"type":"IssuesEvent","created_at":now},
            {"type":"PushEvent","created_at":now},
        ]
        counts=GitHubSource._event_counts(events)
        self.assertEqual(counts["recent_events_7d"],1)
        self.assertEqual(counts["momentum_coverage"]["meaningful_events_sampled"],1)


if __name__=="__main__":unittest.main()
