from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.logic.inactive_process_model_promotion_gate_v2 import (
    assert_packet_has_all_v2_gates,
    assert_recommendations_only,
    evaluate_packet,
    load_packet,
    recommendations_as_dicts,
    validate_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "inactive_process_model_promotion_gate_v2" / "packet.json"


def _packet() -> dict:
    return load_packet(FIXTURE_PATH)


def test_fixture_packet_declares_all_v2_gates() -> None:
    packet = _packet()

    assert_packet_has_all_v2_gates(packet)
    validate_packet(packet)


def test_evaluator_emits_recommendations_only() -> None:
    packet = _packet()
    recommendations = evaluate_packet(packet)

    assert_recommendations_only(recommendations)
    assert {recommendation.recommendation for recommendation in recommendations} == {"promote", "hold", "reject"}


def test_recommendation_payloads_include_required_gate_axes_and_offline_commands() -> None:
    packet = _packet()
    results = recommendations_as_dicts(packet)

    by_delta = {result["delta_id"]: result for result in results}
    promote = by_delta["synthetic-inactive-delta-promote-001"]
    hold = by_delta["synthetic-inactive-delta-hold-001"]
    reject = by_delta["synthetic-inactive-delta-reject-001"]

    assert promote["recommendation"] == "promote"
    assert hold["recommendation"] == "hold"
    assert reject["recommendation"] == "reject"

    promote_gates = {gate["gate"]: gate for gate in promote["gate_results"]}
    assert set(promote_gates) == set(packet["gate_names"])
    assert all(gate["passed"] for gate in promote_gates.values())
    assert promote["offline_validation_commands"] == packet["offline_validation_commands"]

    hold_gates = {gate["gate"]: gate for gate in hold["gate_results"]}
    assert hold_gates["stale_evidence_hold"]["severity"] == "hold"
    assert hold_gates["document_matrix"]["severity"] == "hold"
    assert hold_gates["reviewer_disposition"]["severity"] == "hold"

    reject_gates = {gate["gate"]: gate for gate in reject["gate_results"]}
    assert reject_gates["reviewer_disposition"]["severity"] == "reject"


def test_packet_scope_blocks_active_or_live_surfaces() -> None:
    packet = _packet()

    assert packet["source_mode"] == "fixture_first_synthetic_only"
    assert packet["process_model_state"] == "inactive"
    assert "active_process_models" in packet["forbidden_surfaces"]
    assert "live_crawl" in packet["forbidden_surfaces"]
    assert "devhub_surfaces" in packet["forbidden_surfaces"]
    assert "payments" in packet["forbidden_surfaces"]
    assert "scheduling" in packet["forbidden_surfaces"]


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("permit_family_recommendation", "permit-family recommendation"),
        ("citation_integrity_check", "citation check"),
        ("stale_evidence_hold_check", "stale-evidence hold check"),
        ("document_matrix", "document matrix"),
        ("fee_deadline_matrix", "fee/deadline matrix"),
        ("unsupported_path_notes", "unsupported-path checks"),
        ("reviewer_disposition", "reviewer disposition"),
    ],
)
def test_validation_rejects_missing_required_row_checks(field: str, message: str) -> None:
    packet = _packet()
    packet["synthetic_inactive_delta_rows"] = [deepcopy(packet["synthetic_inactive_delta_rows"][0])]
    packet["synthetic_inactive_delta_rows"][0].pop(field)

    with pytest.raises(ValueError, match=message):
        validate_packet(packet)


def test_validation_rejects_missing_validation_commands() -> None:
    packet = _packet()
    packet.pop("offline_validation_commands")
    for row in packet["synthetic_inactive_delta_rows"]:
        row.pop("offline_validation_commands", None)

    with pytest.raises(ValueError, match="validation commands"):
        validate_packet(packet)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"artifact_ref": "session_state.json"}, "private/session/browser/raw/downloaded artifact"),
        ({"artifact_ref": "browser_state/playwright-report"}, "private/session/browser/raw/downloaded artifact"),
        ({"artifact_ref": "raw_crawl_body.html"}, "private/session/browser/raw/downloaded artifact"),
        ({"artifact_ref": "downloaded_document.pdf"}, "private/session/browser/raw/downloaded artifact"),
        ({"claim": "live crawl completed for this packet"}, "live crawl or DevHub claim"),
        ({"claim": "opened DevHub session for validation"}, "live crawl or DevHub claim"),
        ({"claim": "guarantees approval for the permit"}, "legal or permitting guarantee"),
        ({"claim": "submitted the permit application in DevHub"}, "official-action completion claim"),
        ({"active_mutation": True}, "active mutation flag"),
        ({"claim": "promoted to active process model"}, "active mutation language"),
    ],
)
def test_validation_rejects_forbidden_artifacts_claims_and_mutation_flags(payload: dict, message: str) -> None:
    packet = _packet()
    packet["unsafe_fixture_probe"] = payload

    with pytest.raises(ValueError, match=message):
        validate_packet(packet)


def test_validation_rejects_live_or_consequential_validation_commands() -> None:
    packet = _packet()
    packet["offline_validation_commands"] = [["python3", "ppd/crawler/live_public_scrape.py"]]

    with pytest.raises(ValueError, match="forbidden live or consequential"):
        validate_packet(packet)
