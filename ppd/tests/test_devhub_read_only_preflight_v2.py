from __future__ import annotations

import copy

import pytest

from ppd.devhub.read_only_preflight_v2 import (
    PACKET_VERSION,
    assert_attended_read_only_preflight_packet_v2,
    validate_attended_read_only_preflight_packet_v2,
)


def valid_packet() -> dict[str, object]:
    return {
        "version": PACKET_VERSION,
        "manual_login_readiness_checks": [
            "User-visible browser is ready for manual PortlandOregon.gov sign-in.",
            "User will complete password, CAPTCHA, and MFA prompts manually.",
        ],
        "allowed_read_only_destinations": [
            "DevHub Home read-only review",
            "My Permits & Requests read-only status review",
            "Permit details status message review",
            "Attachment list review",
        ],
        "attendance_statements": [
            "The user remains present for the full session.",
            "The worker stops if the user leaves or cannot review the visible page.",
        ],
        "redaction_requirements": [
            "Only redacted metadata and accessible UI labels may be recorded.",
            "Private field values, account identifiers, and payment details are omitted.",
        ],
        "abort_conditions": [
            "Abort before any submit, upload, certify, pay, schedule, cancel, or save action.",
            "Abort when a page requests credentials, CAPTCHA, MFA, or payment details.",
        ],
        "no_private_artifact_commitments": [
            "Do not persist authenticated page bodies or account-scoped values.",
            "Do not commit private session material or local browser outputs.",
        ],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "active_prompt_mutation": False,
        "active_guardrail_mutation": False,
        "active_devhub_surface_mutation": False,
        "active_source_mutation": False,
        "active_contract_mutation": False,
        "active_release_state_mutation": False,
    }


def test_accepts_valid_attended_read_only_preflight_packet_v2() -> None:
    result = validate_attended_read_only_preflight_packet_v2(valid_packet())

    assert result.ok, result.errors
    assert result.errors == ()
    assert_attended_read_only_preflight_packet_v2(valid_packet())


@pytest.mark.parametrize(
    "field",
    [
        "manual_login_readiness_checks",
        "allowed_read_only_destinations",
        "attendance_statements",
        "redaction_requirements",
        "abort_conditions",
        "no_private_artifact_commitments",
        "validation_commands",
    ],
)
def test_rejects_missing_required_readiness_sections(field: str) -> None:
    packet = valid_packet()
    packet.pop(field)

    result = validate_attended_read_only_preflight_packet_v2(packet)

    assert not result.ok
    assert any(field in error for error in result.errors)


@pytest.mark.parametrize(
    "field",
    [
        "active_prompt_mutation",
        "active_guardrail_mutation",
        "active_devhub_surface_mutation",
        "active_source_mutation",
        "active_contract_mutation",
        "active_release_state_mutation",
    ],
)
def test_rejects_active_mutation_flags(field: str) -> None:
    packet = valid_packet()
    packet[field] = True

    result = validate_attended_read_only_preflight_packet_v2(packet)

    assert not result.ok
    assert any(field in error for error in result.errors)


@pytest.mark.parametrize(
    "marker",
    [
        "auth_state",
        "storage_state",
        "session_state",
        "browser_state",
        "cookies",
        "local_storage",
        "session_storage",
        "trace",
        "har",
        "screenshot",
        "raw_html",
        "raw_crawl",
        "downloaded_documents",
        "downloads",
        "password",
        "credentials",
        "token",
    ],
)
def test_rejects_private_session_browser_raw_or_downloaded_artifacts(marker: str) -> None:
    packet = valid_packet()
    packet["artifact_plan"] = f"Persist {marker} for debugging."

    result = validate_attended_read_only_preflight_packet_v2(packet)

    assert not result.ok
    assert any(marker in error for error in result.errors)


@pytest.mark.parametrize(
    "claim",
    [
        "automated login will be used",
        "automate sign-in after opening DevHub",
        "fill password from the packet",
        "bypass captcha if prompted",
        "automate mfa prompts",
        "submit mfa code",
    ],
)
def test_rejects_automated_login_or_mfa_claims(claim: str) -> None:
    packet = valid_packet()
    packet["manual_login_readiness_checks"] = [claim]

    result = validate_attended_read_only_preflight_packet_v2(packet)

    assert not result.ok
    assert any("automated login" in error or "MFA" in error for error in result.errors)


@pytest.mark.parametrize(
    "claim",
    [
        "official action completed",
        "submitted permit",
        "payment completed",
        "inspection scheduled",
        "correction uploaded",
        "certified acknowledgement",
    ],
)
def test_rejects_official_action_completion_claims(claim: str) -> None:
    packet = valid_packet()
    packet["outcome"] = claim

    result = validate_attended_read_only_preflight_packet_v2(packet)

    assert not result.ok
    assert any("official-action completion" in error for error in result.errors)


@pytest.mark.parametrize(
    "claim",
    [
        "permit will be approved",
        "approval is certain",
        "legal advice is included",
        "compliance guaranteed",
        "permit guarantee",
    ],
)
def test_rejects_legal_or_permitting_guarantees(claim: str) -> None:
    packet = valid_packet()
    packet["guarantee"] = claim

    result = validate_attended_read_only_preflight_packet_v2(packet)

    assert not result.ok
    assert any("legal or permitting guarantees" in error for error in result.errors)


def test_rejects_write_destinations_in_allowed_read_only_destinations() -> None:
    packet = valid_packet()
    packet["allowed_read_only_destinations"] = ["Submit permit request"]

    result = validate_attended_read_only_preflight_packet_v2(packet)

    assert not result.ok
    assert any("read-only DevHub destination" in error for error in result.errors)
    assert any("write or official-action" in error for error in result.errors)


def test_assert_helper_raises_value_error_for_invalid_packet() -> None:
    packet = copy.deepcopy(valid_packet())
    packet["active_contract_mutation"] = True

    with pytest.raises(ValueError, match="active_contract_mutation"):
        assert_attended_read_only_preflight_packet_v2(packet)
