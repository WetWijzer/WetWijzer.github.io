"""Validation for PP&D official source anchor audit packet v1.

The packet is intentionally metadata-only. It may cite official public source
anchors, but it must not carry raw bodies, downloaded files, private URLs,
completion claims, live execution claims, outcome guarantees, or mutation flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlparse

PACKET_VERSION = "official_source_anchor_audit_packet_v1"

OFFICIAL_HOST_ALLOWLIST = frozenset(
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

PRIVATE_QUERY_KEYS = frozenset(
    {
        "access_token",
        "auth",
        "auth_token",
        "code",
        "key",
        "password",
        "session",
        "sessionid",
        "sid",
        "state",
        "ticket",
        "token",
    }
)

PRIVATE_PATH_MARKERS = (
    "/account",
    "/admin",
    "/auth",
    "/login",
    "/logout",
    "/my",
    "/oauth",
    "/payment",
    "/private",
    "/register",
    "/session",
    "/signin",
    "/sign-in",
    "/user",
)

RAW_BODY_KEYS = frozenset(
    {
        "body",
        "content",
        "dom",
        "html",
        "markdown",
        "page_body",
        "raw_body",
        "raw_content",
        "raw_html",
        "text_body",
    }
)

DOWNLOADED_DOCUMENT_KEYS = frozenset(
    {
        "download_path",
        "downloaded_at",
        "downloaded_document",
        "downloaded_document_path",
        "downloaded_documents",
        "file_bytes",
        "local_document_path",
        "pdf_bytes",
        "saved_file",
        "saved_path",
    }
)

COMPLETION_CLAIM_KEYS = frozenset(
    {
        "archive_complete",
        "archive_completed",
        "archive_completion_claim",
        "archive_success",
        "processor_complete",
        "processor_completed",
        "processor_completion_claim",
        "processor_success",
    }
)

LIVE_EXECUTION_KEYS = frozenset(
    {
        "browser_session",
        "crawl_run_id",
        "executed_at",
        "live_crawl",
        "live_execution",
        "live_run",
        "network_capture",
        "playwright_trace",
        "session_state",
    }
)

MUTATION_FLAG_KEYS = frozenset(
    {
        "agent_state_mutated",
        "active_agent_state_mutation",
        "active_guardrail_mutation",
        "active_monitoring_mutation",
        "active_process_mutation",
        "active_release_state_mutation",
        "active_requirement_mutation",
        "active_source_mutation",
        "guardrail_mutated",
        "monitoring_mutated",
        "process_mutated",
        "release_state_mutated",
        "requirement_mutated",
        "source_mutated",
    }
)

GUARANTEE_TERMS = (
    "approval guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "guarantees approval",
    "guarantees permit",
    "legal guarantee",
    "permit will be approved",
    "permitting outcome guaranteed",
)


@dataclass(frozen=True)
class AuditValidationError:
    """A deterministic validation failure for an audit packet."""

    code: str
    message: str
    location: str


def validate_official_source_anchor_audit_packet_v1(
    packet: dict[str, Any],
) -> list[AuditValidationError]:
    """Return all validation errors for an official source anchor audit packet.

    The validator is side-effect free and does not fetch URLs. It only accepts
    packet metadata that can be committed safely and reviewed deterministically.
    """

    errors: list[AuditValidationError] = []

    if not isinstance(packet, dict):
        return [
            AuditValidationError(
                "packet_not_object",
                "audit packet must be a JSON object",
                "$",
            )
        ]

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append(
            AuditValidationError(
                "unsupported_packet_version",
                "packet_version must be official_source_anchor_audit_packet_v1",
                "$.packet_version",
            )
        )

    _require_non_empty_string(packet, "reviewer_owner", "missing_reviewer_owner", errors)
    _require_non_empty_string(packet, "rollback_note", "missing_rollback_note", errors)

    affected_source_ids = packet.get("affected_source_ids")
    if not _is_non_empty_string_list(affected_source_ids):
        errors.append(
            AuditValidationError(
                "missing_affected_source_ids",
                "affected_source_ids must list at least one source id",
                "$.affected_source_ids",
            )
        )

    anchors = packet.get("anchors")
    if not isinstance(anchors, list) or not anchors:
        errors.append(
            AuditValidationError(
                "missing_anchor_rows",
                "anchors must contain at least one anchor row",
                "$.anchors",
            )
        )
    elif all(isinstance(anchor, dict) for anchor in anchors):
        for index, anchor in enumerate(anchors):
            _validate_anchor_row(anchor, index, affected_source_ids, errors)
    else:
        errors.append(
            AuditValidationError(
                "invalid_anchor_rows",
                "every anchor row must be an object",
                "$.anchors",
            )
        )

    for location, key, value in _walk(packet):
        key_lower = key.lower()
        if key_lower in RAW_BODY_KEYS and _has_value(value):
            errors.append(
                AuditValidationError(
                    "raw_page_body_present",
                    "audit packet must not include raw page bodies or extracted full body text",
                    location,
                )
            )
        if key_lower in DOWNLOADED_DOCUMENT_KEYS and _has_value(value):
            errors.append(
                AuditValidationError(
                    "downloaded_document_present",
                    "audit packet must not include downloaded documents or local document paths",
                    location,
                )
            )
        if key_lower in COMPLETION_CLAIM_KEYS and _truthy(value):
            errors.append(
                AuditValidationError(
                    "processor_or_archive_completion_claim",
                    "audit packet must not claim processor or archive completion",
                    location,
                )
            )
        if key_lower in LIVE_EXECUTION_KEYS and _truthy(value):
            errors.append(
                AuditValidationError(
                    "live_execution_claim",
                    "audit packet must not claim or carry live execution state",
                    location,
                )
            )
        if key_lower in MUTATION_FLAG_KEYS and _truthy(value):
            errors.append(
                AuditValidationError(
                    "active_mutation_flag",
                    "audit packet must not set active source, requirement, process, guardrail, monitoring, release-state, or agent-state mutation flags",
                    location,
                )
            )
        if isinstance(value, str) and _contains_outcome_guarantee(value):
            errors.append(
                AuditValidationError(
                    "outcome_guarantee_claim",
                    "audit packet must not include legal or permitting outcome guarantees",
                    location,
                )
            )

    return errors


def is_valid_official_source_anchor_audit_packet_v1(packet: dict[str, Any]) -> bool:
    """Return True when the packet has no validation errors."""

    return not validate_official_source_anchor_audit_packet_v1(packet)


def _validate_anchor_row(
    anchor: dict[str, Any],
    index: int,
    affected_source_ids: Any,
    errors: list[AuditValidationError],
) -> None:
    location = f"$.anchors[{index}]"

    source_id = anchor.get("source_id")
    if not isinstance(source_id, str) or not source_id.strip():
        errors.append(
            AuditValidationError(
                "missing_anchor_source_id",
                "each anchor row must include source_id",
                f"{location}.source_id",
            )
        )
    elif _is_non_empty_string_list(affected_source_ids) and source_id not in affected_source_ids:
        errors.append(
            AuditValidationError(
                "anchor_source_not_affected",
                "anchor source_id must be listed in affected_source_ids",
                f"{location}.source_id",
            )
        )

    citation_ids = anchor.get("citation_ids", anchor.get("source_evidence_ids"))
    if not _is_non_empty_string_list(citation_ids):
        errors.append(
            AuditValidationError(
                "uncited_anchor_row",
                "each anchor row must include at least one citation id",
                f"{location}.citation_ids",
            )
        )

    url = anchor.get("url") or anchor.get("canonical_url")
    if not isinstance(url, str) or not url.strip():
        errors.append(
            AuditValidationError(
                "missing_anchor_url",
                "each anchor row must include url or canonical_url",
                f"{location}.url",
            )
        )
        return

    url_errors = _validate_official_public_url(url, f"{location}.url")
    errors.extend(url_errors)


def _validate_official_public_url(url: str, location: str) -> list[AuditValidationError]:
    errors: list[AuditValidationError] = []
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    if parsed.scheme != "https":
        errors.append(
            AuditValidationError(
                "non_https_url",
                "official source anchor URLs must use https",
                location,
            )
        )

    if host not in OFFICIAL_HOST_ALLOWLIST:
        errors.append(
            AuditValidationError(
                "non_official_or_non_allowlisted_url",
                "official source anchor URL host is not allowlisted",
                location,
            )
        )

    path = parsed.path.lower().rstrip("/")
    if any(path == marker or path.startswith(marker + "/") for marker in PRIVATE_PATH_MARKERS):
        errors.append(
            AuditValidationError(
                "authenticated_or_private_url",
                "official source anchor URL appears to target an authenticated or private surface",
                location,
            )
        )

    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & PRIVATE_QUERY_KEYS:
        errors.append(
            AuditValidationError(
                "authenticated_or_private_url",
                "official source anchor URL includes authentication or session-like query parameters",
                location,
            )
        )

    return errors


def _require_non_empty_string(
    packet: dict[str, Any],
    key: str,
    code: str,
    errors: list[AuditValidationError],
) -> None:
    value = packet.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(
            AuditValidationError(
                code,
                f"{key} must be a non-empty string",
                f"$.{key}",
            )
        )


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            yield child_path, key_text, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _is_non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"", "false", "no", "none", "0"}
    return bool(value)


def _contains_outcome_guarantee(value: str) -> bool:
    normalized = " ".join(value.lower().split())
    return any(term in normalized for term in GUARANTEE_TERMS)
