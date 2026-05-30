from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.agent_readiness.release_rollback_rehearsal_packet_v1 import (
    PACKET_TYPE,
    build_release_rollback_rehearsal_packet_v1,
    validate_release_rollback_rehearsal_packet_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_readiness" / "inactive_release_decision_packet_v2.json"


def _load_fixture() -> dict[str, object]:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_builds_release_rollback_rehearsal_packet_v1_from_inactive_decision_fixture() -> None:
    packet = build_release_rollback_rehearsal_packet_v1(_load_fixture())

    assert packet["packet_type"] == PACKET_TYPE
    assert packet["fixture_only"] is True
    assert packet["rollback_rehearsal_only"] is True
    assert [row["source_decision"] for row in packet["ordered_rollback_scenario_rows"]] == ["approve", "hold"]
    assert [row["sequence"] for row in packet["ordered_rollback_scenario_rows"]] == [1, 2]
    assert packet["affected_inactive_fixture_family_inventory"]
    assert packet["pre_rollback_validation_commands"] == [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ["python3", "-m", "pytest", "ppd/tests/test_inactive_release_decision_packet_v2.py"],
    ]
    assert packet["post_rollback_validation_commands"] == [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ["python3", "-m", "pytest", "ppd/tests/test_release_rollback_rehearsal_packet_v1.py"],
    ]
    assert packet["reviewer_acknowledgement_placeholders"]
    assert packet["residual_risk_notes"]
    assert packet["rollback_rehearsal_attestations"] == {
        "modifies_active_fixtures": False,
        "changes_prompts": False,
        "mutates_release_state": False,
        "uses_live_sources": False,
        "accesses_devhub": False,
        "performs_official_actions": False,
        "activates_rollback": False,
    }

    result = validate_release_rollback_rehearsal_packet_v1(packet)
    assert result.ok, result.as_dict()


def test_validator_rejects_missing_scenario_rows_and_unsafe_commands() -> None:
    packet = build_release_rollback_rehearsal_packet_v1(_load_fixture())
    packet["ordered_rollback_scenario_rows"] = []
    packet["post_rollback_validation_commands"].append(["python3", "ppd/crawler/live_public_scrape.py"])

    result = validate_release_rollback_rehearsal_packet_v1(packet)

    assert not result.ok
    codes = {issue.code for issue in result.issues}
    assert "missing_required_rows" in codes
    assert "unsafe_validation_command" in codes


def test_validator_rejects_active_fixture_mutation_flag() -> None:
    packet = build_release_rollback_rehearsal_packet_v1(_load_fixture())
    packet["affected_inactive_fixture_family_inventory"][0]["active_fixture_mutation"] = True

    result = validate_release_rollback_rehearsal_packet_v1(packet)

    assert not result.ok
    codes = {issue.code for issue in result.issues}
    assert "active_fixture_mutation" in codes
    assert "active_mutation_flag" in codes


def test_builder_rejects_unsafe_inactive_decision_text() -> None:
    fixture = _load_fixture()
    fixture["decision_rows"][0]["rationale"] = "live DevHub execution was observed"

    with pytest.raises(ValueError):
        build_release_rollback_rehearsal_packet_v1(fixture)
