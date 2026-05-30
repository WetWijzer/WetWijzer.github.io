"""Validation for public freshness reviewer handoff v1 packets.

The validator is intentionally fixture-first. It checks already-materialized
handoff rows and rejects private/authenticated references, raw body references,
live execution claims, outcome guarantees, and state mutation flags. It performs
no network I/O, crawler work, processor work, registry updates, or release-state
updates.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence
from urllib.parse import parse_qsl, urlparse


PACKET_TYPE = "ppd.public_freshness_reviewer_handoff.v1"
PACKET_VERSION = "1.0"

_REQUIRED_PACKET_FALSE_FLAGS = (
    "live_crawler_executed",
    "processor_completed",
    "registry_mutation_active",
    "guardrail_mutation_active",
    "monitoring_mutation_active",
    "release_state_mutation_active",
    "agent_state_mutation_active",
)
_REQUIRED_ROW_FIELDS = (
    "source_citations",
    "affected_ids",
    "reviewer_owner_fields",
    "skip_defer_rationale",
    "validation_evidence",
    "rollback_notes",
)
_AUTH_QUERY_KEYS = {
    "access_token",
    "auth",
    "auth_token",
    "code",
    "id_token",
    "jwt",
    "password",
    "session",
    "sessionid",
    "sid",
    "token",
}
_AUTH_PATH_MARKERS = (
    "/account",
    "/auth/",
    "/checkout",
    "/dashboard",
    "/login",
    "/my-permits",
    "/mypermits",
    "/oauth",
    "/payment",
    "/signin",
    "/sign-in",
)
_RAW_KEY_RE = re.compile(r"(^|_)(raw|body_ref|raw_body|raw_html|raw_pdf|warc_ref|har_ref|trace_ref|screenshot_ref)($|_)", re.IGNORECASE)
_RAW_TEXT_RE = re.compile(r"(raw[_ -]?(body|html|pdf|crawl)|body_ref|warc://|\.warc\b|\.har\b|trace\.zip|/raw/|raw-crawl|raw_crawl)", re.IGNORECASE)
_LIVE_CRAWLER_KEY_RE = re.compile(r"(live_?crawl|crawler_?(executed|completed|ran)|crawl_?(executed|completed|ran))", re.IGNORECASE)
_LIVE_CRAWLER_TEXT_RE = re.compile(r"\b(live crawl|crawler completed|crawler executed|ran the crawler|real crawl performed)\b", re.IGNORECASE)
_PROCESSOR_KEY_RE = re.compile(r"(processor_?(completed|executed|finished|ran)|process_?completion)", re.IGNORECASE)
_PROCESSOR_TEXT_RE = re.compile(r"\b(processor completed|processor executed|processor finished|ran the processor|processing completed)\b", re.IGNORECASE)
_GUARANTEE_TEXT_RE = re.compile(r"\b(guarantee[ds]?|will be approved|permit approved|approval guaranteed|legal outcome|legally sufficient|permitting outcome guaranteed)\b", re.IGNORECASE)
_MUTATION_KEY_RE = re.compile(r"(registry|guardrail|monitoring|release_?state|agent_?state).*?(mutation|mutate|update|write|active|enabled)", re.IGNORECASE)
_MUTATION_TEXT_RE = re.compile(r"\b(active|enabled|performed|mutated|updated) (registry|guardrail|monitoring|release-state|release state|agent-state|agent state)\b", re.IGNORECASE)
_AUTH_KEY_RE = re.compile(r"(authenticated|auth_url|session_url|private_url|token|credential|cookie|password|storage_state)", re.IGNORECASE)


@dataclass(frozen=True)
class PublicFreshnessReviewerHandoffIssue:
    code: str
    path: str
    message: str


class PublicFreshnessReviewerHandoffError(ValueError):
    """Raised when a public freshness reviewer handoff packet is invalid."""

    def __init__(self, issues: Sequence[PublicFreshnessReviewerHandoffIssue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(f"{issue.path}: {issue.code}: {issue.message}" for issue in self.issues)
        super().__init__(detail or "public freshness reviewer handoff packet is invalid")


def validate_public_freshness_reviewer_handoff_v1(packet: Mapping[str, Any]) -> list[PublicFreshnessReviewerHandoffIssue]:
    """Return validation issues for a public freshness reviewer handoff v1 packet."""

    issues: list[PublicFreshnessReviewerHandoffIssue] = []
    if not isinstance(packet, Mapping):
        return [PublicFreshnessReviewerHandoffIssue("invalid_packet", "$", "packet must be an object")]

    _scan_forbidden_content(packet, "$", issues)

    if packet.get("packet_type") != PACKET_TYPE:
        issues.append(PublicFreshnessReviewerHandoffIssue("invalid_packet_type", "$.packet_type", "packet_type must be ppd.public_freshness_reviewer_handoff.v1"))
    if packet.get("packet_version") != PACKET_VERSION:
        issues.append(PublicFreshnessReviewerHandoffIssue("invalid_packet_version", "$.packet_version", "packet_version must be 1.0"))
    if packet.get("fixture_first") is not True:
        issues.append(PublicFreshnessReviewerHandoffIssue("not_fixture_first", "$.fixture_first", "handoff must be fixture-first"))
    if packet.get("metadata_only") is not True:
        issues.append(PublicFreshnessReviewerHandoffIssue("not_metadata_only", "$.metadata_only", "handoff must be metadata-only"))
    for flag in _REQUIRED_PACKET_FALSE_FLAGS:
        if packet.get(flag) is not False:
            issues.append(PublicFreshnessReviewerHandoffIssue("unsafe_packet_flag", f"$.{flag}", "execution and mutation flags must be false"))

    rows = _handoff_rows(packet)
    if not rows:
        issues.append(PublicFreshnessReviewerHandoffIssue("missing_handoff_rows", "$.handoff_rows", "at least one handoff row is required"))
    for index, row in enumerate(rows):
        _validate_row(row, f"$.handoff_rows[{index}]", issues)

    return _dedupe_issues(issues)


def require_valid_public_freshness_reviewer_handoff_v1(packet: Mapping[str, Any]) -> None:
    """Raise when a public freshness reviewer handoff v1 packet is invalid."""

    issues = validate_public_freshness_reviewer_handoff_v1(packet)
    if issues:
        raise PublicFreshnessReviewerHandoffError(issues)


def _handoff_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = packet.get("handoff_rows", packet.get("rows"))
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, Mapping)]


def _validate_row(row: Mapping[str, Any], path: str, issues: list[PublicFreshnessReviewerHandoffIssue]) -> None:
    for field in _REQUIRED_ROW_FIELDS:
        if field not in row:
            issues.append(PublicFreshnessReviewerHandoffIssue("missing_required_row_field", f"{path}.{field}", "required reviewer handoff field is missing"))

    if not _string_list(row.get("source_citations") or row.get("citations") or row.get("source_evidence_ids")):
        issues.append(PublicFreshnessReviewerHandoffIssue("missing_source_citations", f"{path}.source_citations", "row must cite public source evidence"))
    if not _has_affected_ids(row.get("affected_ids")):
        issues.append(PublicFreshnessReviewerHandoffIssue("missing_affected_ids", f"{path}.affected_ids", "row must name affected source, requirement, guardrail, or process ids"))
    _validate_reviewer_owner_fields(row.get("reviewer_owner_fields"), f"{path}.reviewer_owner_fields", issues)
    if not _text(row.get("skip_defer_rationale")):
        issues.append(PublicFreshnessReviewerHandoffIssue("missing_skip_defer_rationale", f"{path}.skip_defer_rationale", "skip/defer rationale is required"))
    if not _has_validation_evidence(row.get("validation_evidence")):
        issues.append(PublicFreshnessReviewerHandoffIssue("missing_validation_evidence", f"{path}.validation_evidence", "validation evidence is required"))
    if not _has_rollback_notes(row.get("rollback_notes")):
        issues.append(PublicFreshnessReviewerHandoffIssue("missing_rollback_notes", f"{path}.rollback_notes", "rollback notes are required"))


def _validate_reviewer_owner_fields(value: Any, path: str, issues: list[PublicFreshnessReviewerHandoffIssue]) -> None:
    if not isinstance(value, Mapping):
        issues.append(PublicFreshnessReviewerHandoffIssue("missing_reviewer_owner_fields", path, "reviewer-owner fields must be an object"))
        return
    for key in ("reviewer_owner_id", "reviewer_role", "review_queue"):
        if not _text(value.get(key)):
            issues.append(PublicFreshnessReviewerHandoffIssue("missing_reviewer_owner_field", f"{path}.{key}", "reviewer-owner field is required"))


def _has_affected_ids(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_text(child) or _string_list(child) for child in value.values())
    return bool(_string_list(value))


def _has_validation_evidence(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for item in value:
        if isinstance(item, Mapping):
            if not (_text(item.get("evidence_id")) and (_text(item.get("summary")) or _text(item.get("check")) or _string_list(item.get("source_citations")))):
                return False
        elif not _text(item):
            return False
    return True


def _has_rollback_notes(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for item in value:
        if isinstance(item, Mapping):
            if not (_text(item.get("rollback_note_id")) and _text(item.get("reason"))):
                return False
        elif not _text(item):
            return False
    return True


def _scan_forbidden_content(value: Any, path: str, issues: list[PublicFreshnessReviewerHandoffIssue]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized_key = key_text.lower()
            if _AUTH_KEY_RE.search(key_text) and child not in (None, "", False, [], {}):
                issues.append(PublicFreshnessReviewerHandoffIssue("authenticated_reference", child_path, "authenticated URLs, credentials, cookies, and session references are not allowed"))
            if _RAW_KEY_RE.search(key_text) and child not in (None, "", False, [], {}):
                issues.append(PublicFreshnessReviewerHandoffIssue("raw_body_reference", child_path, "raw body, trace, HAR, screenshot, and WARC references are not allowed"))
            if _LIVE_CRAWLER_KEY_RE.search(key_text) and child not in (None, "", False, [], {}):
                issues.append(PublicFreshnessReviewerHandoffIssue("live_crawler_claim", child_path, "live crawler claims are not allowed"))
            if _PROCESSOR_KEY_RE.search(key_text) and child not in (None, "", False, [], {}):
                issues.append(PublicFreshnessReviewerHandoffIssue("processor_completion_claim", child_path, "processor completion claims are not allowed"))
            if _MUTATION_KEY_RE.search(key_text) and child not in (None, "", False, [], {}):
                issues.append(PublicFreshnessReviewerHandoffIssue("active_state_mutation", child_path, "registry, guardrail, monitoring, release-state, and agent-state mutations must be false or empty"))
            if normalized_key in {"source_type", "privacy_classification", "auth_scope"} and str(child).lower() in {"authenticated", "devhub_authenticated", "account_scoped", "private"}:
                issues.append(PublicFreshnessReviewerHandoffIssue("authenticated_reference", child_path, "handoff rows must remain public and unauthenticated"))
            _scan_forbidden_content(child, child_path, issues)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden_content(child, f"{path}[{index}]", issues)
    elif isinstance(value, str):
        _scan_forbidden_text(value, path, issues)


def _scan_forbidden_text(value: str, path: str, issues: list[PublicFreshnessReviewerHandoffIssue]) -> None:
    if _looks_authenticated_url(value):
        issues.append(PublicFreshnessReviewerHandoffIssue("authenticated_url", path, "authenticated URL references are not allowed"))
    if _RAW_TEXT_RE.search(value):
        issues.append(PublicFreshnessReviewerHandoffIssue("raw_body_reference", path, "raw body references are not allowed"))
    if _LIVE_CRAWLER_TEXT_RE.search(value):
        issues.append(PublicFreshnessReviewerHandoffIssue("live_crawler_claim", path, "live crawler claims are not allowed"))
    if _PROCESSOR_TEXT_RE.search(value):
        issues.append(PublicFreshnessReviewerHandoffIssue("processor_completion_claim", path, "processor completion claims are not allowed"))
    if _GUARANTEE_TEXT_RE.search(value):
        issues.append(PublicFreshnessReviewerHandoffIssue("legal_outcome_guarantee", path, "legal or permitting outcome guarantees are not allowed"))
    if _MUTATION_TEXT_RE.search(value):
        issues.append(PublicFreshnessReviewerHandoffIssue("active_state_mutation", path, "active state mutation claims are not allowed"))


def _looks_authenticated_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    if parsed.username or parsed.password:
        return True
    path = parsed.path.lower()
    if any(marker in path for marker in _AUTH_PATH_MARKERS):
        return True
    query_keys = {key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    return bool(query_keys.intersection(_AUTH_QUERY_KEYS))


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _dedupe_issues(issues: Sequence[PublicFreshnessReviewerHandoffIssue]) -> list[PublicFreshnessReviewerHandoffIssue]:
    seen: set[tuple[str, str, str]] = set()
    result: list[PublicFreshnessReviewerHandoffIssue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key not in seen:
            seen.add(key)
            result.append(issue)
    return result


__all__ = [
    "PACKET_TYPE",
    "PACKET_VERSION",
    "PublicFreshnessReviewerHandoffError",
    "PublicFreshnessReviewerHandoffIssue",
    "require_valid_public_freshness_reviewer_handoff_v1",
    "validate_public_freshness_reviewer_handoff_v1",
]
