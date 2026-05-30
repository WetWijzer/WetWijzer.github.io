from __future__ import annotations

from pathlib import Path

from ppd.rollback_activation_decision import build_packet_from_fixture, validate_packet


FIXTURE = Path(__file__).parent / "fixtures" / "rollback_activation_decision" / "source_packets.json"


def test_fixture_builds_no_rollback_decision_packet() -> None:
    packet = build_packet_from_fixture(FIXTURE)

    assert validate_packet(packet) == []
    assert packet["decision"]["rollback_activation"] == "no-rollback"
    assert packet["decision"]["release_state_mutated"] is False
    assert len(packet["trigger_evaluations"]) == 3
    assert all(not item["triggered"] for item in packet["trigger_evaluations"])


def test_packet_carries_required_attestations_and_offline_validation() -> None:
    packet = build_packet_from_fixture(FIXTURE)

    assert packet["attestations"] == {
        "no_live_crawl": True,
        "no_devhub": True,
        "no_prompt": True,
        "no_guardrail_change": True,
        "no_release_state_mutation": True,
    }
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]
    assert packet["reviewer_owner_fields"]["reviewer"] == "ppd-release-reviewer-fixture"
    assert packet["reviewer_owner_fields"]["owner"] == "ppd-release-owner-fixture"
    assert packet["reviewer_owner_fields"]["acknowledgement_count"] == 3
