from __future__ import annotations

import copy
import unittest
from pathlib import Path
from typing import Any

from ppd.local_draft_preview_review_packet_v2 import build_from_paths
from ppd.local_draft_preview_review_packet_v2_safety import validate_local_draft_preview_review_packet_v2


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "local_draft_preview_review_packet_v2"


def load_packet() -> dict[str, Any]:
    return build_from_paths(
        FIXTURE_DIR / "preview_plan.json",
        FIXTURE_DIR / "readiness_packet.json",
        FIXTURE_DIR / "gap_analysis.json",
    )


class LocalDraftPreviewReviewPacketV2SafetyTest(unittest.TestCase):
    def assert_rejected(self, packet: dict[str, Any], expected_fragment: str) -> None:
        errors = validate_local_draft_preview_review_packet_v2(packet)
        self.assertTrue(errors, "packet should be rejected")
        self.assertIn(expected_fragment, "; ".join(errors))

    def test_valid_generated_fixture_packet_is_accepted(self) -> None:
        self.assertEqual([], validate_local_draft_preview_review_packet_v2(load_packet()))

    def test_rejects_uncited_rows_missing_explanations_and_missing_checkpoints(self) -> None:
        packet = load_packet()
        packet["reviewer_visible_preview_rows"][0]["citation"] = ""
        packet["reviewer_visible_preview_rows"][0].pop("value_explanation")
        packet["reviewer_visible_preview_rows"][1].pop("confirmation_checkpoint")

        errors = "; ".join(validate_local_draft_preview_review_packet_v2(packet))
        self.assertIn("must include citation", errors)
        self.assertIn("must include source-backed value_explanation", errors)
        self.assertIn("must include exact confirmation_checkpoint", errors)

    def test_rejects_missing_gap_checkpoint_and_uncited_blocker(self) -> None:
        packet = load_packet()
        packet["gap_analysis_checkpoints"][0].pop("exact_confirmation")
        packet["unresolved_blocker_summaries"][0]["citation"] = ""

        errors = "; ".join(validate_local_draft_preview_review_packet_v2(packet))
        self.assertIn("gap_analysis_checkpoints[0].exact_confirmation is required", errors)
        self.assertIn("unresolved_blocker_summaries[0].citation is required", errors)

    def test_rejects_private_facts_paths_and_raw_authenticated_or_pdf_values(self) -> None:
        packet = load_packet()
        packet["private_case_facts"] = {"owner_name": "Private fixture owner"}
        packet["local_private_document_path"] = "/home/alex/private/permit.pdf"
        packet["raw_authenticated_values"] = {"devhub_field": "private portal value"}
        packet["raw_pdf_values"] = {"field": "%PDF-1.7 synthetic body %%EOF"}

        errors = "; ".join(validate_local_draft_preview_review_packet_v2(packet))
        self.assertIn("contains private case facts", errors)
        self.assertIn("contains a local private document path", errors)
        self.assertIn("contains a local private path", errors)
        self.assertIn("contains raw authenticated or PDF values", errors)

    def test_rejects_live_execution_claims(self) -> None:
        packet = load_packet()
        packet["live_llm_execution"] = True
        packet["operator_note"] = "The browser opened DevHub and the PDF processor ran before review."

        errors = "; ".join(validate_local_draft_preview_review_packet_v2(packet))
        self.assertIn("claims live DevHub, browser, PDF, LLM, crawler, or processor execution", errors)
        self.assertIn("contains live execution claim", errors)

    def test_rejects_outcome_guarantees_and_final_action_language(self) -> None:
        packet = load_packet()
        packet["reviewer_note"] = "This will be approved and is ready for final submission."

        errors = "; ".join(validate_local_draft_preview_review_packet_v2(packet))
        self.assertIn("contains legal or permitting outcome guarantee", errors)
        self.assertIn("contains final submission/payment/upload/scheduling/cancellation language", errors)

    def test_rejects_attestation_gaps_and_active_mutation_flags(self) -> None:
        packet = load_packet()
        packet["attestations"]["no_pdf_write"] = False
        packet["active_pdf_mutation"] = True
        packet["gap_analysis_mutation_enabled"] = True
        packet["active_guardrail_mutation"] = True
        packet["active_prompt_mutation"] = True
        packet["active_release_state_mutation"] = True
        packet["active_agent_state_mutation"] = True

        errors = "; ".join(validate_local_draft_preview_review_packet_v2(packet))
        self.assertIn("attestations.no_pdf_write must be true", errors)
        self.assertIn("declares an active PDF, gap-analysis, guardrail, prompt, release-state, or agent-state mutation flag", errors)

    def test_input_packet_is_not_mutated(self) -> None:
        packet = load_packet()
        original = copy.deepcopy(packet)
        validate_local_draft_preview_review_packet_v2(packet)
        self.assertEqual(original, packet)


if __name__ == "__main__":
    unittest.main()
