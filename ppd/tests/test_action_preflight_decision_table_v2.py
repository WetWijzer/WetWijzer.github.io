from __future__ import annotations

from pathlib import Path

import pytest

from ppd.action_preflight_decision_table_v2 import (
    assert_valid_preflight_decision_table_v2,
    evaluate_preflight_packet,
    load_json_file,
    validate_preflight_decision_table_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "action_preflight_v2"


def test_preflight_decision_table_v2_matches_fixture() -> None:
    packet = load_json_file(FIXTURE_DIR / "reversible_draft_preview_packet_v2.json")
    classifications = load_json_file(FIXTURE_DIR / "action_classification_fixtures.json")
    expected = load_json_file(FIXTURE_DIR / "expected_decisions_v2.json")

    decisions = evaluate_preflight_packet(packet, classifications)

    assert decisions == expected["decisions"]
    assert validate_preflight_decision_table_v2(decisions) == []


def test_blocked_actions_are_ordered_before_manual_or_allow() -> None:
    packet = load_json_file(FIXTURE_DIR / "reversible_draft_preview_packet_v2.json")
    classifications = load_json_file(FIXTURE_DIR / "action_classification_fixtures.json")

    decisions = evaluate_preflight_packet(packet, classifications)
    assert [decision["decision"] for decision in decisions] == [
        "allow-draft",
        "block",
        "manual-handoff",
    ]
    assert decisions[1]["reason"] == "blocked_action_class"
    assert decisions[1]["refused_action_examples"]


def test_decision_table_v2_rejects_missing_required_guardrail_fields() -> None:
    invalid = load_json_file(FIXTURE_DIR / "invalid_missing_required_fields_v2.json")
    expected = load_json_file(FIXTURE_DIR / "expected_missing_required_field_violations_v2.json")

    violations = validate_preflight_decision_table_v2(invalid["decisions"])

    assert [violation["code"] for violation in violations] == expected["codes"]
    with pytest.raises(ValueError, match="invalid guarded action preflight decision table v2"):
        assert_valid_preflight_decision_table_v2(invalid["decisions"])


def test_decision_table_v2_rejects_forbidden_artifacts_claims_and_mutation_flags() -> None:
    base = load_json_file(FIXTURE_DIR / "expected_decisions_v2.json")["decisions"][0].copy()
    unsafe_decision = {
        **base,
        "notes": [
            "auth_state path was captured",
            "live automation completed in DevHub",
            "submission completed",
            "guarantee approval",
        ],
        "active_prompt_mutation": True,
        "active_guardrail_mutation": True,
        "active_devhub_surface_mutation": True,
        "active_source_mutation": True,
        "active_contract_mutation": True,
        "active_release_state_mutation": True,
    }

    codes = {violation["code"] for violation in validate_preflight_decision_table_v2([unsafe_decision])}

    assert "private_or_session_artifact" in codes
    assert "live_automation_claim" in codes
    assert "official_completion_claim" in codes
    assert "legal_or_permitting_guarantee" in codes
    assert "active_mutation_flag" in codes


def test_decision_table_v2_rejects_private_browser_raw_and_downloaded_artifacts() -> None:
    base = load_json_file(FIXTURE_DIR / "expected_decisions_v2.json")["decisions"][0].copy()
    unsafe_decision = {
        **base,
        "artifact_notes": [
            "Playwright trace.zip was retained",
            "raw HTML body persisted",
            "downloaded document path retained",
        ],
    }

    codes = {violation["code"] for violation in validate_preflight_decision_table_v2([unsafe_decision])}

    assert "browser_artifact" in codes
    assert "raw_or_downloaded_artifact" in codes
