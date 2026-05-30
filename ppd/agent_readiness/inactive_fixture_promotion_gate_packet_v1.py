"""Fixture-first inactive fixture promotion gate packet v1.

This packet consumes only offline fixture inputs. It produces deterministic
review rows and validates that the packet remains an inactive, metadata-only
promotion gate. It must not promote fixtures, crawl sources, open DevHub,
change prompts, mutate active artifacts, or imply official permitting outcomes.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping, Sequence


PACKET_TYPE = "ppd.inactive_fixture_promotion_gate_packet.v1"
VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

MUTATION_FLAGS = (
    "active_artifact_mutation",
    "active_fixture_promotion",
    "active_fixture_mutation",
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_agent_state_mutation",
    "active_release_state_mutation",
    "release_state_mutation",
    "fixture_mutation",
    "prompt_mutation",
    "agent_state_mutation",
    "official_action_performed",
)

PRIVATE_OR_RAW_KEY_TOKENS = (
    "auth",
    "browser",
    "cookie",
    "credential",
    "devhub_session",
    "download",
    "har",
    "local_private_path",
    "password",
    "payment_detail",
    "private_value",
    "raw_body",
    "raw_crawl",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "session",
    "storage_state",
    "trace",
    "warc_payload",
)

LIVE_OR_PROMOTION_CLAIM_TOKENS = (
    "fixture_promoted",
    "live_crawl_completed",
    "live_execution_completed",
    "promoted_to_active",
    "promotion_complete",
    "promotion_completed",
    "release_state_updated",
)

PROHIBITED_TEXT_PHRASES = (
    "approval is guaranteed",
    "guaranteed approval",
    "guarantees approval",
    "guarantee approval",
    "permit will be approved",
    "permit outcome is guaranteed",
    "permitting outcome is guaranteed",
    "promotion complete",
    "promotion completed",
    "live execution completed",
    "submit the application",
    "submit permit",
    "certify acknowledgement",
    "schedule inspection",
    "pay fees",
    "final payment",
    "upload correction",
    "purchase permit",
    "cancel permit",
    "withdraw permit",
)

REQUIRED_ROW_FIELDS = (
    "row_id",
    "source_input",
    "decision",
    "reason",
    "source_evidence_ids",
    "reviewer_disposition",
    "rollback_readiness",
    "validation_replay_commands",
)

REQUIRED_REVIEWER_FIELDS = {"status", "reviewer", "reviewed_at", "notes"}
EVIDENCE_PREFIXES = ("source:", "observation:", "citation:", "official-source:", "fixture-source:", "observed:")


class InactiveFixturePromotionGatePacketV1Error(ValueError):
    """Raised when a gate packet is incomplete or unsafe."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid inactive fixture promotion gate packet v1: " + "; ".join(self.errors))


def build_inactive_fixture_promotion_gate_packet_v1(
    *,
    inactive_fixture_promotion_application_preview_v1: Mapping[str, Any],
    post_promotion_regression_rehearsal_v1: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic offline gate packet from two fixture inputs."""

    input_errors: list[str] = []
    _validate_no_private_raw_live_or_unsafe_payload(
        inactive_fixture_promotion_application_preview_v1,
        input_errors,
        root="inactive_fixture_promotion_application_preview_v1",
    )
    _validate_no_private_raw_live_or_unsafe_payload(
        post_promotion_regression_rehearsal_v1,
        input_errors,
        root="post_promotion_regression_rehearsal_v1",
    )
    if input_errors:
        raise InactiveFixturePromotionGatePacketV1Error(input_errors)

    application_preview = deepcopy(dict(inactive_fixture_promotion_application_preview_v1))
    regression_rehearsal = deepcopy(dict(post_promotion_regression_rehearsal_v1))
    application_evidence = _normalize_evidence_ids(_evidence_ids(application_preview), "application-preview")
    regression_evidence = _normalize_evidence_ids(_evidence_ids(regression_rehearsal), "regression-rehearsal")

    rows = [
        _gate_row(
            row_id="application-preview-coverage",
            source_input="inactive_fixture_promotion_application_preview_v1",
            decision=_decision_for_required_evidence(application_evidence),
            reason="Application preview must cite inactive fixture evidence for every proposed promotion row.",
            evidence_ids=application_evidence,
            rollback_id="rollback-application-preview",
        ),
        _gate_row(
            row_id="post-promotion-regression-rehearsal",
            source_input="post_promotion_regression_rehearsal_v1",
            decision=_decision_for_regression(regression_rehearsal, regression_evidence),
            reason="Regression rehearsal must be present, offline, and evidence-backed before any later promotion request.",
            evidence_ids=regression_evidence,
            rollback_id="rollback-regression-rehearsal",
        ),
        _gate_row(
            row_id="combined-manual-disposition",
            source_input="inactive_fixture_promotion_gate_packet_v1",
            decision="no_go",
            reason="Promotion remains blocked until a reviewer records a separate manual approval outside this packet.",
            evidence_ids=_dedupe([*application_evidence, *regression_evidence, "observation:gate-packet-v1-manual-disposition"]),
            rollback_id="rollback-combined-gate-packet",
        ),
    ]

    packet: dict[str, Any] = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v1",
        "mode": "offline_fixture_gate_only",
        "fixture_first": True,
        "metadata_only": True,
        "consumed_input_packet_refs": {
            "inactive_fixture_promotion_application_preview_v1": _packet_ref(application_preview, "inactive_fixture_promotion_application_preview_v1"),
            "post_promotion_regression_rehearsal_v1": _packet_ref(regression_rehearsal, "post_promotion_regression_rehearsal_v1"),
        },
        "attestations": {
            "no_fixture_changes_applied": True,
            "no_active_artifact_mutation": True,
            "no_prompt_changes": True,
            "no_live_source_crawl": True,
            "no_devhub_access": True,
            "no_official_actions": True,
        },
        "go_no_go_rows": rows,
        "source_evidence_coverage": _source_evidence_coverage(rows),
        "reviewer_disposition_fields": _reviewer_disposition_fields(rows),
        "rollback_readiness": _rollback_readiness(rows),
        "validation_replay_commands": VALIDATION_COMMANDS,
    }
    for flag in MUTATION_FLAGS:
        packet[flag] = False

    errors = validate_inactive_fixture_promotion_gate_packet_v1(packet)
    if errors:
        raise InactiveFixturePromotionGatePacketV1Error(errors)
    return packet


def validate_inactive_fixture_promotion_gate_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for a gate packet."""

    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be ppd.inactive_fixture_promotion_gate_packet.v1")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        errors.append("metadata_only must be true")
    if packet.get("validation_replay_commands") != VALIDATION_COMMANDS:
        errors.append("validation_replay_commands must contain the PP&D daemon self-test command")
    for flag in MUTATION_FLAGS:
        if packet.get(flag) is not False:
            errors.append(f"{flag} must be false")
    _validate_go_no_go_rows(packet.get("go_no_go_rows"), errors)
    _validate_evidence_coverage(packet.get("source_evidence_coverage"), errors)
    _validate_reviewer_fields(packet.get("reviewer_disposition_fields"), errors)
    _validate_rollback(packet.get("rollback_readiness"), errors)
    _validate_no_private_raw_live_or_unsafe_payload(packet, errors, root="packet")
    return errors


def _gate_row(
    *,
    row_id: str,
    source_input: str,
    decision: str,
    reason: str,
    evidence_ids: Sequence[str],
    rollback_id: str,
) -> dict[str, Any]:
    normalized_evidence = _dedupe(evidence_ids)
    if not normalized_evidence:
        normalized_evidence = [f"observation:{row_id}:missing-evidence"]
    return {
        "row_id": row_id,
        "source_input": source_input,
        "decision": decision,
        "reason": reason,
        "source_evidence_ids": normalized_evidence,
        "reviewer_disposition": {
            "status": "pending_manual_review",
            "reviewer": "",
            "reviewed_at": "",
            "notes": "",
        },
        "rollback_readiness": {
            "rollback_id": rollback_id,
            "status": "ready_no_active_changes",
            "checkpoint": "discard this gate packet and leave active PP&D fixtures and artifacts unchanged",
        },
        "validation_replay_commands": VALIDATION_COMMANDS,
    }


def _source_evidence_coverage(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    coverage: list[dict[str, Any]] = []
    for row in rows:
        evidence = _string_items(row.get("source_evidence_ids"))
        coverage.append(
            {
                "coverage_id": f"coverage-{_text(row.get('row_id'), 'row')}",
                "row_id": _text(row.get("row_id"), "row"),
                "source_input": _text(row.get("source_input"), "unknown"),
                "source_evidence_ids": evidence,
                "coverage_status": "covered" if evidence and all(_is_cited_evidence(item) for item in evidence) else "needs_review",
            }
        )
    return coverage


def _reviewer_disposition_fields(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "disposition_id": f"disposition-{_text(row.get('row_id'), 'row')}",
            "row_id": _text(row.get("row_id"), "row"),
            "required_fields": ["status", "reviewer", "reviewed_at", "notes"],
            "allowed_statuses": ["pending_manual_review", "approved_for_separate_future_promotion", "blocked", "needs_changes"],
            "current_status": "pending_manual_review",
        }
        for row in rows
    ]


def _rollback_readiness(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in rows:
        rollback = row.get("rollback_readiness")
        if isinstance(rollback, Mapping):
            result.append(
                {
                    "rollback_id": _text(rollback.get("rollback_id"), f"rollback-{_text(row.get('row_id'), 'row')}"),
                    "row_id": _text(row.get("row_id"), "row"),
                    "status": _text(rollback.get("status"), "ready_no_active_changes"),
                    "checkpoint": _text(rollback.get("checkpoint"), "leave active PP&D artifacts unchanged"),
                    "validation_replay_commands": VALIDATION_COMMANDS,
                }
            )
    return result


def _validate_go_no_go_rows(rows: Any, errors: list[str]) -> None:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append("go_no_go_rows must be a non-empty list")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"go_no_go_rows[{index}] must be an object")
            continue
        for field in REQUIRED_ROW_FIELDS:
            if field not in row:
                errors.append(f"go_no_go_rows[{index}].{field} is required")
        if row.get("decision") not in {"go", "no_go"}:
            errors.append(f"go_no_go_rows[{index}].decision must be go or no_go")
        evidence_ids = _string_items(row.get("source_evidence_ids"))
        if not evidence_ids:
            errors.append(f"go_no_go_rows[{index}].source_evidence_ids must be non-empty")
        if any(not _is_cited_evidence(item) for item in evidence_ids):
            errors.append(f"go_no_go_rows[{index}].source_evidence_ids must cite source or observation evidence")
        reviewer = row.get("reviewer_disposition")
        if not isinstance(reviewer, Mapping):
            errors.append(f"go_no_go_rows[{index}].reviewer_disposition must be an object")
        else:
            missing = REQUIRED_REVIEWER_FIELDS.difference(str(key) for key in reviewer.keys())
            if missing:
                errors.append(f"go_no_go_rows[{index}].reviewer_disposition is missing required fields")
            if reviewer.get("status") != "pending_manual_review":
                errors.append(f"go_no_go_rows[{index}].reviewer_disposition must be pending manual review")
        rollback = row.get("rollback_readiness")
        if not isinstance(rollback, Mapping):
            errors.append(f"go_no_go_rows[{index}].rollback_readiness must be an object")
        elif rollback.get("status") != "ready_no_active_changes":
            errors.append(f"go_no_go_rows[{index}].rollback_readiness must be ready_no_active_changes")
        if row.get("validation_replay_commands") != VALIDATION_COMMANDS:
            errors.append(f"go_no_go_rows[{index}].validation_replay_commands must replay self-test")


def _validate_evidence_coverage(rows: Any, errors: list[str]) -> None:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append("source_evidence_coverage must be a non-empty list")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"source_evidence_coverage[{index}] must be an object")
            continue
        evidence_ids = _string_items(row.get("source_evidence_ids"))
        if not evidence_ids:
            errors.append(f"source_evidence_coverage[{index}] must cite source_evidence_ids")
        if any(not _is_cited_evidence(item) for item in evidence_ids):
            errors.append(f"source_evidence_coverage[{index}] must cite source or observation evidence")


def _validate_reviewer_fields(rows: Any, errors: list[str]) -> None:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append("reviewer_disposition_fields must be a non-empty list")
        return
    for index, row in enumerate(rows):
        required = row.get("required_fields") if isinstance(row, Mapping) else None
        if set(_string_items(required)) != REQUIRED_REVIEWER_FIELDS:
            errors.append(f"reviewer_disposition_fields[{index}] must require status, reviewer, reviewed_at, and notes")


def _validate_rollback(rows: Any, errors: list[str]) -> None:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append("rollback_readiness must be a non-empty list")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"rollback_readiness[{index}] must be an object")
            continue
        if row.get("status") != "ready_no_active_changes":
            errors.append(f"rollback_readiness[{index}].status must be ready_no_active_changes")
        if not _text(row.get("checkpoint")):
            errors.append(f"rollback_readiness[{index}].checkpoint is required")
        if row.get("validation_replay_commands") != VALIDATION_COMMANDS:
            errors.append(f"rollback_readiness[{index}].validation_replay_commands must replay self-test")


def _validate_no_private_raw_live_or_unsafe_payload(value: Mapping[str, Any], errors: list[str], *, root: str) -> None:
    for path, key, child_value in _walk(value, path=root):
        key_name = key.lower()
        if any(token in key_name for token in PRIVATE_OR_RAW_KEY_TOKENS) and _truthy(child_value):
            errors.append(f"{path} must not include private, authenticated, session, browser, raw, PDF, crawl, or downloaded artifacts")
        if any(token in key_name for token in LIVE_OR_PROMOTION_CLAIM_TOKENS) and _truthy(child_value):
            errors.append(f"{path} must not claim live execution, promotion completion, or release-state update")
        if isinstance(child_value, str):
            lowered = child_value.lower()
            if any(phrase in lowered for phrase in PROHIBITED_TEXT_PHRASES):
                errors.append(f"{path} must not include live execution, promotion-complete, outcome guarantee, or consequential action language")


def _walk(value: Any, path: str = "packet", key: str = "") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{path}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _evidence_ids(packet: Mapping[str, Any]) -> list[str]:
    found: list[str] = []
    for key in ("source_evidence_ids", "evidence_ids", "citations", "offline_citations", "observation_evidence_ids"):
        found.extend(_string_items(packet.get(key)))
    for row_key in ("rows", "preview_rows", "regression_rows", "go_no_go_rows", "checks"):
        for row in _sequence(packet.get(row_key)):
            if isinstance(row, Mapping):
                found.extend(_evidence_ids(row))
    return _dedupe(found)


def _normalize_evidence_ids(values: Sequence[str], fallback_namespace: str) -> list[str]:
    normalized: list[str] = []
    for value in values:
        text = value.strip()
        if not text:
            continue
        if _is_cited_evidence(text):
            normalized.append(text)
        else:
            normalized.append(f"source:{fallback_namespace}:{text}")
    return _dedupe(normalized)


def _is_cited_evidence(value: str) -> bool:
    text = value.strip().lower()
    return bool(text) and not text.endswith(":missing-evidence") and text.startswith(EVIDENCE_PREFIXES)


def _decision_for_required_evidence(evidence_ids: Sequence[str]) -> str:
    return "go" if evidence_ids else "no_go"


def _decision_for_regression(packet: Mapping[str, Any], evidence_ids: Sequence[str]) -> str:
    if not evidence_ids:
        return "no_go"
    status_values = [_text(packet.get("status")), _text(packet.get("overall_status")), _text(packet.get("result"))]
    if any(value in {"fail", "failed", "blocked", "needs_changes"} for value in status_values):
        return "no_go"
    rows = [row for row in _sequence(packet.get("regression_rows")) if isinstance(row, Mapping)]
    if any(_text(row.get("status")) in {"fail", "failed", "blocked", "needs_changes"} for row in rows):
        return "no_go"
    return "go"


def _packet_ref(packet: Mapping[str, Any], fallback: str) -> str:
    for key in ("packet_type", "preview_version", "schema_version", "packet_version"):
        value = packet.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return ()


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _dedupe(values: Sequence[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    if isinstance(value, Mapping) and not value:
        return False
    return True


def _text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip().lower()
    return fallback
