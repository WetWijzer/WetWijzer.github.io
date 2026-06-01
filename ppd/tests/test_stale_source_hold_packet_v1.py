from __future__ import annotations

import json
from pathlib import Path

from ppd.validation.stale_source_hold_packet_v1 import (
    assert_valid_stale_source_agent_hold_packet_v1,
    validate_stale_source_agent_hold_packet_v1,
)

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "stale_source_hold_packet_v1"


def _valid_packet() -> dict:
    return json.loads((_FIXTURE_DIR / "valid_packet.json").read_text(encoding="utf-8"))


def test_valid_stale_source_hold_packet_v1_fixture_passes() -> None:
    packet = _valid_packet()

    assert validate_stale_source_agent_hold_packet_v1(packet) == []
    assert_valid_stale_source_agent_hold_packet_v1(packet)


def test_rejects_missing_required_review_evidence_rows() -> None:
    packet = _valid_packet()
    for key in (
        "monitoring_outcome_references",
        "affected_missing_information_rows",
        "blocked_action_rows",
        "next_safe_action_rows",
        "citation_warnings",
        "reviewer_holds",
        "validation_commands",
    ):
        packet[key] = []

    errors = validate_stale_source_agent_hold_packet_v1(packet)

    assert "missing monitoring outcome references" in errors
    assert "missing affected missing-information rows" in errors
    assert "missing blocked-action rows" in errors
    assert "missing next-safe-action rows" in errors
    assert "missing citation warnings" in errors
    assert "missing reviewer holds" in errors
    assert "missing validation commands" in errors


def test_rejects_private_artifacts_live_claims_completion_release_and_mutation_flags() -> None:
    packet = _valid_packet()
    packet["evidence"] = {
        "path": "private/session/browser/raw_crawl/downloads/example.har",
        "claim": "DevHub live crawl official action completed and release activated",
    }
    packet["active_mutation"] = True

    errors = validate_stale_source_agent_hold_packet_v1(packet)

    assert "private/session/browser/raw/downloaded artifacts" in errors
    assert "live crawl or DevHub claims" in errors
    assert "official-action completion claims" in errors
    assert "release activation claims" in errors
    assert "active mutation flags" in errors
