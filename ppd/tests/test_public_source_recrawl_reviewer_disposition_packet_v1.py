from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.public_source_recrawl_reviewer_disposition_packet_v1 import (
    build_public_source_recrawl_reviewer_disposition_packet_v1,
    validate_public_source_recrawl_reviewer_disposition_packet_v1,
)

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'public_source_recrawl_reviewer_disposition'


class PublicSourceRecrawlReviewerDispositionPacketV1Tests(unittest.TestCase):
    def setUp(self) -> None:
        manifest = json.loads((FIXTURE_DIR / 'manifest_v1.json').read_text(encoding='utf-8'))
        self.packet = build_public_source_recrawl_reviewer_disposition_packet_v1(manifest)

    def issue_codes(self, packet: dict[str, object]) -> set[str]:
        return {issue.code for issue in validate_public_source_recrawl_reviewer_disposition_packet_v1(packet)}

    def test_builder_emits_valid_packet(self) -> None:
        self.assertEqual([], validate_public_source_recrawl_reviewer_disposition_packet_v1(self.packet))

    def test_rejects_missing_reviewer_decisions(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet['reviewer_decisions'] = []
        self.assertIn('missing_reviewer_decisions', self.issue_codes(packet))

    def test_rejects_missing_reason_codes(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet['reviewer_decisions'][0]['reason_codes'] = []
        packet['reviewer_decisions'][1]['reason_codes'] = []
        codes = self.issue_codes(packet)
        self.assertIn('missing_approve_reason_code', codes)
        self.assertIn('missing_hold_reason_code', codes)

    def test_rejects_missing_metadata_expectations_skipped_explanations_and_freshness(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet['metadata_only_artifact_expectations'] = {'expected_artifacts': [], 'forbidden_artifacts': []}
        packet['skipped_source_explanations'] = []
        packet['source_freshness_update_placeholders'] = []
        codes = self.issue_codes(packet)
        self.assertIn('missing_expected_metadata_artifacts', codes)
        self.assertIn('missing_forbidden_artifacts', codes)
        self.assertIn('missing_skipped_source_explanation', codes)
        self.assertIn('missing_source_freshness_placeholders', codes)

    def test_rejects_missing_validation_commands(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet['validation_commands'] = []
        self.assertIn('missing_validation_commands', self.issue_codes(packet))

    def test_rejects_unsafe_artifacts_execution_claims_and_mutation_flags(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet['authenticated_session_ref'] = 'session.json'
        packet['operator_claim'] = 'Live network was invoked and raw response body was retained.'
        packet['legal_summary'] = 'Permit will be approved.'
        packet['devhub_action'] = 'Submit permit after review.'
        packet['active_prompt_artifacts_mutated'] = True
        codes = self.issue_codes(packet)
        self.assertIn('unsafe_artifact_reference', codes)
        self.assertIn('live_execution_claim', codes)
        self.assertIn('raw_or_downloaded_data_claim', codes)
        self.assertIn('legal_or_permitting_outcome_guarantee', codes)
        self.assertIn('consequential_devhub_action_language', codes)
        self.assertIn('unsafe_execution_or_mutation_flag', codes)


if __name__ == '__main__':
    unittest.main()
