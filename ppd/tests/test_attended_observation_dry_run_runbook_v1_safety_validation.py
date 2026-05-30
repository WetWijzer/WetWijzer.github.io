from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from ppd.devhub.attended_observation_dry_run_runbook_v1_safety_validation import (
    assert_attended_observation_dry_run_runbook_v1_safe,
    validate_attended_observation_dry_run_runbook_v1_safety,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "attended_observation_dry_run_runbook_v1"


def _runbook() -> dict[str, Any]:
    data = json.loads((FIXTURE_DIR / "runbook_packet.json").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_committed_attended_observation_dry_run_runbook_v1_is_safety_valid() -> None:
    runbook = _runbook()

    assert validate_attended_observation_dry_run_runbook_v1_safety(runbook) == ()
    assert_attended_observation_dry_run_runbook_v1_safe(runbook)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("automation_may_enter_credentials", "automated login"),
        ("automation_may_handle_captcha", "security handling"),
        ("automation_may_handle_mfa", "security handling"),
        ("automation_may_create_account", "security handling"),
    ],
)
def test_rejects_automated_login_captcha_mfa_and_account_creation_flags(field: str, message: str) -> None:
    runbook = _runbook()
    runbook["manual_login_boundaries"][field] = True

    errors = validate_attended_observation_dry_run_runbook_v1_safety(runbook)

    assert any(message in error or field in error for error in errors)


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "Automate login and enter credentials for the user.",
        "Solve CAPTCHA and complete MFA before continuing.",
        "Create account if the user does not already have one.",
        "Click submit to submit application after review.",
        "Upload document and attach file to the official record.",
        "Pay fees and submit payment in DevHub.",
        "Schedule inspection for the permit.",
        "Certify acknowledgement and complete certification.",
        "Cancel request from the DevHub case page.",
        "This is a write-capable action and may click through.",
    ],
)
def test_rejects_unsafe_instruction_language(unsafe_text: str) -> None:
    runbook = _runbook()
    runbook["dry_run_steps"][0]["reviewer_actions"].append(unsafe_text)

    errors = validate_attended_observation_dry_run_runbook_v1_safety(runbook)

    assert errors


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("private_account_value", "Account number: 123456"),
        ("session_file", "storage_state.json"),
        ("auth_state_path", "playwright/.auth/devhub.json"),
        ("screenshot_path", "/home/example/devhub.png"),
        ("trace_path", "trace.zip"),
        ("har_path", "network.har"),
        ("raw_authenticated_value", "Permit number: 24-000000"),
    ],
)
def test_rejects_private_account_values_and_browser_artifacts(key: str, value: str) -> None:
    runbook = _runbook()
    runbook[key] = value

    errors = validate_attended_observation_dry_run_runbook_v1_safety(runbook)

    assert any("private account" in error or "session" in error or "screenshot" in error or "HAR" in error for error in errors)


@pytest.mark.parametrize(
    "flag",
    [
        "devhub_mutation_enabled",
        "surface_registry_mutation_enabled",
        "guardrail_write_enabled",
        "prompt_update_enabled",
        "release_state_mutation_enabled",
        "agent_state_write_enabled",
    ],
)
def test_rejects_active_mutation_flags(flag: str) -> None:
    runbook = _runbook()
    runbook["mutation_flags"] = {flag: True}

    errors = validate_attended_observation_dry_run_runbook_v1_safety(runbook)

    assert any("mutation flag" in error for error in errors)


def test_rejects_enabled_stop_gate_execution() -> None:
    runbook = deepcopy(_runbook())
    runbook["stop_before_action_gates"][0]["automated_execution_allowed"] = True

    errors = validate_attended_observation_dry_run_runbook_v1_safety(runbook)

    assert any("automated_execution_allowed must be false" in error for error in errors)
