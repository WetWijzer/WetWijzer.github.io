from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.agent_readiness.inactive_candidate_rollback_rehearsal_packet_v1 import (
    PACKET_TYPE,
    assert_valid_inactive_candidate_rollback_rehearsal_packet_v1,
    validate_inactive_candidate_rollback_rehearsal_packet_v1,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agent_readiness" / "inactive_candidate_rollback_rehearsal_packet_v1.json"


def _load_fixture() -> dict[str, object]:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _problem_text(packet: dict[str, object]) -> str:
    result = validate_inactive_candidate_rollback_rehearsal_packet_v1(packet)
    assert not result.valid
    return "\n".join(result.problems)


def test_accepts_valid_inactive_candidate_rollback_rehearsal_fixture() -> None:
    packet = _load_fixture()

    result = validate_inactive_candidate_rollback_rehearsal_packet_v1(packet)

    assert packet["packet_type"] == PACKET_TYPE
    assert result.valid, result.problems
    assert_valid_inactive_candidate_rollback_rehearsal_packet_v1(packet)


@pytest.mark.parametrize(
    "field",
    [
        "inactive_candidate_refs",
        "smoke_replay_refs",
        "rollback_triggers",
        "rollback_order",
        "evidence_preservation_checks",
        "reviewer_dispositions",
        "validation_commands",
    ],
)
def test_rejects_missing_required_rehearsal_sections(field: str) -> None:
    packet = _load_fixture()
    packet[field] = []

    problems = _problem_text(packet)

    assert f"{field} must be a non-empty list" in problems


def test_rejects_missing_monitoring_outcome_and_stale_source_hold_refs() -> None:
    packet = _load_fixture()
    packet["monitoring_outcome_refs"] = []
    packet["stale_source_hold_refs"] = []

    problems = _problem_text(packet)

    assert "monitoring_outcome_refs or stale_source_hold_refs must be a non-empty list" in problems


def test_accepts_stale_source_hold_ref_instead_of_monitoring_outcome_ref() -> None:
    packet = _load_fixture()
    packet["monitoring_outcome_refs"] = []
    packet["stale_source_hold_refs"] = [
        {
            "stale_source_hold_ref": "stale-source-hold:fixture-001",
            "hold_state": "manual_review_required",
            "source_refs": ["source:ppd-public-guidance"],
        }
    ]

    result = validate_inactive_candidate_rollback_rehearsal_packet_v1(packet)

    assert result.valid, result.problems


def test_rejects_missing_inactive_candidate_reference_details() -> None:
    packet = _load_fixture()
    packet["inactive_candidate_refs"] = [
        {
            "candidate_ref": "",
            "candidate_state": "active",
            "evidence_refs": [],
            "active_candidate_mutation": True,
        }
    ]

    problems = _problem_text(packet)

    assert "inactive_candidate_refs[0].candidate_ref is required" in problems
    assert "inactive_candidate_refs[0].candidate_state must be inactive_reference_only" in problems
    assert "inactive_candidate_refs[0].evidence_refs must be a non-empty list" in problems
    assert "inactive_candidate_refs[0].active_candidate_mutation must be false" in problems
    assert "packet.inactive_candidate_refs[0].active_candidate_mutation must not contain active mutation flags" in problems


def test_rejects_missing_smoke_replay_reference_details() -> None:
    packet = _load_fixture()
    packet["smoke_replay_refs"] = [
        {
            "smoke_replay_ref": "",
            "replay_mode": "online",
            "passed": False,
            "candidate_refs": [],
        }
    ]

    problems = _problem_text(packet)

    assert "smoke_replay_refs[0].smoke_replay_ref is required" in problems
    assert "smoke_replay_refs[0].replay_mode must be offline_fixture_only" in problems
    assert "smoke_replay_refs[0].passed must be true" in problems
    assert "smoke_replay_refs[0].candidate_refs must be a non-empty list" in problems


def test_rejects_missing_rollback_trigger_and_order_details() -> None:
    packet = _load_fixture()
    packet["rollback_triggers"] = [
        {
            "trigger_ref": "",
            "trigger_state": "active",
            "candidate_refs": [],
            "reason": "",
        }
    ]
    packet["rollback_order"] = [
        {
            "sequence": 3,
            "trigger_ref": "missing-trigger",
            "candidate_refs": [],
            "rollback_state": "active_rollback",
            "validation_command_refs": [],
        }
    ]

    problems = _problem_text(packet)

    assert "rollback_triggers[0].trigger_ref is required" in problems
    assert "rollback_triggers[0].trigger_state must be rehearsal_only" in problems
    assert "rollback_triggers[0].candidate_refs must be a non-empty list" in problems
    assert "rollback_triggers[0].reason is required" in problems
    assert "rollback_order[0].sequence must be 1" in problems
    assert "rollback_order[0].rollback_state must be rehearsal_only_no_active_rollback" in problems
    assert "rollback_order[0].validation_command_refs must be a non-empty list" in problems
    assert "rollback_order[0].trigger_ref must reference rollback_triggers" in problems


def test_rejects_missing_evidence_preservation_checks_and_reviewer_dispositions() -> None:
    packet = _load_fixture()
    packet["evidence_preservation_checks"] = [
        {
            "check_ref": "",
            "evidence_ref": "missing-evidence",
            "preserved": False,
            "private_artifacts_absent": False,
            "raw_artifacts_absent": False,
        }
    ]
    packet["reviewer_dispositions"] = [
        {
            "reviewer_ref": "",
            "disposition": "approved_for_release",
            "candidate_refs": [],
            "notes": "",
        }
    ]

    problems = _problem_text(packet)

    assert "evidence_preservation_checks[0].check_ref is required" in problems
    assert "evidence_preservation_checks[0].evidence_ref must reference inactive candidate or smoke replay evidence" in problems
    assert "evidence_preservation_checks[0].preserved must be true" in problems
    assert "evidence_preservation_checks[0].private_artifacts_absent must be true" in problems
    assert "evidence_preservation_checks[0].raw_artifacts_absent must be true" in problems
    assert "reviewer_dispositions[0].reviewer_ref is required" in problems
    assert "reviewer_dispositions[0].disposition must be an allowed reviewer disposition" in problems
    assert "reviewer_dispositions[0].candidate_refs must be a non-empty list" in problems
    assert "reviewer_dispositions[0].notes is required" in problems


def test_rejects_missing_and_unsafe_validation_commands() -> None:
    packet = _load_fixture()
    packet["validation_commands"] = [[], ["python3", "ppd/crawler/live_public_scrape.py"], ["python3", "devhub_check.py"]]

    problems = _problem_text(packet)

    assert "validation_commands[0] must be an argv string list" in problems
    assert "validation_commands[1] must not invoke live crawl, DevHub, browser, network, auth, session, or download paths" in problems
    assert "validation_commands[2] must not invoke live crawl, DevHub, browser, network, auth, session, or download paths" in problems


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("private_artifact_ref", "fixture-private-artifact", "must not include private, session, browser, raw, downloaded, payment, or trace artifacts"),
        ("session_state", "storage state fixture", "must not include private, session, browser, raw, downloaded, payment, or trace artifacts"),
        ("browser_trace", "trace.zip", "must not include private, session, browser, raw, downloaded, payment, or trace artifacts"),
        ("raw_crawl_output", "raw crawl payload", "must not include private, session, browser, raw, downloaded, payment, or trace artifacts"),
        ("downloaded_pdf", "downloaded document", "must not include private, session, browser, raw, downloaded, payment, or trace artifacts"),
    ],
)
def test_rejects_private_session_browser_raw_and_downloaded_artifacts(field: str, value: str, expected: str) -> None:
    packet = _load_fixture()
    packet[field] = value

    problems = _problem_text(packet)

    assert expected in problems


@pytest.mark.parametrize(
    "claim",
    [
        "live crawl completed",
        "DevHub accessed during rehearsal",
        "release activation completed",
        "promotion completed",
        "official action completed",
        "submitted permit",
        "uploaded corrections",
    ],
)
def test_rejects_live_devhub_activation_promotion_and_official_action_completion_claims(claim: str) -> None:
    packet = _load_fixture()
    packet["reviewer_dispositions"] = copy.deepcopy(packet["reviewer_dispositions"])
    packet["reviewer_dispositions"][0]["notes"] = claim

    problems = _problem_text(packet)

    assert "must not claim private artifacts, live crawl or DevHub access, release activation, promotion, rollback completion, or official-action completion" in problems


def test_rejects_active_mutation_flags_anywhere_in_packet() -> None:
    packet = _load_fixture()
    packet["side_effect_attestations"] = {
        "active_release_state_mutation": True,
        "promotes_release": True,
    }

    problems = _problem_text(packet)

    assert "packet.side_effect_attestations.active_release_state_mutation must not contain active mutation flags" in problems
    assert "packet.side_effect_attestations.promotes_release must not contain active mutation flags" in problems


def test_rejects_unknown_candidate_cross_references() -> None:
    packet = _load_fixture()
    packet["rollback_order"] = copy.deepcopy(packet["rollback_order"])
    packet["rollback_order"][0]["candidate_refs"] = ["inactive-candidate:missing"]

    problems = _problem_text(packet)

    assert "rollback_order[0].candidate_refs must reference inactive_candidate_refs" in problems
