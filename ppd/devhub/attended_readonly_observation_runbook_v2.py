"""Fixture-first attended DevHub read-only observation runbook v2.

This module consumes an already-sanitized attended DevHub read-only preflight
packet v2 and produces deterministic synthetic observation steps. It never
launches Playwright, opens DevHub, logs in, persists browser outputs, stores
private values, or enables consequential DevHub actions.
"""

from __future__ import annotations

from typing import Any, Mapping

from ppd.devhub.read_only_preflight_v2 import (
    PACKET_VERSION as PREFLIGHT_PACKET_VERSION,
    assert_attended_read_only_preflight_packet_v2,
)

RUNBOOK_VERSION = "attended_devhub_readonly_observation_runbook_v2"

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/devhub/attended_readonly_observation_runbook_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_attended_readonly_observation_runbook_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

FORBIDDEN_ACTIONS = (
    "upload",
    "submission",
    "certification",
    "payment",
    "scheduling",
    "cancellation",
    "account_change",
    "official_draft_save",
)

METADATA_CAPTURE_FIELDS = [
    {
        "field_id": "observation_step_id",
        "capture_rule": "Synthetic step identifier only; no live page value.",
        "redaction": "not_private",
    },
    {
        "field_id": "destination_category",
        "capture_rule": "Copy the allowed read-only destination label from the preflight packet.",
        "redaction": "metadata_only",
    },
    {
        "field_id": "accessible_role_placeholder",
        "capture_rule": "Use placeholders such as ROLE_NAVIGATION, ROLE_HEADING, ROLE_STATUS, ROLE_LINK, or ROLE_TABLE.",
        "redaction": "placeholder_only",
    },
    {
        "field_id": "validation_message_placeholder",
        "capture_rule": "Use REDACTED_VALIDATION_MESSAGE_KIND without copying account-scoped text.",
        "redaction": "placeholder_only",
    },
    {
        "field_id": "blocked_action_label_placeholder",
        "capture_rule": "Record only generic blocked-action categories such as BLOCKED_SUBMIT_CONTROL.",
        "redaction": "placeholder_only",
    },
    {
        "field_id": "reviewer_disposition_placeholder",
        "capture_rule": "One of pending_review, accepted_metadata_only, needs_redaction_rework, or rejected_not_read_only.",
        "redaction": "review_metadata_only",
    },
]

ACCESSIBLE_ROLE_PLACEHOLDERS = [
    "ROLE_NAVIGATION",
    "ROLE_MAIN",
    "ROLE_HEADING",
    "ROLE_STATUS",
    "ROLE_LINK",
    "ROLE_BUTTON_READONLY_CONTEXT_ONLY",
    "ROLE_TABLE",
    "ROLE_LIST",
    "ROLE_DIALOG_READONLY_CONTEXT_ONLY",
]

VALIDATION_MESSAGE_PLACEHOLDERS = [
    "REDACTED_REQUIRED_FIELD_MESSAGE_KIND",
    "REDACTED_STATUS_MESSAGE_KIND",
    "REDACTED_NAVIGATION_WARNING_KIND",
    "REDACTED_ACTION_BLOCKED_MESSAGE_KIND",
]

REVIEWER_DISPOSITION_PLACEHOLDERS = [
    {
        "disposition": "pending_review",
        "meaning": "Reviewer has not accepted the synthetic observation row.",
    },
    {
        "disposition": "accepted_metadata_only",
        "meaning": "Reviewer accepts that only structural metadata and placeholders are present.",
    },
    {
        "disposition": "needs_redaction_rework",
        "meaning": "Reviewer found a value that must be replaced by a placeholder before use.",
    },
    {
        "disposition": "rejected_not_read_only",
        "meaning": "Reviewer found that the row crosses into a consequential DevHub path.",
    },
]

REDACTED_JOURNAL_EVENT_EXAMPLES = [
    {
        "event_type": "DevHub attended preflight",
        "event_id": "journal-example-preflight-readonly-v2",
        "summary": "Preflight packet accepted for synthetic read-only observation planning.",
        "kept_fields": ["packet_version", "destination_category_count", "validation_command_count"],
        "redacted_fields": ["REDACTED_PRIVATE_PAGE_VALUE", "REDACTED_ACCOUNT_IDENTIFIER"],
    },
    {
        "event_type": "manual handoff",
        "event_id": "journal-example-manual-handoff-v2",
        "summary": "Attending user remains responsible for all sign-in, challenge, and destination choices.",
        "kept_fields": ["handoff_required", "stop_before_action_checkpoint"],
        "redacted_fields": ["REDACTED_SIGNIN_VALUE", "REDACTED_SECURITY_PROMPT_VALUE"],
    },
    {
        "event_type": "exact-confirmation checkpoint",
        "event_id": "journal-example-stop-before-action-v2",
        "summary": "Worker stops before upload, submit, certify, pay, schedule, cancel, account-change, or official draft-save controls.",
        "kept_fields": ["blocked_action_category", "reviewer_disposition_placeholder"],
        "redacted_fields": ["REDACTED_CONTROL_CONTEXT_VALUE"],
    },
]

STOP_BEFORE_ACTION_CHECKPOINTS = [
    {
        "checkpoint_id": "stop-before-upload",
        "trigger": "Any upload, attachment add, replacement, correction upload, or document selection control is visible or required.",
        "required_response": "Stop before interacting with the control and record only BLOCKED_UPLOAD_CONTROL.",
    },
    {
        "checkpoint_id": "stop-before-submit-or-certify",
        "trigger": "Any submit, final review, acknowledgement, certification, declaration, or attestation path appears.",
        "required_response": "Stop before activation and record only BLOCKED_SUBMIT_OR_CERTIFY_CONTROL.",
    },
    {
        "checkpoint_id": "stop-before-payment",
        "trigger": "Any fee checkout, payment method, payment continuation, purchase, or final payment control appears.",
        "required_response": "Stop before payment flow and record only BLOCKED_PAYMENT_CONTROL.",
    },
    {
        "checkpoint_id": "stop-before-schedule-cancel-or-account-change",
        "trigger": "Any inspection scheduling, cancellation, withdrawal, account profile change, registration, or official save control appears.",
        "required_response": "Stop before the action and record only BLOCKED_ACCOUNT_OR_STATUS_CHANGE_CONTROL.",
    },
]


def build_attended_readonly_observation_runbook_v2(preflight_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic observation runbook from a validated preflight packet."""

    assert_attended_read_only_preflight_packet_v2(preflight_packet)

    destinations = list(preflight_packet.get("allowed_read_only_destinations", []))
    steps = []
    for order, destination in enumerate(destinations, start=1):
        steps.append(
            {
                "order": order,
                "step_id": f"synthetic-readonly-observation-step-{order:02d}",
                "destination_category": str(destination),
                "source_preflight_version": PREFLIGHT_PACKET_VERSION,
                "operator_instruction": "Observe only structural UI metadata for the user-selected read-only destination.",
                "metadata_capture_fields": [field["field_id"] for field in METADATA_CAPTURE_FIELDS],
                "allowed_accessible_role_placeholders": ACCESSIBLE_ROLE_PLACEHOLDERS,
                "validation_message_placeholders": VALIDATION_MESSAGE_PLACEHOLDERS,
                "stop_before_action_checkpoints": [checkpoint["checkpoint_id"] for checkpoint in STOP_BEFORE_ACTION_CHECKPOINTS],
                "reviewer_disposition_placeholder": "pending_review",
            }
        )

    return {
        "version": RUNBOOK_VERSION,
        "consumes_version": PREFLIGHT_PACKET_VERSION,
        "mode": "offline_fixture_first_synthetic_observation_runbook",
        "playwright_launched": False,
        "devhub_opened": False,
        "login_performed": False,
        "private_values_stored": False,
        "browser_artifacts_stored": False,
        "consequential_actions_enabled": False,
        "official_draft_saves_enabled": False,
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "preflight_references": {
            "manual_login_readiness_check_count": len(preflight_packet.get("manual_login_readiness_checks", [])),
            "attendance_statement_count": len(preflight_packet.get("attendance_statements", [])),
            "redaction_requirement_count": len(preflight_packet.get("redaction_requirements", [])),
            "abort_condition_count": len(preflight_packet.get("abort_conditions", [])),
        },
        "ordered_synthetic_observation_steps": steps,
        "metadata_capture_fields": METADATA_CAPTURE_FIELDS,
        "allowed_accessible_role_placeholders": ACCESSIBLE_ROLE_PLACEHOLDERS,
        "validation_message_placeholders": VALIDATION_MESSAGE_PLACEHOLDERS,
        "redacted_journal_event_examples": REDACTED_JOURNAL_EVENT_EXAMPLES,
        "stop_before_action_checkpoints": STOP_BEFORE_ACTION_CHECKPOINTS,
        "reviewer_disposition_placeholders": REVIEWER_DISPOSITION_PLACEHOLDERS,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }


def validate_attended_readonly_observation_runbook_v2(runbook: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a synthetic observation runbook."""

    errors: list[str] = []
    if runbook.get("version") != RUNBOOK_VERSION:
        errors.append(f"version must be {RUNBOOK_VERSION!r}")
    if runbook.get("consumes_version") != PREFLIGHT_PACKET_VERSION:
        errors.append(f"consumes_version must be {PREFLIGHT_PACKET_VERSION!r}")

    for field in (
        "playwright_launched",
        "devhub_opened",
        "login_performed",
        "private_values_stored",
        "browser_artifacts_stored",
        "consequential_actions_enabled",
        "official_draft_saves_enabled",
    ):
        if runbook.get(field) is not False:
            errors.append(f"{field} must be false")

    steps = runbook.get("ordered_synthetic_observation_steps")
    if not isinstance(steps, list) or not steps:
        errors.append("ordered_synthetic_observation_steps must be a non-empty list")
    elif [step.get("order") for step in steps if isinstance(step, Mapping)] != list(range(1, len(steps) + 1)):
        errors.append("ordered_synthetic_observation_steps must be ordered from 1")

    required_lists = (
        "metadata_capture_fields",
        "allowed_accessible_role_placeholders",
        "validation_message_placeholders",
        "redacted_journal_event_examples",
        "stop_before_action_checkpoints",
        "reviewer_disposition_placeholders",
        "offline_validation_commands",
    )
    for field in required_lists:
        value = runbook.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{field} must be a non-empty list")

    commands = runbook.get("offline_validation_commands")
    if commands != OFFLINE_VALIDATION_COMMANDS:
        errors.append("offline_validation_commands must match the exact runbook validation commands")

    forbidden_actions = set(runbook.get("forbidden_actions", []))
    for action in FORBIDDEN_ACTIONS:
        if action not in forbidden_actions:
            errors.append(f"forbidden_actions must include {action}")

    return errors


def require_attended_readonly_observation_runbook_v2(runbook: Mapping[str, Any]) -> None:
    """Raise ValueError when a runbook is incomplete or unsafe."""

    errors = validate_attended_readonly_observation_runbook_v2(runbook)
    if errors:
        raise ValueError("invalid attended DevHub read-only observation runbook v2: " + "; ".join(errors))
