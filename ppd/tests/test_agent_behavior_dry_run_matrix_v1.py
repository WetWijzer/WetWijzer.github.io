from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.agent_behavior_dry_run_matrix_v1 import validate_agent_behavior_dry_run_matrix_v1


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_behavior_dry_run_matrix_v1.json"

EXPECTED_PACKET_IDS = {
    "guarded-agent-release-readiness-packet-v1",
    "guarded-agent-response-acceptance-packet-v1",
    "user-gap-analysis-impact-proposal-v1",
    "agent-response-delta-proposal-v1",
}

REQUIRED_BEHAVIOR_FOCUSES = {
    "missing_information_prompt",
    "stale_evidence_handling",
    "refusal_language",
    "blocked_action_handling",
    "next_safe_action_recommendations",
}

REQUIRED_INVARIANTS = {
    "does_not_change_prompts",
    "does_not_change_active_guardrails",
    "does_not_change_agent_state",
    "does_not_change_release_state",
    "does_not_change_production_behavior",
    "does_not_use_live_crawl",
    "does_not_use_authenticated_automation",
}


def load_matrix() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def assert_command_list(commands: list[list[str]]) -> None:
    assert isinstance(commands, list)
    assert commands
    for command in commands:
        assert isinstance(command, list)
        assert command
        assert all(isinstance(part, str) and part for part in command)


def test_matrix_consumes_expected_packets() -> None:
    matrix = load_matrix()

    assert matrix["schema_version"] == "agent_behavior_dry_run_matrix.v1"
    assert matrix["mode"] == "offline_fixture_only"
    assert set(matrix["non_behavioral_invariants"]) >= REQUIRED_INVARIANTS

    packet_ids = {packet["packet_id"] for packet in matrix["consumed_packets"]}
    assert packet_ids == EXPECTED_PACKET_IDS

    for packet in matrix["consumed_packets"]:
        assert packet["artifact_ref"] == f"offline:{packet['packet_id']}"
        assert packet["required_fields"]
        assert all(isinstance(field, str) and field for field in packet["required_fields"])


def test_required_behavior_focuses_are_present() -> None:
    matrix = load_matrix()
    focuses = {scenario["behavior_focus"] for scenario in matrix["scenarios"]}
    assert focuses == REQUIRED_BEHAVIOR_FOCUSES


def test_matrix_scenarios_are_cited_and_reviewable() -> None:
    matrix = load_matrix()

    assert matrix["reviewer_owner"]
    assert "no runtime effect" in matrix["rollback_note"] or "no prompts" in matrix["rollback_note"]
    assert_command_list(matrix["validation_commands"])

    for scenario in matrix["scenarios"]:
        assert scenario["scenario_id"].endswith("-v1")
        assert scenario["description"]
        assert scenario["expected_outcome"] in {"pass", "block"}
        assert scenario["reviewer_owner"] == matrix["reviewer_owner"]
        assert "no runtime effect" in scenario["rollback_note"]
        assert_command_list(scenario["validation_commands"])

        input_refs = scenario["input_packet_refs"]
        citations = scenario["offline_citations"]
        assert len(input_refs) >= len(EXPECTED_PACKET_IDS)
        assert len(citations) >= len(EXPECTED_PACKET_IDS)

        for packet_id in EXPECTED_PACKET_IDS:
            assert any(packet_id in ref for ref in input_refs)
            assert any(packet_id in citation for citation in citations)

        assert scenario["expected_agent_behavior"]
        assert all(isinstance(item, str) and item for item in scenario["expected_agent_behavior"])


def test_block_scenarios_include_blocked_actions_or_stale_evidence() -> None:
    matrix = load_matrix()

    block_scenarios = [
        scenario for scenario in matrix["scenarios"] if scenario["expected_outcome"] == "block"
    ]
    assert block_scenarios

    for scenario in block_scenarios:
        fixture_inputs = scenario["fixture_inputs"]
        assert fixture_inputs["blocked_actions"] or fixture_inputs["stale_evidence"]
        assert any(
            behavior.startswith("block")
            or "block" in behavior
            or "stale" in behavior
            for behavior in scenario["expected_agent_behavior"]
        )


def test_fixture_does_not_authorize_live_or_consequential_actions() -> None:
    matrix = load_matrix()
    serialized = json.dumps(matrix, sort_keys=True)

    forbidden_runtime_markers = [
        "session_cookie",
        "auth_state",
        "captcha_solution",
        "payment_detail",
        "submit_payment_allowed",
        "upload_allowed",
        "production_behavior_change",
    ]
    for marker in forbidden_runtime_markers:
        assert marker not in serialized

    for scenario in matrix["scenarios"]:
        fixture_inputs = scenario["fixture_inputs"]
        assert isinstance(fixture_inputs["known_facts"], list)
        assert isinstance(fixture_inputs["missing_facts"], list)
        assert isinstance(fixture_inputs["blocked_actions"], list)
        assert isinstance(fixture_inputs["stale_evidence"], list)


def test_validator_accepts_current_fixture() -> None:
    assert validate_agent_behavior_dry_run_matrix_v1(load_matrix()) == []


def test_validator_rejects_uncited_rows_missing_expected_outcome_owner_and_rollback() -> None:
    matrix = load_matrix()
    row = matrix["scenarios"][0]
    row.pop("offline_citations")
    row.pop("input_packet_refs")
    row.pop("expected_outcome")
    row.pop("reviewer_owner")
    row.pop("rollback_note")

    errors = validate_agent_behavior_dry_run_matrix_v1(matrix)

    assert any("offline_citations is required" in error for error in errors)
    assert any("input_packet_refs is required" in error for error in errors)
    assert any("expected_outcome must be pass or block" in error for error in errors)
    assert any("reviewer_owner is required" in error for error in errors)
    assert any("rollback_note is required" in error for error in errors)


def test_validator_rejects_missing_required_behavior_coverage() -> None:
    matrix = load_matrix()
    matrix["scenarios"] = [
        scenario
        for scenario in matrix["scenarios"]
        if scenario["behavior_focus"] not in {"missing_information_prompt", "refusal_language"}
    ]

    errors = validate_agent_behavior_dry_run_matrix_v1(matrix)

    assert any("missing_information_prompt" in error for error in errors)
    assert any("refusal_language" in error for error in errors)


def test_validator_rejects_private_authenticated_session_browser_and_raw_artifacts() -> None:
    matrix = load_matrix()
    matrix["scenarios"][0]["notes"] = "private artifact from authenticated DevHub page"
    matrix["scenarios"][1]["notes"] = "session cookie and browser state were captured"
    matrix["scenarios"][2]["notes"] = "raw PDF downloaded document from crawl output"

    errors = validate_agent_behavior_dry_run_matrix_v1(matrix)

    assert any("private_or_authenticated_artifact" in error for error in errors)
    assert any("session_or_browser_artifact" in error for error in errors)
    assert any("raw_crawl_pdf_or_downloaded_data" in error for error in errors)


def test_validator_rejects_live_execution_guarantee_and_consequential_action_language() -> None:
    matrix = load_matrix()
    matrix["scenarios"][0]["notes"] = "Ran live automation and completed live execution."
    matrix["scenarios"][1]["notes"] = "Approval guaranteed and permit will be issued."
    matrix["scenarios"][2]["notes"] = "Agent will submit the permit and execute payment."

    errors = validate_agent_behavior_dry_run_matrix_v1(matrix)

    assert any("live_execution_claim" in error for error in errors)
    assert any("legal_or_permitting_outcome_guarantee" in error for error in errors)
    assert any("consequential_action_language" in error for error in errors)


def test_validator_rejects_active_prompt_guardrail_user_gap_release_fixture_and_agent_state_mutation_flags() -> None:
    blocked_flags = {
        "active_prompt_mutation": True,
        "active_guardrail_mutation": True,
        "active_user_gap_mutation": True,
        "active_release_state_mutation": True,
        "active_fixture_mutation": True,
        "active_agent_state_mutation": True,
    }

    for key, value in blocked_flags.items():
        matrix = load_matrix()
        matrix[key] = value
        errors = validate_agent_behavior_dry_run_matrix_v1(matrix)
        assert any("active_mutation_flag" in error for error in errors), key


def test_validator_rejects_nested_active_mutation_flags_without_mutating_fixture() -> None:
    matrix = load_matrix()
    original = copy.deepcopy(matrix)
    matrix["scenarios"][0]["fixture_inputs"]["prompt_mutation_active"] = True
    matrix["scenarios"][1]["fixture_inputs"]["guardrail_mutation_active"] = True
    matrix["scenarios"][2]["fixture_inputs"]["user_gap_mutation_active"] = True

    errors = validate_agent_behavior_dry_run_matrix_v1(matrix)

    assert any("prompt_mutation_active" in error for error in errors)
    assert any("guardrail_mutation_active" in error for error in errors)
    assert any("user_gap_mutation_active" in error for error in errors)
    assert original == load_matrix()
