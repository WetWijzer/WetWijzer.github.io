from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.post_preview_human_review_handoff_packet_v2 import (
    OFFLINE_VALIDATION_COMMANDS,
    PACKET_VERSION,
    REQUIRED_TABLE_VERSION,
    build_post_preview_handoff_packet_v2,
    validate_post_preview_handoff_packet_v2,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "post_preview_human_review_handoff_v2"
    / "guarded_action_preflight_decision_table_v2.json"
)


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_builds_ordered_packet_from_guarded_action_preflight_decision_table_v2() -> None:
    packet = build_post_preview_handoff_packet_v2(load_fixture())

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["source_decision_table_version"] == REQUIRED_TABLE_VERSION
    assert [item["action_id"] for item in packet["reviewer_prompts"]] == [
        "draft_preview_values",
        "confirm_contractor_license_context",
        "submit_or_pay_devhub",
    ]
    assert packet["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS


def test_packet_contains_required_reviewer_handoff_sections() -> None:
    packet = build_post_preview_handoff_packet_v2(load_fixture())

    assert packet["evidence_summaries"]
    assert packet["unresolved_missing_fact_prompts"] == [
        {
            "action_id": "confirm_contractor_license_context",
            "prompt": "Ask the user for the missing fact without collecting private values: Whether the applicant is proceeding as owner, contractor, or authorized representative.",
        }
    ]
    issue_types = {item["issue_type"] for item in packet["stale_conflicting_evidence_prompts"]}
    assert issue_types == {"stale", "conflicting"}
    assert packet["blocked_consequential_action_reminders"] == [
        {
            "action_id": "submit_or_pay_devhub",
            "reminder": "Do not upload, submit, certify, pay, schedule, cancel, change an account, or activate a release from this packet.",
        }
    ]
    attendance_action_ids = {item["action_id"] for item in packet["user_attendance_reminders"]}
    assert attendance_action_ids == {"confirm_contractor_license_context", "submit_or_pay_devhub"}


def test_packet_validation_rejects_private_or_session_like_keys() -> None:
    table = load_fixture()
    table["actions"][0]["session_token"] = "redacted-but-not-allowed"

    with pytest.raises(ValueError, match="private or session-like key"):
        build_post_preview_handoff_packet_v2(table)


def test_packet_validation_rejects_unexpected_validation_commands() -> None:
    packet = build_post_preview_handoff_packet_v2(load_fixture())
    packet["offline_validation_commands"] = [["python3", "unexpected.py"]]

    with pytest.raises(ValueError, match="offline validation commands"):
        validate_post_preview_handoff_packet_v2(packet)
