from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.offline_release_gate_readiness_packet_v2 import (
    build_offline_release_gate_readiness_packet_v2,
    build_offline_release_gate_readiness_packet_v2_from_fixture,
    require_offline_release_gate_readiness_packet_v2,
    validate_offline_release_gate_readiness_packet_v2,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "offline_release_gate_readiness_v2" / "source_packet.json"


def _fixture() -> dict[str, object]:
    return build_offline_release_gate_readiness_packet_v2_from_fixture(FIXTURE_PATH)


def test_builds_fixture_first_offline_release_gate_packet_v2() -> None:
    packet = _fixture()

    assert packet["packet_type"] == "ppd.offline_release_gate_readiness_packet.v2"
    assert packet["fixture_only"] is True
    assert packet["release_gate_status"] == "ready_for_fixture_review_only"
    assert len(packet["gate_criteria"]) == 2
    assert len(packet["required_test_commands"]) == 3
    require_offline_release_gate_readiness_packet_v2(packet)


def test_packet_carries_required_attestations_and_false_boundaries() -> None:
    packet = _fixture()
    attestations = {row["attestation_id"]: row for row in packet["attestations"]}

    assert attestations["no_live"]["value"] is True
    assert attestations["no_auth"]["value"] is True
    assert attestations["no_official_action"]["value"] is True
    assert attestations["no_release_state_mutation"]["value"] is True
    assert packet["execution_boundaries"] == {
        "live_network": False,
        "authenticated_session": False,
        "official_action": False,
        "source_mutation": False,
        "surface_registry_mutation": False,
        "guardrail_mutation": False,
        "prompt_mutation": False,
        "monitoring_mutation": False,
        "release_state_mutation": False,
        "agent_state_mutation": False,
    }


def test_gate_criteria_are_cited_and_linked_to_required_commands() -> None:
    packet = _fixture()
    command_ids = {row["command_id"] for row in packet["required_test_commands"]}

    for criterion in packet["gate_criteria"]:
        assert criterion["citations"]
        assert set(criterion["required_test_command_ids"]) == command_ids


def test_rollback_and_reviewer_owner_fields_are_candidate_scoped() -> None:
    packet = _fixture()
    rollback_candidate_ids = {row["candidate_id"] for row in packet["rollback_verification"]}
    owner_candidate_ids = {row["candidate_id"] for row in packet["reviewer_owner_fields"]}

    assert "offline-release-gate-readiness-v2-module" in rollback_candidate_ids
    assert "offline-release-gate-readiness-v2-fixtures" in owner_candidate_ids
    assert all(row["verification_required_before"] == "release_gate_signoff" for row in packet["rollback_verification"])
    assert all(row["required_before"] == "release_gate_signoff" for row in packet["reviewer_owner_fields"])


def test_staging_plan_issues_become_blocker_dispositions() -> None:
    source = deepcopy(build_source_fixture())
    plan = source["implementation_patch_staging_plan_v2"]
    assert isinstance(plan, dict)
    candidates = plan["patch_candidates"]
    assert isinstance(candidates, list)
    first = candidates[0]
    assert isinstance(first, dict)
    first["citations"] = []

    packet = build_offline_release_gate_readiness_packet_v2(source)

    assert packet["release_gate_status"] == "blocked"
    assert any(row["disposition"] == "blocked" for row in packet["blocker_dispositions"])


def test_rejects_live_or_authenticated_artifacts_in_source_fixture() -> None:
    source = build_source_fixture()
    source["validation_fixtures"] = [
        {
            "fixture_id": "bad",
            "path": "storage_state.json",
            "purpose": "bad session state artifact",
        }
    ]

    with pytest.raises(ValueError):
        build_offline_release_gate_readiness_packet_v2(source)


def test_validator_rejects_missing_attestation() -> None:
    packet = _fixture()
    broken = deepcopy(packet)
    broken["attestations"] = [row for row in packet["attestations"] if row["attestation_id"] != "no_auth"]

    result = validate_offline_release_gate_readiness_packet_v2(broken)

    assert not result.ok
    assert "missing attestation: no_auth" in result.errors


def test_validator_rejects_uncited_gate_criteria() -> None:
    packet = _fixture()
    broken = deepcopy(packet)
    broken["gate_criteria"][0]["citations"] = []

    result = validate_offline_release_gate_readiness_packet_v2(broken)

    assert not result.ok
    assert "gate_criteria[0].citations must be non-empty" in result.errors


def test_validator_rejects_missing_candidate_disposition_rollback_or_owner() -> None:
    packet = _fixture()
    candidate_id = packet["gate_criteria"][0]["candidate_id"]

    missing_blocker = deepcopy(packet)
    missing_blocker["blocker_dispositions"] = []
    assert any(
        "blocker_dispositions must be a non-empty list" in error
        for error in validate_offline_release_gate_readiness_packet_v2(missing_blocker).errors
    )

    missing_rollback = deepcopy(packet)
    missing_rollback["rollback_verification"] = [
        row for row in missing_rollback["rollback_verification"] if row["candidate_id"] != candidate_id
    ]
    assert f"candidate {candidate_id} is missing rollback verification" in validate_offline_release_gate_readiness_packet_v2(missing_rollback).errors

    missing_owner = deepcopy(packet)
    missing_owner["reviewer_owner_fields"] = [
        row for row in missing_owner["reviewer_owner_fields"] if row["candidate_id"] != candidate_id
    ]
    assert f"candidate {candidate_id} is missing reviewer owner" in validate_offline_release_gate_readiness_packet_v2(missing_owner).errors


def test_validator_rejects_private_raw_live_claim_and_consequential_language() -> None:
    unsafe_values = [
        {"notes": "used authenticated account email from private facts"},
        {"artifact": "raw PDF artifact captured for audit"},
        {"claim": "live execution promoted to production"},
        {"claim": "permit will be approved"},
        {"claim": "submit the permit after review"},
    ]

    for unsafe in unsafe_values:
        packet = _fixture()
        packet["gate_criteria"][0].update(unsafe)
        result = validate_offline_release_gate_readiness_packet_v2(packet)
        assert not result.ok, unsafe


def test_validator_rejects_active_mutation_boundaries_and_flags() -> None:
    packet = _fixture()
    packet["execution_boundaries"]["source_mutation"] = True
    assert "execution_boundaries.source_mutation must be explicitly false" in validate_offline_release_gate_readiness_packet_v2(packet).errors

    source = build_source_fixture()
    plan = source["implementation_patch_staging_plan_v2"]
    assert isinstance(plan, dict)
    candidates = plan["patch_candidates"]
    assert isinstance(candidates, list)
    first = candidates[0]
    assert isinstance(first, dict)
    first["mutation_flags"] = {"surface_registry": "enabled"}

    with pytest.raises(ValueError):
        build_offline_release_gate_readiness_packet_v2(source)


def build_source_fixture() -> dict[str, object]:
    import json

    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data
