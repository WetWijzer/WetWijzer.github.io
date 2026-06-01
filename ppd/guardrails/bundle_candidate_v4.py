"""Validation for PP&D guardrail bundle recompile candidate v4."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


_REQUIRED_SECTIONS = (
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
)

_PROHIBITED_TEXT = {
    "active_guardrail_mutation_claims": (
        "mutates active guardrail",
        "updates active guardrail",
        "edits active guardrail",
        "changes active guardrail",
        "active guardrail mutation",
    ),
    "private_session_auth_artifacts": (
        "session cookie",
        "auth token",
        "authorization header",
        "private devhub session",
        "mfa secret",
        "captcha token",
    ),
    "autonomous_official_action_claims": (
        "submit permit",
        "certify application",
        "cancel inspection",
        "upload official document",
        "pay fee",
        "autonomously file",
    ),
    "legal_or_permitting_guarantees": (
        "permit guaranteed",
        "approval guaranteed",
        "legally compliant",
        "legal guarantee",
        "will be approved",
    ),
}

_ACTIVE_FLAG_KEYS = frozenset(("active", "is_active", "mutates_active_guardrail", "active_mutation"))


class GuardrailCandidateV4ValidationError(ValueError):
    """Raised when a guardrail bundle recompile candidate v4 is invalid."""


def validate_guardrail_bundle_recompile_candidate_v4(candidate: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a PP&D guardrail bundle candidate v4."""

    errors: list[str] = []

    if candidate.get("candidate_version") != "v4":
        errors.append("candidate_version must be v4")

    for section in _REQUIRED_SECTIONS:
        value = candidate.get(section)
        if _is_missing_section(value):
            errors.append(f"missing required section: {section}")

    for path, value in _walk(candidate):
        if isinstance(value, str):
            lowered = value.lower()
            for category, phrases in _PROHIBITED_TEXT.items():
                if any(phrase in lowered for phrase in phrases):
                    errors.append(f"prohibited {category} at {path}")
        elif isinstance(value, bool):
            key = path.rsplit(".", 1)[-1]
            if key in _ACTIVE_FLAG_KEYS and value:
                errors.append(f"active mutation flag must not be true at {path}")

    return errors


def assert_valid_guardrail_bundle_recompile_candidate_v4(candidate: Mapping[str, Any]) -> None:
    """Raise if a PP&D guardrail bundle candidate v4 is invalid."""

    errors = validate_guardrail_bundle_recompile_candidate_v4(candidate)
    if errors:
        raise GuardrailCandidateV4ValidationError("; ".join(errors))


def _is_missing_section(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Mapping):
        return not value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return len(value) == 0
    return False


def _walk(value: Any, path: str = "candidate") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            items.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for index, child in enumerate(value):
            items.extend(_walk(child, f"{path}[{index}]"))
    return items
