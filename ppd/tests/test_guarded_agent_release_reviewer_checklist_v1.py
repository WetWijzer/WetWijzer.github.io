from __future__ import annotations

from pathlib import Path

import pytest

from ppd.agent_readiness.guarded_agent_release_reviewer_checklist_v1 import (
    GuardedAgentReleaseReviewerChecklistV1Error,
    load_guarded_agent_release_reviewer_checklist_fixture,
    validate_guarded_agent_release_reviewer_checklist_v1,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "guarded_agent_release_reviewer_checklist_v1" / "input_packets.json"


def _valid_packet() -> dict:
    return load_guarded_agent_release_reviewer_checklist_fixture(FIXTURE_PATH)


def test_builds_fixture_first_guarded_agent_release_reviewer_checklist() -> None:
    packet = _valid_packet()

    assert packet["packet_type"] == "ppd.guarded_agent_release_reviewer_checklist.v1"
    assert packet["fixture_first"] is True
    assert packet["metadata_only"] is True
    assert packet["attestations"]["no_fixture_promotion"] is True
    assert packet["attestations"]["no_live_source_crawl"] is True
    assert packet["attestations"]["no_devhub_access"] is True
    assert packet["validation_replay_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    assert validate_guarded_agent_release_reviewer_checklist_v1(packet) == []


def test_outputs_required_reviewer_sections_with_citations() -> None:
    packet = _valid_packet()

    for key in (
        "reviewer_checklist_rows",
        "manual_signoff_placeholders",
        "unresolved_blocker_references",
        "rollback_checkpoints",
        "human_handoff_notes",
    ):
        assert packet[key]
        assert all(row["citations"] for row in packet[key])

    source_packets = {row["source_packet"] for row in packet["reviewer_checklist_rows"]}
    assert "Guarded agent readiness" in source_packets
    assert "Release promotion decision" in source_packets
    assert "Public source refresh plan" in source_packets
    assert "DevHub observed surface plan" in source_packets
    assert any(row["status"] == "unresolved_pending_manual_signoff" for row in packet["unresolved_blocker_references"])


def test_rejects_uncited_rows_missing_replay_and_mutation_flags() -> None:
    packet = _valid_packet()
    packet["reviewer_checklist_rows"][0]["citations"] = []
    packet["manual_signoff_placeholders"][0]["citations"] = []
    packet["unresolved_blocker_references"] = []
    packet["validation_replay_commands"] = []
    packet["active_fixture_promotion"] = True
    packet["active_guardrail_mutation"] = True

    errors = validate_guarded_agent_release_reviewer_checklist_v1(packet)

    assert "reviewer_checklist_rows[0].citations must be non-empty" in errors
    assert "manual_signoff_placeholders[0].citations must be non-empty" in errors
    assert "unresolved_blocker_references must be a non-empty list" in errors
    assert "validation_replay_commands must contain only the PP&D daemon self-test command" in errors
    assert "active_fixture_promotion must be false" in errors
    assert "active_guardrail_mutation must be false" in errors


def test_rejects_private_raw_live_promotion_and_guarantee_text() -> None:
    packet = _valid_packet()
    packet["human_handoff_notes"][0]["note"] = "Do not keep auth_state values."
    packet["human_handoff_notes"][1]["note"] = "Do not include raw PDF material."
    packet["human_handoff_notes"][2]["note"] = "The live crawl completed."
    packet["human_handoff_notes"][3]["note"] = "This was promoted to production."
    packet["reviewer_checklist_rows"][0]["checklist_item"] = "The permit will be approved."

    errors = validate_guarded_agent_release_reviewer_checklist_v1(packet)

    assert any("auth_state" in error for error in errors)
    assert any("raw pdf" in error for error in errors)
    assert any("live crawl completed" in error for error in errors)
    assert any("promoted to production" in error for error in errors)
    assert any("permit will be approved" in error for error in errors)


def test_missing_required_input_fails_closed(tmp_path: Path) -> None:
    fixture = tmp_path / "input_packets.json"
    fixture.write_text('{"guarded_agent_release_readiness_packet_v1": {}}', encoding="utf-8")

    with pytest.raises(GuardedAgentReleaseReviewerChecklistV1Error):
        load_guarded_agent_release_reviewer_checklist_fixture(fixture)
