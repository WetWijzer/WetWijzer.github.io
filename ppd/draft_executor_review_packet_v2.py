from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PACKET_TYPE = "reversible_draft_executor_review_packet_v2"
PACKET_VERSION = 2
SOURCE_CONTRACT_VERSION = "draft_executor_dry_run_v2"
MODE = "fixture_first_offline_review_only"

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/draft_executor_review_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_draft_executor_review_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_REQUIRED_ROW_FIELDS = (
    "synthetic_row_id",
    "request_kind",
    "preview_only",
    "source_action_id",
    "field_mapping",
    "user_fact_trace",
    "source_evidence_trace",
    "selector_confidence",
    "stop_gate",
    "refusal",
    "response",
)

_FORBIDDEN_RESPONSE_FLAGS = (
    "submitted",
    "paid",
    "scheduled",
    "cancelled",
    "account_changed",
    "release_state_activated",
)


class DraftExecutorReviewPacketError(ValueError):
    """Raised when a dry-run executor contract cannot support review packet v2."""


def load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise DraftExecutorReviewPacketError(str(path) + " must contain a JSON object")
    return loaded


def build_from_fixture_path(draft_executor_dry_run_contract_path: Path) -> dict[str, Any]:
    return build_draft_executor_review_packet_v2(load_json(draft_executor_dry_run_contract_path))


def build_draft_executor_review_packet_v2(draft_executor_dry_run_contract_v2: Mapping[str, Any]) -> dict[str, Any]:
    """Build ordered reviewer rows from a fixture-only executor dry-run contract.

    The review packet is metadata-only. It does not import Playwright, open
    DevHub, fill forms, save official drafts, upload files, submit, certify,
    pay, schedule, cancel, change accounts, or activate release state.
    """

    rows = _validated_source_rows(draft_executor_dry_run_contract_v2)
    source_row_ids = [_required_text(row, "synthetic_row_id") for row in rows]

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "mode": MODE,
        "fixture_first": True,
        "consumes": {
            "contract_version": SOURCE_CONTRACT_VERSION,
            "source_row_ids": source_row_ids,
        },
        "reviewer_rows": [
            _dry_run_request_acceptance_row(rows),
            _preview_only_response_review_row(rows),
            _user_fact_trace_review_row(rows),
            _source_evidence_trace_review_row(rows),
            _selector_confidence_hold_reason_row(rows),
            _exact_confirmation_stop_gate_review_row(rows),
            _refused_consequential_action_review_row(rows),
        ],
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "side_effects": {
            "playwright_actions_executed": False,
            "devhub_opened": False,
            "live_forms_filled": False,
            "official_drafts_saved": False,
            "files_uploaded": False,
            "submitted": False,
            "certified": False,
            "paid": False,
            "scheduled": False,
            "cancelled": False,
            "accounts_changed": False,
            "release_state_activated": False,
        },
        "validation_status": "fixture_review_packet_ready_for_reviewer_assignment",
    }
    _validate_packet(packet)
    return packet


def _dry_run_request_acceptance_row(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "review_order": 1,
        "review_area": "dry_run_request_acceptance",
        "status": "pending_reviewer_acceptance",
        "source_row_ids": [_required_text(row, "synthetic_row_id") for row in rows],
        "dry_run_request_acceptance": {
            "accepted_request_kind": "synthetic_executor_preview_request",
            "all_requests_preview_only": all(row.get("preview_only") is True for row in rows),
            "accepted_source_action_ids": [_required_text(row, "source_action_id") for row in rows],
        },
        "reviewer_instruction": "Confirm each request is synthetic, fixture-backed, and preview-only before any executor adapter work is considered.",
    }


def _preview_only_response_review_row(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    response_refs: list[dict[str, Any]] = []
    for row in rows:
        response = _mapping(row.get("response"), "response")
        response_refs.append(
            {
                "source_row_id": _required_text(row, "synthetic_row_id"),
                "response_kind": response.get("response_kind"),
                "executed_playwright_actions": response.get("executed_playwright_actions"),
                "saved_official_drafts": response.get("saved_official_drafts"),
                "uploaded_files": response.get("uploaded_files"),
                "forbidden_flags_clear": all(response.get(flag) is False for flag in _FORBIDDEN_RESPONSE_FLAGS),
            }
        )
    return {
        "review_order": 2,
        "review_area": "preview_only_response_review",
        "status": "pending_reviewer_acceptance",
        "source_row_ids": [item["source_row_id"] for item in response_refs],
        "preview_only_response_review": response_refs,
        "reviewer_instruction": "Confirm responses show no Playwright actions, official draft saves, uploads, submission, payment, scheduling, cancellation, account changes, or release activation.",
    }


def _user_fact_trace_review_row(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    traces = [
        {
            "source_row_id": _required_text(row, "synthetic_row_id"),
            "trace_count": len(_list(row.get("user_fact_trace"), "user_fact_trace")),
            "trace": row.get("user_fact_trace"),
        }
        for row in rows
    ]
    return {
        "review_order": 3,
        "review_area": "user_fact_trace_review",
        "status": "pending_reviewer_acceptance",
        "source_row_ids": [item["source_row_id"] for item in traces],
        "user_fact_trace_review": traces,
        "reviewer_instruction": "Confirm every accepted preview value has a redacted fixture user-fact trace and no private session or browser artifact values.",
    }


def _source_evidence_trace_review_row(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    traces = [
        {
            "source_row_id": _required_text(row, "synthetic_row_id"),
            "trace_count": len(_list(row.get("source_evidence_trace"), "source_evidence_trace")),
            "trace": row.get("source_evidence_trace"),
        }
        for row in rows
    ]
    return {
        "review_order": 4,
        "review_area": "source_evidence_trace_review",
        "status": "pending_reviewer_acceptance",
        "source_row_ids": [item["source_row_id"] for item in traces],
        "source_evidence_trace_review": traces,
        "reviewer_instruction": "Confirm each preview mapping is traceable to committed fixture evidence before any live-source renewal is discussed.",
    }


def _selector_confidence_hold_reason_row(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    holds = []
    for row in rows:
        selector_confidence = _mapping(row.get("selector_confidence"), "selector_confidence")
        holds.append(
            {
                "source_row_id": _required_text(row, "synthetic_row_id"),
                "hold_required": selector_confidence.get("placeholder") is True,
                "confidence_value": selector_confidence.get("value"),
                "hold_reason": selector_confidence.get("reason"),
            }
        )
    return {
        "review_order": 5,
        "review_area": "selector_confidence_hold_reasons",
        "status": "pending_reviewer_acceptance",
        "source_row_ids": [item["source_row_id"] for item in holds],
        "selector_confidence_hold_reasons": holds,
        "reviewer_instruction": "Keep rows on hold while selector confidence is fixture placeholder-only; do not infer live DOM readiness from this packet.",
    }


def _exact_confirmation_stop_gate_review_row(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    gates = []
    for row in rows:
        stop_gate = _mapping(row.get("stop_gate"), "stop_gate")
        gates.append(
            {
                "source_row_id": _required_text(row, "synthetic_row_id"),
                "requires_exact_confirmation": stop_gate.get("requires_exact_confirmation") is True,
                "confirmation_phrase": stop_gate.get("confirmation_phrase"),
            }
        )
    return {
        "review_order": 6,
        "review_area": "exact_confirmation_stop_gate_review",
        "status": "pending_reviewer_acceptance",
        "source_row_ids": [item["source_row_id"] for item in gates],
        "exact_confirmation_stop_gate_review": gates,
        "reviewer_instruction": "Confirm the stop gate is exact, preview-only, and does not authorize official PP&D actions.",
    }


def _refused_consequential_action_review_row(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    refusals = []
    for row in rows:
        refusal = row.get("refusal")
        if isinstance(refusal, Mapping) and refusal.get("refused") is True:
            refusals.append(
                {
                    "source_row_id": _required_text(row, "synthetic_row_id"),
                    "reason": refusal.get("reason"),
                    "example": refusal.get("example"),
                }
            )
    return {
        "review_order": 7,
        "review_area": "refused_consequential_action_review",
        "status": "pending_reviewer_acceptance",
        "source_row_ids": [item["source_row_id"] for item in refusals],
        "refused_consequential_action_review": refusals,
        "reviewer_instruction": "Confirm consequential examples remain refused and are not converted into executor permissions.",
    }


def _validated_source_rows(contract: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    if contract.get("contract_version") != SOURCE_CONTRACT_VERSION:
        raise DraftExecutorReviewPacketError("contract_version must be " + SOURCE_CONTRACT_VERSION)
    if contract.get("mode") != "fixture_first_offline_preview_only":
        raise DraftExecutorReviewPacketError("source contract must be fixture_first_offline_preview_only")
    rows = contract.get("rows")
    if not isinstance(rows, list) or not rows:
        raise DraftExecutorReviewPacketError("source contract rows must be a non-empty list")

    validated: list[Mapping[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise DraftExecutorReviewPacketError("source row " + str(index) + " must be an object")
        missing = [field for field in _REQUIRED_ROW_FIELDS if field not in row]
        if missing:
            raise DraftExecutorReviewPacketError("source row missing fields: " + ", ".join(missing))
        if row.get("preview_only") is not True:
            raise DraftExecutorReviewPacketError("source row must be preview_only")
        response = _mapping(row.get("response"), "response")
        if response.get("executed_playwright_actions") != []:
            raise DraftExecutorReviewPacketError("source row must not execute Playwright actions")
        if response.get("saved_official_drafts") != []:
            raise DraftExecutorReviewPacketError("source row must not save official drafts")
        if response.get("uploaded_files") != []:
            raise DraftExecutorReviewPacketError("source row must not upload files")
        for flag in _FORBIDDEN_RESPONSE_FLAGS:
            if response.get(flag) is not False:
                raise DraftExecutorReviewPacketError("source row response flag must be false: " + flag)
        validated.append(row)
    return validated


def _validate_packet(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != PACKET_TYPE:
        raise DraftExecutorReviewPacketError("unexpected packet_type")
    if packet.get("packet_version") != PACKET_VERSION:
        raise DraftExecutorReviewPacketError("unexpected packet_version")
    rows = packet.get("reviewer_rows")
    if not isinstance(rows, list) or len(rows) != 7:
        raise DraftExecutorReviewPacketError("reviewer_rows must contain seven ordered rows")
    expected_areas = [
        "dry_run_request_acceptance",
        "preview_only_response_review",
        "user_fact_trace_review",
        "source_evidence_trace_review",
        "selector_confidence_hold_reasons",
        "exact_confirmation_stop_gate_review",
        "refused_consequential_action_review",
    ]
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise DraftExecutorReviewPacketError("reviewer row must be an object")
        if row.get("review_order") != position:
            raise DraftExecutorReviewPacketError("reviewer rows must be ordered")
        if row.get("review_area") != expected_areas[position - 1]:
            raise DraftExecutorReviewPacketError("unexpected review area")
        if row.get("status") != "pending_reviewer_acceptance":
            raise DraftExecutorReviewPacketError("reviewer row status must be pending_reviewer_acceptance")
        if not _list(row.get("source_row_ids"), "source_row_ids"):
            raise DraftExecutorReviewPacketError("reviewer row source_row_ids must be non-empty")
    if packet.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        raise DraftExecutorReviewPacketError("offline_validation_commands changed")


def _required_text(source: Mapping[str, Any], key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DraftExecutorReviewPacketError("missing required text field: " + key)
    return value


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DraftExecutorReviewPacketError(label + " must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise DraftExecutorReviewPacketError(label + " must be a list")
    return value
