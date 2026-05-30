from __future__ import annotations

from copy import deepcopy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.requirement_regeneration_promotion_candidate_packet import (
    build_requirement_regeneration_promotion_candidate_packet,
    validate_requirement_regeneration_promotion_candidate_packet,
)

FIXTURES = Path(__file__).parent / 'fixtures' / 'agent_readiness'
SOURCES = FIXTURES / 'requirement_regeneration_promotion_candidate_sources.json'


def _load_sources() -> tuple[dict, dict, dict]:
    with SOURCES.open('r', encoding='utf-8') as handle:
        payload = json.load(handle)
    return (
        payload['requirement_regeneration_rehearsal_tranche_packet'],
        payload['requirement_rerun_disposition_packet'],
        payload['process_model_impact_review_packet'],
    )


class RequirementRegenerationPromotionCandidatePacketTest(unittest.TestCase):
    def test_builds_fixture_first_promotion_candidate_packet(self) -> None:
        packet = build_requirement_regeneration_promotion_candidate_packet(*_load_sources())
        result = validate_requirement_regeneration_promotion_candidate_packet(packet)

        self.assertTrue(result.valid, result.problems)
        self.assertEqual(packet['packet_type'], 'ppd.requirement_regeneration_promotion_candidate_packet.v1')
        self.assertEqual(packet['candidate_status'], 'candidate_deltas_not_promoted')
        self.assertFalse(packet['promotion_policy']['uses_live_extraction'])
        self.assertFalse(packet['promotion_policy']['invokes_processors'])
        self.assertFalse(packet['promotion_policy']['mutates_active_artifacts'])
        self.assertFalse(packet['promotion_policy']['mutates_active_prompts'])
        self.assertEqual(len(packet['candidate_requirement_deltas']), 2)
        self.assertEqual(len(packet['candidate_process_deltas']), 1)
        self.assertEqual(len(packet['candidate_guardrail_deltas']), 1)

    def test_candidate_sections_are_cited_and_have_affected_ids_and_review_owners(self) -> None:
        packet = build_requirement_regeneration_promotion_candidate_packet(*_load_sources())

        for item in packet['candidate_requirement_deltas']:
            self.assertEqual(item['status'], 'candidate_only')
            self.assertTrue(item['affected_requirement_ids'])
            self.assertTrue(item['source_packet_refs'])
            self.assertTrue(item['source_evidence_ids'])
        for item in packet['candidate_process_deltas']:
            self.assertTrue(item['affected_process_ids'])
            self.assertTrue(item['source_evidence_ids'])
        for item in packet['candidate_guardrail_deltas']:
            self.assertTrue(item['affected_guardrail_ids'])
            self.assertTrue(item['source_evidence_ids'])

        owner_roles = {owner['role'] for owner in packet['reviewer_owner_fields']}
        self.assertIn('requirement_delta_reviewer', owner_roles)
        self.assertIn('process_model_reviewer', owner_roles)
        self.assertIn('guardrail_reviewer', owner_roles)

    def test_expected_commands_and_attestations_remain_offline(self) -> None:
        packet = build_requirement_regeneration_promotion_candidate_packet(*_load_sources())

        commands = packet['expected_offline_validation_commands']
        self.assertIn(['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'], commands)
        attestation_ids = {item['attestation_id'] for item in packet['attestations']}
        self.assertEqual(
            {'no-live-extraction', 'no-processor-invocation', 'no-active-artifact-mutation', 'no-outcome-guarantees'},
            attestation_ids,
        )

    def test_validator_rejects_uncited_delta_private_paths_and_mutation_claims(self) -> None:
        packet = build_requirement_regeneration_promotion_candidate_packet(*_load_sources())
        altered = deepcopy(packet)
        altered['candidate_requirement_deltas'][0]['source_evidence_ids'] = []
        altered['candidate_guardrail_deltas'][0]['summary'] = 'Active artifact mutated after processor executed.'
        altered['rollback_notes'][0]['private_path'] = '/tmp/private-regeneration-output.json'
        altered['promotion_policy']['mutates_active_artifacts'] = True

        result = validate_requirement_regeneration_promotion_candidate_packet(altered)
        self.assertFalse(result.valid)
        joined = '; '.join(result.problems)
        self.assertIn('source_evidence_ids', joined)
        self.assertIn('mutates_active_artifacts', joined)
        self.assertIn('private', joined)
        self.assertIn('processor', joined)

    def test_validator_rejects_missing_affected_ids_rollback_owners_and_commands(self) -> None:
        packet = build_requirement_regeneration_promotion_candidate_packet(*_load_sources())
        altered = deepcopy(packet)
        altered['candidate_requirement_deltas'][0].pop('requirement_id', None)
        altered['candidate_requirement_deltas'][0]['affected_requirement_ids'] = []
        altered['candidate_process_deltas'][0].pop('process_id', None)
        altered['candidate_process_deltas'][0]['affected_process_ids'] = []
        altered['candidate_guardrail_deltas'][0].pop('guardrail_bundle_id', None)
        altered['candidate_guardrail_deltas'][0]['affected_guardrail_ids'] = []
        altered['rollback_notes'] = []
        altered['reviewer_owner_fields'] = []
        altered['expected_offline_validation_commands'] = []

        result = validate_requirement_regeneration_promotion_candidate_packet(altered)
        self.assertFalse(result.valid)
        joined = '; '.join(result.problems)
        self.assertIn('affected requirement id', joined)
        self.assertIn('affected process id', joined)
        self.assertIn('affected guardrail id', joined)
        self.assertIn('rollback_notes', joined)
        self.assertIn('reviewer_owner_fields', joined)
        self.assertIn('expected_offline_validation_commands', joined)

    def test_validator_rejects_runtime_references_guarantees_and_active_state_flags(self) -> None:
        packet = build_requirement_regeneration_promotion_candidate_packet(*_load_sources())
        altered = deepcopy(packet)
        altered['candidate_requirement_deltas'][0]['raw_body_ref'] = 'raw_body_download/archive.warc.gz'
        altered['candidate_process_deltas'][0]['private_case_fact'] = 'applicant private parcel fact'
        altered['candidate_guardrail_deltas'][0]['summary'] = 'Permit will be approved after live extraction ran.'
        altered['promotion_policy']['mutates_active_prompts'] = True
        altered['promotion_policy']['writes_release_state'] = True
        altered['active_requirement_mutation_enabled'] = True

        result = validate_requirement_regeneration_promotion_candidate_packet(altered)
        self.assertFalse(result.valid)
        joined = '; '.join(result.problems)
        self.assertIn('raw', joined)
        self.assertIn('private', joined)
        self.assertIn('legal or permitting outcome guarantee', joined)
        self.assertIn('live extraction', joined)
        self.assertIn('mutates_active_prompts', joined)
        self.assertIn('writes_release_state', joined)
        self.assertIn('active requirement', joined)

    def test_validator_rejects_live_or_processor_validation_commands(self) -> None:
        packet = build_requirement_regeneration_promotion_candidate_packet(*_load_sources())
        altered = deepcopy(packet)
        altered['expected_offline_validation_commands'].append(['python3', 'ppd/processors/run.py', '--live'])

        result = validate_requirement_regeneration_promotion_candidate_packet(altered)
        self.assertFalse(result.valid)
        self.assertIn('must remain offline', '; '.join(result.problems))


if __name__ == '__main__':
    unittest.main()
