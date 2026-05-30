from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.contract_coverage_packet_v3 import (
    ALLOWED_NEXT_ACTION_CLASSIFICATIONS,
    MUTATION_FLAGS,
    REQUIRED_INPUT_FAMILIES,
    REQUIRED_OUTPUT_KINDS,
    assert_valid_contract_coverage_packet_v3,
    validate_contract_coverage_packet_v3,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "agent_readiness_contract_v3"
    / "coverage_packet_v3.json"
)

REQUIRED_ATTESTATIONS = {
    "no_live_llm",
    "no_devhub_access",
    "no_user_data",
    "no_official_action",
}


class AgentReadinessContractV3Test(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def _invalid_errors(self, packet: dict) -> str:
        errors = validate_contract_coverage_packet_v3(packet)
        self.assertTrue(errors)
        return "; ".join(errors)

    def test_packet_is_valid_fixture_first_contract_coverage(self) -> None:
        self.assertEqual(validate_contract_coverage_packet_v3(self.packet), [])
        assert_valid_contract_coverage_packet_v3(self.packet)

    def test_packet_consumes_required_families(self) -> None:
        consumed = {source["family"] for source in self.packet["consumed_fixture_packets"]}
        self.assertEqual(consumed, REQUIRED_INPUT_FAMILIES)
        self.assertTrue(
            all(
                source["fixture_path"].startswith("ppd/tests/fixtures/")
                for source in self.packet["consumed_fixture_packets"]
            )
        )
        self.assertTrue(all(source["offline_only"] for source in self.packet["consumed_fixture_packets"]))

    def test_expected_api_outputs_cover_required_agent_responses_with_citations(self) -> None:
        evidence_ids = {evidence["evidence_id"] for evidence in self.packet["source_evidence"]}
        outputs = self.packet["expected_api_outputs"]

        self.assertEqual({output["kind"] for output in outputs}, REQUIRED_OUTPUT_KINDS)
        for output in outputs:
            with self.subTest(output=output["kind"]):
                citations = output.get("citations", [])
                self.assertTrue(citations)
                self.assertTrue(set(citations).issubset(evidence_ids))
                self.assertIn(output["next_action_classification"], ALLOWED_NEXT_ACTION_CLASSIFICATIONS)
                self.assertTrue(output["process_refs"])
                self.assertTrue(output["gap_analysis_refs"])
                self.assertTrue(output["guardrail_refs"])
                self.assertIn("message", output["expected_api_output"])
                self.assertTrue(output["expected_api_output"]["message"])

    def test_drafts_blocks_and_next_actions_preserve_read_only_boundaries(self) -> None:
        outputs = {output["kind"]: output for output in self.packet["expected_api_outputs"]}

        preview = outputs["reversible_draft_preview"]["expected_api_output"]
        self.assertEqual(preview["mode"], "reversible_draft_preview_only")
        self.assertTrue(preview["rollback_available"])
        self.assertFalse(preview["writes_to_devhub"])

        blocked = outputs["blocked_action_explanation"]["expected_api_output"]
        self.assertTrue(blocked["blocked"])
        self.assertEqual(blocked["blocked_action"], "official_record_change")
        self.assertIn("attended review", blocked["message"])

        next_action = outputs["next_safe_read_only_action"]["expected_api_output"]
        self.assertEqual(next_action["action_class"], "read_only")
        self.assertFalse(next_action["requires_devhub_login"])
        self.assertFalse(next_action["changes_official_record"])

    def test_validation_commands_and_attestations_are_offline_and_non_mutating(self) -> None:
        attestations = self.packet["attestations"]
        self.assertEqual(set(attestations), REQUIRED_ATTESTATIONS)
        self.assertTrue(all(attestations.values()))

        commands = self.packet["offline_validation_commands"]
        self.assertIn(["python3", "-m", "unittest", "discover", "-s", "ppd/tests", "-p", "test_*.py"], commands)
        self.assertTrue(all(command[0] == "python3" for command in commands))
        self.assertFalse(any("curl" in part or "devhub" in part.lower() for command in commands for part in command))

    def test_rejects_uncited_api_expectations(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["expected_api_outputs"][0]["citations"] = []
        self.assertIn("must include citations", self._invalid_errors(packet))

    def test_rejects_missing_process_gap_and_guardrail_references(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["expected_api_outputs"][0]["process_refs"] = []
        packet["expected_api_outputs"][1]["gap_analysis_refs"] = []
        packet["expected_api_outputs"][2]["guardrail_refs"] = []
        errors = self._invalid_errors(packet)
        self.assertIn("needs process_refs", errors)
        self.assertIn("needs gap_analysis_refs", errors)
        self.assertIn("needs guardrail_refs", errors)

    def test_rejects_unsupported_next_action_classification(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["expected_api_outputs"][0]["next_action_classification"] = "complete_devhub_submission"
        self.assertIn("unsupported next_action_classification", self._invalid_errors(packet))

    def test_rejects_private_user_facts_authenticated_values_and_raw_artifacts(self) -> None:
        cases = [
            ("property_address", "123 Main Street", "private user facts"),
            ("devhub_session", "session-token", "authenticated DevHub values"),
            ("browser_trace", "trace.zip", "raw document/session/browser artifacts"),
        ]
        for key, value, expected in cases:
            with self.subTest(key=key):
                packet = copy.deepcopy(self.packet)
                packet["expected_api_outputs"][0]["expected_api_output"][key] = value
                self.assertIn(expected, self._invalid_errors(packet))

    def test_rejects_live_completion_claims_guarantees_and_official_action_language(self) -> None:
        cases = [
            ("DevHub completed the record change.", "live LLM or DevHub completion claims"),
            ("The permit will be approved.", "legal or permitting outcome guarantees"),
            ("I will submit the application now.", "final submission/payment/upload/scheduling/cancellation language"),
        ]
        for message, expected in cases:
            with self.subTest(message=message):
                packet = copy.deepcopy(self.packet)
                packet["expected_api_outputs"][0]["expected_api_output"]["message"] = message
                self.assertIn(expected, self._invalid_errors(packet))

    def test_rejects_active_mutation_flags(self) -> None:
        for flag in sorted(MUTATION_FLAGS):
            with self.subTest(flag=flag):
                packet = copy.deepcopy(self.packet)
                packet[flag] = True
                self.assertIn(f"mutation flag {flag}", self._invalid_errors(packet))


if __name__ == "__main__":
    unittest.main()
