from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.guardrails.bundle_candidate_v4 import (
    GuardrailCandidateV4ValidationError,
    assert_valid_guardrail_bundle_recompile_candidate_v4,
    validate_guardrail_bundle_recompile_candidate_v4,
)


_FIXTURE = Path(__file__).parent / "fixtures" / "guardrails" / "candidate_v4_valid.json"


@pytest.fixture()
def valid_candidate() -> dict[str, object]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def test_valid_candidate_has_no_errors(valid_candidate: dict[str, object]) -> None:
    assert validate_guardrail_bundle_recompile_candidate_v4(valid_candidate) == []
    assert_valid_guardrail_bundle_recompile_candidate_v4(valid_candidate)


@pytest.mark.parametrize(
    "section",
    [
        "process_impact_references",
        "prior_guardrail_placeholders",
        "inactive_predicate_changes",
        "reversible_action_gates",
        "exact_confirmation_gates",
        "refused_consequential_financial_action_gates",
        "stale_evidence_blocks",
        "explanation_templates",
        "reviewer_holds",
        "rollback_notes",
        "validation_commands",
    ],
)
def test_rejects_missing_required_sections(valid_candidate: dict[str, object], section: str) -> None:
    candidate = copy.deepcopy(valid_candidate)
    candidate.pop(section)

    errors = validate_guardrail_bundle_recompile_candidate_v4(candidate)

    assert f"missing required section: {section}" in errors


@pytest.mark.parametrize(
    ("field", "claim", "expected"),
    [
        ("notes", "candidate mutates active guardrail state", "active_guardrail_mutation_claims"),
        ("notes", "contains session cookie from a browser profile", "private_session_auth_artifacts"),
        ("notes", "agent may submit permit after review", "autonomous_official_action_claims"),
        ("notes", "permit guaranteed after these checks", "legal_or_permitting_guarantees"),
    ],
)
def test_rejects_prohibited_claims(
    valid_candidate: dict[str, object], field: str, claim: str, expected: str
) -> None:
    candidate = copy.deepcopy(valid_candidate)
    candidate[field] = [claim]

    errors = validate_guardrail_bundle_recompile_candidate_v4(candidate)

    assert any(expected in error for error in errors)


@pytest.mark.parametrize(
    "flag",
    [
        "active",
        "is_active",
        "mutates_active_guardrail",
        "active_mutation",
    ],
)
def test_rejects_active_mutation_flags(valid_candidate: dict[str, object], flag: str) -> None:
    candidate = copy.deepcopy(valid_candidate)
    candidate["inactive_predicate_changes"] = [{"name": "bad", flag: True}]

    errors = validate_guardrail_bundle_recompile_candidate_v4(candidate)

    assert any("active mutation flag must not be true" in error for error in errors)


def test_assertion_helper_raises_combined_error(valid_candidate: dict[str, object]) -> None:
    candidate = copy.deepcopy(valid_candidate)
    candidate.pop("reviewer_holds")
    candidate["notes"] = ["approval guaranteed"]

    with pytest.raises(GuardrailCandidateV4ValidationError) as exc_info:
        assert_valid_guardrail_bundle_recompile_candidate_v4(candidate)

    message = str(exc_info.value)
    assert "missing required section: reviewer_holds" in message
    assert "legal_or_permitting_guarantees" in message
