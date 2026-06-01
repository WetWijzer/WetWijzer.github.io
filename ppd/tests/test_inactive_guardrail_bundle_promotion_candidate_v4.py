from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from ppd.agent_readiness.inactive_guardrail_bundle_promotion_candidate_v4 import (
    OFFLINE_VALIDATION_COMMANDS,
    VALIDATION_COMMANDS,
    load_inactive_guardrail_bundle_promotion_candidate_v4,
    validate_inactive_guardrail_bundle_promotion_candidate_v4,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "inactive_guardrail_bundle_promotion_candidate_v4" / "valid_packet.json"


class InactiveGuardrailBundlePromotionCandidateV4Tests(unittest.TestCase):
    def test_valid_fixture_loads(self) -> None:
        packet = load_inactive_guardrail_bundle_promotion_candidate_v4(FIXTURE_PATH)
        result = validate_inactive_guardrail_bundle_promotion_candidate_v4(packet)

        self.assertTrue(result.valid, result.problems)
        self.assertEqual(packet["packet_type"], "ppd.inactive_guardrail_promotion_candidate.v4")
        self.assertEqual(packet["offline_validation_commands"], OFFLINE_VALIDATION_COMMANDS)
        self.assertEqual(packet["validation_commands"], VALIDATION_COMMANDS)
        self.assertTrue(all(row["candidate_status"] == "inactive_candidate_only" for row in packet["inactive_promotion_rows"]))

    def test_rejects_missing_required_sections(self) -> None:
        for key in (
            "readiness_replay_references",
            "prior_guardrail_placeholder_fixtures",
            "inactive_promotion_rows",
            "activation_prerequisites",
            "stale_source_holds",
            "reviewer_signoff_placeholders",
            "rollback_plan",
            "post_promotion_smoke_checks",
            "offline_validation_commands",
            "validation_commands",
        ):
            packet = self._valid_packet()
            packet.pop(key)

            result = validate_inactive_guardrail_bundle_promotion_candidate_v4(packet)

            self.assertFalse(result.valid, key)
            self.assertIn(f"{key} must be a non-empty list", result.problems)

    def test_rejects_missing_candidate_row_references(self) -> None:
        packet = self._valid_packet()
        row = packet["inactive_promotion_rows"][0]
        for key in (
            "readiness_replay_ref",
            "prior_guardrail_placeholder_fixture_ref",
            "activation_prerequisite_ref",
            "stale_source_hold_ref",
            "reviewer_signoff_placeholder_ref",
            "rollback_plan_ref",
            "post_promotion_smoke_check_ref",
        ):
            row[key] = ""

        result = validate_inactive_guardrail_bundle_promotion_candidate_v4(packet)

        self.assertFalse(result.valid)
        self.assertIn("inactive_promotion_rows[0].readiness_replay_ref is required", result.problems)
        self.assertIn("inactive_promotion_rows[0].prior_guardrail_placeholder_fixture_ref is required", result.problems)
        self.assertIn("inactive_promotion_rows[0].activation_prerequisite_ref is required", result.problems)
        self.assertIn("inactive_promotion_rows[0].stale_source_hold_ref is required", result.problems)
        self.assertIn("inactive_promotion_rows[0].reviewer_signoff_placeholder_ref is required", result.problems)
        self.assertIn("inactive_promotion_rows[0].rollback_plan_ref is required", result.problems)
        self.assertIn("inactive_promotion_rows[0].post_promotion_smoke_check_ref is required", result.problems)

    def test_rejects_missing_activation_prerequisites_and_hold_states(self) -> None:
        packet = self._valid_packet()
        prereq = packet["activation_prerequisites"][0]
        prereq["requires_readiness_replay"] = False
        prereq["requires_prior_placeholder_fixture"] = False
        prereq["requires_stale_source_hold_review"] = False
        prereq["requires_reviewer_signoff"] = False
        prereq["requires_rollback_plan"] = False
        prereq["requires_post_promotion_smoke"] = False
        prereq["requires_validation_commands"] = False
        prereq["activation_allowed"] = True
        packet["stale_source_holds"][0]["hold_status"] = "cleared"
        packet["stale_source_holds"][0]["promotion_blocked"] = False

        result = validate_inactive_guardrail_bundle_promotion_candidate_v4(packet)

        self.assertFalse(result.valid)
        self.assertIn("activation_prerequisites[0].requires_readiness_replay must be true", result.problems)
        self.assertIn("activation_prerequisites[0].requires_validation_commands must be true", result.problems)
        self.assertIn("activation_prerequisites[0].activation_allowed must be false", result.problems)
        self.assertIn("stale_source_holds[0].hold_status must be held_pending_public_source_freshness_review", result.problems)
        self.assertIn("stale_source_holds[0].promotion_blocked must be true", result.problems)

    def test_rejects_signoff_rollback_smoke_and_validation_command_claims(self) -> None:
        packet = self._valid_packet()
        packet["reviewer_signoff_placeholders"][0]["signoff_status"] = "approved"
        packet["reviewer_signoff_placeholders"][0]["reviewer"] = "reviewer"
        packet["reviewer_signoff_placeholders"][0]["signed_at"] = "2026-06-01T00:00:00Z"
        packet["rollback_plan"][0]["rollback_target"] = "mutate_active_guardrail"
        packet["rollback_plan"][0]["active_state_changed"] = True
        packet["post_promotion_smoke_checks"][0]["smoke_status"] = "passed"
        packet["post_promotion_smoke_checks"][0]["requires_separate_post_promotion_task"] = False
        packet["validation_commands"] = [["python3", "-m", "pytest"]]

        result = validate_inactive_guardrail_bundle_promotion_candidate_v4(packet)

        self.assertFalse(result.valid)
        self.assertIn("reviewer_signoff_placeholders[0].signoff_status must be pending_manual_review", result.problems)
        self.assertIn("reviewer_signoff_placeholders[0].reviewer must be blank until manual review", result.problems)
        self.assertIn("rollback_plan[0].rollback_target must be discard_inactive_candidate_only", result.problems)
        self.assertIn("rollback_plan[0].active_state_changed must be false", result.problems)
        self.assertIn("post_promotion_smoke_checks[0].smoke_status must be planned_not_run_for_inactive_candidate", result.problems)
        self.assertIn("validation_commands must contain the PP&D daemon self-test command", result.problems)

    def test_rejects_active_mutation_flags_private_artifacts_official_claims_and_guarantees(self) -> None:
        forbidden_examples = (
            ("active_guardrail_mutation", True),
            ("active_guardrail_bundle_mutation", True),
            ("active_mutation", True),
            ("guardrails_changed", True),
            ("auth_state", {"cookies": ["not-committable"]}),
            ("private_session_artifact", "session state saved"),
            ("trace_file", "trace.zip"),
            ("raw_download", "raw pdf stored in /tmp/private/file.pdf"),
            ("mutation_claim", "active guardrail was mutated"),
            ("official_claim", "official action completed and submitted permit"),
            ("legal_claim", "legally compliant legal guarantee"),
            ("permit_claim", "permit will be approved"),
        )
        for key, value in forbidden_examples:
            packet = self._valid_packet()
            packet[key] = value

            result = validate_inactive_guardrail_bundle_promotion_candidate_v4(packet)

            self.assertFalse(result.valid, key)

    def _valid_packet(self) -> dict[str, object]:
        return copy.deepcopy(json.loads(FIXTURE_PATH.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
