from __future__ import annotations

from copy import deepcopy
import unittest

from ppd.devhub_readonly_observation_rehearsal_v1_validation import (
    ObservationRehearsalValidationError,
    assert_valid_devhub_readonly_observation_rehearsal_v1,
    validate_devhub_readonly_observation_rehearsal_v1,
)


CITATION = "https://www.portland.gov/ppd/devhub-faqs"


def valid_packet() -> dict:
    redaction_requirements = []
    for requirement_id in (
        "no_private_account_values",
        "no_session_files",
        "no_screenshots",
        "no_traces",
        "no_har_artifacts",
        "redact_visible_identifiers",
    ):
        redaction_requirements.append(
            {
                "requirement_id": requirement_id,
                "required": True,
                "enforced": True,
                "allows_private_values": False,
                "allows_artifacts": False,
                "citations": [CITATION],
            }
        )

    attendance_checkpoints = []
    for checkpoint_id in (
        "operator_present_before_observation",
        "read_only_scope_review",
        "manual_handoff_on_consequential_control",
        "user_visible_completion_review",
    ):
        attendance_checkpoints.append(
            {
                "checkpoint_id": checkpoint_id,
                "requires_user_attendance": True,
                "write_action_allowed": False,
                "citations": [CITATION],
            }
        )

    return {
        "packet_version": "devhub-readonly-observation-rehearsal-v1",
        "ui_observations": [
            {
                "surface_id": "devhub-home-readonly-fixture",
                "evidence_summary": "Fixture shows a redacted DevHub home heading and status label for reviewer comparison.",
                "citations": [CITATION],
            }
        ],
        "redaction_requirements": redaction_requirements,
        "attendance_checkpoints": attendance_checkpoints,
        "attestations": {
            "no_live_devhub": True,
            "no_private_values": True,
            "no_browser_artifacts": True,
            "no_official_action": True,
            "active_devhub_mutation": False,
            "active_surface_registry_mutation": False,
            "active_guardrail_mutation": False,
            "active_prompt_mutation": False,
            "active_release_state_mutation": False,
            "active_agent_state_mutation": False,
        },
    }


def violation_codes(packet: dict) -> set[str]:
    return {violation.code for violation in validate_devhub_readonly_observation_rehearsal_v1(packet)}


class DevHubReadonlyObservationRehearsalV1ValidationTest(unittest.TestCase):
    def test_valid_packet_passes(self) -> None:
        packet = valid_packet()
        self.assertEqual([], validate_devhub_readonly_observation_rehearsal_v1(packet))
        assert_valid_devhub_readonly_observation_rehearsal_v1(packet)

    def test_assert_raises_with_violation_details(self) -> None:
        packet = valid_packet()
        packet["ui_observations"][0]["citations"] = []

        with self.assertRaises(ObservationRehearsalValidationError) as caught:
            assert_valid_devhub_readonly_observation_rehearsal_v1(packet)

        self.assertEqual("uncited_ui_evidence", caught.exception.violations[0].code)

    def test_rejects_uncited_ui_evidence(self) -> None:
        packet = valid_packet()
        packet["ui_observations"][0].pop("citations")

        self.assertIn("uncited_ui_evidence", violation_codes(packet))

    def test_rejects_missing_redaction_requirements(self) -> None:
        packet = valid_packet()
        packet["redaction_requirements"] = packet["redaction_requirements"][:-1]

        self.assertIn("missing_redaction_requirement", violation_codes(packet))

    def test_rejects_missing_attendance_checkpoints(self) -> None:
        packet = valid_packet()
        packet["attendance_checkpoints"] = packet["attendance_checkpoints"][:-1]

        self.assertIn("missing_attendance_checkpoint", violation_codes(packet))

    def test_rejects_private_account_values(self) -> None:
        packet = valid_packet()
        packet["ui_observations"][0]["private_account_value"] = "permit number: 24-123456-000-00-CO"

        self.assertIn("private_account_value", violation_codes(packet))

    def test_rejects_session_files_screenshots_traces_and_har_artifacts(self) -> None:
        cases = (
            ("session_file", "storage_state.json", "session_file_artifact"),
            ("screenshot_path", "devhub-home.png", "screenshot_artifact"),
            ("trace_path", "trace.zip", "trace_artifact"),
            ("har_path", "network.har", "har_artifact"),
        )

        for key, value, expected_code in cases:
            with self.subTest(key=key):
                packet = valid_packet()
                packet["ui_observations"][0][key] = value
                self.assertIn(expected_code, violation_codes(packet))

    def test_rejects_write_capable_actions(self) -> None:
        packet = valid_packet()
        packet["ui_observations"][0]["observed_actions"] = [
            {"action_class": "write_capable", "action_summary": "press a DevHub button"}
        ]

        self.assertIn("write_capable_action", violation_codes(packet))

    def test_rejects_official_action_language(self) -> None:
        prohibited_terms = (
            "certify the acknowledgement",
            "submit the application",
            "enter payment",
            "upload corrections",
            "schedule inspection",
            "cancel request",
        )

        for term in prohibited_terms:
            with self.subTest(term=term):
                packet = valid_packet()
                packet["ui_observations"][0]["evidence_summary"] = f"Fixture says to {term}."
                self.assertIn("prohibited_official_action_language", violation_codes(packet))

    def test_rejects_active_mutation_flags(self) -> None:
        mutation_keys = (
            "active_devhub_mutation",
            "active_surface_registry_mutation",
            "active_guardrail_mutation",
            "active_prompt_mutation",
            "active_release_state_mutation",
            "active_agent_state_mutation",
        )

        for key in mutation_keys:
            with self.subTest(key=key):
                packet = valid_packet()
                packet["attestations"] = deepcopy(packet["attestations"])
                packet["attestations"][key] = True
                self.assertIn("active_mutation_flag", violation_codes(packet))


if __name__ == "__main__":
    unittest.main()
