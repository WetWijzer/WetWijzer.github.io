from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from ppd.agent_readiness.agent_readiness_delta_packet_v2 import (
    EXACT_OFFLINE_VALIDATION_COMMANDS,
    AgentReadinessDeltaPacketV2Error,
    assert_valid_agent_readiness_delta_packet_v2,
    build_agent_readiness_delta_packet_v2,
    validate_agent_readiness_delta_packet_v2,
)

FIXTURE = Path(__file__).parent / "fixtures" / "agent_readiness_delta_packet_v2" / "guardrail_impact_replay_plan_v2.json"


def _plan() -> dict[str, Any]:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _packet() -> dict[str, Any]:
    return build_agent_readiness_delta_packet_v2(_plan())


def test_builds_guarded_agent_readiness_delta_packet_v2_from_guardrail_impact_replay_plan_v2() -> None:
    packet = _packet()

    assert packet["packet_type"] == "ppd.agent_readiness_delta_packet.v2"
    assert packet["packet_version"] == "v2"
    assert packet["fixture_first"] is True
    assert packet["offline_only"] is True
    assert packet["consumes"] == [
        {
            "plan_type": "ppd.guardrail_impact_replay_plan.v2",
            "plan_version": "v2",
            "plan_id": "guardrail-impact-replay-plan-v2-fixture",
        }
    ]
    assert packet["exact_offline_validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS
    assert_valid_agent_readiness_delta_packet_v2(packet)


def test_emits_agent_facing_schema_delta_placeholders_for_each_replay_case() -> None:
    packet = _packet()

    assert len(packet["agent_schema_delta_placeholders"]) == 3
    first = packet["agent_schema_delta_placeholders"][0]
    assert first["delta_id"] == "agent-schema-delta-placeholder:guardrail-impact-001-allow-reversible-review"
    assert first["expected_guardrail_decision"] == "ALLOW"
    assert first["agent_schema_fields"] == [
        "missing_information_prompt_expectations",
        "blocked_action_explanation_expectations",
        "reversible_draft_preview_expectations",
        "citation_coverage_placeholders",
        "reviewer_acceptance_placeholders",
    ]
    assert first["placeholder_status"] == "pending_reviewer_acceptance"
    assert first["citations"][0]["source_evidence_id"] == "source:ppd-devhub-guide-submit-permit-application#draft-save-for-later"


def test_emits_missing_blocked_preview_citation_and_reviewer_placeholders() -> None:
    packet = _packet()

    assert packet["missing_information_prompt_expectations"] == [
        {
            "expectation_id": "missing-information-prompt-expectation:guardrail-impact-001-escalate-gap-comparison",
            "replay_case_id": "guardrail-impact-001-escalate-gap-comparison",
            "dependency_row_id": "dependency-001-devhub-application-guide-draft-surface",
            "requirement_refs": ["requirement:devhub-application-draft-save-for-later"],
            "prompt_expectation": "Ask only for missing, stale, ambiguous, or conflicting case facts before continuing.",
            "must_include": [
                "missing fact label",
                "why the fact is needed",
                "cited requirement placeholder",
                "no permitting outcome guarantee",
            ],
            "placeholder_status": "pending_reviewer_acceptance",
            "citations": [
                {
                    "citation_id": "citation-placeholder:guardrail-impact-001-escalate-gap-comparison:001",
                    "source_evidence_id": "source:ppd-devhub-guide-submit-permit-application#draft-save-for-later",
                    "citation_status": "pending_replay_resolution",
                }
            ],
        }
    ]
    assert packet["blocked_action_explanation_expectations"][0]["blocked_decision"] == "BLOCK"
    assert "required user attendance" in packet["blocked_action_explanation_expectations"][0]["explanation_expectation"]
    assert packet["reversible_draft_preview_expectations"][0]["preview_expectation"].startswith("Show a metadata-only draft preview")
    assert packet["citation_coverage_placeholders"][0]["coverage_status"] == "pending_reviewer_acceptance"
    assert packet["reviewer_acceptance_placeholders"][0]["decision"] == "pending_manual_review"
    assert packet["reviewer_acceptance_placeholders"][0]["reviewer"] == ""


def test_rejects_missing_required_sections_and_unsigned_reviewer_drift() -> None:
    packet = _packet()
    packet["missing_information_prompt_expectations"] = []
    packet["reviewer_acceptance_placeholders"][0]["reviewer"] = "reviewer@example.test"

    result = validate_agent_readiness_delta_packet_v2(packet)

    assert not result.valid
    problems = "; ".join(result.problems)
    assert "missing_information_prompt_expectations must be a non-empty list" in problems
    assert "reviewer_acceptance_placeholders[0] must remain unsigned" in problems


def test_rejects_drift_in_attestations_validation_commands_and_change_sections() -> None:
    packet = _packet()
    packet["attestations"]["active_prompts_changed"] = True
    packet["prompt_changes"] = [{"change": "not allowed"}]
    packet["exact_offline_validation_commands"] = []

    result = validate_agent_readiness_delta_packet_v2(packet)

    assert not result.valid
    problems = "; ".join(result.problems)
    assert "attestations.active_prompts_changed must be False" in problems
    assert "prompt_changes must remain empty" in problems
    assert "exact_offline_validation_commands must match" in problems


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("active_prompt_mutation", True, "must be false"),
        ("production_contract_mutation", True, "must be false"),
        ("browser_state_ref", "state.json", "must not include live"),
        ("payment_note", "payment detail", "must not include unsafe"),
        ("guarantee_note", "approval guaranteed", "must not include unsafe"),
    ],
)
def test_rejects_mutation_live_account_file_payment_and_guarantee_content(key: str, value: Any, expected: str) -> None:
    packet = _packet()
    packet[key] = value

    result = validate_agent_readiness_delta_packet_v2(packet)

    assert not result.valid
    assert expected in "; ".join(result.problems)


def test_assert_raises_with_validation_problems() -> None:
    packet = copy.deepcopy(_packet())
    packet["packet_version"] = "wrong"

    with pytest.raises(AgentReadinessDeltaPacketV2Error, match="packet_version"):
        assert_valid_agent_readiness_delta_packet_v2(packet)
