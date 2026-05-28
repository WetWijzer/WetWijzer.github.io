from __future__ import annotations

import json
from pathlib import Path

from ppd.devhub.post_action_hardening import validate_hardening_review_packet


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub"
    / "post_action_hardening"
    / "synthetic_attended_preview_packet.json"
)


def load_packet() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_synthetic_attended_preview_packet_is_valid() -> None:
    packet = load_packet()

    result = validate_hardening_review_packet(packet)

    assert result.valid, result.errors


def test_packet_requires_source_backed_outcome_evidence() -> None:
    packet = load_packet()
    packet["source_backed_outcome_evidence"] = []

    result = validate_hardening_review_packet(packet)

    assert not result.valid
    assert "source_backed_outcome_evidence must not be empty" in result.errors


def test_packet_rejects_clicked_or_filled_controls_as_completion_evidence() -> None:
    packet = load_packet()
    packet["source_backed_outcome_evidence"][0]["observed_preview_fact"] = "Clicked the Save for later button."
    packet["source_backed_outcome_evidence"][0]["supports_outcome"] = "Filled the address field."

    result = validate_hardening_review_packet(packet)

    assert not result.valid
    assert any("cannot be only clicked or filled control evidence" in error for error in result.errors)
    assert any("not only a control interaction" in error for error in result.errors)


def test_packet_blocks_all_required_consequential_followups() -> None:
    packet = load_packet()
    packet["blocked_consequential_followups"] = [
        item for item in packet["blocked_consequential_followups"] if item["action_id"] != "schedule-inspection"
    ]

    result = validate_hardening_review_packet(packet)

    assert not result.valid
    assert any("missing required official action blocks" in error and "schedule-inspection" in error for error in result.errors)


def test_next_actions_are_read_only_or_local_preview_only() -> None:
    packet = load_packet()
    packet["next_safe_actions"].append(
        {
            "action_id": "unsafe-submit",
            "category": "consequential",
            "label": "Submit the draft",
            "requires_attended_browser": True,
            "changes_official_record": True,
            "sourceEvidenceIds": ["official-devhub-guide-submit-permit-application"],
            "citation": "Official DevHub permit application guide.",
        }
    )

    result = validate_hardening_review_packet(packet)

    assert not result.valid
    assert "next_safe_actions[2].category must be read_only or local_preview" in result.errors
    assert "next_safe_actions[2].requires_attended_browser must be false" in result.errors
    assert "next_safe_actions[2].changes_official_record must be false" in result.errors
    assert any("must not propose upload" in error for error in result.errors)


def test_next_actions_require_citations() -> None:
    packet = load_packet()
    packet["next_safe_actions"][0].pop("sourceEvidenceIds")
    packet["next_safe_actions"][0].pop("citation")

    result = validate_hardening_review_packet(packet)

    assert not result.valid
    assert "next_safe_actions[0].sourceEvidenceIds is required" in result.errors
    assert "next_safe_actions[0].citation is required" in result.errors


def test_packet_rejects_private_artifact_references() -> None:
    packet = load_packet()
    packet["journal_linkage"]["unsafe_note"] = "stored screenshot path"

    result = validate_hardening_review_packet(packet)

    assert not result.valid
    assert any("private or disallowed value appears" in error for error in result.errors)


def test_packet_rejects_raw_authenticated_text_and_payment_detail_keys() -> None:
    packet = load_packet()
    packet["journal_linkage"]["raw_authenticated_text"] = "raw authenticated text from an account page"
    packet["journal_linkage"]["payment_card_number"] = "4111111111111111"

    result = validate_hardening_review_packet(packet)

    assert not result.valid
    assert any("private browser artifact key" in error for error in result.errors)
    assert any("private value key" in error for error in result.errors)


def test_packet_rejects_official_action_completion_claim() -> None:
    packet = load_packet()
    packet["action"]["action_id"] = "submit-payment"

    result = validate_hardening_review_packet(packet)

    assert not result.valid
    assert any("must not claim completion of official upload" in error for error in result.errors)
