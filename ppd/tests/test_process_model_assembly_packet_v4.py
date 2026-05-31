from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.agent_readiness.process_model_assembly_packet_v4 import (
    ACTIVE_MUTATION_FLAGS,
    REQUIRED_TOP_LEVEL_SEQUENCES,
    VALIDATION_COMMANDS,
    load_process_model_assembly_packet_v4,
    validate_process_model_assembly_packet_v4,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "process_model_assembly_packet_v4" / "valid_packet.json"


def _valid_packet() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_process_model_assembly_packet_v4_valid_fixture_loads() -> None:
    packet = load_process_model_assembly_packet_v4(FIXTURE_PATH)
    result = validate_process_model_assembly_packet_v4(packet)
    assert result.valid, result.problems


def test_process_model_assembly_packet_v4_rejects_missing_required_sections() -> None:
    for key in REQUIRED_TOP_LEVEL_SEQUENCES:
        packet = _valid_packet()
        packet.pop(key)
        result = validate_process_model_assembly_packet_v4(packet)
        assert not result.valid
        assert any(key in problem for problem in result.problems), result.problems


def test_process_model_assembly_packet_v4_rejects_empty_assembly_rows() -> None:
    for key in (
        "eligibility_rule_rows",
        "required_user_fact_rows",
        "document_requirement_matrix_rows",
        "fee_deadline_trigger_rows",
        "unsupported_path_notes",
        "devhub_boundary_rows",
        "citation_spans",
        "stale_evidence_holds",
        "reviewer_dispositions",
    ):
        packet = _valid_packet()
        packet[key] = []
        result = validate_process_model_assembly_packet_v4(packet)
        assert not result.valid
        assert f"{key} must be a non-empty list" in result.problems


def test_process_model_assembly_packet_v4_rejects_active_mutation_flags() -> None:
    for flag in ACTIVE_MUTATION_FLAGS:
        packet = _valid_packet()
        packet[flag] = True
        result = validate_process_model_assembly_packet_v4(packet)
        assert not result.valid
        assert f"{flag} must be false" in result.problems


def test_process_model_assembly_packet_v4_rejects_unknown_recommendation_refs() -> None:
    unknown_ref_examples = {
        "eligibility_rule_refs": "missing-eligibility-rule",
        "required_user_fact_refs": "missing-user-fact",
        "document_matrix_refs": "missing-document-row",
        "fee_deadline_trigger_refs": "missing-trigger-row",
        "unsupported_path_refs": "missing-unsupported-path",
        "devhub_boundary_refs": "missing-devhub-boundary",
        "citation_span_refs": "missing-citation-span",
        "stale_evidence_hold_refs": "missing-stale-hold",
        "reviewer_disposition_refs": "missing-reviewer-disposition",
    }
    for field, missing_ref in unknown_ref_examples.items():
        packet = _valid_packet()
        recommendation = copy.deepcopy(packet["inactive_process_model_assembly_recommendations"][0])  # type: ignore[index]
        recommendation[field] = [missing_ref]
        packet["inactive_process_model_assembly_recommendations"] = [recommendation]
        result = validate_process_model_assembly_packet_v4(packet)
        assert not result.valid
        assert any(f"unknown ref {missing_ref}" in problem for problem in result.problems), result.problems


def test_process_model_assembly_packet_v4_rejects_live_private_or_consequential_payloads() -> None:
    examples = (
        ("devhub_session", {"note": "not committable"}),
        ("browser_trace", "trace artifact path"),
        ("raw_download", "metadata-only fixtures cannot carry raw crawl output"),
        ("payment_note", "enter payment details"),
        ("live_note", "live crawl was not part of this fixture"),
        ("official_completion_note", "official action completed"),
        ("guarantee_note", "permit will be approved"),
    )
    for key, value in examples:
        packet = _valid_packet()
        packet[key] = value
        result = validate_process_model_assembly_packet_v4(packet)
        assert not result.valid, key


def test_process_model_assembly_packet_v4_requires_exact_offline_validation_commands() -> None:
    packet = _valid_packet()
    packet["validation_commands"] = [["python3", "-m", "pytest"]]
    result = validate_process_model_assembly_packet_v4(packet)
    assert not result.valid
    assert "validation_commands must contain the PP&D daemon self-test command" in result.problems

    packet = _valid_packet()
    recommendation = copy.deepcopy(packet["inactive_process_model_assembly_recommendations"][0])  # type: ignore[index]
    recommendation["validation_commands"] = []
    packet["inactive_process_model_assembly_recommendations"] = [recommendation]
    result = validate_process_model_assembly_packet_v4(packet)
    assert not result.valid
    assert any("validation_commands must contain" in problem for problem in result.problems)
    assert VALIDATION_COMMANDS != []
