from __future__ import annotations

from copy import deepcopy
import unittest

from ppd.devhub_readonly_observation_rehearsal_v1_validation import (
    ObservationRehearsalValidationError,
    assert_valid_devhub_observation_evidence_intake_packet_v1,
    assert_valid_devhub_readonly_observation_rehearsal_v1,
    validate_devhub_observation_evidence_intake_packet_v1,
    validate_devhub_readonly_observation_rehearsal_v1,
)


CITATION = "https://www.portland.gov/ppd/devhub-faqs"


def cited_row(**values: object) -> dict:
    row = dict(values)
    row.setdefault("citations", [CITATION])
    return row


def valid_packet() -> dict:
    redaction_requirements = []
    for requirement_id in (
        "no_private_account_values",
        "no_credentials",
        "no_session_files",
        "no_browser_state",
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
        "user_visible_review",
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
        "packet_version": "devhub-observation-evidence-intake-packet-v1",
        "ui_observations": [
            {
                "surface_id": "devhub-home-readonly-fixture",
                "evidence_summary": "Fixture shows a redacted DevHub home heading and read-only status label for reviewer comparison.",
                "citations": [CITATION],
            }
        ],
        "renewal_authorization_references": [
            cited_row(renewal_authorization_reference="Renewal authorization is only a redacted observed eligibility reference.")
        ],
        "observed_heading_rows": [cited_row(observed_heading="DevHub")],
        "url_pattern_rows": [cited_row(url_pattern="https://devhub.portlandoregon.gov/*")],
        "accessible_landmark_rows": [cited_row(landmark="main")],
        "read_only_action_label_rows": [cited_row(action_label="View", read_only=True)],
        "validation_message_rows": [cited_row(validation_message="Required field message placeholder")],
        "redacted_placeholder_rows": [
            cited_row(placeholder_kind="attachment", placeholder="[redacted]"),
            cited_row(placeholder_kind="status", placeholder="[redacted]"),
            cited_row(placeholder_kind="fee", placeholder="[redacted]"),
        ],
        "stop_condition_rows": [cited_row(stop_condition="Stop before any write-capable control.", read_only=True)],
        "manual_handoff_rows": [cited_row(manual_handoff="Hand off to the present user for any consequential control.", read_only=True)],
        "validation_commands": [
            ["python3", "-m", "unittest", "discover", "-s", "ppd/tests", "-p", "test_*.py"],
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
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
        self.assertEqual([], validate_devhub_observation_evidence_intake_packet_v1(packet))
        assert_valid_devhub_readonly_observation_rehearsal_v1(packet)
        assert_valid_devhub_observation_evidence_intake_packet_v1(packet)

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

    def test_rejects_missing_required_evidence_rows(self) -> None:
        cases = (
            ("renewal_authorization_references", "missing_renewal_authorization_reference"),
            ("observed_heading_rows", "missing_observed_heading_row"),
            ("url_pattern_rows", "missing_url_pattern_row"),
            ("accessible_landmark_rows", "missing_accessible_landmark_row"),
            ("read_only_action_label_rows", "missing_read_only_action_label_row"),
            ("validation_message_rows", "missing_validation_message_row"),
            ("stop_condition_rows", "missing_stop_condition_row"),
            ("manual_handoff_rows", "missing_manual_handoff_row"),
        )

        for key, expected_code in cases:
            with self.subTest(key=key):
                packet = valid_packet()
                packet[key] = []
                self.assertIn(expected_code, violation_codes(packet))

    def test_rejects_missing_redacted_attachment_status_and_fee_placeholders(self) -> None:
        packet = valid_packet()
        packet["redacted_placeholder_rows"] = packet["redacted_placeholder_rows"][:-1]

        self.assertIn("missing_redacted_placeholder_row", violation_codes(packet))

    def test_rejects_unredacted_placeholder_values(self) -> None:
        packet = valid_packet()
        packet["redacted_placeholder_rows"][0]["placeholder"] = "permit number: 24-123456-000-00-CO"

        self.assertIn("missing_redacted_placeholder_row", violation_codes(packet))
        self.assertIn("private_account_value", violation_codes(packet))

    def test_rejects_missing_validation_commands(self) -> None:
        packet = valid_packet()
        packet["validation_commands"] = []

        self.assertIn("missing_validation_command", violation_codes(packet))

    def test_rejects_missing_redaction_requirements(self) -> None:
        packet = valid_packet()
        packet["redaction_requirements"] = packet["redaction_requirements"][:-1]

        self.assertIn("missing_redaction_requirement", violation_codes(packet))

    def test_rejects_missing_redaction_fields(self) -> None:
        packet = valid_packet()
        packet["redaction_requirements"][0].pop("enforced")

        self.assertIn("missing_redaction_requirement", violation_codes(packet))

    def test_rejects_missing_attendance_checkpoints(self) -> None:
        packet = valid_packet()
        packet["attendance_checkpoints"] = packet["attendance_checkpoints"][:-1]

        self.assertIn("missing_attendance_checkpoint", violation_codes(packet))

    def test_rejects_missing_attendance_fields(self) -> None:
        packet = valid_packet()
        packet["attendance_checkpoints"][0].pop("requires_user_attendance")

        self.assertIn("missing_attendance_checkpoint", violation_codes(packet))

    def test_rejects_credentials_and_private_account_values(self) -> None:
        cases = (
            ("credential", "secret-value", "credential_artifact"),
            ("password", "not-redacted", "credential_artifact"),
            ("private_account_value", "permit number: 24-123456-000-00-CO", "private_account_value"),
        )

        for key, value, expected_code in cases:
            with self.subTest(key=key):
                packet = valid_packet()
                packet["ui_observations"][0][key] = value
                self.assertIn(expected_code, violation_codes(packet))

    def test_rejects_session_browser_screenshots_traces_and_har_artifacts(self) -> None:
        cases = (
            ("session_file", "storage_state.json", "session_file_artifact"),
            ("browser_state", {"origin": "devhub"}, "browser_artifact"),
            ("screenshot_path", "devhub-home.png", "screenshot_artifact"),
            ("trace_path", "trace.zip", "trace_artifact"),
            ("har_path", "network.har", "har_artifact"),
        )

        for key, value, expected_code in cases:
            with self.subTest(key=key):
                packet = valid_packet()
                packet["ui_observations"][0][key] = value
                self.assertIn(expected_code, violation_codes(packet))

    def test_rejects_write_capable_action_evidence(self) -> None:
        packet = valid_packet()
        packet["ui_observations"][0]["observed_actions"] = [
            {"action_class": "write_capable", "action_summary": "press a DevHub button"}
        ]

        self.assertIn("write_capable_action", violation_codes(packet))

    def test_rejects_automated_login_captcha_mfa_and_account_creation_handling(self) -> None:
        prohibited_cases = (
            {"automated_login": True},
            {"captcha_automation": "solve CAPTCHA challenge"},
            {"mfa_automation": "handle MFA prompt"},
            {"account_creation": "create account before observation"},
            {"evidence_summary": "Fixture would automate login before the observation."},
            {"evidence_summary": "Fixture would solve CAPTCHA during sign-in."},
            {"evidence_summary": "Fixture would perform MFA for the user."},
            {"evidence_summary": "Fixture would automate account creation."},
        )

        for prohibited in prohibited_cases:
            with self.subTest(prohibited=prohibited):
                packet = valid_packet()
                packet["ui_observations"][0].update(prohibited)
                self.assertIn("prohibited_auth_automation", violation_codes(packet))

    def test_rejects_official_completion_and_consequential_action_claims(self) -> None:
        cases = (
            ("The permit application was submitted.", "official_action_completion_claim"),
            ("Payment completed in DevHub.", "official_action_completion_claim"),
            ("The packet can upload corrections.", "consequential_action_claim"),
            ("The operator may schedule inspection.", "consequential_action_claim"),
        )

        for text, expected_code in cases:
            with self.subTest(text=text):
                packet = valid_packet()
                packet["ui_observations"][0]["evidence_summary"] = text
                self.assertIn(expected_code, violation_codes(packet))

    def test_rejects_live_crawl_claims(self) -> None:
        packet = valid_packet()
        packet["ui_observations"][0]["evidence_summary"] = "The live crawl opened DevHub with an authenticated session."

        self.assertIn("live_crawl_claim", violation_codes(packet))

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
