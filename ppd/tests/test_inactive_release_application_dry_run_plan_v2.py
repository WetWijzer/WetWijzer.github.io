from __future__ import annotations

from copy import deepcopy

from ppd.agent_readiness.inactive_release_application_dry_run_plan_v2 import (
    build_inactive_release_application_dry_run_plan_v2,
    validate_inactive_release_application_dry_run_plan_v2,
)


def _valid_packet() -> dict:
    return build_inactive_release_application_dry_run_plan_v2()


def _codes(packet: dict) -> set[str]:
    result = validate_inactive_release_application_dry_run_plan_v2(packet)
    return {issue.code for issue in result.issues}


def test_inactive_release_application_dry_run_plan_v2_accepts_minimal_valid_packet() -> None:
    result = validate_inactive_release_application_dry_run_plan_v2(_valid_packet())

    assert result.ok is True
    assert result.issues == ()


def test_inactive_release_application_dry_run_plan_v2_rejects_missing_required_sections() -> None:
    for section in (
        "synthetic_application_steps",
        "expected_file_delta_placeholders",
        "post_application_replay_prerequisites",
        "rollback_rehearsal_checkpoints",
        "reviewer_stop_gates",
        "validation_commands",
    ):
        packet = _valid_packet()
        packet[section] = []

        assert "missing_required_section" in _codes(packet)


def test_inactive_release_application_dry_run_plan_v2_rejects_incomplete_step_coverage() -> None:
    packet = _valid_packet()
    packet["synthetic_application_steps"] = packet["synthetic_application_steps"][:1]

    codes = _codes(packet)

    assert "missing_synthetic_step_action" in codes


def test_inactive_release_application_dry_run_plan_v2_rejects_invalid_file_delta_placeholder() -> None:
    packet = _valid_packet()
    packet["expected_file_delta_placeholders"][0]["file_path"] = "ppd/daemon/release-state/active.json"
    packet["expected_file_delta_placeholders"][0]["status"] = "applied"

    codes = _codes(packet)

    assert "invalid_file_delta_placeholder_path" in codes
    assert "invalid_file_delta_status" in codes


def test_inactive_release_application_dry_run_plan_v2_rejects_bad_replay_rollback_and_stop_gates() -> None:
    packet = _valid_packet()
    packet["post_application_replay_prerequisites"][0]["replay_command"] = ["python3", "ppd/crawler/live_public_scrape.py"]
    packet["rollback_rehearsal_checkpoints"][0]["expected_inverse_delta_placeholder_ids"] = []
    packet["reviewer_stop_gates"][0]["status"] = "passed"

    codes = _codes(packet)

    assert "unsafe_validation_command" in codes
    assert "missing_inverse_delta_placeholders" in codes
    assert "invalid_reviewer_stop_gate_status" in codes


def test_inactive_release_application_dry_run_plan_v2_rejects_private_raw_live_consequential_and_guarantee_content() -> None:
    unsafe_examples = [
        ("session_artifact", {"path": "state.json"}, "private_or_raw_artifact_field"),
        ("raw_downloaded_pdf", "raw downloaded pdf", "private_or_raw_artifact_field"),
        ("note", "live execution completed", "unsafe_plan_text"),
        ("operator_note", "submit permit after review", "unsafe_plan_text"),
        ("legal_note", "approval is guaranteed", "unsafe_plan_text"),
    ]
    for key, value, expected_code in unsafe_examples:
        packet = _valid_packet()
        packet[key] = value

        assert expected_code in _codes(packet)


def test_inactive_release_application_dry_run_plan_v2_rejects_active_promotion_and_release_state_mutation_flags() -> None:
    for key in (
        "active_promotion_enabled",
        "active_release_state_mutation",
        "apply_release",
        "promotes_fixtures",
        "release_state_mutation",
        "updates_release_state",
    ):
        packet = _valid_packet()
        packet[key] = True

        assert "active_mutation_flag" in _codes(packet)


def test_inactive_release_application_dry_run_plan_v2_rejects_missing_validation_commands() -> None:
    packet = _valid_packet()
    del packet["validation_commands"]

    codes = _codes(packet)

    assert "missing_required_section" in codes


def test_inactive_release_application_dry_run_plan_v2_does_not_mutate_input_during_validation() -> None:
    packet = _valid_packet()
    before = deepcopy(packet)

    validate_inactive_release_application_dry_run_plan_v2(packet)

    assert packet == before
