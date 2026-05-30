from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from ppd.inactive_release_decision_packet_v2 import (
    assert_valid_inactive_release_decision_packet,
    build_inactive_release_decision_packet,
    validate_inactive_release_decision_packet,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _source_packet() -> dict[str, Any]:
    return json.loads((FIXTURES / "approved_offline_release_reviewer_disposition_packet_v2.json").read_text(encoding="utf-8"))


def _valid_packet() -> dict[str, Any]:
    return build_inactive_release_decision_packet(_source_packet())


def _assert_rejected(packet: dict[str, Any], code: str) -> None:
    issues = validate_inactive_release_decision_packet(packet)
    assert any(issue["code"] == code for issue in issues), issues
    with pytest.raises(ValueError, match=code):
        assert_valid_inactive_release_decision_packet(packet)


def test_builds_ordered_inactive_release_decision_packet_v2() -> None:
    source = _source_packet()
    expected = json.loads((FIXTURES / "inactive_release_decision_packet_v2.json").read_text(encoding="utf-8"))

    actual = build_inactive_release_decision_packet(source)

    assert actual == expected
    assert [row["release_id"] for row in actual["rows"]] == [
        "inactive-release-2026-05-30-a",
        "inactive-release-2026-05-30-b",
    ]
    assert all(row["inactive_release_decision"] == "hold-inactive-pending-human-approval" for row in actual["rows"])
    assert all(row["promotion_scope_placeholder"]["status"] == "placeholder-only" for row in actual["rows"])
    assert all(row["human_approval_placeholder"]["status"] == "not-approved" for row in actual["rows"])
    assert all(row["no_live_access_attestation"]["attested"] is True for row in actual["rows"])
    assert validate_inactive_release_decision_packet(actual) == []


def test_rejects_non_approved_disposition_rows() -> None:
    source = _source_packet()
    source["rows"][0]["reviewer_disposition"] = "needs-live-review"

    with pytest.raises(ValueError, match="not approved"):
        build_inactive_release_decision_packet(source)


def test_rejects_unsafe_source_disposition_artifacts_before_building() -> None:
    source = _source_packet()
    source["rows"][0]["browser_session_artifact"] = "session-state.json"

    with pytest.raises(ValueError, match="private_or_raw_artifact_field"):
        build_inactive_release_decision_packet(source)


@pytest.mark.parametrize(
    ("mutator", "code"),
    [
        (lambda packet: packet.update({"rows": []}), "missing_release_decision_rows"),
        (lambda packet: packet["rows"][0].pop("promotion_scope_placeholder"), "missing_promotion_scope_placeholder"),
        (lambda packet: packet["rows"][0].pop("human_approval_placeholder"), "missing_human_approval_placeholder"),
        (lambda packet: packet["rows"][0].update({"rollback_plan_reference": ""}), "missing_rollback_plan_reference"),
        (lambda packet: packet["rows"][0].pop("no_live_access_attestation"), "missing_no_live_access_attestation"),
        (lambda packet: packet.update({"validation_commands": []}), "missing_validation_commands"),
        (lambda packet: packet.update({"downloaded_document_path": "/tmp/private/raw.pdf"}), "private_or_raw_artifact_field"),
        (lambda packet: packet["rows"][0].update({"decision_basis": "Live execution completed against DevHub."}), "live_execution_claim"),
        (lambda packet: packet["rows"][0].update({"decision_basis": "Submission completed for the permit."}), "consequential_official_action_language"),
        (lambda packet: packet["rows"][0].update({"decision_basis": "Permit will be approved after this release."}), "legal_or_permitting_guarantee"),
        (lambda packet: packet.update({"active_release_state_mutation": True}), "active_mutation_flag"),
        (lambda packet: packet.update({"validation_commands": [["python3", "ppd/crawler/live_run.py"]]}), "unsafe_validation_command"),
    ],
)
def test_rejects_inactive_release_decision_packet_v2_safety_violations(mutator: Any, code: str) -> None:
    packet = copy.deepcopy(_valid_packet())
    mutator(packet)

    _assert_rejected(packet, code)
