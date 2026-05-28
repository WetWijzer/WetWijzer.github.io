from __future__ import annotations

import json
import unittest
from pathlib import Path

from ppd.validation.pdf_form_extraction_review_packet import PdfFormExtractionReviewPacketError, require_pdf_form_extraction_review_packet, validate_pdf_form_extraction_review_packet

FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'pdf_form_extraction_review_packet' / 'packets.json'


class PdfFormExtractionReviewPacketValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))

    def test_valid_review_packet_passes_validation(self) -> None:
        result = validate_pdf_form_extraction_review_packet(self.fixture['valid_packet'])
        self.assertTrue(result.ok)
        self.assertEqual((), result.findings)

    def test_review_packet_rejects_required_blocker_categories(self) -> None:
        result = validate_pdf_form_extraction_review_packet(self.fixture['invalid_packet'])
        self.assertFalse(result.ok)
        self.assertEqual({'downloaded_file_path_present', 'field_without_page_or_citation_anchor', 'pdf_binary_present', 'private_value_present', 'raw_ocr_image_present', 'signature_or_certification_completion_claim', 'unmarked_ocr_derived_text', 'unsupported_field_type'}, {finding.code for finding in result.findings})

    def test_ocr_text_is_allowed_when_marked_for_review(self) -> None:
        packet = self.fixture['valid_packet']
        packet['fields'][0]['ocr_derived'] = True
        packet['fields'][0]['ocr_confidence'] = 0.82
        packet['fields'][0]['human_review_status'] = 'needs_human_review'
        result = validate_pdf_form_extraction_review_packet(packet)
        self.assertTrue(result.ok)

    def test_require_helper_raises_with_deterministic_codes(self) -> None:
        with self.assertRaises(PdfFormExtractionReviewPacketError) as context:
            require_pdf_form_extraction_review_packet(self.fixture['invalid_packet'])
        self.assertIn('pdf_binary_present', str(context.exception))
        self.assertTrue(context.exception.findings)


if __name__ == '__main__':
    unittest.main()
