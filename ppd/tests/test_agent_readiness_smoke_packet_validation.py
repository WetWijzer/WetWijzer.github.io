from __future__ import annotations

import pytest

from ppd.agent_readiness.smoke_packet_validation import (
    SmokePacketValidationError,
    iter_final_smoke_packet_issues,
    validate_final_smoke_packet,
)


def _valid_packet() -> dict:
    return {
        "packet_id": "final-smoke-readiness-fixture",
        "reviewer_owners": {"safety": "ppd-reviewer"},
        "mutation_flags": {
            "prompt_mutation_enabled": False,
            "guardrail_mutation_enabled": False,
            "surface_registry_mutation_enabled": False,
            "agent_state_mutation_enabled": False,
        },
        "consequential_controls": [
            {"name": "submit", "enabled": False},
            {"name": "schedule", "enabled": False},
            {"name": "payment", "enabled": False},
        ],
        "blocked_actions": [
            {
                "action": "submit permit request",
                "explanation": "Submission requires attended user confirmation and official source review.",
            }
        ],
        "smoke_scenarios": [
            {
                "scenario_id": "missing-upload-review",
                "reviewer_owner": "ppd-reviewer",
                "citations": ["ppd-source-submit-plans-online"],
                "expected_prompts": ["Ask for the missing public document category."],
                "expected_refusals": ["Refuse to upload to the official DevHub record."],
                "expected_previews": ["Show only a redacted local draft preview."],
                "blocked_actions": [
                    {
                        "action": "official upload",
                        "reason": "Official upload is consequential and requires attendance.",
                    }
                ],
            }
        ],
    }


def _issue_codes(packet: dict) -> set[str]:
    return {issue.code for issue in iter_final_smoke_packet_issues(packet)}


def test_valid_final_smoke_packet_is_accepted() -> None:
    validate_final_smoke_packet(_valid_packet())


def test_rejects_uncited_and_incomplete_smoke_scenarios() -> None:
    packet = _valid_packet()
    packet["smoke_scenarios"] = [
        {
            "scenario_id": "bad-scenario",
            "blocked_actions": [{"action": "submit"}],
        }
    ]

    codes = _issue_codes(packet)

    assert "uncited_smoke_scenario" in codes
    assert "missing_expected_prompts" in codes
    assert "missing_expected_refusals" in codes
    assert "missing_expected_previews" in codes
    assert "missing_scenario_reviewer_owner" in codes
    assert "missing_blocked_action_explanation" in codes


def test_rejects_missing_reviewer_owners() -> None:
    packet = _valid_packet()
    packet["reviewer_owners"] = {}

    assert "missing_reviewer_owners" in _issue_codes(packet)


def test_rejects_private_case_facts_raw_auth_values_and_private_paths() -> None:
    packet = _valid_packet()
    packet["case_facts"] = {
        "applicant_email": "person@example.test",
        "auth_token": "raw-token-value",
        "supporting_document_path": "/home/alex/private/permit.pdf",
    }

    codes = _issue_codes(packet)

    assert "private_case_fact" in codes
    assert "raw_authenticated_value" in codes
    assert "local_private_path" in codes


def test_rejects_live_execution_claims_and_outcome_guarantees() -> None:
    packet = _valid_packet()
    packet["execution_notes"] = [
        "Successfully ran live DevHub browser automation for this smoke test.",
        "This permit will be approved after submission.",
    ]

    codes = _issue_codes(packet)

    assert "live_execution_claim" in codes
    assert "outcome_guarantee" in codes


def test_rejects_enabled_consequential_controls_and_mutation_flags() -> None:
    packet = _valid_packet()
    packet["consequential_controls"] = [{"name": "submit", "enabled": True}]
    packet["mutation_flags"] = {
        "prompt_mutation_enabled": True,
        "guardrail_mutation_enabled": True,
        "surface_registry_mutation_enabled": True,
        "agent_state_mutation_enabled": True,
    }

    codes = _issue_codes(packet)

    assert "enabled_consequential_control" in codes
    assert "active_mutation_flag" in codes


def test_raise_error_carries_all_issues() -> None:
    packet = _valid_packet()
    packet["smoke_scenarios"][0].pop("citations")
    packet["smoke_scenarios"][0].pop("expected_previews")

    with pytest.raises(SmokePacketValidationError) as exc_info:
        validate_final_smoke_packet(packet)

    codes = {issue.code for issue in exc_info.value.issues}
    assert {"uncited_smoke_scenario", "missing_expected_previews"}.issubset(codes)
