from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ppd.agent_readiness import AgentReadinessPacketError, require_agent_readiness_packet_ready, validate_agent_readiness_packet

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_readiness" / "readiness_packet_fixture.json"
_NOW = datetime(2026, 5, 15, tzinfo=timezone.utc)


def _fixture_with_spans() -> dict:
    fixture = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    for index, evidence in enumerate(fixture["normalized_source_evidence"]):
        evidence["citation_spans"] = [
            {
                "span_id": f"span-{evidence['evidence_id']}",
                "start": index * 10,
                "end": index * 10 + 8,
                "source_evidence_ids": [evidence["evidence_id"]],
            }
        ]
    return fixture


def test_accepts_fixture_first_agent_readiness_packet() -> None:
    result = validate_agent_readiness_packet(_fixture_with_spans(), now=_NOW)

    assert result.ready is True
    assert result.problems == ()


def test_rejects_stale_source_evidence() -> None:
    fixture = _fixture_with_spans()
    fixture["normalized_source_evidence"][0]["last_verified_at"] = "2026-01-01T00:00:00Z"

    result = validate_agent_readiness_packet(fixture, now=_NOW)

    assert result.ready is False
    assert any("stale" in problem for problem in result.problems)


def test_rejects_missing_citation_spans() -> None:
    fixture = _fixture_with_spans()
    fixture["normalized_source_evidence"][0].pop("citation_spans")

    result = validate_agent_readiness_packet(fixture, now=_NOW)

    assert result.ready is False
    assert any("missing citation_spans" in problem for problem in result.problems)


def test_rejects_incomplete_crawl_promotion_audit_status() -> None:
    fixture = _fixture_with_spans()
    fixture["crawl_promotion_audit"]["promotion_status"] = "incomplete"
    fixture["crawl_promotion_audit"]["promotable"] = False

    result = validate_agent_readiness_packet(fixture, now=_NOW)

    assert result.ready is False
    assert any("crawl_promotion_audit" in problem for problem in result.problems)
    assert any("incomplete" in problem for problem in result.problems)


def test_rejects_absent_devhub_surface_map_readiness() -> None:
    fixture = _fixture_with_spans()
    fixture.pop("devhub_surface_map_readiness")

    result = validate_agent_readiness_packet(fixture, now=_NOW)

    assert result.ready is False
    assert "devhub_surface_map_readiness is required" in result.problems


def test_rejects_consequential_action_without_required_handoff_gates() -> None:
    fixture = _fixture_with_spans()
    fixture["action_decision_output"]["requires_manual_handoff"] = False
    fixture["action_decision_output"]["requires_attendance"] = False
    fixture["action_decision_output"]["requires_exact_confirmation"] = False

    result = validate_agent_readiness_packet(fixture, now=_NOW)

    assert result.ready is False
    assert any("manual handoff" in problem for problem in result.problems)
    assert any("exact-confirmation" in problem for problem in result.problems)


def test_require_agent_readiness_packet_ready_raises_existing_packet_error() -> None:
    fixture = _fixture_with_spans()
    fixture["crawl_promotion_audit"]["manifest_ids"] = []

    with pytest.raises(AgentReadinessPacketError) as excinfo:
        require_agent_readiness_packet_ready(fixture, now=_NOW)

    assert excinfo.value.code == "invalid_agent_readiness_packet"
    assert any("manifest_ids" in problem for problem in excinfo.value.problems)


def test_validation_does_not_mutate_fixture() -> None:
    fixture = _fixture_with_spans()
    original = deepcopy(fixture)

    validate_agent_readiness_packet(fixture, now=_NOW)

    assert fixture == original
