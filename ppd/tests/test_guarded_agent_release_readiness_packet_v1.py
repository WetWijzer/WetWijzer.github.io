from __future__ import annotations

from pathlib import Path

import pytest

from ppd.agent_readiness.guarded_agent_release_readiness_packet_v1 import (
    GuardedAgentReleaseReadinessPacketV1Error,
    load_guarded_agent_release_readiness_fixture,
    validate_guarded_agent_release_readiness_packet_v1,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "guarded_agent_release_readiness_packet_v1" / "input_packets.json"


def _valid_packet() -> dict:
    return load_guarded_agent_release_readiness_fixture(FIXTURE_PATH)


def test_builds_fixture_first_guarded_agent_release_readiness_packet() -> None:
    packet = _valid_packet()

    assert packet["packet_type"] == "ppd.guarded_agent_release_readiness_packet.v1"
    assert packet["fixture_first"] is True
    assert packet["metadata_only"] is True
    assert packet["attestations"]["no_prompt_changes"] is True
    assert packet["attestations"]["no_active_guardrail_changes"] is True
    assert packet["validation_replay_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    assert validate_guarded_agent_release_readiness_packet_v1(packet) == []


def test_outputs_cited_readiness_expectation_blocker_rollback_and_handoff_rows() -> None:
    packet = _valid_packet()

    row_groups = (
        "agent_facing_readiness_rows",
        "expectation_rows",
        "release_blockers",
        "rollback_checkpoints",
        "human_handoff_notes",
    )
    for row_group in row_groups:
        assert packet[row_group]
        assert all(row["citations"] for row in packet[row_group])

    expectation_types = {row["expectation_type"] for row in packet["expectation_rows"]}
    assert "missing-information expectation" in expectation_types
    assert "refusal expectation" in expectation_types
    assert "next-safe-action expectation" in expectation_types
    assert any(blocker["blocked_release_area"] == "official agent actions" for blocker in packet["release_blockers"])


def test_rejects_uncited_readiness_expectation_blocker_rollback_and_handoff_rows() -> None:
    for row_group in (
        "agent_facing_readiness_rows",
        "expectation_rows",
        "release_blockers",
        "rollback_checkpoints",
        "human_handoff_notes",
    ):
        packet = _valid_packet()
        packet[row_group][0]["citations"] = []

        assert f"{row_group}[0].citations must be non-empty" in validate_guarded_agent_release_readiness_packet_v1(packet)


def test_rejects_missing_expectation_types_release_blockers_validation_and_rollback() -> None:
    packet = _valid_packet()
    packet["expectation_rows"] = [
        row for row in packet["expectation_rows"] if row["expectation_type"] != "refusal expectation"
    ]
    packet["release_blockers"] = []
    packet["validation_replay_commands"] = []
    packet["rollback_checkpoints"] = []

    errors = validate_guarded_agent_release_readiness_packet_v1(packet)

    assert "expectation_rows missing refusal expectation" in errors
    assert "release_blockers must be a non-empty list" in errors
    assert "validation_replay_commands must contain only the PP&D daemon self-test command" in errors
    assert "rollback_checkpoints must be a non-empty list" in errors


def test_rejects_mutation_flags_private_artifacts_and_raw_data() -> None:
    packet = _valid_packet()
    packet["active_prompt_mutation"] = True
    packet["active_guardrail_mutation"] = True
    packet["active_process_mutation"] = True
    packet["active_user_gap_mutation"] = True
    packet["active_release_state_mutation"] = True
    packet["active_fixture_mutation"] = True
    packet["active_agent_state_mutation"] = True
    packet["human_handoff_notes"][0]["note"] = "Do not include auth_state material."
    packet["human_handoff_notes"][1]["note"] = "Do not include raw crawl or downloaded PDF data."

    errors = validate_guarded_agent_release_readiness_packet_v1(packet)

    assert "active_prompt_mutation must be false" in errors
    assert "active_guardrail_mutation must be false" in errors
    assert "active_process_mutation must be false" in errors
    assert "active_user_gap_mutation must be false" in errors
    assert "active_release_state_mutation must be false" in errors
    assert "active_fixture_mutation must be false" in errors
    assert "active_agent_state_mutation must be false" in errors
    assert any(error.startswith("forbidden private_or_authenticated_artifact text") for error in errors)
    assert any(error.startswith("forbidden raw_crawl_pdf_or_downloaded_data text") for error in errors)


def test_rejects_live_execution_promotion_guarantees_and_consequential_action_language() -> None:
    packet = _valid_packet()
    packet["agent_facing_readiness_rows"][0]["agent_facing_use"] = "The live crawl execution completed."
    packet["agent_facing_readiness_rows"][1]["agent_facing_use"] = "Promoted to production."
    packet["expectation_rows"][0]["expected_agent_behavior"] = "The permit will be approved."
    packet["expectation_rows"][1]["expected_agent_behavior"] = "I will submit the permit."

    errors = validate_guarded_agent_release_readiness_packet_v1(packet)

    assert any(error.startswith("forbidden live execution claim") for error in errors)
    assert any(error.startswith("forbidden live promotion claim") for error in errors)
    assert any(error.startswith("forbidden legal or permitting outcome guarantee") for error in errors)
    assert any(error.startswith("forbidden consequential action language") for error in errors)


def test_missing_required_input_fails_closed(tmp_path: Path) -> None:
    fixture = tmp_path / "input_packets.json"
    fixture.write_text('{"release_promotion_decision_packet_v1": {}}', encoding="utf-8")

    with pytest.raises(GuardedAgentReleaseReadinessPacketV1Error):
        load_guarded_agent_release_readiness_fixture(fixture)
