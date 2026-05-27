import json
import unittest
from pathlib import Path

from ppd.validation.refreshed_requirement_packet_gate import (
    RefreshedRequirementPacketGateError,
    require_refreshed_requirement_packet_for_formal_guardrails,
    validate_refreshed_requirement_packet_for_formal_guardrails,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "refreshed_requirement_packet_gate" / "packets.json"


class RefreshedRequirementPacketGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_valid_packet_can_feed_formal_guardrails(self) -> None:
        result = validate_refreshed_requirement_packet_for_formal_guardrails(self.fixture["valid_packet"])

        self.assertTrue(result.ok)
        self.assertEqual((), result.findings)

    def test_packet_blocks_all_formal_guardrail_ingestion_risks(self) -> None:
        result = validate_refreshed_requirement_packet_for_formal_guardrails(self.fixture["invalid_packet"])

        self.assertFalse(result.ok)
        self.assertEqual(
            {
                "missing_citation_spans",
                "stale_source_hash",
                "low_confidence_without_human_review",
                "unsupported_requirement_type",
                "missing_affected_process_ids",
                "missing_affected_guardrail_ids",
            },
            {finding.code for finding in result.findings},
        )

    def test_low_confidence_requirement_passes_after_human_review(self) -> None:
        packet = self.fixture["valid_packet"]
        requirement = packet["records"][0]["requirements"][0]
        requirement["confidence"] = 0.6
        requirement["human_review_status"] = "human_reviewed"

        result = validate_refreshed_requirement_packet_for_formal_guardrails(packet)

        self.assertTrue(result.ok)

    def test_require_helper_raises_with_blocker_codes(self) -> None:
        with self.assertRaises(RefreshedRequirementPacketGateError) as context:
            require_refreshed_requirement_packet_for_formal_guardrails(self.fixture["invalid_packet"])

        self.assertIn("missing_citation_spans", str(context.exception))
        self.assertTrue(context.exception.findings)


if __name__ == "__main__":
    unittest.main()
