"""Validation for PP&D public source refresh reviewer queue v1.

The queue is a commit-safe review surface. Items may identify public sources that
need review, explain why they should be deferred or rolled back, and name affected
models. They must not carry raw crawl output, downloaded artifacts, authenticated
URLs, completion claims, outcome guarantees, or mutation instructions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlparse


ALLOWLISTED_HOSTS = frozenset(
    {
        "www.portland.gov",
        "portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "portlandoregon.gov",
        "www.portlandmaps.com",
        "portlandmaps.com",
    }
)

AUTHENTICATED_PATH_MARKERS = (
    "/login",
    "/logout",
    "/signin",
    "/sign-in",
    "/sign_in",
    "/register",
    "/account",
    "/accounts",
    "/my-permits",
    "/mypermits",
    "/dashboard",
    "/user/",
    "/users/",
    "/profile",
    "/session",
    "/sessions",
    "/oauth",
    "/saml",
    "/auth",
)

AUTHENTICATED_QUERY_KEYS = frozenset(
    {
        "access_token",
        "auth",
        "code",
        "id_token",
        "key",
        "password",
        "refresh_token",
        "session",
        "sid",
        "signature",
        "sso",
        "state",
        "ticket",
        "token",
    }
)

RAW_BODY_KEYS = frozenset(
    {
        "body",
        "body_html",
        "body_text",
        "content",
        "content_html",
        "content_text",
        "dom",
        "html",
        "markdown",
        "page_body",
        "page_html",
        "page_text",
        "raw",
        "raw_body",
        "raw_content",
        "raw_html",
        "raw_markdown",
        "raw_page",
        "raw_text",
        "response_body",
        "text",
    }
)

DOWNLOADED_DOCUMENT_KEYS = frozenset(
    {
        "attachment_bytes",
        "attachment_path",
        "attachments",
        "base64_document",
        "blob",
        "document_bytes",
        "document_path",
        "download",
        "download_path",
        "downloaded_document",
        "downloaded_documents",
        "file_bytes",
        "file_path",
        "local_document",
        "local_path",
        "pdf_bytes",
        "pdf_path",
        "saved_file",
        "tmp_path",
        "warc_path",
    }
)

COMPLETION_CLAIM_KEYS = frozenset(
    {
        "archive_complete",
        "archive_completed",
        "archive_completion_claim",
        "archived",
        "completed",
        "completion_claim",
        "extraction_complete",
        "processor_complete",
        "processor_completed",
        "processor_completion_claim",
        "refresh_complete",
        "refresh_completed",
    }
)

MUTATION_FLAG_KEYS = frozenset(
    {
        "agent_state_mutation",
        "agent_state_mutation_enabled",
        "apply_guardrail_changes",
        "apply_monitoring_changes",
        "apply_process_changes",
        "apply_release_state_changes",
        "apply_requirement_changes",
        "apply_source_changes",
        "commit_agent_state",
        "commit_guardrails",
        "commit_monitoring",
        "commit_processes",
        "commit_release_state",
        "commit_requirements",
        "commit_sources",
        "guardrail_mutation",
        "guardrail_mutation_enabled",
        "monitoring_mutation",
        "monitoring_mutation_enabled",
        "mutate_agent_state",
        "mutate_guardrails",
        "mutate_monitoring",
        "mutate_processes",
        "mutate_release_state",
        "mutate_requirements",
        "mutate_sources",
        "process_mutation",
        "process_mutation_enabled",
        "release_state_mutation",
        "release_state_mutation_enabled",
        "requirement_mutation",
        "requirement_mutation_enabled",
        "source_mutation",
        "source_mutation_enabled",
        "update_agent_state",
        "update_guardrails",
        "update_monitoring",
        "update_processes",
        "update_release_state",
        "update_requirements",
        "update_sources",
    }
)

OUTCOME_GUARANTEE_PHRASES = (
    "guarantee approval",
    "guarantee permit",
    "guaranteed approval",
    "guaranteed issuance",
    "guarantees approval",
    "guarantees permit",
    "legally compliant",
    "legal compliance guaranteed",
    "permit approval guaranteed",
    "permit will be approved",
    "permit will be issued",
    "will be approved",
    "will be issued",
    "will pass inspection",
    "will satisfy code",
)


@dataclass(frozen=True)
class QueueValidationIssue:
    """A deterministic validation issue for a queue item."""

    code: str
    path: str
    message: str


class QueueValidationError(ValueError):
    """Raised when callers request exception-based queue validation."""

    def __init__(self, issues: Iterable[QueueValidationIssue]) -> None:
        self.issues = tuple(issues)
        joined = "; ".join(f"{issue.path}: {issue.code}" for issue in self.issues)
        super().__init__(joined)


def validate_public_source_refresh_reviewer_queue_v1(payload: Any) -> list[QueueValidationIssue]:
    """Return validation issues for a reviewer queue payload.

    Accepted payload shapes are either a single queue item dict, a list of queue
    item dicts, or a dict containing an ``items`` list. Validation is intentionally
    conservative because this queue is commit-safe review metadata, not a crawl
    artifact store or mutating operations ledger.
    """

    issues: list[QueueValidationIssue] = []
    items = _coerce_items(payload, issues)
    for index, item in enumerate(items):
        path = f"items[{index}]"
        if not isinstance(item, dict):
            issues.append(QueueValidationIssue("item_not_object", path, "Queue item must be an object."))
            continue
        _validate_item(item, path, issues)
    return issues


def assert_valid_public_source_refresh_reviewer_queue_v1(payload: Any) -> None:
    """Raise ``QueueValidationError`` when the payload is invalid."""

    issues = validate_public_source_refresh_reviewer_queue_v1(payload)
    if issues:
        raise QueueValidationError(issues)


def _coerce_items(payload: Any, issues: list[QueueValidationIssue]) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if "items" in payload:
            items = payload["items"]
            if isinstance(items, list):
                return items
            issues.append(QueueValidationIssue("items_not_list", "items", "Queue items must be a list."))
            return []
        return [payload]
    issues.append(QueueValidationIssue("payload_not_object_or_list", "$", "Queue payload must be an object or list."))
    return []


def _validate_item(item: dict[str, Any], path: str, issues: list[QueueValidationIssue]) -> None:
    if not _has_citation(item):
        issues.append(QueueValidationIssue("missing_citation", path, "Queue item must include at least one public source citation."))

    affected_ids = item.get("affected_ids")
    if not _is_nonempty_string_list(affected_ids):
        issues.append(QueueValidationIssue("missing_affected_ids", f"{path}.affected_ids", "Queue item must name affected source, requirement, process, or guardrail IDs."))

    if not (_nonempty_string(item.get("defer_rationale")) or _nonempty_string(item.get("rollback_rationale"))):
        issues.append(QueueValidationIssue("missing_defer_or_rollback_rationale", path, "Queue item must include defer_rationale or rollback_rationale."))

    for key_path, key, value in _walk(item, path):
        normalized_key = key.lower() if key else ""
        if normalized_key in RAW_BODY_KEYS:
            issues.append(QueueValidationIssue("raw_page_body_present", key_path, "Queue item must not include raw page bodies."))
        if normalized_key in DOWNLOADED_DOCUMENT_KEYS:
            issues.append(QueueValidationIssue("downloaded_document_present", key_path, "Queue item must not include downloaded documents or local document paths."))
        if normalized_key in COMPLETION_CLAIM_KEYS and _truthy_claim(value):
            issues.append(QueueValidationIssue("processor_or_archive_completion_claim", key_path, "Queue item must not claim processor or archive completion."))
        if normalized_key in MUTATION_FLAG_KEYS and _truthy_claim(value):
            issues.append(QueueValidationIssue("active_mutation_flag", key_path, "Queue item must not enable source, requirement, process, guardrail, monitoring, release-state, or agent-state mutation."))
        if normalized_key in {"status", "state"} and isinstance(value, str) and value.strip().lower() in {"complete", "completed", "archived", "processed", "released"}:
            issues.append(QueueValidationIssue("processor_or_archive_completion_claim", key_path, "Queue item status must not claim completion."))
        if _looks_like_url_value(normalized_key, value):
            _validate_url(str(value), key_path, issues)
        if isinstance(value, str) and _contains_outcome_guarantee(value):
            issues.append(QueueValidationIssue("outcome_guarantee", key_path, "Queue item must not guarantee legal or permitting outcomes."))


def _has_citation(item: dict[str, Any]) -> bool:
    citations = item.get("citations", item.get("source_citations", item.get("source_evidence")))
    if not isinstance(citations, list) or not citations:
        return False
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        source_id = citation.get("source_id") or citation.get("id")
        url = citation.get("url") or citation.get("canonical_url")
        if _nonempty_string(source_id) and _nonempty_string(url):
            return True
    return False


def _validate_url(url: str, path: str, issues: list[QueueValidationIssue]) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in ALLOWLISTED_HOSTS:
        issues.append(QueueValidationIssue("url_not_allowlisted", path, "Queue item URL must be HTTPS and on the PP&D public-source allowlist."))
        return
    lowered_path = parsed.path.lower()
    if any(marker in lowered_path for marker in AUTHENTICATED_PATH_MARKERS):
        issues.append(QueueValidationIssue("authenticated_url", path, "Queue item URL must not target authenticated or account-scoped surfaces."))
    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & AUTHENTICATED_QUERY_KEYS:
        issues.append(QueueValidationIssue("authenticated_url", path, "Queue item URL must not include auth, token, session, or SSO query parameters."))


def _walk(value: Any, path: str) -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            yield child_path, key_text, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, "", child
            yield from _walk(child, child_path)


def _looks_like_url_value(key: str, value: Any) -> bool:
    if not isinstance(value, str):
        return False
    stripped = value.strip().lower()
    if stripped.startswith("http://") or stripped.startswith("https://"):
        return True
    return key.endswith("url") or key in {"url", "canonical_url", "requested_url", "source_url"}


def _contains_outcome_guarantee(value: str) -> bool:
    lowered = " ".join(value.lower().split())
    return any(phrase in lowered for phrase in OUTCOME_GUARANTEE_PHRASES)


def _truthy_claim(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"", "false", "no", "none", "not_applicable", "n/a"}
    return value is not None


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_nonempty_string(item) for item in value)
