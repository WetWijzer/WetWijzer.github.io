from __future__ import annotations

import json
from pathlib import Path

from ppd.logic.guardrail_refresh_regression_review import (
    GuardrailRefreshRegressionReviewError,
    assert_valid_guardrail_refresh_regression_review_packet,
    validate_guardrail_refresh_regression_review_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guardrail_refresh_regression_review"


def _valid_packet() -> dict:
    return json.loads((FIXTURE_DIR / "valid_packet.json").read_text(encoding="utf-8"))


def test_accepts_cited_offline_regression_review_packet() -> None:
    packet = _valid_packet()

    assert validate_guardrail_refresh_regression_review_packet(packet) == []
    assert_valid_guardrail_refresh_regression_review_packet(packet)


def test_rejects_missing_required_review_metadata() -> None:
    packet = {
        "expectations": [{"statement": "Draft-only actions remain blocked."}],
        "rollback_notes": "",
        "reviewer_owners": [],
        "offline_validation_commands": [],
    }

    codes = {finding.code for finding in validate_guardrail_refresh_regression_review_packet(packet)}

    assert "missing_affected_guardrail_bundle_ids" in codes
    assert "missing_rollback_notes" in codes
    assert "missing_reviewer_owners" in codes
    assert "missing_offline_validation_commands" in codes
    assert "uncited_expectation" in codes


def test_rejects_private_auth_and_local_path_material() -> None:
    packet = _valid_packet()
    packet["notes"] = [
        "Contains private case fact from account-scoped intake.",
        "cookie=session-token-value",
        "Review artifact path: /home/alex/private/devhub/state.json",
    ]

    codes = {finding.code for finding in validate_guardrail_refresh_regression_review_packet(packet)}

    assert "private_case_fact" in codes
    assert "raw_authenticated_value" in codes
    assert "local_private_path" in codes


def test_rejects_live_execution_claims_and_outcome_guarantees() -> None:
    packet = _valid_packet()
    packet["review_notes"] = "Ran live DevHub and executed crawler; permit will be approved."

    codes = {finding.code for finding in validate_guardrail_refresh_regression_review_packet(packet)}

    assert "live_execution_claim" in codes
    assert "outcome_guarantee" in codes


def test_rejects_enabled_consequential_controls_and_mutation_flags() -> None:
    packet = _valid_packet()
    packet["controls"] = {
        "allow_payment": True,
        "submit_enabled": True,
    }
    packet["mutations"] = {
        "prompt_mutation_enabled": True,
        "guardrail_mutation_enabled": True,
        "surface_registry_mutation_enabled": True,
        "monitoring_mutation_enabled": True,
        "release_state_mutation_enabled": True,
    }

    codes = [finding.code for finding in validate_guardrail_refresh_regression_review_packet(packet)]

    assert codes.count("enabled_consequential_control") == 2
    assert codes.count("active_mutation_flag") == 5


def test_assert_helper_raises_with_findings() -> None:
    packet = _valid_packet()
    packet["expectations"][0].pop("citations")

    try:
        assert_valid_guardrail_refresh_regression_review_packet(packet)
    except GuardrailRefreshRegressionReviewError as error:
        assert {finding.code for finding in error.findings} == {"uncited_expectation"}
    else:
        raise AssertionError("expected GuardrailRefreshRegressionReviewError")
