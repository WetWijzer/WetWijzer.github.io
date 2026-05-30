"""Validation for inactive DevHub observed-surface patch previews v2.

The preview is an offline review artifact. It may describe candidate observations, but it
must not contain private browser/session artifacts, raw crawl output, live DevHub action
claims, outcome guarantees, or active mutation flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


EXPECTED_PREVIEW_VERSION = "devhub_observed_surface_inactive_patch_preview_v2"
EXPECTED_MODE = "inactive_patch_preview"
EXPECTED_SURFACE_STATE = "inactive"

MUTATION_FLAG_NAMES = (
    "active_devhub_surface_mutation",
    "active_devhub_process_mutation",
    "active_devhub_guardrail_mutation",
    "active_devhub_release_state_mutation",
    "active_devhub_fixture_mutation",
    "active_devhub_agent_state_mutation",
)

PRIVATE_ARTIFACT_TOKENS = (
    "auth_state",
    "browser_context",
    "cookie",
    "credential",
    "har",
    "local_storage",
    "mfa",
    "password",
    "playwright_trace",
    "private_devhub_session",
    "screenshot",
    "session_storage",
    "trace.zip",
)

RAW_ARTIFACT_TOKENS = (
    "downloaded_pdf",
    "downloaded-data",
    "downloaded_data",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "warc",
)

LIVE_EXECUTION_TOKENS = (
    "executed in devhub",
    "live devhub execution",
    "live run completed",
    "promoted to active",
    "production promotion",
    "released to active",
)

OUTCOME_GUARANTEE_TOKENS = (
    "approval guaranteed",
    "guarantees approval",
    "guarantees issuance",
    "permit will be approved",
    "permit will be issued",
    "review outcome guaranteed",
)

CONSEQUENTIAL_ACTION_TOKENS = (
    "certify acknowledgement",
    "pay the fee",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit correction",
    "upload correction",
    "withdraw permit",
)


@dataclass(frozen=True)
class PreviewViolation:
    """A deterministic validation failure for an inactive patch preview."""

    code: str
    message: str


def validate_inactive_patch_preview_v2(packet: Mapping[str, Any]) -> list[PreviewViolation]:
    """Return every violation found in an inactive patch preview packet."""

    violations: list[PreviewViolation] = []

    _require_equal(violations, packet, "preview_version", EXPECTED_PREVIEW_VERSION)
    _require_equal(violations, packet, "mode", EXPECTED_MODE)
    _require_equal(violations, packet, "surface_state", EXPECTED_SURFACE_STATE)
    _require_equal(violations, packet, "devhub_execution", "none")
    _require_equal(violations, packet, "promotion_claim", "none")

    _validate_before_after_rows(violations, packet.get("rows"))
    _validate_observation_evidence(violations, packet.get("observation_evidence"))
    _validate_selector_confidence_notes(violations, packet.get("selector_confidence_notes"))
    _validate_gates(violations, packet.get("gates"))
    _validate_blocked_rows(violations, packet.get("blocked_rows"))
    _validate_validation_inventory(violations, packet.get("validation_inventory"))
    _validate_mutation_flags(violations, packet.get("mutation_flags"))
    _validate_artifacts(violations, packet.get("artifact_manifest"))
    _validate_text_claims(violations, packet)

    return violations


def assert_valid_inactive_patch_preview_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the inactive patch preview packet is invalid."""

    violations = validate_inactive_patch_preview_v2(packet)
    if violations:
        detail = "; ".join(f"{violation.code}: {violation.message}" for violation in violations)
        raise ValueError(detail)


def _require_equal(
    violations: list[PreviewViolation], packet: Mapping[str, Any], field_name: str, expected: str
) -> None:
    if packet.get(field_name) != expected:
        violations.append(
            PreviewViolation(
                code=f"invalid_{field_name}",
                message=f"{field_name} must be {expected!r} for inactive preview v2",
            )
        )


def _validate_before_after_rows(violations: list[PreviewViolation], rows: Any) -> None:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        violations.append(PreviewViolation("missing_before_after_rows", "rows must include before/after entries"))
        return

    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            violations.append(PreviewViolation("invalid_row", f"row {index} must be an object"))
            continue
        if not row.get("before") or not row.get("after"):
            violations.append(
                PreviewViolation("missing_before_after_rows", f"row {index} must include before and after values")
            )
        if not row.get("observation_evidence_id"):
            violations.append(
                PreviewViolation("uncited_observation_evidence", f"row {index} must cite observation evidence")
            )


def _validate_observation_evidence(violations: list[PreviewViolation], evidence: Any) -> None:
    if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)) or not evidence:
        violations.append(
            PreviewViolation("uncited_observation_evidence", "observation_evidence must include cited evidence")
        )
        return

    for index, item in enumerate(evidence):
        if not isinstance(item, Mapping):
            violations.append(PreviewViolation("invalid_observation_evidence", f"evidence {index} must be an object"))
            continue
        missing = [name for name in ("evidence_id", "citation", "observed_at", "summary") if not item.get(name)]
        if missing:
            violations.append(
                PreviewViolation(
                    "uncited_observation_evidence",
                    f"evidence {index} is missing required fields: {', '.join(missing)}",
                )
            )


def _validate_selector_confidence_notes(violations: list[PreviewViolation], notes: Any) -> None:
    if not isinstance(notes, Sequence) or isinstance(notes, (str, bytes)) or not notes:
        violations.append(
            PreviewViolation("missing_selector_confidence_notes", "selector_confidence_notes must be populated")
        )
        return

    for index, note in enumerate(notes):
        if not isinstance(note, Mapping) or not note.get("selector") or not note.get("confidence_note"):
            violations.append(
                PreviewViolation(
                    "missing_selector_confidence_notes",
                    f"selector confidence note {index} must include selector and confidence_note",
                )
            )


def _validate_gates(violations: list[PreviewViolation], gates: Any) -> None:
    if not isinstance(gates, Mapping):
        violations.append(PreviewViolation("missing_redaction_gate", "gates.redaction must be present"))
        violations.append(PreviewViolation("missing_attendance_gate", "gates.attendance must be present"))
        return

    redaction = gates.get("redaction")
    attendance = gates.get("attendance")
    if not isinstance(redaction, Mapping) or redaction.get("status") != "pass" or not redaction.get("notes"):
        violations.append(PreviewViolation("missing_redaction_gate", "redaction gate must pass with notes"))
    if not isinstance(attendance, Mapping) or attendance.get("status") != "pass" or not attendance.get("notes"):
        violations.append(PreviewViolation("missing_attendance_gate", "attendance gate must pass with notes"))


def _validate_blocked_rows(violations: list[PreviewViolation], blocked_rows: Any) -> None:
    if not isinstance(blocked_rows, Sequence) or isinstance(blocked_rows, (str, bytes)) or not blocked_rows:
        violations.append(
            PreviewViolation("missing_blocked_row_explanations", "blocked_rows must explain refused or unavailable rows")
        )
        return

    for index, row in enumerate(blocked_rows):
        if not isinstance(row, Mapping) or not row.get("row_id") or not row.get("explanation"):
            violations.append(
                PreviewViolation(
                    "missing_blocked_row_explanations",
                    f"blocked row {index} must include row_id and explanation",
                )
            )


def _validate_validation_inventory(violations: list[PreviewViolation], inventory: Any) -> None:
    if not isinstance(inventory, Sequence) or isinstance(inventory, (str, bytes)) or not inventory:
        violations.append(PreviewViolation("missing_validation_inventory", "validation_inventory must be populated"))
        return

    required = {
        "before_after_rows",
        "observation_evidence",
        "selector_confidence_notes",
        "redaction_gate",
        "attendance_gate",
        "blocked_row_explanations",
        "artifact_exclusion",
        "mutation_flags",
    }
    observed = {item.get("check") for item in inventory if isinstance(item, Mapping)}
    missing = sorted(required - observed)
    if missing:
        violations.append(
            PreviewViolation("missing_validation_inventory", f"validation_inventory missing checks: {', '.join(missing)}")
        )


def _validate_mutation_flags(violations: list[PreviewViolation], mutation_flags: Any) -> None:
    if not isinstance(mutation_flags, Mapping):
        violations.append(PreviewViolation("active_mutation_flag", "mutation_flags must be present and false"))
        return

    for flag_name in MUTATION_FLAG_NAMES:
        if mutation_flags.get(flag_name) is not False:
            violations.append(
                PreviewViolation("active_mutation_flag", f"{flag_name} must be false for inactive preview v2")
            )


def _validate_artifacts(violations: list[PreviewViolation], artifact_manifest: Any) -> None:
    if artifact_manifest in (None, []):
        return
    if not isinstance(artifact_manifest, Sequence) or isinstance(artifact_manifest, (str, bytes)):
        violations.append(PreviewViolation("private_or_raw_artifact", "artifact_manifest must be a list when present"))
        return

    for index, artifact in enumerate(artifact_manifest):
        text = _flatten_text(artifact).lower()
        if any(token in text for token in PRIVATE_ARTIFACT_TOKENS):
            violations.append(
                PreviewViolation("private_or_session_artifact", f"artifact {index} references private/auth/session/browser data")
            )
        if any(token in text for token in RAW_ARTIFACT_TOKENS):
            violations.append(PreviewViolation("raw_crawl_or_download_artifact", f"artifact {index} references raw data"))


def _validate_text_claims(violations: list[PreviewViolation], packet: Mapping[str, Any]) -> None:
    text = _flatten_text(packet).lower()
    for token in LIVE_EXECUTION_TOKENS:
        if token in text:
            violations.append(PreviewViolation("live_devhub_execution_or_promotion_claim", f"forbidden claim: {token}"))
    for token in OUTCOME_GUARANTEE_TOKENS:
        if token in text:
            violations.append(PreviewViolation("legal_or_permitting_outcome_guarantee", f"forbidden guarantee: {token}"))
    for token in CONSEQUENTIAL_ACTION_TOKENS:
        if token in text:
            violations.append(PreviewViolation("consequential_action_language", f"forbidden action language: {token}"))


def _flatten_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(str(key) + " " + _flatten_text(item) for key, item in value.items())
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)
