from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.agent_readiness.consumer_post_release_smoke_transcript_packet import (
    PostReleaseSmokeTranscriptValidationError,
    assert_valid_agent_consumer_post_release_smoke_transcript_packet,
    validate_agent_consumer_post_release_smoke_transcript_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "agent_consumer_post_release_smoke_transcript_packet"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_post_release_smoke_transcript_packet_passes() -> None:
    packet = _load_fixture("valid_packet.json")

    result = validate_agent_consumer_post_release_smoke_transcript_packet(packet)

    assert result.valid
    assert result.errors == ()
    assert_valid_agent_consumer_post_release_smoke_transcript_packet(packet)


def test_invalid_packet_reports_required_rejections() -> None:
    packet = _load_fixture("invalid_packet.json")

    result = validate_agent_consumer_post_release_smoke_transcript_packet(packet)
    codes = set(result.errors)

    assert "uncited_consumer_scenario" in codes
    assert "missing_observed_safe_read_only_response" in codes
    assert "missing_reversible_draft_preview_boundary" in codes
    assert "missing_blocked_action_message" in codes
    assert "missing_reviewer_owner" in codes
    assert "private_case_fact" in codes
    assert "raw_authenticated_value" in codes
    assert "local_private_path" in codes
    assert "live_execution_claim" in codes
    assert "outcome_guarantee" in codes
    assert "enabled_consequential_control" in codes
    assert "active_mutation_flag" in codes


def test_assert_valid_raises_with_findings_for_invalid_packet() -> None:
    packet = _load_fixture("invalid_packet.json")

    with pytest.raises(PostReleaseSmokeTranscriptValidationError) as exc_info:
        assert_valid_agent_consumer_post_release_smoke_transcript_packet(packet)

    assert exc_info.value.findings


def test_rejects_active_monitoring_mutation_flag() -> None:
    packet = _load_fixture("valid_packet.json")
    broken = copy.deepcopy(packet)
    broken["mutation_flags"]["monitoring_mutation_enabled"] = True

    result = validate_agent_consumer_post_release_smoke_transcript_packet(broken)

    assert "active_mutation_flag" in result.errors
