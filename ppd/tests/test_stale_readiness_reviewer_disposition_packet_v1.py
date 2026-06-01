from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.stale_readiness_reviewer_disposition_packet_v1 import (
    validate_stale_readiness_reviewer_disposition_packet_v1,
)

FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'stale_readiness_reviewer_disposition_packet_v1' / 'valid_packet.json'


class StaleReadinessReviewerDispositionPacketV1Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))

    def issue_codes(self, packet: dict[str, object]) -> set[str]:
        return {issue.code for issue in validate_stale_readiness_reviewer_disposition_packet_v1(packet)}

    def test_valid_fixture_has_no_issues(self) -> None:
        self.assertEqual([], validate_stale_readiness_reviewer_disposition_packet_v1(self.packet))

    def test_rejects_missing_required_reviewer_structure(self) -> None:
        cases = {
            'combined_readiness_references': 'missing_combined_readiness_references',
            'dependency_ordering': 'missing_dependency_ordering',
            'owner_routing': 'missing_owner_routing',
            'reviewer_routing': 'missing_reviewer_routing',
            'stale_source_hold_reasons': 'missing_stale_source_hold_reasons',
            'rollback_notes': 'missing_rollback_notes',
            'validation_commands': 'missing_validation_commands',
        }
        for field, expected_code in cases.items():
            packet = copy.deepcopy(self.packet)
            packet[field] = []
            self.assertIn(expected_code, self.issue_codes(packet), field)

    def test_rejects_missing_disposition_rows(self) -> None:
        for disposition in ('proceed', 'hold', 'reject'):
            packet = copy.deepcopy(self.packet)
            packet['disposition_rows'] = [row for row in packet['disposition_rows'] if row['disposition'] != disposition]
            self.assertIn(f'missing_{disposition}_disposition_row', self.issue_codes(packet))

    def test_rejects_missing_row_owner_reviewer_and_hold_reason(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet['disposition_rows'][1]['owner'] = ''
        packet['disposition_rows'][1]['reviewer'] = ''
        packet['disposition_rows'][1]['stale_source_hold_reasons'] = []
        codes = self.issue_codes(packet)
        self.assertIn('missing_owner_routing', codes)
        self.assertIn('missing_reviewer_routing', codes)
        self.assertIn('missing_stale_source_hold_reasons', codes)

    def test_rejects_forbidden_artifacts_claims_and_active_mutation_flags(self) -> None:
        fragments = [
            ({'credential_ref': 'redacted'}, 'forbidden_artifact_reference'),
            ({'operator_note': 'session cookie captured in browser state'}, 'credentials_or_session_artifact'),
            ({'operator_note': 'screenshot, browser trace, and HAR file attached'}, 'browser_evidence_artifact'),
            ({'operator_note': 'private artifact includes raw crawl and downloaded document'}, 'private_raw_or_downloaded_artifact'),
            ({'operator_note': 'live DevHub crawl completed'}, 'live_devhub_or_crawl_claim'),
            ({'operator_note': 'official action completed and permit submitted'}, 'official_action_completion_claim'),
            ({'operator_note': 'release promoted to production'}, 'release_promotion_claim'),
            ({'operator_note': 'permitting guarantee: will be approved'}, 'legal_or_permitting_guarantee'),
            ({'mutation_flags': {'active_mutation': True}}, 'active_mutation_flag'),
        ]
        for fragment, expected_code in fragments:
            packet = copy.deepcopy(self.packet)
            packet.update(fragment)
            self.assertIn(expected_code, self.issue_codes(packet), expected_code)


if __name__ == '__main__':
    unittest.main()
