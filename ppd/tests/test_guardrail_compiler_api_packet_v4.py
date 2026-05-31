from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.agent_readiness.guardrail_compiler_api_packet_v4 import (
    ACTIVE_MUTATION_FLAGS,
    REQUIRED_ROW_SEQUENCES,
    VALIDATION_COMMANDS,
    compile_guardrail_compiler_api_packet_v4,
    load_guardrail_compiler_api_packet_v4,
    validate_guardrail_compiler_api_packet_v4,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "guardrail_compiler_api_packet_v4" / "valid_packet.json"
ASSEMBLY_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "process_model_assembly_packet_v4" / "valid_packet.json"


def _valid_packet() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _assembly_packet() -> dict[str, object]:
    return json.loads(ASSEMBLY_FIXTURE_PATH.read_text(encoding="utf-8"))


def _without_row_field(packet: dict[str, object], row_family: str, field: str) -> dict[str, object]:
    row = copy.deepcopy(packet[row_family][0])  # type: ignore[index]
    row.pop(field, None)
    packet[row_family] = [row]
    return packet


def test_guardrail_compiler_api_packet_v4_valid_fixture_loads() -> None:
    packet = load_guardrail_compiler_api_packet_v4(FIXTURE_PATH)
    result = validate_guardrail_compiler_api_packet_v4(packet)
    assert result.valid, result.problems


def test_guardrail_compiler_api_packet_v4_compiles_from_inactive_assembly_recommendation() -> None:
    compiled = compile_guardrail_compiler_api_packet_v4(_assembly_packet())
    expected = _valid_packet()
    assert compiled == expected


def test_guardrail_compiler_api_packet_v4_requires_all_row_families() -> None:
    for key in REQUIRED_ROW_SEQUENCES:
        packet = _valid_packet()
        packet.pop(key)
        result = validate_guardrail_compiler_api_packet_v4(packet)
        assert not result.valid
        assert f"{key} must be a non-empty list" in result.problems


def test_guardrail_compiler_api_packet_v4_rejects_missing_compiler_row_details() -> None:
    required_fields = (
        ("deterministic_predicate_rows", "requirement_node_ref"),
        ("deterministic_predicate_rows", "predicate_name"),
        ("deterministic_predicate_rows", "deterministic_expression"),
        ("deontic_rule_rows", "requirement_node_refs"),
        ("deontic_rule_rows", "modality"),
        ("deontic_rule_rows", "rule_text"),
        ("temporal_rule_rows", "stale_source_hold_refs"),
        ("temporal_rule_rows", "temporal_condition"),
        ("reversible_action_rows", "allowed_action"),
        ("reversible_action_rows", "reversibility_basis"),
        ("exact_confirmation_rows", "confirmation_scope"),
        ("exact_confirmation_rows", "required_confirmation"),
        ("refused_action_rows", "refused_action_family"),
        ("refused_action_rows", "refusal_reason"),
        ("missing_information_rows", "missing_information"),
        ("missing_information_rows", "ask_policy"),
        ("stale_source_hold_rows", "source_hold_refs"),
        ("stale_source_hold_rows", "hold_reason"),
        ("stale_source_hold_rows", "release_condition"),
        ("reviewer_disposition_rows", "reviewer_disposition_refs"),
        ("reviewer_disposition_rows", "decision"),
        ("reviewer_disposition_rows", "required_review"),
    )
    for row_family, field in required_fields:
        result = validate_guardrail_compiler_api_packet_v4(_without_row_field(_valid_packet(), row_family, field))
        assert not result.valid, (row_family, field)
        assert any(field in problem for problem in result.problems)


def test_guardrail_compiler_api_packet_v4_rejects_missing_explanation_template_placeholders() -> None:
    packet = _without_row_field(_valid_packet(), "explanation_template_rows", "placeholders")
    result = validate_guardrail_compiler_api_packet_v4(packet)
    assert not result.valid
    assert any("placeholders must be a non-empty list of strings" in problem for problem in result.problems)

    packet = _valid_packet()
    row = copy.deepcopy(packet["explanation_template_rows"][0])  # type: ignore[index]
    row["template_text"] = "I can use this only as an offline fixture row."
    packet["explanation_template_rows"] = [row]
    result = validate_guardrail_compiler_api_packet_v4(packet)
    assert not result.valid
    assert any("template_text must include placeholder {hold_reason}" in problem for problem in result.problems)


def test_guardrail_compiler_api_packet_v4_rejects_active_mutation_flags() -> None:
    for flag in ACTIVE_MUTATION_FLAGS:
        packet = _valid_packet()
        packet[flag] = True
        result = validate_guardrail_compiler_api_packet_v4(packet)
        assert not result.valid
        assert f"{flag} must be false" in result.problems


def test_guardrail_compiler_api_packet_v4_requires_inactive_row_statuses() -> None:
    packet = _valid_packet()
    row = copy.deepcopy(packet["deontic_rule_rows"][0])  # type: ignore[index]
    row["output_status"] = "active_guardrail_row"
    packet["deontic_rule_rows"] = [row]
    result = validate_guardrail_compiler_api_packet_v4(packet)
    assert not result.valid
    assert any("output_status must be inactive_compiler_row_only" in problem for problem in result.problems)


def test_guardrail_compiler_api_packet_v4_keeps_stale_hold_and_reviewer_pending() -> None:
    packet = _valid_packet()
    stale_row = copy.deepcopy(packet["stale_source_hold_rows"][0])  # type: ignore[index]
    stale_row["output_status"] = "released"
    packet["stale_source_hold_rows"] = [stale_row]
    result = validate_guardrail_compiler_api_packet_v4(packet)
    assert not result.valid
    assert any("output_status must be hold_active" in problem for problem in result.problems)

    packet = _valid_packet()
    reviewer_row = copy.deepcopy(packet["reviewer_disposition_rows"][0])  # type: ignore[index]
    reviewer_row["output_status"] = "approved"
    packet["reviewer_disposition_rows"] = [reviewer_row]
    result = validate_guardrail_compiler_api_packet_v4(packet)
    assert not result.valid
    assert any("output_status must be pending_manual_review" in problem for problem in result.problems)

    packet = _valid_packet()
    reviewer_row = copy.deepcopy(packet["reviewer_disposition_rows"][0])  # type: ignore[index]
    reviewer_row["decision"] = "approved"
    packet["reviewer_disposition_rows"] = [reviewer_row]
    result = validate_guardrail_compiler_api_packet_v4(packet)
    assert not result.valid
    assert any("decision must be pending" in problem for problem in result.problems)


def test_guardrail_compiler_api_packet_v4_requires_exact_offline_validation_command_rows() -> None:
    packet = _valid_packet()
    packet["validation_commands"] = [["python3", "-m", "pytest"]]
    result = validate_guardrail_compiler_api_packet_v4(packet)
    assert not result.valid
    assert "validation_commands must contain the exact PP&D daemon self-test command" in result.problems

    packet = _valid_packet()
    command_row = copy.deepcopy(packet["offline_validation_command_rows"][0])  # type: ignore[index]
    command_row["command"] = ["python3", "-m", "pytest"]
    packet["offline_validation_command_rows"] = [command_row]
    result = validate_guardrail_compiler_api_packet_v4(packet)
    assert not result.valid
    assert any("command must be the exact PP&D daemon self-test argv" in problem for problem in result.problems)
    assert VALIDATION_COMMANDS == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]


def test_guardrail_compiler_api_packet_v4_rejects_live_or_consequential_completion_values() -> None:
    examples = (
        "live crawl",
        "live DevHub",
        "browser state",
        "auth state",
        "raw crawl",
        "downloaded document",
        "private session",
        "screenshot",
        "trace.zip",
        "har file",
        "submitted to DevHub",
        "uploaded to DevHub",
        "payment details entered",
        "scheduled inspection",
        "official action completed",
        "certification completed",
        "permit approved guarantee",
        "legal advice guarantee",
    )
    for value in examples:
        packet = _valid_packet()
        row = copy.deepcopy(packet["explanation_template_rows"][0])  # type: ignore[index]
        row["template_text"] = value
        packet["explanation_template_rows"] = [row]
        result = validate_guardrail_compiler_api_packet_v4(packet)
        assert not result.valid, value
