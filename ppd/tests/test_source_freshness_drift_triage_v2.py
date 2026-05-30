from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.source_freshness_drift_triage_v2 import (
    TriageValidationError,
    is_valid_source_freshness_drift_triage_v2_packet,
    validate_source_freshness_drift_triage_v2_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source_freshness_drift_triage_v2"


def _valid_packet() -> dict:
    return json.loads((FIXTURE_DIR / "valid_packet.json").read_text(encoding="utf-8"))


def _issue_codes(packet: dict) -> set[str]:
    with pytest.raises(TriageValidationError) as exc_info:
        validate_source_freshness_drift_triage_v2_packet(packet)
    return {issue.code for issue in exc_info.value.issues}


def test_valid_source_freshness_drift_triage_v2_packet_accepts_offline_cited_fixture() -> None:
    packet = _valid_packet()

    validate_source_freshness_drift_triage_v2_packet(packet)

    assert is_valid_source_freshness_drift_triage_v2_packet(packet)


@pytest.mark.parametrize(
    ("field", "expected_code"),
    [
        ("citations", "uncited_classification"),
        ("affected_artifact_ids", "missing_affected_artifact_ids"),
        ("escalation_owner", "missing_escalation_owner"),
    ],
)
def test_source_freshness_drift_triage_v2_packet_rejects_incomplete_classifications(field: str, expected_code: str) -> None:
    packet = _valid_packet()
    if field == "escalation_owner":
        packet["classifications"][0][field] = ""
    else:
        packet["classifications"][0][field] = []

    assert expected_code in _issue_codes(packet)


def test_source_freshness_drift_triage_v2_packet_rejects_private_or_authenticated_facts() -> None:
    packet = _valid_packet()
    packet["classifications"][0]["fact_scope"] = "authenticated DevHub account fact"

    assert "private_or_authenticated_fact" in _issue_codes(packet)


def test_source_freshness_drift_triage_v2_packet_rejects_raw_crawl_and_download_references() -> None:
    packet = _valid_packet()
    packet["raw_crawl_output_ref"] = "file:///tmp/ppd/raw-response.warc"

    assert "raw_or_downloaded_reference" in _issue_codes(packet)


@pytest.mark.parametrize(
    "claim",
    [
        "Ran live crawler against DevHub before triage.",
        "Executed processor and LLM execution for this packet.",
    ],
)
def test_source_freshness_drift_triage_v2_packet_rejects_live_execution_claims(claim: str) -> None:
    packet = _valid_packet()
    packet["classifications"][0]["execution_note"] = claim

    assert "live_execution_claim" in _issue_codes(packet)


def test_source_freshness_drift_triage_v2_packet_rejects_legal_or_permitting_outcome_guarantees() -> None:
    packet = _valid_packet()
    packet["classifications"][0]["outcome_note"] = "Permit will be approved after this correction."

    assert "outcome_guarantee" in _issue_codes(packet)


@pytest.mark.parametrize(
    "flag",
    [
        {"mutation_flags": ["source"]},
        {"mutate_guardrail": True},
        {"update_schedule": True},
        {"active_release_state_mutation": True},
        {"agent_state_mutation": True},
    ],
)
def test_source_freshness_drift_triage_v2_packet_rejects_active_mutation_flags(flag: dict) -> None:
    packet = _valid_packet()
    packet.update(flag)

    assert "active_mutation_flag" in _issue_codes(packet)
