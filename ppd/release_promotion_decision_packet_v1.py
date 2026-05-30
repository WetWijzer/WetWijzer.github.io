"""Fixture-first release promotion decision packet v1.

This module is intentionally offline-only. It transforms already-captured
fixture packets into a decision packet and does not promote fixtures, update
release state, contact DevHub, or read private artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


Decision = str


@dataclass(frozen=True)
class DecisionInput:
    """Normalized input for one cited decision row."""

    identifier: str
    subject: str
    gate_status: str
    reviewer_disposition: str
    citations: tuple[str, ...]
    rationale: str


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value)


def _first_present(mapping: Mapping[str, Any], names: tuple[str, ...], fallback: Any = None) -> Any:
    for name in names:
        if name in mapping:
            return mapping[name]
    return fallback


def _citations(*items: Mapping[str, Any]) -> tuple[str, ...]:
    found: list[str] = []
    for item in items:
        for key in ("citations", "evidence", "source_refs", "sourceRefs"):
            for value in _as_list(item.get(key)):
                text = _text(value).strip()
                if text and text not in found:
                    found.append(text)
        explicit = item.get("citation")
        if explicit:
            text = _text(explicit).strip()
            if text and text not in found:
                found.append(text)
    return tuple(found or ("fixture:uncited-input",))


def _gate_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = _first_present(packet, ("gate_rows", "gateRows", "checks", "rows"), [])
    return [row for row in _as_list(rows) if isinstance(row, Mapping)]


def _reviewer_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = _first_present(packet, ("reviewer_rows", "reviewerRows", "dispositions", "rows"), [])
    return [row for row in _as_list(rows) if isinstance(row, Mapping)]


def _index_by_identifier(rows: list[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for position, row in enumerate(rows, start=1):
        identifier = _text(
            _first_present(row, ("id", "identifier", "check_id", "row_id"), f"row-{position}")
        )
        indexed[identifier] = row
    return indexed


def _decision_for(gate_status: str, reviewer_disposition: str) -> Decision:
    gate = gate_status.lower().strip()
    reviewer = reviewer_disposition.lower().strip()
    blocking_gate = gate in {"block", "blocked", "fail", "failed", "error"}
    blocking_review = reviewer in {"block", "blocked", "reject", "rejected"}
    defer_gate = gate in {"defer", "deferred", "warn", "warning", "needs-review"}
    defer_review = reviewer in {"defer", "deferred", "needs-work", "needs_review"}
    promote_gate = gate in {"pass", "passed", "ok", "green"}
    promote_review = reviewer in {"approve", "approved", "accepted", "promote"}
    if blocking_gate or blocking_review:
        return "block"
    if defer_gate or defer_review:
        return "defer"
    if promote_gate and promote_review:
        return "promote"
    return "defer"


def _decision_inputs(
    rehearsal_gate_v2: Mapping[str, Any], reviewer_disposition_packet_v2: Mapping[str, Any]
) -> list[DecisionInput]:
    gate_rows = _index_by_identifier(_gate_rows(rehearsal_gate_v2))
    reviewer_rows = _index_by_identifier(_reviewer_rows(reviewer_disposition_packet_v2))
    identifiers = sorted(set(gate_rows) | set(reviewer_rows))
    normalized: list[DecisionInput] = []
    for identifier in identifiers:
        gate_row = gate_rows.get(identifier, {})
        reviewer_row = reviewer_rows.get(identifier, {})
        subject = _text(
            _first_present(gate_row, ("subject", "name", "title"), None)
            or _first_present(reviewer_row, ("subject", "name", "title"), identifier)
        )
        gate_status = _text(_first_present(gate_row, ("status", "gate_status", "result"), "missing"))
        reviewer_disposition = _text(
            _first_present(reviewer_row, ("disposition", "reviewer_disposition", "status"), "missing")
        )
        rationale_parts = []
        gate_reason = _text(_first_present(gate_row, ("rationale", "reason", "note"), "")).strip()
        reviewer_reason = _text(
            _first_present(reviewer_row, ("rationale", "reason", "note"), "")
        ).strip()
        if gate_reason:
            rationale_parts.append(f"gate: {gate_reason}")
        if reviewer_reason:
            rationale_parts.append(f"reviewer: {reviewer_reason}")
        normalized.append(
            DecisionInput(
                identifier=identifier,
                subject=subject,
                gate_status=gate_status,
                reviewer_disposition=reviewer_disposition,
                citations=_citations(gate_row, reviewer_row),
                rationale="; ".join(rationale_parts) or "Derived from fixture gate and reviewer packets.",
            )
        )
    return normalized


def build_release_promotion_decision_packet_v1(
    rehearsal_gate_v2: Mapping[str, Any], reviewer_disposition_packet_v2: Mapping[str, Any]
) -> dict[str, Any]:
    """Build an offline release promotion decision packet from fixture inputs."""

    rows = []
    decisions: list[str] = []
    for item in _decision_inputs(rehearsal_gate_v2, reviewer_disposition_packet_v2):
        decision = _decision_for(item.gate_status, item.reviewer_disposition)
        decisions.append(decision)
        rows.append(
            {
                "id": item.identifier,
                "subject": item.subject,
                "decision": decision,
                "gate_status": item.gate_status,
                "reviewer_disposition": item.reviewer_disposition,
                "citations": list(item.citations),
                "rationale": item.rationale,
            }
        )

    if "block" in decisions:
        overall = "block"
    elif "defer" in decisions or not decisions:
        overall = "defer"
    else:
        overall = "promote"

    return {
        "packet_type": "release_promotion_decision_packet",
        "version": 1,
        "input_packets": {
            "release_rehearsal_gate": "v2",
            "reviewer_disposition_packet": "v2",
        },
        "overall_decision": overall,
        "decision_rows": rows,
        "release_scope_boundaries": {
            "included": [
                "fixture-derived decision rows",
                "fixture-derived citations",
                "manual signoff placeholders",
                "validation replay commands",
                "rollback checkpoints",
            ],
            "excluded": [
                "live crawl promotion",
                "DevHub authenticated automation",
                "private artifact creation or upload",
                "official PP&D action",
                "active fixture, prompt, process model, guardrail, release state, or agent state promotion",
            ],
        },
        "manual_signoff_placeholders": [
            {"role": "release_reviewer", "status": "pending_manual_signoff", "signed_by": None},
            {"role": "release_supervisor", "status": "pending_manual_signoff", "signed_by": None},
        ],
        "validation_replay_commands": [
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]
        ],
        "rollback_checkpoints": [
            "retain prior fixture packet versions",
            "restore previous release decision packet artifact if validation fails",
            "do not mutate active release state during replay",
        ],
        "attestations": {
            "no_live_crawl": True,
            "no_devhub_session": True,
            "no_private_artifact": True,
            "no_official_action": True,
            "no_active_fixture_promotion": True,
            "no_prompt_promotion": True,
            "no_process_model_promotion": True,
            "no_guardrail_promotion": True,
            "no_release_state_promotion": True,
            "no_agent_state_promotion": True,
        },
    }
