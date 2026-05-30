from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.promotion.combined_dependency_packet_v1 import (
    PacketError,
    build_combined_promotion_dependency_packet_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "promotion_dependency_packet_v1" / "source_inputs.json"


def _fixture_inputs() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_builds_ordered_combined_promotion_dependency_packet_v1() -> None:
    packet = build_combined_promotion_dependency_packet_v1(_fixture_inputs())

    assert packet["packet_id"] == "combined_promotion_dependency_packet_v1"
    assert packet["consumes"] == [
        "public_source_refresh_patch_plan_v1",
        "devhub_read_only_observation_promotion_plan_v1",
        "reviewer_disposition_ledger_v1",
        "supervised_offline_release_rehearsal_v1",
    ]
    assert [item["sequence"] for item in packet["ordered_promotion_prerequisites"]] == [10, 20, 30, 40]
    assert [item["prerequisite_id"] for item in packet["ordered_promotion_prerequisites"]] == [
        "public_source_refresh_patch_plan_accepted",
        "devhub_read_only_observation_plan_accepted",
        "reviewer_disposition_ledger_accepted",
        "supervised_offline_release_rehearsal_passed",
    ]


def test_combined_packet_carries_reviewers_fixtures_rollbacks_and_commands() -> None:
    packet = build_combined_promotion_dependency_packet_v1(_fixture_inputs())

    assert packet["reviewer_owners"] == {
        "public_source_refresh": "public-source-fixture-reviewer",
        "devhub_read_only_observation": "devhub-observation-fixture-reviewer",
        "reviewer_disposition": "promotion-supervisor",
        "offline_release_rehearsal": "offline-release-reviewer",
    }
    assert packet["affected_fixture_families"] == [
        "action_policy",
        "archive_manifest",
        "attended_read_only_observation",
        "daemon_self_test",
        "devhub_surface_map",
        "promotion_dependency_packet",
        "public_requirement_extraction",
        "release_rehearsal",
        "source_registry",
    ]
    assert [checkpoint["checkpoint_id"] for checkpoint in packet["rollback_checkpoints"]] == [
        "rollback-public-source-refresh-fixtures",
        "rollback-devhub-read-only-observation-fixtures",
        "rollback-combined-promotion-packet-fixture",
    ]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]


def test_combined_packet_requires_offline_safety_attestations() -> None:
    packet = build_combined_promotion_dependency_packet_v1(_fixture_inputs())

    assert packet["attestations"] == {
        "no_live_crawl": True,
        "no_devhub_session": True,
        "no_private_artifact": True,
        "no_official_action": True,
        "no_active_mutation": True,
    }
    assert packet["promotion_blockers"] == []


def test_rejects_missing_required_attestation() -> None:
    inputs = _fixture_inputs()
    inputs["packets"]["devhub_read_only_observation_promotion_plan_v1"]["attestations"]["no_devhub_session"] = False

    with pytest.raises(PacketError, match="required attestations"):
        build_combined_promotion_dependency_packet_v1(inputs)
