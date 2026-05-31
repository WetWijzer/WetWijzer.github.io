from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.citation_span_integrity_packet_v2 import (
    build_citation_span_integrity_packet_v2,
    validate_citation_span_integrity_packet_v2,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "citation_span_integrity_packet_v2" / "valid_fixture.json"


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _valid_packet() -> dict:
    return build_citation_span_integrity_packet_v2(_fixture(), generated_at="2026-05-31T00:00:00Z")


def _codes(packet: dict) -> set[str]:
    return set(validate_citation_span_integrity_packet_v2(packet).codes())


def test_builds_valid_fixture_first_packet() -> None:
    packet = _valid_packet()
    result = validate_citation_span_integrity_packet_v2(packet)

    assert result.valid
    assert packet["active_mutation_flags"]["active_source_mutation"] is False
    assert packet["requirement_to_guardrail_traces"]
    assert packet["refusal_to_source_traces"]


def test_rejects_missing_source_evidence_ids_and_span_placeholders() -> None:
    packet = _valid_packet()
    packet["agent_facing_requirements"][0]["source_evidence_ids"] = []
    packet["agent_facing_requirements"][0]["citation_span_placeholders"] = []

    assert "missing_agent_facing_source_evidence" in _codes(packet)
    assert "missing_agent_facing_citation_span" in _codes(packet)


def test_rejects_missing_freshness_and_reviewer_disposition() -> None:
    packet = _valid_packet()
    packet["source_evidence"][0].pop("freshness_status")
    packet["agent_facing_refusals"][0].pop("reviewer_disposition_placeholder")

    codes = _codes(packet)
    assert "missing_freshness_status" in codes
    assert "missing_agent_facing_reviewer_disposition" in codes


def test_rejects_missing_requirement_to_guardrail_and_refusal_to_source_traces() -> None:
    packet = _valid_packet()
    packet["agent_facing_requirements"][0]["guardrail_trace_ids"] = []
    packet["agent_facing_refusals"][0]["source_trace_ids"] = []

    codes = _codes(packet)
    assert "missing_requirement_to_guardrail_trace" in codes
    assert "missing_refusal_to_source_trace" in codes


def test_rejects_missing_validation_commands() -> None:
    packet = _valid_packet()
    packet["offline_validation_commands"] = []

    assert "unexpected_validation_commands" in _codes(packet)


def test_rejects_private_session_browser_raw_and_downloaded_artifacts() -> None:
    packet = _valid_packet()
    packet["source_evidence"][0]["artifact_note"] = "browser state trace.zip raw crawl downloaded document"

    assert "private_or_live_artifact_reference" in _codes(packet)


def test_rejects_live_crawl_devhub_claims_and_legal_guarantees() -> None:
    packet = _valid_packet()
    packet["agent_facing_requirements"][0]["claim"] = "Live crawl observed DevHub verified this permit will be approved."

    codes = _codes(packet)
    assert "private_or_live_artifact_reference" in codes
    assert "legal_or_permitting_guarantee" in codes


def test_rejects_active_mutation_flags() -> None:
    packet = _valid_packet()
    for flag in list(packet["active_mutation_flags"]):
        mutated = copy.deepcopy(packet)
        mutated["active_mutation_flags"][flag] = True
        assert "active_mutation_flag_enabled" in _codes(mutated)
