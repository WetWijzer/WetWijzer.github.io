"""Validation for PP&D HTML extraction review packets.

The validator is deterministic and side-effect free. It checks already-built
review packet dictionaries and never fetches URLs, persists page bodies, or
opens authenticated sessions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

_ALLOWED_HOSTS = {
    "www.portland.gov",
    "portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "portlandoregon.gov",
    "www.portlandmaps.com",
    "portlandmaps.com",
}

_PRIVATE_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
}

_PRIVATE_PATH_MARKERS = (
    "/login",
    "/signin",
    "/sign-in",
    "/register",
    "/account",
    "/accounts",
    "/my-permits",
    "/mypermits",
    "/cart",
    "/checkout",
    "/payment",
    "/payments",
    "/upload",
    "/submit",
    "/inspection/schedule",
)

_FORBIDDEN_BODY_KEYS = {
    "html",
    "raw_html",
    "rawHtml",
    "body",
    "raw_body",
    "rawBody",
    "body_html",
    "bodyHtml",
    "body_text",
    "bodyText",
    "raw_content",
    "rawContent",
}

_READY_STATUSES = {"ready", "passed", "approved", "complete", "compiled"}
_PENDING_HUMAN_REVIEW_STATUSES = {
    "pending",
    "pending_human_review",
    "needs_human_review",
    "queued_for_human_review",
    "not_reviewed",
}

_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class HtmlReviewPacketValidationIssue:
    code: str
    message: str
    path: str


@dataclass(frozen=True)
class HtmlReviewPacketValidationResult:
    ok: bool
    issues: tuple[HtmlReviewPacketValidationIssue, ...] = field(default_factory=tuple)

    def error_codes(self) -> tuple[str, ...]:
        return tuple(issue.code for issue in self.issues)


def validate_html_extraction_review_packet(packet: dict[str, Any]) -> HtmlReviewPacketValidationResult:
    issues: list[HtmlReviewPacketValidationIssue] = []

    _reject_body_storage(packet, "$", issues)
    _validate_source_identity(packet, issues)
    _validate_freshness_evidence(packet, issues)
    _validate_content_hash(packet, issues)
    _validate_section_ordering(packet, issues)
    _validate_section_citations(packet, issues)
    _validate_links(packet, issues)
    _validate_guardrail_status(packet, issues)

    return HtmlReviewPacketValidationResult(ok=not issues, issues=tuple(issues))


def assert_html_extraction_review_packet(packet: dict[str, Any]) -> None:
    result = validate_html_extraction_review_packet(packet)
    if result.ok:
        return
    details = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in result.issues)
    raise ValueError(details)


def _issue(issues: list[HtmlReviewPacketValidationIssue], code: str, path: str, message: str) -> None:
    issues.append(HtmlReviewPacketValidationIssue(code=code, path=path, message=message))


def _reject_body_storage(value: Any, path: str, issues: list[HtmlReviewPacketValidationIssue]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _FORBIDDEN_BODY_KEYS:
                _issue(issues, "raw_or_body_storage", child_path, "review packets must not store raw HTML or page body fields")
            _reject_body_storage(child, child_path, issues)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_body_storage(child, f"{path}[{index}]", issues)


def _source(packet: dict[str, Any]) -> dict[str, Any]:
    source = packet.get("source")
    return source if isinstance(source, dict) else {}


def _extraction(packet: dict[str, Any]) -> dict[str, Any]:
    extraction = packet.get("extraction")
    return extraction if isinstance(extraction, dict) else {}


def _validate_source_identity(packet: dict[str, Any], issues: list[HtmlReviewPacketValidationIssue]) -> None:
    source = _source(packet)
    extraction = _extraction(packet)
    source_id = source.get("source_id") or packet.get("source_id")
    if not isinstance(source_id, str) or not source_id.strip():
        _issue(issues, "missing_source_id", "$.source.source_id", "source_id is required")
    extraction_source_id = extraction.get("source_id")
    if not isinstance(extraction_source_id, str) or not extraction_source_id.strip():
        _issue(issues, "missing_source_id", "$.extraction.source_id", "extraction source_id is required")
    elif isinstance(source_id, str) and source_id.strip() and extraction_source_id != source_id:
        _issue(issues, "source_id_mismatch", "$.extraction.source_id", "extraction source_id must match packet source_id")


def _validate_freshness_evidence(packet: dict[str, Any], issues: list[HtmlReviewPacketValidationIssue]) -> None:
    source = _source(packet)
    fetched_at = source.get("fetched_at") or packet.get("fetched_at")
    if not isinstance(fetched_at, str) or not fetched_at.strip():
        _issue(issues, "missing_freshness_evidence", "$.source.fetched_at", "capture freshness timestamp is required")

    evidence_fields = (
        source.get("last_modified_at"),
        source.get("last_reviewed_at"),
        source.get("published_at"),
        source.get("visible_date_evidence"),
        packet.get("modified_date_evidence"),
    )
    evidence_list = source.get("date_evidence")
    has_list_evidence = isinstance(evidence_list, list) and bool(evidence_list)
    has_scalar_evidence = any(isinstance(item, str) and item.strip() for item in evidence_fields)
    if not has_list_evidence and not has_scalar_evidence:
        _issue(issues, "missing_date_evidence", "$.source", "visible or metadata date evidence is required")


def _validate_content_hash(packet: dict[str, Any], issues: list[HtmlReviewPacketValidationIssue]) -> None:
    extraction = _extraction(packet)
    content_hash = extraction.get("content_hash") or packet.get("content_hash")
    if not isinstance(content_hash, str) or not _HASH_RE.match(content_hash):
        _issue(issues, "invented_hash", "$.extraction.content_hash", "content_hash must be a sha256 digest with 64 lowercase hex characters")
        return

    hash_evidence = extraction.get("hash_evidence") or packet.get("hash_evidence")
    if not isinstance(hash_evidence, dict):
        _issue(issues, "invented_hash", "$.extraction.hash_evidence", "hash evidence is required")
        return
    if hash_evidence.get("value") != content_hash:
        _issue(issues, "invented_hash", "$.extraction.hash_evidence.value", "hash evidence value must match content_hash")
    if hash_evidence.get("algorithm") != "sha256":
        _issue(issues, "invented_hash", "$.extraction.hash_evidence.algorithm", "hash evidence algorithm must be sha256")
    if hash_evidence.get("derived_from") not in {"normalized_text", "extracted_text", "public_capture_metadata"}:
        _issue(issues, "invented_hash", "$.extraction.hash_evidence.derived_from", "hash must be derived from a supported public extraction artifact")
    if hash_evidence.get("status") in {"invented", "placeholder", "llm_generated"}:
        _issue(issues, "invented_hash", "$.extraction.hash_evidence.status", "invented or placeholder hash statuses are rejected")


def _sections(packet: dict[str, Any]) -> list[Any]:
    extraction = _extraction(packet)
    sections = extraction.get("sections")
    return sections if isinstance(sections, list) else []


def _validate_section_ordering(packet: dict[str, Any], issues: list[HtmlReviewPacketValidationIssue]) -> None:
    extraction = _extraction(packet)
    sections = _sections(packet)
    if extraction.get("section_order_preserved") is not True:
        _issue(issues, "lost_section_ordering", "$.extraction.section_order_preserved", "section order must be explicitly preserved")
    if extraction.get("lost_section_ordering") is True:
        _issue(issues, "lost_section_ordering", "$.extraction.lost_section_ordering", "lost section ordering is rejected")
    sequences: list[int] = []
    for index, section in enumerate(sections):
        if not isinstance(section, dict):
            _issue(issues, "lost_section_ordering", f"$.extraction.sections[{index}]", "section must be an object")
            continue
        sequence = section.get("sequence")
        if not isinstance(sequence, int):
            _issue(issues, "lost_section_ordering", f"$.extraction.sections[{index}].sequence", "section sequence integer is required")
        else:
            sequences.append(sequence)
    expected = list(range(1, len(sequences) + 1))
    if sequences and sequences != expected:
        _issue(issues, "lost_section_ordering", "$.extraction.sections", "section sequences must be contiguous and in source order")


def _validate_section_citations(packet: dict[str, Any], issues: list[HtmlReviewPacketValidationIssue]) -> None:
    source_id = _source(packet).get("source_id") or packet.get("source_id")
    for index, section in enumerate(_sections(packet)):
        if not isinstance(section, dict):
            continue
        path = f"$.extraction.sections[{index}]"
        citations = section.get("citation_spans") or section.get("source_evidence_ids")
        if not isinstance(citations, list) or not citations:
            _issue(issues, "uncited_extracted_section", path, "each extracted section requires citation spans or source evidence ids")
        if section.get("source_id") != source_id:
            _issue(issues, "missing_source_id", f"{path}.source_id", "section source_id must match packet source_id")


def _validate_links(packet: dict[str, Any], issues: list[HtmlReviewPacketValidationIssue]) -> None:
    extraction = _extraction(packet)
    links = extraction.get("links", [])
    if not isinstance(links, list):
        _issue(issues, "unsupported_or_private_link", "$.extraction.links", "links must be a list")
        return
    for index, link in enumerate(links):
        path = f"$.extraction.links[{index}]"
        if not isinstance(link, dict):
            _issue(issues, "unsupported_or_private_link", path, "link must be an object")
            continue
        url = link.get("url")
        if not isinstance(url, str) or not _is_supported_public_link(url):
            _issue(issues, "unsupported_or_private_link", f"{path}.url", "link must use an allowed public PP&D host and must not target private or authenticated paths")


def _is_supported_public_link(url: str) -> bool:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme in {"mailto", "tel"}:
        return True
    if scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower()
    if host in _PRIVATE_HOSTS or host.endswith(".local") or host.endswith(".internal"):
        return False
    if host not in _ALLOWED_HOSTS:
        return False
    path = parsed.path.lower()
    return not any(marker in path for marker in _PRIVATE_PATH_MARKERS)


def _validate_guardrail_status(packet: dict[str, Any], issues: list[HtmlReviewPacketValidationIssue]) -> None:
    human_status = str(packet.get("human_review_status", "pending_human_review")).lower()
    guardrail_status = str(packet.get("guardrail_status", packet.get("validation_status", ""))).lower()
    if human_status in _PENDING_HUMAN_REVIEW_STATUSES and guardrail_status in _READY_STATUSES:
        _issue(issues, "ready_guardrail_status_before_human_review", "$.guardrail_status", "guardrails cannot be marked ready before human review")
