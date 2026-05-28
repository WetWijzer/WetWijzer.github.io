from __future__ import annotations

import unittest
from pathlib import Path

from ppd.daemon.proposal_size_guard import (
    build_proposal_retry_envelope,
    load_proposal_size_guard_fixture,
    validate_proposal_size_guard_fixture,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "daemon" / "proposal_size_guard_repeated_failures.json"


class ProposalSizeGuardTest(unittest.TestCase):
    def test_repeated_syntax_preflight_failures_recommend_narrow_retry_envelope(self) -> None:
        fixture = load_proposal_size_guard_fixture(FIXTURE_PATH)
        envelope = build_proposal_retry_envelope(fixture)

        self.assertTrue(envelope.guard_active)
        self.assertEqual(envelope.target_task, "checkbox-118")
        self.assertEqual(envelope.repeated_failure_kinds, ("syntax_preflight",))
        self.assertEqual(envelope.max_total_files, 2)
        self.assertEqual(
            envelope.allowed_file_roles,
            ("one_daemon_core_file", "one_daemon_unittest_file"),
        )
        self.assertIn("one-core-file plus one-test", envelope.recommendation)

    def test_fixture_preserves_task_order_and_does_not_complete_domain_tasks(self) -> None:
        fixture = load_proposal_size_guard_fixture(FIXTURE_PATH)
        errors = validate_proposal_size_guard_fixture(fixture)

        self.assertEqual(errors, [])
        self.assertEqual(fixture.get("task_order_changes"), [])
        self.assertEqual(fixture.get("completed_domain_tasks"), [])
        self.assertIs(fixture.get("preserves_task_ordering"), True)
        self.assertIs(fixture.get("marks_domain_tasks_complete"), False)

    def test_repeated_timeout_failures_also_activate_guard(self) -> None:
        fixture = load_proposal_size_guard_fixture(FIXTURE_PATH)
        timeout_fixture = dict(fixture)
        timeout_fixture["failure_history"] = [
            {"target_task": "checkbox-118", "failure_kind": "timeout"},
            {"target_task": "checkbox-118", "failure_kind": "timeout"},
        ]

        envelope = build_proposal_retry_envelope(timeout_fixture)

        self.assertTrue(envelope.guard_active)
        self.assertEqual(envelope.repeated_failure_kinds, ("timeout",))


if __name__ == "__main__":
    unittest.main()
