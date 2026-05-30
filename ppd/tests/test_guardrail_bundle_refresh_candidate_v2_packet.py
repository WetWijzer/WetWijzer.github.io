from __future__ import annotations

import copy
from pathlib import Path
import unittest

from ppd.agent_readiness.guardrail_bundle_refresh_candidate_v2_packet import (
    load_guardrail_bundle_refresh_candidate_v2_fixture,
    validate_guardrail_bundle_refresh_candidate_v2_packet,
)

FIXTURES = Path(__file__).parent / "fixtures" / "guardrail_bundle_refresh_candidate_v2"


class GuardrailBundleRefreshCandidateV2PacketTest(unittest.TestCase):
    def _packet(self) -> dict:
        return load_guardrail_bundle_refresh_candidate_v2_fixture(FIXTURES / "valid_packet.json")

    def test_accepts_valid_fixture_first_candidate_packet(self) -> None:
        packet = self._packet()
        result = validate_guardrail_bundle_refresh_candidate_v2_packet(packet)

        self.assertTrue(result.valid)
        self.assertEqual(packet["packet_type"], "ppd.guardrail_bundle_refresh_candidate_packet.v2")
        self.assertEqual(packet["candidate_status"], "candidate_packet_only_not_applied")
        self.assertTrue(packet["affected_process_ids"])
        self.assertTrue(packet["affected_requirement_ids"])
        self.assertTrue(packet["reviewer_owners"])
        self.assertTrue(all(predicate["activation_allowed"] is False for predicate in packet["predicate_candidates"]))

    def test_rejects_uncited_predicates_missing_refs_checkpoints_and_owners(self) -> None:
        packet = copy.deepcopy(self._packet())
        packet["affected_process_ids"] = []
        packet["affected_requirement_ids"] = []
        packet["reviewer_owners"] = []
        predicate = packet["predicate_candidates"][0]
        predicate["source_evidence_ids"] = []
        predicate["affected_process_ids"] = []
        predicate["affected_requirement_ids"] = []
        predicate["reviewer_owner"] = ""
        predicate["checkpoint_expectations"] = {}

        result = validate_guardrail_bundle_refresh_candidate_v2_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("affected_process_ids must be a non-empty list", result.problems)
        self.assertIn("affected_requirement_ids must be a non-empty list", result.problems)
        self.assertIn("reviewer_owners must be a non-empty list", result.problems)
        self.assertIn("predicate_candidates[0] lacks source_evidence_ids", result.problems)
        self.assertIn("predicate_candidates[0] lacks affected_process_ids", result.problems)
        self.assertIn("predicate_candidates[0] lacks affected_requirement_ids", result.problems)
        self.assertIn("predicate_candidates[0] lacks reviewer_owner", result.problems)
        self.assertIn("predicate_candidates[0] lacks checkpoint_expectations", result.problems)
        self.assertIn("predicate_candidates[0] lacks reversible_action_predicates checkpoint expectations", result.problems)
        self.assertIn("predicate_candidates[0] lacks exact_confirmation_predicates checkpoint expectations", result.problems)

    def test_rejects_private_authenticated_facts_raw_artifacts_live_claims_and_guarantees(self) -> None:
        packet = copy.deepcopy(self._packet())
        packet["private_case_facts"] = {"address": "fixture redacted value"}
        packet["predicate_candidates"][0]["evidence"] = {
            "privacy_classification": "devhub_authenticated_private",
            "raw_pdf_path": "/tmp/private/downloads/application.pdf",
            "session_trace": "session://browser-trace",
            "summary": "Live LLM called DevHub and ran crawler processor execution; permit will issue.",
        }

        result = validate_guardrail_bundle_refresh_candidate_v2_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("private_case_facts must not include private or authenticated facts", result.problems)
        self.assertIn("predicate_candidates[0].evidence must not include private or authenticated facts", result.problems)
        self.assertIn("predicate_candidates[0].evidence.raw_pdf_path must not reference raw crawl, PDF, session, browser, WARC, download, or local artifacts", result.problems)
        self.assertIn("predicate_candidates[0].evidence.session_trace must not reference raw crawl, PDF, session, browser, WARC, download, or local artifacts", result.problems)
        self.assertIn("predicate_candidates[0].evidence.summary must not claim live LLM, DevHub, crawler, or processor execution", result.problems)
        self.assertIn("predicate_candidates[0].evidence.summary must not guarantee legal or permitting outcomes", result.problems)

    def test_rejects_enabled_consequential_controls_and_active_mutation_flags(self) -> None:
        packet = copy.deepcopy(self._packet())
        packet["predicate_candidates"][0]["consequential_controls"][0]["enabled"] = True
        packet["predicate_candidates"][0]["activation_allowed"] = True
        packet["attestations"]["active_guardrail_mutation"] = True
        packet["attestations"]["active_prompt_mutation"] = True
        packet["attestations"]["active_surface_registry_mutation"] = True
        packet["attestations"]["active_monitoring_mutation"] = True
        packet["attestations"]["release_state_mutation"] = True
        packet["attestations"]["active_agent_state_mutation"] = True
        packet["nested"] = {
            "mutation_flags": {
                "guardrail": True,
                "prompt": True,
                "surface_registry": True,
                "monitoring": True,
                "release_state": True,
                "agent_state": True
            }
        }

        result = validate_guardrail_bundle_refresh_candidate_v2_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("predicate_candidates[0].consequential_controls[0] must not enable consequential controls", result.problems)
        self.assertIn("predicate_candidates[0] must keep activation_allowed false", result.problems)
        self.assertIn("attestations.active_guardrail_mutation must be false", result.problems)
        self.assertIn("attestations.active_prompt_mutation must be false", result.problems)
        self.assertIn("attestations.active_surface_registry_mutation must be false", result.problems)
        self.assertIn("attestations.active_monitoring_mutation must be false", result.problems)
        self.assertIn("attestations.release_state_mutation must be false", result.problems)
        self.assertIn("attestations.active_agent_state_mutation must be false", result.problems)
        self.assertIn("nested.mutation_flags.guardrail must be false", result.problems)
        self.assertIn("nested.mutation_flags.prompt must be false", result.problems)
        self.assertIn("nested.mutation_flags.surface_registry must be false", result.problems)
        self.assertIn("nested.mutation_flags.monitoring must be false", result.problems)
        self.assertIn("nested.mutation_flags.release_state must be false", result.problems)
        self.assertIn("nested.mutation_flags.agent_state must be false", result.problems)


if __name__ == "__main__":
    unittest.main()
