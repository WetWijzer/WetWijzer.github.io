from __future__ import annotations

import json
from pathlib import Path

from ppd.requirement_regeneration_promotion_approval import build_approval_packet


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "requirement_regeneration_promotion_approval"


def _load_json(name: str):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_build_approval_packet_matches_fixture() -> None:
    packets = _load_json("input_packets.json")
    expected = _load_json("approval_packet.json")

    actual = build_approval_packet(
        packets["candidate_packet"],
        packets["release_blocker_packet"],
        packets["freshness_packet"],
    )

    assert actual == expected


def test_approval_packet_contains_required_no_mutation_attestations() -> None:
    packets = _load_json("input_packets.json")
    packet = build_approval_packet(
        packets["candidate_packet"],
        packets["release_blocker_packet"],
        packets["freshness_packet"],
    )

    assert packet["attestations"] == {
        "no_active_requirement_mutation": True,
        "no_active_process_mutation": True,
        "no_active_guardrail_mutation": True,
        "no_active_prompt_mutation": True,
        "no_active_release_mutation": True,
    }
    assert packet["expected_offline_validation_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    assert {decision["decision"] for decision in packet["decisions"]} == {"approve", "defer"}
    assert all(decision["reviewer_signoff"]["required"] for decision in packet["decisions"])
