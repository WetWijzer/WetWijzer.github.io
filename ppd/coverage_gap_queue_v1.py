"""Fixture-first coverage gap queue for Portland PP&D requirement extraction.

This module is intentionally offline-only: it consumes fixture packets and returns
review queue items without mutating active requirements or guardrail bundles.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

GAP_TYPES = (
    "forms",
    "pdfs",
    "fee_triggers",
    "deadlines",
    "file_rules",
    "permit_type_exceptions",
    "action_gates",
)

REQUIRED_QUEUE_FIELDS = (
    "gap_id",
    "gap_type",
    "title",
    "citation",
    "affected_document_ids",
    "affected_source_ids",
    "affected_requirement_ids",
    "human_review_status",
    "reviewer_owner",
    "rollback_note",
    "offline_validation_commands",
)

HUMAN_REVIEW_STATUSES = {"needs_review", "in_review", "approved", "rejected"}

_PRIVATE_OR_AUTH_KEYS = {
    "auth",
    "authorization",
    "bearer_token",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session",
    "mfa",
    "password",
    "private_artifact",
    "private_case_facts",
    "secret",
    "session",
    "session_file",
    "storage_state",
    "token",
    "username",
}

_RAW_ARTIFACT_KEYS = {
    "body",
    "content",
    "download_path",
    "downloaded_data",
    "downloaded_document",
    "pdf_bytes",
    "raw_body",
    "raw_content",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "raw_response",
    "response_body",
    "screenshot",
    "screenshot_path",
    "trace",
    "trace_path",
    "warc_path",
}

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_document_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "agent_state_mutation",
    "applies_source_update",
    "document_mutation",
    "guardrail_mutation",
    "mutates_agent_state",
    "mutates_documents",
    "mutates_guardrails",
    "mutates_processes",
    "mutates_release_state",
    "mutates_requirements",
    "mutates_sources",
    "process_mutation",
    "promotes_guardrail_bundle",
    "release_state_mutation",
    "requirement_mutation",
    "source_mutation",
    "updates_active_source_registry",
    "updates_agent_state",
    "updates_documents",
    "updates_guardrails",
    "updates_processes",
    "updates_release_state",
    "updates_requirements",
}

_LIVE_EXTRACTION_OR_PROMOTION_PHRASES = (
    "extraction completed",
    "extraction executed",
    "extraction ran",
    "live extraction",
    "live promotion",
    "promoted to active",
    "promotion completed",
    "published to active",
    "ran extractor",
    "ran live",
    "requirements promoted",
)

_OUTCOME_GUARANTEE_PHRASES = (
    "approval guaranteed",
    "approved automatically",
    "guaranteed approval",
    "guarantees approval",
    "permit approved",
    "permit issuance guaranteed",
    "will be approved",
    "will be issued",
    "will pass inspection",
)

_CONSEQUENTIAL_ACTION_PHRASES = (
    "cancel inspection",
    "certify acknowledgement",
    "make payment",
    "pay fee",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit permit",
    "submit payment",
    "upload correction",
    "upload to devhub",
    "withdraw permit",
)


@dataclass(frozen=True)
class CoverageGapQueueViolation:
    code: str
    path: str
    message: str


class CoverageGapQueueValidationError(ValueError):
    """Raised when a coverage gap queue packet is unsafe or malformed."""

    def __init__(self, violations: list[CoverageGapQueueViolation]) -> None:
        self.violations = violations
        codes = ", ".join(sorted({violation.code for violation in violations}))
        super().__init__(f"invalid coverage gap queue v1: {codes}")


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected object fixture at {path}")
    return data


def build_coverage_gap_queue_v1(
    traceability_packet: dict[str, Any],
    document_records: dict[str, Any],
    requirement_nodes: dict[str, Any],
    public_source_change_impact: dict[str, Any],
    official_source_anchor_audit: dict[str, Any],
) -> dict[str, Any]:
    documents_by_id = {item["document_id"]: item for item in document_records.get("documents", [])}
    requirements_by_id = {item["requirement_id"]: item for item in requirement_nodes.get("requirements", [])}
    traces_by_requirement = {
        item["requirement_id"]: item for item in traceability_packet.get("requirement_traces", [])
    }
    impacted_sources = {
        source_id
        for item in public_source_change_impact.get("impacts", [])
        for source_id in item.get("affected_source_ids", [])
    }
    anchor_findings = {
        item["source_id"]: item
        for item in official_source_anchor_audit.get("anchor_findings", [])
        if item.get("status") != "pass"
    }

    queue: list[dict[str, Any]] = []
    seen: set[str] = set()

    for requirement_id, requirement in sorted(requirements_by_id.items()):
        trace = traces_by_requirement.get(requirement_id, {})
        source_ids = list(dict.fromkeys(trace.get("source_ids", []) + requirement.get("source_ids", [])))
        document_ids = list(dict.fromkeys(trace.get("document_ids", []) + requirement.get("document_ids", [])))
        gap_types = [item for item in requirement.get("coverage_gap_types", []) if item in GAP_TYPES]

        for gap_type in gap_types:
            gap_id = f"coverage-gap-v1:{gap_type}:{requirement_id}"
            if gap_id in seen:
                continue
            seen.add(gap_id)
            cited_source = _first_cited_source(source_ids, anchor_findings, documents_by_id)
            queue.append(
                _queue_item(
                    gap_id=gap_id,
                    gap_type=gap_type,
                    title=requirement.get("title", f"Review {gap_type} extraction coverage"),
                    citation=cited_source,
                    document_ids=document_ids,
                    source_ids=source_ids,
                    requirement_ids=[requirement_id],
                    reason=requirement.get("coverage_gap_reason", "Fixture marks this requirement as needing extraction coverage review."),
                    impacted=bool(set(source_ids) & impacted_sources),
                )
            )

    packet = {
        "packet_type": "fixture_first_requirement_extraction_coverage_gap_queue_v1",
        "source_packets": {
            "traceability_packet_id": traceability_packet.get("packet_id"),
            "document_records_fixture_id": document_records.get("fixture_id"),
            "requirement_nodes_fixture_id": requirement_nodes.get("fixture_id"),
            "public_source_change_impact_packet_id": public_source_change_impact.get("packet_id"),
            "official_source_anchor_audit_packet_id": official_source_anchor_audit.get("packet_id"),
        },
        "gap_types": list(GAP_TYPES),
        "queue": queue,
    }
    assert_valid_coverage_gap_queue_v1(packet)
    return packet


def build_coverage_gap_queue_from_paths(paths: dict[str, str | Path]) -> dict[str, Any]:
    return build_coverage_gap_queue_v1(
        traceability_packet=load_json(paths["traceability_packet"]),
        document_records=load_json(paths["document_records"]),
        requirement_nodes=load_json(paths["requirement_nodes"]),
        public_source_change_impact=load_json(paths["public_source_change_impact"]),
        official_source_anchor_audit=load_json(paths["official_source_anchor_audit"]),
    )


def validate_coverage_gap_queue_v1(packet: Mapping[str, Any]) -> list[CoverageGapQueueViolation]:
    violations: list[CoverageGapQueueViolation] = []

    if packet.get("packet_type") != "fixture_first_requirement_extraction_coverage_gap_queue_v1":
        violations.append(_violation("invalid_packet_type", "packet_type", "coverage gap queue packet type is not recognized"))

    queue = packet.get("queue")
    if not isinstance(queue, list):
        return violations + [_violation("missing_queue", "queue", "coverage gap queue must be a list")]

    for index, item in enumerate(queue):
        path = f"queue[{index}]"
        if not isinstance(item, Mapping):
            violations.append(_violation("invalid_queue_item", path, "coverage gap queue item must be an object"))
            continue
        violations.extend(_validate_queue_item(item, path))

    violations.extend(_validate_forbidden_content(packet, "packet"))
    return violations


def assert_valid_coverage_gap_queue_v1(packet: Mapping[str, Any]) -> None:
    violations = validate_coverage_gap_queue_v1(packet)
    if violations:
        raise CoverageGapQueueValidationError(violations)


def is_valid_coverage_gap_queue_v1(packet: Mapping[str, Any]) -> bool:
    return not validate_coverage_gap_queue_v1(packet)


def _validate_queue_item(item: Mapping[str, Any], path: str) -> list[CoverageGapQueueViolation]:
    violations: list[CoverageGapQueueViolation] = []

    for field in REQUIRED_QUEUE_FIELDS:
        if field not in item:
            violations.append(_violation("missing_required_field", f"{path}.{field}", "queue item is missing a required field"))

    if item.get("gap_type") not in GAP_TYPES:
        violations.append(_violation("invalid_gap_type", f"{path}.gap_type", "gap type is not allowed for coverage gap queue v1"))

    for field, code in (
        ("affected_document_ids", "missing_affected_document_ids"),
        ("affected_source_ids", "missing_affected_source_ids"),
        ("affected_requirement_ids", "missing_affected_requirement_ids"),
    ):
        if not _non_empty_string_list(item.get(field)):
            violations.append(_violation(code, f"{path}.{field}", f"{field} must contain at least one identifier"))

    status = item.get("human_review_status")
    if status not in HUMAN_REVIEW_STATUSES:
        violations.append(_violation("missing_human_review_status", f"{path}.human_review_status", "human review status is required"))

    if not _non_empty_text(item.get("reviewer_owner")):
        violations.append(_violation("missing_reviewer_owner", f"{path}.reviewer_owner", "reviewer owner is required"))

    if not _non_empty_text(item.get("rollback_note")):
        violations.append(_violation("missing_rollback_note", f"{path}.rollback_note", "rollback note is required"))

    citation = item.get("citation")
    if not isinstance(citation, Mapping):
        violations.append(_violation("uncited_gap", f"{path}.citation", "coverage gap item must include a citation object"))
    else:
        source_ids = item.get("affected_source_ids") if isinstance(item.get("affected_source_ids"), list) else []
        citation_source_id = citation.get("source_id")
        if not _non_empty_text(citation_source_id):
            violations.append(_violation("uncited_gap", f"{path}.citation.source_id", "citation source_id is required"))
        elif source_ids and citation_source_id not in source_ids:
            violations.append(_violation("uncited_gap", f"{path}.citation.source_id", "citation source_id must be affected by this gap"))
        if not _non_empty_text(citation.get("url")):
            violations.append(_violation("uncited_gap", f"{path}.citation.url", "citation URL is required"))
        if not _non_empty_text(citation.get("anchor")):
            violations.append(_violation("uncited_gap", f"{path}.citation.anchor", "citation anchor is required"))
        if citation.get("audit_status") == "missing_source_anchor":
            violations.append(_violation("uncited_gap", f"{path}.citation.audit_status", "missing source anchors cannot enter the queue"))

    return violations


def _first_cited_source(
    source_ids: list[str],
    anchor_findings: dict[str, dict[str, Any]],
    documents_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    for source_id in source_ids:
        finding = anchor_findings.get(source_id)
        if finding:
            return {
                "source_id": source_id,
                "anchor": finding.get("anchor"),
                "url": finding.get("url"),
                "audit_status": finding.get("status"),
            }
    for document in documents_by_id.values():
        if document.get("source_id") in source_ids:
            return {
                "source_id": document.get("source_id"),
                "anchor": document.get("official_anchor"),
                "url": document.get("official_url"),
                "audit_status": "not_audited_in_fixture",
            }
    return {"source_id": source_ids[0] if source_ids else None, "audit_status": "missing_source_anchor"}


def _queue_item(
    *,
    gap_id: str,
    gap_type: str,
    title: str,
    citation: dict[str, Any],
    document_ids: list[str],
    source_ids: list[str],
    requirement_ids: list[str],
    reason: str,
    impacted: bool,
) -> dict[str, Any]:
    item = {
        "gap_id": gap_id,
        "gap_type": gap_type,
        "title": title,
        "citation": citation,
        "affected_document_ids": document_ids,
        "affected_source_ids": source_ids,
        "affected_requirement_ids": requirement_ids,
        "human_review_status": "needs_review",
        "reviewer_owner": "ppd-fixture-reviewer",
        "rollback_note": "Fixture-only queue item; remove this generated packet to roll back without changing active requirements.",
        "offline_validation_commands": [
            ["python3", "-m", "py_compile", "ppd/coverage_gap_queue_v1.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_coverage_gap_queue_v1.py"],
        ],
        "reason": reason,
        "public_source_change_impacted": impacted,
    }
    missing = [field for field in REQUIRED_QUEUE_FIELDS if field not in item]
    if missing:
        raise ValueError(f"queue item missing required fields: {missing}")
    return item


def _validate_forbidden_content(value: Any, path: str) -> list[CoverageGapQueueViolation]:
    violations: list[CoverageGapQueueViolation] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized_key = _normalize_key(str(key))
            nested_path = f"{path}.{key}"
            if normalized_key in _PRIVATE_OR_AUTH_KEYS:
                violations.append(_violation("private_or_authenticated_artifact", nested_path, "private or authenticated artifacts are not allowed"))
            if normalized_key in _RAW_ARTIFACT_KEYS:
                violations.append(_violation("raw_artifact", nested_path, "raw crawl, PDF, response, trace, screenshot, or downloaded data is not allowed"))
            if normalized_key in _MUTATION_KEYS and nested not in (False, None, "", [], {}):
                violations.append(_violation("active_mutation_flag", nested_path, "active source, document, requirement, process, guardrail, release-state, or agent-state mutation flags are not allowed"))
            violations.extend(_validate_forbidden_content(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            violations.extend(_validate_forbidden_content(nested, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = " ".join(value.lower().split())
        if _contains_phrase(lowered, _LIVE_EXTRACTION_OR_PROMOTION_PHRASES):
            violations.append(_violation("live_extraction_or_promotion_claim", path, "live extraction or promotion claims are not allowed"))
        if _contains_phrase(lowered, _OUTCOME_GUARANTEE_PHRASES):
            violations.append(_violation("legal_or_permitting_outcome_guarantee", path, "legal or permitting outcome guarantees are not allowed"))
        if _contains_phrase(lowered, _CONSEQUENTIAL_ACTION_PHRASES):
            violations.append(_violation("consequential_action_language", path, "consequential action language is not allowed in coverage gap queue items"))
    return violations


def _contains_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_non_empty_text(item) for item in value)


def _violation(code: str, path: str, message: str) -> CoverageGapQueueViolation:
    return CoverageGapQueueViolation(code=code, path=path, message=message)
