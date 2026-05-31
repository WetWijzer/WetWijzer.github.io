from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness.inactive_release_transition_audit_packet_v1 import (
    PACKET_VERSION,
    build_audit_packet,
    build_audit_packet_from_fixture,
    load_fixture,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "inactive_release_transition_audit_packet_v1"
    / "synthetic_decision_rows.json"
)


def _single_ready_fixture() -> dict[str, object]:
    fixture = load_fixture(FIXTURE_PATH)
    fixture["decision_rows"] = [fixture["decision_rows"][0]]
    return fixture


def _failing_checks_for_first_row(fixture: dict[str, object]) -> list[str]:
    packet = build_audit_packet(fixture)
    return packet["audited_decisions"][0]["failing_checks"]


def test_inactive_release_transition_audit_packet_is_no_op() -> None:
    packet = build_audit_packet_from_fixture(FIXTURE_PATH)

    assert packet["packet_version"] == PACKET_VERSION
    assert packet["audit_mode"] == "fixture_first_inactive"
    assert packet["side_effects"] == "none"
    assert packet["all_recommendations_are_no_op"] is True
    assert packet["synthetic_decisions_present"] == [
        "release-held",
        "release-ready",
        "release-rejected",
    ]

    for row in packet["audited_decisions"]:
        assert row["transition_recommendation"].startswith("no_op_")
        assert row["state_mutation_performed"] is False
        assert row["artifact_promotion_performed"] is False


def test_release_ready_row_passes_but_still_requires_external_no_op_review() -> None:
    packet = build_audit_packet_from_fixture(FIXTURE_PATH)
    rows = {row["row_id"]: row for row in packet["audited_decisions"]}

    ready = rows["synthetic-release-ready-row"]
    assert ready["decision"] == "release-ready"
    assert ready["ready_for_external_promotion"] is True
    assert ready["failing_checks"] == []
    assert ready["transition_recommendation"] == "no_op_release_ready_requires_external_promotion_review"


def test_held_and_rejected_rows_remain_inactive_without_transition() -> None:
    packet = build_audit_packet_from_fixture(FIXTURE_PATH)
    rows = {row["row_id"]: row for row in packet["audited_decisions"]}

    held = rows["synthetic-release-held-row"]
    assert held["decision"] == "release-held"
    assert held["ready_for_external_promotion"] is False
    assert "promotion_prerequisite:guardrail_bundle_validated" in held["failing_checks"]
    assert "reviewer_approval:fixture-reviewer-validation" in held["failing_checks"]
    assert "rollback_blocker_check:held-validation-blocker" in held["failing_checks"]
    assert "validation_command:held-self-test-record" in held["failing_checks"]
    assert held["transition_recommendation"] == "no_op_keep_release_held_until_findings_clear"

    rejected = rows["synthetic-release-rejected-row"]
    assert rejected["decision"] == "release-rejected"
    assert rejected["ready_for_external_promotion"] is False
    assert "source_evidence:rejected-source-evidence" in rejected["failing_checks"]
    assert rejected["transition_recommendation"] == "no_op_keep_release_rejected_without_transition"


def test_missing_decision_rows_are_rejected() -> None:
    fixture = load_fixture(FIXTURE_PATH)
    fixture["decision_rows"] = []

    with pytest.raises(ValueError, match="decision_rows must be a non-empty list"):
        build_audit_packet(fixture)


@pytest.mark.parametrize(
    ("field_name", "expected_check"),
    [
        ("source_evidence", "source_evidence"),
        ("reviewer_approvals", "reviewer_approvals"),
        ("rollback_blocker_checks", "rollback_blocker_checks"),
        ("validation_commands", "validation_commands"),
    ],
)
def test_required_transition_records_are_rejected_when_missing(field_name: str, expected_check: str) -> None:
    fixture = _single_ready_fixture()
    row = fixture["decision_rows"][0]
    row[field_name] = []

    assert expected_check in _failing_checks_for_first_row(fixture)


def test_missing_evidence_hash_is_rejected() -> None:
    fixture = _single_ready_fixture()
    evidence = fixture["decision_rows"][0]["source_evidence"][0]
    evidence.pop("expected_sha256")

    assert "source_evidence:ready-source-evidence" in _failing_checks_for_first_row(fixture)


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("private_artifacts", [{"artifact_ref": "private://devhub/session.json"}]),
        ("session_state", {"state": "redacted but still private"}),
        ("browser_artifacts", [{"artifact_type": "browser", "artifact_ref": "browser://trace.zip"}]),
        ("raw_body", "raw page body"),
        ("downloaded_artifacts", [{"artifact_type": "downloaded", "artifact_ref": "downloaded://form.pdf"}]),
        ("release_promotion_claim", "release was promoted"),
        ("official_action_completed", True),
        ("live_crawl_used", True),
        ("devhub_used", True),
        ("legal_guarantee", "permit approval is guaranteed"),
        ("active_mutation", True),
    ],
)
def test_inactive_boundary_rejects_prohibited_claims(field_name: str, field_value: object) -> None:
    fixture = _single_ready_fixture()
    row = fixture["decision_rows"][0]
    row[field_name] = deepcopy(field_value)

    assert "inactive_boundary" in _failing_checks_for_first_row(fixture)
