from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.inactive_fixture_promotion_gate_packet_v1 import (
    PACKET_TYPE,
    InactiveFixturePromotionGatePacketV1Error,
    build_inactive_fixture_promotion_gate_packet_v1,
    validate_inactive_fixture_promotion_gate_packet_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "inactive_fixture_promotion_gate_packet_v1"
SELF_TEST_COMMAND = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]


def _fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _valid_packet() -> dict:
    return build_inactive_fixture_promotion_gate_packet_v1(
        inactive_fixture_promotion_application_preview_v1=_fixture("application_preview_v1.json"),
        post_promotion_regression_rehearsal_v1=_fixture("post_promotion_regression_rehearsal_v1.json"),
    )


def test_build_gate_packet_from_offline_fixture_inputs() -> None:
    packet = _valid_packet()

    assert packet["packet_type"] == PACKET_TYPE
    assert packet["fixture_first"] is True
    assert packet["metadata_only"] is True
    assert packet["active_fixture_promotion"] is False
    assert packet["active_prompt_mutation"] is False
    assert packet["active_agent_state_mutation"] is False
    assert packet["active_artifact_mutation"] is False
    assert packet["official_action_performed"] is False
    assert packet["validation_replay_commands"] == SELF_TEST_COMMAND
    assert [row["row_id"] for row in packet["go_no_go_rows"]] == [
        "application-preview-coverage",
        "post-promotion-regression-rehearsal",
        "combined-manual-disposition",
    ]
    assert [row["decision"] for row in packet["go_no_go_rows"]] == ["go", "go", "no_go"]
    assert all(row["reviewer_disposition"]["status"] == "pending_manual_review" for row in packet["go_no_go_rows"])
    assert all(row["rollback_readiness"]["status"] == "ready_no_active_changes" for row in packet["go_no_go_rows"])
    assert validate_inactive_fixture_promotion_gate_packet_v1(packet) == []


def test_validation_rejects_missing_go_no_go_rows() -> None:
    packet = _valid_packet()
    packet.pop("go_no_go_rows")

    assert "go_no_go_rows must be a non-empty list" in validate_inactive_fixture_promotion_gate_packet_v1(packet)


def test_validation_rejects_uncited_source_or_observation_evidence() -> None:
    packet = _valid_packet()
    packet["go_no_go_rows"][0]["source_evidence_ids"] = ["uncited-evidence"]
    packet["source_evidence_coverage"][0]["source_evidence_ids"] = ["uncited-evidence"]

    errors = validate_inactive_fixture_promotion_gate_packet_v1(packet)

    assert "go_no_go_rows[0].source_evidence_ids must cite source or observation evidence" in errors
    assert "source_evidence_coverage[0] must cite source or observation evidence" in errors


def test_validation_rejects_missing_reviewer_disposition_fields() -> None:
    packet = _valid_packet()
    packet["go_no_go_rows"][0]["reviewer_disposition"] = {"status": "pending_manual_review"}
    packet["reviewer_disposition_fields"][0]["required_fields"] = ["status"]

    errors = validate_inactive_fixture_promotion_gate_packet_v1(packet)

    assert "go_no_go_rows[0].reviewer_disposition is missing required fields" in errors
    assert "reviewer_disposition_fields[0] must require status, reviewer, reviewed_at, and notes" in errors


def test_validation_rejects_missing_rollback_readiness_and_replay_commands() -> None:
    packet = _valid_packet()
    packet["go_no_go_rows"][0].pop("rollback_readiness")
    packet["go_no_go_rows"][1]["validation_replay_commands"] = []
    packet["rollback_readiness"] = []
    packet["validation_replay_commands"] = []

    errors = validate_inactive_fixture_promotion_gate_packet_v1(packet)

    assert "validation_replay_commands must contain the PP&D daemon self-test command" in errors
    assert "go_no_go_rows[0].rollback_readiness is required" in errors
    assert "go_no_go_rows[1].validation_replay_commands must replay self-test" in errors
    assert "rollback_readiness must be a non-empty list" in errors


def test_validation_rejects_private_raw_browser_session_and_downloaded_artifacts() -> None:
    packet = _valid_packet()
    packet["browser_trace_path"] = "trace.zip"
    packet["session_storage"] = {"token": "redacted-but-not-allowed"}
    packet["raw_pdf"] = "not allowed"
    packet["downloaded_document"] = "permit.pdf"

    errors = validate_inactive_fixture_promotion_gate_packet_v1(packet)

    assert any("browser_trace_path" in error for error in errors)
    assert any("session_storage" in error for error in errors)
    assert any("raw_pdf" in error for error in errors)
    assert any("downloaded_document" in error for error in errors)


def test_validation_rejects_live_promotion_outcome_and_consequential_language() -> None:
    packet = _valid_packet()
    packet["live_execution_completed"] = True
    packet["notes"] = "Promotion complete. Permit approval is guaranteed. Submit the application."

    errors = validate_inactive_fixture_promotion_gate_packet_v1(packet)

    assert any("live_execution_completed" in error for error in errors)
    assert any("outcome guarantee" in error for error in errors)


def test_validation_rejects_active_mutation_flags() -> None:
    packet = _valid_packet()
    for flag in (
        "active_fixture_promotion",
        "active_artifact_mutation",
        "active_release_state_mutation",
        "active_prompt_mutation",
        "active_agent_state_mutation",
    ):
        mutated = deepcopy(packet)
        mutated[flag] = True
        assert f"{flag} must be false" in validate_inactive_fixture_promotion_gate_packet_v1(mutated)


def test_builder_rejects_private_or_raw_payload_keys() -> None:
    application_preview = _fixture("application_preview_v1.json")
    application_preview["raw_pdf"] = "not allowed"

    with pytest.raises(InactiveFixturePromotionGatePacketV1Error) as excinfo:
        build_inactive_fixture_promotion_gate_packet_v1(
            inactive_fixture_promotion_application_preview_v1=application_preview,
            post_promotion_regression_rehearsal_v1=_fixture("post_promotion_regression_rehearsal_v1.json"),
        )

    assert "raw" in str(excinfo.value)
