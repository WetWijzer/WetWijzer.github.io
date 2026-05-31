from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.agent_readiness.inactive_activation_rehearsal_v2 import (
    PACKET_TYPE,
    build_inactive_activation_rehearsal_v2,
    validate_inactive_activation_rehearsal_v2,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "inactive_activation_rehearsal_v2" / "approved_release_decision_packet_v2.json"


def _approved_decision_packet() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _valid_packet() -> dict[str, object]:
    return build_inactive_activation_rehearsal_v2(_approved_decision_packet())


def _codes(packet: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_inactive_activation_rehearsal_v2(packet).issues}


def test_builds_no_op_activation_rehearsal_from_approved_decision_fixture() -> None:
    packet = _valid_packet()

    assert packet["packet_type"] == PACKET_TYPE
    assert packet["fixture_only"] is True
    assert packet["no_op_activation_plan"] is True
    assert packet["source_release_decision_packet"]["approved"] is True
    assert packet["target_inactive_bundle_ids"] == [
        "inactive-fixture-guarded-agent-release-bundle-v2",
        "inactive-fixture-offline-release-gate-bundle-v2",
    ]
    assert packet["offline_validation_commands"] == [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ["python3", "-m", "pytest", "ppd/tests/test_inactive_activation_rehearsal_v2.py"],
    ]

    result = validate_inactive_activation_rehearsal_v2(packet)
    assert result.ok, result.as_dict()


def test_rehearsal_expected_active_state_diffs_are_no_change_only() -> None:
    packet = _valid_packet()

    diffs = packet["expected_active_state_diffs"]
    assert diffs
    assert {row["expected_diff"] for row in diffs} == {"no_change"}
    assert {row["status"] for row in diffs} == {"placeholder_only"}

    broken = copy.deepcopy(packet)
    broken["expected_active_state_diffs"][0]["expected_diff"] = "replace_active_state"
    result = validate_inactive_activation_rehearsal_v2(broken)

    assert not result.ok
    assert any(issue.code == "invalid_expected_active_state_diff" for issue in result.issues)


def test_rehearsal_rejects_non_approved_release_decision_packet() -> None:
    decision_packet = _approved_decision_packet()
    decision_packet["decision_rows"][0]["decision"] = "hold"

    with pytest.raises(ValueError, match="only approved"):
        build_inactive_activation_rehearsal_v2(decision_packet)


def test_rehearsal_keeps_smoke_checks_as_placeholders() -> None:
    packet = _valid_packet()

    placeholders = packet["post_activation_smoke_check_placeholders"]
    assert placeholders
    assert all(row["status"] == "placeholder_only" for row in placeholders)
    assert all(row["result"] is None for row in placeholders)


def test_rehearsal_attestations_block_mutation_surfaces() -> None:
    packet = _valid_packet()

    attestations = packet["no_op_attestations"]
    assert attestations == {
        "changes_active_release_state": False,
        "changes_prompts": False,
        "changes_guardrails": False,
        "changes_source_registries": False,
        "changes_process_models": False,
        "changes_contracts": False,
        "changes_devhub_surfaces": False,
        "uses_live_sources": False,
        "accesses_devhub": False,
        "performs_official_actions": False,
    }

    broken = copy.deepcopy(packet)
    broken["no_op_attestations"]["changes_prompts"] = True
    result = validate_inactive_activation_rehearsal_v2(broken)

    assert not result.ok
    assert any(issue.code == "invalid_no_op_attestation" for issue in result.issues)


@pytest.mark.parametrize(
    ("section", "expected_code"),
    [
        ("preflight_checkpoints", "missing_required_section"),
        ("target_inactive_bundle_ids", "missing_required_section"),
        ("expected_active_state_diffs", "missing_required_section"),
        ("rollback_rehearsal_references", "missing_required_section"),
        ("post_activation_smoke_check_placeholders", "missing_required_section"),
        ("offline_validation_commands", "missing_required_section"),
    ],
)
def test_rehearsal_rejects_missing_required_sections(section: str, expected_code: str) -> None:
    packet = _valid_packet()
    packet[section] = []

    assert expected_code in _codes(packet)


@pytest.mark.parametrize(
    ("section", "id_key", "expected_code"),
    [
        ("preflight_checkpoints", "checkpoint_id", "missing_preflight_checkpoint"),
        ("rollback_rehearsal_references", "reference_id", "missing_rollback_reference"),
        ("post_activation_smoke_check_placeholders", "placeholder_id", "missing_smoke_placeholder"),
    ],
)
def test_rehearsal_rejects_missing_required_named_rows(section: str, id_key: str, expected_code: str) -> None:
    packet = _valid_packet()
    removed_id = packet[section][0][id_key]
    packet[section] = [row for row in packet[section] if row[id_key] != removed_id]

    assert expected_code in _codes(packet)


def test_rehearsal_rejects_target_bundle_ids_that_are_not_inactive() -> None:
    packet = _valid_packet()
    packet["target_inactive_bundle_ids"] = ["active-release-bundle-v2"]

    assert "invalid_target_inactive_bundle_id" in _codes(packet)


def test_rehearsal_rejects_missing_active_state_diff_component_coverage() -> None:
    packet = _valid_packet()
    packet["expected_active_state_diffs"] = packet["expected_active_state_diffs"][1:]

    assert "missing_active_state_diff_coverage" in _codes(packet)


@pytest.mark.parametrize(
    "command",
    [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ["python3", "-m", "pytest", "ppd/tests/test_inactive_activation_rehearsal_v2.py"],
    ],
)
def test_rehearsal_rejects_missing_exact_offline_validation_commands(command: list[str]) -> None:
    packet = _valid_packet()
    packet["offline_validation_commands"] = [row for row in packet["offline_validation_commands"] if row != command]

    assert "missing_validation_command" in _codes(packet)


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    [
        ("session_state", "session storage state file", "private_or_raw_artifact_field"),
        ("browser_trace", "trace file", "private_or_raw_artifact_field"),
        ("raw_crawl_output", "raw crawl html", "private_or_raw_artifact_field"),
        ("downloaded_document", "downloaded permit pdf", "private_or_raw_artifact_field"),
        ("notes", "opened DevHub and completed a live crawl", "unsafe_text"),
        ("completion_claim", "official action completed and permit submitted", "unsafe_text"),
        ("guarantee", "permit approval is assured and legally valid", "unsafe_text"),
        ("active_mutation", True, "active_mutation_flag"),
        ("updates_guardrails", True, "active_mutation_flag"),
    ],
)
def test_rehearsal_rejects_forbidden_artifacts_claims_guarantees_and_mutation_flags(
    field: str,
    value: object,
    expected_code: str,
) -> None:
    packet = _valid_packet()
    packet[field] = value

    assert expected_code in _codes(packet)


def test_rehearsal_rejects_unsafe_validation_commands() -> None:
    packet = _valid_packet()
    packet["offline_validation_commands"].append(["python3", "-m", "ppd.devhub.live_run"])

    assert "unsafe_validation_command" in _codes(packet)
