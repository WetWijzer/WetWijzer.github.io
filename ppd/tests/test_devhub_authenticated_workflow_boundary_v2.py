from __future__ import annotations

import unittest

from ppd.devhub.authenticated_workflow_boundary_v2 import (
    PACKET_VERSION,
    validate_boundary_packet_v2,
)


def valid_packet() -> dict:
    return {
        "version": PACKET_VERSION,
        "surfaces": [
            {
                "surface_id": "devhub-home-readonly",
                "category": "safe_read_only",
                "requires_attendance": True,
                "requires_exact_confirmation": False,
                "redaction_expectations": ["Do not persist private page values."],
                "abort_conditions": ["Abort if MFA, CAPTCHA, payment, upload, certify, submit, or schedule prompts appear."],
                "reviewer_placeholder": "human-devhub-reviewer",
            }
        ],
        "actions": [
            {
                "action_id": "review-visible-status",
                "classification": "read_only",
                "requires_attendance": True,
                "requires_exact_confirmation": False,
                "redaction_expectations": ["Record only normalized labels and source-neutral status categories."],
                "abort_conditions": ["Abort before changing any account, permit, upload, payment, or inspection state."],
                "reviewer_placeholder": "human-devhub-reviewer",
            }
        ],
        "artifacts": [
            {"kind": "redacted_surface_manifest", "ref": "fixture-only"},
        ],
        "claims": ["Fixture packet validates guardrail shape only."],
        "mutation_flags": [
            {"name": "active_devhub_surface_mutation", "active": False},
            {"name": "active_devhub_prompt_mutation", "active": False},
            {"name": "active_devhub_guardrail_mutation", "active": False},
            {"name": "active_devhub_contract_mutation", "active": False},
            {"name": "active_devhub_process_model_mutation", "active": False},
            {"name": "active_devhub_source_mutation", "active": False},
            {"name": "active_devhub_release_state_mutation", "active": False},
        ],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
    }


class DevHubAuthenticatedWorkflowBoundaryV2Test(unittest.TestCase):
    def test_accepts_commit_safe_packet(self) -> None:
        result = validate_boundary_packet_v2(valid_packet())
        self.assertTrue(result.ok, result.errors)

    def test_rejects_missing_required_top_level_sections(self) -> None:
        packet = valid_packet()
        del packet["surfaces"]
        del packet["actions"]
        del packet["validation_commands"]

        result = validate_boundary_packet_v2(packet)

        self.assertFalse(result.ok)
        self.assertIn("surfaces must be a non-empty sequence", result.errors)
        self.assertIn("actions must be a non-empty sequence", result.errors)
        self.assertIn("validation_commands must be a non-empty sequence", result.errors)

    def test_rejects_missing_surface_boundary_fields(self) -> None:
        packet = valid_packet()
        packet["surfaces"] = [{"surface_id": "incomplete"}]

        result = validate_boundary_packet_v2(packet)

        self.assertFalse(result.ok)
        self.assertIn("surfaces[0].category must be one of ['consequential_official', 'reversible_draft', 'safe_read_only', 'unsupported']", result.errors)
        self.assertIn("surfaces[0].requires_attendance must be a boolean", result.errors)
        self.assertIn("surfaces[0].requires_exact_confirmation must be a boolean", result.errors)
        self.assertIn("surfaces[0].redaction_expectations must be a non-empty sequence", result.errors)
        self.assertIn("surfaces[0].abort_conditions must be a non-empty sequence", result.errors)
        self.assertIn("surfaces[0].reviewer_placeholder must be a non-empty string", result.errors)

    def test_rejects_missing_action_boundary_fields(self) -> None:
        packet = valid_packet()
        packet["actions"] = [{"action_id": "incomplete"}]

        result = validate_boundary_packet_v2(packet)

        self.assertFalse(result.ok)
        self.assertIn("actions[0].classification must be one of ['exact_confirmation_required', 'manual_handoff_required', 'read_only', 'refused', 'reversible_draft']", result.errors)
        self.assertIn("actions[0].requires_attendance must be a boolean", result.errors)
        self.assertIn("actions[0].requires_exact_confirmation must be a boolean", result.errors)
        self.assertIn("actions[0].redaction_expectations must be a non-empty sequence", result.errors)
        self.assertIn("actions[0].abort_conditions must be a non-empty sequence", result.errors)
        self.assertIn("actions[0].reviewer_placeholder must be a non-empty string", result.errors)

    def test_rejects_private_session_browser_and_capture_artifacts(self) -> None:
        prohibited_kinds = [
            "session",
            "auth_state",
            "browser_context",
            "screenshot",
            "trace",
            "har",
        ]
        for kind in prohibited_kinds:
            with self.subTest(kind=kind):
                packet = valid_packet()
                packet["artifacts"] = [{"kind": kind, "path": f"tmp/{kind}.json"}]

                result = validate_boundary_packet_v2(packet)

                self.assertFalse(result.ok)
                self.assertTrue(any("prohibited" in error for error in result.errors), result.errors)

    def test_rejects_private_material_by_key_or_reference(self) -> None:
        packet = valid_packet()
        packet["session_cookie"] = "redacted"
        packet["notes"] = ["playwright trace.zip was captured"]

        result = validate_boundary_packet_v2(packet)

        self.assertFalse(result.ok)
        self.assertTrue(any("session_cookie" in error for error in result.errors), result.errors)
        self.assertTrue(any("trace.zip" in error or "references prohibited" in error for error in result.errors), result.errors)

    def test_rejects_live_authenticated_official_legal_and_permitting_claims(self) -> None:
        prohibited_claims = [
            "Live authenticated claim: the permit approved status is final.",
            "Application submitted to the city.",
            "Inspection scheduled successfully.",
            "This is legal advice and guarantees approval.",
        ]
        for claim in prohibited_claims:
            with self.subTest(claim=claim):
                packet = valid_packet()
                packet["claims"] = [claim]

                result = validate_boundary_packet_v2(packet)

                self.assertFalse(result.ok)
                self.assertTrue(any("claim" in error for error in result.errors), result.errors)

    def test_rejects_active_devhub_mutation_flags(self) -> None:
        prohibited_flags = [
            "active_devhub_surface_mutation",
            "active_devhub_prompt_mutation",
            "active_devhub_guardrail_mutation",
            "active_devhub_contract_mutation",
            "active_devhub_process_model_mutation",
            "active_devhub_source_mutation",
            "active_devhub_release_state_mutation",
        ]
        for flag in prohibited_flags:
            with self.subTest(flag=flag):
                packet = valid_packet()
                packet["mutation_flags"] = [{"name": flag, "active": True}]

                result = validate_boundary_packet_v2(packet)

                self.assertFalse(result.ok)
                self.assertTrue(any("mutation" in error for error in result.errors), result.errors)

    def test_rejects_boolean_top_level_mutation_flags(self) -> None:
        packet = valid_packet()
        packet["active_devhub_guardrail_mutation"] = True

        result = validate_boundary_packet_v2(packet)

        self.assertFalse(result.ok)
        self.assertIn("active_devhub_guardrail_mutation prohibits active DevHub mutation flag", result.errors)


if __name__ == "__main__":
    unittest.main()
