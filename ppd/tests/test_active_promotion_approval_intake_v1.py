from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.active_promotion_approval_intake_v1 import (
    PACKET_TYPE,
    build_active_promotion_approval_intake_v1,
    validate_active_promotion_approval_intake_source_v1,
    validate_active_promotion_approval_intake_v1,
)

FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'active_promotion_approval_intake_v1' / 'active_preflight_gate_v1.json'


def _source_packet() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))


class ActivePromotionApprovalIntakeV1Tests(unittest.TestCase):
    def test_builds_ordered_reviewer_intake_from_preflight_fixture(self) -> None:
        packet = build_active_promotion_approval_intake_v1(_source_packet())

        self.assertEqual(packet['packet_type'], PACKET_TYPE)
        self.assertEqual(packet['source_packet']['packet_type'], 'ppd.active_promotion_preflight_gate.v1')
        self.assertEqual([row['order'] for row in packet['reviewer_decision_rows']], [1, 2])
        self.assertEqual(packet['reviewer_decision_rows'][0]['source_decision'], 'no_go')
        self.assertEqual(packet['reviewer_decision_rows'][1]['source_decision'], 'blocked')
        self.assertEqual(packet['approval_evidence_placeholders'][0]['approval_status'], 'pending_evidence')
        self.assertEqual(
            packet['unresolved_blocker_carry_forward'][0]['carry_forward_status'],
            'unresolved_pending_reviewer_clearance',
        )
        self.assertEqual(
            packet['rollback_readiness_acknowledgements'][0]['reviewer_acknowledgement_placeholder'],
            'pending_rollback_owner_acknowledgement',
        )
        self.assertEqual(
            packet['validation_replay_acknowledgements'][0]['reviewer_acknowledgement_placeholder'],
            'pending_validation_replay_acknowledgement',
        )
        self.assertGreaterEqual(len(packet['no_go_reason_placeholders']), 2)
        self.assertTrue(validate_active_promotion_approval_intake_v1(packet)['valid'])

    def test_nonmutation_acknowledgements_are_all_false_and_complete(self) -> None:
        packet = build_active_promotion_approval_intake_v1(_source_packet())

        self.assertEqual(
            packet['nonmutation_acknowledgements'],
            {
                'fixture_promotion_applied': False,
                'fixture_mutated': False,
                'active_artifacts_mutated': False,
                'active_artifact_mutation_requested': False,
                'prompts_changed': False,
                'prompt_mutation_requested': False,
                'release_state_updated': False,
                'release_state_mutation_requested': False,
                'agent_state_updated': False,
                'agent_state_mutation_requested': False,
                'live_sources_crawled': False,
                'devhub_accessed': False,
                'official_actions_performed': False,
            },
        )

    def test_source_validation_rejects_missing_sections_and_unsafe_content(self) -> None:
        packet = copy.deepcopy(_source_packet())
        packet.pop('validation_replay_checklist')
        packet['notes'] = 'Promoted to active with a DevHub session and screenshot.'
        packet['active_artifact_mutated'] = True

        result = validate_active_promotion_approval_intake_source_v1(packet)
        joined = '\n'.join(result['problems'])

        self.assertFalse(result['valid'])
        self.assertIn('source_missing_validation_replay_checklist', result['problems'])
        self.assertIn('forbidden_text:promoted to active', joined)
        self.assertIn('forbidden_text:devhub session', joined)
        self.assertIn('forbidden_text:screenshot', joined)
        self.assertIn('forbidden_mutation_flag', joined)

    def test_intake_validation_rejects_missing_required_rows_and_fields(self) -> None:
        packet = build_active_promotion_approval_intake_v1(_source_packet())
        packet['reviewer_decision_rows'][0].pop('evidence_placeholder')
        packet['approval_evidence_placeholders'][0].pop('evidence_reference_placeholder')
        packet['unresolved_blocker_carry_forward'][0].pop('clearance_evidence_placeholder')
        packet['rollback_readiness_acknowledgements'][0].pop('reviewer_acknowledgement_placeholder')
        packet['validation_replay_acknowledgements'][0].pop('reviewer_acknowledgement_placeholder')
        packet['no_go_reason_placeholders'][0].pop('reason_placeholder')

        result = validate_active_promotion_approval_intake_v1(packet)
        joined = '\n'.join(result['problems'])

        self.assertFalse(result['valid'])
        self.assertIn('reviewer_decision_rows[0]:missing_evidence_placeholder', joined)
        self.assertIn('approval_evidence_placeholders[0]:missing_evidence_reference_placeholder', joined)
        self.assertIn('unresolved_blocker_carry_forward[0]:missing_clearance_evidence_placeholder', joined)
        self.assertIn('rollback_readiness_acknowledgements[0]:missing_reviewer_acknowledgement_placeholder', joined)
        self.assertIn('validation_replay_acknowledgements[0]:missing_reviewer_acknowledgement_placeholder', joined)
        self.assertIn('no_go_reason_placeholders[0]:missing_reason_placeholder', joined)

    def test_intake_validation_rejects_missing_lists_and_true_nonmutation_flags(self) -> None:
        packet = build_active_promotion_approval_intake_v1(_source_packet())
        packet.pop('approval_evidence_placeholders')
        packet['nonmutation_acknowledgements'].pop('agent_state_updated')
        packet['nonmutation_acknowledgements']['release_state_updated'] = True

        result = validate_active_promotion_approval_intake_v1(packet)
        joined = '\n'.join(result['problems'])

        self.assertFalse(result['valid'])
        self.assertIn('missing_approval_evidence_placeholders', result['problems'])
        self.assertIn('missing_nonmutation_acknowledgement:agent_state_updated', result['problems'])
        self.assertIn('nonmutation_acknowledgement_must_be_false:release_state_updated', result['problems'])
        self.assertIn('forbidden_mutation_flag', joined)

    def test_rejects_private_artifacts_raw_data_outcome_claims_and_consequential_language(self) -> None:
        packet = build_active_promotion_approval_intake_v1(_source_packet())
        packet['browser_state'] = {'path': 'state.json'}
        packet['notes'] = 'Approval guaranteed after raw PDF review; agent will submit final payment.'
        packet['trace_file'] = 'trace.zip'

        result = validate_active_promotion_approval_intake_v1(packet)
        joined = '\n'.join(result['problems'])

        self.assertFalse(result['valid'])
        self.assertIn('forbidden_artifact_key', joined)
        self.assertIn('forbidden_text:approval guaranteed', joined)
        self.assertIn('forbidden_text:raw pdf', joined)
        self.assertIn('forbidden_text:agent will submit', joined)
        self.assertIn('forbidden_text:final payment', joined)


if __name__ == '__main__':
    unittest.main()
