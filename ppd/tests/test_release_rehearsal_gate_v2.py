from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.release_rehearsal_gate_v2 import (
    MANUAL_ONLY_GATES,
    PACKET_VERSION,
    build_release_rehearsal_gate_v2,
    build_release_rehearsal_gate_v2_from_fixture,
    validate_release_rehearsal_gate_v2,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "release_rehearsal_gate_v2" / "inputs.json"


def _packet() -> dict:
    return build_release_rehearsal_gate_v2_from_fixture(FIXTURE_PATH)


def test_release_rehearsal_gate_v2_builds_cited_pass_and_block_rows() -> None:
    packet = _packet()
    rows = {row["artifact_id"]: row for row in packet["gate_rows"]}

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["overall_gate_status"] == "blocked"
    assert rows["inactive-preview-alpha"]["decision"] == "pass"
    assert rows["inactive-preview-beta"]["decision"] == "block"
    assert "reviewer:alpha:approved" in rows["inactive-preview-alpha"]["citations"]
    assert "preview:beta:source-evidence" in rows["inactive-preview-beta"]["citations"]
    assert validate_release_rehearsal_gate_v2(packet).ok


def test_release_rehearsal_gate_v2_includes_manual_gates_commands_rollbacks_and_handoff() -> None:
    packet = _packet()

    assert {gate["gate_id"] for gate in packet["manual_only_gates"]} == set(MANUAL_ONLY_GATES)
    assert all(gate["manual_only"] is True for gate in packet["manual_only_gates"])
    assert all(set(row["manual_only_gate_refs"]) == set(MANUAL_ONLY_GATES) for row in packet["gate_rows"])
    assert ["python3", "-m", "py_compile", "ppd/release_rehearsal_gate_v2.py"] in packet["validation_replay_commands"]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["validation_replay_commands"]
    assert packet["rollback_checkpoints"]
    assert packet["handoff_notes"]


def test_release_rehearsal_gate_v2_attests_no_live_auth_official_financial_or_promotion_actions() -> None:
    attestations = _packet()["attestations"]

    assert attestations == {
        "fixture_first": True,
        "no_live_execution": True,
        "no_authenticated_devhub_session": True,
        "no_private_artifacts": True,
        "no_official_actions": True,
        "no_financial_actions": True,
        "no_artifact_promotion": True,
    }


def test_release_rehearsal_gate_v2_rejects_uncited_rows_missing_manual_gates_commands_rollbacks_and_handoff() -> None:
    broken = _packet()
    broken["gate_rows"][0]["citations"] = []
    broken["manual_only_gates"] = []
    broken["validation_replay_commands"] = []
    broken["rollback_checkpoints"] = []
    broken["handoff_notes"] = []

    result = validate_release_rehearsal_gate_v2(broken)

    assert not result.ok
    joined = "; ".join(result.errors)
    assert "gate_rows[0].citations must be non-empty" in joined
    assert "manual_only_gates must include every required manual-only gate" in joined
    assert "validation_replay_commands must be a non-empty list of command lists" in joined
    assert "rollback_checkpoints must be non-empty" in joined
    assert "handoff_notes must be non-empty" in joined


def test_release_rehearsal_gate_v2_requires_pass_and_block_rows() -> None:
    broken = _packet()
    broken["gate_rows"] = [row for row in broken["gate_rows"] if row["decision"] == "pass"]

    result = validate_release_rehearsal_gate_v2(broken)

    assert not result.ok
    assert "gate_rows must include pass and block decisions" in "; ".join(result.errors)


def test_release_rehearsal_gate_v2_rejects_private_authenticated_raw_session_browser_live_promotion_and_mutation_material() -> None:
    unsafe_cases = [
        ("auth_state", "state.json"),
        ("authenticated_artifact", "private account value"),
        ("browser_artifact", "trace.zip"),
        ("devhub_session", "session value"),
        ("downloaded_data", "downloaded fixture body"),
        ("downloaded_document", "download.pdf"),
        ("pdf_artifact", "raw PDF file"),
        ("raw_body", "html body"),
        ("raw_crawl", "crawl output"),
        ("raw_pdf", "%PDF"),
        ("session_state", "state.json"),
        ("storage_state", "storage.json"),
        ("note", "active promotion is complete"),
        ("active_source_mutation", True),
        ("active_document_mutation", True),
        ("active_requirement_mutation", True),
        ("active_process_mutation", True),
        ("active_guardrail_mutation", True),
        ("active_prompt_mutation", True),
        ("active_release_state_mutation", True),
        ("active_agent_state_mutation", True),
        ("promotion_executed", True),
        ("official_action_performed", True),
        ("financial_action_performed", True),
    ]

    for key, value in unsafe_cases:
        packet = _packet()
        packet[key] = value
        result = validate_release_rehearsal_gate_v2(packet)
        assert not result.ok, key


def test_release_rehearsal_gate_v2_rejects_nested_active_mutation_flags() -> None:
    for flag in ("source", "document", "requirement", "process", "guardrail", "prompt", "release_state", "agent_state"):
        packet = _packet()
        packet["mutation_flags"] = {flag: "enabled"}

        result = validate_release_rehearsal_gate_v2(packet)

        assert not result.ok, flag
        assert "mutation_flags" in "; ".join(result.errors)


def test_release_rehearsal_gate_v2_rejects_outcome_guarantees_and_consequential_language() -> None:
    unsafe_notes = [
        "approval guaranteed",
        "city will approve",
        "legal outcome is guaranteed",
        "permit will be approved",
        "click submit",
        "submit the permit application",
        "upload corrections",
        "enter payment",
        "final payment",
        "purchase permit",
        "schedule inspection",
        "certify acknowledgement",
        "cancel permit",
        "withdraw application",
        "request extension",
        "reactivate permit",
    ]

    for note in unsafe_notes:
        packet = _packet()
        packet["gate_rows"][0]["note"] = note
        result = validate_release_rehearsal_gate_v2(packet)
        assert not result.ok, note


def test_release_rehearsal_gate_v2_rejects_missing_required_inputs() -> None:
    with pytest.raises(ValueError, match="missing required release rehearsal gate inputs"):
        build_release_rehearsal_gate_v2({})


def test_release_rehearsal_gate_v2_rejects_missing_consumed_version_reference() -> None:
    packet = _packet()
    broken = deepcopy(packet)
    broken["consumes"]["reviewer_disposition_packet_v2"] = ""

    result = validate_release_rehearsal_gate_v2(broken)

    assert not result.ok
    assert "consumes.reviewer_disposition_packet_v2 must be present" in "; ".join(result.errors)
