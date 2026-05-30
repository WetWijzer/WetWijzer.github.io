from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.devhub_readonly_evidence_envelope_v2 import (
    ENVELOPE_VERSION,
    build_envelope,
    load_fixture,
    validate_devhub_readonly_evidence_envelope_v2,
)

FIXTURES = Path(__file__).parent / "fixtures" / "devhub_readonly_evidence_envelope_v2"
PLAN = FIXTURES / "attended_devhub_readonly_live_dry_run_plan_v2.json"
LEDGER = FIXTURES / "post_briefing_dry_run_authorization_ledger_v2.json"


def _valid_envelope() -> dict:
    return build_envelope(load_fixture(PLAN), load_fixture(LEDGER))


def test_builds_cited_synthetic_read_only_observation_slots() -> None:
    envelope = _valid_envelope()

    assert envelope["version"] == ENVELOPE_VERSION
    assert envelope["mode"] == "fixture-first-attended-read-only"
    slots = envelope["observation_slots"]
    expected_slots = {
        "visible_surface_labels",
        "allowed_read_only_checks",
        "manual_login_mfa_captcha_handoff_notes",
        "redaction_checklist_outcomes",
        "operator_abort_conditions",
        "offline_validation_commands",
        "attestations",
    }
    assert set(slots) == expected_slots
    for name, slot in slots.items():
        assert slot["kind"] == "synthetic_read_only_observation_slot"
        assert slot["citations"], name
        assert slot["citations"][0]["source"].startswith(str(FIXTURES))


def test_attestations_cover_forbidden_live_artifacts() -> None:
    envelope = _valid_envelope()
    attestations = envelope["observation_slots"]["attestations"]["value"]

    assert attestations == {
        "no_live_devhub": True,
        "no_auth_state": True,
        "no_screenshot": True,
        "no_trace": True,
        "no_har": True,
        "no_surface_registry_mutation": True,
    }


def test_missing_attestation_is_rejected() -> None:
    plan = load_fixture(PLAN)
    ledger = load_fixture(LEDGER)
    ledger.document["attestations"]["no_har"] = False

    with pytest.raises(ValueError, match="no_har"):
        build_envelope(plan, ledger)


def test_rejects_uncited_observation_slot() -> None:
    envelope = _valid_envelope()
    envelope["observation_slots"]["visible_surface_labels"].pop("citations")

    result = validate_devhub_readonly_evidence_envelope_v2(envelope)

    assert not result.ok
    assert any("slot must include citations: visible_surface_labels" in error for error in result.errors)


def test_rejects_missing_manual_handoff_or_redaction_outcomes() -> None:
    envelope = _valid_envelope()
    envelope["observation_slots"].pop("manual_login_mfa_captcha_handoff_notes")
    envelope["observation_slots"]["redaction_checklist_outcomes"]["value"] = []

    result = validate_devhub_readonly_evidence_envelope_v2(envelope)

    assert not result.ok
    assert any("manual_login_mfa_captcha_handoff_notes is required" in error for error in result.errors)
    assert any("redaction_checklist_outcomes" in error for error in result.errors)


def test_rejects_private_authenticated_values_credentials_and_session_artifacts() -> None:
    envelope = _valid_envelope()
    envelope["observation_slots"]["visible_surface_labels"]["value"].append("Contact owner@example.test for permit number 24-123456-000-00-CO")
    envelope["credential"] = "redacted"
    envelope["session_state"] = "redacted"

    result = validate_devhub_readonly_evidence_envelope_v2(envelope)

    assert not result.ok
    assert any("private, authenticated, credential, or session values" in error for error in result.errors)


def test_rejects_screenshots_traces_har_references_and_browser_automation_claims() -> None:
    envelope = _valid_envelope()
    envelope["observation_slots"]["visible_surface_labels"]["value"].append("Playwright launched a live browser and captured a screenshot and HAR file.")

    result = validate_devhub_readonly_evidence_envelope_v2(envelope)

    assert not result.ok
    assert any("screenshots, traces, HAR" in error for error in result.errors)
    assert any("browser automation" in error for error in result.errors)


def test_rejects_live_devhub_completion_legal_guarantees_and_consequential_enablement() -> None:
    envelope = _valid_envelope()
    envelope["observation_slots"]["allowed_read_only_checks"]["value"] = [
        "Live DevHub completed the review and permit approval is guaranteed.",
        "Operator is allowed to click submit and complete payment.",
    ]

    result = validate_devhub_readonly_evidence_envelope_v2(envelope)

    assert not result.ok
    assert any("live completion" in error for error in result.errors)
    assert any("guarantee legal compliance or permitting outcomes" in error for error in result.errors)
    assert any("consequential DevHub actions" in error for error in result.errors)


def test_rejects_active_mutation_flags() -> None:
    for flag in (
        "active_surface_registry_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "monitoring_mutation",
        "release_state_mutation",
        "agent_state_mutation",
    ):
        envelope = deepcopy(_valid_envelope())
        envelope[flag] = True

        result = validate_devhub_readonly_evidence_envelope_v2(envelope)

        assert not result.ok
        assert any(flag in error for error in result.errors)
