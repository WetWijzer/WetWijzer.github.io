from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.platform.agent_consumer_release_handoff import (
    HandoffValidationError,
    assert_valid_agent_consumer_release_handoff_packet,
    validate_agent_consumer_release_handoff_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "agent_consumer_release_handoff"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_agent_consumer_release_handoff_packet_passes() -> None:
    packet = _load_fixture("valid_packet.json")

    findings = validate_agent_consumer_release_handoff_packet(packet)

    assert findings == []
    assert_valid_agent_consumer_release_handoff_packet(packet)


def test_invalid_agent_consumer_release_handoff_packet_reports_required_rejections() -> None:
    packet = _load_fixture("invalid_packet.json")

    findings = validate_agent_consumer_release_handoff_packet(packet)
    codes = {finding.code for finding in findings}

    assert "uncited_capability_claim" in codes
    assert "missing_supported_scenarios" in codes
    assert "missing_scenario_id" in codes
    assert "uncited_scenario" in codes
    assert "incomplete_reversible_draft_boundaries" in codes
    assert "incomplete_reviewer_owner" in codes
    assert "private_or_authenticated_key" in codes
    assert "raw_authenticated_value" in codes
    assert "private_case_fact" in codes
    assert "local_private_path" in codes
    assert "live_execution_claim" in codes
    assert "outcome_guarantee" in codes
    assert "enabled_consequential_control" in codes
    assert "active_mutation_flag" in codes


def test_assert_valid_raises_with_findings_for_invalid_packet() -> None:
    packet = _load_fixture("invalid_packet.json")

    with pytest.raises(HandoffValidationError) as exc_info:
        assert_valid_agent_consumer_release_handoff_packet(packet)

    assert exc_info.value.findings
