from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.daemon.post_recompile_agent_readiness_replay_v4 import (
    assert_post_recompile_agent_readiness_replay_v4,
    validate_post_recompile_agent_readiness_replay_v4,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "post_recompile_agent_readiness_replay_v4"


def _load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def test_replay_v4_accepts_complete_safe_packet() -> None:
    packet = _load_fixture("valid_packet.json")

    result = validate_post_recompile_agent_readiness_replay_v4(packet)

    assert result.ok is True
    assert result.errors == ()
    assert_post_recompile_agent_readiness_replay_v4(packet)


@pytest.mark.parametrize(
    ("field_name", "expected_error"),
    [
        ("reviewer_packet_refs", "missing reviewer packet references"),
        ("synthetic_agent_request_fixtures", "missing synthetic agent request fixtures"),
        ("affected_missing_information_prompts", "missing affected missing-information prompts"),
        ("blocked_stale_evidence_paths", "missing blocked stale-evidence paths"),
        ("blocked_consequential_or_financial_actions", "missing blocked consequential or financial actions"),
        ("reversible_draft_only_next_actions", "missing reversible draft-only next actions"),
        ("explanation_template_coverage", "missing explanation-template coverage"),
        ("manual_handoff_reminders", "missing manual handoff reminders"),
        ("rollback_notes", "missing rollback notes"),
        ("validation_commands", "missing validation commands"),
    ],
)
def test_replay_v4_rejects_missing_required_readiness_sections(
    field_name: str,
    expected_error: str,
) -> None:
    packet = _load_fixture("valid_packet.json")
    packet[field_name] = []

    result = validate_post_recompile_agent_readiness_replay_v4(packet)

    assert result.ok is False
    assert expected_error in result.errors


def test_replay_v4_rejects_private_session_or_auth_artifacts() -> None:
    packet = _load_fixture("valid_packet.json")
    packet["reviewer_packet_refs"].append("artifacts/devhub_session_storage_state.json")

    result = validate_post_recompile_agent_readiness_replay_v4(packet)

    assert result.ok is False
    assert any("private/session/auth artifact" in error for error in result.errors)


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "The agent will submit the permit request after replay.",
        "This package says approval guaranteed for the applicant.",
    ],
)
def test_replay_v4_rejects_official_action_claims_and_guarantees(unsafe_text: str) -> None:
    packet = _load_fixture("valid_packet.json")
    packet["explanation_template_coverage"]["unsafe_template"] = unsafe_text

    result = validate_post_recompile_agent_readiness_replay_v4(packet)

    assert result.ok is False


def test_replay_v4_rejects_active_mutation_flags() -> None:
    packet = _load_fixture("valid_packet.json")
    packet["runtime_controls"] = {"submit_enabled": True}

    result = validate_post_recompile_agent_readiness_replay_v4(packet)

    assert result.ok is False
    assert any("active mutation flag" in error for error in result.errors)


def test_replay_v4_assertion_raises_with_rejection_reasons() -> None:
    packet = _load_fixture("valid_packet.json")
    packet["validation_commands"] = []

    with pytest.raises(ValueError, match="missing validation commands"):
        assert_post_recompile_agent_readiness_replay_v4(packet)
