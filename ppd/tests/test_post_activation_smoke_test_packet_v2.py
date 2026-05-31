from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.agent_readiness.post_activation_smoke_test_packet_v2 import (
    DEFAULT_OFFLINE_VALIDATION_COMMANDS,
    PACKET_TYPE,
    REQUIRED_SMOKE_CASE_IDS,
    PostActivationSmokeValidationError,
    assert_valid_post_activation_smoke_test_packet_v2,
    build_post_activation_smoke_test_packet_v2,
    validate_post_activation_smoke_test_packet_v2,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "post_activation_smoke_test_packet_v2" / "noop_activation_rehearsal.json"


def _source_rehearsal() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _valid_packet() -> dict[str, object]:
    return build_post_activation_smoke_test_packet_v2(_source_rehearsal())


def test_builds_agent_facing_post_activation_smoke_packet_from_noop_rehearsal() -> None:
    packet = _valid_packet()

    assert packet["packet_type"] == PACKET_TYPE
    assert packet["fixture_only"] is True
    assert packet["offline_only"] is True
    assert packet["agent_facing"] is True
    assert packet["consumed_noop_activation_rehearsal"]["expected_active_state_diff"] == "no_change"
    assert [case["case_id"] for case in packet["smoke_cases"]] == list(REQUIRED_SMOKE_CASE_IDS)
    assert packet["exact_offline_validation_commands"] == [list(command) for command in DEFAULT_OFFLINE_VALIDATION_COMMANDS]

    result = validate_post_activation_smoke_test_packet_v2(packet)
    assert result.valid, result.errors
    assert_valid_post_activation_smoke_test_packet_v2(packet)


def test_each_smoke_case_has_expected_citations_and_exact_commands() -> None:
    packet = _valid_packet()
    coverage = {row["case_id"]: row["required_citations"] for row in packet["expected_citation_coverage"]}

    for case in packet["smoke_cases"]:
        assert case["expected_citations"]
        assert case["expected_citations"] == coverage[case["case_id"]]
        assert case["exact_offline_validation_commands"] == packet["exact_offline_validation_commands"]
        assert case["case_type"] in {
            "user_gap",
            "guarded_action",
            "draft_preview",
            "stale_source_hold",
            "refused_consequential_action",
        }


def test_rejects_source_rehearsal_that_is_not_noop() -> None:
    source = _source_rehearsal()
    source["no_op_attestations"]["accesses_devhub"] = True

    with pytest.raises(ValueError, match="accesses_devhub"):
        build_post_activation_smoke_test_packet_v2(source)


def test_rejects_missing_required_case_citations_and_command_drift() -> None:
    packet = _valid_packet()
    broken = copy.deepcopy(packet)
    broken["smoke_cases"][0]["expected_citations"] = []
    broken["smoke_cases"][1]["exact_offline_validation_commands"] = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    broken["expected_citation_coverage"][0]["required_citations"] = []

    result = validate_post_activation_smoke_test_packet_v2(broken)

    assert not result.valid
    assert "missing_expected_citations" in result.errors
    assert "exact_offline_validation_commands_mismatch" in result.errors
    assert "citation_coverage_mismatch" in result.errors


def test_rejects_runtime_effects_enabled_consequential_controls_and_mutation_flags() -> None:
    packet = _valid_packet()
    broken = copy.deepcopy(packet)
    broken["prohibited_runtime_effects"]["opens_devhub"] = True
    broken["consequential_controls"][0]["enabled"] = True
    broken["mutation_flags"]["active_release_state_mutation_enabled"] = True

    result = validate_post_activation_smoke_test_packet_v2(broken)

    assert not result.valid
    assert "prohibited_runtime_effect_enabled:opens_devhub" in result.errors
    assert "enabled_consequential_control" in result.errors
    assert "active_mutation_flag" in result.errors


def test_rejects_private_artifacts_live_execution_claims_and_guarantees() -> None:
    packet = _valid_packet()
    broken = copy.deepcopy(packet)
    broken["notes"] = "Opened DevHub in a live browser with auth_state.json and approval is assured."

    result = validate_post_activation_smoke_test_packet_v2(broken)

    assert not result.valid
    assert "private_or_auth_artifact_reference" in result.errors
    assert "live_execution_claim" in result.errors
    assert "outcome_guarantee" in result.errors


def test_assert_valid_reports_invalid_packet() -> None:
    packet = _valid_packet()
    packet["smoke_cases"] = []

    with pytest.raises(PostActivationSmokeValidationError):
        assert_valid_post_activation_smoke_test_packet_v2(packet)
