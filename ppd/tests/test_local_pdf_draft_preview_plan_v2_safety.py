from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from typing import Any

from ppd.local_pdf_draft_preview_plan_v2_safety import validate_local_pdf_draft_preview_plan_v2


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "local_pdf_draft_preview_plan_v2" / "fixture_first_packet.json"


def load_packet() -> dict[str, Any]:
    with FIXTURE_PATH.open(encoding="utf-8") as packet_file:
        return json.load(packet_file)


class LocalPdfDraftPreviewPlanV2SafetyTest(unittest.TestCase):
    def assert_rejected(self, packet: dict[str, Any], expected_fragment: str) -> None:
        errors = validate_local_pdf_draft_preview_plan_v2(packet)
        self.assertTrue(errors, "packet should be rejected")
        self.assertIn(expected_fragment, "; ".join(errors))

    def test_valid_fixture_is_accepted(self) -> None:
        self.assertEqual([], validate_local_pdf_draft_preview_plan_v2(load_packet()))

    def test_rejects_uncited_field_mapping_and_missing_withheld_rationale(self) -> None:
        packet = load_packet()
        packet["field_mapping_decisions"][0]["source_evidence_ids"] = []
        packet["field_mapping_decisions"][3].pop("withheld_reason")

        errors = "; ".join(validate_local_pdf_draft_preview_plan_v2(packet))
        self.assertIn("must cite source_evidence_ids", errors)
        self.assertIn("withholds a field without withheld_reason", errors)

    def test_rejects_missing_blocker_references(self) -> None:
        packet = load_packet()
        packet["missing_fact_blockers"][0]["blocks_field_names"] = ["field_not_in_mapping"]
        packet["missing_document_blockers"][0]["source_fixture_finding_ids"] = []
        packet["missing_document_blockers"][1]["source_evidence_ids"] = ["unknown-evidence"]

        errors = "; ".join(validate_local_pdf_draft_preview_plan_v2(packet))
        self.assertIn("blocks_field_names must reference field_mapping_decisions", errors)
        self.assertIn("source_fixture_finding_ids must not be empty", errors)
        self.assertIn("cites unknown source evidence", errors)

    def test_rejects_local_private_paths_and_raw_pdf_or_form_values(self) -> None:
        packet = load_packet()
        packet["preview_notes"] = "Read from /home/alex/private/permit.pdf"
        packet["raw_pdf_body"] = "%PDF-1.7 synthetic body %%EOF"
        packet["form_values"] = {"project_address": "123 private example"}

        errors = "; ".join(validate_local_pdf_draft_preview_plan_v2(packet))
        self.assertIn("contains a local private path", errors)
        self.assertIn("references raw PDF body or form values", errors)
        self.assertIn("contains raw PDF body or form-value reference", errors)

    def test_rejects_live_pdf_reads_writes_and_execution_claims(self) -> None:
        packet = load_packet()
        packet["generated_from"]["live_pdf_read"] = True
        packet["generated_from"]["live_pdf_write"] = True
        packet["operator_note"] = "The browser executed DevHub and the processor crawled the source before the LLM ran."

        errors = "; ".join(validate_local_pdf_draft_preview_plan_v2(packet))
        self.assertIn("claims live PDF", errors)
        self.assertIn("contains live execution claim", errors)

    def test_rejects_guarantees_and_final_action_language(self) -> None:
        packet = load_packet()
        packet["reviewer_note"] = "This will be approved and is ready for final submission."

        errors = "; ".join(validate_local_pdf_draft_preview_plan_v2(packet))
        self.assertIn("contains legal or permitting outcome guarantee", errors)
        self.assertIn("contains final submission/payment/upload/scheduling/cancellation language", errors)

    def test_rejects_preview_expectation_violations_and_required_attestation_gaps(self) -> None:
        packet = load_packet()
        packet["preview_only_artifact_expectations"]["may_read_pdf_binary"] = True
        packet["preview_only_artifact_expectations"]["may_write_pdf_binary"] = True
        packet["attestations"]["no_pdf_read"] = False
        packet["attestations"].pop("no_pdf_write")

        errors = "; ".join(validate_local_pdf_draft_preview_plan_v2(packet))
        self.assertIn("may_read_pdf_binary must be false", errors)
        self.assertIn("may_write_pdf_binary must be false", errors)
        self.assertIn("attestations.no_pdf_read must be true", errors)
        self.assertIn("attestations.no_pdf_write must be true", errors)

    def test_rejects_active_mutation_flags_for_all_prohibited_targets(self) -> None:
        mutation_keys = [
            "active_pdf_mutation",
            "active_document_mutation",
            "active_process_mutation",
            "active_gap_analysis_mutation",
            "active_guardrail_mutation",
            "active_prompt_mutation",
            "release_state_mutation",
            "agent_state_mutation",
        ]
        for key in mutation_keys:
            with self.subTest(key=key):
                packet = load_packet()
                packet[key] = True
                self.assert_rejected(packet, "declares an active PDF, document, process, gap-analysis, guardrail, prompt, release-state, or agent-state mutation flag")

    def test_rejects_withheld_missing_fact_field_without_matching_blocker(self) -> None:
        packet = load_packet()
        packet["missing_fact_blockers"] = [
            blocker for blocker in packet["missing_fact_blockers"] if "work_start_date" not in blocker["blocks_field_names"]
        ]

        self.assert_rejected(packet, "withheld missing-fact field lacks a matching missing_fact_blocker")

    def test_input_packet_is_not_mutated(self) -> None:
        packet = load_packet()
        original = copy.deepcopy(packet)
        validate_local_pdf_draft_preview_plan_v2(packet)
        self.assertEqual(original, packet)


if __name__ == "__main__":
    unittest.main()
