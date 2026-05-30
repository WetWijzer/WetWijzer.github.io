import json
import unittest
from pathlib import Path

from ppd.agent_readiness.official_source_anchor_audit_packet_v1 import (
    NO_ACTION_STATEMENTS,
    SCHEMA_VERSION,
    build_official_source_anchor_audit_packet_v1,
    render_official_source_anchor_audit_packet_v1,
)


FIXTURE = Path(__file__).parent / 'fixtures' / 'official_source_anchor_audit_packet_v1' / 'source_inputs.json'


class OfficialSourceAnchorAuditPacketV1Tests(unittest.TestCase):
    def load_inputs(self):
        return json.loads(FIXTURE.read_text(encoding='utf-8'))

    def test_builds_cited_gap_rows_from_fixture_inputs(self):
        packet = build_official_source_anchor_audit_packet_v1(self.load_inputs())
        self.assertEqual(packet['schema_version'], SCHEMA_VERSION)
        self.assertTrue(packet['fixture_first'])
        self.assertTrue(packet['metadata_only'])
        self.assertGreaterEqual(len(packet['gap_rows']), 3)
        first = packet['gap_rows'][0]
        self.assertIn('stale_visible_date_evidence', first['issue_types'])
        self.assertIn('policy_status_needs_review', first['issue_types'])
        self.assertIn('ppd-public-landing', first['affected_source_ids'])
        self.assertIn('source_anchor_coverage_matrix:ppd-public-landing', first['citations'])
        self.assertEqual(first['reviewer_owner'], 'PP&D public source registry maintainer')
        self.assertTrue(first['offline_validation_commands'])

    def test_missing_anchor_rows_name_registry_and_index_gaps(self):
        packet = build_official_source_anchor_audit_packet_v1(self.load_inputs())
        rows_by_url = {row['anchor_url']: row for row in packet['gap_rows']}
        missing = rows_by_url['https://devhub.portlandoregon.gov']
        self.assertIn('missing_committed_source_registry_anchor', missing['issue_types'])
        self.assertIn('missing_source_index_anchor', missing['issue_types'])
        self.assertEqual(missing['citations'], ['human_release_handoff_packet_v1', 'original_ppd_official_source_anchor_list'])
        self.assertEqual(missing['affected_source_ids'], ['official-anchor-3:unregistered'])

    def test_packet_declares_offline_non_mutating_boundaries(self):
        packet = build_official_source_anchor_audit_packet_v1(self.load_inputs())
        self.assertEqual(packet['attestations'], {
            'live_crawl_performed': False,
            'download_performed': False,
            'processor_execution_performed': False,
            'raw_body_persisted': False,
            'source_registry_mutated': False,
        })
        for statement in NO_ACTION_STATEMENTS:
            self.assertIn(statement, packet['no_action_statements'])

    def test_rendered_packet_contains_required_sections(self):
        packet = build_official_source_anchor_audit_packet_v1(self.load_inputs())
        rendered = render_official_source_anchor_audit_packet_v1(packet)
        self.assertIn('Official Source Anchor Audit Packet v1', rendered)
        self.assertIn('Offline validation commands:', rendered)
        self.assertIn('Explicit non-action statements:', rendered)
        self.assertIn('No live crawl has been performed.', rendered)


if __name__ == '__main__':
    unittest.main()
