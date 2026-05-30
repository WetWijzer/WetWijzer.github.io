from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.public_recrawl_dry_run_evidence_envelope_v2 import (
    REQUIRED_ATTESTATIONS,
    REQUIRED_SLOT_KINDS,
    build_public_recrawl_dry_run_evidence_envelope_v2,
    require_valid_public_recrawl_dry_run_evidence_envelope_v2,
    validate_public_recrawl_dry_run_evidence_envelope_v2,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_recrawl_dry_run_evidence_envelope_v2" / "source_packets.json"


def _load_source_packets() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _build_envelope() -> dict:
    return build_public_recrawl_dry_run_evidence_envelope_v2(_load_source_packets())


def test_builds_cited_metadata_only_observation_slots() -> None:
    envelope = _build_envelope()
    result = validate_public_recrawl_dry_run_evidence_envelope_v2(envelope)

    assert result.valid, result.errors
    assert envelope["packet_type"] == "public-recrawl-dry-run-evidence-envelope"
    assert envelope["version"] == "v2"
    assert envelope["fixture_first"] is True
    assert envelope["metadata_only"] is True
    assert {row["source_key"] for row in envelope["consumes"]} == {
        "public_recrawl_live_dry_run_plan_v2",
        "post_briefing_dry_run_authorization_ledger_v2",
    }

    slot_kinds = {slot["slot_kind"] for slot in envelope["observation_slots"]}
    assert REQUIRED_SLOT_KINDS.issubset(slot_kinds)
    assert all(slot["metadata_only"] is True for slot in envelope["observation_slots"])
    assert all(slot["citations"] for slot in envelope["observation_slots"])
    require_valid_public_recrawl_dry_run_evidence_envelope_v2(envelope)


def test_envelope_includes_requested_public_recrawl_observation_values() -> None:
    envelope = _build_envelope()
    slots_by_kind = {slot["slot_kind"]: slot for slot in envelope["observation_slots"]}

    assert slots_by_kind["seed_url"]["observed_value"] == {
        "seed_url": "https://www.portland.gov/council/agenda"
    }
    assert slots_by_kind["allowlist_robots_decision"]["observed_value"]["robots_decision"]["policy"] == "allowed"
    assert slots_by_kind["redirect_content_type_hash_placeholder"]["observed_value"] == {
        "requested_url": "https://www.portland.gov/council/agenda",
        "final_url": None,
        "redirect_chain": [],
        "http_status": None,
        "content_type": "text/html",
        "content_hash": "metadata_only_placeholder_not_captured",
        "raw_body_persisted": False,
    }
    assert slots_by_kind["skip_reason"]["observed_value"]["skipped_reason"] == "not_skipped_fixture_selected_for_metadata_observation"
    assert slots_by_kind["rate_limit_observation"]["observed_value"]["delay_seconds"] == 60
    assert "abort-if-live-execution-requested" in slots_by_kind["operator_stop_condition"]["observed_value"]["ledger_abort_condition_ids"]


def test_envelope_carries_required_attestation_slots_and_false_side_effects() -> None:
    envelope = _build_envelope()
    attestation_slots = [slot for slot in envelope["observation_slots"] if slot["slot_kind"] == "attestation"]

    assert {slot["observed_value"]["attestation_id"] for slot in attestation_slots} == set(REQUIRED_ATTESTATIONS)
    assert all(slot["observed_value"]["attested"] is True for slot in attestation_slots)
    assert envelope["attestations"] == {key: True for key in sorted(REQUIRED_ATTESTATIONS)}
    assert all(value is False for value in envelope["side_effects"].values())


def test_validator_rejects_uncited_observation_slot() -> None:
    envelope = _build_envelope()
    envelope["observation_slots"][0]["citations"] = []

    result = validate_public_recrawl_dry_run_evidence_envelope_v2(envelope)

    assert not result.valid
    assert "observation_slots[0].citations must be non-empty" in result.errors


def test_validator_rejects_missing_required_attestation_slot() -> None:
    envelope = _build_envelope()
    envelope["observation_slots"] = [
        slot
        for slot in envelope["observation_slots"]
        if slot.get("observed_value", {}).get("attestation_id") != "no_live_crawl"
    ]

    result = validate_public_recrawl_dry_run_evidence_envelope_v2(envelope)

    assert not result.valid
    assert "missing attestation slots: no_live_crawl" in result.errors


def test_validator_rejects_side_effect_claims() -> None:
    envelope = _build_envelope()
    envelope["side_effects"]["processor_invoked"] = True

    result = validate_public_recrawl_dry_run_evidence_envelope_v2(envelope)

    assert not result.valid
    assert "envelope.side_effects.processor_invoked must be false" in result.errors


def test_builder_rejects_missing_consumed_source_packet() -> None:
    source_packets = copy.deepcopy(_load_source_packets())
    source_packets.pop("post_briefing_dry_run_authorization_ledger_v2")

    try:
        build_public_recrawl_dry_run_evidence_envelope_v2(source_packets)
    except ValueError as exc:
        assert "missing source packets" in str(exc)
    else:
        raise AssertionError("expected missing source packet failure")
