from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from ppd.agent_readiness.guardrail_to_agent_explanation_packet_v1 import (
    EXPLANATION_KINDS,
    REQUIRED_ATTESTATIONS,
    GuardrailToAgentExplanationPacketError,
    build_guardrail_to_agent_explanation_packet,
    load_guardrail_to_agent_explanation_fixture,
    validate_guardrail_to_agent_explanation_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "guardrail_to_agent_explanation_packet_v1" / "synthetic_case_packet.json"


class GuardrailToAgentExplanationPacketV1Test(unittest.TestCase):
    def fixture(self) -> dict:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def packet(self) -> dict:
        return load_guardrail_to_agent_explanation_fixture(FIXTURE_PATH)

    def build(self, fixture: dict) -> dict:
        return build_guardrail_to_agent_explanation_packet(
            guardrail_bundle=fixture["guardrail_bundle"],
            user_gap_analysis=fixture["user_gap_analysis"],
            blocked_action_fixtures=fixture["blocked_action_fixtures"],
            agent_readiness_adapter_outputs=fixture["agent_readiness_adapter_outputs"],
            source_evidence=fixture["source_evidence"],
        )

    def test_builds_fixture_first_guardrail_to_agent_explanation_packet(self) -> None:
        packet = self.packet()

        self.assertEqual(packet["packet_type"], "ppd.guardrail_to_agent_explanation_packet.v1")
        self.assertTrue(packet["fixture_first"])
        self.assertTrue(packet["metadata_only"])
        self.assertEqual(packet["explanation_order"], list(EXPLANATION_KINDS))
        self.assertEqual(packet["case_id"], "case-synthetic-guardrail-explanation")
        self.assertEqual(packet["guardrail_bundle_id"], "guardrail-explanation-single-pdf-v1")
        self.assertEqual(validate_guardrail_to_agent_explanation_packet(packet), [])
        for attestation in REQUIRED_ATTESTATIONS:
            self.assertIs(packet["attestations"][attestation], True)

    def test_exposes_all_required_cited_explanation_templates(self) -> None:
        packet = self.packet()
        templates = {template["kind"]: template for template in packet["explanation_templates"]}
        citation_ids = {citation["evidence_id"] for citation in packet["citation_index"]}

        self.assertEqual(set(templates), set(EXPLANATION_KINDS))
        self.assertEqual(templates["missing_facts"]["missing_facts"], ["project_scope_summary"])
        self.assertEqual(templates["missing_facts"]["missing_documents"], ["single_pdf_plan_set"])
        self.assertEqual(templates["stale_conflicting_evidence"]["status"], "refresh_or_human_review_required")
        self.assertTrue(templates["stale_conflicting_evidence"]["stale_evidence"])
        self.assertTrue(templates["stale_conflicting_evidence"]["conflicting_evidence"])
        self.assertIn("adapter-output-next-safe-action", templates["next_safe_read_only_actions"]["readiness_adapter_refs"])
        for template in packet["explanation_templates"]:
            self.assertTrue(template["citation_ids"])
            self.assertTrue(set(template["citation_ids"]).issubset(citation_ids))

    def test_blocked_official_actions_and_reversible_limits_are_fail_closed(self) -> None:
        packet = self.packet()
        templates = {template["kind"]: template for template in packet["explanation_templates"]}
        blocked = templates["blocked_official_actions"]["actions"]
        reversible = templates["reversible_draft_limits"]["actions"]

        self.assertEqual({action["action_id"] for action in blocked}, {"submit-permit-request", "upload-plans-to-official-record", "pay-review-fees"})
        self.assertTrue(all(action["status"] == "blocked" for action in blocked))
        self.assertTrue(all(action["requires_exact_confirmation"] is True for action in blocked))
        self.assertTrue(all(action["requires_user_attendance"] is True for action in blocked))
        self.assertTrue(all(action["official_action_executed"] is False for action in blocked))
        self.assertTrue(all(action["reason"] for action in blocked))
        self.assertTrue(all(action["may_upload"] is False for action in reversible))
        self.assertTrue(all(action["may_submit"] is False for action in reversible))
        self.assertTrue(all(action["may_pay"] is False for action in reversible))

    def test_rejects_missing_citations_and_false_attestations(self) -> None:
        packet = self.packet()
        packet["explanation_templates"][0]["citation_ids"] = []
        packet["attestations"]["no_live_llm"] = False

        errors = validate_guardrail_to_agent_explanation_packet(packet)

        self.assertTrue(any("citation_ids must be non-empty" in error for error in errors))
        self.assertTrue(any("attestations.no_live_llm must be true" in error for error in errors))

    def test_rejects_private_data_raw_artifacts_and_consequential_next_safe_actions(self) -> None:
        fixture = deepcopy(self.fixture())
        fixture["user_gap_analysis"]["known_facts"].append({"fact_id": "applicant", "value": "private"})
        fixture["agent_readiness_adapter_outputs"][0]["raw_html"] = "private"
        fixture["user_gap_analysis"]["next_safe_actions"].append(
            {"next_safe_action_id": "submit", "action_id": "submit-permit-request", "classification": "submission"}
        )

        with self.assertRaises(GuardrailToAgentExplanationPacketError) as caught:
            self.build(fixture)

        problems = caught.exception.problems
        self.assertTrue(any("private value field" in problem for problem in problems))
        self.assertTrue(any("raw document, session, or browser artifact" in problem for problem in problems))
        self.assertTrue(any("next_safe_actions cannot include consequential" in problem for problem in problems))

    def test_rejects_stale_or_unofficial_source_evidence(self) -> None:
        fixture = deepcopy(self.fixture())
        fixture["source_evidence"][0]["freshness_status"] = "stale"
        fixture["source_evidence"][1]["canonical_url"] = "https://example.test/not-ppd"

        with self.assertRaises(GuardrailToAgentExplanationPacketError) as caught:
            self.build(fixture)

        self.assertTrue(any("must be current" in problem for problem in caught.exception.problems))
        self.assertTrue(any("official PP&D URL" in problem for problem in caught.exception.problems))

    def test_rejects_mismatched_bundle_and_gap_analysis(self) -> None:
        fixture = deepcopy(self.fixture())
        fixture["user_gap_analysis"]["guardrail_bundle_id"] = "different-bundle"

        with self.assertRaises(GuardrailToAgentExplanationPacketError) as caught:
            self.build(fixture)

        self.assertTrue(any("guardrail_bundle_id values must match" in problem for problem in caught.exception.problems))
        self.assertTrue(any("unsupported" in problem for problem in caught.exception.problems))

    def test_rejects_missing_blocked_action_rationale(self) -> None:
        fixture = deepcopy(self.fixture())
        fixture["user_gap_analysis"]["blocked_actions"][0]["reason"] = ""

        with self.assertRaises(GuardrailToAgentExplanationPacketError) as caught:
            self.build(fixture)

        self.assertTrue(any("requires a rationale" in problem for problem in caught.exception.problems))

    def test_rejects_private_authenticated_facts_and_artifact_fields(self) -> None:
        fixture = deepcopy(self.fixture())
        fixture["user_gap_analysis"]["known_facts"].append(
            {"fact_id": "private-devhub-status", "privacy_classification": "devhub_authenticated"}
        )
        fixture["agent_readiness_adapter_outputs"][0]["browser_trace"] = "trace.zip"
        fixture["agent_readiness_adapter_outputs"][1]["session_artifact"] = "session.json"

        with self.assertRaises(GuardrailToAgentExplanationPacketError) as caught:
            self.build(fixture)

        problems = caught.exception.problems
        self.assertTrue(any("private or authenticated facts" in problem for problem in problems))
        self.assertTrue(any("raw document, session, or browser artifact" in problem for problem in problems))

    def test_rejects_guarantees_final_action_language_and_mutation_flags(self) -> None:
        packet = self.packet()
        packet["explanation_templates"][0]["agent_message"] = "This guarantees approval and the permit will issue."
        packet["explanation_templates"][1]["agent_message"] = "Click final submission now."
        packet["active_prompt_mutation"] = True
        packet["active_guardrail_mutation"] = True
        packet["active_source_mutation"] = True
        packet["active_surface_registry_mutation"] = True
        packet["active_release_state_mutation"] = True
        packet["active_agent_state_mutation"] = True

        errors = validate_guardrail_to_agent_explanation_packet(packet)

        self.assertTrue(any("must not guarantee legal or permitting outcomes" in error for error in errors))
        self.assertTrue(any("must not include final submission" in error for error in errors))
        self.assertTrue(any("active prompt, guardrail, source, surface-registry, release-state, or agent-state mutation" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
