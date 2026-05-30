"""Fixture-first public source refresh execution readiness packets.

This module intentionally performs no network, processor, download, or registry
mutation work. It combines committed planning fixtures into a deterministic
operator readiness packet for review before any public source refresh run.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


READINESS_PACKET_SCHEMA_VERSION = "ppd-public-source-refresh-readiness-v1"


@dataclass(frozen=True)
class SourceInputs:
    """Normalized inputs for one proposed public source refresh target."""

    source_id: str
    canonical_url: str
    proposed_decision: str
    proposal_citations: tuple[str, ...]
    acceptance_status: str
    acceptance_citations: tuple[str, ...]
    runbook_citations: tuple[str, ...]
    owner: str
    reviewer: str
    expected_content_type: str


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON fixture as a dictionary."""

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected object fixture at {path}")
    return data


def _index_by_source_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("source item is missing source_id")
        indexed[source_id] = item
    return indexed


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("citation fields must be lists")
    return tuple(str(entry) for entry in value)


def _normalize_source_inputs(
    tranche_proposal: dict[str, Any],
    dry_run_acceptance: dict[str, Any],
    runbook_candidate: dict[str, Any],
) -> list[SourceInputs]:
    proposal_sources = _index_by_source_id(list(tranche_proposal.get("sources", [])))
    acceptance_sources = _index_by_source_id(list(dry_run_acceptance.get("sources", [])))
    runbook_sources = _index_by_source_id(list(runbook_candidate.get("sources", [])))

    source_ids = sorted(set(proposal_sources) | set(acceptance_sources) | set(runbook_sources))
    normalized: list[SourceInputs] = []
    for source_id in source_ids:
        proposal = proposal_sources.get(source_id, {})
        acceptance = acceptance_sources.get(source_id, {})
        runbook = runbook_sources.get(source_id, {})
        normalized.append(
            SourceInputs(
                source_id=source_id,
                canonical_url=str(proposal.get("canonical_url") or acceptance.get("canonical_url") or runbook.get("canonical_url") or ""),
                proposed_decision=str(proposal.get("proposed_decision", "missing")),
                proposal_citations=_as_tuple(proposal.get("citations", [])),
                acceptance_status=str(acceptance.get("dry_run_status", "missing")),
                acceptance_citations=_as_tuple(acceptance.get("citations", [])),
                runbook_citations=_as_tuple(runbook.get("citations", [])),
                owner=str(runbook.get("operator_owner") or proposal.get("owner") or "unassigned"),
                reviewer=str(runbook.get("reviewer_owner") or acceptance.get("reviewer") or "unassigned"),
                expected_content_type=str(proposal.get("expected_content_type", "unknown")),
            )
        )
    return normalized


def _decision_for(source: SourceInputs) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if source.proposed_decision != "include_refresh":
        reasons.append(f"proposal decision is {source.proposed_decision}")
    if source.acceptance_status != "accepted_metadata_only":
        reasons.append(f"dry-run acceptance is {source.acceptance_status}")
    if not source.canonical_url:
        reasons.append("canonical URL missing")
    if source.owner == "unassigned" or source.reviewer == "unassigned":
        reasons.append("operator or reviewer owner missing")
    if not source.runbook_citations:
        reasons.append("runbook citation missing")
    if reasons:
        return "no_go", reasons
    return "go", ["proposal, dry-run checklist, and runbook all support metadata-only refresh readiness"]


def build_readiness_packet(
    tranche_proposal: dict[str, Any],
    dry_run_acceptance: dict[str, Any],
    runbook_candidate: dict[str, Any],
) -> dict[str, Any]:
    """Build a deterministic no-side-effect readiness packet from fixtures."""

    generated_at = str(
        tranche_proposal.get("packet_timestamp")
        or dry_run_acceptance.get("packet_timestamp")
        or runbook_candidate.get("packet_timestamp")
        or "fixture-only"
    )
    source_inputs = _normalize_source_inputs(tranche_proposal, dry_run_acceptance, runbook_candidate)

    decisions: list[dict[str, Any]] = []
    expected_records: list[dict[str, Any]] = []
    for source in source_inputs:
        decision, reasons = _decision_for(source)
        citations = sorted(set(source.proposal_citations + source.acceptance_citations + source.runbook_citations))
        decisions.append(
            {
                "source_id": source.source_id,
                "canonical_url": source.canonical_url,
                "decision": decision,
                "reasons": reasons,
                "citations": citations,
                "reviewer_owner": source.reviewer,
                "operator_owner": source.owner,
            }
        )
        expected_records.append(
            {
                "source_id": source.source_id,
                "canonical_url": source.canonical_url,
                "capture_mode": "metadata_only",
                "expected_content_type": source.expected_content_type,
                "expected_fields": [
                    "source_id",
                    "canonical_url",
                    "http_status",
                    "content_type",
                    "content_hash",
                    "capture_started_at",
                    "capture_finished_at",
                    "processor_name",
                    "processor_version",
                    "skipped_reason",
                    "no_raw_body_persisted",
                ],
                "forbidden_fields": [
                    "raw_body",
                    "downloaded_document_path",
                    "authenticated_session_state",
                    "private_page_value",
                ],
            }
        )

    runbook_abort_triggers = list(runbook_candidate.get("abort_triggers", []))
    acceptance_abort_triggers = list(dry_run_acceptance.get("abort_triggers", []))
    attendance_prerequisites = list(runbook_candidate.get("operator_attendance_prerequisites", []))

    return {
        "schema_version": READINESS_PACKET_SCHEMA_VERSION,
        "packet_id": "fixture-public-source-refresh-readiness-20260529",
        "generated_at": generated_at,
        "inputs": {
            "tranche_proposal_packet_id": tranche_proposal.get("packet_id"),
            "dry_run_acceptance_packet_id": dry_run_acceptance.get("packet_id"),
            "runbook_candidate_id": runbook_candidate.get("runbook_id"),
        },
        "execution_scope": "fixture_first_public_source_refresh_readiness",
        "per_source_go_no_go": decisions,
        "operator_attendance_prerequisites": attendance_prerequisites,
        "abort_triggers": sorted(set(str(item) for item in runbook_abort_triggers + acceptance_abort_triggers)),
        "expected_metadata_only_capture_records": expected_records,
        "reviewer_owner_fields": [
            {
                "source_id": decision["source_id"],
                "operator_owner": decision["operator_owner"],
                "reviewer_owner": decision["reviewer_owner"],
                "review_status": "pending_human_review",
            }
            for decision in decisions
        ],
        "attestations": {
            "fixture_first": True,
            "no_live_fetch": True,
            "no_download": True,
            "no_processor_invocation": True,
            "no_registry_mutation": True,
            "no_authenticated_automation": True,
            "no_raw_body_persistence": True,
        },
    }


def build_readiness_packet_from_fixture_dir(fixture_dir: Path) -> dict[str, Any]:
    """Build the packet from the standard committed fixture directory."""

    return build_readiness_packet(
        load_json(fixture_dir / "public_source_refresh_tranche_proposal_packet.json"),
        load_json(fixture_dir / "public_source_refresh_dry_run_acceptance_checklist_packet.json"),
        load_json(fixture_dir / "source_refresh_runbook_candidate.json"),
    )
