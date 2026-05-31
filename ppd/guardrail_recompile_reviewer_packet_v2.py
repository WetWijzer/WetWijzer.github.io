"""Fixture-first reviewer packet for guardrail recompile dry-run plan v2.

The packet is an offline review artifact only. It consumes the synthetic dry-run
plan and command validation results, then emits reviewer rows without writing
active guardrail bundles, prompts, source registries, process models, DevHub
surfaces, contracts, or release state.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ppd.guardrail_recompile_dry_run_plan_v2 import PLAN_VERSION as DRY_RUN_PLAN_VERSION
from ppd.guardrail_recompile_dry_run_plan_v2_validation import validate_guardrail_recompile_dry_run_plan_v2

PACKET_VERSION = "guardrail-recompile-reviewer-packet-v2"

OFFLINE_VALIDATION_COMMANDS = [
    [
        "python3",
        "-m",
        "py_compile",
        "ppd/guardrail_recompile_reviewer_packet_v2.py",
        "ppd/tests/test_guardrail_recompile_reviewer_packet_v2.py",
    ],
    ["python3", "-m", "pytest", "ppd/tests/test_guardrail_recompile_reviewer_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_BLOCKED_ACTION_REMINDERS = (
    "do_not_automate_captcha_mfa_account_creation_or_password_recovery",
    "do_not_enter_or_submit_payment_details",
    "do_not_upload_submit_certify_schedule_cancel_or_withdraw",
    "require_attended_action_specific_confirmation_for_consequential_steps",
)

_REVIEWER_ROW_KEYS = (
    "review_row_id",
    "row_order",
    "reviewer_disposition",
    "source_delta_row_id",
    "requirement_id",
    "guardrail_bundle_id",
    "requirement_delta_trace_placeholders",
    "predicate_impact_review_notes",
    "migration_risk_disposition_placeholders",
    "stale_source_hold_carry_forward_decision",
    "blocked_action_reminder_checks",
    "validation_result_status",
)


def build_guardrail_recompile_reviewer_packet_v2(
    dry_run_plan: Mapping[str, Any], validation_results: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Build an ordered reviewer packet from a dry-run plan and validation results."""

    plan_issues = validate_guardrail_recompile_dry_run_plan_v2(dry_run_plan)
    validation_summary = _validation_summary(dry_run_plan, validation_results)
    global_reject_reasons = [issue.code for issue in plan_issues] + validation_summary["failure_codes"]

    rows = []
    for index, delta_row in enumerate(_delta_rows(dry_run_plan), start=1):
        row = _review_row(index, delta_row, global_reject_reasons)
        missing = [key for key in _REVIEWER_ROW_KEYS if key not in row]
        if missing:
            raise AssertionError(f"internal reviewer row missing keys: {missing}")
        rows.append(row)

    return {
        "packet_version": PACKET_VERSION,
        "source_plan_version": dry_run_plan.get("plan_version", DRY_RUN_PLAN_VERSION),
        "source_plan_id": dry_run_plan.get("source_packet_id", "unknown_guardrail_recompile_plan"),
        "mode": "fixture_first_offline_review_packet",
        "review_scope": "inactive_guardrail_recompile_dry_run_review_only",
        "rows_are_ordered_by": "dry_run_plan_row_order",
        "ordered_reviewer_accept_hold_reject_rows": rows,
        "requirement_delta_trace_placeholder_summary": _trace_summary(rows),
        "predicate_impact_review_note_summary": _predicate_summary(rows),
        "migration_risk_disposition_placeholder_summary": _migration_summary(rows),
        "stale_source_hold_carry_forward_summary": _stale_hold_summary(rows),
        "blocked_action_reminder_check_summary": _blocked_action_summary(rows),
        "validation_result_summary": validation_summary,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "no_state_change_attestation": {
            "active_guardrail_bundles": "unchanged",
            "prompts": "unchanged",
            "source_registries": "unchanged",
            "process_models": "unchanged",
            "devhub_surfaces": "unchanged",
            "contracts": "unchanged",
            "release_state": "unchanged",
        },
    }


def _delta_rows(plan: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = plan.get("ordered_synthetic_guardrail_bundle_delta_rows", [])
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
        return []
    mappings = [row for row in rows if isinstance(row, Mapping)]
    return sorted(mappings, key=lambda row: int(row.get("row_order", 0) or 0))


def _review_row(index: int, delta_row: Mapping[str, Any], global_reject_reasons: Sequence[str]) -> dict[str, Any]:
    disposition, disposition_reason = _disposition(delta_row, global_reject_reasons)
    stale_decision = _stale_source_decision(delta_row, disposition)
    validation_status = "failed" if global_reject_reasons else "passed"
    requirement_id = _text(delta_row.get("requirement_id"), f"unknown_requirement_{index}")
    guardrail_bundle_id = _text(delta_row.get("guardrail_bundle_id"), "unknown_guardrail_bundle")

    return {
        "review_row_id": f"guardrail-review-v2::{index:04d}::{requirement_id}",
        "row_order": index,
        "reviewer_disposition": {
            "decision": disposition,
            "reason": disposition_reason,
            "allowed_decisions": ["accept", "hold", "reject"],
            "reviewer": "unassigned",
            "notes_placeholder": "pending_human_reviewer_notes",
        },
        "source_delta_row_id": _text(delta_row.get("delta_row_id"), f"missing_delta_row_id_{index}"),
        "requirement_id": requirement_id,
        "guardrail_bundle_id": guardrail_bundle_id,
        "requirement_delta_trace_placeholders": _trace_placeholders(delta_row),
        "predicate_impact_review_notes": _predicate_notes(delta_row),
        "migration_risk_disposition_placeholders": _migration_placeholders(delta_row),
        "stale_source_hold_carry_forward_decision": stale_decision,
        "blocked_action_reminder_checks": _blocked_action_checks(delta_row),
        "validation_result_status": {
            "status": validation_status,
            "failure_codes": list(global_reject_reasons),
            "review_effect": "reject_until_validation_passes" if global_reject_reasons else "available_for_reviewer_disposition",
        },
    }


def _disposition(delta_row: Mapping[str, Any], global_reject_reasons: Sequence[str]) -> tuple[str, str]:
    if global_reject_reasons:
        return "reject", "dry-run plan or offline validation results are not clean"
    if _requires_hold(delta_row):
        return "hold", "predicate impact or consequential-action guardrail requires reviewer confirmation"
    return "accept", "synthetic reversible-action row is ready for reviewer acceptance"


def _requires_hold(delta_row: Mapping[str, Any]) -> bool:
    delta_kind = _text(delta_row.get("bundle_delta_kind"), "")
    requirement_type = _text(delta_row.get("requirement_type"), "")
    if delta_kind in {"synthetic_update_candidate", "synthetic_removal_candidate"}:
        return True
    if requirement_type in {"action_gate", "prohibition", "deadline", "fee_trigger"}:
        return True
    return False


def _trace_placeholders(delta_row: Mapping[str, Any]) -> list[dict[str, Any]]:
    requirement_id = _text(delta_row.get("requirement_id"), "unknown_requirement")
    source_evidence_ids = _text_list(delta_row.get("source_evidence_ids"))
    return [
        {
            "trace_id": f"requirement-delta-trace::{requirement_id}",
            "requirement_id": requirement_id,
            "source_evidence_ids": source_evidence_ids,
            "process_id": _text(delta_row.get("process_id"), "pending_process_trace"),
            "guardrail_bundle_id": _text(delta_row.get("guardrail_bundle_id"), "pending_guardrail_trace"),
            "trace_status": "placeholder_pending_reviewer_confirmation",
        }
    ]


def _predicate_notes(delta_row: Mapping[str, Any]) -> list[dict[str, str]]:
    requirement_id = _text(delta_row.get("requirement_id"), "unknown_requirement")
    notes = []
    for field in (
        "deterministic_predicate_impact_placeholders",
        "deontic_rule_placeholders",
        "temporal_rule_placeholders",
        "reversible_action_predicate_placeholders",
        "exact_confirmation_predicate_placeholders",
        "refused_action_predicate_placeholders",
    ):
        placeholders = delta_row.get(field, [])
        count = len(placeholders) if isinstance(placeholders, Sequence) and not isinstance(placeholders, (str, bytes, bytearray)) else 0
        notes.append(
            {
                "note_id": f"predicate-impact-review::{requirement_id}::{field}",
                "placeholder_field": field,
                "placeholder_count": str(count),
                "review_note": "confirm predicate impact against requirement delta trace before promotion",
            }
        )
    return notes


def _migration_placeholders(delta_row: Mapping[str, Any]) -> list[dict[str, str]]:
    requirement_id = _text(delta_row.get("requirement_id"), "unknown_requirement")
    risk_notes = _text_list(delta_row.get("migration_risk_notes"))
    if not risk_notes:
        risk_notes = ["migration risk note missing; hold for reviewer completion"]
    return [
        {
            "migration_risk_id": f"migration-risk-disposition::{requirement_id}::{index:02d}",
            "risk_note": note,
            "disposition_placeholder": "pending_accept_hold_or_reject_decision",
            "release_effect": "no_release_effect_in_reviewer_packet",
        }
        for index, note in enumerate(risk_notes, start=1)
    ]


def _stale_source_decision(delta_row: Mapping[str, Any], disposition: str) -> dict[str, str]:
    delta_kind = _text(delta_row.get("bundle_delta_kind"), "")
    if disposition == "reject":
        decision = "carry_forward_hold_until_validation_passes"
    elif delta_kind in {"synthetic_update_candidate", "synthetic_removal_candidate"}:
        decision = "carry_forward_hold_for_stale_source_reviewer_confirmation"
    else:
        decision = "no_stale_source_hold_required_by_this_row"
    return {
        "decision": decision,
        "source_status": "stale_source_review_not_recompiled",
        "review_note": "do not clear stale-source holds until cited requirement evidence and predicate impact are reviewed",
    }


def _blocked_action_checks(delta_row: Mapping[str, Any]) -> list[dict[str, str]]:
    requirement_id = _text(delta_row.get("requirement_id"), "unknown_requirement")
    return [
        {
            "check_id": f"blocked-action-reminder::{requirement_id}::{index:02d}",
            "reminder": reminder,
            "status": "reminder_present",
        }
        for index, reminder in enumerate(_BLOCKED_ACTION_REMINDERS, start=1)
    ]


def _validation_summary(plan: Mapping[str, Any], validation_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    expected_commands = plan.get("offline_validation_commands", [])
    expected = {_command_key(command) for command in expected_commands if _is_command(command)}
    observed = {_command_key(result.get("command")) for result in validation_results if _is_command(result.get("command"))}
    failure_codes: list[str] = []
    result_rows = []

    missing = sorted(expected - observed)
    unexpected = sorted(observed - expected)
    if missing:
        failure_codes.append("missing_validation_result")
    if unexpected:
        failure_codes.append("unexpected_validation_result")

    for index, result in enumerate(validation_results, start=1):
        command = result.get("command")
        returncode = result.get("returncode")
        status = "passed" if returncode == 0 else "failed"
        if status == "failed":
            failure_codes.append("validation_command_failed")
        result_rows.append(
            {
                "result_order": index,
                "command": list(command) if _is_command(command) else [],
                "returncode": returncode,
                "status": status,
            }
        )

    return {
        "status": "passed" if not failure_codes else "failed",
        "failure_codes": sorted(set(failure_codes)),
        "expected_command_count": len(expected),
        "observed_command_count": len(observed),
        "missing_commands": [key.split("\u001f") for key in missing],
        "unexpected_commands": [key.split("\u001f") for key in unexpected],
        "validation_result_rows": result_rows,
    }


def _trace_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {"row_count": len(rows), "placeholder_count": sum(len(row["requirement_delta_trace_placeholders"]) for row in rows)}


def _predicate_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {"row_count": len(rows), "review_note_count": sum(len(row["predicate_impact_review_notes"]) for row in rows)}


def _migration_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {"row_count": len(rows), "placeholder_count": sum(len(row["migration_risk_disposition_placeholders"]) for row in rows)}


def _stale_hold_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    hold_count = sum(1 for row in rows if row["stale_source_hold_carry_forward_decision"]["decision"] != "no_stale_source_hold_required_by_this_row")
    return {"row_count": len(rows), "carry_forward_hold_count": hold_count}


def _blocked_action_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {"row_count": len(rows), "reminder_check_count": sum(len(row["blocked_action_reminder_checks"]) for row in rows)}


def _is_command(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and all(isinstance(part, str) for part in value)


def _command_key(command: Any) -> str:
    if not _is_command(command):
        return ""
    return "\u001f".join(command)


def _text(value: Any, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, Sequence):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


__all__ = [
    "OFFLINE_VALIDATION_COMMANDS",
    "PACKET_VERSION",
    "build_guardrail_recompile_reviewer_packet_v2",
]
