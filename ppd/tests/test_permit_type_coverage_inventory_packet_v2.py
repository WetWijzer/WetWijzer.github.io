from __future__ import annotations

import copy
import unittest

from ppd.agent_readiness.permit_type_coverage_inventory_packet_v2 import (
    build_permit_type_coverage_inventory_packet_v2,
    require_valid_permit_type_coverage_inventory_packet_v2,
    validate_permit_type_coverage_inventory_packet_v2,
)


class PermitTypeCoverageInventoryPacketV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = build_permit_type_coverage_inventory_packet_v2({})

    def assertInvalidContains(self, packet: dict, expected: str) -> None:
        errors = validate_permit_type_coverage_inventory_packet_v2(packet)
        self.assertTrue(errors, 'packet unexpectedly valid')
        self.assertIn(expected, '; '.join(errors))

    def test_default_packet_is_valid_and_has_review_rows(self) -> None:
        require_valid_permit_type_coverage_inventory_packet_v2(self.packet)
        self.assertEqual(self.packet['schema_version'], 'permit_type_coverage_inventory_packet_v2')
        self.assertTrue(self.packet['official_anchor_derived_permit_categories'])
        self.assertTrue(self.packet['existing_coverage_mappings'])
        self.assertTrue(self.packet['uncovered_or_weakly_covered_permit_families'])

    def test_rejects_missing_inventory_sections(self) -> None:
        checks = [
            ('official_anchor_derived_permit_categories', 'official_anchor_derived_permit_categories must include official permit categories'),
            ('existing_coverage_mappings', 'existing_coverage_mappings must include one mapping per official permit category'),
            ('uncovered_or_weakly_covered_permit_families', 'uncovered_or_weakly_covered_permit_families must include uncovered or weakly covered rows'),
            ('exact_offline_validation_commands', 'exact_offline_validation_commands must include validation commands'),
        ]
        for key, expected in checks:
            packet = copy.deepcopy(self.packet)
            packet[key] = []
            self.assertInvalidContains(packet, expected)

    def test_rejects_missing_row_required_review_fields(self) -> None:
        required_fields = [
            ('source_evidence_placeholders', 'source_evidence_placeholders'),
            ('stale_source_hold_notes', 'stale_source_hold_notes'),
            ('unsupported_path_notes', 'unsupported_path_notes'),
            ('exact_offline_validation_commands', 'exact_offline_validation_commands'),
        ]
        for field, expected in required_fields:
            packet = copy.deepcopy(self.packet)
            packet['all_permit_family_rows'][0][field] = []
            self.assertInvalidContains(packet, expected)

        packet = copy.deepcopy(self.packet)
        packet['all_permit_family_rows'][0].pop('reviewer_disposition_placeholder')
        self.assertInvalidContains(packet, 'reviewer_disposition_placeholder')

    def test_rejects_private_raw_and_session_artifacts(self) -> None:
        for key in ('auth_state', 'browser_trace', 'downloaded_document', 'raw_body', 'screenshot'):
            packet = copy.deepcopy(self.packet)
            packet[key] = 'committed artifact path'
            self.assertInvalidContains(packet, 'private/session/browser/raw/downloaded artifacts')

    def test_rejects_live_devhub_claims_guarantees_and_mutations(self) -> None:
        cases = [
            ('notes', 'live crawl completed for this packet', 'live crawl or DevHub claim'),
            ('notes', 'permit approval is certain', 'legal or permitting guarantee'),
            ('active_source_mutation', True, 'active mutation flags'),
            ('active_requirement_mutation', True, 'active mutation flags'),
            ('active_process_model_mutation', True, 'active mutation flags'),
            ('active_guardrail_mutation', True, 'active mutation flags'),
            ('active_prompt_mutation', True, 'active mutation flags'),
            ('active_contract_mutation', True, 'active mutation flags'),
            ('active_devhub_surface_mutation', True, 'active mutation flags'),
            ('active_release_state_mutation', True, 'active mutation flags'),
        ]
        for key, value, expected in cases:
            packet = copy.deepcopy(self.packet)
            packet[key] = value
            self.assertInvalidContains(packet, expected)


if __name__ == '__main__':
    unittest.main()
