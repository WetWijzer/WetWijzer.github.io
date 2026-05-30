"""Fixture-first public freshness reviewer handoff v1.

This module converts scheduler rehearsal v4 fixtures and their validation
outcomes into reviewer-owned handoff rows. It is deliberately metadata-only: it
never recrawls, downloads documents, invokes processors, or mutates the source
registry or live monitoring schedule.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

PACKET_TYPE = "ppd.public_freshness_reviewer_handoff.v1"
MODE = "fixture_first_public_freshness_reviewer_handoff"
SCHEDULER_SCHEMA = "ppd.public_freshness_scheduler_rehearsal.v4"

_ALLOWED_PUBLIC_HOSTS = {
    "www.portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "www.portlandmaps.com",
}

_FORBIDDEN_KEYS = {
    "archive_path",
    "auth_state",
    "body_html",
    "body_text",
    "browser_trace",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "download_path",
    "download_url",
    "downloaded_document",
    "har_path",
    "local_path",
    "password",
    "raw_body",
    "raw_content",
    "raw_html",
    "screenshot_path",
    "session_state",
    "storage_state",
    "trace_path",
    "warc_path",
}

_FORBIDDEN_TRUE_KEYS = {
    "active_registry_mutation",
    "active_schedule_mutation",
    "download_documents",
    "fetch_urls",
    "live_network_invoked",
    "network_allowed",
    "network_invoked",
    "processor_invoked",
    "recrawl_invoked",
    "registry_mutated",
    "schedule_mutated",
    "source_registry_mutation_allowed",
}

_PRIVATE_PATH_MARKERS = (
    "/account",
    "/admin",
    "/auth",
    "/dashboard",
    "/login",
    "/my-permits",
    "/oauth",
    "/payment",
    "/permitcart",
    "/profile",
    "/session",
    "/signin",
    "/sign-in",
    "/upload",
)
_PRIVATE_QUERY_MARKERS = ("access_token=", "auth=", "password=", "session=", "token=")


@dataclass(frozen=True)
class PublicFreshnessReviewerHandoffValidationResult:
    """Validation result for public freshness reviewer handoff packets."""

    valid: bool
    errors: tuple[str, ...]


def build_public_freshness_reviewer_handoff_v1(
    scheduler_rehearsal_v4_packet: Mapping[str, Any],
    scheduler_validation_outcome: Mapping[str, Any],
    *,
    generated_at: str,
) -> dict[str, Any]:
    """Build a cited, review-only handoff from scheduler rehearsal fixtures."""

    rows: list[dict[str, Any]] = []
    validation_errors = _validation_errors_by_row(scheduler_validation_outcome)

    for index, candidate in enumerate(_mapping_list(scheduler_rehearsal_v4_packet.get("cited_metadata_only_recrawl_schedule_candidates"))):
        rows.append(_review_row(candidate, index, "schedule_candidate", validation_errors))

    offset = len(rows)
    for index, deferred in enumerate(_mapping_list(scheduler_rehearsal_v4_packet.get("skip_defer_reasons"))):
        rows.append(_review_row(deferred, offset + index, "skip_or_defer", validation_errors))

    packet = {
        "packet_type": PACKET_TYPE,
        "mode": MODE,
        "generated_at": generated_at,
        "fixture_first": True,
        "metadata_only": True,
        "input_artifacts": {
            "scheduler_rehearsal_schema": _text(scheduler_rehearsal_v4_packet.get("schema")),
            "scheduler_validation_ok": scheduler_validation_outcome.get("ok") is True,
        },
        "execution_policy": {
            "network_allowed": False,
            "network_invoked": False,
            "fetch_urls": False,
            "recrawl_invoked": False,
            "download_documents": False,
            "processor_invoked": False,
            "source_registry_mutation_allowed": False,
            "registry_mutated": False,
            "schedule_mutated": False,
        },
        "reviewer_handoff_rows": rows,
        "source_ids": sorted({source_id for row in rows for source_id in row["source_ids"]}),
        "affected_requirement_ids": sorted({item for row in rows for item in row["affected_requirement_ids"]}),
        "affected_process_ids": sorted({item for row in rows for item in row["affected_process_ids"]}),
        "attestation_summary": {
            "no_recrawl": True,
            "no_download": True,
            "no_processor": True,
            "no_registry_mutation": True,
            "no_schedule_mutation": True,
            "reviewer_approval_required_before_live_use": True,
        },
    }

    result = validate_public_freshness_reviewer_handoff_v1(packet)
    if not result.valid:
        raise ValueError("invalid public freshness reviewer handoff v1: " + "; ".join(result.errors))
    return packet


def validate_public_freshness_reviewer_handoff_v1(packet: Mapping[str, Any]) -> PublicFreshnessReviewerHandoffValidationResult:
    """Validate a handoff packet without side effects."""

    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be " + PACKET_TYPE)
    if packet.get("mode") != MODE:
        errors.append("mode must be " + MODE)
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        errors.append("metadata_only must be true")

    input_artifacts = _mapping(packet.get("input_artifacts"))
    if input_artifacts.get("scheduler_rehearsal_schema") != SCHEDULER_SCHEMA:
        errors.append("input_artifacts.scheduler_rehearsal_schema must be scheduler rehearsal v4")

    policy = _mapping(packet.get("execution_policy"))
    for key in (
        "network_allowed",
        "network_invoked",
        "fetch_urls",
        "recrawl_invoked",
        "download_documents",
        "processor_invoked",
        "source_registry_mutation_allowed",
        "registry_mutated",
        "schedule_mutated",
    ):
        if policy.get(key) is not False:
            errors.append(f"execution_policy.{key} must be false")

    rows = packet.get("reviewer_handoff_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("reviewer_handoff_rows must be a non-empty list")
    else:
        for index, row in enumerate(rows):
            _validate_row(row, index, errors)

    summary = _mapping(packet.get("attestation_summary"))
    for key in (
        "no_recrawl",
        "no_download",
        "no_processor",
        "no_registry_mutation",
        "no_schedule_mutation",
        "reviewer_approval_required_before_live_use",
    ):
        if summary.get(key) is not True:
            errors.append(f"attestation_summary.{key} must be true")

    if not _string_list(packet.get("source_ids")):
        errors.append("source_ids must be non-empty")
    if not _string_list(packet.get("affected_requirement_ids")) and not _string_list(packet.get("affected_process_ids")):
        errors.append("affected_requirement_ids or affected_process_ids must be non-empty")

    _validate_no_forbidden_fields(packet, "$", errors)
    return PublicFreshnessReviewerHandoffValidationResult(valid=not errors, errors=tuple(errors))


def _review_row(row: Mapping[str, Any], index: int, row_kind: str, validation_errors: Mapping[str, list[Mapping[str, Any]]]) -> dict[str, Any]:
    source_ids = _string_list(row.get("affected_source_ids")) or _string_list(row.get("source_ids"))
    primary_source_id = _text(row.get("source_id")) or (source_ids[0] if source_ids else f"unknown-source-{index + 1}")
    if primary_source_id not in source_ids:
        source_ids = [primary_source_id, *source_ids]

    affected_requirement_ids = _string_list(row.get("affected_requirement_ids"))
    affected_process_ids = _string_list(row.get("affected_process_ids"))
    row_errors = validation_errors.get(primary_source_id, []) + validation_errors.get(_text(row.get("schedule_id")), [])
    citations = _citations(row.get("citations"), primary_source_id)
    stale_or_defer_reasons = _stale_or_defer_reasons(row, row_errors, row_kind)

    return {
        "review_row_id": "public-freshness-review-row-" + _slug(primary_source_id),
        "row_kind": row_kind,
        "schedule_candidate_id": _text(row.get("schedule_id"), "schedule-candidate-" + _slug(primary_source_id)),
        "primary_source_id": primary_source_id,
        "source_ids": sorted(set(source_ids)),
        "canonical_url": _safe_public_url(row),
        "citations": citations,
        "citation_ids": [citation["citation_id"] for citation in citations],
        "affected_requirement_ids": sorted(set(affected_requirement_ids)),
        "affected_process_ids": sorted(set(affected_process_ids)),
        "reviewer_owner": _text(row.get("reviewer_owner"), "ppd-public-freshness-reviewer"),
        "review_status": "human_review_required",
        "stale_or_defer_reasons": stale_or_defer_reasons,
        "proposed_offline_checks": _offline_checks(row, row_errors),
        "validation_outcome": {
            "scheduler_validation_ok": not row_errors,
            "related_error_codes": sorted({_text(error.get("code")) for error in row_errors if _text(error.get("code"))}),
        },
        "attestations": {
            "no_recrawl": True,
            "no_download": True,
            "no_processor": True,
            "no_registry_mutation": True,
            "no_schedule_mutation": True,
            "fixture_first": True,
            "metadata_only": True,
        },
    }


def _validate_row(value: Any, index: int, errors: list[str]) -> None:
    prefix = f"reviewer_handoff_rows[{index}]"
    if not isinstance(value, Mapping):
        errors.append(prefix + " must be an object")
        return
    if value.get("row_kind") not in {"schedule_candidate", "skip_or_defer"}:
        errors.append(prefix + ".row_kind is invalid")
    if not _text(value.get("review_row_id")):
        errors.append(prefix + ".review_row_id is required")
    if not _text(value.get("primary_source_id")):
        errors.append(prefix + ".primary_source_id is required")
    if not _string_list(value.get("source_ids")):
        errors.append(prefix + ".source_ids must be non-empty")
    if not _citations(value.get("citations"), _text(value.get("primary_source_id"))):
        errors.append(prefix + ".citations must be non-empty")
    if not _string_list(value.get("affected_requirement_ids")) and not _string_list(value.get("affected_process_ids")):
        errors.append(prefix + ".affected_requirement_ids or affected_process_ids must be non-empty")
    if not _text(value.get("reviewer_owner")):
        errors.append(prefix + ".reviewer_owner is required")
    if value.get("review_status") != "human_review_required":
        errors.append(prefix + ".review_status must be human_review_required")
    if not isinstance(value.get("stale_or_defer_reasons"), list) or not value.get("stale_or_defer_reasons"):
        errors.append(prefix + ".stale_or_defer_reasons must be non-empty")
    if not _string_list(value.get("proposed_offline_checks")):
        errors.append(prefix + ".proposed_offline_checks must be non-empty")

    attestations = _mapping(value.get("attestations"))
    for key in ("no_recrawl", "no_download", "no_processor", "no_registry_mutation", "no_schedule_mutation", "fixture_first", "metadata_only"):
        if attestations.get(key) is not True:
            errors.append(prefix + f".attestations.{key} must be true")

    canonical_url = _text(value.get("canonical_url"))
    if canonical_url and not _is_safe_public_url(canonical_url):
        errors.append(prefix + ".canonical_url must be public allowlisted metadata URL")


def _validation_errors_by_row(outcome: Mapping[str, Any]) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    errors = outcome.get("errors")
    if not isinstance(errors, list):
        return grouped
    for error in errors:
        if not isinstance(error, Mapping):
            continue
        row_name = _text(error.get("row"), "packet")
        grouped.setdefault(row_name, []).append(error)
    return grouped


def _stale_or_defer_reasons(row: Mapping[str, Any], validation_errors: list[Mapping[str, Any]], row_kind: str) -> list[dict[str, str]]:
    reasons: list[dict[str, str]] = []
    reason_text = _text(row.get("reason")) or _text(row.get("defer_rationale")) or _text(row.get("skip_rationale")) or _text(row.get("stale_reason"))
    if reason_text:
        reasons.append({"reason_id": "source-row-reason-" + _slug(reason_text)[:48], "reason": reason_text})
    elif row_kind == "schedule_candidate":
        reasons.append(
            {
                "reason_id": "candidate-requires-human-freshness-review",
                "reason": "Scheduler rehearsal candidate must be reviewed before any live recrawl or registry schedule change.",
            }
        )

    for error in validation_errors:
        code = _text(error.get("code"), "scheduler-validation-error")
        message = _text(error.get("message"), "Scheduler rehearsal validation reported an issue for this row.")
        reasons.append({"reason_id": "scheduler-validation-" + _slug(code), "reason": message})
    return reasons


def _offline_checks(row: Mapping[str, Any], validation_errors: list[Mapping[str, Any]]) -> list[str]:
    checks = _string_list(row.get("proposed_offline_checks"))
    if checks:
        return checks
    checks = [
        "Compare fixture citation IDs against the source registry metadata snapshot.",
        "Confirm affected requirement or process IDs still map to the cited public source IDs.",
        "Review stale or defer reasons before authorizing any separate live recrawl request.",
    ]
    if validation_errors:
        checks.append("Resolve scheduler rehearsal validation errors in fixtures before approving the row.")
    return checks


def _citations(value: Any, fallback_source_id: str) -> list[dict[str, str]]:
    citations: list[dict[str, str]] = []
    if isinstance(value, list):
        for index, citation in enumerate(value, 1):
            if isinstance(citation, Mapping):
                citation_id = _text(citation.get("citation_id"), f"citation-{_slug(fallback_source_id)}-{index}")
                source_id = _text(citation.get("source_id"), fallback_source_id)
                cited_field = _text(citation.get("cited_field"), "scheduler_rehearsal_fixture")
                quote = _text(citation.get("quote"))
                item = {"citation_id": citation_id, "source_id": source_id, "cited_field": cited_field}
                if quote:
                    item["quote"] = quote
                citations.append(item)
            elif isinstance(citation, str) and citation.strip():
                citations.append(
                    {
                        "citation_id": citation.strip(),
                        "source_id": fallback_source_id,
                        "cited_field": "scheduler_rehearsal_fixture",
                    }
                )
    return citations


def _safe_public_url(row: Mapping[str, Any]) -> str:
    for key in ("canonical_url", "url", "public_url"):
        value = _text(row.get(key))
        if value and _is_safe_public_url(value):
            return value
    metadata = row.get("metadata_fields")
    if isinstance(metadata, Mapping):
        for key in ("canonical_url", "url", "public_url"):
            value = _text(metadata.get(key))
            if value and _is_safe_public_url(value):
                return value
    return ""


def _is_safe_public_url(value: str) -> bool:
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    path = parsed.path.lower()
    query = parsed.query.lower()
    if parsed.scheme != "https" or host not in _ALLOWED_PUBLIC_HOSTS:
        return False
    if any(marker in path for marker in _PRIVATE_PATH_MARKERS):
        return False
    return not any(marker in query for marker in _PRIVATE_QUERY_MARKERS)


def _validate_no_forbidden_fields(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            child_path = f"{path}.{key_text}"
            if lowered in _FORBIDDEN_KEYS:
                errors.append(child_path + " is forbidden in public freshness reviewer handoff packets")
            if lowered in _FORBIDDEN_TRUE_KEYS and child is True:
                errors.append(child_path + " must not be true")
            _validate_no_forbidden_fields(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_no_forbidden_fields(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        lowered_value = value.lower()
        if any(marker in lowered_value for marker in (".har", ".warc", "trace.zip", "raw_body", "download_path", "storage_state")):
            errors.append(path + " must not reference raw crawl or browser artifacts")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) and value.strip() else default


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


__all__ = [
    "MODE",
    "PACKET_TYPE",
    "PublicFreshnessReviewerHandoffValidationResult",
    "build_public_freshness_reviewer_handoff_v1",
    "validate_public_freshness_reviewer_handoff_v1",
]
