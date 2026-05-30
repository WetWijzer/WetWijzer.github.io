from __future__ import annotations

import pytest

from ppd.release_promotion.readiness_digest_v1 import validate_inactive_readiness_digest_v1


def _valid_digest() -> dict[str, object]:
    return {
        "schema_version": "inactive-release-promotion-readiness-digest-v1",
        "status": "inactive",
        "readiness_summary_rows": [
            {"area": "fixtures", "state": "ready", "evidence": "deterministic fixture inventory only"}
        ],
        "unresolved_hold_carry_forward": {"present": True, "items": []},
        "unresolved_blocker_carry_forward": {"present": True, "items": []},
        "rollback_rehearsal_refs": ["rollback-rehearsal:deterministic-dry-run"],
        "prerequisite_validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "reviewer_handoff_placeholders": ["reviewer", "date", "decision"],
        "no_go_reasons": ["validation failure", "missing reviewer signoff"],
        "active_artifact_mutation": False,
        "active_prompt_mutation": False,
        "active_release_state_mutation": False,
        "active_fixture_mutation": False,
        "active_agent_state_mutation": False,
    }


def test_valid_inactive_digest_passes() -> None:
    result = validate_inactive_readiness_digest_v1(_valid_digest())

    assert result.ok is True
    assert result.findings == ()


@pytest.mark.parametrize(
    "field_name",
    [
        "readiness_summary_rows",
        "unresolved_hold_carry_forward",
        "unresolved_blocker_carry_forward",
        "rollback_rehearsal_refs",
        "prerequisite_validation_commands",
        "reviewer_handoff_placeholders",
        "no_go_reasons",
    ],
)
def test_rejects_missing_required_readiness_fields(field_name: str) -> None:
    digest = _valid_digest()
    digest[field_name] = []

    result = validate_inactive_readiness_digest_v1(digest)

    assert result.ok is False
    assert any(finding.code == f"missing_{field_name}" for finding in result.findings)


@pytest.mark.parametrize(
    ("value", "expected_code"),
    [
        ("ppd/private/session/storage_state.json", "private_or_session_artifact"),
        ("ppd/browser-artifacts/screenshots/home.png", "private_browser_or_capture_file"),
        ("ppd/traces/devhub.har", "private_browser_or_capture_file"),
        ("raw crawl body captured for review", "raw_or_downloaded_data"),
        ("release complete after live execution", "live_execution_or_release_claim"),
        ("permit will be approved", "legal_or_permitting_outcome_guarantee"),
        ("submit permit and pay fees", "consequential_action_language"),
    ],
)
def test_rejects_prohibited_digest_content(value: str, expected_code: str) -> None:
    digest = _valid_digest()
    digest["readiness_summary_rows"] = [{"area": "unsafe", "evidence": value}]

    result = validate_inactive_readiness_digest_v1(digest)

    assert result.ok is False
    assert any(finding.code == expected_code for finding in result.findings)


@pytest.mark.parametrize(
    "flag_name",
    [
        "active_artifact_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_fixture_mutation",
        "active_agent_state_mutation",
        "mutates_active_artifacts",
        "mutates_active_prompts",
        "mutates_active_release_state",
        "mutates_active_fixtures",
        "mutates_active_agent_state",
    ],
)
def test_rejects_active_mutation_flags(flag_name: str) -> None:
    digest = _valid_digest()
    digest[flag_name] = True

    result = validate_inactive_readiness_digest_v1(digest)

    assert result.ok is False
    assert any(finding.code == "active_mutation_flag" and finding.location == flag_name for finding in result.findings)


def test_rejects_active_status_or_wrong_schema() -> None:
    digest = _valid_digest()
    digest["status"] = "active"
    digest["schema_version"] = "release-promotion-readiness-digest-v1"

    result = validate_inactive_readiness_digest_v1(digest)

    assert result.ok is False
    assert {finding.code for finding in result.findings} >= {"invalid_status", "invalid_schema_version"}
