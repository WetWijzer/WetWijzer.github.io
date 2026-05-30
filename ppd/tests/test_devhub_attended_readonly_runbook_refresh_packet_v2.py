from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.devhub.attended_readonly_runbook_refresh_packet_v2 import (
    OFFLINE_VALIDATION_COMMANDS,
    REQUIRED_ATTESTATIONS,
    build_from_fixture_paths,
    validate_devhub_attended_readonly_runbook_refresh_packet_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"
RUNBOOK_REFRESH_DIR = FIXTURE_DIR / "devhub_attended_readonly_runbook_refresh_packet_v2"
SURFACE_ACCEPTANCE_DIR = FIXTURE_DIR / "surface_registry_refresh_acceptance_packet_v2"
LAUNCH_READINESS_DIR = FIXTURE_DIR / "devhub_attended_read_only_pilot_launch_readiness"


def _load_fixture(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_packet() -> dict:
    return build_from_fixture_paths(
        SURFACE_ACCEPTANCE_DIR / "expected_surface_registry_refresh_acceptance_packet_v2.json",
        SURFACE_ACCEPTANCE_DIR / "devhub_attended_readonly_observation_packet_v2.json",
        LAUNCH_READINESS_DIR / "launch_readiness_packet.json",
    )


def test_builds_expected_devhub_attended_readonly_runbook_refresh_packet_v2() -> None:
    assert _build_packet() == _load_fixture(RUNBOOK_REFRESH_DIR / "expected_packet.json")


def test_runbook_refresh_packet_contains_required_deltas_steps_boundaries_and_redactions() -> None:
    packet = _build_packet()

    validate_devhub_attended_readonly_runbook_refresh_packet_v2(packet)

    assert [delta["decision"] for delta in packet["operator_checklist_deltas"]] == ["accepted", "deferred", "rejected"]
    assert [step["step_id"] for step in packet["allowed_read_only_verification_steps"]] == [
        "verify:update:devhub-home-readonly-status-card",
        "verify:update:my-permits-filter-selector",
    ]
    assert all(step["read_only"] is True for step in packet["allowed_read_only_verification_steps"])
    assert all(step["official_action_allowed"] is False for step in packet["allowed_read_only_verification_steps"])
    assert packet["manual_login_mfa_captcha_handoff_boundaries"][0]["agent_may_automate_mfa_or_captcha"] is False
    assert all(requirement["private_values_allowed"] is False for requirement in packet["redaction_requirements"])
    assert all(requirement["browser_artifacts_allowed"] is False for requirement in packet["redaction_requirements"])


def test_runbook_refresh_packet_contains_attestations_and_offline_validation_commands() -> None:
    packet = _build_packet()

    assert packet["attestations"] == {name: True for name in REQUIRED_ATTESTATIONS}
    assert packet["offline_validation_commands"] == [list(command) for command in OFFLINE_VALIDATION_COMMANDS]


def test_runbook_refresh_validator_rejects_missing_citations() -> None:
    packet = _build_packet()
    packet["operator_checklist_deltas"][0]["citations"] = []

    with pytest.raises(ValueError, match="citations must not be empty"):
        validate_devhub_attended_readonly_runbook_refresh_packet_v2(packet)


def test_runbook_refresh_validator_rejects_boundary_that_allows_mfa_or_captcha_automation() -> None:
    packet = _build_packet()
    packet["manual_login_mfa_captcha_handoff_boundaries"][0]["agent_may_automate_mfa_or_captcha"] = True

    with pytest.raises(ValueError, match="MFA or CAPTCHA automation"):
        validate_devhub_attended_readonly_runbook_refresh_packet_v2(packet)
