from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.devhub.attended_readonly_authorization_packet_v2 import (
    PACKET_VERSION,
    assert_valid_packet,
    load_packet,
    validate_packet,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub"
    / "attended_readonly_authorization_packet_v2.json"
)


def _packet() -> dict:
    return load_packet(FIXTURE_PATH)


def _findings_for_missing_key(key: str) -> list[str]:
    packet = _packet()
    packet.pop(key)
    return validate_packet(packet)


def test_attended_readonly_authorization_packet_v2_fixture_is_valid() -> None:
    packet = _packet()

    assert packet["packet_version"] == PACKET_VERSION
    assert validate_packet(packet) == []
    assert_valid_packet(packet)


def test_packet_is_fixture_first_and_does_not_authorize_live_devhub_access() -> None:
    packet = _packet()

    assert packet["authorization_mode"] == "fixture_first_attended_read_only"
    assert packet["live_devhub_access_permitted"] is False
    assert packet["creates_browser_state"] is False


def test_packet_defines_required_attended_manual_login_boundaries() -> None:
    packet = _packet()
    boundaries = " ".join(packet["manual_login_boundaries"]).lower()

    assert "manually complete mfa" in boundaries
    assert "captcha" in boundaries
    assert "must not request" in boundaries
    assert "credentials" in boundaries
    assert "account" in boundaries


def test_read_only_surfaces_allow_only_observation_and_redacted_metadata() -> None:
    packet = _packet()

    assert packet["read_only_target_surfaces"]
    for surface in packet["read_only_target_surfaces"]:
        assert surface["target_mode"] == "read_only_observation"
        assert surface["requires_user_attendance"] is True
        assert surface["allowed_actions"] == [
            "observe_visible_text",
            "record_redacted_metadata",
        ]


def test_packet_prohibits_private_devhub_artifacts() -> None:
    packet = _packet()
    artifact_types = {entry["artifact_type"] for entry in packet["prohibited_artifacts"]}

    assert "auth_state" in artifact_types
    assert "browser_context_storage" in artifact_types
    assert "browser_profile" in artifact_types
    assert "cookie_jar" in artifact_types
    assert "screenshot" in artifact_types
    assert "trace" in artifact_types
    assert "har" in artifact_types
    assert "raw_authenticated_html" in artifact_types
    assert "downloaded_document" in artifact_types
    assert "session_recording" in artifact_types
    assert "storage_state" in artifact_types


def test_packet_blocks_consequential_or_authentication_automation() -> None:
    packet = _packet()
    prohibited = set(packet["prohibited_automation_actions"])

    assert "authentication" in prohibited
    assert "mfa" in prohibited
    assert "captcha" in prohibited
    assert "submission" in prohibited
    assert "certification" in prohibited
    assert "upload" in prohibited
    assert "payment" in prohibited
    assert "schedule_inspection" in prohibited


def test_packet_includes_post_observation_review_placeholders() -> None:
    packet = _packet()
    placeholder_ids = {
        placeholder["placeholder_id"]
        for placeholder in packet["post_observation_review_placeholders"]
    }

    assert "review-redaction-completeness-v2" in placeholder_ids
    assert "review-surface-classification-v2" in placeholder_ids
    assert "review-abort-handling-v2" in placeholder_ids
    assert "review-source-gap-followup-v2" in placeholder_ids


def test_packet_offline_validation_commands_do_not_open_devhub_or_browser() -> None:
    packet = _packet()
    blocked_terms = (
        "devhub.portlandoregon.gov",
        "playwright",
        "browser",
        "curl",
        "wget",
        "screenshot",
        "trace",
        "har",
        "login",
    )

    for command in packet["offline_validation_commands"]:
        joined = " ".join(command).lower()
        assert not any(term in joined for term in blocked_terms)


@pytest.mark.parametrize(
    "key, expected",
    [
        ("synthetic_user_attended_preflight_evidence", "synthetic_user_attended_preflight_evidence must be a non-empty list"),
        ("manual_login_boundaries", "manual_login_boundaries must be a non-empty list"),
        ("read_only_target_surfaces", "read_only_target_surfaces must be a non-empty list"),
        ("redaction_expectations", "redaction_expectations must be a non-empty list"),
        ("abort_conditions", "abort_conditions must be a non-empty list"),
        ("post_observation_review_placeholders", "post_observation_review_placeholders must be a non-empty list"),
        ("offline_validation_commands", "offline_validation_commands must be a non-empty list"),
    ],
)
def test_validator_rejects_missing_required_packet_sections(key: str, expected: str) -> None:
    assert expected in _findings_for_missing_key(key)


def test_validator_rejects_missing_attendance_evidence_placeholder() -> None:
    packet = _packet()
    packet["synthetic_user_attended_preflight_evidence"] = packet["synthetic_user_attended_preflight_evidence"][1:]

    findings = validate_packet(packet)

    assert any("synthetic_user_attended_preflight_evidence missing required ids" in finding for finding in findings)


def test_validator_rejects_missing_manual_login_boundary_terms() -> None:
    packet = _packet()
    packet["manual_login_boundaries"] = ["User may be nearby."]

    findings = validate_packet(packet)

    assert any("manual_login_boundaries missing required terms" in finding for finding in findings)


def test_validator_rejects_missing_read_only_surface_target() -> None:
    packet = _packet()
    packet["read_only_target_surfaces"] = packet["read_only_target_surfaces"][:-1]

    findings = validate_packet(packet)

    assert any("read_only_target_surfaces missing required ids" in finding for finding in findings)


def test_validator_rejects_missing_redaction_expectation_terms() -> None:
    packet = _packet()
    packet["redaction_expectations"] = ["Redact some values."]

    findings = validate_packet(packet)

    assert any("redaction_expectations missing required terms" in finding for finding in findings)


def test_validator_rejects_missing_abort_condition_terms() -> None:
    packet = _packet()
    packet["abort_conditions"] = ["Stop on uncertainty."]

    findings = validate_packet(packet)

    assert any("abort_conditions missing required terms" in finding for finding in findings)


def test_validator_rejects_missing_post_observation_review_placeholder() -> None:
    packet = _packet()
    packet["post_observation_review_placeholders"] = packet["post_observation_review_placeholders"][:-1]

    findings = validate_packet(packet)

    assert any("post_observation_review_placeholders missing required ids" in finding for finding in findings)


def test_validator_rejects_missing_required_validation_command() -> None:
    packet = _packet()
    packet["offline_validation_commands"] = packet["offline_validation_commands"][:-1]

    findings = validate_packet(packet)

    assert any("offline_validation_commands missing required commands" in finding for finding in findings)


@pytest.mark.parametrize(
    "artifact_type",
    [
        "auth_state",
        "browser_context_storage",
        "browser_profile",
        "cookie_jar",
        "downloaded_document",
        "har",
        "raw_authenticated_html",
        "screenshot",
        "session_recording",
        "storage_state",
        "trace",
    ],
)
def test_validator_rejects_private_session_browser_raw_or_downloaded_artifact_outputs(artifact_type: str) -> None:
    packet = _packet()
    packet["created_artifacts"] = [{"artifact_type": artifact_type}]

    findings = validate_packet(packet)

    assert "created_artifacts must not include private/session/browser/raw/downloaded artifacts" in findings


def test_validator_rejects_missing_private_artifact_prohibition() -> None:
    packet = _packet()
    packet["prohibited_artifacts"] = [
        artifact for artifact in packet["prohibited_artifacts"] if artifact["artifact_type"] != "downloaded_document"
    ]

    findings = validate_packet(packet)

    assert any("prohibited_artifacts missing forbidden artifact types" in finding for finding in findings)


@pytest.mark.parametrize(
    "key, value, expected",
    [
        ("live_authenticated_claims", ["live authenticated DevHub observation completed"], "live_authenticated_claims must be absent or empty"),
        ("official_action_completion_claims", ["Permit application submitted"], "official_action_completion_claims must be absent or empty"),
        ("legal_or_permitting_guarantees", ["Permit approval is guaranteed"], "legal_or_permitting_guarantees must be absent or empty"),
    ],
)
def test_validator_rejects_explicit_claim_lists(key: str, value: object, expected: str) -> None:
    packet = _packet()
    packet[key] = value

    assert expected in validate_packet(packet)


@pytest.mark.parametrize(
    "claim, expected",
    [
        ("Authenticated DevHub session completed and verified.", "live authenticated claim text is not allowed"),
        ("Permit request submitted for this account.", "official-action completion claim text is not allowed"),
        ("Permit issuance is assured.", "legal or permitting guarantee text is not allowed"),
    ],
)
def test_validator_rejects_unsafe_claim_text(claim: str, expected: str) -> None:
    packet = _packet()
    packet["unsafe_claim"] = claim

    findings = validate_packet(packet)

    assert any(expected in finding for finding in findings)


@pytest.mark.parametrize(
    "flag",
    [
        "active_devhub_surface_mutation",
        "active_devhub_prompt_mutation",
        "active_devhub_guardrail_mutation",
        "active_devhub_source_mutation",
        "active_devhub_process_model_mutation",
        "active_devhub_contract_mutation",
        "active_devhub_release_state_mutation",
    ],
)
def test_validator_rejects_active_devhub_mutation_flags(flag: str) -> None:
    packet = deepcopy(_packet())
    packet[flag] = True

    assert f"{flag} must not be true" in validate_packet(packet)
