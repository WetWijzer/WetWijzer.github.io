from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from ppd.agent_readiness.agent_readiness_replay_packet_v2 import (
    build_agent_readiness_replay_packet_v2_from_fixture,
    validate_agent_readiness_replay_packet_v2,
)

FIXTURE = Path(__file__).parent / "fixtures" / "agent_readiness_replay_packet_v2" / "source_packets.json"


class AgentReadinessReplayPacketV2Tests(unittest.TestCase):
    def packet(self) -> dict[str, object]:
        return build_agent_readiness_replay_packet_v2_from_fixture(FIXTURE)

    def problems(self, packet: dict[str, object]) -> str:
        result = validate_agent_readiness_replay_packet_v2(packet)
        self.assertFalse(result.valid)
        return "; ".join(result.problems)

    def test_builds_valid_fixture_first_replay_packet(self) -> None:
        packet = self.packet()
        result = validate_agent_readiness_replay_packet_v2(packet)
        self.assertTrue(result.valid, result.problems)
        self.assertTrue(packet["attestations"]["no_live_llm"])
        self.assertTrue(packet["attestations"]["no_devhub"])
        self.assertTrue(packet["attestations"]["no_user_data"])
        self.assertTrue(packet["attestations"]["no_official_action"])
        self.assertTrue(packet["attestations"]["no_source_mutation"])
        self.assertTrue(packet["attestations"]["no_surface_registry_mutation"])
        self.assertTrue(packet["attestations"]["no_release_state_mutation"])

    def test_emits_cited_prompts_notices_blocks_and_safe_actions(self) -> None:
        packet = self.packet()
        self.assertGreaterEqual(len(packet["expected_missing_fact_prompts"]), 2)
        self.assertGreaterEqual(len(packet["stale_evidence_notices"]), 1)
        self.assertGreaterEqual(len(packet["conflicting_evidence_notices"]), 1)
        self.assertGreaterEqual(len(packet["blocked_action_explanations"]), 2)
        self.assertGreaterEqual(len(packet["next_safe_actions"]), 2)
        for field in (
            "expected_missing_fact_prompts",
            "stale_evidence_notices",
            "conflicting_evidence_notices",
            "blocked_action_explanations",
            "next_safe_actions",
            "reviewer_owner_fields",
        ):
            for item in packet[field]:
                self.assertTrue(item["source_evidence_ids"], field)

    def test_rejects_missing_reviewer_owner_fields(self) -> None:
        packet = self.packet()
        packet["reviewer_owner_fields"] = []
        self.assertIn("reviewer_owner_fields must be non-empty", self.problems(packet))

    def test_rejects_uncited_replay_expectations(self) -> None:
        packet = self.packet()
        packet["expected_missing_fact_prompts"][0]["source_evidence_ids"] = []
        self.assertIn("expected_missing_fact_prompts[0].source_evidence_ids must cite fixture evidence", self.problems(packet))

    def test_rejects_unknown_citation(self) -> None:
        packet = self.packet()
        packet["next_safe_actions"][0]["source_evidence_ids"] = ["missing:evidence"]
        self.assertIn("next_safe_actions[0].source_evidence_ids cites unknown evidence id missing:evidence", self.problems(packet))

    def test_rejects_missing_gap_analysis_reference(self) -> None:
        packet = self.packet()
        packet["input_packet_ids"]["user_gap_analysis_fixture"] = "missing-gap-fixture"
        packet["expected_missing_fact_prompts"][0]["source_evidence_ids"] = ["proposal-v2:offline-validation"]
        problems = self.problems(packet)
        self.assertIn("input_packet_ids.user_gap_analysis_fixture must reference a gap-analysis fixture", problems)
        self.assertIn("expected_missing_fact_prompts[0].source_evidence_ids must cite gap-analysis evidence", problems)

    def test_rejects_missing_guardrail_reference(self) -> None:
        packet = self.packet()
        packet["input_packet_ids"]["guardrail_bundle_fixture"] = "missing-guardrail-fixture"
        packet["blocked_action_explanations"][0]["source_evidence_ids"] = ["proposal-v2:offline-validation"]
        problems = self.problems(packet)
        self.assertIn("input_packet_ids.guardrail_bundle_fixture must reference a guardrail bundle fixture", problems)
        self.assertIn("blocked_action_explanations[0].source_evidence_ids must cite guardrail evidence", problems)

    def test_rejects_unsupported_next_action_classification(self) -> None:
        packet = self.packet()
        packet["next_safe_actions"][0]["action_class"] = "official_submission"
        self.assertIn("next_safe_actions[0].action_class must be one of", self.problems(packet))

    def test_rejects_private_user_facts_and_authenticated_devhub_values(self) -> None:
        packet = self.packet()
        packet["user_facts"] = {"project_address": "private"}
        packet["devhub_authenticated_values"] = {"permit_cart": "redacted-but-not-allowed"}
        problems = self.problems(packet)
        self.assertIn("must not include private user facts, authenticated values, or raw session/browser artifacts", problems)

    def test_rejects_raw_document_session_and_browser_artifacts(self) -> None:
        packet = self.packet()
        packet["raw_pdf"] = "raw document bytes"
        packet["session_state"] = {"cookie": "redacted"}
        packet["browser_context"] = "playwright trace file"
        problems = self.problems(packet)
        self.assertIn("must not include private user facts, authenticated values, or raw session/browser artifacts", problems)
        self.assertIn("contains forbidden replay-packet safety language", problems)

    def test_rejects_live_llm_or_devhub_completion_claims(self) -> None:
        packet = self.packet()
        packet["notes"] = "The live LLM completed the replay and opened DevHub."
        self.assertIn("contains forbidden replay-packet safety language", self.problems(packet))

    def test_rejects_legal_or_permitting_outcome_guarantees(self) -> None:
        packet = self.packet()
        packet["notes"] = "Permit will be approved and compliance guaranteed."
        self.assertIn("contains forbidden replay-packet safety language", self.problems(packet))

    def test_rejects_final_official_action_language(self) -> None:
        packet = self.packet()
        packet["notes"] = "Final submission is ready; submit payment and schedule inspection."
        self.assertIn("contains forbidden replay-packet safety language", self.problems(packet))

    def test_rejects_active_mutation_flags(self) -> None:
        packet = self.packet()
        packet = deepcopy(packet)
        packet["active_prompt_mutation"] = True
        packet["active_guardrail_mutation"] = True
        packet["active_source_mutation"] = True
        packet["active_surface_registry_mutation"] = True
        packet["active_release_state_mutation"] = True
        packet["active_agent_state_mutation"] = True
        self.assertIn("must not declare active prompt, guardrail, source, surface-registry, release-state, or agent-state mutation", self.problems(packet))

    def test_rejects_missing_required_attestations(self) -> None:
        packet = self.packet()
        packet = deepcopy(packet)
        packet["attestations"]["no_live_llm"] = False
        self.assertIn("attestations.no_live_llm must be true", self.problems(packet))


if __name__ == "__main__":
    unittest.main()
