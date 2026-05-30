from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ppd.devhub.attended_observation_dry_run_runbook_v1 import (
    REQUIRED_ATTESTATIONS,
    REQUIRED_STOP_GATE_KINDS,
    AttendedObservationDryRunRunbookError,
    build_runbook_from_handoff_checklist,
    validate_runbook,
    validate_runbook_file,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "attended_observation_dry_run_runbook_v1"
SOURCE_CHECKLIST = Path(__file__).parent / "fixtures" / "attended_observation_handoff_checklist_v1" / "checklist_packet.json"


def _read(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_committed_runbook_fixture_is_valid() -> None:
    result = validate_runbook_file(FIXTURE_DIR / "runbook_packet.json")

    assert result.runbook_id == "fixture-first-attended-devhub-observation-dry-run-runbook-v1"
    assert result.step_count >= 4
    assert result.stop_gate_count >= len(REQUIRED_STOP_GATE_KINDS)
    assert result.attestation_count == len(REQUIRED_ATTESTATIONS)


def test_builder_converts_handoff_checklist_into_reviewer_ready_dry_run_steps() -> None:
    runbook = build_runbook_from_handoff_checklist(_read(SOURCE_CHECKLIST))
    result = validate_runbook(runbook)

    assert result.step_count >= 4
    assert runbook["source_handoff_checklist"]["converted_fixture_first"] is True
    assert runbook["manual_login_boundaries"]["manual_login_only"] is True
    assert runbook["manual_login_boundaries"]["automation_may_enter_credentials"] is False
    assert runbook["read_only_page_evidence_expectations"]


def test_requires_manual_login_boundaries_without_captcha_mfa_or_account_creation() -> None:
    runbook = _read(FIXTURE_DIR / "runbook_packet.json")
    broken = deepcopy(runbook)
    broken["manual_login_boundaries"]["automation_may_handle_captcha"] = True
    broken["manual_login_boundaries"]["automation_may_handle_mfa"] = True
    broken["manual_login_boundaries"]["automation_may_create_account"] = True

    with pytest.raises(AttendedObservationDryRunRunbookError, match="automation_may_handle_captcha must be false"):
        validate_runbook(broken)


def test_requires_read_only_page_evidence_without_raw_values_or_screenshots() -> None:
    runbook = _read(FIXTURE_DIR / "runbook_packet.json")
    broken = deepcopy(runbook)
    evidence = broken["read_only_page_evidence_expectations"]
    assert isinstance(evidence, list)
    first = evidence[0]
    assert isinstance(first, dict)
    first["raw_values_allowed"] = True
    first["screenshots_allowed"] = True

    with pytest.raises(AttendedObservationDryRunRunbookError, match="raw_values_allowed must be false"):
        validate_runbook(broken)


@pytest.mark.parametrize("action_kind", REQUIRED_STOP_GATE_KINDS)
def test_requires_each_exact_stop_before_action_gate(action_kind: str) -> None:
    runbook = _read(FIXTURE_DIR / "runbook_packet.json")
    broken = deepcopy(runbook)
    gates = broken["stop_before_action_gates"]
    assert isinstance(gates, list)
    broken["stop_before_action_gates"] = [gate for gate in gates if isinstance(gate, dict) and gate.get("action_kind") != action_kind]

    with pytest.raises(AttendedObservationDryRunRunbookError, match=f"stop_before_action_gates missing {action_kind}"):
        validate_runbook(broken)


@pytest.mark.parametrize("attestation", REQUIRED_ATTESTATIONS)
def test_requires_each_no_automation_attestation(attestation: str) -> None:
    runbook = _read(FIXTURE_DIR / "runbook_packet.json")
    broken = deepcopy(runbook)
    broken["attestations"][attestation] = False

    with pytest.raises(AttendedObservationDryRunRunbookError, match=f"attestations.{attestation} must be true"):
        validate_runbook(broken)


def test_rejects_private_browser_artifacts_and_live_action_claims() -> None:
    runbook = _read(FIXTURE_DIR / "runbook_packet.json")
    broken = deepcopy(runbook)
    broken["storage_state"] = "playwright/.auth/devhub.json"
    broken["dry_run_steps"][0]["reviewer_actions"].append("Automation uploaded and submitted the permit application.")

    with pytest.raises(AttendedObservationDryRunRunbookError, match="forbidden private/browser artifact"):
        validate_runbook(broken)
