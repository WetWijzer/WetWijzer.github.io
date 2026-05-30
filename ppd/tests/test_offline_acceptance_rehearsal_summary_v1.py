from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.offline_acceptance_rehearsal_summary_v1 import (
    CONSUMES,
    REQUIRED_ATTESTATIONS,
    OfflineAcceptanceSummaryError,
    build_offline_acceptance_rehearsal_summary_v1,
    validate_offline_acceptance_rehearsal_summary_v1,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "offline_acceptance_rehearsal_summary_v1" / "source_inputs.json"


class OfflineAcceptanceRehearsalSummaryV1Test(unittest.TestCase):
    def load_inputs(self) -> dict[str, object]:
        with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def valid_summary(self) -> dict[str, object]:
        return build_offline_acceptance_rehearsal_summary_v1(self.load_inputs())

    def issue_codes(self, packet: dict[str, object]) -> set[str]:
        return {issue.code for issue in validate_offline_acceptance_rehearsal_summary_v1(packet)}

    def test_builds_cited_summary_from_four_fixture_packets(self) -> None:
        summary = self.valid_summary()

        self.assertEqual(summary["packet_version"], "offline-acceptance-rehearsal-summary-v1")
        self.assertEqual(summary["consumes"], list(CONSUMES))
        self.assertEqual(summary["attestations"], REQUIRED_ATTESTATIONS)
        self.assertGreaterEqual(len(summary["acceptance_rows"]), 6)
        self.assertGreaterEqual(len(summary["manual_review_blockers"]), 2)
        self.assertEqual(len(summary["unresolved_deferrals"]), 1)
        self.assertEqual(summary["deferral_handling"]["status"], "unresolved_deferrals_present")
        self.assertGreaterEqual(len(summary["rollback_checkpoints"]), 4)
        self.assertIn(["python3", "ppd/daemon/ppd_daemon.py", "--self-test"], summary["validation_command_inventory"])

        for section_name in ("acceptance_rows", "manual_review_blockers", "unresolved_deferrals", "rollback_checkpoints"):
            for row in summary[section_name]:
                self.assertTrue(row["id"])
                self.assertTrue(row["summary"])
                self.assertTrue(row["citations"])

        self.assertEqual(validate_offline_acceptance_rehearsal_summary_v1(summary), [])

    def test_rejects_live_devhub_or_private_artifact_claims(self) -> None:
        inputs = self.load_inputs()
        replay_queue = inputs["guardrail_regression_replay_queue_v1"]
        assert isinstance(replay_queue, dict)
        replay_queue["uses_devhub_session"] = True

        with self.assertRaises(OfflineAcceptanceSummaryError) as raised:
            build_offline_acceptance_rehearsal_summary_v1(inputs)

        self.assertIn("forbidden_true_flag", str(raised.exception))

    def test_rejects_missing_consumed_packet(self) -> None:
        inputs = self.load_inputs()
        del inputs["action_journal_replay_findings_v1"]

        with self.assertRaises(OfflineAcceptanceSummaryError) as raised:
            build_offline_acceptance_rehearsal_summary_v1(inputs)

        self.assertIn("missing_input", str(raised.exception))

    def test_rejects_uncited_acceptance_rows(self) -> None:
        summary = self.valid_summary()
        row = summary["acceptance_rows"][0]
        assert isinstance(row, dict)
        row["citations"] = []

        self.assertIn("missing_citations", self.issue_codes(summary))

    def test_rejects_missing_blocker_deferral_rollback_and_command_inventory(self) -> None:
        cases = [
            ("manual_review_blockers", "missing_required_section"),
            ("rollback_checkpoints", "missing_required_section"),
            ("validation_command_inventory", "missing_required_section"),
            ("deferral_handling", "missing_deferral_handling"),
        ]
        for key, expected_code in cases:
            with self.subTest(key=key):
                summary = self.valid_summary()
                del summary[key]
                self.assertIn(expected_code, self.issue_codes(summary))

    def test_rejects_private_authenticated_session_browser_raw_or_downloaded_artifacts(self) -> None:
        forbidden_keys = [
            "auth_state",
            "browser_state",
            "devhub_session",
            "downloaded_artifact",
            "private_artifact",
            "raw_crawl_output",
            "raw_downloaded_artifact",
            "session_state",
            "trace_file",
        ]
        for key in forbidden_keys:
            with self.subTest(key=key):
                summary = self.valid_summary()
                summary[key] = "fixture value"
                self.assertIn("forbidden_artifact_key", self.issue_codes(summary))

    def test_rejects_live_execution_promotion_and_active_mutation_flags(self) -> None:
        forbidden_flags = [
            "live_execution_performed",
            "promotion_executed",
            "active_source_registry_mutated",
            "active_surface_registry_mutated",
            "active_guardrail_state_mutated",
            "prompt_state_mutated",
            "release_state_mutated",
            "agent_state_mutated",
        ]
        for flag in forbidden_flags:
            with self.subTest(flag=flag):
                summary = self.valid_summary()
                summary[flag] = True
                self.assertIn("forbidden_true_flag", self.issue_codes(summary))

    def test_rejects_legal_or_permitting_outcome_guarantees(self) -> None:
        summary = self.valid_summary()
        row = summary["acceptance_rows"][0]
        assert isinstance(row, dict)
        row["summary"] = "This offline row says permit will be approved."

        self.assertIn("forbidden_outcome_guarantee", self.issue_codes(summary))

    def test_rejects_consequential_action_language(self) -> None:
        summary = self.valid_summary()
        row = summary["acceptance_rows"][0]
        assert isinstance(row, dict)
        row["summary"] = "This offline row says submit permit after review."

        self.assertIn("forbidden_consequential_action_language", self.issue_codes(summary))

    def test_rejects_active_state_mutation_language(self) -> None:
        summary = self.valid_summary()
        summary["rollback_checkpoints"] = copy.deepcopy(summary["rollback_checkpoints"])
        row = summary["rollback_checkpoints"][0]
        assert isinstance(row, dict)
        row["summary"] = "This candidate mutated active source registry during rehearsal."

        self.assertIn("forbidden_active_state_mutation", self.issue_codes(summary))


if __name__ == "__main__":
    unittest.main()
