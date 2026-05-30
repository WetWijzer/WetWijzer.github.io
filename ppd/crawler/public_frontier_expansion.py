"""Fixture-first public crawl frontier expansion for PP&D.

This module intentionally performs no network I/O. It converts committed audit,
allowlist, robots/policy, and source-index fixtures into metadata-only candidate
frontier rows that can be reviewed before any live crawl is scheduled.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


SUPPORTED_SCHEMES = {"http", "https"}
HTML_CONTENT_TYPES = {"text/html", "application/xhtml+xml"}
PDF_CONTENT_TYPES = {"application/pdf"}


@dataclass(frozen=True)
class FrontierCandidate:
    """Metadata-only candidate row for a future public crawl frontier."""

    canonical_url: str
    source_page: str
    link_text: str
    content_type_expectation: str
    allow_skip_decision: str
    skip_reason: str
    processor_handoff_expectation: str
    reviewer_owner: str
    rollback_note: str
    offline_validation_commands: tuple[tuple[str, ...], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "canonical_url": self.canonical_url,
            "source_page": self.source_page,
            "link_text": self.link_text,
            "content_type_expectation": self.content_type_expectation,
            "allow_skip_decision": self.allow_skip_decision,
            "skip_reason": self.skip_reason,
            "processor_handoff_expectation": self.processor_handoff_expectation,
            "reviewer_owner": self.reviewer_owner,
            "rollback_note": self.rollback_note,
            "offline_validation_commands": [list(command) for command in self.offline_validation_commands],
        }


def load_fixture_packet(path: Path) -> dict[str, Any]:
    """Load a frontier expansion fixture packet from JSON."""

    with path.open("r", encoding="utf-8") as fixture_file:
        packet = json.load(fixture_file)
    if not isinstance(packet, dict):
        raise ValueError("frontier expansion fixture packet must be a JSON object")
    return packet


def expand_public_frontier_from_fixture(path: Path) -> list[dict[str, Any]]:
    """Expand a fixture packet into deterministic candidate frontier rows."""

    return [candidate.as_dict() for candidate in expand_public_frontier(load_fixture_packet(path))]


def expand_public_frontier(packet: dict[str, Any]) -> list[FrontierCandidate]:
    """Build metadata-only candidate rows from fixture data.

    Expected packet keys:
    - official_source_anchor_audit_packet_v1.anchors[].links[]
    - public_crawl_allowlist_fixtures_v1.allowed_hosts[]
    - robots_policy_preflight_fixtures_v1.decisions[]
    - source_index_records_v1.records[]
    """

    allowed_hosts = set(_string_list(packet.get("public_crawl_allowlist_fixtures_v1", {}).get("allowed_hosts", [])))
    private_patterns = tuple(_string_list(packet.get("public_crawl_allowlist_fixtures_v1", {}).get("private_path_patterns", [])))
    robots_by_url = _robots_decisions(packet.get("robots_policy_preflight_fixtures_v1", {}).get("decisions", []))
    source_index = _source_index(packet.get("source_index_records_v1", {}).get("records", []))
    reviewer_owner = str(packet.get("reviewer_owner", "ppd-public-crawl-reviewer"))
    rollback_note = str(packet.get("rollback_note", "Remove generated metadata-only candidates before promoting any active frontier."))
    validation_commands = _validation_commands(packet.get("offline_validation_commands", []))

    candidates: list[FrontierCandidate] = []
    seen: set[tuple[str, str]] = set()

    anchors = packet.get("official_source_anchor_audit_packet_v1", {}).get("anchors", [])
    if not isinstance(anchors, list):
        raise ValueError("official_source_anchor_audit_packet_v1.anchors must be a list")

    for anchor in anchors:
        if not isinstance(anchor, dict):
            continue
        source_page = canonicalize_url(str(anchor.get("canonical_url", "")))
        links = anchor.get("links", [])
        if not isinstance(links, list):
            continue
        for link in links:
            if not isinstance(link, dict):
                continue
            raw_url = str(link.get("href", ""))
            canonical_url = canonicalize_url(raw_url)
            if not canonical_url:
                continue
            dedupe_key = (source_page, canonical_url)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            source_record = source_index.get(canonical_url, {})
            content_type = _content_type_expectation(canonical_url, link, source_record)
            decision, skip_reason = _allow_or_skip(
                canonical_url=canonical_url,
                content_type=content_type,
                allowed_hosts=allowed_hosts,
                private_patterns=private_patterns,
                robots_decision=robots_by_url.get(canonical_url),
            )
            handoff = _processor_handoff_expectation(content_type, decision, skip_reason, source_record)

            candidates.append(
                FrontierCandidate(
                    canonical_url=canonical_url,
                    source_page=source_page,
                    link_text=_clean_link_text(str(link.get("text", ""))),
                    content_type_expectation=content_type,
                    allow_skip_decision=decision,
                    skip_reason=skip_reason,
                    processor_handoff_expectation=handoff,
                    reviewer_owner=reviewer_owner,
                    rollback_note=rollback_note,
                    offline_validation_commands=validation_commands,
                )
            )

    candidates.sort(key=lambda candidate: (candidate.allow_skip_decision, candidate.source_page, candidate.canonical_url))
    return candidates


def canonicalize_url(url: str) -> str:
    """Canonicalize a URL for metadata comparison without fetching it."""

    if not url:
        return ""
    parts = urlsplit(url.strip())
    if not parts.scheme or not parts.netloc:
        return url.strip()
    scheme = parts.scheme.lower()
    host = parts.hostname.lower() if parts.hostname else parts.netloc.lower()
    port = parts.port
    netloc = host
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        netloc = f"{host}:{port}"
    path = parts.path or "/"
    query_items = parse_qsl(parts.query, keep_blank_values=True)
    query = urlencode(sorted(query_items), doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))


def _allow_or_skip(
    *,
    canonical_url: str,
    content_type: str,
    allowed_hosts: set[str],
    private_patterns: tuple[str, ...],
    robots_decision: str | None,
) -> tuple[str, str]:
    parts = urlsplit(canonical_url)
    if parts.scheme.lower() not in SUPPORTED_SCHEMES:
        return "skip", "unsupported_scheme"
    host = (parts.hostname or "").lower()
    if host not in allowed_hosts:
        return "skip", "outside_allowlist"
    if any(pattern in parts.path for pattern in private_patterns):
        return "skip", "private_or_authenticated"
    if robots_decision == "disallow":
        return "skip", "disallowed_by_robots_or_policy"
    if content_type not in HTML_CONTENT_TYPES | PDF_CONTENT_TYPES:
        return "skip", "unsupported_content_type"
    return "allow", ""


def _processor_handoff_expectation(
    content_type: str,
    decision: str,
    skip_reason: str,
    source_record: dict[str, Any],
) -> str:
    if decision == "skip":
        return f"no_handoff:{skip_reason}"
    policy = str(source_record.get("processor_policy", "metadata_only_preflight"))
    if content_type in PDF_CONTENT_TYPES:
        return f"candidate_for_pdf_processor:{policy}"
    if content_type in HTML_CONTENT_TYPES:
        return f"candidate_for_html_processor:{policy}"
    return f"no_handoff:unsupported_content_type:{policy}"


def _content_type_expectation(url: str, link: dict[str, Any], source_record: dict[str, Any]) -> str:
    for value in (link.get("content_type_expectation"), source_record.get("content_type_expectation"), source_record.get("content_type")):
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    path = urlsplit(url).path.lower()
    if path.endswith(".pdf") or path.endswith("/download"):
        return "application/pdf"
    return "text/html"


def _robots_decisions(records: Any) -> dict[str, str]:
    decisions: dict[str, str] = {}
    if not isinstance(records, list):
        raise ValueError("robots_policy_preflight_fixtures_v1.decisions must be a list")
    for record in records:
        if not isinstance(record, dict):
            continue
        url = canonicalize_url(str(record.get("canonical_url", "")))
        decision = str(record.get("decision", "")).strip().lower()
        if url and decision:
            decisions[url] = decision
    return decisions


def _source_index(records: Any) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    if not isinstance(records, list):
        raise ValueError("source_index_records_v1.records must be a list")
    for record in records:
        if not isinstance(record, dict):
            continue
        url = canonicalize_url(str(record.get("canonical_url", "")))
        if url:
            index[url] = record
    return index


def _validation_commands(commands: Any) -> tuple[tuple[str, ...], ...]:
    if not isinstance(commands, list):
        raise ValueError("offline_validation_commands must be a list")
    normalized: list[tuple[str, ...]] = []
    for command in commands:
        if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
            raise ValueError("each offline validation command must be a list of strings")
        normalized.append(tuple(command))
    return tuple(normalized)


def _string_list(values: Iterable[Any]) -> list[str]:
    return [str(value).strip().lower() for value in values if str(value).strip()]


def _clean_link_text(text: str) -> str:
    return " ".join(text.split())
