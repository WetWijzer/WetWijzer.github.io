from __future__ import annotations

from pathlib import Path

import pytest

from ppd.devhub.attended_readonly_preflight_packet_v2 import (
    ABORT_CONDITIONS,
    CONSUMES_PACKET_VERSION,
    OFFLINE_VALIDATION_COMMANDS,
    PACKET_VERSION,
    build_attended_readonly_preflight_packet_v2,
    build_from_fixture,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub_attended_readonly_preflight_packet_v2"
    / "post_preview_handoff_packet_v2.json"
)


def test_builds_fixture_first_preflight_packet_without_live_side_effects() -> None:
    packet = build_from_fixture(FIXTURE_PATH)

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["consumes_packet_version"] == CONSUMES_PACKET_VERSION
    assert packet["mode"] == "offline_fixture_first_preflight_only"
    assert packet["live_devhub_opened"] is False
    assert packet["auth_state_created"] is False
    assert packet["browser_or_session_artifacts_created"] is False
    assert packet["live_automation_performed"] is False


def test_manual_login_readiness_checks_are_ordered_and_include_handoff_items() -> None:
    packet = build_from_fixture(FIXTURE_PATH)
    checks = packet["ordered_manual_login_readiness_checks"]

    assert [check["order"] for check in checks] == list(range(1, len(checks) + 1))
    assert checks[0]["check_id"] == "offline_fixture_source_confirmed"
    assert checks[-1]["check_id"] == "handoff_review_items_resolved"
    assert checks[-1]["handoff_review_item_count"] == 3
    assert [item["order"] for item in packet["post_preview_handoff_review_items"]] == [1, 2, 3]
    assert all(item["blocks_if_missing"] for item in packet["post_preview_handoff_review_items"])


def test_allowed_destinations_attendance_redaction_and_abort_rules_are_present() -> None:
    packet = build_from_fixture(FIXTURE_PATH)

    destination_categories = {
        destination["category"]
        for destination in packet["allowed_read_only_destination_categories"]
    }
    assert "authenticated_home_or_dashboard" in destination_categories
    assert "payment_due_summary_without_payment_entry" in destination_categories

    attendance_text = " ".join(packet["required_user_attendance_statements"]).lower()
    assert "user remains present" in attendance_text
    assert "mfa" in attendance_text
    assert "captcha" in attendance_text

    redaction_text = " ".join(packet["redaction_requirements"]).lower()
    assert "credentials" in redaction_text
    assert "auth state" in redaction_text
    assert "screenshots" in redaction_text
    assert "payment details" in redaction_text

    abort_condition_names = {condition["condition"] for condition in ABORT_CONDITIONS}
    assert "mfa_or_security_prompt_presented" in abort_condition_names
    assert "captcha_or_bot_challenge_presented" in abort_condition_names
    assert "account_creation_or_registration_path_presented" in abort_condition_names
    assert "payment_entry_or_checkout_path_presented" in abort_condition_names
    assert "upload_submit_certify_schedule_cancel_or_final_action_presented" in abort_condition_names


def test_no_private_artifact_commitments_and_exact_offline_validation_commands() -> None:
    packet = build_from_fixture(FIXTURE_PATH)

    commitments = " ".join(packet["no_private_artifact_commitments"]).lower()
    assert "no devhub browser is opened" in commitments
    assert "no credentials" in commitments
    assert "no live authenticated automation" in commitments
    assert packet["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]


def test_rejects_wrong_handoff_packet_version() -> None:
    with pytest.raises(ValueError, match="expected packet_version"):
        build_attended_readonly_preflight_packet_v2(
            {
                "packet_version": "wrong_version",
                "packet_id": "bad-fixture",
            }
        )
