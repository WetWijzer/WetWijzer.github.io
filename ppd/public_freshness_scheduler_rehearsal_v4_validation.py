"""Safety validation for public freshness scheduler rehearsal v4 packets.

The validator is fixture-first and side-effect free. It rejects scheduler
rehearsal rows that would imply uncited scheduling, authenticated access, raw
artifact persistence, live crawler or processor completion, outcome guarantees,
or active state mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

ALLOWED_PUBLIC_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)

AUTHENTICATED_URL_MARKERS = (
    "/account",
    "/accounts",
    "/auth",
    "/dashboard",
    "/login",
    "/logout",
    "/my-permits",
    "/oauth",
    "/permitcart",
    "/profile",
    "/register",
    "/session",
    "/signin",
    "/sign-in",
    "/user",
)

RAW_ARTIFACT_MARKERS = (
    "raw_body",
    "body_html",
    "body_text",
    "download_path",
    "download_url",
    "downloaded_document",
    "archive_path",
    "archive_url",
    "warc_path",
    "browser_artifact",
    "browser_trace",
    "trace_path",
    "har_path",
    "screenshot_path",
    "storage_state",
    "cookie_jar",
)

COMPLETION_CLAIM_MARKERS = (
    "crawler_completed",
    "crawl_completed",
    "processor_completed",
    "processing_completed",
    "extraction_completed",
    "archive_completed",
    "live_crawl_completed",
    "processor_run_completed",
)

OUTCOME_GUARANTEE_MARKERS = (
    "approval_guaranteed",
    "permit_guaranteed",
    "issuance_guaranteed",
    "inspection_pass_guaranteed",
    "legal_compliance_guaranteed",
    "guarantees_approval",
    "guarantees_permit",
    "guaranteed_outcome",
)

ACTIVE_MUTATION_MARKERS = (
    "active_source_mutation",
    "active_schedule_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "mutates_sources",
    "mutates_schedule",
    "mutates_requirements",
    "mutates_processes",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_monitoring",
    "mutates_release_state",
    "mutates_agent_state",
)


@dataclass(frozen=True)
class SchedulerRehearsalSafetyError:
    row: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"row": self.row, "code": self.code, "message": self.message}


class SchedulerRehearsalSafetyValidationError(ValueError):
    """Raised when scheduler rehearsal safety validation fails."""

    def __init__(self, errors: Iterable[SchedulerRehearsalSafetyError]) -> None:
        self.errors = tuple(errors)
        detail = "; ".join(f"{error.row}:{error.code}" for error in self.errors)
        super().__init__(f"invalid public freshness scheduler rehearsal v4: {detail}")


def validate_public_freshness_scheduler_rehearsal_v4_safety(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Return a serializable safety validation result for a rehearsal packet."""

    errors: list[SchedulerRehearsalSafetyError] = []
    if packet.get("schema") != "ppd.public_freshness_scheduler_rehearsal.v4":
        errors.append(SchedulerRehearsalSafetyError("packet", "unsupported_schema", "packet must declare scheduler rehearsal v4 schema"))

    candidates = packet.get("cited_metadata_only_recrawl_schedule_candidates")
    if not isinstance(candidates, list):
        errors.append(SchedulerRehearsalSafetyError("packet", "missing_schedule_candidates", "packet must include schedule candidates"))
        candidates = []
    for index, row in enumerate(candidates):
        _validate_row(row, f"schedule_candidates[{index}]", False, errors)

    skip_defer_rows = packet.get("skip_defer_reasons")
    if not isinstance(skip_defer_rows, list):
        errors.append(SchedulerRehearsalSafetyError("packet", "missing_skip_defer_reasons", "packet must include skip/defer rows"))
        skip_defer_rows = []
    for index, row in enumerate(skip_defer_rows):
        _validate_row(row, f"skip_defer_reasons[{index}]", True, errors)

    _reject_markers(packet, RAW_ARTIFACT_MARKERS, "raw_or_browser_artifact", errors)
    _reject_markers(packet, COMPLETION_CLAIM_MARKERS, "live_completion_claim", errors)
    _reject_markers(packet, OUTCOME_GUARANTEE_MARKERS, "outcome_guarantee", errors)
    _reject_markers(packet, ACTIVE_MUTATION_MARKERS, "active_mutation_flag", errors)

    return {"ok": not errors, "errors": [error.as_dict() for error in errors]}


def require_public_freshness_scheduler_rehearsal_v4_safety(packet: Mapping[str, Any]) -> None:
    """Raise when a public freshness scheduler rehearsal v4 packet is unsafe."""

    result = validate_public_freshness_scheduler_rehearsal_v4_safety(packet)
    if not result["ok"]:
        raise SchedulerRehearsalSafetyValidationError(
            SchedulerRehearsalSafetyError(error["row"], error["code"], error["message"])
            for error in result["errors"]
        )


def _validate_row(row: Any, fallback_name: str, skip_or_defer: bool, errors: list[SchedulerRehearsalSafetyError]) -> None:
    if not isinstance(row, Mapping):
        errors.append(SchedulerRehearsalSafetyError(fallback_name, "invalid_row", "schedule row must be an object"))
        return

    row_name = str(row.get("source_id") or row.get("schedule_id") or fallback_name)
    if not _has_citations(row.get("citations")):
        errors.append(SchedulerRehearsalSafetyError(row_name, "missing_citations", "schedule row must include citations"))
    if not _non_empty_string_list(row.get("affected_source_ids")):
        errors.append(SchedulerRehearsalSafetyError(row_name, "missing_affected_source", "schedule row must identify affected source IDs"))
    if not _non_empty_string_list(row.get("affected_requirement_ids")):
        errors.append(SchedulerRehearsalSafetyError(row_name, "missing_affected_requirement", "schedule row must identify affected requirement IDs"))
    if skip_or_defer and not _non_empty_string(row.get("reason") or row.get("skip_rationale") or row.get("defer_rationale")):
        errors.append(SchedulerRehearsalSafetyError(row_name, "missing_skip_defer_rationale", "skip/defer rows must include rationale"))

    url = _row_url(row)
    if url:
        _validate_url(url, row, row_name, errors)
    elif not skip_or_defer:
        errors.append(SchedulerRehearsalSafetyError(row_name, "missing_url", "schedule candidates must include a public metadata URL"))


def _row_url(row: Mapping[str, Any]) -> str:
    for key in ("canonical_url", "url", "public_url"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    metadata = row.get("metadata_fields")
    if isinstance(metadata, Mapping):
        for key in ("canonical_url", "url", "public_url"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _validate_url(url: str, row: Mapping[str, Any], row_name: str, errors: list[SchedulerRehearsalSafetyError]) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    path = parsed.path.lower()
    if parsed.scheme != "https" or host not in ALLOWED_PUBLIC_HOSTS:
        errors.append(SchedulerRehearsalSafetyError(row_name, "non_allowlisted_url", "URL must be HTTPS and public-allowlisted"))

    auth_scope = str(row.get("auth_scope", row.get("privacy_classification", ""))).lower()
    if row.get("requires_auth") is True or row.get("authenticated") is True or "authenticated" in auth_scope or any(marker in path for marker in AUTHENTICATED_URL_MARKERS):
        errors.append(SchedulerRehearsalSafetyError(row_name, "authenticated_url", "URL must not be authenticated or account scoped"))


def _reject_markers(value: Any, markers: Iterable[str], code: str, errors: list[SchedulerRehearsalSafetyError]) -> None:
    marker_set = set(markers)
    for path, found in _walk(value):
        key = path.rsplit(".", 1)[-1].lower()
        if key in marker_set:
            errors.append(SchedulerRehearsalSafetyError("packet", code, f"prohibited field {path}"))
            continue
        if isinstance(found, str):
            normalized = found.strip().lower().replace("-", "_").replace(" ", "_")
            if normalized in marker_set:
                errors.append(SchedulerRehearsalSafetyError("packet", code, f"prohibited marker {found}"))


def _walk(value: Any, prefix: str = "packet") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}"
            yield child_prefix, child
            yield from _walk(child, child_prefix)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[{index}]"
            yield child_prefix, child
            yield from _walk(child, child_prefix)


def _has_citations(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    return any(isinstance(item, str) and item.strip() for item in value) or any(isinstance(item, Mapping) and item for item in value)


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
