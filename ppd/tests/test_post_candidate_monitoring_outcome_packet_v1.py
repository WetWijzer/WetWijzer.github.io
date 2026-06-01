from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.post_candidate_monitoring_outcome_packet_v1 import (
    require_post_candidate_monitoring_outcome_packet_v1,
    validate_post_candidate_monitoring_outcome_packet_v1,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "post_candidate_monitoring_outcome_packet_v1"
VALID_PACKET_PATH = FIXTURE_DIR / "valid_packet.json"
REJECTION_CASES_PATH = FIXTURE_DIR / "rejection_cases.json"


def _valid_packet() -> dict:
    return json.loads(VALID_PACKET_PATH.read_text(encoding="utf-8"))


def test_post_candidate_monitoring_outcome_packet_v1_accepts_valid_fixture() -> None:
    packet = _valid_packet()
    result = validate_post_candidate_monitoring_outcome_packet_v1(packet)
    assert result.ready, result.problems
    assert result.as_dict()["ready"] is True
    require_post_candidate_monitoring_outcome_packet_v1(packet)


def test_post_candidate_monitoring_outcome_packet_v1_rejects_fixture_cases() -> None:
    cases = json.loads(REJECTION_CASES_PATH.read_text(encoding="utf-8"))
    assert cases
    for case in cases:
        packet = _valid_packet()
        _deep_update(packet, case["patch"])
        result = validate_post_candidate_monitoring_outcome_packet_v1(packet)
        assert not result.ready, case["case_id"]
        assert any(case["expected_problem"] in problem for problem in result.problems), (case["case_id"], result.problems)


def test_post_candidate_monitoring_outcome_packet_v1_requires_pass_hold_and_reject() -> None:
    expected = {
        "pass": "missing per-anchor pass outcome",
        "hold": "missing per-anchor hold outcome",
        "reject": "missing per-anchor reject outcome",
    }
    for outcome, expected_problem in expected.items():
        packet = _valid_packet()
        packet["per_anchor_outcomes"] = [row for row in packet["per_anchor_outcomes"] if row.get("outcome") != outcome]
        result = validate_post_candidate_monitoring_outcome_packet_v1(packet)
        assert not result.ready, outcome
        assert any(expected_problem in problem for problem in result.problems), result.problems


def test_post_candidate_monitoring_outcome_packet_v1_requires_every_plan_source_anchor() -> None:
    packet = _valid_packet()
    packet["per_anchor_outcomes"] = [
        row for row in packet["per_anchor_outcomes"] if row.get("source_evidence_id") != "src-online-permitting-tools"
    ]
    result = validate_post_candidate_monitoring_outcome_packet_v1(packet)
    assert not result.ready
    assert any("missing per-anchor outcome row for source_evidence_id: src-online-permitting-tools" in problem for problem in result.problems)


def test_post_candidate_monitoring_outcome_packet_v1_rejects_foreign_plan_references() -> None:
    packet = _valid_packet()
    packet["per_anchor_outcomes"][0]["check_id"] = "foreign-check"
    packet["per_anchor_outcomes"][1]["source_evidence_id"] = "foreign-source"
    result = validate_post_candidate_monitoring_outcome_packet_v1(packet)
    assert not result.ready
    assert any("references check_id outside synthetic monitoring plan rows" in problem for problem in result.problems)
    assert any("references source_evidence_id outside synthetic monitoring plan rows" in problem for problem in result.problems)


def _deep_update(target: dict, patch: dict) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)
        else:
            target[key] = copy.deepcopy(value)
