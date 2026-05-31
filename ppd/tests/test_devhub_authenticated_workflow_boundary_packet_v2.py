from __future__ import annotations

import json
from pathlib import Path

from ppd.devhub.authenticated_workflow_boundary_packet_v2 import (
    ACTION_CATEGORIES,
    PACKET_VERSION,
    assert_valid_packet,
    load_packet,
    validate_packet,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "authenticated_workflow_boundary_packet_v2.json"


def test_fixture_loads_from_test_relative_path() -> None:
    packet = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert packet["version"] == PACKET_VERSION
    assert_valid_packet(packet)


def test_module_load_packet_uses_committed_fixture() -> None:
    packet = load_packet()

    assert packet["packet_id"] == "devhub_authenticated_workflow_boundary_packet_v2_fixture"
    assert validate_packet(packet) == []


def test_packet_covers_all_required_action_categories() -> None:
    packet = load_packet(FIXTURE_PATH)
    categories = {surface["action_category"] for surface in packet["surfaces"]}

    assert categories == ACTION_CATEGORIES


def test_consequential_financial_and_manual_handoff_require_attendance_and_exact_confirmation() -> None:
    packet = load_packet(FIXTURE_PATH)
    gated_categories = {"consequential_official", "financial", "unsupported_manual_handoff"}

    for surface in packet["surfaces"]:
        if surface["action_category"] in gated_categories:
            assert surface["attendance_required"] is True
            assert surface["exact_confirmation_required"] is True
            assert "exact_confirmation_checkpoint" in surface


def test_fixture_declares_only_offline_validation_commands() -> None:
    packet = load_packet(FIXTURE_PATH)

    assert packet["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/devhub/authenticated_workflow_boundary_packet_v2.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_devhub_authenticated_workflow_boundary_packet_v2.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def test_packet_rejects_missing_category() -> None:
    packet = load_packet(FIXTURE_PATH)
    packet["surfaces"] = [surface for surface in packet["surfaces"] if surface["action_category"] != "financial"]

    errors = validate_packet(packet)

    assert "missing action categories: financial" in errors


def test_packet_rejects_ungated_financial_action() -> None:
    packet = load_packet(FIXTURE_PATH)
    for surface in packet["surfaces"]:
        if surface["action_category"] == "financial":
            surface["attendance_required"] = False
            surface["exact_confirmation_required"] = False
            break

    errors = validate_packet(packet)

    assert any(error.endswith("must require attendance") for error in errors)
    assert any(error.endswith("must require exact confirmation") for error in errors)
