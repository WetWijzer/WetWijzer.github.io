from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ppd.agent_readiness.active_promotion_preflight_gate_v1 import (
    validate_active_promotion_preflight_gate_v1,
)


FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'active_promotion_preflight_gate_v1' / 'valid_preflight_packet.json'


def _valid_packet() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))


class ActivePromotionPreflightGateV1Tests(unittest.TestCase):
    def test_valid_fixture_packet_passes(self) -> None:
        result = validate_active_promotion_preflight_gate_v1(_valid_packet())

        self.assertTrue(result.valid)
        self.assertEqual(result.problems, ())

    def test_rejects_missing_required_preflight_sections(self) -> None:
        packet = _valid_packet()
        for key in (
            'final_go_no_go_rows',
            'human_approval_placeholders',
            'active_mutation_blocker_inventory',
            'validation_replay_checklist',
            'rollback_readiness_summary',
            'release_state_nonmutation_notes',
        ):
            packet.pop(key)

        result = validate_active_promotion_preflight_gate_v1(packet)

        self.assertFalse(result.valid)
        self.assertIn('missing_final_go_no_go_rows', result.problems)
        self.assertIn('missing_human_approval_placeholders', result.problems)
        self.assertIn('missing_active_mutation_blocker_inventory', result.problems)
        self.assertIn('missing_validation_replay_checklist', result.problems)
        self.assertIn('missing_rollback_readiness_summary', result.problems)
        self.assertIn('missing_release_state_nonmutation_notes', result.problems)

    def test_rejects_artifacts_claims_language_and_mutation_flags(self) -> None:
        packet = copy.deepcopy(_valid_packet())
        packet['private_artifact'] = 'blocked'
        packet['review_notes'] = [
            'Authenticated artifact with session cookie, browser state, screenshot, HAR file, and auth file.',
            'Raw crawl output included raw PDF and downloaded data.',
            'Live execution finished, promotion executed, and release complete.',
            'Approval guaranteed; agent will submit the permit.',
        ]
        packet['active_artifact_mutated'] = True
        packet['active_prompt_mutated'] = True
        packet['active_release_state_mutated'] = True
        packet['active_fixture_mutated'] = True
        packet['active_agent_state_mutated'] = True

        result = validate_active_promotion_preflight_gate_v1(packet)
        joined = '\n'.join(result.problems)

        self.assertFalse(result.valid)
        self.assertIn('forbidden_artifact_key', joined)
        self.assertIn('private_or_authenticated_artifact', joined)
        self.assertIn('session_or_browser_artifact', joined)
        self.assertIn('screenshot_trace_har_or_auth_file', joined)
        self.assertIn('raw_pdf_or_downloaded_data', joined)
        self.assertIn('live_execution_or_promotion_claim', joined)
        self.assertIn('outcome_guarantee', joined)
        self.assertIn('consequential_action_language', joined)
        self.assertIn('active_mutation_flag', joined)


if __name__ == '__main__':
    unittest.main()
