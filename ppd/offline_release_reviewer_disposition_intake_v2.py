"""Offline release reviewer disposition intake packet v2.

This module is fixture-first and side-effect free. It transforms an offline
release rehearsal gate v2 document into ordered reviewer decision rows for
human review intake.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

SCHEMA_VERSION = "ppd.offline_release_reviewer_disposition_intake.v2"
SOURCE_SCHEMA_VERSION = "ppd.offline_release_rehearsal_gate.v2"


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _ack(source: dict[str, Any], key: str) -> dict[str, Any]:
    payload = source.get(key)
    if not isinstance(payload, dict):
        payload = {}
    return {
        "acknowledgement_required": True,
        "acknowledged": False,
        "summary": _text(payload.get("summary")),
        "evidence_ids": [_text(item) for item in _as_list(payload.get("evidence_ids"))],
    }


def _blocker_rows(gate: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, blocker in enumerate(_as_list(gate.get("unresolved_blockers")), start=1):
        if not isinstance(blocker, dict):
            continue
        rows.append(
            {
                "carry_forward_order": index,
                "blocker_id": _text(blocker.get("id")),
                "severity": _text(blocker.get("severity")),
                "owner": _text(blocker.get("owner")),
                "description": _text(blocker.get("description")),
                "required_resolution": _text(blocker.get("required_resolution")),
                "carried_forward": True,
            }
        )
    return rows


def _decision_rows(gate: dict[str, Any], blockers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reviewer_gates = [item for item in _as_list(gate.get("reviewer_gates")) if isinstance(item, dict)]
    reviewer_gates.sort(key=lambda item: (int(item.get("order", 0)), _text(item.get("reviewer")), _text(item.get("gate_id"))))

    rows: list[dict[str, Any]] = []
    blocker_ids = [item["blocker_id"] for item in blockers if item.get("blocker_id")]
    for index, item in enumerate(reviewer_gates, start=1):
        source_decision = _text(item.get("recommended_disposition") or item.get("status") or "review_required")
        rows.append(
            {
                "decision_row_order": index,
                "reviewer": _text(item.get("reviewer")),
                "review_area": _text(item.get("review_area")),
                "source_gate_id": _text(item.get("gate_id")),
                "source_gate_order": int(item.get("order", index)),
                "recommended_disposition": source_decision,
                "reviewer_decision_placeholder": "pending_reviewer_decision",
                "no_go_reason_placeholder": "",
                "unresolved_blocker_ids": blocker_ids,
                "evidence_summary_acknowledgement": _ack(item, "evidence_summary"),
                "rollback_readiness_acknowledgement": _ack(item, "rollback_readiness"),
                "validation_replay_acknowledgement": _ack(item, "validation_replay"),
            }
        )
    return rows


def build_disposition_intake_packet(gate: dict[str, Any]) -> dict[str, Any]:
    """Build an offline reviewer disposition intake packet from gate v2 data."""
    if not isinstance(gate, dict):
        raise TypeError("gate must be a dictionary")

    blockers = _blocker_rows(gate)
    rows = _decision_rows(gate, blockers)
    return {
        "schema_version": SCHEMA_VERSION,
        "source_schema_version": _text(gate.get("schema_version") or SOURCE_SCHEMA_VERSION),
        "source_gate_packet_id": _text(gate.get("gate_packet_id")),
        "offline_only": True,
        "official_action": False,
        "fixture_changes_applied": False,
        "active_artifacts_mutated": False,
        "release_state_updated": False,
        "live_sources_crawled": False,
        "devhub_accessed": False,
        "reviewer_decision_rows": rows,
        "unresolved_blockers_carried_forward": blockers,
        "source_gate_snapshot": deepcopy(gate),
    }


__all__ = ["SCHEMA_VERSION", "SOURCE_SCHEMA_VERSION", "build_disposition_intake_packet"]
