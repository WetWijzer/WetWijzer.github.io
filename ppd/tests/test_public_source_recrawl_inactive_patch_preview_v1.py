from __future__ import annotations

import ast
import copy
import unittest
from pathlib import Path

from ppd.agent_readiness.public_source_recrawl_inactive_patch_preview_v1 import (
    build_public_source_recrawl_inactive_patch_preview_v1,
    validate_public_source_recrawl_inactive_patch_preview_v1,
)

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'public_source_recrawl_inactive_patch_preview'


class PublicSourceRecrawlInactivePatchPreviewV1Tests(unittest.TestCase):
    def setUp(self) -> None:
        fixture_text = (FIXTURE_DIR / 'reviewer_disposition_packet_v1.pydata').read_text(encoding='utf-8')
        self.disposition_packet = ast.literal_eval(fixture_text)
        self.preview = build_public_source_recrawl_inactive_patch_preview_v1(self.disposition_packet)

    def issue_codes(self, packet: dict[str, object]) -> set[str]:
        return {issue.code for issue in validate_public_source_recrawl_inactive_patch_preview_v1(packet)}

    def test_builder_emits_valid_inactive_preview_from_approved_rows_only(self) -> None:
        self.assertEqual([], validate_public_source_recrawl_inactive_patch_preview_v1(self.preview))
        self.assertEqual({'ppd-devhub-faq'}, {row['source_id'] for row in self.preview['source_registry_delta_placeholders']})
        self.assertEqual('excluded_from_inactive_delta_placeholders', self.preview['held_or_skipped_reviewer_disposition_notes'][0]['preview_effect'])
        self.assertFalse(self.preview['active_source_artifacts_mutated'])
        self.assertFalse(self.preview['active_requirement_artifacts_mutated'])

    def test_preview_contains_required_placeholder_families(self) -> None:
        for key in ('source_registry_delta_placeholders', 'archive_manifest_delta_placeholders', 'normalized_document_reference_placeholders', 'freshness_monitor_replay_notes'):
            self.assertEqual(1, len(self.preview[key]))
            self.assertEqual('inactive_preview_only', self.preview[key][0]['inactive_patch_state'])

    def test_rejects_missing_placeholders_and_source_mismatch(self) -> None:
        packet = copy.deepcopy(self.preview)
        packet['archive_manifest_delta_placeholders'] = []
        packet['freshness_monitor_replay_notes'][0]['source_id'] = 'wrong-source'
        codes = self.issue_codes(packet)
        self.assertIn('missing_placeholder_rows', codes)
        self.assertIn('placeholder_source_mismatch', codes)

    def test_rejects_missing_validation_commands_unsafe_text_and_mutation_flags(self) -> None:
        packet = copy.deepcopy(self.preview)
        packet['validation_commands'] = []
        packet['active_guardrail_artifacts_mutated'] = True
        packet['authenticated_session_ref'] = 'session.json'
        packet['operator_note'] = 'Live network request executed and raw response body retained. Submit permit after review.'
        codes = self.issue_codes(packet)
        self.assertIn('missing_validation_commands', codes)
        self.assertIn('unsafe_execution_or_mutation_flag', codes)
        self.assertIn('unsafe_artifact_reference', codes)
        self.assertIn('live_execution_claim', codes)
        self.assertIn('payload_or_download_claim', codes)
        self.assertIn('consequential_devhub_action_language', codes)


if __name__ == '__main__':
    unittest.main()
