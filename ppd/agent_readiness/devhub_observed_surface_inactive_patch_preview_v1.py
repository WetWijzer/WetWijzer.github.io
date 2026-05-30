"""Fixture-first DevHub observed-surface inactive patch preview v1.

This module builds and validates offline-only inactive surface-map delta previews from
approved DevHub read-only observation reviewer disposition queue v1 rows. It does not
execute DevHub automation, promote active surfaces, or store browser/session artifacts.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ppd.agent_readiness.devhub_read_only_observation_reviewer_disposition_queue_v1 import (
    QUEUE_VERSION,
    assert_valid_devhub_read_only_observation_reviewer_disposition_queue_v1,
)

EXPECTED_PREVIEW_VERSION = "devhub_observed_surface_inactive_patch_preview_v1"
EXPECTED_MODE = "inactive_patch_preview"
EXPECTED_SURFACE_STATE = "inactive"
EXPECTED_FIXTURE_SCOPE = "inactive_devhub_surface_fixture_preview"

PRIVATE_ARTIFACT_TOKENS = (
    "auth",
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
    "downloaded document",
    "downloaded pdf",
    "downloaded-data",
    "downloaded_data",
    "pdf download",
    "raw crawl",
    "raw_crawl",
    "raw download",
    "raw_download",
    "raw html",
    "raw_html",
    "raw pdf",
    "raw_pdf",
    "warc",
)

LIVE_EXECUTION_TOKENS = (
    "applied promotion",
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
    "cancel inspection",
    "cancel permit",
    "certification",
    "certify",
    "pay fee",
    "pay the fee",
    "payment",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit correction",
    "submission",
    "upload correction",
    "upload file",
    "upload plans",
)

REQUIRED_VALIDATION_CHECKS = frozenset(
    {
        "approved_disposition_rows_consumed",
        "inactive_surface_map_delta_previews",
        "selector_confidence_placeholders",
        "accessible_role_name_evidence_placeholders",
        "redacted_field_inventory_placeholders",
        "action_classification_references",
        "reviewer_signoff_placeholders",
        "validation_commands",
        "artifact_exclusion",
        "text_claim_exclusion",
        "mutation_scope",
    }
)

ALLOWED_TRUE_MUTATION_FLAGS = frozenset({EXPECTED_FIXTURE_SCOPE})


@dataclass(frozen=True)
class PreviewViolation:
    """A deterministic validation failure for an inactive patch preview."""

    code: str
    message: str


def build_inactive_patch_preview_from_disposition_packet_v1(disposition_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Return an inactive preview packet from approved read-only disposition rows."""

    assert_valid_devhub_read_only_observation_reviewer_disposition_queue_v1(disposition_packet)
    buckets = {
        str(bucket.get("bucket_id") or bucket.get("id")): bucket
        for bucket in disposition_packet.get("safe_read_only_surface_buckets", [])
        if isinstance(bucket, Mapping)
    }
    rows = [
        row
        for row in disposition_packet.get("reviewer_decision_rows", [])
        if isinstance(row, Mapping) and row.get("reviewer_decision") == "approve_read_only"
    ]
    evidence = [_evidence_from_row(row) for row in rows]
    previews = []
    selector_placeholders = []
    role_name_placeholders = []
    redacted_field_placeholders = []
    classifications = []
    consumed = []
    for index, row in enumerate(rows, start=1):
        row_id = str(row.get("row_id"))
        bucket = buckets.get(str(row.get("safe_read_only_surface_bucket_id")), {})
        surface_ids = [str(value) for value in bucket.get("surface_ids", []) if isinstance(value, str) and value]
        surface_id = surface_ids[0] if surface_ids else f"inactive-devhub-observed-surface-{index}"
        evidence_id = f"obs-evidence-{row_id}"
        consumed.append(
            {
                "row_id": row_id,
                "reviewer_decision": "approve_read_only",
                "source_queue_version": QUEUE_VERSION,
                "evidence_id": evidence_id,
            }
        )
        previews.append(
            {
                "preview_id": f"inactive-delta-{row_id}",
                "delta_type": "inactive_surface_map_delta",
                "source_disposition_row_id": row_id,
                "surface_id": surface_id,
                "before": {"surface_state": "absent_from_inactive_fixture", "actions": [], "fields": []},
                "after": {
                    "surface_state": "inactive_fixture_preview_only",
                    "auth_scope": "devhub_read_only_observation",
                    "surface_id": surface_id,
                    "action_refs": [f"action-classification-{row_id}"],
                },
                "observation_evidence_ids": [evidence_id],
            }
        )
        selector_placeholders.append(
            {
                "placeholder_id": f"selector-confidence-{row_id}",
                "surface_id": surface_id,
                "selector": "placeholder:reviewer-supplied-accessible-selector",
                "confidence": "placeholder_pending_review",
                "confidence_note": "Reserved for offline reviewer selector confidence evidence.",
            }
        )
        role_name_placeholders.append(
            {
                "placeholder_id": f"role-name-evidence-{row_id}",
                "surface_id": surface_id,
                "role": "placeholder_role",
                "name": "placeholder_name",
                "evidence_placeholder": "Reserved for accessible role and name evidence from the approved read-only observation row.",
            }
        )
        redacted_field_placeholders.append(
            {
                "placeholder_id": f"redacted-field-inventory-{row_id}",
                "surface_id": surface_id,
                "field_ref": "placeholder_redacted_field_ref",
                "redaction_policy": "redacted_placeholder_only",
                "status": "pending_reviewer_inventory",
            }
        )
        classifications.append(
            {
                "classification_ref": f"action-classification-{row_id}",
                "source_disposition_row_id": row_id,
                "surface_id": surface_id,
                "classification": "safe_read_only",
                "guardrail_effect": "observe_only",
            }
        )
    return {
        "preview_version": EXPECTED_PREVIEW_VERSION,
        "mode": EXPECTED_MODE,
        "surface_state": EXPECTED_SURFACE_STATE,
        "fixture_scope": EXPECTED_FIXTURE_SCOPE,
        "disposition_packet_version": QUEUE_VERSION,
        "devhub_execution": "none",
        "promotion_claim": "none",
        "disposition_rows_consumed": consumed,
        "observation_evidence": evidence,
        "inactive_fixture_previews": previews,
        "selector_confidence_placeholders": selector_placeholders,
        "accessible_role_name_evidence_placeholders": role_name_placeholders,
        "redacted_field_inventory_placeholders": redacted_field_placeholders,
        "action_classification_references": classifications,
        "reviewer_signoff_placeholders": [
            {"role": "surface_reviewer", "status": "pending", "notes_placeholder": "Reviewer confirms inactive fixture preview only."},
            {"role": "guardrail_reviewer", "status": "pending", "notes_placeholder": "Reviewer confirms no active guardrail change."},
        ],
        "rollback_notes": ["Discard this inactive fixture preview packet; no active artifact restore is required."],
        "validation_commands": [
            ["python3", "-m", "py_compile", "ppd/agent_readiness/devhub_observed_surface_inactive_patch_preview_v1.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_devhub_observed_surface_inactive_patch_preview_v1.py"],
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ],
        "validation_inventory": [
            {"check": check, "status": "included"} for check in sorted(REQUIRED_VALIDATION_CHECKS)
        ],
        "mutation_flags": {
            EXPECTED_FIXTURE_SCOPE: True,
            "active_devhub_surface_mutation": False,
            "active_devhub_guardrail_mutation": False,
            "active_devhub_prompt_mutation": False,
            "active_devhub_release_state_mutation": False,
            "active_devhub_browser_artifact_mutation": False,
            "active_devhub_session_artifact_mutation": False,
        },
        "artifact_manifest": [],
    }


def validate_inactive_patch_preview_v1(packet: Mapping[str, Any]) -> list[PreviewViolation]:
    """Return all validation failures for an inactive DevHub patch preview packet."""

    violations: list[PreviewViolation] = []
    _require_equal(violations, packet, "preview_version", EXPECTED_PREVIEW_VERSION)
    _require_equal(violations, packet, "mode", EXPECTED_MODE)
    _require_equal(violations, packet, "surface_state", EXPECTED_SURFACE_STATE)
    _require_equal(violations, packet, "fixture_scope", EXPECTED_FIXTURE_SCOPE)
    _require_equal(violations, packet, "disposition_packet_version", QUEUE_VERSION)
    _require_equal(violations, packet, "devhub_execution", "none")
    _require_equal(violations, packet, "promotion_claim", "none")
    evidence_ids = _validate_observation_evidence(violations, packet.get("observation_evidence"))
    consumed_ids = _validate_consumed_rows(violations, packet.get("disposition_rows_consumed"), evidence_ids)
    _validate_before_after_previews(violations, packet.get("inactive_fixture_previews"), evidence_ids, consumed_ids)
    _validate_placeholder_rows(violations, packet.get("selector_confidence_placeholders"), "selector_confidence_placeholders", ("placeholder_id", "surface_id", "selector", "confidence_note"))
    _validate_placeholder_rows(violations, packet.get("accessible_role_name_evidence_placeholders"), "accessible_role_name_evidence_placeholders", ("placeholder_id", "surface_id", "role", "name", "evidence_placeholder"))
    _validate_placeholder_rows(violations, packet.get("redacted_field_inventory_placeholders"), "redacted_field_inventory_placeholders", ("placeholder_id", "surface_id", "field_ref", "redaction_policy", "status"))
    _validate_action_classification_references(violations, packet.get("action_classification_references"), consumed_ids)
    _validate_reviewer_signoff_placeholders(violations, packet.get("reviewer_signoff_placeholders"))
    _validate_nonempty_sequence_field(violations, packet, "rollback_notes", "missing_rollback_notes")
    _validate_validation_commands(violations, packet.get("validation_commands"))
    _validate_validation_inventory(violations, packet.get("validation_inventory"))
    _validate_mutation_flags(violations, packet.get("mutation_flags"))
    _validate_artifacts(violations, packet.get("artifact_manifest"))
    _validate_text_claims(violations, packet)
    return violations


def assert_valid_inactive_patch_preview_v1(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the inactive patch preview packet is invalid."""

    violations = validate_inactive_patch_preview_v1(packet)
    if violations:
        detail = "; ".join(f"{violation.code}: {violation.message}" for violation in violations)
        raise ValueError(detail)


def _evidence_from_row(row: Mapping[str, Any]) -> dict[str, str]:
    row_id = str(row.get("row_id"))
    return {
        "evidence_id": f"obs-evidence-{row_id}",
        "source_disposition_row_id": row_id,
        "citation": _first_citation(row.get("citations")) or "approved reviewer disposition row",
        "observed_at": "2026-05-30T00:00:00Z",
        "summary": str(row.get("rationale") or "Approved read-only observation row."),
    }


def _first_citation(value: Any) -> str:
    if isinstance(value, str):
        return value
    if _is_non_string_sequence(value):
        for item in value:
            if isinstance(item, str) and item:
                return item
            if isinstance(item, Mapping):
                for key in ("url", "canonical_url", "source_id", "source_evidence_id"):
                    if isinstance(item.get(key), str) and item.get(key):
                        return str(item[key])
    return ""


def _require_equal(violations: list[PreviewViolation], packet: Mapping[str, Any], field_name: str, expected: str) -> None:
    if packet.get(field_name) != expected:
        violations.append(PreviewViolation(code=f"invalid_{field_name}", message=f"{field_name} must be {expected!r} for inactive preview v1"))


def _validate_consumed_rows(violations: list[PreviewViolation], rows: Any, evidence_ids: set[str]) -> set[str]:
    if not _is_non_string_sequence(rows) or not rows:
        violations.append(PreviewViolation("missing_approved_disposition_rows_consumed", "disposition_rows_consumed must include approved row references"))
        return set()
    consumed_ids: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            violations.append(PreviewViolation("invalid_disposition_row_consumed", f"consumed row {index} must be an object"))
            continue
        row_id = row.get("row_id")
        evidence_id = row.get("evidence_id")
        if not row_id or row.get("reviewer_decision") != "approve_read_only" or row.get("source_queue_version") != QUEUE_VERSION:
            violations.append(PreviewViolation("missing_approved_disposition_rows_consumed", f"consumed row {index} must cite an approved queue v1 row"))
        if evidence_id not in evidence_ids:
            violations.append(PreviewViolation("uncited_observation_evidence", f"consumed row {index} must reference declared evidence"))
        if isinstance(row_id, str):
            consumed_ids.add(row_id)
    return consumed_ids


def _validate_before_after_previews(violations: list[PreviewViolation], previews: Any, evidence_ids: set[str], consumed_ids: set[str]) -> None:
    if not _is_non_string_sequence(previews) or not previews:
        violations.append(PreviewViolation("missing_inactive_surface_map_delta_previews", "inactive_fixture_previews must include before/after surface-map deltas"))
        return
    for index, preview in enumerate(previews):
        if not isinstance(preview, Mapping):
            violations.append(PreviewViolation("invalid_inactive_surface_map_delta_preview", f"preview {index} must be an object"))
            continue
        if not preview.get("preview_id") or preview.get("delta_type") != "inactive_surface_map_delta" or not preview.get("before") or not preview.get("after"):
            violations.append(PreviewViolation("missing_inactive_surface_map_delta_previews", f"preview {index} must include preview_id, delta_type, before, and after"))
        if preview.get("source_disposition_row_id") not in consumed_ids:
            violations.append(PreviewViolation("missing_approved_disposition_rows_consumed", f"preview {index} must cite a consumed row"))
        cited_ids = _string_list(preview.get("observation_evidence_ids"))
        if not cited_ids or any(evidence_id not in evidence_ids for evidence_id in cited_ids):
            violations.append(PreviewViolation("uncited_observation_evidence", f"preview {index} must cite committed observation evidence ids"))


def _validate_observation_evidence(violations: list[PreviewViolation], evidence: Any) -> set[str]:
    if not _is_non_string_sequence(evidence) or not evidence:
        violations.append(PreviewViolation("uncited_observation_evidence", "observation_evidence must include cited offline evidence records"))
        return set()
    evidence_ids: set[str] = set()
    for index, item in enumerate(evidence):
        if not isinstance(item, Mapping):
            violations.append(PreviewViolation("invalid_observation_evidence", f"evidence {index} must be an object"))
            continue
        missing = [name for name in ("evidence_id", "citation", "observed_at", "summary") if not item.get(name)]
        if missing:
            violations.append(PreviewViolation("uncited_observation_evidence", f"evidence {index} missing required fields: {', '.join(missing)}"))
            continue
        evidence_ids.add(str(item["evidence_id"]))
    return evidence_ids


def _validate_placeholder_rows(violations: list[PreviewViolation], rows: Any, field_name: str, required: tuple[str, ...]) -> None:
    if not _is_non_string_sequence(rows) or not rows:
        violations.append(PreviewViolation(f"missing_{field_name}", f"{field_name} must be populated"))
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            violations.append(PreviewViolation(f"missing_{field_name}", f"{field_name}[{index}] must be an object"))
            continue
        missing = [name for name in required if not row.get(name)]
        if missing:
            violations.append(PreviewViolation(f"missing_{field_name}", f"{field_name}[{index}] missing fields: {', '.join(missing)}"))


def _validate_action_classification_references(violations: list[PreviewViolation], refs: Any, consumed_ids: set[str]) -> None:
    if not _is_non_string_sequence(refs) or not refs:
        violations.append(PreviewViolation("missing_action_classification_references", "action_classification_references must be populated"))
        return
    for index, ref in enumerate(refs):
        if not isinstance(ref, Mapping):
            violations.append(PreviewViolation("missing_action_classification_references", f"classification ref {index} must be an object"))
            continue
        if not ref.get("classification_ref") or ref.get("classification") != "safe_read_only" or not ref.get("surface_id"):
            violations.append(PreviewViolation("missing_action_classification_references", f"classification ref {index} must identify a safe_read_only surface reference"))
        if ref.get("source_disposition_row_id") not in consumed_ids:
            violations.append(PreviewViolation("missing_approved_disposition_rows_consumed", f"classification ref {index} must cite a consumed row"))


def _validate_reviewer_signoff_placeholders(violations: list[PreviewViolation], placeholders: Any) -> None:
    if not _is_non_string_sequence(placeholders) or not placeholders:
        violations.append(PreviewViolation("missing_reviewer_signoff_placeholders", "reviewer_signoff_placeholders must reserve reviewer and status fields"))
        return
    for index, placeholder in enumerate(placeholders):
        if not isinstance(placeholder, Mapping) or not placeholder.get("role") or placeholder.get("status") != "pending" or not placeholder.get("notes_placeholder"):
            violations.append(PreviewViolation("missing_reviewer_signoff_placeholders", f"placeholder {index} must include role, pending status, and notes_placeholder"))


def _validate_nonempty_sequence_field(violations: list[PreviewViolation], packet: Mapping[str, Any], field_name: str, code: str) -> None:
    value = packet.get(field_name)
    if not _is_non_string_sequence(value) or not value:
        violations.append(PreviewViolation(code, f"{field_name} must be populated"))


def _validate_validation_commands(violations: list[PreviewViolation], commands: Any) -> None:
    if not _is_non_string_sequence(commands) or not commands:
        violations.append(PreviewViolation("missing_validation_commands", "validation_commands must be populated"))
        return
    for index, command in enumerate(commands):
        if not _is_non_string_sequence(command) or not all(isinstance(part, str) and part for part in command):
            violations.append(PreviewViolation("missing_validation_commands", f"validation command {index} must be a list of strings"))


def _validate_validation_inventory(violations: list[PreviewViolation], inventory: Any) -> None:
    if not _is_non_string_sequence(inventory) or not inventory:
        violations.append(PreviewViolation("missing_validation_inventory", "validation_inventory must be populated"))
        return
    observed = {item.get("check") for item in inventory if isinstance(item, Mapping)}
    missing = sorted(REQUIRED_VALIDATION_CHECKS - observed)
    if missing:
        violations.append(PreviewViolation("missing_validation_inventory", "validation_inventory missing checks: " + ", ".join(missing)))


def _validate_mutation_flags(violations: list[PreviewViolation], mutation_flags: Any) -> None:
    if not isinstance(mutation_flags, Mapping):
        violations.append(PreviewViolation("mutation_flag_outside_inactive_fixture_scope", "mutation_flags must be present"))
        return
    for flag_name, enabled in mutation_flags.items():
        if enabled is True and flag_name not in ALLOWED_TRUE_MUTATION_FLAGS:
            violations.append(PreviewViolation("mutation_flag_outside_inactive_fixture_scope", f"{flag_name} is outside inactive DevHub surface fixture preview scope"))
    if mutation_flags.get(EXPECTED_FIXTURE_SCOPE) is not True:
        violations.append(PreviewViolation("mutation_flag_outside_inactive_fixture_scope", f"{EXPECTED_FIXTURE_SCOPE} must be true"))


def _validate_artifacts(violations: list[PreviewViolation], artifact_manifest: Any) -> None:
    if artifact_manifest in (None, []):
        return
    if not _is_non_string_sequence(artifact_manifest):
        violations.append(PreviewViolation("private_or_raw_artifact", "artifact_manifest must be a list when present"))
        return
    for index, artifact in enumerate(artifact_manifest):
        text = _flatten_text(artifact).lower()
        if any(token in text for token in PRIVATE_ARTIFACT_TOKENS):
            violations.append(PreviewViolation("private_authenticated_session_or_browser_artifact", f"artifact {index} references private, authenticated, session, or browser data"))
        if any(token in text for token in RAW_ARTIFACT_TOKENS):
            violations.append(PreviewViolation("raw_crawl_pdf_or_downloaded_data_artifact", f"artifact {index} references raw data"))


def _validate_text_claims(violations: list[PreviewViolation], packet: Mapping[str, Any]) -> None:
    text = _flatten_text(packet).lower()
    for token in LIVE_EXECUTION_TOKENS:
        if token in text:
            violations.append(PreviewViolation("live_execution_or_applied_promotion_claim", f"forbidden claim: {token}"))
    for token in OUTCOME_GUARANTEE_TOKENS:
        if token in text:
            violations.append(PreviewViolation("legal_or_permitting_outcome_guarantee", f"forbidden guarantee: {token}"))
    for token in CONSEQUENTIAL_ACTION_TOKENS:
        if token in text:
            violations.append(PreviewViolation("consequential_devhub_action_language", f"forbidden action language: {token}"))


def _is_non_string_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _string_list(value: Any) -> list[str]:
    if not _is_non_string_sequence(value):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _flatten_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(str(key) + " " + _flatten_text(item) for key, item in value.items())
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)
