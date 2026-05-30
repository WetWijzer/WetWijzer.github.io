from __future__ import annotations

import copy
import unittest

from ppd.crawler.public_source_change_impact_rehearsal_v1 import (
    PublicSourceChangeImpactRehearsalError,
    build_public_source_change_impact_rehearsal_v1,
    require_valid_public_source_change_impact_rehearsal_v1,
    validate_public_source_change_impact_rehearsal_v1,
)


class PublicSourceChangeImpactRehearsalV1Test(unittest.TestCase):
    def test_builder_produces_valid_fixture_first_rehearsal(self) -> None:
        packet = build_public_source_change_impact_rehearsal_v1()
        result = validate_public_source_change_impact_rehearsal_v1(packet)
        self.assertTrue(result.valid)
        self.assertTrue(packet['fixture_first'])
        self.assertTrue(packet['rehearsal_only'])
        self.assertFalse(packet['source_mutation_active'])
        self.assertEqual(packet['rehearsal_summary']['impact_row_count'], 1)

    def test_rejects_required_unsafe_or_incomplete_rows(self) -> None:
        cases = [
            (lambda packet: packet['impact_rows'][0].update({'citations': []}), 'citations must include'),
            (lambda packet: packet['impact_rows'][0].update({'source_id': 'unknown-source'}), 'unknown source_id unknown-source'),
            (lambda packet: packet['impact_rows'][0].update({'affected_requirement_ids': ['unknown-req']}), 'unknown requirement_id unknown-req'),
            (lambda packet: packet['impact_rows'][0].update({'freshness_rationale': ''}), 'freshness_rationale is required'),
            (lambda packet: packet['impact_rows'][0].update({'change_rationale': ''}), 'change_rationale is required'),
            (lambda packet: packet['impact_rows'][0]['citations'][0].update({'public_url': 'https://user:secret@www.portland.gov/ppd'}), 'authenticated or credential-bearing URL'),
            (lambda packet: packet['impact_rows'][0].update({'debug_ref': '/tmp/ppd/raw/body.html'}), 'forbidden raw body'),
            (lambda packet: packet['impact_rows'][0].update({'download_ref': '/tmp/ppd/downloads/source.pdf'}), 'downloaded-document'),
            (lambda packet: packet['impact_rows'][0].update({'processorCompleted': True}), 'processor completion claims are not allowed'),
            (lambda packet: packet['impact_rows'][0].update({'impact_summary': 'This guarantees approval for the permit.'}), 'outcome guarantee'),
            (lambda packet: packet.update({'active_source_mutation': True}), 'cannot mutate active state'),
            (lambda packet: packet.update({'active_requirement_mutation': True}), 'cannot mutate active state'),
            (lambda packet: packet.update({'active_process_mutation': True}), 'cannot mutate active state'),
            (lambda packet: packet.update({'active_guardrail_mutation': True}), 'cannot mutate active state'),
            (lambda packet: packet.update({'active_monitoring_mutation': True}), 'cannot mutate active state'),
            (lambda packet: packet.update({'active_release_state_mutation': True}), 'cannot mutate active state'),
            (lambda packet: packet.update({'active_agent_state_mutation': True}), 'cannot mutate active state'),
        ]
        for mutation, expected in cases:
            with self.subTest(expected=expected):
                packet = copy.deepcopy(build_public_source_change_impact_rehearsal_v1())
                mutation(packet)
                with self.assertRaises(PublicSourceChangeImpactRehearsalError) as exc_info:
                    require_valid_public_source_change_impact_rehearsal_v1(packet)
                self.assertIn(expected, str(exc_info.exception))

    def test_rejects_uncited_affected_requirement_even_with_other_citation(self) -> None:
        packet = copy.deepcopy(build_public_source_change_impact_rehearsal_v1())
        packet['requirement_registry_snapshot'].append(
            {
                'requirement_id': 'req-extra-review',
                'source_id': 'ppd-submit-plans-online',
                'requirement_type': 'action_gate',
            }
        )
        packet['impact_rows'][0]['affected_requirement_ids'].append('req-extra-review')
        with self.assertRaises(PublicSourceChangeImpactRehearsalError) as exc_info:
            require_valid_public_source_change_impact_rehearsal_v1(packet)
        self.assertIn('citations must cite every affected requirement_id: req-extra-review', str(exc_info.exception))


if __name__ == '__main__':
    unittest.main()
