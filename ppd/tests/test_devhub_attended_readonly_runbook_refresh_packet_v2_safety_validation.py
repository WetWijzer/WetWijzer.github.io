from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from ppd.devhub.attended_readonly_runbook_refresh_packet_v2_safety_validation import (
    validate_attended_readonly_runbook_refresh_packet_v2_safety,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub_attended_readonly_runbook_refresh_packet_v2"
    / "expected_packet.json"
)


def _packet() -> dict:
    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _errors(packet: dict) -> tuple[str, ...]:
    return validate_attended_readonly_runbook_refresh_packet_v2_safety(packet)


def test_valid_fixture_passes_safety_validation() -> None:
    assert _errors(_packet()) == ()


def test_rejects_uncited_checklist_deltas() -> None:
    packet = _packet()
    packet["operator_checklist_deltas"][0]["citations"] = []

    assert any("operator_checklist_deltas[0].citations" in error for error in _errors(packet))


def test_rejects_missing_manual_handoff_boundaries() -> None:
    packet = _packet()
    packet["manual_login_mfa_captcha_handoff_boundaries"] = packet["manual_login_mfa_captcha_handoff_boundaries"][1:]

    assert any("manual login/MFA/CAPTCHA handoff boundary" in error for error in _errors(packet))


def test_rejects_private_or_authenticated_values() -> None:
    packet = _packet()
    packet["operator_checklist_deltas"][0]["review_note"] = "permit number: 24-123456"

    assert any("private or authenticated values" in error for error in _errors(packet))


def test_rejects_session_auth_and_browser_artifacts() -> None:
    packet = _packet()
    packet["redaction_requirements"][0]["review_note"] = "Stored screenshot.png and auth state at /home/operator/devhub/auth_state.json."

    errors = _errors(packet)
    assert any("artifact" in error for error in errors)
    assert any("auth state" in error or "screenshot" in error for error in errors)


def test_rejects_live_devhub_browser_execution_claims() -> None:
    packet = _packet()
    packet["allowed_read_only_verification_steps"][0]["operator_note"] = "Playwright opened the live DevHub browser and captured the status card."

    assert any("live DevHub or browser execution" in error for error in _errors(packet))


def test_rejects_credential_mfa_captcha_automation_language() -> None:
    packet = _packet()
    packet["manual_login_mfa_captcha_handoff_boundaries"][0]["trigger"] = "Agent automated MFA and solved CAPTCHA during login."

    assert any("credential, MFA, CAPTCHA, or login automation" in error for error in _errors(packet))


def test_rejects_legal_or_permitting_outcome_guarantees() -> None:
    packet = _packet()
    packet["operator_checklist_deltas"][0]["operator_checklist_text"] = "This runbook will ensure permit approval."

    assert any("legal compliance or permitting outcomes" in error for error in _errors(packet))


def test_rejects_consequential_action_enablement() -> None:
    packet = _packet()
    packet["allowed_read_only_verification_steps"][0]["allowed_operator_actions"].append("Click submit to complete the upload.")

    assert any("consequential DevHub actions" in error for error in _errors(packet))


def test_rejects_active_mutation_flags() -> None:
    packet = _packet()
    mutated = deepcopy(packet["attestations"])
    mutated.update(
        {
            "active_runbook_mutation": True,
            "active_surface_registry_mutation": True,
            "active_guardrail_mutation": True,
            "active_prompt_mutation": True,
            "active_monitoring_mutation": True,
            "active_release_state_mutation": True,
            "active_agent_state_mutation": True,
        }
    )
    packet["attestations"] = mutated

    assert any("active runbook, surface-registry, guardrail, prompt" in error for error in _errors(packet))
