from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.pdf.draft_preview_packet_v2 import (
    OFFLINE_VALIDATION_COMMANDS,
    build_pdf_draft_preview_packet_v2,
    packet_summary,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "pdf_draft_preview_packet_v2"
    / "synthetic_permit_facts.json"
)


class PdfDraftPreviewPacketV2Tests(unittest.TestCase):
    def load_fixture(self) -> dict:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_complete_fixture_builds_reversible_preview_packet(self) -> None:
        packet = build_pdf_draft_preview_packet_v2(self.load_fixture())
        summary = packet_summary(packet)

        self.assertEqual(packet["packet_version"], "ppd_pdf_draft_preview_packet_v2")
        self.assertEqual(summary["required_gap_count"], 0)
        self.assertTrue(summary["ready_for_local_preview_fill_rehearsal"])
        self.assertFalse(summary["ready_for_official_upload_or_submission"])
        self.assertGreaterEqual(summary["planned_field_count"], 8)

        for field_plan in packet["local_preview_pdf_field_plan"]:
            self.assertTrue(field_plan["reversible"])
            self.assertEqual(field_plan["allowed_action"], "plan_local_preview_value_only")
            self.assertIn("write_pdf", field_plan["disallowed_actions"])
            self.assertIn("upload", field_plan["disallowed_actions"])
            self.assertIn("submit", field_plan["disallowed_actions"])
            self.assertIn("certify", field_plan["disallowed_actions"])

    def test_missing_required_fact_is_reported_as_gap(self) -> None:
        facts = self.load_fixture()
        facts["site_address"] = ""
        facts.pop("applicant_email")

        packet = build_pdf_draft_preview_packet_v2(facts)
        gap_keys = {gap["fact_key"] for gap in packet["required_fact_gaps"]}

        self.assertEqual(gap_keys, {"site_address", "applicant_email"})
        self.assertFalse(packet["readiness"]["ready_for_local_preview_fill_rehearsal"])
        self.assertFalse(packet["readiness"]["ready_for_official_upload_or_submission"])

    def test_packet_contains_required_safety_sections(self) -> None:
        packet = build_pdf_draft_preview_packet_v2(self.load_fixture())

        self.assertGreaterEqual(len(packet["unsupported_field_notes"]), 4)
        self.assertGreaterEqual(len(packet["citation_references"]), 4)
        self.assertGreaterEqual(len(packet["user_visible_review_checkpoints"]), 4)
        self.assertIn("read_private_pdf", packet["refused_actions"])
        self.assertIn("persist_generated_pdf", packet["refused_actions"])
        self.assertIn("submit_application", packet["refused_actions"])
        self.assertIn("certify_acknowledgement", packet["refused_actions"])

        assurance_text = " ".join(packet["no_private_file_assurances"])
        self.assertIn("Does not open", assurance_text)
        self.assertIn("Does not create or persist generated PDF files", assurance_text)
        self.assertIn("Does not upload files", assurance_text)

    def test_offline_validation_commands_are_exact_and_local(self) -> None:
        packet = build_pdf_draft_preview_packet_v2(self.load_fixture())

        self.assertEqual(packet["offline_validation_commands"], OFFLINE_VALIDATION_COMMANDS)
        self.assertIn(
            ["python3", "-m", "unittest", "ppd.tests.test_pdf_draft_preview_packet_v2"],
            packet["offline_validation_commands"],
        )
        self.assertIn(
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
            packet["offline_validation_commands"],
        )


if __name__ == "__main__":
    unittest.main()
