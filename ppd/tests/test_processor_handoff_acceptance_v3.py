from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ppd.crawler.processor_handoff_acceptance_v3 import (
    AcceptancePacketError,
    assert_acceptance_packet,
    load_acceptance_packet,
    validate_acceptance_packet,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "processor_handoff_acceptance_v3"
    / "synthetic_packet.json"
)


def test_synthetic_processor_handoff_acceptance_packet_v3_is_valid() -> None:
    packet = load_acceptance_packet(FIXTURE_PATH)

    result = assert_acceptance_packet(packet)

    assert result["valid"] is True
    assert result["packet_version"] == "v3"
    assert result["reviewed_seed_url_count"] == 3
    assert result["allowed_seed_url_count"] == 3
    assert result["skipped_url_count"] == 7


def test_packet_rejects_live_processor_execution_before_review() -> None:
    packet = load_acceptance_packet(FIXTURE_PATH)
    packet = copy.deepcopy(packet)
    packet["live_processor_execution_allowed"] = True
    packet["handoff_gate"]["accepted_for_live_processor_execution"] = True

    result = validate_acceptance_packet(packet)

    assert result["valid"] is False
    assert "live_processor_execution_allowed must be false" in result["errors"]
    assert "handoff_gate.accepted_for_live_processor_execution must be false" in result["errors"]
    with pytest.raises(AcceptancePacketError):
        assert_acceptance_packet(packet)


def test_packet_rejects_raw_body_persistence_flags() -> None:
    packet = load_acceptance_packet(FIXTURE_PATH)
    packet = copy.deepcopy(packet)
    packet["persistence_flags"]["no_raw_body_persisted"] = False
    packet["archive_manifest_expectations"][0]["raw_body_artifact_ref"] = "local/raw/body.html"

    result = validate_acceptance_packet(packet)

    assert result["valid"] is False
    assert "persistence_flags.no_raw_body_persisted must be true" in result["errors"]
    assert (
        "archive expectation for https://www.portland.gov/ppd must not include a raw_body_artifact_ref"
        in result["errors"]
    )


def test_packet_rejects_missing_skipped_url_reason_coverage() -> None:
    packet = load_acceptance_packet(FIXTURE_PATH)
    packet = copy.deepcopy(packet)
    packet["skipped_urls"] = packet["skipped_urls"][:-1]

    result = validate_acceptance_packet(packet)

    assert result["valid"] is False
    assert "skipped_urls must cover reason codes: unsupported_content_type" in result["errors"]
