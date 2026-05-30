"""Fixture-first inactive public source refresh patch previews.

This module intentionally works only from committed fixtures or caller-provided
Python dictionaries. It does not crawl, download, write active artifacts, or read
from the current public corpus.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


JsonMap = Dict[str, Any]


BLOCK_SOURCE_NOT_IN_PLAN = "source_not_in_public_source_refresh_plan_v2"
BLOCK_ACTIVE_SOURCE = "active_public_source_artifact_not_previewable"
BLOCK_MISSING_AFTER = "missing_after_fixture"
BLOCK_CITATION_LOSS = "citation_preservation_failed"


class PublicSourceRefreshPreviewError(ValueError):
    """Raised when preview inputs are malformed."""


def load_json_fixture(path: Path) -> JsonMap:
    """Load a JSON fixture without side effects beyond reading the fixture file."""

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise PublicSourceRefreshPreviewError(f"fixture must be a JSON object: {path}")
    return data


def build_preview_from_fixture_paths(
    public_source_refresh_plan_v2_path: Path,
    source_to_requirement_traceability_packet_v1_path: Path,
    inactive_public_source_fixtures_path: Path,
) -> JsonMap:
    """Build a deterministic preview from fixture paths."""

    return build_preview(
        public_source_refresh_plan_v2=load_json_fixture(public_source_refresh_plan_v2_path),
        source_to_requirement_traceability_packet_v1=load_json_fixture(
            source_to_requirement_traceability_packet_v1_path
        ),
        inactive_public_source_fixtures=load_json_fixture(inactive_public_source_fixtures_path),
    )


def build_preview(
    public_source_refresh_plan_v2: Mapping[str, Any],
    source_to_requirement_traceability_packet_v1: Mapping[str, Any],
    inactive_public_source_fixtures: Mapping[str, Any],
) -> JsonMap:
    """Create deterministic before/after preview rows for inactive sources only."""

    plan_sources = _index_by_source_id(public_source_refresh_plan_v2.get("source_updates", []))
    trace_sources = _index_by_source_id(source_to_requirement_traceability_packet_v1.get("source_traces", []))
    fixture_sources = _index_by_source_id(inactive_public_source_fixtures.get("sources", []))

    source_ids = sorted(set(plan_sources) | set(trace_sources) | set(fixture_sources))
    preview_rows: List[JsonMap] = []
    blocked_rows: List[JsonMap] = []
    citation_checks: List[JsonMap] = []
    validation_inventory: List[JsonMap] = []

    for source_id in source_ids:
        plan_entry = plan_sources.get(source_id)
        trace_entry = trace_sources.get(source_id, {"source_id": source_id})
        fixture_entry = fixture_sources.get(source_id)
        row = _build_row(source_id, plan_entry, trace_entry, fixture_entry)
        preview_rows.append(row)
        citation_checks.append(row["citation_preservation_check"])
        validation_inventory.extend(row["validation_inventory"])
        if row["blocked"]:
            blocked_rows.append(
                {
                    "source_id": source_id,
                    "blocked_reasons": row["blocked_reasons"],
                    "explanation": row["blocked_explanation"],
                    "reviewer_owner": row["reviewer_owner"],
                }
            )

    return {
        "preview_version": "public_source_refresh_inactive_patch_preview_v3",
        "refresh_plan_id": public_source_refresh_plan_v2.get("refresh_plan_id"),
        "traceability_packet_id": source_to_requirement_traceability_packet_v1.get("traceability_packet_id"),
        "fixture_inventory_id": inactive_public_source_fixtures.get("fixture_inventory_id"),
        "mode": "fixture_first_no_live_crawl_no_active_mutation",
        "reviewer_owner": public_source_refresh_plan_v2.get("reviewer_owner", "ppd-source-reviewer"),
        "rollback_checkpoints": list(public_source_refresh_plan_v2.get("rollback_checkpoints", [])),
        "preview_rows": preview_rows,
        "citation_preservation_checks": citation_checks,
        "blocked_rows": blocked_rows,
        "validation_inventory": _dedupe_validation_inventory(validation_inventory),
        "determinism": {
            "row_order": "source_id_ascending",
            "input_policy": "committed_fixtures_only",
            "network_policy": "disabled",
            "active_artifact_mutation": "disabled",
        },
    }


def _build_row(
    source_id: str,
    plan_entry: Optional[Mapping[str, Any]],
    trace_entry: Mapping[str, Any],
    fixture_entry: Optional[Mapping[str, Any]],
) -> JsonMap:
    reviewer_owner = _first_present(
        plan_entry.get("reviewer_owner") if plan_entry else None,
        trace_entry.get("reviewer_owner"),
        "ppd-source-reviewer",
    )
    before = fixture_entry.get("before", {}) if fixture_entry else {}
    after = fixture_entry.get("after", {}) if fixture_entry else {}
    affected_refs = {
        "requirements": sorted(trace_entry.get("affected_requirements", [])),
        "processes": sorted(trace_entry.get("affected_processes", [])),
        "guardrails": sorted(trace_entry.get("affected_guardrails", [])),
    }
    citation_check = _citation_preservation_check(source_id, trace_entry, before, after)

    blocked_reasons: List[str] = []
    if plan_entry is None:
        blocked_reasons.append(BLOCK_SOURCE_NOT_IN_PLAN)
    if fixture_entry and fixture_entry.get("artifact_state") != "inactive":
        blocked_reasons.append(BLOCK_ACTIVE_SOURCE)
    if not fixture_entry or not after:
        blocked_reasons.append(BLOCK_MISSING_AFTER)
    if not citation_check["passed"]:
        blocked_reasons.append(BLOCK_CITATION_LOSS)

    before_summary = {
        "document_id": before.get("document_id"),
        "content_hash": before.get("content_hash"),
        "citation_ids": sorted(before.get("citation_ids", [])),
    }
    after_summary = {
        "document_id": after.get("document_id"),
        "content_hash": after.get("content_hash"),
        "citation_ids": sorted(after.get("citation_ids", [])),
    }

    return {
        "source_id": source_id,
        "canonical_url": _first_present(
            fixture_entry.get("canonical_url") if fixture_entry else None,
            plan_entry.get("canonical_url") if plan_entry else None,
            trace_entry.get("canonical_url"),
        ),
        "blocked": bool(blocked_reasons),
        "blocked_reasons": blocked_reasons,
        "blocked_explanation": _blocked_explanation(blocked_reasons),
        "reviewer_owner": reviewer_owner,
        "before": before_summary,
        "after": after_summary,
        "proposed_patch": {
            "operation": "preview_replace_inactive_normalized_document",
            "mutates_active_artifacts": False,
            "raw_content_committed": False,
            "live_crawl_required": False,
        },
        "citation_preservation_check": citation_check,
        "affected_references": affected_refs,
        "validation_inventory": _row_validation_inventory(source_id, affected_refs, citation_check),
        "rollback_checkpoints": list(plan_entry.get("rollback_checkpoints", [])) if plan_entry else [],
    }


def _citation_preservation_check(
    source_id: str,
    trace_entry: Mapping[str, Any],
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> JsonMap:
    required = set(trace_entry.get("required_citation_ids", []))
    before_ids = set(before.get("citation_ids", []))
    after_ids = set(after.get("citation_ids", []))
    missing_before = sorted(required - before_ids)
    missing_after = sorted(required - after_ids)
    return {
        "source_id": source_id,
        "required_citation_ids": sorted(required),
        "missing_before_citation_ids": missing_before,
        "missing_after_citation_ids": missing_after,
        "passed": not missing_before and not missing_after,
    }


def _row_validation_inventory(
    source_id: str,
    affected_refs: Mapping[str, Sequence[str]],
    citation_check: Mapping[str, Any],
) -> List[JsonMap]:
    inventory = [
        {
            "validation_id": f"{source_id}:fixture-only-inputs",
            "source_id": source_id,
            "kind": "input_boundary",
            "status": "required",
        },
        {
            "validation_id": f"{source_id}:citation-preservation",
            "source_id": source_id,
            "kind": "citation_preservation",
            "status": "passed" if citation_check.get("passed") else "blocked",
        },
    ]
    for requirement_id in affected_refs.get("requirements", []):
        inventory.append(
            {
                "validation_id": f"{source_id}:requirement:{requirement_id}",
                "source_id": source_id,
                "kind": "affected_requirement_review",
                "status": "required",
            }
        )
    for process_id in affected_refs.get("processes", []):
        inventory.append(
            {
                "validation_id": f"{source_id}:process:{process_id}",
                "source_id": source_id,
                "kind": "affected_process_review",
                "status": "required",
            }
        )
    for guardrail_id in affected_refs.get("guardrails", []):
        inventory.append(
            {
                "validation_id": f"{source_id}:guardrail:{guardrail_id}",
                "source_id": source_id,
                "kind": "affected_guardrail_review",
                "status": "required",
            }
        )
    return inventory


def _blocked_explanation(blocked_reasons: Sequence[str]) -> Optional[str]:
    if not blocked_reasons:
        return None
    explanations = {
        BLOCK_SOURCE_NOT_IN_PLAN: "The fixture source is not authorized by public source refresh plan v2.",
        BLOCK_ACTIVE_SOURCE: "Only inactive public-source fixtures may be previewed by this patch preview.",
        BLOCK_MISSING_AFTER: "The fixture does not include a deterministic after state for review.",
        BLOCK_CITATION_LOSS: "One or more required traceability citations would be missing before or after the preview.",
    }
    return " ".join(explanations[reason] for reason in blocked_reasons)


def _index_by_source_id(items: Any) -> Dict[str, Mapping[str, Any]]:
    if not isinstance(items, list):
        raise PublicSourceRefreshPreviewError("expected a list of source records")
    indexed: Dict[str, Mapping[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            raise PublicSourceRefreshPreviewError("source records must be JSON objects")
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise PublicSourceRefreshPreviewError("source records must include a non-empty source_id")
        indexed[source_id] = item
    return indexed


def _dedupe_validation_inventory(items: Iterable[Mapping[str, Any]]) -> List[JsonMap]:
    deduped: Dict[str, JsonMap] = {}
    for item in items:
        validation_id = str(item.get("validation_id"))
        deduped[validation_id] = dict(item)
    return [deduped[key] for key in sorted(deduped)]


def _first_present(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None
