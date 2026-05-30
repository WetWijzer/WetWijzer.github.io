from __future__ import annotations

from pathlib import Path

import pytest

from ppd.devhub.attended_observation_prep_packet_v1 import (
    PREP_PACKET_VERSION,
    assert_valid_attended_observation_prep_packet_v1,
    build_attended_observation_prep_packet_v1,
    load_json_packet,
    validate_attended_observation_prep_packet_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "attended_observation_prep_packet_v1_backlog.json"


def test_builds_ordered_manual_attendance_prep_rows_from_backlog_fixture() -> None:
    backlog = load_json_packet(FIXTURE_PATH)

    packet = build_attended_observation_prep_packet_v1(backlog)

    assert packet["packet_version"] == PREP_PACKET_VERSION
    assert packet["source_backlog_packet_id"] == backlog["packet_id"]
    assert [row["order"] for row in packet["manual_attendance_preflight_rows"]] == [1, 2, 3]
    assert [row["source_work_item_id"] for row in packet["manual_attendance_preflight_rows"]] == [
        "observe-synthetic-devhub-home",
        "observe-synthetic-permit-status-detail",
        "observe-synthetic-fee-notice-review",
    ]
    assert validate_attended_observation_prep_packet_v1(packet) == []


def test_packet_exposes_required_operator_prep_sections() -> None:
    packet = build_attended_observation_prep_packet_v1(load_json_packet(FIXTURE_PATH))

    assert {target["surface"] for target in packet["allowed_read_only_surface_targets"]} == {
        "synthetic_devhub_home",
        "synthetic_permit_status_detail",
        "synthetic_fee_notice_review",
    }
    assert packet["redaction_inventory"]
    assert packet["blocked_consequential_action_reminders"]
    assert packet["abort_conditions"]
    assert packet["reviewer_prompts"]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]


def test_packet_blocks_all_artifact_and_official_action_outputs() -> None:
    packet = build_attended_observation_prep_packet_v1(load_json_packet(FIXTURE_PATH))

    assert all(value is False for value in packet["artifact_policy"].values())
    for key in (
        "creates_auth_state",
        "creates_browser_artifacts",
        "creates_har_files",
        "creates_screenshots",
        "creates_traces",
        "captures_private_values",
        "stores_downloads",
        "stores_raw_crawl_output",
        "creates_uploads",
        "creates_submissions",
        "creates_payments",
        "creates_certifications",
        "creates_cancellations",
        "creates_scheduling_artifacts",
    ):
        assert packet["artifact_policy"][key] is False


def test_validator_rejects_missing_required_sections() -> None:
    packet = build_attended_observation_prep_packet_v1(load_json_packet(FIXTURE_PATH))
    packet["reviewer_prompts"] = []

    errors = validate_attended_observation_prep_packet_v1(packet)

    assert "reviewer_prompts must be a non-empty list" in errors


def test_validator_rejects_consequential_language_outside_blocked_reminders() -> None:
    packet = build_attended_observation_prep_packet_v1(load_json_packet(FIXTURE_PATH))
    packet["manual_attendance_preflight_rows"][0]["objective"] = "Submit after observing."

    errors = validate_attended_observation_prep_packet_v1(packet)

    assert any("consequential action language outside blocked reminders" in error for error in errors)


def test_assert_valid_raises_stable_error() -> None:
    packet = build_attended_observation_prep_packet_v1(load_json_packet(FIXTURE_PATH))
    packet["artifact_policy"]["creates_screenshots"] = True

    with pytest.raises(AssertionError, match="artifact_policy.creates_screenshots must be false"):
        assert_valid_attended_observation_prep_packet_v1(packet)
