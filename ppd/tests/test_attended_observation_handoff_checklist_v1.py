from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ppd.devhub.attended_observation_handoff_checklist_v1 import (
    build_attended_observation_handoff_checklist,
    validate_attended_observation_handoff_checklist,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "attended_observation_handoff_checklist_v1"


def _read(name: str) -> dict[str, object]:
    data = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _sources() -> tuple[dict[str, object], dict[str, object]]:
    data = _read("source_packets.json")
    return data["devhub_read_only_observation_rehearsal_v1"], data["action_classification_fixture"]


def test_committed_checklist_fixture_is_valid() -> None:
    packet = _read("checklist_packet.json")

    assert validate_attended_observation_handoff_checklist(packet) == ()
    assert packet["fixture_first"] is True
    assert packet["offline_only"] is True
    assert packet["devhub_launched"] is False
    assert packet["browser_automation_performed"] is False


def test_builder_consumes_observation_rehearsal_and_action_classification_fixtures() -> None:
    packet = build_attended_observation_handoff_checklist(*_sources())

    assert validate_attended_observation_handoff_checklist(packet) == ()
    assert packet["source_packets"]["devhub_read_only_observation_rehearsal_v1"]["consumed"] is True
    assert packet["source_packets"]["action_classification_fixture"]["consumed"] is True
    assert packet["visible_ui_evidence_expectations"]
    assert packet["redaction_checks"]
    assert packet["attendance_checkpoints"]
    assert packet["rollback_notes"]


def test_stop_gates_cover_upload_submit_payment_and_scheduling_without_execution() -> None:
    packet = build_attended_observation_handoff_checklist(*_sources())
    gates = {gate["action_kind"]: gate for gate in packet["stop_before_action_gates"]}

    for action_kind in ("upload", "submit", "payment", "scheduling"):
        assert gates[action_kind]["stop_before_action"] is True
        assert gates[action_kind]["requires_attendance"] is True
        assert gates[action_kind]["requires_exact_confirmation"] is True
        assert gates[action_kind]["automated_execution_allowed"] is False


def test_rejects_missing_ui_evidence_redaction_and_attendance_checkpoints() -> None:
    packet = build_attended_observation_handoff_checklist(*_sources())
    broken = deepcopy(packet)
    broken["visible_ui_evidence_expectations"] = []
    broken["attendance_checkpoints"] = []
    broken["redaction_checks"] = [row for row in broken["redaction_checks"] if row["check_id"] != "no_auth_state"]

    errors = validate_attended_observation_handoff_checklist(broken)

    assert "visible_ui_evidence_expectations must be non-empty" in errors
    assert "attendance_checkpoints must be non-empty" in errors
    assert "redaction_checks missing no_auth_state" in errors


def test_rejects_missing_attestations_and_redaction_checks() -> None:
    packet = build_attended_observation_handoff_checklist(*_sources())
    broken = deepcopy(packet)
    broken["attestations"]["no_payment"] = False
    broken["redaction_checks"] = [row for row in broken["redaction_checks"] if row["check_id"] != "no_auth_state"]

    errors = validate_attended_observation_handoff_checklist(broken)

    assert "attestations.no_payment must be true" in errors
    assert "redaction_checks missing no_auth_state" in errors


def test_rejects_browser_session_private_artifacts_and_live_action_claims() -> None:
    packet = build_attended_observation_handoff_checklist(*_sources())
    broken = deepcopy(packet)
    broken["storage_state"] = "playwright/.auth/devhub.json"
    broken["manual_observation_checklists"][0]["items"].append("Reviewer clicked through and submitted the application.")

    errors = validate_attended_observation_handoff_checklist(broken)

    assert any("forbidden private/browser artifact" in error for error in errors)
    assert any("claims live login, click-through, upload, submit" in error for error in errors)


def test_rejects_private_account_values_and_write_capable_flags() -> None:
    packet = build_attended_observation_handoff_checklist(*_sources())
    broken = deepcopy(packet)
    broken["visible_ui_evidence_expectations"][0]["account_email"] = "owner@example.test"
    broken["manual_observation_checklists"][0]["write_capable"] = True

    errors = validate_attended_observation_handoff_checklist(broken)

    assert any("forbidden private account value" in error for error in errors)
    assert any("write-capable action flag" in error for error in errors)


def test_rejects_unsafe_official_action_language_outside_stop_gates() -> None:
    packet = build_attended_observation_handoff_checklist(*_sources())
    broken = deepcopy(packet)
    broken["manual_observation_checklists"][0]["items"].append("Certify the acknowledgement, upload the correction PDF, pay fees, schedule inspection, and cancel if needed.")

    errors = validate_attended_observation_handoff_checklist(broken)

    assert any("unsafe certification, submission, payment, upload, scheduling, or cancellation language" in error for error in errors)


def test_rejects_active_mutation_flags_and_text() -> None:
    packet = build_attended_observation_handoff_checklist(*_sources())
    broken = deepcopy(packet)
    broken["active_devhub_mutation"] = True
    broken["rollback_notes"].append({"note_id": "bad", "manual_only": True, "note": "Enable active surface-registry mutation after review."})

    errors = validate_attended_observation_handoff_checklist(broken)

    assert any("active DevHub, surface-registry, guardrail, prompt, release-state, or agent-state mutation flag" in error for error in errors)
    assert any("active DevHub, surface-registry, guardrail, prompt, release-state, or agent-state mutation text" in error for error in errors)


@pytest.mark.parametrize("attestation", ["no_login_automation", "no_session_state", "no_click_through", "no_upload", "no_submit", "no_payment", "no_scheduling"])
def test_requires_each_no_automation_attestation(attestation: str) -> None:
    packet = build_attended_observation_handoff_checklist(*_sources())
    packet["attestations"][attestation] = False

    assert f"attestations.{attestation} must be true" in validate_attended_observation_handoff_checklist(packet)
