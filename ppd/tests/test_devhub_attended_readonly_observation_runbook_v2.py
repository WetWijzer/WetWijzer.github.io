from __future__ import annotations

import copy

import pytest

from ppd.devhub.attended_readonly_observation_runbook_v2 import (
    FORBIDDEN_ACTIONS,
    OFFLINE_VALIDATION_COMMANDS,
    RUNBOOK_VERSION,
    build_attended_readonly_observation_runbook_v2,
    require_attended_readonly_observation_runbook_v2,
    validate_attended_readonly_observation_runbook_v2,
)
from ppd.devhub.read_only_preflight_v2 import PACKET_VERSION as PREFLIGHT_PACKET_VERSION


def valid_preflight_packet() -> dict[str, object]:
    return {
        "version": PREFLIGHT_PACKET_VERSION,
        "manual_login_readiness_checks": [
            "User-visible browser is ready for manual PortlandOregon.gov sign-in.",
            "User handles CAPTCHA and MFA prompts manually while the worker waits.",
        ],
        "allowed_read_only_destinations": [
            "DevHub Home read-only review",
            "My Permits & Requests read-only status review",
            "Permit details status message review",
        ],
        "attendance_statements": [
            "The user remains present for the full observed run.",
            "The worker stops if the user leaves or cannot review the visible page.",
        ],
        "redaction_requirements": [
            "Only redacted metadata and accessible UI labels may be recorded.",
            "Private field values, account identifiers, and payment details are omitted.",
        ],
        "abort_conditions": [
            "Abort before any submit, upload, certify, pay, schedule, cancel, or save action.",
            "Abort when a page requests sign-in secrets, CAPTCHA, MFA, or payment details.",
        ],
        "no_private_artifact_commitments": [
            "Do not persist authenticated page bodies or account-scoped values.",
            "Do not commit local browser outputs or private user material.",
        ],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "active_prompt_mutation": False,
        "active_guardrail_mutation": False,
        "active_devhub_surface_mutation": False,
        "active_source_mutation": False,
        "active_contract_mutation": False,
        "active_release_state_mutation": False,
    }


def test_builds_ordered_synthetic_runbook_from_valid_preflight_packet() -> None:
    runbook = build_attended_readonly_observation_runbook_v2(valid_preflight_packet())

    assert runbook["version"] == RUNBOOK_VERSION
    assert runbook["consumes_version"] == PREFLIGHT_PACKET_VERSION
    assert runbook["mode"] == "offline_fixture_first_synthetic_observation_runbook"
    assert runbook["playwright_launched"] is False
    assert runbook["devhub_opened"] is False
    assert runbook["login_performed"] is False
    assert runbook["private_values_stored"] is False
    assert runbook["browser_artifacts_stored"] is False
    assert runbook["consequential_actions_enabled"] is False
    assert runbook["official_draft_saves_enabled"] is False

    steps = runbook["ordered_synthetic_observation_steps"]
    assert [step["order"] for step in steps] == [1, 2, 3]
    assert steps[0]["step_id"] == "synthetic-readonly-observation-step-01"
    assert steps[0]["reviewer_disposition_placeholder"] == "pending_review"


def test_runbook_contains_metadata_placeholders_and_redacted_journal_examples() -> None:
    runbook = build_attended_readonly_observation_runbook_v2(valid_preflight_packet())

    capture_field_ids = {field["field_id"] for field in runbook["metadata_capture_fields"]}
    assert "accessible_role_placeholder" in capture_field_ids
    assert "validation_message_placeholder" in capture_field_ids
    assert "blocked_action_label_placeholder" in capture_field_ids

    assert "ROLE_HEADING" in runbook["allowed_accessible_role_placeholders"]
    assert "ROLE_STATUS" in runbook["allowed_accessible_role_placeholders"]
    assert "REDACTED_ACTION_BLOCKED_MESSAGE_KIND" in runbook["validation_message_placeholders"]

    journal_text = str(runbook["redacted_journal_event_examples"])
    assert "REDACTED_ACCOUNT_IDENTIFIER" in journal_text
    assert "REDACTED_CONTROL_CONTEXT_VALUE" in journal_text


def test_runbook_contains_stop_before_action_and_reviewer_disposition_placeholders() -> None:
    runbook = build_attended_readonly_observation_runbook_v2(valid_preflight_packet())

    checkpoint_ids = {checkpoint["checkpoint_id"] for checkpoint in runbook["stop_before_action_checkpoints"]}
    assert "stop-before-upload" in checkpoint_ids
    assert "stop-before-submit-or-certify" in checkpoint_ids
    assert "stop-before-payment" in checkpoint_ids
    assert "stop-before-schedule-cancel-or-account-change" in checkpoint_ids

    dispositions = {item["disposition"] for item in runbook["reviewer_disposition_placeholders"]}
    assert "pending_review" in dispositions
    assert "accepted_metadata_only" in dispositions
    assert "needs_redaction_rework" in dispositions
    assert "rejected_not_read_only" in dispositions

    assert set(FORBIDDEN_ACTIONS).issubset(set(runbook["forbidden_actions"]))


def test_runbook_exposes_exact_offline_validation_commands() -> None:
    runbook = build_attended_readonly_observation_runbook_v2(valid_preflight_packet())

    assert runbook["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in runbook["offline_validation_commands"]
    require_attended_readonly_observation_runbook_v2(runbook)


def test_rejects_invalid_preflight_packet_before_building_runbook() -> None:
    packet = valid_preflight_packet()
    packet["active_devhub_surface_mutation"] = True

    with pytest.raises(ValueError, match="active_devhub_surface_mutation"):
        build_attended_readonly_observation_runbook_v2(packet)


def test_runbook_validation_rejects_missing_ordered_steps_and_enabled_actions() -> None:
    runbook = build_attended_readonly_observation_runbook_v2(valid_preflight_packet())
    broken = copy.deepcopy(runbook)
    broken["ordered_synthetic_observation_steps"] = []
    broken["consequential_actions_enabled"] = True

    errors = validate_attended_readonly_observation_runbook_v2(broken)

    assert any("ordered_synthetic_observation_steps" in error for error in errors)
    assert any("consequential_actions_enabled" in error for error in errors)
