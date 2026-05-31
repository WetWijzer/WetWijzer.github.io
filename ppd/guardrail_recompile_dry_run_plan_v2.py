"""Fixture-first guardrail recompile dry-run plan v2.

This module intentionally builds synthetic review rows only. It does not read or
write active guardrail bundles, prompt files, source registries, process models,
DevHub surfaces, or release state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

PLAN_VERSION = "guardrail-recompile-dry-run-plan-v2"
EXPECTED_PACKET_VERSION = "requirement-reextraction-dry-run-packet-v2"

OFFLINE_VALIDATION_COMMANDS = [
    [
        "python3",
        "-m",
        "py_compile",
        "ppd/guardrail_recompile_dry_run_plan_v2.py",
        "ppd/tests/test_guardrail_recompile_dry_run_plan_v2.py",
    ],
    ["python3", "-m", "pytest", "ppd/tests/test_guardrail_recompile_dry_run_plan_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

PLACEHOLDER_STATUS = "placeholder_pending_human_review"

REQUIRED_ROW_KEYS = (
    "delta_row_id",
    "row_order",
    "source_packet_id",
    "requirement_id",
    "source_evidence_ids",
    "process_id",
    "guardrail_bundle_id",
    "bundle_delta_kind",
    "requirement_type",
    "synthetic_guardrail_bundle_delta",
    "deterministic_predicate_impact_placeholders",
    "deontic_rule_placeholders",
    "temporal_rule_placeholders",
    "reversible_action_predicate_placeholders",
    "exact_confirmation_predicate_placeholders",
    "refused_action_predicate_placeholders",
    "migration_risk_notes",
    "reviewer_disposition_placeholders",
)


@dataclass(frozen=True)
class RequirementDryRunRow:
    """Normalized source row consumed from a re-extraction dry-run packet."""

    requirement_id: str
    requirement_type: str
    action: str
    subject: str
    object_value: str
    process_id: str
    guardrail_bundle_id: str
    source_evidence_ids: tuple[str, ...]
    formalization_status: str
    human_review_status: str
    change_hint: str
    deadline_or_temporal_scope: str


def _as_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _as_text_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    if isinstance(value, Iterable):
        result = []
        for item in value:
            text = _as_text(item)
            if text:
                result.append(text)
        return tuple(result)
    return (_as_text(value),)


def _packet_rows(packet: dict[str, Any]) -> list[RequirementDryRunRow]:
    packet_version = _as_text(packet.get("packet_version"))
    if packet_version != EXPECTED_PACKET_VERSION:
        raise ValueError(
            f"expected packet_version {EXPECTED_PACKET_VERSION!r}, got {packet_version!r}"
        )

    raw_rows = packet.get("requirement_rows")
    if not isinstance(raw_rows, list):
        raise ValueError("requirement_rows must be a list")

    normalized = []
    for index, raw in enumerate(raw_rows):
        if not isinstance(raw, dict):
            raise ValueError(f"requirement_rows[{index}] must be an object")
        requirement_id = _as_text(raw.get("requirement_id"))
        if not requirement_id:
            raise ValueError(f"requirement_rows[{index}] is missing requirement_id")
        normalized.append(
            RequirementDryRunRow(
                requirement_id=requirement_id,
                requirement_type=_as_text(raw.get("requirement_type"), "unknown"),
                action=_as_text(raw.get("action"), "unspecified_action"),
                subject=_as_text(raw.get("subject"), "unspecified_subject"),
                object_value=_as_text(raw.get("object"), "unspecified_object"),
                process_id=_as_text(raw.get("process_id"), "synthetic_process_pending_mapping"),
                guardrail_bundle_id=_as_text(
                    raw.get("guardrail_bundle_id"),
                    "synthetic_guardrail_bundle_pending_mapping",
                ),
                source_evidence_ids=_as_text_tuple(raw.get("source_evidence_ids")),
                formalization_status=_as_text(
                    raw.get("formalization_status"),
                    "pending_dry_run_formalization",
                ),
                human_review_status=_as_text(
                    raw.get("human_review_status"),
                    "pending_review",
                ),
                change_hint=_as_text(raw.get("change_hint"), "synthetic_delta"),
                deadline_or_temporal_scope=_as_text(
                    raw.get("deadline_or_temporal_scope"),
                    "not_applicable_or_unextracted",
                ),
            )
        )
    return sorted(normalized, key=lambda row: (row.process_id, row.guardrail_bundle_id, row.requirement_id))


def _bundle_delta_kind(row: RequirementDryRunRow) -> str:
    if row.formalization_status in {"new", "unformalized", "pending_dry_run_formalization"}:
        return "synthetic_addition_candidate"
    if row.change_hint in {"changed", "modified", "stale_source_changed"}:
        return "synthetic_update_candidate"
    if row.change_hint in {"removed", "missing_from_reextract"}:
        return "synthetic_removal_candidate"
    return "synthetic_review_candidate"


def _deterministic_predicate_placeholders(row: RequirementDryRunRow) -> list[dict[str, str]]:
    return [
        {
            "predicate_id": f"predicate-impact::{row.requirement_id}::precondition",
            "status": PLACEHOLDER_STATUS,
            "expected_impact": "deterministic precondition impact requires compiler review",
        },
        {
            "predicate_id": f"predicate-impact::{row.requirement_id}::evidence",
            "status": PLACEHOLDER_STATUS,
            "expected_impact": "source evidence coverage requires traceability review",
        },
    ]


def _deontic_placeholders(row: RequirementDryRunRow) -> list[dict[str, str]]:
    return [
        {
            "rule_id": f"deontic::{row.requirement_id}::{row.requirement_type}",
            "status": PLACEHOLDER_STATUS,
            "modality": row.requirement_type,
            "subject": row.subject,
            "action": row.action,
            "object": row.object_value,
        }
    ]


def _temporal_placeholders(row: RequirementDryRunRow) -> list[dict[str, str]]:
    return [
        {
            "rule_id": f"temporal::{row.requirement_id}",
            "status": PLACEHOLDER_STATUS,
            "deadline_or_temporal_scope": row.deadline_or_temporal_scope,
        }
    ]


def _action_placeholders(prefix: str, row: RequirementDryRunRow, rationale: str) -> list[dict[str, str]]:
    return [
        {
            "predicate_id": f"{prefix}::{row.requirement_id}",
            "status": PLACEHOLDER_STATUS,
            "rationale": rationale,
        }
    ]


def compile_guardrail_recompile_dry_run_plan_v2(packet: dict[str, Any]) -> dict[str, Any]:
    """Compile a requirement re-extraction dry-run packet into review rows."""

    rows = _packet_rows(packet)
    source_packet_id = _as_text(packet.get("packet_id"), "unknown_requirement_reextract_packet")
    delta_rows = []
    for offset, row in enumerate(rows, start=1):
        delta = {
            "delta_row_id": f"guardrail-delta-v2::{offset:04d}::{row.requirement_id}",
            "row_order": offset,
            "source_packet_id": source_packet_id,
            "requirement_id": row.requirement_id,
            "source_evidence_ids": list(row.source_evidence_ids),
            "process_id": row.process_id,
            "guardrail_bundle_id": row.guardrail_bundle_id,
            "bundle_delta_kind": _bundle_delta_kind(row),
            "requirement_type": row.requirement_type,
            "synthetic_guardrail_bundle_delta": {
                "status": "synthetic_inactive_delta_only",
                "writes_active_bundle": "false",
                "compiler_target": row.guardrail_bundle_id,
            },
            "deterministic_predicate_impact_placeholders": _deterministic_predicate_placeholders(row),
            "deontic_rule_placeholders": _deontic_placeholders(row),
            "temporal_rule_placeholders": _temporal_placeholders(row),
            "reversible_action_predicate_placeholders": _action_placeholders(
                "reversible-action-predicate",
                row,
                "classify whether draft-only assistance remains reversible before any official action",
            ),
            "exact_confirmation_predicate_placeholders": _action_placeholders(
                "exact-confirmation-predicate",
                row,
                "require action-specific user confirmation before consequential workflow steps",
            ),
            "refused_action_predicate_placeholders": _action_placeholders(
                "refused-action-predicate",
                row,
                "block CAPTCHA, MFA, payment, upload, submission, certification, cancellation, and scheduling automation",
            ),
            "migration_risk_notes": [
                "inactive synthetic row only; do not migrate without reviewer approval",
                "compare predicate impact against cited source evidence before compiler promotion",
                "verify no prompt, source registry, process model, DevHub surface, or release state mutation is needed",
            ],
            "reviewer_disposition_placeholders": {
                "review_status": "pending",
                "reviewer": "unassigned",
                "decision": "undecided",
                "notes": "",
            },
        }
        missing_keys = [key for key in REQUIRED_ROW_KEYS if key not in delta]
        if missing_keys:
            raise AssertionError(f"internal row assembly missing keys: {missing_keys}")
        delta_rows.append(delta)

    return {
        "plan_version": PLAN_VERSION,
        "source_packet_id": source_packet_id,
        "input_packet_version": EXPECTED_PACKET_VERSION,
        "mode": "fixture_first_offline_dry_run",
        "active_bundle_mutation": "forbidden",
        "ordered_synthetic_guardrail_bundle_delta_rows": delta_rows,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }


__all__ = [
    "EXPECTED_PACKET_VERSION",
    "OFFLINE_VALIDATION_COMMANDS",
    "PLAN_VERSION",
    "REQUIRED_ROW_KEYS",
    "compile_guardrail_recompile_dry_run_plan_v2",
]
