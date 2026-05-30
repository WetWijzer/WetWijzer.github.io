from __future__ import annotations

import pytest

from ppd.release_gate.offline_rehearsal_gate_v2 import (
    assert_offline_release_rehearsal_gate_v2,
    validate_offline_release_rehearsal_gate_v2,
)


_REQUIRED_FIELDS = (
    "promotion_candidate_inputs",
    "guardrail_replay_inputs",
    "agent_readiness_inputs",
    "release_gate_checks",
    "evidence_bundle_references",
    "validation_transcript_placeholders",
    "rollback_readiness_placeholders",
    "human_reviewer_decisions",
    "validation_commands",
)


def _valid_payload() -> dict[str, object]:
    return {
        "promotion_candidate_inputs": ["candidate manifest fixture ppd/tests/fixtures/release_gate/candidate.json"],
        "guardrail_replay_inputs": ["deterministic replay fixture ppd/tests/fixtures/release_gate/replay.json"],
        "agent_readiness_inputs": ["readiness checklist fixture with no private values"],
        "release_gate_checks": ["offline policy check", "fixture schema check"],
        "evidence_bundle_references": ["ppd/tests/fixtures/release_gate/evidence_bundle.json"],
        "validation_transcript_placeholders": ["redacted transcript placeholder only"],
        "rollback_readiness_placeholders": ["rollback plan placeholder only"],
        "human_reviewer_decisions": ["reviewer: pending offline approval"],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "metadata": {"mode": "offline rehearsal", "fixture_only": True},
    }


def test_accepts_complete_offline_rehearsal_payload() -> None:
    result = validate_offline_release_rehearsal_gate_v2(_valid_payload())

    assert result.accepted is True
    assert result.issues == ()


@pytest.mark.parametrize("field_name", _REQUIRED_FIELDS)
def test_rejects_missing_required_inputs(field_name: str) -> None:
    payload = _valid_payload()
    payload.pop(field_name)

    result = validate_offline_release_rehearsal_gate_v2(payload)

    assert result.accepted is False
    assert any(issue.code == field_name for issue in result.issues)


@pytest.mark.parametrize("field_name", _REQUIRED_FIELDS)
def test_rejects_empty_required_inputs(field_name: str) -> None:
    payload = _valid_payload()
    payload[field_name] = []

    result = validate_offline_release_rehearsal_gate_v2(payload)

    assert result.accepted is False
    assert any(issue.code == field_name for issue in result.issues)


@pytest.mark.parametrize(
    "bad_value, expected_code",
    [
        ("private trace artifact: ppd/devhub/traces/session.trace.zip", "private_artifact_reference"),
        ("browser_state storage file was attached", "private_artifact_reference"),
        ("raw downloaded permit packet", "private_artifact_reference"),
        ("live execution completed against DevHub", "live_execution_claim"),
        ("submitted permit application during rehearsal", "consequential_official_action_language"),
        ("permit guaranteed after validation", "legal_or_permitting_guarantee"),
    ],
)
def test_rejects_prohibited_text_claims(bad_value: str, expected_code: str) -> None:
    payload = _valid_payload()
    payload["evidence_bundle_references"] = [bad_value]

    result = validate_offline_release_rehearsal_gate_v2(payload)

    assert result.accepted is False
    assert any(issue.code == expected_code for issue in result.issues)


@pytest.mark.parametrize(
    "flag_name",
    [
        "active_promotion",
        "active_release_state_mutation",
        "apply_release_state",
        "commit_release_state",
        "execute_promotion",
        "mutate_release_state",
        "promote_now",
        "release_state_mutation_enabled",
    ],
)
def test_rejects_active_promotion_or_release_mutation_flags(flag_name: str) -> None:
    payload = _valid_payload()
    payload["release_flags"] = {flag_name: True}

    result = validate_offline_release_rehearsal_gate_v2(payload)

    assert result.accepted is False
    assert any(issue.code == "active_release_state_mutation_flag" for issue in result.issues)


def test_assert_helper_raises_with_rejection_details() -> None:
    payload = _valid_payload()
    payload["validation_commands"] = []

    with pytest.raises(ValueError, match="missing validation commands"):
        assert_offline_release_rehearsal_gate_v2(payload)
