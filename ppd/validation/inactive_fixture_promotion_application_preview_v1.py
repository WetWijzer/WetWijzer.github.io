"""Validation for inactive fixture promotion application preview v1.

This validator is intentionally local and deterministic. It checks preview metadata and
textual fields before any promotion can be treated as executable or applied.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


BLOCKED_TEXT_PATTERNS = (
    "captcha",
    "mfa",
    "auth state",
    "authenticated session",
    "session cookie",
    "browser trace",
    "playwright trace",
    "private devhub",
    "raw crawl",
    "raw pdf",
    "downloaded pdf",
    "downloaded data",
    "live execution",
    "executed live",
    "promotion applied",
    "applied promotion",
    "guarantee approval",
    "guarantees approval",
    "permit will be issued",
    "legal outcome",
    "must submit",
    "must file",
    "must pay",
    "certify",
    "cancel permit",
    "upload documents",
)

MUTATION_FLAG_KEYS = (
    "active_artifact_mutation",
    "release_state_mutation",
    "fixture_mutation",
    "agent_state_mutation",
    "mutates_active_artifacts",
    "mutates_release_state",
    "mutates_fixtures",
    "mutates_agent_state",
    "writes_active_artifacts",
    "writes_release_state",
    "writes_fixtures",
    "writes_agent_state",
)


@dataclass(frozen=True)
class ValidationResult:
    """Result for an inactive fixture promotion preview validation."""

    ok: bool
    errors: tuple[str, ...]


def validate_inactive_fixture_promotion_application_preview_v1(
    preview: Mapping[str, Any],
) -> ValidationResult:
    """Validate an inactive fixture promotion application preview v1 payload."""

    errors: list[str] = []

    if preview.get("schema_version") != "inactive_fixture_promotion_application_preview_v1":
        errors.append("schema_version must be inactive_fixture_promotion_application_preview_v1")

    _require_mapping(preview, "before_fixture_preview", errors)
    _require_mapping(preview, "after_fixture_preview", errors)
    _require_non_empty_sequence(preview, "source_citations", errors)
    _require_non_empty_sequence(preview, "observation_evidence", errors)
    _require_mapping(preview, "citation_preservation_checks", errors)
    _require_non_empty_sequence(preview, "blocked_row_explanations", errors)
    _require_non_empty_sequence(preview, "validation_replay_inventory", errors)
    _require_non_empty_sequence(preview, "reviewer_signoff_placeholders", errors)
    _require_non_empty_text(preview, "rollback_notes", errors)

    for key in MUTATION_FLAG_KEYS:
        if preview.get(key) is True:
            errors.append(f"{key} must not be true for an inactive preview")

    if preview.get("active") is True:
        errors.append("active must not be true for an inactive preview")
    if preview.get("release_state") in {"active", "released", "published"}:
        errors.append("release_state must not claim an active release state")

    text = _flatten_text(preview).lower()
    for pattern in BLOCKED_TEXT_PATTERNS:
        if pattern in text:
            errors.append(f"blocked language or artifact reference found: {pattern}")

    return ValidationResult(ok=not errors, errors=tuple(errors))


def assert_inactive_fixture_promotion_application_preview_v1(
    preview: Mapping[str, Any],
) -> None:
    """Raise ValueError when the preview is invalid."""

    result = validate_inactive_fixture_promotion_application_preview_v1(preview)
    if not result.ok:
        raise ValueError("; ".join(result.errors))


def _require_mapping(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = payload.get(key)
    if not isinstance(value, Mapping) or not value:
        errors.append(f"{key} is required and must be a non-empty mapping")


def _require_non_empty_sequence(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = payload.get(key)
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
        errors.append(f"{key} is required and must be a non-empty sequence")


def _require_non_empty_text(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key} is required and must be non-empty text")


def _flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(str(key) + " " + _flatten_text(item) for key, item in value.items())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return " ".join(_flatten_text(item) for item in value)
    return ""
