from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from ppd.devhub.surface_map_reviewer_packet_v2 import (
    SurfaceMapReviewerPacketError,
    build_surface_map_reviewer_packet_v2,
    validate_surface_map_reviewer_packet_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_surface_map_reviewer_packet_v2"


def _load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _valid_packet() -> dict:
    return build_surface_map_reviewer_packet_v2(_load_fixture("surface_map_candidate_v2.json"))


def test_build_reviewer_packet_matches_expected_fixture() -> None:
    candidate = _load_fixture("surface_map_candidate_v2.json")
    expected = _load_fixture("expected_surface_map_reviewer_packet_v2.json")

    assert build_surface_map_reviewer_packet_v2(candidate) == expected


def test_reviewer_rows_are_ordered_accept_hold_reject_rows() -> None:
    packet = _valid_packet()
    rows = packet["reviewer_accept_hold_reject_rows"]

    assert [row["order"] for row in rows] == [1, 2, 3, 4]
    assert {tuple(row["allowed_reviewer_dispositions"]) for row in rows} == {("accept", "hold", "reject")}
    assert {row["surface_map_change_applied"] for row in rows} == {False}
    assert {row["official_action_allowed"] for row in rows} == {False}


def test_trace_redaction_selector_and_blocked_notes_are_cross_referenced() -> None:
    packet = _valid_packet()

    trace_ids = {item["trace_placeholder_id"] for item in packet["observation_to_candidate_trace_placeholders"]}
    redaction_ids = {item["redaction_reference_id"] for item in packet["redaction_acceptance_references"]}
    selector_ids = {item["selector_risk_note_id"] for item in packet["unresolved_selector_risk_notes"]}
    blocked_ids = {item["blocked_action_confirmation_note_id"] for item in packet["blocked_action_confirmation_notes"]}

    for row in packet["reviewer_accept_hold_reject_rows"]:
        assert row["observation_to_candidate_trace_placeholder_id"] in trace_ids
        assert row["redaction_acceptance_reference_id"] in redaction_ids
        assert row["selector_risk_note_id"] in selector_ids
        if row["candidate_row_id"] == "surface-row-004-action-submit_application":
            assert row["blocked_action_confirmation_note_id"] in blocked_ids
            assert row["recommended_initial_disposition"] == "reject"
        else:
            assert row["recommended_initial_disposition"] == "hold"


def test_valid_reviewer_packet_validation_passes() -> None:
    assert validate_surface_map_reviewer_packet_v2(_valid_packet()) == []


def test_invalid_source_candidate_is_rejected() -> None:
    candidate = _load_fixture("surface_map_candidate_v2.json")
    candidate["candidate_rows"] = []

    with pytest.raises(SurfaceMapReviewerPacketError, match="source surface-map candidate v2 is invalid"):
        build_surface_map_reviewer_packet_v2(candidate)


def test_reviewer_packet_validation_rejects_surface_map_application() -> None:
    packet = _valid_packet()
    packet["reviewer_accept_hold_reject_rows"][0] = deepcopy(packet["reviewer_accept_hold_reject_rows"][0])
    packet["reviewer_accept_hold_reject_rows"][0]["surface_map_change_applied"] = True

    assert "reviewer_row_surface_map_change_applied_must_be_false" in validate_surface_map_reviewer_packet_v2(packet)


def test_reviewer_packet_validation_rejects_private_browser_artifacts() -> None:
    packet = _valid_packet()
    packet["review_notes"] = "Reviewer stored trace.zip from a browser session."

    assert any("private_session_browser_or_artifact_text" in error for error in validate_surface_map_reviewer_packet_v2(packet))


def test_reviewer_packet_validation_rejects_online_validation_commands() -> None:
    packet = _valid_packet()
    packet["offline_validation_commands"] = [["python3", "-m", "playwright", "open", "https://devhub.portlandoregon.gov"]]

    errors = validate_surface_map_reviewer_packet_v2(packet)

    assert "offline_validation_commands_must_be_exact" in errors


def test_reviewer_packet_validation_rejects_consequential_enablement() -> None:
    packet = _valid_packet()
    packet["review_notes"] = "The agent may submit the permit application after review."

    assert any("consequential_official_action_enablement_text" in error for error in validate_surface_map_reviewer_packet_v2(packet))
