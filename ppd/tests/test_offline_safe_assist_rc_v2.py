from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.release.offline_safe_assist_rc_v2 import (
    assert_valid_release_candidate_packet,
    build_release_candidate_packet,
    validate_release_candidate_packet,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "offline_safe_assist_rc_v2"


def test_release_candidate_packet_consumes_all_required_fixtures() -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)

    assert packet["packet_id"] == "offline-safe-assist-release-candidate-packet-v2"
    assert set(packet["fixture_inputs"]) == {
        "prompt_refresh_release_handoff",
        "draft_preview_agent_handoff_acceptance",
        "guardrail_refresh_regression_matrix",
        "surface_registry_refresh_acceptance",
        "release_rollback_readiness",
    }
    for fixture_input in packet["fixture_inputs"].values():
        assert fixture_input["citation"].endswith(":v2")


def test_release_candidate_notes_are_cited_by_domain() -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)

    expected_note_keys = {
        "candidate_source_notes",
        "candidate_process_notes",
        "candidate_guardrail_notes",
        "candidate_surface_notes",
        "candidate_prompt_compatibility_notes",
        "candidate_rollback_notes",
    }
    assert set(packet["notes"]) == expected_note_keys
    for note in packet["notes"].values():
        assert note["summary"]
        assert note["citations"]


def test_consequential_actions_are_blocked_until_attended_exact_confirmation() -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)
    gates = {gate["action"]: gate for gate in packet["blocked_consequential_action_gates"]}

    for action in [
        "submit permit request",
        "certify acknowledgement",
        "upload correction to official record",
        "schedule inspection",
        "pay fees",
        "final payment execution",
        "official correction upload",
        "inspection scheduling",
        "permit cancellation or withdrawal",
        "purchase trade permit",
        "cancel permit request",
    ]:
        assert gates[action]["status"] == "blocked_until_user_attended_exact_confirmation"
        assert gates[action]["citations"]


def test_rollback_prerequisites_validation_commands_and_attestations_are_offline_safe() -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)

    assert "blocked consequential-action gates are present" in packet["rollback_prerequisites"]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]
    assert packet["attestations"] == {
        "no_live_release": True,
        "no_live_devhub": True,
        "no_llm": True,
        "no_crawler": True,
        "no_processor": True,
        "no_release_state_mutation": True,
    }
    assert packet["mutation_flags"] == {
        "source_mutation_active": False,
        "process_mutation_active": False,
        "guardrail_mutation_active": False,
        "surface_registry_mutation_active": False,
        "prompt_mutation_active": False,
        "monitoring_mutation_active": False,
        "release_state_mutation_active": False,
        "agent_state_mutation_active": False,
    }


def test_release_candidate_packet_passes_fail_closed_validation() -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)

    result = validate_release_candidate_packet(packet)

    assert result.valid, result.problems
    assert_valid_release_candidate_packet(packet)


def test_validation_rejects_uncited_compatibility_notes() -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)
    packet["notes"]["candidate_prompt_compatibility_notes"]["citations"] = []

    result = validate_release_candidate_packet(packet)

    assert not result.valid
    assert any("uncited compatibility note" in problem for problem in result.problems)


@pytest.mark.parametrize(
    ("mutator", "expected_problem"),
    [
        (
            lambda packet: packet.__setitem__("blocked_consequential_action_gates", []),
            "blocked_consequential_action_gates must be present",
        ),
        (
            lambda packet: packet.__setitem__("rollback_prerequisites", []),
            "rollback_prerequisites must be present",
        ),
        (
            lambda packet: packet.__setitem__("offline_validation_commands", []),
            "offline_validation_commands must be present",
        ),
    ],
)
def test_validation_rejects_missing_gates_rollback_or_offline_commands(mutator, expected_problem: str) -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)
    mutator(packet)

    result = validate_release_candidate_packet(packet)

    assert not result.valid
    assert expected_problem in result.problems


@pytest.mark.parametrize(
    ("path", "value", "expected_fragment"),
    [
        (("private_fact",), "owner phone from authenticated account", "private or authenticated fact"),
        (("raw_pdf",), "raw PDF session artifact", "raw crawl, PDF, browser, or session artifact"),
        (("notes", "candidate_source_notes", "summary"), "Live DevHub execution completed.", "live release, DevHub, browser, LLM, crawler, or processor execution claim"),
        (("notes", "candidate_process_notes", "summary"), "Permit will be approved.", "legal or permitting outcome guarantee"),
        (("notes", "candidate_guardrail_notes", "summary"), "Final payment completed in DevHub.", "final submission, payment, upload, scheduling, or cancellation language"),
        (("active_source_mutation",), True, "active mutation flag must be false"),
        (("mutation_flags", "agent_state_mutation_active"), True, "active mutation flag must be false"),
    ],
)
def test_validation_rejects_private_artifacts_live_claims_guarantees_final_actions_and_mutations(
    path: tuple[str, ...], value: object, expected_fragment: str
) -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)
    _assign(packet, path, value)

    result = validate_release_candidate_packet(packet)

    assert not result.valid
    assert any(expected_fragment in problem for problem in result.problems)


def test_validation_rejects_validation_commands_that_invoke_live_tools() -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)
    packet["offline_validation_commands"] = [["python3", "ppd/crawler/live_public_scrape.py"]]

    result = validate_release_candidate_packet(packet)

    assert not result.valid
    assert any("offline_validation_commands[0] invokes non-offline capability" in problem for problem in result.problems)


def test_validation_rejects_missing_specific_blocked_action_gate() -> None:
    packet = build_release_candidate_packet(FIXTURE_DIR)
    packet["blocked_consequential_action_gates"] = [
        gate for gate in packet["blocked_consequential_action_gates"] if "certify" not in gate["action"]
    ]

    result = validate_release_candidate_packet(packet)

    assert not result.valid
    assert "missing blocked-action gate for certify" in result.problems


def _assign(packet: dict[str, object], path: tuple[str, ...], value: object) -> None:
    target: dict[str, object] = packet
    for key in path[:-1]:
        target = target[key]  # type: ignore[assignment,index]
    target[path[-1]] = deepcopy(value)
