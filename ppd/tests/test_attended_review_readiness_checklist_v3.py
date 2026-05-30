from __future__ import annotations

import unittest
from pathlib import Path

from ppd.agent_readiness.attended_review_readiness_checklist_v3 import (
    CHECKLIST_VERSION,
    ChecklistFixtureError,
    build_attended_review_readiness_checklist_v3,
    load_fixture_packet,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "agent_readiness"
    / "attended_review_readiness_inputs_v3.json"
)


class AttendedReviewReadinessChecklistV3Test(unittest.TestCase):
    def test_builds_cited_human_review_rows_from_all_input_artifacts(self) -> None:
        packet = load_fixture_packet(FIXTURE_PATH)

        checklist = build_attended_review_readiness_checklist_v3(packet)

        self.assertEqual(checklist["checklist_version"], CHECKLIST_VERSION)
        self.assertEqual(
            checklist["generated_from"],
            [
                "inactive_migration_bundle_acceptance_packet_v2",
                "guardrail_regression_replay_matrix_v3",
                "public_source_freshness_watch_plan_v3",
            ],
        )
        rows = checklist["checklist_rows"]
        self.assertEqual(len(rows), 8)
        self.assertTrue(any(row["row_id"] == "migration::bundle-inactive-status" for row in rows))
        self.assertTrue(any(row["row_id"] == "guardrail::payment-submit-block" for row in rows))
        self.assertTrue(any(row["row_id"] == "freshness::single-pdf-process" for row in rows))
        for row in rows:
            self.assertGreater(len(row["cited_evidence"]), 0)
            self.assertIn("human_review_question", row)
            self.assertIn("required_attended_action", row)
            self.assertIn("side_effect_boundary", row)

    def test_carries_unresolved_deferrals_and_fixture_only_acceptance(self) -> None:
        packet = load_fixture_packet(FIXTURE_PATH)

        checklist = build_attended_review_readiness_checklist_v3(packet)

        deferrals = checklist["unresolved_deferrals"]
        self.assertEqual(
            {item["deferral_id"] for item in deferrals},
            {
                "migration-live-promotion-deferred",
                "devhub-ui-drift-replay-deferred",
                "public-source-live-refresh-deferred",
            },
        )
        criteria = checklist["fixture_only_acceptance_criteria"]
        self.assertEqual(
            [item["criterion_id"] for item in criteria],
            [
                "fixture-only-inputs",
                "cited-human-review-rows",
                "deferrals-remain-explicit",
            ],
        )

    def test_includes_rollback_validation_commands_and_required_attestations(self) -> None:
        packet = load_fixture_packet(FIXTURE_PATH)

        checklist = build_attended_review_readiness_checklist_v3(packet)

        self.assertEqual(
            checklist["rollback_verification"][0]["check_id"],
            "rollback-fixture-only",
        )
        self.assertIn(
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
            checklist["offline_validation_commands"],
        )
        self.assertEqual(
            checklist["attestations"],
            {
                "no_live_crawl": True,
                "no_authentication": True,
                "no_release": True,
                "no_official_action": True,
                "fixture_first": True,
                "future_attended_review_only": True,
            },
        )

    def test_rejects_missing_or_false_boundary_attestations(self) -> None:
        packet = load_fixture_packet(FIXTURE_PATH)
        packet["attestations"]["no_authentication"] = False

        with self.assertRaises(ChecklistFixtureError):
            build_attended_review_readiness_checklist_v3(packet)


if __name__ == "__main__":
    unittest.main()
