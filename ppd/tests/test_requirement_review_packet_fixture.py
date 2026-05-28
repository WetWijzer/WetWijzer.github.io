"""Validate the synthetic requirement extraction review packet fixture."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Mapping

from ppd.validation.requirement_extraction_review_packet import (
    validate_requirement_extraction_review_packet,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "requirement_review_packet"
    / "synthetic_single_record_packet.json"
)

EXPECTED_REQUIREMENT_TYPES = {
    "action_gate",
    "deadline",
    "document_requirement",
    "exception",
    "fee_trigger",
    "obligation",
    "prohibition",
}


class RequirementReviewPacketFixtureTest(unittest.TestCase):
    def test_fixture_is_review_ready_and_synthetic(self) -> None:
        packet = _load_packet()

        self.assertTrue(packet["fixture_metadata"]["synthetic_fixture_only"])
        self.assertFalse(packet["fixture_metadata"]["live_crawl_used"])
        self.assertFalse(packet["fixture_metadata"]["authenticated_data_used"])

        result = validate_requirement_extraction_review_packet(packet)
        self.assertTrue(result.ok, [finding.code for finding in result.findings])

    def test_fixture_maps_one_document_to_required_node_types(self) -> None:
        packet = _load_packet()
        document = packet["normalized_document_record"]
        document_id = document["document_id"]
        requirements = packet["requirements"]

        self.assertEqual(EXPECTED_REQUIREMENT_TYPES, {node["requirement_type"] for node in requirements})
        self.assertEqual(len(EXPECTED_REQUIREMENT_TYPES), len(requirements))

        for node in requirements:
            self.assertEqual("needs_human_review", node["human_review_status"])
            self.assertEqual("candidate", node["formalization_status"])
            self.assertEqual(["synthetic_building_permit"], node["permit_types"])
            self.assertTrue(node["source_evidence_ids"])

            citation_spans = node["citation_spans"]
            self.assertEqual(1, len(citation_spans))
            span = citation_spans[0]
            self.assertEqual(document_id, span["document_id"])
            self.assertEqual(node["source_evidence_ids"], [span["evidence_id"]])

    def test_citation_spans_resolve_to_synthetic_section_text(self) -> None:
        packet = _load_packet()
        sections = {
            section["section_id"]: section["text"]
            for section in packet["normalized_document_record"]["sections"]
        }

        for node in packet["requirements"]:
            for span in node["citation_spans"]:
                section_text = sections[span["section_id"]]
                start = span["start"]
                end = span["end"]
                quote = span["quote"]

                self.assertIsInstance(start, int)
                self.assertIsInstance(end, int)
                self.assertLess(start, end)
                self.assertEqual(quote, section_text[start:end])
                self.assertEqual(len(quote), end - start)


def _load_packet() -> Mapping[str, Any]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
        packet = json.load(fixture_file)
    if not isinstance(packet, Mapping):
        raise AssertionError("fixture packet must be a JSON object")
    return packet


if __name__ == "__main__":
    unittest.main()
