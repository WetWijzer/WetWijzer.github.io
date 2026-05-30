"""Fixture-first DevHub read-only observation reviewer disposition queue v1.

This module consumes the DevHub read-only observation evidence intake gate v1
and produces an offline-only reviewer queue. It records ordered reviewer decision
rows, safe read-only surface buckets, redaction confirmation placeholders,
blocked-action carry-forward notes, rollback checkpoints, and exact validation
commands. It does not create auth state, browser artifacts, uploads,
submissions, payments, certifications, cancellations, scheduling artifacts, or
active surface-map changes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
import re

from ppd.devhub.observation_evidence_intake_gate_v1 import (
    REQUIRED_REDACTION_ATTESTATIONS,
    accepted_observation_rows,
)

QUEUE_VERSION = "devhub_read_only_observation_reviewer_disposition_queue_v1"
DECISION_STATUS = "pending_reviewer_disposition"
REDACTION_STATUS = "pending_reviewer_confirmation"

OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/devhub/read_only_observation_reviewer_disposition_queue_v1.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_read_only_observation_reviewer_disposition_queue_v1.py"],
]

FORBIDDEN_KEYS = frozenset(
    {
        "auth_state",
        "browser_context",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "download_path",
        "har_path",
        "local_storage",
        "password",
        "payment_detail",
        "private_value",
        "raw_authenticated_value",
        "raw_dom",
        "raw_download",
        "session_file",
        "session_path",
        "storage_state",
        "trace_path",
        "upload_payload",
    }
)

ACTIVE_MUTATION_KEYS = frozenset(
    {
        "active_surface_map_change",
        "active_surface_map_changes",
        "active_surface_mutation",
        "active_devhub_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_fixture_mutation",
        "active_agent_state_mutation",
    }
)

PRIVATE_TEXT_RE = re.compile(
    r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|storage[_-]?state\.json|trace\.zip|\.(?:har|png|jpg|jpeg)\b|bearer\s+[A-Za-z0-9._-]+|password\s*[:=]|cookie\s*[:=])",
    re.IGNORECASE,
)

ONLINE_COMMAND_MARKERS = ("curl", "wget", "playwright", "devhub.portlandoregon.gov", "http://", "https://")
BLOCKED_ACTION_RE = re.compile(
    r"\b(upload|submit|submission|certify|certification|pay|payment|schedule|scheduling|cancel|cancellation|withdraw|purchase|account creation|password recovery|mfa|captcha)\b",
    re.IGNORECASE,
)
BLOCKING_RE = re.compile(r"\b(stop before|block|blocked|do not|must not|refuse|manual handoff|required confirmation)\b", re.IGNORECASE)


def build_reviewer_disposition_queue_v1(intake_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic reviewer disposition queue from an intake packet."""

    rows = sorted(accepted_observation_rows(intake_packet), key=lambda row: (str(row.get("surface_id", "")), str(row.get("row_id", ""))))
    decision_rows: list[dict[str, Any]] = []
    buckets: dict[str, list[str]] = {}
    rollback_checkpoints: list[dict[str, Any]] = []

    for index, row in enumerate(rows, start=1):
        bucket = _bucket_for_surface(str(row.get("surface_id", "")))
        decision_row_id = f"devhub-read-only-review-disposition-v1-{index:03d}"
        blocked_notes = [str(note).strip() for note in row.get("blocked_action_notes", []) if str(note).strip()]
        evidence_refs = _evidence_refs(row)
        checkpoint = {
            "checkpoint_id": f"rollback-{decision_row_id}",
            "decision_row_id": decision_row_id,
            "restart_from_fixture": True,
            "rollback_action": "Discard the reviewer row and rebuild from the committed intake fixture.",
            "active_surface_map_changes": False,
        }
        decision_rows.append(
            {
                "decision_row_id": decision_row_id,
                "decision_order": index,
                "source_intake_row_id": str(row.get("row_id", "")),
                "surface_id": str(row.get("surface_id", "")),
                "surface_label": str(row.get("surface_label", row.get("surface_id", ""))),
                "safe_read_only_surface_bucket": bucket,
                "decision_status": DECISION_STATUS,
                "reviewer_decision_placeholder": "Reviewer records accept, reject, or needs-follow-up after offline validation.",
                "evidence_refs": evidence_refs,
                "redaction_confirmation_placeholders": _redaction_placeholders(),
                "blocked_action_carry_forward_notes": blocked_notes,
                "rollback_checkpoint": checkpoint,
                "offline_validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
                "active_surface_map_changes": False,
            }
        )
        buckets.setdefault(bucket, []).append(decision_row_id)
        rollback_checkpoints.append(checkpoint)

    queue = {
        "version": QUEUE_VERSION,
        "packet_id": "devhub-read-only-observation-reviewer-disposition-queue-v1",
        "fixture_first": True,
        "read_only_only": True,
        "consumes_intake_gate_version": "devhub_read_only_observation_evidence_intake_gate_v1",
        "consumed_intake_gate_packet_id": str(intake_packet.get("packet_id", "")),
        "no_active_surface_map_changes": True,
        "reviewer_decision_rows": decision_rows,
        "safe_read_only_surface_buckets": buckets,
        "rollback_checkpoints": rollback_checkpoints,
        "validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
    }
    assert_valid_reviewer_disposition_queue_v1(queue)
    return queue


def validate_reviewer_disposition_queue_v1(queue: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a reviewer disposition queue."""

    errors: list[str] = []
    if queue.get("version") != QUEUE_VERSION:
        errors.append(f"version must be {QUEUE_VERSION}")
    if queue.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if queue.get("read_only_only") is not True:
        errors.append("read_only_only must be true")
    if queue.get("no_active_surface_map_changes") is not True:
        errors.append("no_active_surface_map_changes must be true")
    if not _non_empty_text(queue.get("consumed_intake_gate_packet_id")):
        errors.append("consumed_intake_gate_packet_id is required")

    rows = queue.get("reviewer_decision_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("reviewer_decision_rows must contain ordered reviewer decision rows")
        rows = []

    seen_ids: set[str] = set()
    row_ids: list[str] = []
    for expected_order, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            errors.append(f"reviewer_decision_rows[{expected_order - 1}] must be an object")
            continue
        row_id = str(row.get("decision_row_id", "")).strip()
        if not row_id:
            errors.append(f"reviewer_decision_rows[{expected_order - 1}].decision_row_id is required")
        elif row_id in seen_ids:
            errors.append(f"reviewer_decision_rows[{expected_order - 1}].decision_row_id must be unique")
        else:
            seen_ids.add(row_id)
            row_ids.append(row_id)
        _validate_row(row, expected_order, errors)

    _validate_buckets(queue.get("safe_read_only_surface_buckets"), row_ids, errors)
    _validate_rollback_checkpoints(queue.get("rollback_checkpoints"), row_ids, errors)
    if queue.get("validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        errors.append("validation_commands must match the exact offline reviewer disposition queue commands")

    _scan_forbidden(queue, "$", errors)
    return errors


def assert_valid_reviewer_disposition_queue_v1(queue: Mapping[str, Any]) -> None:
    errors = validate_reviewer_disposition_queue_v1(queue)
    if errors:
        raise ValueError("DevHub read-only observation reviewer disposition queue rejected: " + "; ".join(errors))


def _validate_row(row: Mapping[str, Any], expected_order: int, errors: list[str]) -> None:
    prefix = f"reviewer_decision_rows[{expected_order - 1}]"
    if row.get("decision_order") != expected_order:
        errors.append(f"{prefix}.decision_order must be sequential")
    for key in ("source_intake_row_id", "surface_id", "surface_label", "safe_read_only_surface_bucket"):
        if not _non_empty_text(row.get(key)):
            errors.append(f"{prefix}.{key} is required")
    if row.get("decision_status") != DECISION_STATUS:
        errors.append(f"{prefix}.decision_status must remain pending reviewer disposition")
    if row.get("active_surface_map_changes") is not False:
        errors.append(f"{prefix}.active_surface_map_changes must be false")
    if not _non_empty_text(row.get("reviewer_decision_placeholder")):
        errors.append(f"{prefix}.reviewer_decision_placeholder is required")
    if not _non_empty_text_list(row.get("evidence_refs")):
        errors.append(f"{prefix}.evidence_refs must cite intake or source evidence")
    _validate_redaction_placeholders(row.get("redaction_confirmation_placeholders"), prefix, errors)
    _validate_blocked_notes(row.get("blocked_action_carry_forward_notes"), prefix, errors)
    _validate_checkpoint(row.get("rollback_checkpoint"), str(row.get("decision_row_id", "")), f"{prefix}.rollback_checkpoint", errors)
    _validate_commands(row.get("offline_validation_commands"), f"{prefix}.offline_validation_commands", errors)


def _validate_redaction_placeholders(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, list) or len(value) != len(REQUIRED_REDACTION_ATTESTATIONS):
        errors.append(f"{prefix}.redaction_confirmation_placeholders must include all redaction attestations")
        return
    by_id = {item.get("attestation_id"): item for item in value if isinstance(item, Mapping)}
    for attestation in REQUIRED_REDACTION_ATTESTATIONS:
        item = by_id.get(attestation)
        if not isinstance(item, Mapping):
            errors.append(f"{prefix}.redaction_confirmation_placeholders missing {attestation}")
            continue
        if item.get("confirmation_status") != REDACTION_STATUS:
            errors.append(f"{prefix}.redaction_confirmation_placeholders.{attestation} must remain pending")
        if not _non_empty_text(item.get("reviewer_placeholder")):
            errors.append(f"{prefix}.redaction_confirmation_placeholders.{attestation} needs reviewer placeholder text")


def _validate_blocked_notes(value: Any, prefix: str, errors: list[str]) -> None:
    if not _non_empty_text_list(value):
        errors.append(f"{prefix}.blocked_action_carry_forward_notes must carry blocked-action notes forward")
        return
    joined = " ".join(str(item) for item in value)
    if not BLOCKED_ACTION_RE.search(joined) or not BLOCKING_RE.search(joined):
        errors.append(f"{prefix}.blocked_action_carry_forward_notes must frame consequential actions as blocked")


def _validate_buckets(value: Any, row_ids: list[str], errors: list[str]) -> None:
    if not isinstance(value, Mapping) or not value:
        errors.append("safe_read_only_surface_buckets must group every reviewer row")
        return
    bucketed: list[str] = []
    for bucket, ids in value.items():
        if not str(bucket).strip():
            errors.append("safe_read_only_surface_buckets names must be non-empty")
        if not isinstance(ids, list) or not ids:
            errors.append(f"safe_read_only_surface_buckets.{bucket} must contain row ids")
            continue
        bucketed.extend(str(item) for item in ids)
    if sorted(bucketed) != sorted(row_ids):
        errors.append("safe_read_only_surface_buckets must contain exactly the reviewer decision row ids")


def _validate_rollback_checkpoints(value: Any, row_ids: list[str], errors: list[str]) -> None:
    if not isinstance(value, list) or len(value) != len(row_ids):
        errors.append("rollback_checkpoints must include one checkpoint per reviewer row")
        return
    for index, checkpoint in enumerate(value):
        _validate_checkpoint(checkpoint, "", f"rollback_checkpoints[{index}]", errors)


def _validate_checkpoint(value: Any, expected_row_id: str, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{prefix} must be an object")
        return
    if not _non_empty_text(value.get("checkpoint_id")):
        errors.append(f"{prefix}.checkpoint_id is required")
    if expected_row_id and value.get("decision_row_id") != expected_row_id:
        errors.append(f"{prefix}.decision_row_id must match its reviewer row")
    if value.get("restart_from_fixture") is not True:
        errors.append(f"{prefix}.restart_from_fixture must be true")
    if value.get("active_surface_map_changes") is not False:
        errors.append(f"{prefix}.active_surface_map_changes must be false")
    if not _non_empty_text(value.get("rollback_action")):
        errors.append(f"{prefix}.rollback_action is required")


def _validate_commands(value: Any, prefix: str, errors: list[str]) -> None:
    if value != OFFLINE_VALIDATION_COMMANDS:
        errors.append(f"{prefix} must match the exact offline commands")
        return
    for command in value:
        joined = " ".join(command).lower()
        if any(marker in joined for marker in ONLINE_COMMAND_MARKERS):
            errors.append(f"{prefix} must not include online validation commands")


def _scan_forbidden(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized_key = str(key).lower().replace("-", "_")
            child_path = f"{path}.{key}"
            if normalized_key in FORBIDDEN_KEYS:
                errors.append(f"{child_path} must not include private DevHub artifacts or values")
            if normalized_key in ACTIVE_MUTATION_KEYS and child not in (False, None, "", [], {}):
                errors.append(f"{child_path} must not set active mutation or surface-map changes")
            _scan_forbidden(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]", errors)
    elif isinstance(value, str) and PRIVATE_TEXT_RE.search(value):
        errors.append(f"{path} must not include private DevHub artifact text")


def _redaction_placeholders() -> list[dict[str, str]]:
    return [
        {
            "attestation_id": attestation,
            "confirmation_status": REDACTION_STATUS,
            "reviewer_placeholder": "Reviewer confirms the attestation from committed metadata only.",
        }
        for attestation in REQUIRED_REDACTION_ATTESTATIONS
    ]


def _evidence_refs(row: Mapping[str, Any]) -> list[str]:
    refs = row.get("source_evidence_refs") or row.get("observation_evidence_refs") or []
    return [str(ref).strip() for ref in refs if str(ref).strip()]


def _bucket_for_surface(surface_id: str) -> str:
    lowered = surface_id.lower()
    if "home" in lowered:
        return "devhub_home"
    if "status" in lowered or "permit" in lowered:
        return "permit_status_review"
    if "fee" in lowered:
        return "fee_notice_review"
    if "correction" in lowered:
        return "correction_request_review"
    return "other_safe_read_only"


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_text_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_non_empty_text(item) for item in value)
