from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from ppd.devhub.readonly_observation_delta_v3 import (
    OFFLINE_VALIDATION_COMMANDS,
    ReadOnlyObservationDeltaV3Error,
    build_readonly_observation_delta_packet_v3,
    validate_readonly_observation_delta_packet_v3,
    validate_source_observation_notes_v3,
)

FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'devhub' / 'readonly_observation_notes_v3.json'


class DevHubReadOnlyObservationDeltaV3Test(unittest.TestCase):
    def load_fixture(self) -> dict:
        return json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))

    def test_builds_complete_redacted_delta_packet_from_fixture_notes(self) -> None:
        packet = build_readonly_observation_delta_packet_v3(self.load_fixture())

        self.assertEqual(packet['schema_version'], 'devhub_readonly_observation_delta_packet_v3')
        self.assertEqual(packet['mode'], 'offline_fixture_inactive_delta')
        self.assertEqual(packet['validation_commands'], OFFLINE_VALIDATION_COMMANDS)
        self.assertTrue(packet['surface_map_candidate_deltas'])
        self.assertTrue(packet['selector_confidence_rows'])
        self.assertTrue(packet['validation_message_rows'])
        self.assertTrue(packet['abort_condition_rows'])
        self.assertTrue(packet['reviewer_hold_rows'])
        self.assertEqual(validate_readonly_observation_delta_packet_v3(packet), [])

    def test_rows_are_inactive_redacted_candidate_only_and_require_reviewer_controls(self) -> None:
        packet = build_readonly_observation_delta_packet_v3(self.load_fixture())
        delta = packet['surface_map_candidate_deltas'][0]

        self.assertEqual(delta['activation_state'], 'inactive_reviewer_candidate_delta')
        self.assertTrue(delta['redacted'])
        self.assertTrue(delta['candidate_only'])
        self.assertTrue(delta['requires_attendance'])
        self.assertTrue(delta['requires_exact_confirmation'])
        self.assertTrue(delta['field_candidate_ids'])
        self.assertTrue(delta['validation_message_row_ids'])
        self.assertTrue(delta['abort_condition_row_ids'])
        self.assertTrue(delta['reviewer_hold_row_ids'])
        self.assertTrue(all(row['candidate_only'] for row in packet['selector_confidence_rows']))
        self.assertTrue(all(row['candidate_only'] for row in packet['validation_message_rows']))
        self.assertTrue(all(row['candidate_only'] for row in packet['abort_condition_rows']))
        self.assertTrue(all(row['candidate_only'] for row in packet['reviewer_hold_rows']))

    def test_redacts_common_private_surface_values_before_delta_output(self) -> None:
        source = self.load_fixture()
        source['observations'][0]['validation_notes'].append(
            'Synthetic fixture mentioned tester@example.com, 503-555-0199, and 26-123456-000-00-CO.'
        )

        packet = build_readonly_observation_delta_packet_v3(source)
        rendered = json.dumps(packet, sort_keys=True)

        self.assertIn('[redacted-email]', rendered)
        self.assertIn('[redacted-phone]', rendered)
        self.assertIn('[redacted-permit-id]', rendered)
        self.assertNotIn('tester@example.com', rendered)
        self.assertNotIn('503-555-0199', rendered)
        self.assertNotIn('26-123456-000-00-CO', rendered)

    def test_rejects_missing_required_delta_rows(self) -> None:
        required_rows = {
            'surface_map_candidate_deltas': 'missing_redacted_surface_rows',
            'selector_confidence_rows': 'missing_selector_confidence_rows',
            'validation_message_rows': 'missing_validation_message_rows',
            'abort_condition_rows': 'missing_abort_condition_rows',
            'reviewer_hold_rows': 'missing_reviewer_hold_rows',
            'validation_commands': 'missing_validation_commands',
        }
        packet = build_readonly_observation_delta_packet_v3(self.load_fixture())

        for field, expected_error in required_rows.items():
            with self.subTest(field=field):
                invalid = copy.deepcopy(packet)
                invalid[field] = []
                self.assertIn(expected_error, validate_readonly_observation_delta_packet_v3(invalid))

    def test_rejects_surface_rows_without_redaction_candidate_and_reviewer_controls(self) -> None:
        packet = build_readonly_observation_delta_packet_v3(self.load_fixture())
        invalid = copy.deepcopy(packet)
        delta = invalid['surface_map_candidate_deltas'][0]
        delta['redacted'] = False
        delta['candidate_only'] = False
        delta['requires_attendance'] = False
        delta['requires_exact_confirmation'] = False
        delta['field_candidate_ids'] = []
        delta['validation_message_row_ids'] = []
        delta['abort_condition_row_ids'] = []
        delta['reviewer_hold_row_ids'] = []

        errors = validate_readonly_observation_delta_packet_v3(invalid)

        self.assertIn('surface_delta_not_marked_redacted', errors)
        self.assertIn('surface_delta_not_candidate_only', errors)
        self.assertIn('surface_delta_missing_attendance_requirement', errors)
        self.assertIn('surface_delta_missing_exact_confirmation_requirement', errors)
        self.assertIn('surface_delta_missing_field_candidate_ids', errors)
        self.assertIn('surface_delta_missing_validation_message_row_ids', errors)
        self.assertIn('surface_delta_missing_abort_condition_row_ids', errors)
        self.assertIn('surface_delta_missing_reviewer_hold_row_ids', errors)

    def test_rejects_private_browser_artifacts_screenshots_traces_har_and_unapproved_actions(self) -> None:
        source = self.load_fixture()
        source['observations'][0]['screenshot'] = 'screen.png'
        source['observations'][0]['trace_file'] = 'trace.zip'
        source['observations'][0]['har_data'] = {'path': 'network.har'}
        source['observations'][0]['reviewer_notes'].append('Automation may submit the application after review.')

        errors = validate_source_observation_notes_v3(source)

        self.assertIn('prohibited_private_or_browser_artifact_key', errors)
        self.assertIn('unapproved_consequential_action_claim', errors)
        with self.assertRaises(ReadOnlyObservationDeltaV3Error):
            build_readonly_observation_delta_packet_v3(source)

    def test_rejects_live_auth_official_completion_and_legal_guarantee_claims(self) -> None:
        source = self.load_fixture()
        source['observations'][0]['reviewer_notes'].extend([
            'The live authenticated DevHub session showed this field.',
            'The submission completed successfully.',
            'This packet is legally sufficient and will be approved.',
        ])

        errors = validate_source_observation_notes_v3(source)

        self.assertIn('live_authenticated_devhub_claim', errors)
        self.assertIn('official_action_completion_claim', errors)
        self.assertIn('legal_or_permitting_guarantee', errors)

    def test_rejects_active_mutation_flags_in_source_or_delta(self) -> None:
        source = self.load_fixture()
        source['active_devhub_surface_mutation'] = True

        self.assertIn('active_mutation_flag', validate_source_observation_notes_v3(source))

        packet = build_readonly_observation_delta_packet_v3(self.load_fixture())
        mutation_flags = [
            'active_devhub_surface_mutation',
            'active_prompt_mutation',
            'active_guardrail_mutation',
            'active_contract_mutation',
            'active_process_model_mutation',
            'active_source_mutation',
            'active_release_state_mutation',
        ]
        for flag in mutation_flags:
            with self.subTest(flag=flag):
                mutated = copy.deepcopy(packet)
                mutated[flag] = True
                self.assertIn('active_mutation_flag', validate_readonly_observation_delta_packet_v3(mutated))

    def test_delta_requires_exact_offline_validation_commands(self) -> None:
        packet = build_readonly_observation_delta_packet_v3(self.load_fixture())
        packet['validation_commands'] = [['python3', 'ppd/daemon/ppd_daemon.py', '--self-test']]

        self.assertIn('validation_commands_not_exact', validate_readonly_observation_delta_packet_v3(packet))


if __name__ == '__main__':
    unittest.main()
