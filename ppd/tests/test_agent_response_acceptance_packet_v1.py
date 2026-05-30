from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.agent_response_acceptance_packet_v1 import (
    OFFLINE_VALIDATION_COMMANDS,
    REQUIRED_ATTESTATIONS,
    REQUIRED_EXAMPLE_KINDS,
    AgentResponseAcceptancePacketV1Error,
    build_agent_response_acceptance_packet_v1,
    load_agent_response_acceptance_fixture,
    validate_agent_response_acceptance_packet_v1,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_response_acceptance_packet_v1" / "acceptance_inputs.json"


class GuardedAgentResponseAcceptancePacketV1Test(unittest.TestCase):
    def fixture(self) -> dict:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def packet(self) -> dict:
        return load_agent_response_acceptance_fixture(FIXTURE_PATH)

    def build(self, fixture: dict) -> dict:
        return build_agent_response_acceptance_packet_v1(
            guardrail_to_agent_explanation_packet=fixture["guardrail_to_agent_explanation_packet"],
            offline_agent_readiness_adapter_outputs=fixture["offline_agent_readiness_adapter_outputs"],
            user_gap_analysis_to_draft_preview_bridge_v1=fixture["user_gap_analysis_to_draft_preview_bridge_v1"],
            action_journal_replay_fixture=fixture["action_journal_replay_fixture"],
        )

    def test_builds_fixture_first_guarded_agent_response_acceptance_packet(self) -> None:
        packet = self.packet()

        self.assertEqual(packet["packet_type"], "ppd.guarded_agent_response_acceptance_packet.v1")
        self.assertTrue(packet["fixture_first"])
        self.assertTrue(packet["metadata_only"])
        self.assertEqual(packet["process_id"], "ppd-single-pdf-plan-review-v1")
        self.assertEqual(packet["guardrail_bundle_id"], "guardrail-explanation-single-pdf-v1")
        self.assertEqual(packet["offline_validation_commands"], OFFLINE_VALIDATION_COMMANDS)
        self.assertEqual(validate_agent_response_acceptance_packet_v1(packet), [])
        for attestation in REQUIRED_ATTESTATIONS:
            self.assertIs(packet["attestations"][attestation], True)

    def test_covers_required_final_response_examples_with_citations(self) -> None:
        packet = self.packet()
        examples = {example["example_kind"]: example for example in packet["final_response_examples"]}

        self.assertEqual(set(examples), set(REQUIRED_EXAMPLE_KINDS))
        for kind, example in examples.items():
            with self.subTest(kind=kind):
                self.assertTrue(example["final_response"])
                self.assertTrue(example["citations"])
                self.assertTrue(example["consumed_input_refs"])
                self.assertFalse(example["safety"]["live_llm_used"])
                self.assertFalse(example["safety"]["devhub_used"])
                self.assertFalse(example["safety"]["private_data_used"])
                self.assertFalse(example["safety"]["official_action_performed"])

    def test_examples_consume_expected_input_packets(self) -> None:
        packet = self.packet()
        refs = packet["input_refs"]

        self.assertEqual(refs["guardrail_to_agent_explanation_packet"], "ppd.guardrail_to_agent_explanation_packet.v1")
        self.assertEqual(refs["guardrail_bundle_id"], "guardrail-explanation-single-pdf-v1")
        self.assertEqual(refs["action_journal_replay_packet"], "action-journal-acceptance-packet-v1")
        self.assertIn("missing_information_prompt", refs["offline_agent_readiness_adapter_output_kinds"])
        self.assertEqual(refs["draft_preview_bridge_analysis_id"], "user-gap-analysis::handoff-v4::agent-response-acceptance")

    def test_missing_facts_stale_evidence_reversible_limits_blocks_and_next_steps_are_represented(self) -> None:
        examples = {example["example_kind"]: example for example in self.packet()["final_response_examples"]}

        self.assertEqual(examples["missing_facts"]["missing_items"], ["project_scope_summary", "single_pdf_plan_set"])
        self.assertEqual(
            examples["stale_conflicting_evidence"]["bridge_notice_ids"],
            ["stale_evidence::fixture-user-upload-inventory", "conflicting_evidence::fixture-plan-set-label-conflict"],
        )
        self.assertEqual(
            examples["reversible_draft_limits"]["blocked_field_ids"],
            ["draft-field::project-scope", "draft-field::plan-set-readiness"],
        )
        self.assertEqual(
            examples["blocked_official_actions"]["blocked_action_ids"],
            ["submit-permit-request", "upload-plans-to-official-record", "pay-review-fees"],
        )
        self.assertEqual(
            examples["next_safe_read_only_steps"]["read_only_action_ids"],
            ["read::review-single-pdf-guidance", "read::review-devhub-submit-guide"],
        )

    def test_rejects_missing_adapter_examples(self) -> None:
        fixture = self.fixture()
        fixture["offline_agent_readiness_adapter_outputs"] = fixture["offline_agent_readiness_adapter_outputs"][:1]

        with self.assertRaises(AgentResponseAcceptancePacketV1Error) as caught:
            self.build(fixture)

        self.assertTrue(any("offline adapter outputs missing" in problem for problem in caught.exception.problems))

    def test_rejects_private_raw_mutating_and_official_action_material(self) -> None:
        fixture = self.fixture()
        fixture["offline_agent_readiness_adapter_outputs"][0]["private_value"] = "unredacted"
        fixture["user_gap_analysis_to_draft_preview_bridge_v1"]["raw_html"] = "private"
        fixture["action_journal_replay_fixture"]["active_prompt_mutation"] = True

        with self.assertRaises(AgentResponseAcceptancePacketV1Error) as caught:
            self.build(fixture)

        problems = caught.exception.problems
        self.assertTrue(any("private data field" in problem for problem in problems))
        self.assertTrue(any("raw document, session, or browser artifact" in problem for problem in problems))
        self.assertTrue(any("active prompt" in problem for problem in problems))

    def test_rejects_unsupported_process_or_guardrail_ids(self) -> None:
        fixture = self.fixture()
        fixture["guardrail_to_agent_explanation_packet"]["process_id"] = "unsupported-process"
        fixture["user_gap_analysis_to_draft_preview_bridge_v1"]["process_id"] = "unsupported-process"
        fixture["guardrail_to_agent_explanation_packet"]["guardrail_bundle_id"] = "unsupported-guardrail"

        with self.assertRaises(AgentResponseAcceptancePacketV1Error) as caught:
            self.build(fixture)

        problems = caught.exception.problems
        self.assertTrue(any("unsupported process_id" in problem for problem in problems))
        self.assertTrue(any("unsupported guardrail_bundle_id" in problem for problem in problems))

    def test_rejects_unsafe_final_response_language_or_missing_citations(self) -> None:
        packet = copy.deepcopy(self.packet())
        packet["final_response_examples"][0]["final_response"] = "This guarantees approval."
        packet["final_response_examples"][1]["citations"] = []
        packet["final_response_examples"][2]["safety"]["devhub_used"] = True

        errors = validate_agent_response_acceptance_packet_v1(packet)

        self.assertTrue(any("guarantee" in error for error in errors))
        self.assertTrue(any("citations" in error for error in errors))
        self.assertTrue(any("devhub_used" in error for error in errors))

    def test_rejects_uncited_private_authenticated_and_final_action_language(self) -> None:
        packet = copy.deepcopy(self.packet())
        packet["final_response_examples"][0]["final_response"] = "This is an uncited response example."
        packet["final_response_examples"][1]["final_response"] = "I used an authenticated fact from DevHub."
        packet["final_response_examples"][2]["final_response"] = "I will submit the application and schedule the inspection."
        packet["final_response_examples"][3]["citations"] = ["citation needed"]

        errors = validate_agent_response_acceptance_packet_v1(packet)

        self.assertTrue(any("uncited response example" in error for error in errors))
        self.assertTrue(any("private or authenticated value text" in error for error in errors))
        self.assertTrue(any("final official action language" in error for error in errors))
        self.assertTrue(any("uncited placeholders" in error for error in errors))

    def test_rejects_unsupported_ids_on_built_packet(self) -> None:
        packet = copy.deepcopy(self.packet())
        packet["process_id"] = "unsupported-process"
        packet["guardrail_bundle_id"] = "unsupported-guardrail"

        errors = validate_agent_response_acceptance_packet_v1(packet)

        self.assertTrue(any("unsupported process_id" in error for error in errors))
        self.assertTrue(any("unsupported guardrail_bundle_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
