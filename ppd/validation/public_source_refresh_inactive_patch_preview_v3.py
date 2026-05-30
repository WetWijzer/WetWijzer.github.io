"""Validation for inactive public source refresh patch previews v3.

This module is intentionally narrow: it validates preview payloads before any
source refresh can claim promotion, mutation, or consequential permitting/legal
outcomes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


MUTATION_FLAG_FIELDS = (
    "active_source_mutation",
    "document_mutation",
    "requirement_mutation",
    "process_mutation",
    "guardrail_mutation",
    "release_state_mutation",
    "agent_state_mutation",
)

FORBIDDEN_TEXT_MARKERS = (
    "private devhub session",
    "authenticated session",
    "auth state",
    "browser trace",
    "session cookie",
    "raw crawl",
    "raw pdf",
    "downloaded pdf",
    "downloaded data",
    "live crawl completed",
    "promoted to active",
    "promotion completed",
    "permit approved",
    "permit guaranteed",
    "legal guarantee",
    "you must apply",
    "you should submit",
    "take consequential action",
)


@dataclass(frozen=True)
class PreviewValidationResult:
    """Result returned by inactive preview validation."""

    ok: bool
    errors: tuple[str, ...]


def validate_inactive_patch_preview_v3(preview: Mapping[str, Any]) -> PreviewValidationResult:
    """Validate an inactive public source refresh patch preview v3 payload."""

    errors: list[str] = []

    if preview.get("preview_version") != 3:
        errors.append("preview_version must be 3")
    if preview.get("state") != "inactive_patch_preview":
        errors.append("state must be inactive_patch_preview")

    rows = preview.get("rows")
    if not _is_non_empty_sequence(rows):
        errors.append("rows must contain at least one before/after row")
    else:
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                errors.append(f"rows[{index}] must be an object")
                continue
            if not row.get("before"):
                errors.append(f"rows[{index}] is missing before")
            if not row.get("after"):
                errors.append(f"rows[{index}] is missing after")
            if not _is_non_empty_sequence(row.get("source_evidence")):
                errors.append(f"rows[{index}] is missing cited source_evidence")
            elif not all(_has_citation(evidence) for evidence in row["source_evidence"]):
                errors.append(f"rows[{index}] has uncited source_evidence")
            if not row.get("citation_preservation_check"):
                errors.append(f"rows[{index}] is missing citation_preservation_check")
            if not row.get("affected_requirement"):
                errors.append(f"rows[{index}] is missing affected_requirement")
            if not row.get("affected_process"):
                errors.append(f"rows[{index}] is missing affected_process")
            if not row.get("affected_guardrail"):
                errors.append(f"rows[{index}] is missing affected_guardrail")

    blocked_rows = preview.get("blocked_rows")
    if not _is_non_empty_sequence(blocked_rows):
        errors.append("blocked_rows must explain every blocked row")
    else:
        for index, blocked_row in enumerate(blocked_rows):
            if not isinstance(blocked_row, Mapping):
                errors.append(f"blocked_rows[{index}] must be an object")
                continue
            if not blocked_row.get("row_id"):
                errors.append(f"blocked_rows[{index}] is missing row_id")
            if not blocked_row.get("explanation"):
                errors.append(f"blocked_rows[{index}] is missing explanation")

    inventory = preview.get("validation_inventory")
    if not isinstance(inventory, Mapping) or not inventory:
        errors.append("validation_inventory is required")
    else:
        for key in ("sources", "documents", "requirements", "processes", "guardrails"):
            if not _is_non_empty_sequence(inventory.get(key)):
                errors.append(f"validation_inventory.{key} must be non-empty")

    for field in MUTATION_FLAG_FIELDS:
        if preview.get(field) is not False:
            errors.append(f"{field} must be false")

    combined_text = _flatten_text(preview).lower()
    for marker in FORBIDDEN_TEXT_MARKERS:
        if marker in combined_text:
            errors.append(f"forbidden content marker present: {marker}")

    return PreviewValidationResult(ok=not errors, errors=tuple(errors))


def assert_valid_inactive_patch_preview_v3(preview: Mapping[str, Any]) -> None:
    """Raise ValueError when an inactive patch preview v3 payload is invalid."""

    result = validate_inactive_patch_preview_v3(preview)
    if not result.ok:
        raise ValueError("inactive patch preview v3 validation failed: " + "; ".join(result.errors))


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _has_citation(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    citation = value.get("citation")
    return isinstance(citation, Mapping) and bool(citation.get("source_id")) and bool(citation.get("locator"))


def _flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return "\n".join(_flatten_text(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return "\n".join(_flatten_text(item) for item in value)
    return ""
