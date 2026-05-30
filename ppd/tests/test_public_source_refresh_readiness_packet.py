from __future__ import annotations

import json
from pathlib import Path

from ppd.source_refresh.readiness_packet import build_readiness_packet_from_fixture_dir


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source_refresh_readiness"


def test_builds_expected_fixture_first_readiness_packet() -> None:
    expected = json.loads((FIXTURE_DIR / "expected_public_source_refresh_readiness_packet.json").read_text(encoding="utf-8"))

    packet = build_readiness_packet_from_fixture_dir(FIXTURE_DIR)

    assert packet == expected


def test_readiness_packet_keeps_execution_side_effects_disabled() -> None:
    packet = build_readiness_packet_from_fixture_dir(FIXTURE_DIR)

    assert packet["attestations"] == {
        "fixture_first": True,
        "no_live_fetch": True,
        "no_download": True,
        "no_processor_invocation": True,
        "no_registry_mutation": True,
        "no_authenticated_automation": True,
        "no_raw_body_persistence": True,
    }
    assert all(record["capture_mode"] == "metadata_only" for record in packet["expected_metadata_only_capture_records"])
    assert all("raw_body" in record["forbidden_fields"] for record in packet["expected_metadata_only_capture_records"])


def test_per_source_decisions_include_citations_and_review_owners() -> None:
    packet = build_readiness_packet_from_fixture_dir(FIXTURE_DIR)
    decisions = {entry["source_id"]: entry for entry in packet["per_source_go_no_go"]}

    assert decisions["ppd-online-tools-overview"]["decision"] == "go"
    assert decisions["ppd-online-tools-overview"]["reviewer_owner"] == "ppd-public-refresh-reviewer"
    assert "runbook:no-processor-before-review" in decisions["ppd-online-tools-overview"]["citations"]

    assert decisions["ppd-fee-payment-guide"]["decision"] == "no_go"
    assert "proposal decision is defer_download" in decisions["ppd-fee-payment-guide"]["reasons"]
    assert "dry-run:pdf-download-not-authorized" in decisions["ppd-fee-payment-guide"]["citations"]
