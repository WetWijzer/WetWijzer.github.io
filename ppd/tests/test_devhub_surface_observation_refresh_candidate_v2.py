from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ppd.devhub_surface_observation_refresh_candidate_v2 import (
    build_candidate_from_files,
    validate_devhub_surface_observation_refresh_candidate_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_surface_observation_refresh_v2"


def _candidate() -> dict:
    return build_candidate_from_files(
        FIXTURE_DIR / "live_dry_run_acceptance_review_packet_v2.json",
        FIXTURE_DIR / "attended_devhub_read_only_evidence_envelope_v2.json",
        FIXTURE_DIR / "surface_registry_refresh_review_fixture.json",
    )


def test_build_candidate_cites_all_source_fixtures_and_attests_no_live_artifacts() -> None:
    candidate = _candidate()

    assert candidate["candidate_version"] == "devhub_read_only_surface_observation_refresh_candidate_v2"
    assert len(candidate["observations"]) == 2
    assert candidate["attestations"] == {
        "no_live_devhub": True,
        "no_auth_state": True,
        "no_screenshot": True,
        "no_trace": True,
        "no_har": True,
        "no_surface_registry_mutation": True,
    }
    assert validate_devhub_surface_observation_refresh_candidate_v2(candidate).ok

    for observation in candidate["observations"]:
        assert observation["read_only"] is True
        cited = {citation["fixture"] for citation in observation["citations"]}
        assert str(FIXTURE_DIR / "live_dry_run_acceptance_review_packet_v2.json") in cited
        assert str(FIXTURE_DIR / "attended_devhub_read_only_evidence_envelope_v2.json") in cited
        assert str(FIXTURE_DIR / "surface_registry_refresh_review_fixture.json") in cited


def test_candidate_includes_review_dispositions_and_offline_validation_commands() -> None:
    candidate = _candidate()

    handoffs = {item["surface_id"]: item for item in candidate["manual_handoff_dispositions"]}
    redactions = {item["surface_id"]: item for item in candidate["redaction_dispositions"]}
    owners = {item["surface_id"]: item["reviewer_owner"] for item in candidate["reviewer_owner_fields"]}
    confidence = {item["surface_id"]: item["confidence"] for item in candidate["selector_confidence_notes"]}

    assert handoffs["case-status"]["required"] is True
    assert redactions["case-status"]["disposition"] == "synthetic-only"
    assert owners["permit-search"] == "ppd-surface-review"
    assert confidence == {"permit-search": "medium", "case-status": "low"}
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in candidate["offline_validation_commands"]


def test_validator_rejects_uncited_surface_or_action_observations() -> None:
    candidate = _candidate()
    candidate["observations"][0]["citations"] = [{"fixture": "fixture.json", "supports": "surface"}]

    result = validate_devhub_surface_observation_refresh_candidate_v2(candidate)

    assert not result.ok
    assert any("surface and action" in error for error in result.errors)


def test_validator_rejects_missing_selector_handoff_or_redaction_dispositions() -> None:
    for field in ("selector_confidence_notes", "manual_handoff_dispositions", "redaction_dispositions"):
        candidate = _candidate()
        candidate[field] = []

        result = validate_devhub_surface_observation_refresh_candidate_v2(candidate)

        assert not result.ok
        assert any(field in error for error in result.errors)


def test_validator_rejects_private_credentials_session_and_browser_artifacts() -> None:
    candidate = _candidate()
    candidate["observations"][0]["account_id"] = "private-account"
    candidate["observations"][0]["credentials"] = {"username": "applicant@example.test"}
    candidate["observations"][0]["auth_state"] = "storage_state.json"
    candidate["observations"][0]["trace_path"] = "/tmp/trace.zip"
    candidate["observations"][0]["har_path"] = "/tmp/devhub.har"
    candidate["observations"][0]["screenshot_path"] = "/tmp/devhub.png"

    result = validate_devhub_surface_observation_refresh_candidate_v2(candidate)

    assert not result.ok
    assert any("private or authenticated values" in error for error in result.errors)
    assert any("credentials" in error or "session/auth state" in error for error in result.errors)
    assert any("screenshots" in error or "browser artifact" in error for error in result.errors)


def test_validator_rejects_browser_completion_outcome_and_consequential_claims() -> None:
    candidate = _candidate()
    candidate["observations"][0]["synthetic_action_candidate"] = (
        "Playwright clicked through DevHub, permit approved, and submit permit is enabled."
    )

    result = validate_devhub_surface_observation_refresh_candidate_v2(candidate)

    assert not result.ok
    assert any("prohibited browser automation" in error for error in result.errors)
    assert any("consequential DevHub action" in error for error in result.errors)


def test_validator_rejects_active_mutation_flags() -> None:
    flags = (
        "active_surface_registry_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "monitoring_mutation",
        "release_state_mutation",
        "agent_state_mutation",
    )
    for flag in flags:
        candidate = deepcopy(_candidate())
        candidate["mutation_flags"] = {flag: True}

        result = validate_devhub_surface_observation_refresh_candidate_v2(candidate)

        assert not result.ok
        assert any(flag in error for error in result.errors)
