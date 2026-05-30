from __future__ import annotations

from ppd.logic.process_gap_refresh_packet_v2 import (
    PacketValidationError,
    assert_valid_process_to_gap_analysis_refresh_packet_v2,
    validate_process_to_gap_analysis_refresh_packet_v2,
)


def valid_packet() -> dict:
    return {
        "packet_type": "process_to_gap_analysis_refresh",
        "version": 2,
        "process_refs": ["process:residential-building-permit"],
        "source_refs": ["source:ppd-devhub-guide"],
        "gap_analysis_updates": [
            {
                "update_id": "gap-update-1",
                "process_id": "process:residential-building-permit",
                "source_evidence_ids": ["evidence:devhub-guide:apply-step"],
                "citations": [
                    {
                        "source_id": "source:ppd-devhub-guide",
                        "span": "permit requests requiring plan review must be submitted through the guided flow",
                    }
                ],
                "missing_facts": ["permit request type selection"],
            }
        ],
        "blocked_actions": [
            {
                "action": "submit permit request",
                "rationale": "Submission is consequential and requires attended exact confirmation.",
                "source_evidence_ids": ["evidence:devhub-guide:certification"],
            }
        ],
        "next_safe_actions": [
            {
                "action": "review cited public guide section",
                "rationale": "Read-only review can clarify the missing permit request type.",
                "source_evidence_ids": ["evidence:devhub-guide:apply-step"],
            }
        ],
    }


def assert_rejects(packet: dict, expected: str) -> None:
    result = validate_process_to_gap_analysis_refresh_packet_v2(packet)
    assert not result.ok
    assert any(expected in error for error in result.errors), result.errors


def test_accepts_cited_non_mutating_refresh_packet() -> None:
    result = validate_process_to_gap_analysis_refresh_packet_v2(valid_packet())
    assert result.ok, result.errors
    assert_valid_process_to_gap_analysis_refresh_packet_v2(valid_packet())


def test_rejects_uncited_gap_analysis_updates() -> None:
    packet = valid_packet()
    packet["gap_analysis_updates"][0].pop("citations")
    packet["gap_analysis_updates"][0].pop("source_evidence_ids")
    assert_rejects(packet, "must include citations")


def test_rejects_missing_packet_source_or_process_references() -> None:
    packet = valid_packet()
    packet.pop("source_refs")
    packet.pop("process_refs")
    assert_rejects(packet, "source references")
    assert_rejects(packet, "process references")


def test_rejects_gap_update_missing_source_or_process_reference() -> None:
    packet = valid_packet()
    packet["gap_analysis_updates"][0].pop("process_id")
    packet["gap_analysis_updates"][0].pop("source_evidence_ids")
    packet["gap_analysis_updates"][0].pop("citations")
    assert_rejects(packet, "must include a process reference")
    assert_rejects(packet, "must include a source reference")


def test_rejects_missing_blocked_action_or_next_safe_action_rationale() -> None:
    packet = valid_packet()
    packet["blocked_actions"][0].pop("rationale")
    packet["next_safe_actions"][0].pop("rationale")
    assert_rejects(packet, "blocked-action rationale")
    assert_rejects(packet, "next-safe-action rationale")


def test_rejects_private_case_facts() -> None:
    packet = valid_packet()
    packet["case_facts"] = {"owner_name": "Example Person"}
    assert_rejects(packet, "private case facts")


def test_rejects_raw_authenticated_values() -> None:
    packet = valid_packet()
    packet["raw_authenticated_values"] = {"permit_number_field": "private-account-value"}
    assert_rejects(packet, "raw authenticated values")


def test_rejects_local_private_document_paths() -> None:
    packet = valid_packet()
    packet["matched_documents"] = [{"path": "/home/example/private/site-plan.pdf"}]
    assert_rejects(packet, "local private document paths")


def test_rejects_live_execution_claims() -> None:
    packet = valid_packet()
    packet["notes"] = "Opened DevHub in a browser and clicked through the authenticated page."
    assert_rejects(packet, "live execution")


def test_rejects_legal_or_permitting_outcome_guarantees() -> None:
    packet = valid_packet()
    packet["summary"] = "This permit will be approved after submission."
    assert_rejects(packet, "guarantee legal or permitting outcomes")


def test_rejects_enabled_consequential_action_language() -> None:
    packet = valid_packet()
    packet["actions"] = [{"action": "submit permit request", "enabled": True}]
    assert_rejects(packet, "must not enable consequential actions")


def test_rejects_active_mutation_flags() -> None:
    packet = valid_packet()
    packet["mutate_gap_analysis"] = True
    packet["update_process_model"] = True
    packet["guardrail_mutation_enabled"] = True
    packet["prompt_mutation_enabled"] = True
    packet["monitoring_mutation_enabled"] = True
    packet["release_state_mutation_enabled"] = True
    packet["agent_state_mutation_enabled"] = True
    result = validate_process_to_gap_analysis_refresh_packet_v2(packet)
    assert not result.ok
    mutation_errors = [error for error in result.errors if "active mutation" in error]
    assert len(mutation_errors) == 7


def test_assert_valid_raises_with_errors() -> None:
    packet = valid_packet()
    packet["live_devhub_execution"] = True
    try:
        assert_valid_process_to_gap_analysis_refresh_packet_v2(packet)
    except PacketValidationError as exc:
        assert "live execution" in str(exc)
    else:
        raise AssertionError("expected PacketValidationError")
