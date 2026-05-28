from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "pdf_form_review" / "synthetic_pdf_form_review_packet.json"
REQUIRED_COVERAGE = {
    "page_anchors",
    "tables",
    "checklist_items",
    "required_document_labels",
    "signature_certification_blocks",
    "fillable_field_names",
    "field_types",
    "checkbox_radio_options",
    "ocr_confidence_markers",
}
FIELD_TYPES = {"text", "checkbox", "radio", "select", "date", "signature"}
PRIVATE_MARKERS = (
    "cookie",
    "credential",
    "password",
    "payment card",
    "session storage",
    "auth state",
    "trace.zip",
    "har file",
)


def load_packet() -> dict[str, Any]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
        packet = json.load(fixture_file)
    if not isinstance(packet, dict):
        raise AssertionError("review packet must be a JSON object")
    return packet


def require_string(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AssertionError(f"{key} must be a non-empty string")
    return value


class PdfFormReviewPacketFixtureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load_packet()
        anchors = self.packet.get("pageAnchors")
        self.assertIsInstance(anchors, list)
        self.anchor_ids = {require_string(anchor, "anchorId") for anchor in anchors}

    def test_packet_is_fixture_only_synthetic_metadata(self) -> None:
        self.assertEqual(self.packet.get("extractionMode"), "fixture_only")
        self.assertIs(self.packet.get("syntheticMetadataOnly"), True)
        self.assertIs(self.packet.get("liveCrawlPerformed"), False)
        source = self.packet.get("source")
        self.assertIsInstance(source, dict)
        self.assertTrue(require_string(source, "canonicalUrl").startswith("https://"))
        self.assertEqual(source.get("privacyClassification"), "public_synthetic_metadata")
        self.assertIs(source.get("rawBodyPersisted"), False)
        serialized = json.dumps(self.packet, sort_keys=True).lower()
        for marker in PRIVATE_MARKERS:
            self.assertNotIn(marker, serialized)

    def test_coverage_categories_match_review_scope(self) -> None:
        coverage = self.packet.get("coverageCategories")
        self.assertIsInstance(coverage, list)
        self.assertEqual(set(coverage), REQUIRED_COVERAGE)

    def test_page_anchors_are_positive_and_unique(self) -> None:
        anchors = self.packet.get("pageAnchors")
        self.assertGreaterEqual(len(anchors), 3)
        seen: set[str] = set()
        for anchor in anchors:
            anchor_id = require_string(anchor, "anchorId")
            self.assertNotIn(anchor_id, seen)
            seen.add(anchor_id)
            self.assertIsInstance(anchor.get("pageNumber"), int)
            self.assertGreater(anchor["pageNumber"], 0)
            require_string(anchor, "heading")
            require_string(anchor, "syntheticTextSnippet")

    def test_tables_and_rows_reference_page_anchors(self) -> None:
        tables = self.packet.get("tables")
        self.assertIsInstance(tables, list)
        self.assertGreaterEqual(len(tables), 1)
        for table in tables:
            require_string(table, "tableId")
            self.assertIn(require_string(table, "pageAnchorId"), self.anchor_ids)
            require_string(table, "caption")
            headers = table.get("headers")
            rows = table.get("rows")
            self.assertIsInstance(headers, list)
            self.assertIsInstance(rows, list)
            self.assertGreaterEqual(len(headers), 2)
            self.assertGreaterEqual(len(rows), 1)
            for row in rows:
                self.assertIsInstance(row, list)
                self.assertEqual(len(row), len(headers))

    def test_checklists_document_labels_and_certification_blocks_are_reviewable(self) -> None:
        checklist_items = self.packet.get("checklistItems")
        document_labels = self.packet.get("requiredDocumentLabels")
        certification_blocks = self.packet.get("signatureCertificationBlocks")
        self.assertIsInstance(checklist_items, list)
        self.assertIsInstance(document_labels, list)
        self.assertIsInstance(certification_blocks, list)
        self.assertGreaterEqual(len(checklist_items), 2)
        self.assertGreaterEqual(len(document_labels), 2)
        self.assertGreaterEqual(len(certification_blocks), 1)

        for item in checklist_items:
            require_string(item, "itemId")
            self.assertIn(require_string(item, "pageAnchorId"), self.anchor_ids)
            require_string(item, "label")
            self.assertIsInstance(item.get("required"), bool)

        for label in document_labels:
            require_string(label, "labelId")
            self.assertIn(require_string(label, "pageAnchorId"), self.anchor_ids)
            require_string(label, "label")
            require_string(label, "requiredWhen")
            require_string(label, "reviewNote")

        for block in certification_blocks:
            require_string(block, "blockId")
            self.assertIn(require_string(block, "pageAnchorId"), self.anchor_ids)
            self.assertIs(block.get("requiresSignature"), True)
            self.assertIs(block.get("requiresDate"), True)
            self.assertIs(block.get("requiresAttendedConfirmation"), True)
            self.assertEqual(block.get("automationPolicy"), "review_only_stop_before_certification")

    def test_fillable_fields_include_names_types_and_options(self) -> None:
        fields = self.packet.get("fillableFields")
        self.assertIsInstance(fields, list)
        self.assertGreaterEqual(len(fields), 5)
        names: set[str] = set()
        types: set[str] = set()
        for field in fields:
            require_string(field, "fieldId")
            field_name = require_string(field, "fieldName")
            self.assertNotIn(field_name, names)
            names.add(field_name)
            field_type = require_string(field, "fieldType")
            self.assertIn(field_type, FIELD_TYPES)
            types.add(field_type)
            self.assertIn(require_string(field, "pageAnchorId"), self.anchor_ids)
            require_string(field, "label")
            self.assertIsInstance(field.get("required"), bool)
            options = field.get("options")
            self.assertIsInstance(options, list)
            if field_type in {"checkbox", "radio", "select"}:
                self.assertGreaterEqual(len(options), 1)
            else:
                self.assertEqual(options, [])
        self.assertTrue({"text", "checkbox", "radio", "date", "signature"}.issubset(types))

    def test_ocr_confidence_markers_are_bounded_and_reviewable(self) -> None:
        markers = self.packet.get("ocrConfidenceMarkers")
        self.assertIsInstance(markers, list)
        self.assertGreaterEqual(len(markers), 2)
        for marker in markers:
            require_string(marker, "markerId")
            self.assertIn(require_string(marker, "pageAnchorId"), self.anchor_ids)
            require_string(marker, "textRole")
            confidence = marker.get("confidence")
            self.assertIsInstance(confidence, (int, float))
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
            self.assertIn(marker.get("humanReviewStatus"), {"needs_review", "reviewed"})
            require_string(marker, "reason")


if __name__ == "__main__":
    unittest.main()
