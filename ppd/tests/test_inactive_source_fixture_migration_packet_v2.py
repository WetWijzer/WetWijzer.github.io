from __future__ import annotations

import unittest
from copy import deepcopy
from pathlib import Path

from ppd.inactive_source_fixture_migration_packet_v2 import (
    PACKET_TYPE,
    REQUIRED_ATTESTATIONS,
    build_inactive_source_fixture_migration_packet_v2_from_fixture,
    validate_inactive_source_fixture_migration_packet_v2,
)

FIXTURE = Path(__file__).parent / 'fixtures' / 'inactive_source_fixture_migration_packet_v2' / 'source_packets.json'
DEFERRED_FIXTURE = Path(__file__).parent / 'fixtures' / 'inactive_source_fixture_migration_packet_v2' / 'deferred_only_source_packets.json'


def _valid_packet() -> dict[str, object]:
    return build_inactive_source_fixture_migration_packet_v2_from_fixture(FIXTURE)


class InactiveSourceFixtureMigrationPacketV2Test(unittest.TestCase):
    def test_builds_fixture_first_inactive_source_migration_packet_v2(self) -> None:
        packet = _valid_packet()

        self.assertEqual(packet['packet_type'], PACKET_TYPE)
        self.assertEqual(packet['packet_version'], 2)
        self.assertEqual(packet['attestations'], REQUIRED_ATTESTATIONS)
        self.assertTrue(packet['offline_validation_commands'])

        patch_rows = packet['cited_fixture_only_source_registry_metadata_patch_rows']
        checksum_rows = packet['before_after_fixture_checksums']
        rollback_rows = packet['rollback_checkpoints']
        reviewer_rows = packet['reviewer_owner_fields']

        self.assertIsInstance(patch_rows, list)
        self.assertTrue(patch_rows)
        self.assertIsInstance(checksum_rows, list)
        self.assertTrue(checksum_rows)
        self.assertIsInstance(rollback_rows, list)
        self.assertTrue(rollback_rows)
        self.assertIsInstance(reviewer_rows, list)
        self.assertTrue(reviewer_rows)

        first = patch_rows[0]
        self.assertIs(first['fixture_only'], True)
        self.assertIs(first['source_registry_fixture_patch'], True)
        self.assertIs(first['active_source_registry_mutation'], False)
        self.assertTrue(first['reviewer_owner'])
        self.assertTrue(first['citations'])

        checksum = checksum_rows[0]
        self.assertEqual(len(checksum['before_fixture_checksum']), 64)
        self.assertEqual(len(checksum['after_fixture_checksum']), 64)
        validate_inactive_source_fixture_migration_packet_v2(packet)

    def test_validation_rejects_active_source_registry_mutation(self) -> None:
        packet = _valid_packet()
        broken = deepcopy(packet)
        broken['cited_fixture_only_source_registry_metadata_patch_rows'][0]['active_source_registry_mutation'] = True

        with self.assertRaisesRegex(ValueError, 'active_source_registry_mutation'):
            validate_inactive_source_fixture_migration_packet_v2(broken)

    def test_validation_rejects_missing_checksums_and_reviewer_owner_fields(self) -> None:
        packet = _valid_packet()
        broken = deepcopy(packet)
        broken['before_after_fixture_checksums'] = []
        broken['reviewer_owner_fields'] = []

        with self.assertRaisesRegex(ValueError, 'before/after fixture checksums'):
            validate_inactive_source_fixture_migration_packet_v2(broken)

    def test_builder_rejects_unapproved_migration_matrix(self) -> None:
        with self.assertRaisesRegex(ValueError, 'at least one approve row'):
            build_inactive_source_fixture_migration_packet_v2_from_fixture(DEFERRED_FIXTURE)

    def test_validation_rejects_uncited_source_fixture_rows(self) -> None:
        packet = _valid_packet()
        broken = deepcopy(packet)
        broken['cited_fixture_only_source_registry_metadata_patch_rows'][0]['citations'] = []

        with self.assertRaisesRegex(ValueError, 'citations must be non-empty'):
            validate_inactive_source_fixture_migration_packet_v2(broken)

    def test_validation_rejects_checksum_rows_missing_before_after_values(self) -> None:
        packet = _valid_packet()
        broken = deepcopy(packet)
        broken['before_after_fixture_checksums'][0]['before_fixture_checksum'] = ''

        with self.assertRaisesRegex(ValueError, 'before_fixture_checksum'):
            validate_inactive_source_fixture_migration_packet_v2(broken)

    def test_validation_rejects_missing_rollback_checkpoints(self) -> None:
        packet = _valid_packet()
        broken = deepcopy(packet)
        broken['rollback_checkpoints'] = []

        with self.assertRaisesRegex(ValueError, 'rollback checkpoints'):
            validate_inactive_source_fixture_migration_packet_v2(broken)

    def test_validation_rejects_non_allowlisted_and_authenticated_urls(self) -> None:
        packet = _valid_packet()
        outside = deepcopy(packet)
        outside['cited_fixture_only_source_registry_metadata_patch_rows'][0]['after_metadata_value'] = 'https://example.com/ppd'

        with self.assertRaisesRegex(ValueError, 'non-allowlisted URL'):
            validate_inactive_source_fixture_migration_packet_v2(outside)

        authenticated = deepcopy(packet)
        authenticated['cited_fixture_only_source_registry_metadata_patch_rows'][0]['after_metadata_value'] = 'https://devhub.portlandoregon.gov/account/dashboard'

        with self.assertRaisesRegex(ValueError, 'authenticated or account-scoped URL'):
            validate_inactive_source_fixture_migration_packet_v2(authenticated)

    def test_validation_rejects_raw_browser_and_live_processor_artifacts(self) -> None:
        packet = _valid_packet()
        raw = deepcopy(packet)
        raw['cited_fixture_only_source_registry_metadata_patch_rows'][0]['raw_body'] = 'raw body'

        with self.assertRaisesRegex(ValueError, 'raw/download/archive/browser artifact'):
            validate_inactive_source_fixture_migration_packet_v2(raw)

        live = deepcopy(packet)
        live['rollback_checkpoints'][0]['summary'] = 'Live crawl completed and processor completed for this fixture.'

        with self.assertRaisesRegex(ValueError, 'prohibited live'):
            validate_inactive_source_fixture_migration_packet_v2(live)

    def test_validation_rejects_legal_or_permitting_outcome_guarantees(self) -> None:
        packet = _valid_packet()
        broken = deepcopy(packet)
        broken['cited_fixture_only_source_registry_metadata_patch_rows'][0]['after_metadata_value'] = 'This guarantees permit approval.'

        with self.assertRaisesRegex(ValueError, 'legal outcome guarantee'):
            validate_inactive_source_fixture_migration_packet_v2(broken)

    def test_validation_rejects_active_mutation_flags_for_all_protected_states(self) -> None:
        protected_flags = (
            'active_source_mutation',
            'active_schedule_mutation',
            'active_requirement_mutation',
            'active_process_mutation',
            'active_guardrail_mutation',
            'active_prompt_mutation',
            'active_monitoring_mutation',
            'active_release_state_mutation',
            'active_agent_state_mutation',
        )

        for flag in protected_flags:
            packet = _valid_packet()
            packet['cited_fixture_only_source_registry_metadata_patch_rows'][0][flag] = True
            with self.subTest(flag=flag):
                with self.assertRaisesRegex(ValueError, 'mutation flag'):
                    validate_inactive_source_fixture_migration_packet_v2(packet)

    def test_validation_rejects_nested_mutation_flags(self) -> None:
        packet = _valid_packet()
        packet['mutation_flags'] = {'source': False, 'schedule': True}

        with self.assertRaisesRegex(ValueError, 'mutation flag'):
            validate_inactive_source_fixture_migration_packet_v2(packet)


if __name__ == '__main__':
    unittest.main()
