"""Fixture-first reconciliation for PP&D source refresh results.

This module is intentionally offline-only. It consumes already-captured review and
intake packets and emits cited source-level reconciliation decisions without
crawling, processing, registry writes, or requirement/guardrail mutation.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

Decision = str


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _string_list(value: Any) -> list[str]:
    return sorted({str(item) for item in _as_list(value) if item is not None and str(item)})


def _source_key(record: dict[str, Any]) -> str:
    source_id = record.get("source_id") or record.get("id") or record.get("source")
    if not source_id:
        raise ValueError("source record is missing source_id")
    return str(source_id)


def _index_sources(packet: dict[str, Any], field: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in _as_list(packet.get(field)):
        if not isinstance(record, dict):
            raise ValueError(f"{field} entries must be objects")
        indexed[_source_key(record)] = record
    return indexed


def _citations(source_id: str, metadata: dict[str, Any]) -> list[dict[str, str]]:
    cited = []
    for citation in _as_list(metadata.get("citations")):
        if not isinstance(citation, dict):
            continue
        href = citation.get("href") or citation.get("url")
        label = citation.get("label") or citation.get("title") or source_id
        if href:
            cited.append({"label": str(label), "href": str(href)})
    if cited:
        return cited
    source_url = metadata.get("source_url") or metadata.get("url")
    if source_url:
        return [{"label": source_id, "href": str(source_url)}]
    return []


def _decision(freshness: dict[str, Any], metadata: dict[str, Any], extraction: dict[str, Any]) -> Decision:
    explicit = freshness.get("review_decision") or metadata.get("refresh_decision") or extraction.get("rerun_decision")
    if explicit in {"accepted", "deferred", "escalated"}:
        return str(explicit)

    extraction_status = str(extraction.get("status", "")).lower()
    freshness_status = str(freshness.get("status", "")).lower()
    metadata_status = str(metadata.get("status", "")).lower()

    if extraction_status in {"failed", "error", "blocked"}:
        return "escalated"
    if freshness_status in {"conflict", "requires_review"}:
        return "escalated"
    if metadata_status in {"missing", "unavailable"}:
        return "deferred"
    if freshness_status in {"stale", "deferred"}:
        return "deferred"
    return "accepted"


def reconcile_source_refresh_results(
    source_freshness_delta_review_packet: dict[str, Any],
    public_source_refresh_metadata_intake_packet: dict[str, Any],
    requirement_extraction_rerun_result_intake_packet: dict[str, Any],
    reviewer_owner: str,
) -> dict[str, Any]:
    """Return an offline reconciliation packet from three upstream packets."""
    if not reviewer_owner:
        raise ValueError("reviewer_owner is required")

    freshness_by_source = _index_sources(source_freshness_delta_review_packet, "source_deltas")
    metadata_by_source = _index_sources(public_source_refresh_metadata_intake_packet, "sources")
    extraction_by_source = _index_sources(requirement_extraction_rerun_result_intake_packet, "source_results")
    source_ids = sorted(set(freshness_by_source) | set(metadata_by_source) | set(extraction_by_source))

    decisions = []
    for source_id in source_ids:
        freshness = freshness_by_source.get(source_id, {})
        metadata = metadata_by_source.get(source_id, {})
        extraction = extraction_by_source.get(source_id, {})
        decision = _decision(freshness, metadata, extraction)
        affected_requirement_ids = _string_list(freshness.get("requirement_ids"))
        affected_requirement_ids.extend(_string_list(extraction.get("requirement_ids")))
        affected_process_ids = _string_list(freshness.get("process_ids"))
        affected_process_ids.extend(_string_list(extraction.get("process_ids")))
        affected_guardrail_ids = _string_list(freshness.get("guardrail_ids"))
        affected_guardrail_ids.extend(_string_list(extraction.get("guardrail_ids")))

        decisions.append(
            {
                "source_id": source_id,
                "decision": decision,
                "decision_basis": _string_list(
                    freshness.get("delta_reasons")
                    or metadata.get("refresh_notes")
                    or extraction.get("result_notes")
                    or ["fixture-first reconciliation"]
                ),
                "citations": _citations(source_id, metadata),
                "affected_requirement_ids": sorted(set(affected_requirement_ids)),
                "affected_process_ids": sorted(set(affected_process_ids)),
                "affected_guardrail_ids": sorted(set(affected_guardrail_ids)),
                "reviewer_owner": reviewer_owner,
            }
        )

    packet = {
        "packet_type": "source_refresh_result_reconciliation",
        "schema_version": 1,
        "inputs": {
            "source_freshness_delta_review_packet_id": source_freshness_delta_review_packet.get("packet_id"),
            "public_source_refresh_metadata_intake_packet_id": public_source_refresh_metadata_intake_packet.get("packet_id"),
            "requirement_extraction_rerun_result_intake_packet_id": requirement_extraction_rerun_result_intake_packet.get("packet_id"),
        },
        "source_decisions": decisions,
        "reviewer_owner": reviewer_owner,
        "offline_validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "attestations": {
            "no_live_crawl": True,
            "no_processor_execution": True,
            "no_registry_mutation": True,
            "no_requirement_mutation": True,
            "no_guardrail_mutation": True,
        },
    }
    return deepcopy(packet)
