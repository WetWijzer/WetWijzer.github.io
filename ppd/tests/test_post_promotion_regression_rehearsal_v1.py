from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ppd.post_promotion_regression_rehearsal_v1 import (
    REQUIRED_SCENARIO_FOCUSES,
    PostPromotionRegressionRehearsalV1Error,
    build_post_promotion_regression_rehearsal_v1,
    build_post_promotion_regression_rehearsal_v1_from_fixture,
    load_json,
    validate_post_promotion_regression_rehearsal_v1,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "post_promotion_regression_rehearsal_v1" / "source_packet.json"


def _inputs() -> dict[str, object]:
    return load_json(FIXTURE_PATH)["input_packets"]  # type: ignore[return-value]


def _packet() -> dict[str, object]:
    return build_post_promotion_regression_rehearsal_v1(_inputs())


def test_builds_ordered_fixture_first_post_promotion_regression_rehearsal_v1() -> None:
    packet = _packet()

    assert validate_post_promotion_regression_rehearsal_v1(packet) == []
    assert packet["mode"] == "offline_fixture_post_promotion_regression_only"
    assert packet["attestations"]["no_live_sources"] is True  # type: ignore[index]
    assert packet["attestations"]["no_devhub_access"] is True  # type: ignore[index]
    assert packet["attestations"]["no_active_promotion"] is True  # type: ignore[index]
    assert packet["attestations"]["no_official_actions"] is True  # type: ignore[index]

    scenarios = packet["ordered_offline_regression_scenarios"]
    assert [scenario["sequence"] for scenario in scenarios] == list(range(1, 9))  # type: ignore[index]
    assert [scenario["focus"] for scenario in scenarios] == list(REQUIRED_SCENARIO_FOCUSES)  # type: ignore[index]
    assert all(scenario["citations"] for scenario in scenarios)  # type: ignore[index]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["validation_replay_commands"]  # type: ignore[operator]


def test_build_from_fixture_matches_direct_build() -> None:
    assert build_post_promotion_regression_rehearsal_v1_from_fixture(FIXTURE_PATH) == _packet()


def test_rejects_missing_required_scenario_focus() -> None:
    packet = _packet()
    packet["ordered_offline_regression_scenarios"] = packet["ordered_offline_regression_scenarios"][:-1]  # type: ignore[index]

    errors = validate_post_promotion_regression_rehearsal_v1(packet)

    assert any("ordered_offline_regression_scenarios" in error for error in errors)
    assert any("scenario focus order" in error for error in errors)


def test_rejects_uncited_regression_scenario() -> None:
    packet = _packet()
    packet["ordered_offline_regression_scenarios"][0]["citations"] = []  # type: ignore[index]

    errors = validate_post_promotion_regression_rehearsal_v1(packet)

    assert "ordered_offline_regression_scenarios[0].citations must be non-empty" in errors


def test_rejects_missing_expected_pass_or_block_outcome() -> None:
    packet = _packet()
    packet["ordered_offline_regression_scenarios"][0].pop("expected_result")  # type: ignore[index]
    packet["ordered_offline_regression_scenarios"][1]["expected_result"] = "maybe"  # type: ignore[index]

    errors = validate_post_promotion_regression_rehearsal_v1(packet)

    assert "ordered_offline_regression_scenarios[0].expected_result must be pass or block" in errors
    assert "ordered_offline_regression_scenarios[1].expected_result must be pass or block" in errors


def test_rejects_missing_rollback_readiness() -> None:
    packet = _packet()
    packet["rollback_readiness"] = {"ready_for_manual_rollback_review": False, "checkpoint_refs": []}
    packet["ordered_offline_regression_scenarios"][0]["rollback_checkpoint_ref"] = ""  # type: ignore[index]

    errors = validate_post_promotion_regression_rehearsal_v1(packet)

    assert "rollback_readiness.ready_for_manual_rollback_review must be true" in errors
    assert "rollback_readiness.checkpoint_refs must be non-empty" in errors
    assert "rollback_readiness.activation_status must be not_activated_rehearsal_only" in errors
    assert "ordered_offline_regression_scenarios[0].rollback_checkpoint_ref must be present" in errors


def test_rejects_missing_validation_replay_commands() -> None:
    packet = _packet()
    packet["validation_replay_commands"] = []
    packet["ordered_offline_regression_scenarios"][0]["validation_replay_commands"] = []  # type: ignore[index]

    errors = validate_post_promotion_regression_rehearsal_v1(packet)

    assert "validation_replay_commands must be a non-empty command list" in errors
    assert "ordered_offline_regression_scenarios[0].validation_replay_commands must be non-empty" in errors


def test_rejects_private_live_promotion_and_official_action_content() -> None:
    packet = _packet()
    packet["auth_state"] = {"storage_state": "private browser state"}
    packet["ordered_offline_regression_scenarios"][0]["offline_steps"][0] = "Live crawl completed and fixture promoted to active."  # type: ignore[index]
    packet["ordered_offline_regression_scenarios"][1]["offline_steps"][0] = "Submit the permit because approval is guaranteed."  # type: ignore[index]

    errors = validate_post_promotion_regression_rehearsal_v1(packet)

    assert any("forbidden private" in error or "forbidden private," in error for error in errors)
    assert any("live execution, release, or active promotion claim" in error for error in errors)
    assert any("legal or permitting outcome guarantee" in error for error in errors)
    assert any("consequential action language" in error for error in errors)


def test_rejects_private_authenticated_session_browser_raw_pdf_and_download_artifacts() -> None:
    packet = _packet()
    packet["devhub_session"] = "authenticated session artifact"
    packet["browser_artifact"] = "trace file"
    packet["raw_crawl_output"] = "raw crawl output"
    packet["downloaded_pdf"] = "downloaded pdf"

    errors = validate_post_promotion_regression_rehearsal_v1(packet)

    assert any("packet.devhub_session uses a forbidden" in error for error in errors)
    assert any("packet.browser_artifact uses a forbidden" in error for error in errors)
    assert any("packet.raw_crawl_output uses a forbidden" in error for error in errors)
    assert any("packet.downloaded_pdf uses a forbidden" in error for error in errors)


def test_rejects_active_mutation_flags() -> None:
    packet = _packet()
    mutation_flags = deepcopy(packet["mutation_flags"])
    mutation_flags["active_prompt_mutation"] = True
    mutation_flags["active_source_mutation"] = True
    mutation_flags["active_document_mutation"] = True
    mutation_flags["active_requirement_mutation"] = True
    mutation_flags["active_process_mutation"] = True
    mutation_flags["active_guardrail_mutation"] = True
    mutation_flags["active_release_state_mutation"] = True
    mutation_flags["active_fixture_mutation"] = True
    mutation_flags["active_agent_state_mutation"] = True
    packet["mutation_flags"] = mutation_flags

    errors = validate_post_promotion_regression_rehearsal_v1(packet)

    assert "mutation_flags.active_prompt_mutation must be false" in errors
    assert "mutation_flags.active_source_mutation must be false" in errors
    assert "mutation_flags.active_document_mutation must be false" in errors
    assert "mutation_flags.active_requirement_mutation must be false" in errors
    assert "mutation_flags.active_process_mutation must be false" in errors
    assert "mutation_flags.active_guardrail_mutation must be false" in errors
    assert "mutation_flags.active_release_state_mutation must be false" in errors
    assert "mutation_flags.active_fixture_mutation must be false" in errors
    assert "mutation_flags.active_agent_state_mutation must be false" in errors


def test_rejects_nested_active_mutation_flag_names_even_outside_declared_flags() -> None:
    packet = _packet()
    packet["nested"] = {"active_requirement_mutation": True}

    errors = validate_post_promotion_regression_rehearsal_v1(packet)

    assert "packet.nested.active_requirement_mutation must be false" in errors


def test_build_raises_when_required_input_is_missing() -> None:
    inputs = _inputs()
    inputs.pop("action_journal_replay_validator_v1")

    try:
        build_post_promotion_regression_rehearsal_v1(inputs)
    except ValueError as exc:
        assert "missing required rehearsal inputs" in str(exc)
    else:
        raise AssertionError("missing input should raise ValueError")


def test_require_style_error_is_available_for_invalid_built_packet() -> None:
    packet = _packet()
    packet["validation_replay_commands"] = []

    errors = validate_post_promotion_regression_rehearsal_v1(packet)
    assert errors

    try:
        from ppd.post_promotion_regression_rehearsal_v1 import require_post_promotion_regression_rehearsal_v1

        require_post_promotion_regression_rehearsal_v1(packet)
    except PostPromotionRegressionRehearsalV1Error as exc:
        assert exc.errors == tuple(errors)
    else:
        raise AssertionError("invalid packet should raise PostPromotionRegressionRehearsalV1Error")
