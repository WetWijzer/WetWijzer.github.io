from __future__ import annotations

from copy import deepcopy
from datetime import date
import unittest

from ppd.local_pdf_preview_readiness import (
    LocalPdfPreviewReadinessError,
    require_local_pdf_preview_readiness_packet,
    validate_local_pdf_preview_readiness_packet,
)


def ready_packet() -> dict:
    return {
        'packet_type': 'local_pdf_preview_readiness',
        'packet_id': 'fixture-local-preview-readiness',
        'preview_only': True,
        'writes_pdf_binary': False,
        'source_evidence': [
            {
                'evidence_id': 'evidence-apply-permits',
                'url': 'https://www.portland.gov/ppd/get-permit/apply-permits',
                'observed_on': '2026-05-01',
                'title': 'Apply for permits',
            }
        ],
        'field_mappings': [
            {
                'pdf_field_name': 'project_description',
                'value_strategy': 'redacted_placeholder',
                'source_evidence_ids': ['evidence-apply-permits'],
            }
        ],
        'blocked_fields': [
            {
                'pdf_field_name': 'applicant_signature',
                'complete': False,
                'may_autofill': False,
                'source_evidence_ids': ['evidence-apply-permits'],
            }
        ],
        'previews': [
            {
                'preview_id': 'local-preview-001',
                'rendered': True,
                'metadata_only': True,
                'contains_pdf_binary': False,
            }
        ],
    }


class LocalPdfPreviewReadinessTest(unittest.TestCase):
    def assert_rejects(self, packet: dict, text: str) -> None:
        errors = validate_local_pdf_preview_readiness_packet(packet, now=date(2026, 5, 27))
        self.assertTrue(errors)
        self.assertIn(text, '; '.join(errors))
        with self.assertRaises(LocalPdfPreviewReadinessError):
            require_local_pdf_preview_readiness_packet(packet, now=date(2026, 5, 27))

    def test_accepts_metadata_only_cited_fresh_preview_packet(self) -> None:
        packet = ready_packet()

        self.assertEqual([], validate_local_pdf_preview_readiness_packet(packet, now=date(2026, 5, 27)))
        require_local_pdf_preview_readiness_packet(packet, now=date(2026, 5, 27))

    def test_rejects_private_values_and_local_private_paths(self) -> None:
        packet = ready_packet()
        packet['field_mappings'].append(
            {
                'pdf_field_name': 'owner_email',
                'value': 'resident@example.com',
                'note': '/home/person/private/form.pdf',
                'source_evidence_ids': ['evidence-apply-permits'],
            }
        )

        self.assert_rejects(packet, 'private value is not allowed')
        self.assert_rejects(packet, 'local private path is not allowed')

    def test_rejects_credentials_and_payment_details(self) -> None:
        packet = ready_packet()
        packet['devhub_credentials'] = {'password': 'redacted', 'session_token': 'redacted'}
        packet['payment'] = {'card_number': '4111 1111 1111 1111', 'cvv': '123'}

        self.assert_rejects(packet, 'private or credential key is not allowed')

    def test_rejects_stale_evidence(self) -> None:
        packet = ready_packet()
        packet['source_evidence'][0]['observed_on'] = '2025-01-01'

        self.assert_rejects(packet, 'stale')

    def test_rejects_uncited_field_mappings(self) -> None:
        packet = ready_packet()
        del packet['field_mappings'][0]['source_evidence_ids']

        self.assert_rejects(packet, 'must cite source_evidence_ids')

    def test_rejects_missing_previews(self) -> None:
        packet = ready_packet()
        packet['previews'] = []

        self.assert_rejects(packet, 'at least one local preview')

    def test_rejects_pdf_binary_write_attempts(self) -> None:
        packet = ready_packet()
        packet['writes_pdf_binary'] = True
        packet['pdf_base64'] = 'JVBERi0xLjQK'

        self.assert_rejects(packet, 'PDF binary')

    def test_rejects_certification_or_submission_completion(self) -> None:
        packet = ready_packet()
        packet['field_mappings'].append(
            {
                'pdf_field_name': 'certification_acknowledgement_checkbox',
                'status': 'complete',
                'source_evidence_ids': ['evidence-apply-permits'],
            }
        )
        packet['field_mappings'].append(
            {
                'pdf_field_name': 'submission_ready',
                'complete': True,
                'source_evidence_ids': ['evidence-apply-permits'],
            }
        )

        self.assert_rejects(packet, 'must not mark certification or submission complete')

    def test_validation_does_not_mutate_packet(self) -> None:
        packet = ready_packet()
        original = deepcopy(packet)

        validate_local_pdf_preview_readiness_packet(packet, now=date(2026, 5, 27))

        self.assertEqual(original, packet)


if __name__ == '__main__':
    unittest.main()
