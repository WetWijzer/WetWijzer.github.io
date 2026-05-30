"""Validation for DevHub observed surface update plan v2 candidates.

The validator is intentionally conservative: missing fields fail closed and any
claim that implies live DevHub execution, legal/permitting guarantees,
consequential action, private artifacts, raw crawl data, or active mutation is
rejected.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any


FORBIDDEN_ARTIFACT_TERMS = (
    "auth_state",
    "authenticated",
    "browser_storage",
    "cookie",
    "cookies",
    "downloaded_pdf",
    "downloaded data",
    "har",
    "localstorage",
    "private devhub session",
    "raw crawl",
    "raw pdf",
    "session artifact",
    "session file",
    "trace.zip",
)

LIVE_EXECUTION_TERMS = (
    "clicked submit",
    "executed in devhub",
    "filed permit",
    "live devhub",
    "logged in",
    "submitted application",
    "uploaded document",
)

OUTCOME_GUARANTEE_TERMS = (
    "approval guaranteed",
    "approved permit",
    "guarantee approval",
    "guarantees approval",
    "legal advice",
    "permit will be issued",
    "will be approved",
)

CONSEQUENTIAL_ACTION_TERMS = (
    "cancel inspection",
    "certify",
    "create account",
    "make payment",
    "pay fee",
    "schedule inspection",
    "submit application",
    "upload document",
)

MUTATION_FLAG_NAMES = (
    "mutates_active_agent_state",
    "mutates_active_devhub_guardrails",
    "mutates_active_devhub_process",
    "mutates_active_devhub_prompt",
    "mutates_active_devhub_release_state",
    "mutates_active_devhub_surface",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_process",
    "mutates_prompt",
    "mutates_release_state",
    "mutates_surface",
)

REQUIRED_TOP_LEVEL_FIELDS = (
    "candidates",
    "selector_confidence_review_rows",
    "redaction_checks",
    "manual_attendance_gates",
    "reviewer_owner",
    "rollback_note",
)


@dataclass(frozen=True)
class ValidationIssue:
    """A single fail-closed validation issue."""

    code: str
    message: str


def validate_devhub_observed_surface_update_plan_v2(plan: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return validation issues for a DevHub observed surface update plan v2."""

    issues: list[ValidationIssue] = []

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if _is_blank(plan.get(field)):
            issues.append(ValidationIssue("missing_required_field", f"Missing required field: {field}"))

    candidates = plan.get("candidates")
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)) or not candidates:
        issues.append(ValidationIssue("missing_candidates", "At least one surface update candidate is required."))
    else:
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, Mapping):
                issues.append(ValidationIssue("invalid_candidate", f"Candidate {index} must be an object."))
                continue
            if _is_blank(candidate.get("citations")):
                issues.append(ValidationIssue("uncited_candidate", f"Candidate {index} must include citations."))
            if _is_blank(candidate.get("selector_confidence_review_row_id")):
                issues.append(
                    ValidationIssue(
                        "missing_selector_confidence_review_row",
                        f"Candidate {index} must reference a selector-confidence review row.",
                    )
                )
            if _truthy_mutation_flag(candidate):
                issues.append(ValidationIssue("active_mutation_flag", f"Candidate {index} declares an active mutation flag."))

    if not _has_review_rows(plan.get("selector_confidence_review_rows")):
        issues.append(
            ValidationIssue(
                "missing_selector_confidence_review_rows",
                "Selector-confidence review rows are required and must include selector and confidence fields.",
            )
        )

    if not _checks_pass(plan.get("redaction_checks")):
        issues.append(ValidationIssue("missing_redaction_checks", "Redaction checks are required and must pass."))

    if not _manual_gates_present(plan.get("manual_attendance_gates")):
        issues.append(
            ValidationIssue(
                "missing_manual_attendance_gates",
                "Manual attendance gates are required for observed DevHub surface updates.",
            )
        )

    if _truthy_mutation_flag(plan):
        issues.append(ValidationIssue("active_mutation_flag", "Plan declares an active mutation flag."))

    text = _flatten_text(plan).lower()
    _reject_terms(issues, text, FORBIDDEN_ARTIFACT_TERMS, "private_or_raw_artifact")
    _reject_terms(issues, text, LIVE_EXECUTION_TERMS, "live_devhub_execution_claim")
    _reject_terms(issues, text, OUTCOME_GUARANTEE_TERMS, "legal_or_permitting_outcome_guarantee")
    _reject_terms(issues, text, CONSEQUENTIAL_ACTION_TERMS, "consequential_action_language")

    return issues


def assert_valid_devhub_observed_surface_update_plan_v2(plan: Mapping[str, Any]) -> None:
    """Raise ValueError when the plan is not acceptable."""

    issues = validate_devhub_observed_surface_update_plan_v2(plan)
    if issues:
        detail = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        raise ValueError(detail)


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Mapping):
        return not value
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return not value
    return False


def _has_review_rows(value: Any) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        return False
    for row in value:
        if not isinstance(row, Mapping):
            return False
        if _is_blank(row.get("selector")) or _is_blank(row.get("confidence")):
            return False
    return True


def _checks_pass(value: Any) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        return False
    for check in value:
        if not isinstance(check, Mapping):
            return False
        if check.get("passed") is not True:
            return False
    return True


def _manual_gates_present(value: Any) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        return False
    for gate in value:
        if not isinstance(gate, Mapping):
            return False
        if gate.get("required") is not True:
            return False
        if _is_blank(gate.get("name")):
            return False
    return True


def _truthy_mutation_flag(value: Mapping[str, Any]) -> bool:
    for name in MUTATION_FLAG_NAMES:
        if value.get(name) is True:
            return True
    flags = value.get("mutation_flags")
    if isinstance(flags, Mapping):
        return any(flags.get(name) is True for name in MUTATION_FLAG_NAMES) or any(flags.values())
    if isinstance(flags, Iterable) and not isinstance(flags, (str, bytes, Mapping)):
        return any(bool(flag) for flag in flags)
    return False


def _flatten_text(value: Any) -> str:
    parts: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            parts.append(str(key))
            parts.append(_flatten_text(item))
    elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        for item in value:
            parts.append(_flatten_text(item))
    elif value is not None:
        parts.append(str(value))
    return "\n".join(parts)


def _reject_terms(issues: list[ValidationIssue], text: str, terms: Sequence[str], code: str) -> None:
    for term in terms:
        if term in text:
            issues.append(ValidationIssue(code, f"Forbidden language or artifact reference detected: {term}"))
