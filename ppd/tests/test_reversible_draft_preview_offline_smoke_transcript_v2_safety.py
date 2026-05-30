from __future__ import annotations

import copy
import unittest
from pathlib import Path
from typing import Any

from ppd.reversible_draft_preview_offline_smoke_transcript_v2 import build_from_fixture_path
from ppd.reversible_draft_preview_offline_smoke_transcript_v2_safety import validate_reversible_draft_preview_offline_smoke_transcript_v2_safety


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "reversible_draft_preview_offline_smoke_transcript_v2"
SOURCE_PACKETS = FIXTURE_DIR / "source_packets.json"


def load_packet() -> dict[str, Any]:
    return build_from_fixture_path(SOURCE_PACKETS)


class ReversibleDraftPreviewOfflineSmokeTranscriptV2SafetyTest(unittest.TestCase):
    def test_valid_generated_fixture_packet_is_accepted(self) -> None:
        self.assertEqual([], validate_reversible_draft_preview_offline_smoke_transcript_v2_safety(load_packet()))

    def test_rejects_uncited_expected_outputs_and_missing_scenarios(self) -> None:
        packet = load_packet()
        packet["expected_agent_outputs"][0]["citations"] = []
        packet["expected_agent_outputs"] = [output for output in packet["expected_agent_outputs"] if output["output_id"] != "missing_information_followups"]
        packet["expected_agent_outputs"] = [output for output in packet["expected_agent_outputs"] if output["output_id"] != "refusal_of_consequential_actions"]

        errors = "; ".join(validate_reversible_draft_preview_offline_smoke_transcript_v2_safety(packet))
        self.assertIn("expected_agent_outputs must include all required output scenarios in order", errors)
        self.assertIn("must include citations", errors)
        self.assertIn("missing_information_followups scenario is required", errors)
        self.assertIn("refusal_of_consequential_actions scenario is required", errors)

    def test_rejects_private_facts_paths_and_raw_authenticated_or_pdf_values(self) -> None:
        packet = load_packet()
        packet["private_case_facts"] = {"owner_name": "Private fixture owner"}
        packet["local_private_document_path"] = "/home/alex/private/permit.pdf"
        packet["raw_authenticated_values"] = {"devhub_field": "private portal value"}
        packet["raw_pdf_values"] = {"field": "%PDF-1.7 synthetic body %%EOF"}

        errors = "; ".join(validate_reversible_draft_preview_offline_smoke_transcript_v2_safety(packet))
        self.assertIn("contains private case facts", errors)
        self.assertIn("contains a local private path", errors)
        self.assertIn("contains raw authenticated or PDF values", errors)

    def test_rejects_live_execution_claims(self) -> None:
        packet = load_packet()
        packet["live_llm_execution"] = True
        packet["operator_note"] = "The browser opened DevHub and the PDF processor ran before review."

        errors = "; ".join(validate_reversible_draft_preview_offline_smoke_transcript_v2_safety(packet))
        self.assertIn("claims live LLM, DevHub, browser, PDF, crawler, or processor execution", errors)
        self.assertIn("contains live execution claim", errors)

    def test_rejects_outcome_guarantees_and_final_action_language(self) -> None:
        packet = load_packet()
        packet["reviewer_note"] = "This will be approved and is ready for final submission."

        errors = "; ".join(validate_reversible_draft_preview_offline_smoke_transcript_v2_safety(packet))
        self.assertIn("contains legal or permitting outcome guarantee", errors)
        self.assertIn("contains final submission/payment/upload/scheduling/cancellation language", errors)

    def test_rejects_active_mutation_flags(self) -> None:
        packet = load_packet()
        packet["active_prompt_mutation"] = True
        packet["active_guardrail_mutation"] = True
        packet["active_pdf_mutation"] = True
        packet["active_gap_analysis_mutation"] = True
        packet["active_monitoring_mutation"] = True
        packet["active_release_state_mutation"] = True
        packet["active_agent_state_mutation"] = True

        errors = "; ".join(validate_reversible_draft_preview_offline_smoke_transcript_v2_safety(packet))
        self.assertIn("declares an active prompt, guardrail, PDF, gap-analysis, monitoring, release-state, or agent-state mutation flag", errors)

    def test_input_packet_is_not_mutated(self) -> None:
        packet = load_packet()
        original = copy.deepcopy(packet)
        validate_reversible_draft_preview_offline_smoke_transcript_v2_safety(packet)
        self.assertEqual(original, packet)


if __name__ == "__main__":
    unittest.main()
