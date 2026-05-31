from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from ppd.agent_readiness.inactive_guardrail_bundle_promotion_candidate_v2 import (
    OFFLINE_VALIDATION_COMMANDS,
    VALIDATION_COMMANDS,
    load_inactive_guardrail_bundle_promotion_candidate_v2,
    validate_inactive_guardrail_bundle_promotion_candidate_v2,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "inactive_guardrail_bundle_promotion_candidate_v2" / "valid_packet.json"


class InactiveGuardrailBundlePromotionCandidateV2Tests(unittest.TestCase):
    def test_valid_fixture_loads(self) -> None:
        packet = load_inactive_guardrail_bundle_promotion_candidate_v2(FIXTURE_PATH)
        result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

        self.assertTrue(result.valid, result.problems)
        self.assertEqual(packet["packet_type"], "ppd.inactive_guardrail_bundle_promotion_candidate.v2")
        self.assertEqual(packet["offline_validation_commands"], OFFLINE_VALIDATION_COMMANDS)
        self.assertEqual(packet["validation_commands"], VALIDATION_COMMANDS)
        self.assertEqual([row["sequence"] for row in packet["inactive_bundle_candidate_records"]], [1, 2])
        self.assertTrue(all(row["candidate_status"] == "inactive_candidate_only" for row in packet["inactive_bundle_candidate_records"]))
        self.assertTrue(all(row["activation_allowed"] is False for row in packet["release_gate_prerequisites"]))

    def test_rejects_missing_required_candidate_sections(self) -> None:
        for key in (
            "inactive_bundle_candidate_records",
            "source_evidence_trace_placeholders",
            "predicate_snapshot_placeholders",
            "rollback_references",
            "reviewer_approval_placeholders",
            "release_gate_prerequisites",
            "validation_commands",
        ):
            packet = self._valid_packet()
            packet.pop(key)

            result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

            self.assertFalse(result.valid, key)
            self.assertIn(f"{key} must be a non-empty list", result.problems)

    def test_rejects_unapproved_recompile_reviewer_rows(self) -> None:
        packet = self._valid_packet()
        packet["approved_recompile_reviewer_rows"][0]["reviewer_disposition"] = "pending_review"

        result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

        self.assertFalse(result.valid)
        self.assertIn(
            "approved_recompile_reviewer_rows[0].reviewer_disposition must approve inactive bundle candidacy",
            result.problems,
        )

    def test_rejects_unordered_or_active_candidate_records(self) -> None:
        packet = self._valid_packet()
        packet["inactive_bundle_candidate_records"][0]["sequence"] = 2
        packet["inactive_bundle_candidate_records"][0]["candidate_status"] = "active"
        packet["inactive_bundle_candidate_records"][0]["replaces_active_guardrail"] = True
        packet["inactive_bundle_candidate_records"][0]["activation_allowed"] = True

        result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

        self.assertFalse(result.valid)
        self.assertIn("inactive_bundle_candidate_records[0].sequence must be 1", result.problems)
        self.assertIn("inactive_bundle_candidate_records[0].candidate_status must remain inactive_candidate_only", result.problems)
        self.assertIn("inactive_bundle_candidate_records[0].replaces_active_guardrail must be false when an active bundle is referenced", result.problems)
        self.assertIn("inactive_bundle_candidate_records[0].activation_allowed must be false", result.problems)

    def test_rejects_missing_candidate_cross_references(self) -> None:
        packet = self._valid_packet()
        row = packet["inactive_bundle_candidate_records"][0]
        row["source_reviewer_row_ref"] = "missing-review-row"
        row["source_evidence_trace_placeholder_refs"] = ["missing-trace-placeholder"]
        row["predicate_snapshot_placeholder_refs"] = ["missing-predicate-snapshot"]
        row["rollback_ref"] = "missing-rollback"
        row["reviewer_approval_placeholder_ref"] = "missing-approval"
        row["release_gate_prerequisite_ref"] = "missing-gate"

        result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

        self.assertFalse(result.valid)
        self.assertIn("inactive_bundle_candidate_records[0].source_reviewer_row_ref must reference approved_recompile_reviewer_rows", result.problems)
        self.assertIn("inactive_bundle_candidate_records[0].source_evidence_trace_placeholder_refs must reference source_evidence_trace_placeholders", result.problems)
        self.assertIn("inactive_bundle_candidate_records[0].predicate_snapshot_placeholder_refs must reference predicate_snapshot_placeholders", result.problems)
        self.assertIn("inactive_bundle_candidate_records[0].rollback_ref must reference rollback_references", result.problems)
        self.assertIn("inactive_bundle_candidate_records[0].reviewer_approval_placeholder_ref must reference reviewer_approval_placeholders", result.problems)
        self.assertIn("inactive_bundle_candidate_records[0].release_gate_prerequisite_ref must reference release_gate_prerequisites", result.problems)

    def test_rejects_orphan_prerequisite_candidate_references(self) -> None:
        packet = self._valid_packet()
        packet["source_evidence_trace_placeholders"][0]["candidate_id"] = "missing-candidate"
        packet["predicate_snapshot_placeholders"][0]["candidate_id"] = "missing-candidate"
        packet["rollback_references"][0]["candidate_id"] = "missing-candidate"
        packet["reviewer_approval_placeholders"][0]["candidate_id"] = "missing-candidate"
        packet["release_gate_prerequisites"][0]["candidate_id"] = "missing-candidate"

        result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

        self.assertFalse(result.valid)
        self.assertIn("source_evidence_trace_placeholders[0].candidate_id must reference inactive_bundle_candidate_records", result.problems)
        self.assertIn("predicate_snapshot_placeholders[0].candidate_id must reference inactive_bundle_candidate_records", result.problems)
        self.assertIn("rollback_references[0].candidate_id must reference inactive_bundle_candidate_records", result.problems)
        self.assertIn("reviewer_approval_placeholders[0].candidate_id must reference inactive_bundle_candidate_records", result.problems)
        self.assertIn("release_gate_prerequisites[0].candidate_id must reference inactive_bundle_candidate_records", result.problems)

    def test_rejects_non_placeholder_review_and_release_activation(self) -> None:
        packet = self._valid_packet()
        packet["reviewer_approval_placeholders"][0]["approval_status"] = "approved"
        packet["reviewer_approval_placeholders"][0]["reviewer"] = "reviewer-name"
        packet["reviewer_approval_placeholders"][0]["reviewed_at"] = "2026-05-31T00:00:00Z"
        packet["release_gate_prerequisites"][0]["gate_status"] = "approved"
        packet["release_gate_prerequisites"][0]["activation_allowed"] = True
        packet["release_gate_prerequisites"][0]["requires_rollback_review"] = False
        packet["release_gate_prerequisites"][0]["requires_no_active_guardrail_replacement"] = False

        result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

        self.assertFalse(result.valid)
        self.assertIn("reviewer_approval_placeholders[0].approval_status must be pending_manual_review", result.problems)
        self.assertIn("reviewer_approval_placeholders[0].reviewer must be blank until manual review", result.problems)
        self.assertIn("reviewer_approval_placeholders[0].reviewed_at must be blank until manual review", result.problems)
        self.assertIn("release_gate_prerequisites[0].gate_status must be blocked_pending_manual_release_review", result.problems)
        self.assertIn("release_gate_prerequisites[0].activation_allowed must be false", result.problems)
        self.assertIn("release_gate_prerequisites[0].requires_rollback_review must be true", result.problems)
        self.assertIn("release_gate_prerequisites[0].requires_no_active_guardrail_replacement must be true", result.problems)

    def test_rejects_changed_validation_commands(self) -> None:
        packet = self._valid_packet()
        packet["offline_validation_commands"] = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
        packet["validation_commands"] = [["python3", "-m", "pytest"]]

        result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

        self.assertFalse(result.valid)
        self.assertIn(
            "offline_validation_commands must exactly match the inactive candidate offline validation command bundle",
            result.problems,
        )
        self.assertIn("validation_commands must contain the PP&D daemon self-test command", result.problems)

    def test_rejects_private_live_raw_outcome_and_consequential_payloads(self) -> None:
        forbidden_examples = (
            ("auth_state", {"cookies": ["not-committable"]}),
            ("browser_artifact", {"path": "artifact.zip"}),
            ("downloaded_artifact", "downloaded document saved"),
            ("status_note", "opened DevHub and performed live crawl"),
            ("devhub_claim", "DevHub observed during live source run"),
            ("artifact_note", "raw pdf stored in /tmp/private/file.pdf"),
            ("outcome_note", "permit will be approved"),
            ("legal_note", "legally compliant legal guarantee"),
            ("action_note", "agent will submit permit"),
        )
        for key, value in forbidden_examples:
            packet = self._valid_packet()
            packet[key] = value

            result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

            self.assertFalse(result.valid, key)

    def test_rejects_active_mutation_flags(self) -> None:
        for key in (
            "active_source_mutation",
            "active_requirement_mutation",
            "active_process_model_mutation",
            "active_process_mutation",
            "active_guardrail_replaced",
            "active_guardrail_mutation",
            "active_prompt_mutation",
            "active_contract_mutation",
            "active_devhub_surface_mutation",
            "active_surface_mutation",
            "active_release_state_mutation",
            "source_mutation",
            "requirement_mutation",
            "process_model_mutation",
            "process_mutation",
            "guardrail_mutation",
            "prompt_mutation",
            "contract_mutation",
            "devhub_surface_mutation",
            "surface_mutation",
            "devhub_opened",
            "live_source_crawl",
            "release_state_activated",
            "release_state_mutation",
            "promotion_executed",
        ):
            packet = self._valid_packet()
            packet[key] = True

            result = validate_inactive_guardrail_bundle_promotion_candidate_v2(packet)

            self.assertFalse(result.valid, key)
            self.assertTrue(any(key in problem for problem in result.problems), result.problems)

    def _valid_packet(self) -> dict[str, object]:
        return copy.deepcopy(json.loads(FIXTURE_PATH.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
