from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.extraction.requirement_reextraction_dry_run_packet_v2 import (
    assert_valid_requirement_reextraction_dry_run_packet_v2,
    validate_requirement_reextraction_dry_run_packet_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "requirement_reextraction_dry_run_packet_v2"


def _load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _codes(packet: dict) -> set[str]:
    return {finding.code for finding in validate_requirement_reextraction_dry_run_packet_v2(packet)}


def test_valid_requirement_reextraction_dry_run_packet_v2_fixture_passes() -> None:
    packet = _load_fixture("valid_packet.json")

    assert validate_requirement_reextraction_dry_run_packet_v2(packet) == []
    assert_valid_requirement_reextraction_dry_run_packet_v2(packet)


def test_rejects_missing_required_collections_and_placeholders() -> None:
    packet = _load_fixture("valid_packet.json")
    for key in (
        "requirement_delta_rows",
        "citation_span_placeholders",
        "confidence_placeholders",
        "human_review_placeholders",
        "affected_process_model_placeholders",
        "affected_guardrail_placeholders",
        "validation_commands",
    ):
        broken = copy.deepcopy(packet)
        broken.pop(key)
        assert f"missing_{key}" in _codes(broken)

    broken = copy.deepcopy(packet)
    broken["delta_placeholders"].pop("changed")
    assert "missing_changed_placeholder" in _codes(broken)


def test_rejects_missing_each_delta_kind_row() -> None:
    packet = _load_fixture("valid_packet.json")
    broken = copy.deepcopy(packet)
    broken["requirement_delta_rows"] = [
        row for row in broken["requirement_delta_rows"] if row["delta_kind"] != "removed"
    ]

    assert "missing_removed_delta_row" in _codes(broken)


def test_rejects_missing_row_level_review_and_impact_placeholders() -> None:
    packet = _load_fixture("valid_packet.json")
    cases = {
        "citation_span_placeholder": "missing_citation_span_placeholder",
        "confidence_placeholder": "missing_confidence_placeholder",
        "human_review_placeholder": "missing_human_review_placeholder",
        "affected_process_model_placeholder": "missing_affected_process_model_placeholder",
        "affected_guardrail_placeholder": "missing_affected_guardrail_placeholder",
    }
    for field, code in cases.items():
        broken = copy.deepcopy(packet)
        broken["requirement_delta_rows"][0].pop(field)
        assert code in _codes(broken)


def test_rejects_invalid_validation_command_shape() -> None:
    packet = _load_fixture("valid_packet.json")
    packet["validation_commands"] = ["python3 ppd/daemon/ppd_daemon.py --self-test"]

    assert "invalid_validation_command" in _codes(packet)


def test_rejects_forbidden_private_artifacts_live_claims_guarantees_and_mutations() -> None:
    invalid_cases = _load_fixture("invalid_cases.json")
    for case in invalid_cases["cases"]:
        findings = validate_requirement_reextraction_dry_run_packet_v2(case["packet"])
        codes = {finding.code for finding in findings}
        assert case["expected_code"] in codes, case["name"]
