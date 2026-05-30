"""Fixture-first public source change reviewer disposition queue v1.

This module is intentionally side-effect free. It consumes already-normalized public
source change triage packets and returns reviewer disposition data. It does not
crawl, download, persist raw bodies, mutate registries, or claim official action.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
from typing import Any

QUEUE_VERSION = "public_source_change_reviewer_disposition_queue_v1"
SUPPORTED_PACKET_VERSION = "public_source_change_triage_packet_v1"

_ALLOWED_STATUSES = {"changed", "unchanged", "needs_review", "needs-review"}
_BUCKET_ORDER = {"changed": 0, "needs_review": 1, "unchanged": 2}
_FORBIDDEN_RAW_FIELDS = {
    "raw_body",
    "raw_html",
    "html",
    "body",
    "document_bytes",
    "downloaded_document",
    "screenshot",
    "trace",
    "har",
}
_MUTATION_FLAGS = {
    "mutates_source_registry",
    "mutates_documents",
    "mutates_requirements",
    "mutates_process_models",
    "mutates_guardrails",
    "changes_release_state",
    "claims_official_action",
    "requires_live_crawl",
}


def load_triage_packet(path: str | Path) -> dict[str, Any]:
    """Load a triage packet fixture from disk."""
    with Path(path).open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError("triage packet must be a JSON object")
    return packet


def build_reviewer_disposition_queue(packet: dict[str, Any]) -> dict[str, Any]:
    """Build ordered reviewer decision rows from a public change triage packet."""
    _validate_packet_shape(packet)

    rows = []
    for index, change in enumerate(packet.get("changes", [])):
        if not isinstance(change, dict):
            raise ValueError(f"change at index {index} must be an object")
        rows.append(_build_row(packet, change, index))

    rows.sort(key=lambda row: (row["sort_key"][0], row["sort_key"][1], row["change_id"]))
    for position, row in enumerate(rows, start=1):
        row["review_order"] = position
        del row["sort_key"]

    return {
        "queue_version": QUEUE_VERSION,
        "input_packet_version": packet["packet_version"],
        "packet_id": packet["packet_id"],
        "source": "fixture_only",
        "no_live_crawling": True,
        "no_raw_body_persistence": True,
        "official_action_claim": False,
        "decision_rows": rows,
        "buckets": _bucket_rows(rows),
        "blocked_promotion_reasons": _queue_blockers(packet, rows),
        "rollback_checkpoints": _rollback_checkpoints(packet, rows),
        "validation_commands": offline_validation_commands(),
    }


def offline_validation_commands() -> list[list[str]]:
    return [
        ["python3", "-m", "py_compile", "ppd/extraction/public_source_change_reviewer.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_public_source_change_reviewer.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def _validate_packet_shape(packet: dict[str, Any]) -> None:
    if packet.get("packet_version") != SUPPORTED_PACKET_VERSION:
        raise ValueError(f"packet_version must be {SUPPORTED_PACKET_VERSION}")
    if not packet.get("packet_id"):
        raise ValueError("packet_id is required")
    changes = packet.get("changes")
    if not isinstance(changes, list):
        raise ValueError("changes must be a list")


def _build_row(packet: dict[str, Any], change: dict[str, Any], index: int) -> dict[str, Any]:
    status = _normalize_status(str(change.get("triage_status", "needs_review")))
    priority = int(change.get("review_priority", index + 1))
    impact_references = _impact_references(change)
    blockers = _change_blockers(packet, change, impact_references)

    return {
        "review_order": 0,
        "change_id": str(change.get("change_id") or f"change-{index + 1}"),
        "source_id": str(change.get("source_id") or ""),
        "canonical_url": str(change.get("canonical_url") or ""),
        "bucket": status,
        "review_priority": priority,
        "reviewer_decision": _default_decision(status, blockers),
        "summary": str(change.get("summary") or ""),
        "changed_fields": list(change.get("changed_fields", [])),
        "unchanged_fields": list(change.get("unchanged_fields", [])),
        "cited_impact_references": impact_references,
        "blocked_promotion_reasons": blockers,
        "rollback_checkpoint": {
            "checkpoint_id": f"rollback:{packet['packet_id']}:{change.get('change_id') or index + 1}",
            "restore_target": "prior reviewer disposition output only",
            "release_state_change": False,
        },
        "sort_key": (_BUCKET_ORDER[status], priority),
    }


def _normalize_status(status: str) -> str:
    normalized = status.strip().lower().replace("-", "_")
    if normalized not in _ALLOWED_STATUSES:
        return "needs_review"
    return "needs_review" if normalized == "needs-review" else normalized


def _default_decision(status: str, blockers: list[str]) -> str:
    if blockers:
        return "blocked_needs_human_review"
    if status == "changed":
        return "review_changed_source_impacts"
    if status == "unchanged":
        return "confirm_no_guardrail_or_process_update"
    return "needs_human_review"


def _impact_references(change: dict[str, Any]) -> list[dict[str, Any]]:
    references = change.get("impact_references", [])
    if not isinstance(references, list):
        return []

    normalized = []
    for ref in references:
        if not isinstance(ref, dict):
            continue
        normalized.append(
            {
                "reference_id": str(ref.get("reference_id") or ""),
                "reference_type": str(ref.get("reference_type") or "unspecified"),
                "target_id": str(ref.get("target_id") or ""),
                "citation": deepcopy(ref.get("citation", {})),
                "impact": str(ref.get("impact") or "review required"),
            }
        )
    return normalized


def _change_blockers(
    packet: dict[str, Any], change: dict[str, Any], impact_references: list[dict[str, Any]]
) -> list[str]:
    blockers = []
    forbidden_fields = sorted(_present_forbidden_fields(change))
    if forbidden_fields:
        blockers.append("raw_or_downloaded_content_present:" + ",".join(forbidden_fields))
    if _truthy_mutation_flags(change):
        blockers.append("prohibited_mutation_or_official_action_flag_present")
    if _truthy_mutation_flags(packet):
        blockers.append("packet_requests_prohibited_mutation_or_live_crawl")
    if _normalize_status(str(change.get("triage_status", "needs_review"))) == "changed" and not impact_references:
        blockers.append("changed_source_without_cited_impact_reference")
    if not change.get("canonical_url"):
        blockers.append("missing_canonical_url")
    if not change.get("source_id"):
        blockers.append("missing_source_id")
    return blockers


def _present_forbidden_fields(value: Any, prefix: str = "") -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{prefix}.{key}" if prefix else str(key)
            if key in _FORBIDDEN_RAW_FIELDS and child not in (None, "", [], {}):
                found.add(child_path)
            found.update(_present_forbidden_fields(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.update(_present_forbidden_fields(child, f"{prefix}[{index}]"))
    return found


def _truthy_mutation_flags(value: dict[str, Any]) -> bool:
    return any(bool(value.get(flag)) for flag in _MUTATION_FLAGS)


def _bucket_rows(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    buckets = {"changed": [], "unchanged": [], "needs_review": []}
    for row in rows:
        buckets[row["bucket"]].append(row["change_id"])
    return buckets


def _queue_blockers(packet: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    blockers = []
    if _present_forbidden_fields(packet):
        blockers.append("packet_contains_raw_or_downloaded_content")
    if _truthy_mutation_flags(packet):
        blockers.append("packet_requests_prohibited_mutation_or_live_crawl")
    for row in rows:
        for reason in row["blocked_promotion_reasons"]:
            blockers.append(f"{row['change_id']}:{reason}")
    return blockers


def _rollback_checkpoints(packet: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checkpoints = [
        {
            "checkpoint_id": f"rollback:{packet['packet_id']}:queue",
            "restore_target": "discard generated reviewer queue artifact",
            "release_state_change": False,
        }
    ]
    checkpoints.extend(row["rollback_checkpoint"] for row in rows)
    return checkpoints
