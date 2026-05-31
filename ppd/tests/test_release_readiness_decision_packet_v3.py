from __future__ import annotations

import json
from pathlib import Path

from ppd.release_readiness_decision_packet_v3 import (
    build_all_release_readiness_decision_packets_v3,
    build_release_readiness_decision_packet_v3,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "release_readiness_decision_packet_v3" / "scenarios.json"


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_release_readiness_decision_packet_v3_has_only_synthetic_scenarios() -> None:
    fixture = load_fixture()
    packets = build_all_release_readiness_decision_packets_v3()

    assert set(packets) == set(fixture["scenarios"])
    assert set(packets) == {"release-ready", "release-held", "release-rejected"}


def test_release_readiness_decision_packet_v3_sections_and_effects() -> None:
    fixture = load_fixture()
    required_sections = fixture["required_sections"]
    forbidden_effects = fixture["forbidden_effects"]

    for scenario in fixture["scenarios"]:
        packet = build_release_readiness_decision_packet_v3(str(scenario))
        assert packet["packet_version"] == "release-readiness-decision-packet-v3"
        assert packet["scenario"] == scenario

        for section in required_sections:
            assert section in packet
            assert packet[section]

        for key, expected in forbidden_effects.items():
            assert packet[key] is expected


def test_release_readiness_decision_packet_v3_decisions_are_distinct() -> None:
    ready = build_release_readiness_decision_packet_v3("release-ready")
    held = build_release_readiness_decision_packet_v3("release-held")
    rejected = build_release_readiness_decision_packet_v3("release-rejected")

    assert ready["decision"] == {
        "status": "ready",
        "release_allowed": True,
        "hold_required": False,
        "rejection_required": False,
        "basis": "synthetic offline fixture decision packet v3",
    }
    assert held["decision"]["status"] == "held"
    assert held["decision"]["release_allowed"] is False
    assert held["decision"]["hold_required"] is True
    assert held["decision"]["rejection_required"] is False
    assert rejected["decision"]["status"] == "rejected"
    assert rejected["decision"]["release_allowed"] is False
    assert rejected["decision"]["hold_required"] is False
    assert rejected["decision"]["rejection_required"] is True


def test_release_readiness_decision_packet_v3_validation_commands_are_exact_offline_commands() -> None:
    packet = build_release_readiness_decision_packet_v3("release-ready")

    assert packet["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/release_readiness_decision_packet_v3.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_release_readiness_decision_packet_v3.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def test_release_readiness_decision_packet_v3_rejects_unknown_scenario() -> None:
    try:
        build_release_readiness_decision_packet_v3("live-release")
    except ValueError as exc:
        assert "unsupported synthetic scenario" in str(exc)
    else:
        raise AssertionError("unknown scenarios must be rejected")
