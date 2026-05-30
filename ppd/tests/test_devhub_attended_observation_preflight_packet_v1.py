from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.devhub.devhub_attended_observation_preflight_packet_v1 import (
    PREFLIGHT_PACKET_VERSION,
    assert_valid_devhub_attended_observation_preflight_packet_v1,
    build_devhub_attended_observation_preflight_packet_v1,
    load_json_packet,
    validate_devhub_attended_observation_preflight_packet_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "devhub_attended_observation_renewal_queue_v1.json"


def _valid_packet() -> dict[str, object]:
    return build_devhub_attended_observation_preflight_packet_v1(load_json_packet(FIXTURE_PATH))


def test_builds_ordered_observation_session_readiness_rows_from_renewal_queue_fixture() -> None:
    queue = load_json_packet(FIXTURE_PATH)

    packet = build_devhub_attended_observation_preflight_packet_v1(queue)

    assert packet["packet_version"] == PREFLIGHT_PACKET_VERSION
    assert packet["source_queue_id"] == queue["queue_id"]
    assert [row["order"] for row in packet["observation_session_readiness_rows"]] == [1, 2]
    assert [row["source_candidate_id"] for row in packet["observation_session_readiness_rows"]] == [
        "renew-devhub-home-readonly",
        "renew-permit-status-readonly",
    ]
    assert validate_devhub_attended_observation_preflight_packet_v1(packet) == []


def test_packet_contains_manual_login_redaction_scope_blocker_and_reviewer_sections() -> None:
    packet = _valid_packet()

    assert packet["manual_login_handoff_placeholders"]
    assert packet["redaction_checklist_confirmations"]
    assert packet["read_only_surface_scope_citations"]
    assert packet["blocked_consequential_action_reminders"]
    assert packet["reviewer_approval_placeholders"]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]
    assert all(row["confirmation_status"] == "pending_reviewer_confirmation" for row in packet["redaction_checklist_confirmations"])


def test_packet_blocks_artifacts_and_mutations() -> None:
    packet = _valid_packet()

    assert all(value is False for value in packet["artifact_policy"].values())
    assert all(value is False for value in packet["mutation_flags"].values())


@pytest.mark.parametrize(
    "required_key",
    [
        "observation_session_readiness_rows",
        "manual_login_handoff_placeholders",
        "redaction_checklist_confirmations",
        "read_only_surface_scope_citations",
        "blocked_consequential_action_reminders",
        "reviewer_approval_placeholders",
        "offline_validation_commands",
    ],
)
def test_validator_rejects_missing_required_preflight_sections(required_key: str) -> None:
    packet = _valid_packet()
    packet[required_key] = []

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert f"{required_key} must be a non-empty list" in errors


def test_validator_rejects_uncited_read_only_surface_scope() -> None:
    packet = _valid_packet()
    packet["observation_session_readiness_rows"][0]["read_only_surface_scope_citation_ids"] = ["missing-scope-citation"]

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert any("must reference a declared read-only scope citation" in error for error in errors)


def test_validator_rejects_unknown_manual_redaction_blocker_and_reviewer_refs() -> None:
    packet = _valid_packet()
    row = packet["observation_session_readiness_rows"][0]
    row["manual_login_handoff_placeholder_id"] = "missing-manual"
    row["redaction_checklist_confirmation_id"] = "missing-redaction"
    row["blocked_consequential_action_reminder_id"] = "missing-blocker"
    row["reviewer_approval_placeholder_id"] = "missing-reviewer"

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert sum("must reference a declared preflight packet item" in error for error in errors) == 4


def test_validator_rejects_out_of_order_readiness_rows() -> None:
    packet = _valid_packet()
    packet["observation_session_readiness_rows"][1]["order"] = 4

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert "observation_session_readiness_rows order must be contiguous starting at 1" in errors


@pytest.mark.parametrize(
    "field_value",
    [
        "credential token",
        "auth state file",
        "DevHub session storage",
        "browser artifact",
        "private page value",
        "screenshot trace.zip HAR file",
    ],
)
def test_validator_rejects_credentials_sessions_auth_browser_and_capture_artifacts(field_value: str) -> None:
    packet = _valid_packet()
    packet["manual_login_handoff_placeholders"][0]["operator_note"] = field_value

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert any("private or browser evidence language" in error for error in errors)


def test_validator_rejects_live_devhub_access_claims() -> None:
    packet = _valid_packet()
    packet["observation_session_readiness_rows"][0]["renewal_reason"] = "Logged into DevHub and completed authenticated run."

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert any("live DevHub access language" in error for error in errors)


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "read-only metadata then payment",
        "read-only metadata then submission",
        "read-only metadata then scheduling",
        "read-only metadata then cancellation",
        "read-only metadata then certification",
        "read-only metadata then upload",
    ],
)
def test_validator_rejects_consequential_language_outside_blocked_reminders(unsafe_text: str) -> None:
    packet = _valid_packet()
    packet["observation_session_readiness_rows"][0]["allowed_result"] = unsafe_text

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert any("consequential action language outside blocked reminders" in error for error in errors)


@pytest.mark.parametrize(
    "flag_key",
    [
        "active_surface_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
    ],
)
def test_validator_rejects_active_surface_guardrail_prompt_and_release_mutation_flags(flag_key: str) -> None:
    packet = _valid_packet()
    packet["mutation_flags"] = deepcopy(packet["mutation_flags"])
    packet["mutation_flags"][flag_key] = True

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert f"mutation_flags.{flag_key} must be false" in "; ".join(errors)


def test_validator_rejects_nested_active_mutation_flags() -> None:
    packet = _valid_packet()
    packet["observation_session_readiness_rows"][0]["mutates_surfaces"] = "enabled"

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert any("mutates_surfaces must be false" in error for error in errors)


def test_validator_rejects_live_or_browser_validation_commands() -> None:
    packet = _valid_packet()
    packet["offline_validation_commands"].append(["npx", "playwright", "test", "--headed"])

    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)

    assert any("offline_validation_commands" in error and "must stay offline" in error for error in errors)


def test_assert_valid_raises_stable_error() -> None:
    packet = _valid_packet()
    packet["artifact_policy"]["captures_screenshots"] = True

    with pytest.raises(AssertionError, match="artifact_policy.captures_screenshots must be false"):
        assert_valid_devhub_attended_observation_preflight_packet_v1(packet)
