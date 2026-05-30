import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.agent_prompt_refresh_acceptance_packet import (
    AgentPromptRefreshAcceptancePacketError,
    assert_valid_agent_prompt_refresh_acceptance_packet,
    validate_agent_prompt_refresh_acceptance_packet,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "agent_prompt_refresh_acceptance_packet"
    / "valid_acceptance_packet.json"
)


class AgentPromptRefreshAcceptancePacketTest(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_valid_fixture_passes(self):
        result = validate_agent_prompt_refresh_acceptance_packet(self.packet)
        self.assertTrue(result.valid, result.problems)
        assert_valid_agent_prompt_refresh_acceptance_packet(self.packet)

    def test_rejects_uncited_decisions_and_missing_rationales(self):
        packet = copy.deepcopy(self.packet)
        packet["acceptance_decisions"][0]["source_evidence_ids"] = []
        packet["acceptance_decisions"][1].pop("deferred_rationale")
        packet["acceptance_decisions"][2].pop("rejected_rationale")

        result = validate_agent_prompt_refresh_acceptance_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("acceptance_decisions[0].source_evidence_ids is required", result.problems)
        self.assertIn("acceptance_decisions[1].deferred_rationale is required", result.problems)
        self.assertIn("acceptance_decisions[2].rejected_rationale is required", result.problems)

    def test_rejects_missing_scenario_or_blocked_action_references(self):
        packet = copy.deepcopy(self.packet)
        packet["acceptance_decisions"][0]["scenario_refs"] = []
        packet["acceptance_decisions"][0]["blocked_action_refs"] = []

        result = validate_agent_prompt_refresh_acceptance_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("acceptance_decisions[0] must reference scenario_refs or blocked_action_refs", result.problems)

    def test_rejects_missing_review_controls(self):
        packet = copy.deepcopy(self.packet)
        packet["rollback_notes"] = []
        packet["reviewer_owners"] = []
        packet["offline_validation_commands"] = []

        result = validate_agent_prompt_refresh_acceptance_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("rollback_notes must be a non-empty list", result.problems)
        self.assertIn("reviewer_owners must be a non-empty list", result.problems)
        self.assertIn("offline_validation_commands must be a non-empty list of commands", result.problems)

    def test_rejects_private_case_facts_raw_auth_values_and_local_paths(self):
        packet = copy.deepcopy(self.packet)
        packet["private_case_facts"] = {"address": "private applicant address"}
        packet["raw_authenticated_values"] = {"permit_number": "private-authenticated-value"}
        packet["local_path"] = "/home/alex/devhub/session.json"

        result = validate_agent_prompt_refresh_acceptance_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("private case facts are not allowed at $.private_case_facts", result.problems)
        self.assertIn("raw authenticated values are not allowed at $.raw_authenticated_values", result.problems)
        self.assertIn("local private paths are not allowed at $.local_path", result.problems)

    def test_rejects_live_execution_claims_and_outcome_guarantees(self):
        packet = copy.deepcopy(self.packet)
        packet["review_summary"] = "Opened DevHub and ran the processor during acceptance review."
        packet["guarantee"] = "The permit will be approved."

        result = validate_agent_prompt_refresh_acceptance_packet(packet)

        self.assertFalse(result.valid)
        self.assertTrue(any("live LLM, DevHub, crawler, or processor execution claims" in problem for problem in result.problems))
        self.assertTrue(any("legal or permitting outcome guarantees" in problem for problem in result.problems))

    def test_rejects_enabled_consequential_controls_and_active_mutation_flags(self):
        packet = copy.deepcopy(self.packet)
        packet["payment_enabled"] = True
        packet["active_prompt_mutation"] = True
        packet["active_guardrail_mutation"] = True
        packet["active_surface_registry_mutation"] = True
        packet["active_monitoring_mutation"] = True
        packet["active_release_state_mutation"] = True
        packet["active_agent_state_mutation"] = True

        result = validate_agent_prompt_refresh_acceptance_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("enabled consequential controls are not allowed at $.payment_enabled", result.problems)
        self.assertIn("active mutation flag is not allowed at $.active_prompt_mutation", result.problems)
        self.assertIn("active mutation flag is not allowed at $.active_guardrail_mutation", result.problems)
        self.assertIn("active mutation flag is not allowed at $.active_surface_registry_mutation", result.problems)
        self.assertIn("active mutation flag is not allowed at $.active_monitoring_mutation", result.problems)
        self.assertIn("active mutation flag is not allowed at $.active_release_state_mutation", result.problems)
        self.assertIn("active mutation flag is not allowed at $.active_agent_state_mutation", result.problems)

    def test_assert_helper_raises(self):
        packet = copy.deepcopy(self.packet)
        packet["acceptance_decisions"] = []

        with self.assertRaises(AgentPromptRefreshAcceptancePacketError):
            assert_valid_agent_prompt_refresh_acceptance_packet(packet)


if __name__ == "__main__":
    unittest.main()
