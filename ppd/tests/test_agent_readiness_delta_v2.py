from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guardrails.agent_readiness_delta_v2 import (  # noqa: E402
    PACKET_VERSION,
    assert_guarded_agent_readiness_delta_packet_v2,
    validate_guarded_agent_readiness_delta_packet_v2,
)


def valid_packet():
    return {
        "packet_version": PACKET_VERSION,
        "schema_delta_placeholders": [
            {"name": "agent_readiness_delta.schema", "status": "placeholder_only"}
        ],
        "expectations": {
            "missing_information_prompts": [
                "Ask for stale, missing, ambiguous, or conflicting user facts."
            ],
            "blocked_action_explanations": [
                "Explain why upload, submit, schedule, certify, cancel, or payment actions are blocked."
            ],
            "reversible_draft_previews": [
                "Preview local draft field mappings before any attended DevHub action."
            ],
        },
        "citation_coverage_placeholders": [
            "Every process, requirement, and guardrail delta must reserve source evidence IDs."
        ],
        "reviewer_acceptance_placeholders": [
            "Reviewer must confirm placeholders, evidence coverage, and blocked-action text."
        ],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "active_prompt_mutation": False,
        "active_contract_mutation": False,
        "active_source_mutation": False,
        "active_surface_mutation": False,
        "active_guardrail_mutation": False,
        "active_release_state_mutation": False,
    }


class GuardedAgentReadinessDeltaPacketV2Test(unittest.TestCase):
    def error_codes(self, packet):
        return {error.code for error in validate_guarded_agent_readiness_delta_packet_v2(packet)}

    def test_accepts_complete_placeholder_only_packet(self):
        packet = valid_packet()
        self.assertEqual([], validate_guarded_agent_readiness_delta_packet_v2(packet))
        assert_guarded_agent_readiness_delta_packet_v2(packet)

    def test_rejects_missing_schema_delta_placeholders(self):
        packet = valid_packet()
        packet["schema_delta_placeholders"] = []
        self.assertIn("missing_schema_delta_placeholders", self.error_codes(packet))

    def test_rejects_missing_prompt_and_action_expectations(self):
        packet = valid_packet()
        packet["expectations"] = {
            "missing_information_prompts": [],
            "blocked_action_explanations": [],
            "reversible_draft_previews": [],
        }
        codes = self.error_codes(packet)
        self.assertIn("missing_missing_information_prompts", codes)
        self.assertIn("missing_blocked_action_explanations", codes)
        self.assertIn("missing_reversible_draft_previews", codes)

    def test_rejects_missing_citation_reviewer_and_validation_placeholders(self):
        packet = valid_packet()
        packet["citation_coverage_placeholders"] = []
        packet["reviewer_acceptance_placeholders"] = []
        packet["validation_commands"] = []
        codes = self.error_codes(packet)
        self.assertIn("missing_citation_coverage_placeholders", codes)
        self.assertIn("missing_reviewer_acceptance_placeholders", codes)
        self.assertIn("missing_validation_commands", codes)

    def test_rejects_private_artifacts_and_live_claims(self):
        packet = valid_packet()
        packet["notes"] = [
            "Includes Playwright trace.zip and storage_state output.",
            "Ran live crawl against authenticated DevHub.",
        ]
        codes = self.error_codes(packet)
        self.assertIn("private_or_session_artifact", codes)
        self.assertIn("live_devhub_or_crawl_claim", codes)

    def test_rejects_official_action_language_and_guarantees(self):
        packet = valid_packet()
        packet["claims"] = [
            "The agent submitted the permit and paid the fee.",
            "This guarantees approval and is legal advice.",
        ]
        codes = self.error_codes(packet)
        self.assertIn("consequential_official_action_language", codes)
        self.assertIn("legal_or_permitting_guarantee", codes)

    def test_rejects_active_mutation_flags(self):
        for field in (
            "active_prompt_mutation",
            "active_contract_mutation",
            "active_source_mutation",
            "active_surface_mutation",
            "active_guardrail_mutation",
            "active_release_state_mutation",
        ):
            packet = valid_packet()
            packet[field] = True
            codes = self.error_codes(packet)
            self.assertIn("active_mutation_flag", codes)

    def test_assert_raises_value_error_for_invalid_packet(self):
        packet = valid_packet()
        packet["validation_commands"] = []
        with self.assertRaises(ValueError):
            assert_guarded_agent_readiness_delta_packet_v2(packet)


if __name__ == "__main__":
    unittest.main()
