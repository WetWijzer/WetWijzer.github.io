from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from ppd.agent_readiness.devhub_read_only_observation_renewal_authorization_packet_v1 import (
    validate_devhub_read_only_observation_renewal_authorization_packet_v1,
)


_FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub_read_only_observation_renewal_authorization_packet_v1.json"
)


def valid_packet() -> dict:
    return json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))


class DevHubReadOnlyObservationRenewalAuthorizationPacketV1Test(unittest.TestCase):
    def assert_rejects(self, packet: dict, expected_code: str) -> None:
        issues = validate_devhub_read_only_observation_renewal_authorization_packet_v1(packet)
        self.assertTrue(issues, "packet unexpectedly validated")
        self.assertTrue(any(issue.code == expected_code for issue in issues), [issue.as_dict() for issue in issues])

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], validate_devhub_read_only_observation_renewal_authorization_packet_v1(valid_packet()))

    def test_rejects_missing_required_sections(self) -> None:
        expected = {
            "attendance_prerequisites": "missing_attendance_prerequisites",
            "allowed_read_only_surfaces": "missing_allowed_read_only_surfaces",
            "redaction_requirements": "missing_redaction_requirements",
            "stop_conditions": "missing_stop_conditions",
            "manual_handoff_points": "missing_manual_handoff_points",
            "observation_evidence_placeholders": "missing_observation_evidence_placeholders",
            "validation_commands": "missing_validation_commands",
        }
        for key, code in expected.items():
            packet = valid_packet()
            packet[key] = []
            self.assert_rejects(packet, code)

    def test_rejects_missing_authorization_row_references(self) -> None:
        expected = {
            "attendance_prerequisite_id": "missing_attendance_prerequisite_id",
            "surface_id": "missing_surface_id",
            "redaction_requirement_id": "missing_redaction_requirement_id",
            "stop_condition_id": "missing_stop_condition_id",
            "manual_handoff_point_id": "missing_manual_handoff_point_id",
            "evidence_placeholder_id": "missing_evidence_placeholder_id",
        }
        for key, code in expected.items():
            packet = valid_packet()
            packet["authorization_rows"][0][key] = ""
            self.assert_rejects(packet, code)

    def test_rejects_unknown_authorization_row_references(self) -> None:
        packet = valid_packet()
        packet["authorization_rows"][0]["surface_id"] = "missing-surface"
        self.assert_rejects(packet, "unknown_surface_id")

    def test_rejects_non_read_only_surfaces(self) -> None:
        packet = valid_packet()
        packet["allowed_read_only_surfaces"][0]["classification"] = "reversible_draft"
        self.assert_rejects(packet, "surface_not_read_only")

    def test_rejects_surfaces_without_attendance_or_with_mutation(self) -> None:
        packet = valid_packet()
        packet["allowed_read_only_surfaces"][0]["requires_attendance"] = False
        self.assert_rejects(packet, "surface_missing_attendance_requirement")

        packet = valid_packet()
        packet["allowed_read_only_surfaces"][0]["allows_mutation"] = True
        self.assert_rejects(packet, "surface_allows_mutation")

    def test_rejects_artifact_policy_flags(self) -> None:
        for key in valid_packet()["artifact_policy"]:
            packet = valid_packet()
            packet["artifact_policy"][key] = True
            self.assert_rejects(packet, "artifact_policy_not_false")

    def test_rejects_credentials_session_browser_screenshot_trace_har_and_private_artifacts(self) -> None:
        cases = (
            ("stored credential token", "private_or_session_artifact_language"),
            ("kept DevHub session state", "private_or_session_artifact_language"),
            ("captured auth state and browser profile", "private_or_session_artifact_language"),
            ("recorded private page value", "private_or_session_artifact_language"),
            ("saved screenshot.png with network trace.har", "browser_capture_artifact_language"),
        )
        for text, code in cases:
            packet = valid_packet()
            packet["operator_notes"] = text
            self.assert_rejects(packet, code)

    def test_rejects_devhub_login_automation_claims(self) -> None:
        for phrase in ("automated login", "entered password", "logged into DevHub", "programmatic login"):
            packet = valid_packet()
            packet["operator_notes"] = phrase
            self.assert_rejects(packet, "devhub_login_automation_claim")

    def test_rejects_official_action_completion_claims(self) -> None:
        for phrase in ("official action completed", "permit submitted", "payment completed", "scheduled inspection"):
            packet = valid_packet()
            packet["operator_notes"] = phrase
            self.assert_rejects(packet, "official_action_completion_claim")

    def test_rejects_consequential_action_claims_outside_stop_and_handoff_safeguards(self) -> None:
        for phrase in ("submit permit", "make payment", "upload document", "schedule inspection", "certification"):
            packet = valid_packet()
            packet["authorization_rows"][0]["renewal_reason"] = f"Authorization claims it can {phrase}."
            self.assert_rejects(packet, "consequential_action_claim")

    def test_rejects_unsafe_validation_commands(self) -> None:
        packet = valid_packet()
        packet["validation_commands"] = [["python3", "run_live_devhub_login.py"]]
        self.assert_rejects(packet, "unsafe_validation_command")

    def test_rejects_active_mutation_flags(self) -> None:
        for flag in (
            "active_surface_mutation",
            "active_guardrail_mutation",
            "active_prompt_mutation",
            "active_release_state_mutation",
            "active_agent_state_mutation",
            "active_authorization_mutation",
        ):
            packet = deepcopy(valid_packet())
            packet["mutation_flags"][flag] = True
            self.assert_rejects(packet, "active_mutation_flag")


if __name__ == "__main__":
    unittest.main()
