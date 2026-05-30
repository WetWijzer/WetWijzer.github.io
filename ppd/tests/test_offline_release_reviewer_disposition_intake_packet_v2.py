from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.offline_release_reviewer_disposition_intake_packet_v2 import (
    assert_valid_offline_release_reviewer_disposition_intake_packet_v2,
    load_offline_release_reviewer_disposition_intake_packet_v2,
    validate_offline_release_reviewer_disposition_intake_packet_v2,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "offline_release_reviewer_disposition_intake_packet_v2"
    / "valid_packet.json"
)


def _valid_packet() -> dict:
    return load_offline_release_reviewer_disposition_intake_packet_v2(FIXTURE_PATH)


def _issue_codes(packet: dict) -> set[str]:
    return {issue.code for issue in validate_offline_release_reviewer_disposition_intake_packet_v2(packet).issues}


def test_valid_offline_release_reviewer_disposition_intake_packet_v2_fixture() -> None:
    packet = _valid_packet()

    result = validate_offline_release_reviewer_disposition_intake_packet_v2(packet)

    assert result.ok, result.as_dict()
    assert_valid_offline_release_reviewer_disposition_intake_packet_v2(packet)


@pytest.mark.parametrize(
    ("field", "expected_code"),
    [
        ("reviewer_decision_rows", "missing_reviewer_decision_rows"),
        ("evidence_bundle_references", "missing_evidence_bundle_references"),
        ("validation_transcript_review_placeholders", "missing_validation_transcript_review_placeholders"),
        ("rollback_readiness_confirmations", "missing_rollback_readiness_confirmations"),
        ("unresolved_risk_notes", "missing_unresolved_risk_notes"),
        ("offline_validation_commands", "missing_offline_validation_commands"),
        ("evidence_summary_acknowledgements", "missing_evidence_summary_acknowledgements"),
        ("unresolved_blocker_carry_forward", "missing_unresolved_blocker_carry_forward"),
        ("rollback_readiness_acknowledgements", "missing_rollback_readiness_acknowledgements"),
        ("validation_replay_acknowledgements", "missing_validation_replay_acknowledgements"),
        ("no_go_reason_placeholders", "missing_no_go_reason_placeholders"),
    ],
)
def test_required_packet_sections_are_rejected_when_missing(field: str, expected_code: str) -> None:
    packet = _valid_packet()
    packet[field] = []

    assert expected_code in _issue_codes(packet)


def test_missing_reviewer_decision_is_rejected() -> None:
    packet = _valid_packet()
    packet["reviewer_decision_rows"][0]["decision"] = ""

    assert "invalid_reviewer_decision" in _issue_codes(packet)


def test_missing_evidence_bundle_reference_fields_are_rejected() -> None:
    packet = _valid_packet()
    packet["evidence_bundle_references"][0]["bundle_id"] = ""

    assert "missing_evidence_bundle_reference_field" in _issue_codes(packet)


def test_missing_validation_transcript_review_placeholder_fields_are_rejected() -> None:
    packet = _valid_packet()
    packet["validation_transcript_review_placeholders"][0]["review_placeholder"] = ""

    assert "missing_validation_transcript_review_placeholder_field" in _issue_codes(packet)


def test_rollback_readiness_confirmation_must_be_true() -> None:
    packet = _valid_packet()
    packet["rollback_readiness_confirmations"][0]["confirmed"] = False

    assert "rollback_readiness_confirmation_not_true" in _issue_codes(packet)


def test_missing_unresolved_risk_note_fields_are_rejected() -> None:
    packet = _valid_packet()
    packet["unresolved_risk_notes"][0]["note"] = ""

    assert "missing_unresolved_risk_note_field" in _issue_codes(packet)


def test_invalid_unresolved_risk_note_status_is_rejected() -> None:
    packet = _valid_packet()
    packet["unresolved_risk_notes"][0]["status"] = "closed_without_review"

    assert "invalid_unresolved_risk_note_status" in _issue_codes(packet)


def test_unsafe_offline_validation_command_is_rejected() -> None:
    packet = _valid_packet()
    packet["offline_validation_commands"].append(["python3", "ppd/crawler/live_public_scrape.py"])

    assert "unsafe_offline_validation_command" in _issue_codes(packet)


def test_uncited_evidence_summary_acknowledgement_is_rejected() -> None:
    packet = _valid_packet()
    packet["evidence_summary_acknowledgements"][0]["citations"] = []

    assert "uncited_evidence_summary_acknowledgement" in _issue_codes(packet)


@pytest.mark.parametrize(
    "missing_field",
    ["blocker_id", "carry_forward_owner", "carry_forward_reason"],
)
def test_missing_unresolved_blocker_carry_forward_fields_are_rejected(missing_field: str) -> None:
    packet = _valid_packet()
    packet["unresolved_blocker_carry_forward"][0].pop(missing_field)

    assert "missing_unresolved_blocker_carry_forward_field" in _issue_codes(packet)


def test_missing_reviewer_decision_row_citation_is_rejected() -> None:
    packet = _valid_packet()
    packet["reviewer_decision_rows"][0]["citations"] = []

    assert "uncited_reviewer_decision" in _issue_codes(packet)


@pytest.mark.parametrize(
    ("field", "expected_code"),
    [
        ("evidence_bundle_references", "uncited_evidence_bundle_reference"),
        ("validation_transcript_review_placeholders", "uncited_validation_transcript_review_placeholder"),
        ("rollback_readiness_confirmations", "uncited_rollback_readiness_confirmation"),
        ("unresolved_risk_notes", "uncited_unresolved_risk_note"),
        ("rollback_readiness_acknowledgements", "uncited_rollback_readiness_acknowledgement"),
        ("validation_replay_acknowledgements", "uncited_validation_replay_acknowledgement"),
    ],
)
def test_uncited_required_review_sections_are_rejected(field: str, expected_code: str) -> None:
    packet = _valid_packet()
    packet[field][0]["citations"] = []

    assert expected_code in _issue_codes(packet)


def test_missing_no_go_reason_placeholder_fields_are_rejected() -> None:
    packet = _valid_packet()
    packet["no_go_reason_placeholders"][0]["reason_placeholder"] = ""

    assert "missing_no_go_reason_placeholder_field" in _issue_codes(packet)


@pytest.mark.parametrize(
    ("key", "value", "expected_code"),
    [
        ("auth_state", "state.json", "private_authenticated_session_or_browser_artifact"),
        ("browser_file", "browser-state.json", "private_authenticated_session_or_browser_artifact"),
        ("session_file", "session.json", "private_authenticated_session_or_browser_artifact"),
        ("screenshot_file", "review.png", "private_authenticated_session_or_browser_artifact"),
        ("trace_file", "trace.zip", "private_authenticated_session_or_browser_artifact"),
        ("har_file", "network.har", "private_authenticated_session_or_browser_artifact"),
        ("raw_crawl_output", "raw fixture bytes", "raw_crawl_pdf_or_downloaded_data"),
        ("downloaded_artifacts", ["guide.pdf"], "raw_crawl_pdf_or_downloaded_data"),
        ("downloaded_pdf", "guide.pdf", "raw_crawl_pdf_or_downloaded_data"),
        ("active_artifact_mutation", True, "active_mutation_flag"),
        ("active_prompt_mutation", "enabled", "active_mutation_flag"),
        ("active_release_state_mutation", True, "active_mutation_flag"),
        ("active_promotion", True, "active_mutation_flag"),
        ("promotion_enabled", True, "active_mutation_flag"),
        ("active_fixture_mutation", True, "active_mutation_flag"),
        ("active_agent_state_mutation", True, "active_mutation_flag"),
    ],
)
def test_artifact_raw_data_and_mutation_fields_are_rejected(key: str, value: object, expected_code: str) -> None:
    packet = _valid_packet()
    packet[key] = value

    assert expected_code in _issue_codes(packet)


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "live execution completed for the reviewer gate",
        "release complete after the offline pass",
        "active promotion is enabled by this packet",
        "official action performed after review",
        "consequential official action authorized",
        "permit will be approved by the city",
        "approval is guaranteed for this case",
        "legally compliant outcome is guaranteed",
        "enter payment details during review",
        "submit the application after review",
        "schedule the inspection from the packet",
        "cancel the inspection from the packet",
        "certify the application in DevHub",
        "upload corrections from this intake row",
        "downloaded artifacts are attached to this row",
    ],
)
def test_unsafe_claims_and_consequential_action_language_are_rejected(unsafe_text: str) -> None:
    packet = _valid_packet()
    packet["reviewer_decision_rows"] = deepcopy(packet["reviewer_decision_rows"])
    packet["reviewer_decision_rows"][0]["rationale"] = unsafe_text

    assert "unsafe_release_intake_text" in _issue_codes(packet)


def test_mutation_flags_map_rejects_active_named_flags() -> None:
    packet = _valid_packet()
    packet["mutation_flags"] = {"artifact": False, "promotion": True}

    assert "active_mutation_flag" in _issue_codes(packet)
