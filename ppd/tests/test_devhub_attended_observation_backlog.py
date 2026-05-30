from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.devhub.attended_observation_backlog import (
    FORBIDDEN_ARTIFACT_TYPES,
    PACKET_VERSION,
    build_observation_backlog_packet,
    validate_observation_backlog_packet,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "attended_observation_backlog_v1.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_builds_ordered_attended_readonly_backlog_packet_from_fixture() -> None:
    packet = build_observation_backlog_packet(load_fixture())

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["mode"] == "fixture_first_attended_read_only_observation"
    assert packet["artifact_policy"] == {
        "creates_session_state": False,
        "creates_traces": False,
        "creates_screenshots": False,
        "creates_har_files": False,
        "creates_auth_files": False,
        "captures_private_values": False,
        "creates_official_action_artifacts": False,
    }

    work_items = packet["work_items"]
    assert [item["order"] for item in work_items] == [1, 2, 3, 4, 5]
    assert [item["surface_id"] for item in work_items] == [
        "devhub_home",
        "my_permits_requests",
        "permit_detail_status",
        "fee_notice_review",
        "attachments_and_inspections_review",
    ]
    assert all(item["safe_read_only_evidence_needs"] for item in work_items)
    assert all(item["redaction_requirements"] for item in work_items)
    assert all(item["manual_attendance_checkpoints"] for item in work_items)
    assert all(item["blocked_consequential_actions"] for item in work_items)
    assert all(item["offline_validation_commands"] for item in work_items)
    assert validate_observation_backlog_packet(packet) == []


def test_packet_never_requests_forbidden_artifacts() -> None:
    packet = build_observation_backlog_packet(load_fixture())
    serialized = json.dumps(packet, sort_keys=True)

    forbidden_tokens = {
        "session_state",
        "trace.zip",
        "screenshot.png",
        "network.har",
        "storage_state.json",
        "cookie",
        "password",
        "private_value",
        "raw_authenticated_html",
    }
    assert forbidden_tokens.isdisjoint(serialized.split())
    for artifact_type in FORBIDDEN_ARTIFACT_TYPES:
        assert artifact_type not in packet.get("requested_artifacts", [])


def test_rejects_fixture_that_requests_forbidden_capture_artifacts() -> None:
    fixture = load_fixture()
    fixture["synthetic_surfaces"][0]["requested_artifacts"] = ["screenshot", "har"]

    with pytest.raises(ValueError, match="forbidden artifacts"):
        build_observation_backlog_packet(fixture)


def test_rejects_non_readonly_observation_action() -> None:
    fixture = load_fixture()
    fixture["synthetic_surfaces"][0]["allowed_observations"] = ["submit_application"]

    with pytest.raises(ValueError, match="non-read-only observation"):
        build_observation_backlog_packet(fixture)


def test_rejects_blocked_action_without_consequential_classification() -> None:
    fixture = load_fixture()
    fixture["synthetic_surfaces"][0]["blocked_consequential_actions"] = ["open help text"]

    with pytest.raises(ValueError, match="consequential classification"):
        build_observation_backlog_packet(fixture)
