from __future__ import annotations

import unittest

from ppd.agent_readiness.devhub_observation_backlog_packet_v1 import (
    PACKET_VERSION,
    validate_devhub_observation_backlog_packet_v1,
)


def valid_packet() -> dict:
    common_commands = [["python3", "-m", "unittest", "discover", "-s", "ppd/tests", "-p", "test_*.py"]]
    return {
        "packet_version": PACKET_VERSION,
        "packet_id": "synthetic-attended-devhub-readonly-backlog-v1",
        "attendance_mode": "manual_attended",
        "observation_mode": "read_only",
        "safe_read_only_classifications": [
            {"surface": "synthetic_permit_status", "classification": "safe_read_only"}
        ],
        "redaction_requirements": ["record only synthetic labels and typed placeholders"],
        "manual_attendance_checkpoints": ["operator remains present before every observed navigation step"],
        "blocked_consequential_actions": [
            {"action": "submit application", "classification": "consequential", "status": "blocked"},
            {"action": "upload document", "classification": "consequential", "status": "blocked"},
            {"action": "pay fee", "classification": "financial", "status": "blocked"},
            {"action": "schedule inspection", "classification": "consequential", "status": "blocked"},
            {"action": "cancel request", "classification": "consequential", "status": "blocked"},
            {"action": "certify application", "classification": "consequential", "status": "blocked"},
        ],
        "validation_commands": common_commands,
        "artifact_policy": {
            "creates_auth_files": False,
            "creates_browser_artifacts": False,
            "creates_har_files": False,
            "creates_screenshots": False,
            "creates_session_state": False,
            "creates_traces": False,
            "captures_private_values": False,
            "stores_downloads": False,
            "stores_raw_crawl_output": False,
        },
        "mutation_flags": {
            "active_surface_mutation": False,
            "active_guardrail_mutation": False,
            "active_prompt_mutation": False,
            "active_release_state_mutation": False,
            "active_agent_state_mutation": False,
        },
        "work_items": [
            {
                "id": "observe-synthetic-permit-status",
                "surface": "synthetic_permit_status",
                "classification": "safe_read_only",
                "objective": "Observe synthetic status labels and navigation structure only.",
                "redaction_requirements": ["use placeholders for account scoped values"],
                "manual_attendance_checkpoints": ["pause before any non-observation control"],
                "blocked_consequential_actions": ["submit application", "upload document", "pay fee"],
                "validation_commands": common_commands,
            }
        ],
    }


class DevhubObservationBacklogPacketV1Test(unittest.TestCase):
    def assert_rejects(self, packet: dict, expected_fragment: str) -> None:
        errors = validate_devhub_observation_backlog_packet_v1(packet)
        self.assertTrue(errors, "packet unexpectedly validated")
        self.assertTrue(any(expected_fragment in error for error in errors), errors)

    def test_valid_packet_passes(self) -> None:
        self.assertEqual([], validate_devhub_observation_backlog_packet_v1(valid_packet()))

    def test_rejects_missing_required_backlog_sections(self) -> None:
        for key in (
            "safe_read_only_classifications",
            "redaction_requirements",
            "manual_attendance_checkpoints",
            "blocked_consequential_actions",
            "validation_commands",
        ):
            packet = valid_packet()
            packet[key] = []
            self.assert_rejects(packet, f"{key} must be a non-empty list")

    def test_rejects_missing_work_item_controls(self) -> None:
        for key in (
            "redaction_requirements",
            "manual_attendance_checkpoints",
            "blocked_consequential_actions",
            "validation_commands",
        ):
            packet = valid_packet()
            packet["work_items"][0][key] = []
            self.assert_rejects(packet, f"work_items[0].{key} must be a non-empty list")

    def test_rejects_non_safe_read_only_classifications(self) -> None:
        packet = valid_packet()
        packet["safe_read_only_classifications"][0]["classification"] = "reversible_draft_edit"
        self.assert_rejects(packet, "safe_read_only_classifications[0].classification must be safe_read_only")

        packet = valid_packet()
        packet["work_items"][0]["classification"] = "financial"
        self.assert_rejects(packet, "work_items[0].classification must be safe_read_only")

    def test_rejects_private_capture_and_raw_data_artifacts(self) -> None:
        cases = [
            ("operator_notes", "stored DevHub session cookie", "private/authenticated/session artifact"),
            ("operator_notes", "kept screenshot.png and network.har", "screenshot/trace/HAR/auth-file artifact"),
            ("operator_notes", "raw crawl and downloaded PDF data", "raw crawl/PDF/downloaded data"),
        ]
        for key, value, fragment in cases:
            packet = valid_packet()
            packet[key] = value
            self.assert_rejects(packet, fragment)

    def test_rejects_live_execution_claims_and_outcome_guarantees(self) -> None:
        packet = valid_packet()
        packet["operator_notes"] = "Ran against live DevHub and completed authenticated run."
        self.assert_rejects(packet, "live authenticated execution claim")

        packet = valid_packet()
        packet["operator_notes"] = "Permit approved and will be issued."
        self.assert_rejects(packet, "legal or permitting outcome guarantee")

    def test_rejects_consequential_language_outside_blocked_rows(self) -> None:
        packet = valid_packet()
        packet["work_items"][0]["objective"] = "Submit payment after observation."
        self.assert_rejects(packet, "consequential action language outside blocked rows")

    def test_rejects_artifact_policy_and_active_mutation_flags(self) -> None:
        for key in (
            "creates_auth_files",
            "creates_browser_artifacts",
            "creates_har_files",
            "creates_screenshots",
            "creates_session_state",
            "creates_traces",
            "captures_private_values",
            "stores_downloads",
            "stores_raw_crawl_output",
        ):
            packet = valid_packet()
            packet["artifact_policy"][key] = True
            self.assert_rejects(packet, f"artifact_policy.{key} must be false")

        for key in (
            "active_surface_mutation",
            "active_guardrail_mutation",
            "active_prompt_mutation",
            "active_release_state_mutation",
            "active_agent_state_mutation",
        ):
            packet = valid_packet()
            packet["mutation_flags"][key] = True
            self.assert_rejects(packet, f"mutation_flags.{key} must be false or absent")


if __name__ == "__main__":
    unittest.main()
