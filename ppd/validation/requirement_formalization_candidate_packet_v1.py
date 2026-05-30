"""Validation for requirement formalization candidate packet v1.

This validator is intentionally local and deterministic. It checks packet metadata
and candidate rows before any formalization workflow can consume them.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


REQUIRED_PACKET_FIELDS = (
    "reviewer_owner",
    "rollback_note",
    "review_status",
    "formalization_status",
)

REQUIRED_ROW_FIELDS = (
    "affected_source_id",
    "affected_document_id",
    "affected_requirement_id",
    "confidence",
    "review_status",
    "formalization_status",
)

MUTATION_FLAG_NAMES = {
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "source_mutation",
    "document_mutation",
    "requirement_mutation",
    "process_mutation",
    "guardrail_mutation",
    "release_state_mutation",
    "agent_state_mutation",
    "mutates_source",
    "mutates_document",
    "mutates_requirement",
    "mutates_process",
    "mutates_guardrail",
    "mutates_release_state",
    "mutates_agent_state",
}

PRIVATE_ARTIFACT_TERMS = (
    "authorization",
    "bearer ",
    "cookie",
    "devhub_session",
    "password",
    "private_artifact",
    "private devhub",
    "session_token",
    "x-csrf",
)

RAW_ARTIFACT_KEYS = {
    "download_path",
    "downloaded_file",
    "downloaded_pdf",
    "html_snapshot",
    "pdf_bytes",
    "pdf_path",
    "raw_body",
    "raw_crawl_output",
    "raw_html",
    "raw_pdf",
    "screenshot_path",
}

RAW_ARTIFACT_TYPES = {
    "download",
    "downloaded_document",
    "pdf",
    "raw_crawl",
    "raw_html",
    "raw_pdf",
}

GUARANTEE_TERMS = (
    "guarantee approval",
    "guaranteed approval",
    "guarantees approval",
    "legal guarantee",
    "permit will be approved",
    "permitting outcome guarantee",
    "will be approved",
    "will be granted",
)

CONSEQUENTIAL_ACTION_TERMS = (
    "appeal the decision",
    "cancel the application",
    "certify compliance",
    "file the permit",
    "make payment",
    "pay the fee",
    "schedule inspection",
    "submit the application",
    "upload the plans",
)


def validate_packet(packet: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return validation issues for a candidate packet v1 mapping."""

    issues: list[ValidationIssue] = []

    version = packet.get("packet_version") or packet.get("version")
    if version not in {"requirement_formalization_candidate_packet_v1", "v1"}:
        issues.append(
            ValidationIssue(
                "invalid_packet_version",
                "packet_version",
                "packet_version must identify requirement formalization candidate packet v1",
            )
        )

    for field in REQUIRED_PACKET_FIELDS:
        if _blank(packet.get(field)):
            issues.append(
                ValidationIssue(
                    "missing_packet_metadata",
                    field,
                    f"packet is missing required metadata field {field}",
                )
            )

    rows = packet.get("candidate_rows", packet.get("candidates"))
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        issues.append(
            ValidationIssue(
                "missing_candidate_rows",
                "candidate_rows",
                "packet must include a candidate_rows sequence",
            )
        )
        rows = []

    for index, row in enumerate(rows):
        row_path = f"candidate_rows[{index}]"
        if not isinstance(row, Mapping):
            issues.append(
                ValidationIssue(
                    "invalid_candidate_row",
                    row_path,
                    "candidate row must be an object",
                )
            )
            continue

        for field in REQUIRED_ROW_FIELDS:
            if _blank(row.get(field)):
                issues.append(
                    ValidationIssue(
                        "missing_candidate_field",
                        f"{row_path}.{field}",
                        f"candidate row is missing required field {field}",
                    )
                )

        citations = row.get("citations") or row.get("source_citations") or row.get("evidence_citations")
        if not isinstance(citations, Sequence) or isinstance(citations, (str, bytes)) or len(citations) == 0:
            issues.append(
                ValidationIssue(
                    "uncited_candidate_row",
                    f"{row_path}.citations",
                    "candidate row must include at least one structured citation",
                )
            )

    _scan_value(packet, "packet", issues)
    return issues


def is_valid_packet(packet: Mapping[str, Any]) -> bool:
    return not validate_packet(packet)


def issue_dicts(packet: Mapping[str, Any]) -> list[dict[str, str]]:
    return [issue.__dict__.copy() for issue in validate_packet(packet)]


def _blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _scan_value(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            lowered_key = key_text.lower()

            if lowered_key in RAW_ARTIFACT_KEYS and not _blank(child):
                issues.append(
                    ValidationIssue(
                        "raw_or_downloaded_artifact",
                        child_path,
                        "packet must not include raw crawl, PDF, screenshot, or downloaded artifact data",
                    )
                )

            if lowered_key in MUTATION_FLAG_NAMES and child is True:
                issues.append(
                    ValidationIssue(
                        "active_mutation_flag",
                        child_path,
                        "packet must not request active source, document, requirement, process, guardrail, release-state, or agent-state mutation",
                    )
                )

            if lowered_key == "artifact_type" and str(child).lower() in RAW_ARTIFACT_TYPES:
                issues.append(
                    ValidationIssue(
                        "raw_or_downloaded_artifact",
                        child_path,
                        "packet must not reference raw crawl, PDF, or downloaded artifact types",
                    )
                )

            _scan_value(child, child_path, issues)
        return

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _scan_value(child, f"{path}[{index}]", issues)
        return

    if isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in PRIVATE_ARTIFACT_TERMS):
            issues.append(
                ValidationIssue(
                    "private_or_authenticated_artifact",
                    path,
                    "packet must not include private or authenticated artifacts, sessions, cookies, or tokens",
                )
            )
        if any(term in lowered for term in GUARANTEE_TERMS):
            issues.append(
                ValidationIssue(
                    "legal_or_permitting_outcome_guarantee",
                    path,
                    "packet must not include legal or permitting outcome guarantees",
                )
            )
        if any(term in lowered for term in CONSEQUENTIAL_ACTION_TERMS):
            issues.append(
                ValidationIssue(
                    "consequential_action_language",
                    path,
                    "packet must not include consequential action language",
                )
            )
