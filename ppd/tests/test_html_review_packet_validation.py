from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.extraction.html_review_packet import validate_html_extraction_review_packet

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "html_review_packets"


class HtmlReviewPacketValidationTest(unittest.TestCase):
    def load_fixture(self, name: str) -> dict:
        with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_accepts_minimal_public_cited_pending_packet(self) -> None:
        packet = self.load_fixture("valid_pending_packet.json")
        result = validate_html_extraction_review_packet(packet)
        self.assertTrue(result.ok, result.issues)

    def test_rejects_pre_review_packet_safety_failures(self) -> None:
        packet = self.load_fixture("invalid_pre_review_packet.json")
        result = validate_html_extraction_review_packet(packet)
        self.assertFalse(result.ok)
        self.assertEqual(
            {
                "raw_or_body_storage",
                "lost_section_ordering",
                "uncited_extracted_section",
                "unsupported_or_private_link",
                "missing_freshness_evidence",
                "missing_date_evidence",
                "missing_source_id",
                "invented_hash",
                "ready_guardrail_status_before_human_review",
            },
            set(result.error_codes()),
        )


if __name__ == "__main__":
    unittest.main()
