from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from ppd.agent_readiness.process_guardrail_refresh_candidate_packet import (
    build_process_guardrail_refresh_candidate_packet,
    validate_process_guardrail_refresh_candidate_packet,
)

FIXTURES = Path(__file__).parent / "fixtures" / "process_guardrail_refresh_candidate"


class ProcessGuardrailRefreshCandidatePacketTest(unittest.TestCase):
    def _source_packets(self) -> dict:
        with (FIXTURES / "source_packets.json").open(encoding="utf-8") as handle:
            return json.load(handle)

    def _packet(self) -> dict:
        packets = self._source_packets()
        return build_process_guardrail_refresh_candidate_packet(
            packets["requirement_rerun_result_intake_packet"],
            packets["process_model_impact_review_packet"],
            packets["guardrail_bundle_update_candidate_packet"],
        )

    def test_builds_fixture_first_process_guardrail_refresh_candidate(self) -> None:
        packet = self._packet()

        self.assertEqual(packet["packet_type"], "ppd.process_guardrail_refresh_candidate_packet.v1")
        self.assertTrue(packet["fixture_only"])
        self.assertEqual(packet["candidate_status"], "candidate_deltas_not_applied")
        self.assertEqual(
            packet["source_packet_ids"],
            {
                "requirement_rerun_result_intake_packet": "result-intake-for-work-order-20260529-fixture-rerun-001",
                "process_model_impact_review_packet": "impact-review-valid-001",
                "guardrail_bundle_update_candidate_packet": "guardrail-bundle-update-candidate-fixture-001",
            },
        )
        self.assertGreaterEqual(len(packet["candidate_process_deltas"]), 2)
        self.assertGreaterEqual(len(packet["candidate_guardrail_deltas"]), 3)
        self.assertTrue(all(delta["source_evidence_ids"] for delta in packet["candidate_process_deltas"]))
        self.assertTrue(all(delta["source_evidence_ids"] for delta in packet["candidate_guardrail_deltas"]))
        self.assertTrue(all(delta["affected_process_ids"] for delta in packet["candidate_process_deltas"]))
        self.assertTrue(all(delta["affected_guardrail_ids"] for delta in packet["candidate_guardrail_deltas"]))
        self.assertTrue(all(delta["activation_allowed"] is False for delta in packet["candidate_process_deltas"]))
        self.assertTrue(all(delta["activation_allowed"] is False for delta in packet["candidate_guardrail_deltas"]))

    def test_includes_rollback_reviewer_validation_and_no_mutation_attestations(self) -> None:
        packet = self._packet()

        self.assertTrue(packet["rollback_notes"])
        self.assertTrue(packet["reviewer_owner_fields"])
        self.assertIn(["python3", "ppd/daemon/ppd_daemon.py", "--self-test"], packet["expected_offline_validation_commands"])
        owners = {owner["reviewer_owner_id"] for owner in packet["reviewer_owner_fields"]}
        self.assertEqual(owners, {"ppd-guardrail-reviewer", "ppd-process-reviewer", "ppd-requirements-reviewer"})
        attestations = packet["attestations"]
        self.assertTrue(attestations["no_active_process_mutation"])
        self.assertTrue(attestations["no_active_guardrail_mutation"])
        self.assertTrue(attestations["no_active_prompt_mutation"])
        self.assertTrue(attestations["no_active_surface_registry_mutation"])
        self.assertTrue(attestations["no_active_monitoring_mutation"])
        self.assertTrue(attestations["no_release_state_mutation"])
        self.assertFalse(attestations["active_process_mutation"])
        self.assertFalse(attestations["active_guardrail_mutation"])
        self.assertFalse(attestations["active_prompt_mutation"])
        self.assertFalse(attestations["active_surface_registry_mutation"])
        self.assertFalse(attestations["active_monitoring_mutation"])
        self.assertFalse(attestations["release_state_mutation"])

    def test_validation_accepts_valid_packet_and_rejects_uncited_or_mutating_packet(self) -> None:
        packet = self._packet()
        self.assertTrue(validate_process_guardrail_refresh_candidate_packet(packet).valid)

        packet["candidate_process_deltas"][0]["source_evidence_ids"] = []
        packet["attestations"]["active_process_mutation"] = True
        result = validate_process_guardrail_refresh_candidate_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("candidate_process_deltas[0] lacks source_evidence_ids", result.problems)
        self.assertIn("attestations.active_process_mutation must be false", result.problems)
        self.assertIn("attestations.active_process_mutation must not set active mutation flags", result.problems)

    def test_validation_rejects_missing_affected_ids_and_review_controls(self) -> None:
        packet = self._packet()
        packet["candidate_process_deltas"][0]["affected_process_ids"] = []
        packet["candidate_guardrail_deltas"][0]["affected_guardrail_ids"] = []
        packet["rollback_notes"] = []
        packet["reviewer_owner_fields"] = []
        packet["expected_offline_validation_commands"] = []

        result = validate_process_guardrail_refresh_candidate_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("candidate_process_deltas[0] lacks affected_process_ids", result.problems)
        self.assertIn("candidate_guardrail_deltas[0] lacks affected_guardrail_ids", result.problems)
        self.assertIn("rollback_notes must be a non-empty list", result.problems)
        self.assertIn("reviewer_owner_fields must be a non-empty list", result.problems)
        self.assertIn("expected_offline_validation_commands must be a non-empty list", result.problems)

    def test_validation_rejects_private_artifacts_live_claims_guarantees_and_new_mutation_flags(self) -> None:
        packet = self._packet()
        packet["private_case_facts"] = {"address": "redacted fixture should not be here"}
        packet["candidate_process_deltas"][0]["raw_body_ref"] = "archive://raw/body.warc.gz"
        packet["candidate_process_deltas"][0]["summary"] = "A live extraction executed and guarantees approval."
        packet["attestations"]["active_surface_registry_mutation"] = True
        packet["attestations"]["active_monitoring_mutation"] = True
        packet["nested"] = {"mutation_flags": {"surface_registry": True, "monitoring": True}}

        result = validate_process_guardrail_refresh_candidate_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("private_case_facts must not include private case facts", result.problems)
        self.assertIn("candidate_process_deltas[0].raw_body_ref must not reference raw body, download, archive, WARC, or local artifacts", result.problems)
        self.assertIn("candidate_process_deltas[0].summary must not claim live extraction or processor execution", result.problems)
        self.assertIn("candidate_process_deltas[0].summary must not guarantee legal or permitting outcomes", result.problems)
        self.assertIn("attestations.active_surface_registry_mutation must be false", result.problems)
        self.assertIn("attestations.active_monitoring_mutation must be false", result.problems)
        self.assertIn("nested.mutation_flags.surface_registry must be false", result.problems)
        self.assertIn("nested.mutation_flags.monitoring must be false", result.problems)

    def test_validation_rejects_private_classification_raw_downloads_processor_claims_and_release_flags(self) -> None:
        packet = copy.deepcopy(self._packet())
        packet["candidate_guardrail_deltas"][0]["evidence"] = {
            "privacy_classification": "case_private",
            "download_url": "https://example.invalid/downloads/private.pdf",
            "note": "Ran processor execution and permit will issue.",
        }
        packet["attestations"]["release_state_mutation"] = True

        result = validate_process_guardrail_refresh_candidate_packet(packet)

        self.assertFalse(result.valid)
        self.assertIn("candidate_guardrail_deltas[0].evidence must not include private case facts", result.problems)
        self.assertIn("candidate_guardrail_deltas[0].evidence.download_url must not reference raw body, download, archive, WARC, or local artifacts", result.problems)
        self.assertIn("candidate_guardrail_deltas[0].evidence.note must not claim live extraction or processor execution", result.problems)
        self.assertIn("candidate_guardrail_deltas[0].evidence.note must not guarantee legal or permitting outcomes", result.problems)
        self.assertIn("attestations.release_state_mutation must be false", result.problems)


if __name__ == "__main__":
    unittest.main()
