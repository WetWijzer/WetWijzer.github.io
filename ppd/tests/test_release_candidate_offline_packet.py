from pathlib import Path

import pytest

from ppd.release_candidate import (
    PacketAssemblyError,
    assemble_release_candidate_packet,
    assert_valid_release_candidate_packet,
    load_fixture_packet,
    validate_release_candidate_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "release_candidate_assembly"


def test_assembles_fixture_first_release_candidate_packet() -> None:
    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")

    assembled = assemble_release_candidate_packet(source_packet)

    assert assembled["packet_type"] == "offline_release_candidate_assembly"
    assert assembled["mode"] == "fixture_first_offline"
    assert assembled["release_ready"] is True
    assert assembled["residual_blockers"] == []
    assert assembled["attestations"] == {
        "no_crawl_performed": True,
        "no_processor_executed": True,
        "no_devhub_session_started": True,
        "no_prompt_invoked": True,
        "no_guardrail_compiled": True,
        "no_release_mutation_performed": True,
    }
    assert assembled["validation_command_set"] == [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]
    ]
    assert validate_release_candidate_packet(assembled) == []

    decisions = assembled["release_inclusion_decisions"]
    assert [decision["decision_id"] for decision in decisions] == [
        "public_source_refresh",
        "requirement_regeneration",
        "agent_readiness",
        "devhub_read_only_pilot",
    ]
    assert all(decision["included"] is True for decision in decisions)
    assert all(decision["citations"] for decision in decisions)

    rollback_owners = assembled["rollback_owner_fields"]
    assert set(rollback_owners) == {
        "public_source_refresh",
        "requirement_regeneration",
        "agent_readiness",
        "devhub_read_only_pilot",
    }
    assert rollback_owners["devhub_read_only_pilot"]["rollback_action"].startswith("Disable DevHub pilot inclusion")


def test_residual_blocker_excludes_decision_and_carries_citation_and_status() -> None:
    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    source_packet["packets"][2]["residual_blockers"] = [
        {
            "blocker_id": "agent-smoke:blocker",
            "status": "unresolved",
            "description": "Final smoke output is missing a cited action gate assertion.",
            "owner": "PPD agent readiness owner",
        }
    ]

    assembled = assemble_release_candidate_packet(source_packet)

    assert assembled["release_ready"] is False
    agent_decision = next(
        decision for decision in assembled["release_inclusion_decisions"] if decision["decision_id"] == "agent_readiness"
    )
    assert agent_decision["included"] is False
    assert assembled["residual_blockers"] == [
        {
            "blocker_id": "agent-smoke:blocker",
            "status": "unresolved",
            "description": "Final smoke output is missing a cited action gate assertion.",
            "owner": "PPD agent readiness owner",
            "source_packet_type": "agent_readiness_final_smoke",
            "citations": [
                "agent-smoke:offline-gap-analysis",
                "agent-smoke:action-gate-checks",
            ],
        }
    ]


def test_requires_offline_non_mutation_attestations() -> None:
    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    source_packet["attestations"]["no_devhub_session_started"] = False

    with pytest.raises(PacketAssemblyError, match="no_devhub_session_started"):
        assemble_release_candidate_packet(source_packet)


def test_requires_all_four_source_packets() -> None:
    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    source_packet["packets"] = source_packet["packets"][:-1]

    with pytest.raises(PacketAssemblyError, match="devhub_attended_read_only_pilot_evidence_review"):
        assemble_release_candidate_packet(source_packet)


def test_rejects_uncited_inclusion_decisions_and_missing_consumed_packet_refs() -> None:
    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    assembled = assemble_release_candidate_packet(source_packet)
    assembled["assembled_from"] = assembled["assembled_from"][:-1]
    assembled["release_inclusion_decisions"][0]["citations"] = []

    problems = validate_release_candidate_packet(assembled)

    assert any("assembled_from is missing" in problem for problem in problems)
    assert any("release_inclusion_decisions[0] lacks citations" in problem for problem in problems)


def test_rejects_missing_validation_commands_and_rollback_owners() -> None:
    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    source_packet["packets"][0]["validation_commands"] = []

    with pytest.raises(PacketAssemblyError, match="validation_commands"):
        assemble_release_candidate_packet(source_packet)

    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    del source_packet["packets"][0]["rollback_owner"]

    with pytest.raises(PacketAssemblyError, match="rollback_owner"):
        assemble_release_candidate_packet(source_packet)


def test_rejects_residual_blockers_without_status() -> None:
    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    source_packet["packets"][1]["residual_blockers"] = [
        {
            "blocker_id": "requirement:blocker",
            "description": "Owner must decide whether the regenerated guardrail stays deferred.",
        }
    ]

    with pytest.raises(PacketAssemblyError, match="must include status"):
        assemble_release_candidate_packet(source_packet)


def test_rejects_raw_private_live_guarantee_and_mutation_content() -> None:
    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    source_packet["packets"][0]["raw_body"] = "raw fixture"

    with pytest.raises(PacketAssemblyError, match="private or raw artifact"):
        assemble_release_candidate_packet(source_packet)

    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    source_packet["packets"][0]["note"] = "The live processor executed against current sources."

    with pytest.raises(PacketAssemblyError, match="live crawler, processor, DevHub, or LLM"):
        assemble_release_candidate_packet(source_packet)

    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    source_packet["packets"][0]["note"] = "This guarantees permit approval."

    with pytest.raises(PacketAssemblyError, match="outcome guarantee"):
        assemble_release_candidate_packet(source_packet)

    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    source_packet["packets"][0]["active_source_mutation"] = True

    with pytest.raises(PacketAssemblyError, match="active mutation"):
        assemble_release_candidate_packet(source_packet)


def test_assert_valid_rejects_incomplete_assembled_packet() -> None:
    source_packet = load_fixture_packet(FIXTURE_DIR / "input_packets.json")
    assembled = assemble_release_candidate_packet(source_packet)
    assembled["rollback_owner_fields"].pop("agent_readiness")

    with pytest.raises(PacketAssemblyError, match="rollback_owner_fields.agent_readiness"):
        assert_valid_release_candidate_packet(assembled)
