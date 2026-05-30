from __future__ import annotations

from copy import deepcopy

from ppd.agent_readiness.combined_inactive_fixture_promotion_rehearsal_v2 import (
    build_combined_inactive_fixture_promotion_rehearsal_v2,
    validate_combined_inactive_fixture_promotion_rehearsal_v2,
)


def _valid_packet() -> dict[str, object]:
    return build_combined_inactive_fixture_promotion_rehearsal_v2(
        public_source_refresh_inactive_patch_preview_v3={
            "preview_version": "public-source-refresh-inactive-patch-preview-v3",
            "citations": ["public-source-preview:v3:test"],
            "blocked_rows": [
                {
                    "explanation": "public preview row requires reviewer disposition",
                    "citations": ["public-source-preview:v3:blocker:test"],
                }
            ],
        },
        devhub_observed_surface_inactive_patch_preview_v2={
            "preview_version": "devhub-observed-surface-inactive-patch-preview-v2",
            "citations": ["devhub-observed-surface-preview:v2:test"],
            "rows": [
                {
                    "status": "blocked",
                    "citations": ["devhub-observed-surface-preview:v2:row:test"],
                }
            ],
        },
        guarded_agent_release_reviewer_checklist_v1={
            "packet_type": "ppd.guarded_agent_release_reviewer_checklist.v1",
            "citations": ["guarded-agent-release-reviewer-checklist:v1:test"],
            "unresolved_blocker_references": [
                {
                    "blocker_ref": "reviewer-checklist-blocker-test",
                    "citations": ["guarded-agent-release-reviewer-checklist:v1:blocker:test"],
                }
            ],
        },
        agent_behavior_dry_run_scenario_matrix_v1={
            "schema_version": "agent_behavior_dry_run_matrix.v1",
            "citations": ["agent-behavior-dry-run-matrix:v1:test"],
            "scenarios": [
                {
                    "expected_outcome": "block",
                    "citations": ["agent-behavior-dry-run-matrix:v1:scenario:test"],
                }
            ],
        },
    )


def test_combined_inactive_fixture_promotion_rehearsal_v2_accepts_valid_packet() -> None:
    assert validate_combined_inactive_fixture_promotion_rehearsal_v2(_valid_packet()) == []


def test_combined_inactive_fixture_promotion_rehearsal_v2_rejects_missing_gate_controls() -> None:
    packet = _valid_packet()
    gate = deepcopy(packet["ordered_offline_rehearsal_gates"][0])  # type: ignore[index]
    gate.pop("citations")
    gate.pop("dependency_checks")
    gate.pop("manual_only_signoff_placeholder")
    gate.pop("blocked_promotion_explanation")
    gate.pop("validation_replay_commands")
    gate.pop("rollback_checkpoint")
    packet["ordered_offline_rehearsal_gates"] = [gate]

    errors = validate_combined_inactive_fixture_promotion_rehearsal_v2(packet)

    assert any("citations" in error for error in errors)
    assert any("dependency_checks" in error for error in errors)
    assert any("manual_only_signoff_placeholder" in error for error in errors)
    assert any("blocked_promotion_explanation" in error for error in errors)
    assert any("validation_replay_commands" in error for error in errors)
    assert any("rollback_checkpoint" in error for error in errors)


def test_combined_inactive_fixture_promotion_rehearsal_v2_rejects_unsafe_artifacts_and_claims() -> None:
    packet = _valid_packet()
    packet["auth_state"] = {"storage_state": "private DevHub session"}
    packet["raw_pdf"] = "raw pdf data"
    packet["promotion_completed"] = True
    packet["outcome_claim"] = "Permit will be approved."
    packet["action_instruction"] = "Submit permit after rehearsal."

    errors = validate_combined_inactive_fixture_promotion_rehearsal_v2(packet)

    assert any("private, authenticated, session, or browser artifacts" in error for error in errors)
    assert any("raw crawl, PDF, downloaded, or WARC payload data" in error for error in errors)
    assert any("live execution, promotion, or release-state update" in error for error in errors)
    assert any("outcome guarantees" in error for error in errors)
    assert any("consequential action language" in error for error in errors)


def test_combined_inactive_fixture_promotion_rehearsal_v2_rejects_active_mutation_flags() -> None:
    for flag in (
        "active_source_mutation",
        "active_document_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_fixture_promotion",
        "active_agent_state_mutation",
        "official_action_performed",
    ):
        packet = _valid_packet()
        packet[flag] = True

        errors = validate_combined_inactive_fixture_promotion_rehearsal_v2(packet)

        assert f"{flag} must be false" in errors
