from __future__ import annotations

import unittest
from copy import deepcopy

from ppd.agent_readiness.devhub_attended_observation_renewal_queue_v1 import (
    QUEUE_VERSION,
    validate_devhub_attended_observation_renewal_queue_v1,
)


def valid_queue() -> dict:
    return {
        "queue_version": QUEUE_VERSION,
        "queue_id": "synthetic-attended-observation-renewal-queue-v1",
        "observation_candidate_rows": [
            {
                "candidate_id": "renew-synthetic-permit-status",
                "surface_id": "synthetic_permit_status",
                "renewal_reason": "Refresh offline read-only surface notes from cited public guidance.",
                "reviewer_owner": "ppd-reviewer",
                "source_evidence_ids": ["public-devhub-faq"],
                "attendance_preflight_placeholder_id": "attendance-preflight-1",
                "redaction_checklist_reference_id": "redaction-checklist-1",
                "safe_read_only_action_classification_id": "classification-1",
                "blocked_consequential_action_reminder_id": "blocked-reminder-1",
                "reviewer_approval_placeholder_id": "reviewer-approval-1",
            }
        ],
        "attendance_preflight_placeholders": [
            {
                "attendance_preflight_placeholder_id": "attendance-preflight-1",
                "status": "placeholder_only",
                "note": "Human operator presence must be confirmed before any offline observation renewal is accepted.",
            }
        ],
        "redaction_checklist_references": [
            {
                "redaction_checklist_reference_id": "redaction-checklist-1",
                "checklist_ref": "ppd-redacted-read-only-observation-checklist",
                "note": "Record synthetic labels, public citations, and placeholders only.",
            }
        ],
        "safe_read_only_action_classifications": [
            {
                "classification_id": "classification-1",
                "classification": "safe_read_only",
                "note": "Observation candidate is limited to offline review of visible labels and navigation structure.",
            }
        ],
        "blocked_consequential_action_reminders": [
            {
                "blocked_consequential_action_reminder_id": "blocked-reminder-1",
                "reminder": "Payment, submission, scheduling, cancellation, certification, and upload workflows remain blocked.",
            }
        ],
        "reviewer_approval_placeholders": [
            {
                "reviewer_approval_placeholder_id": "reviewer-approval-1",
                "status": "pending_reviewer_approval",
                "note": "Reviewer approval must be supplied before renewal can feed any downstream packet.",
            }
        ],
        "artifact_policy": {
            "captures_auth_files": False,
            "captures_browser_artifacts": False,
            "captures_har_files": False,
            "captures_private_page_values": False,
            "captures_private_values": False,
            "captures_screenshots": False,
            "captures_session_state": False,
            "captures_traces": False,
            "creates_auth_files": False,
            "creates_browser_artifacts": False,
            "creates_har_files": False,
            "creates_screenshots": False,
            "creates_session_state": False,
            "creates_traces": False,
            "stores_downloads": False,
            "stores_raw_crawl_output": False,
            "stores_raw_private_output": False,
        },
        "mutation_flags": {
            "active_surface_mutation": False,
            "active_guardrail_mutation": False,
            "active_prompt_mutation": False,
            "active_release_state_mutation": False,
            "active_agent_state_mutation": False,
        },
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
    }


class DevHubAttendedObservationRenewalQueueV1Test(unittest.TestCase):
    def assert_rejects(self, queue: dict, expected_code: str) -> None:
        issues = validate_devhub_attended_observation_renewal_queue_v1(queue)
        self.assertTrue(issues, "queue unexpectedly validated")
        self.assertTrue(any(issue.code == expected_code for issue in issues), [issue.as_dict() for issue in issues])

    def test_valid_queue_passes(self) -> None:
        self.assertEqual([], validate_devhub_attended_observation_renewal_queue_v1(valid_queue()))

    def test_rejects_missing_required_queue_sections(self) -> None:
        expected = {
            "observation_candidate_rows": "missing_observation_candidate_rows",
            "attendance_preflight_placeholders": "missing_attendance_preflight_placeholders",
            "redaction_checklist_references": "missing_redaction_checklist_references",
            "safe_read_only_action_classifications": "missing_safe_read_only_action_classifications",
            "blocked_consequential_action_reminders": "missing_blocked_consequential_action_reminders",
            "reviewer_approval_placeholders": "missing_reviewer_approval_placeholders",
        }
        for key, code in expected.items():
            queue = valid_queue()
            queue[key] = []
            self.assert_rejects(queue, code)

    def test_rejects_missing_candidate_row_references(self) -> None:
        expected = {
            "attendance_preflight_placeholder_id": "missing_attendance_preflight_placeholder_id",
            "redaction_checklist_reference_id": "missing_redaction_checklist_reference_id",
            "safe_read_only_action_classification_id": "missing_safe_read_only_action_classification_id",
            "blocked_consequential_action_reminder_id": "missing_blocked_consequential_action_reminder_id",
            "reviewer_approval_placeholder_id": "missing_reviewer_approval_placeholder_id",
        }
        for key, code in expected.items():
            queue = valid_queue()
            queue["observation_candidate_rows"][0][key] = ""
            self.assert_rejects(queue, code)

    def test_rejects_unknown_candidate_row_references(self) -> None:
        queue = valid_queue()
        queue["observation_candidate_rows"][0]["reviewer_approval_placeholder_id"] = "missing-reviewer"
        self.assert_rejects(queue, "unknown_reviewer_approval_placeholder_id")

    def test_rejects_non_safe_read_only_action_classifications(self) -> None:
        queue = valid_queue()
        queue["safe_read_only_action_classifications"][0]["classification"] = "reversible_draft"
        self.assert_rejects(queue, "unsafe_action_classification")

    def test_rejects_artifact_policy_flags(self) -> None:
        for key in valid_queue()["artifact_policy"]:
            queue = valid_queue()
            queue["artifact_policy"][key] = True
            self.assert_rejects(queue, "artifact_policy_not_false")

    def test_rejects_credentials_session_auth_browser_artifacts_and_private_values(self) -> None:
        cases = (
            ("stored credential token", "private_or_session_artifact_language"),
            ("kept DevHub session state", "private_or_session_artifact_language"),
            ("captured auth state and browser profile", "private_or_session_artifact_language"),
            ("recorded private page value", "private_or_session_artifact_language"),
            ("saved screenshot.png with network trace.har", "browser_capture_artifact_language"),
        )
        for text, code in cases:
            queue = valid_queue()
            queue["operator_notes"] = text
            self.assert_rejects(queue, code)

    def test_rejects_live_devhub_access_claims(self) -> None:
        queue = valid_queue()
        queue["operator_notes"] = "Logged into DevHub and ran against live DevHub."
        self.assert_rejects(queue, "live_devhub_access_claim")

    def test_rejects_consequential_language_outside_blocked_reminders(self) -> None:
        for phrase in (
            "payment",
            "submission",
            "scheduling",
            "cancellation",
            "certification",
            "upload",
        ):
            queue = valid_queue()
            queue["observation_candidate_rows"][0]["renewal_reason"] = f"Candidate mentions {phrase}."
            self.assert_rejects(queue, "consequential_action_language")

    def test_rejects_active_surface_guardrail_prompt_and_release_state_mutation_flags(self) -> None:
        for flag in (
            "active_surface_mutation",
            "active_guardrail_mutation",
            "active_prompt_mutation",
            "active_release_state_mutation",
            "active_agent_state_mutation",
        ):
            queue = deepcopy(valid_queue())
            queue["mutation_flags"][flag] = True
            self.assert_rejects(queue, "active_mutation_flag")


if __name__ == "__main__":
    unittest.main()
