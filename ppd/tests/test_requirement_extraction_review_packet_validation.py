from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.validation.requirement_extraction_review_packet import (
    RequirementExtractionReviewPacketError,
    require_requirement_extraction_review_packet,
    validate_requirement_extraction_review_packet,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "requirement_extraction_review_packet" / "packets.json"


class RequirementExtractionReviewPacketValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_valid_review_packet_passes_validation(self) -> None:
        result = validate_requirement_extraction_review_packet(self.fixture["valid_packet"])

        self.assertTrue(result.ok)
        self.assertEqual((), result.findings)

    def test_review_packet_rejects_all_required_blocker_categories(self) -> None:
        result = validate_requirement_extraction_review_packet(self.fixture["invalid_packet"])

        self.assertFalse(result.ok)
        self.assertEqual(
            {
                "formalization_ready_before_review",
                "low_confidence_without_human_review_status",
                "missing_permit_link",
                "missing_process_stage_link",
                "private_value_present",
                "raw_document_body_present",
                "uncited_requirement",
                "unsupported_requirement_type",
            },
            {finding.code for finding in result.findings},
        )

    def test_low_confidence_node_is_allowed_when_it_is_in_review_queue(self) -> None:
        packet = self.fixture["valid_packet"]
        requirement = packet["requirements"][0]
        requirement["confidence"] = 0.5
        requirement["human_review_status"] = "needs_human_review"
        requirement["formalization_status"] = "blocked_pending_review"

        result = validate_requirement_extraction_review_packet(packet)

        self.assertTrue(result.ok)

    def test_ready_status_requires_completed_human_review(self) -> None:
        packet = self.fixture["valid_packet"]
        requirement = packet["requirements"][1]
        requirement["confidence"] = 0.95
        requirement["human_review_status"] = "needs_human_review"
        requirement["formalization_status"] = "ready"

        result = validate_requirement_extraction_review_packet(packet)

        self.assertFalse(result.ok)
        self.assertEqual({"formalization_ready_before_review"}, {finding.code for finding in result.findings})

    def test_require_helper_raises_with_deterministic_codes(self) -> None:
        with self.assertRaises(RequirementExtractionReviewPacketError) as context:
            require_requirement_extraction_review_packet(self.fixture["invalid_packet"])

        self.assertIn("uncited_requirement", str(context.exception))
        self.assertTrue(context.exception.findings)


if __name__ == "__main__":
    unittest.main()
