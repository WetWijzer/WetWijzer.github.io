"""Validation for PP&D source change monitoring reports.

The monitor is allowed to persist source metadata, citations, and hashes. It is
not allowed to launder guessed hashes, private URLs, raw page bodies, downloaded
file paths, uncited affected IDs, or guardrail promotions that still require
review.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import parse_qsl, urlparse


_ALLOWED_PUBLIC_HOSTS = {
    "www.portland.gov",
    "portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "www.portlandmaps.com",
    "portlandmaps.com",
}

_PRIVATE_PATH_MARKERS = (
    "/login",
    "/signin",
    "/sign-in",
    "/register",
    "/account",
    "/accounts",
    "/profile",
    "/my-permits",
    "/mypermits",
    "/my-requests",
    "/dashboard",
    "/admin",
    "/payment",
    "/checkout",
    "/upload",
    "/corrections",
)

_PRIVATE_QUERY_MARKERS = {
    "access_token",
    "auth",
    "authorization",
    "code",
    "cookie",
    "jwt",
    "key",
    "password",
    "session",
    "sessionid",
    "sid",
    "signature",
    "state",
    "token",
}

_RAW_BODY_KEYS = {
    "body",
    "body_html",
    "body_text",
    "content",
    "dom",
    "html",
    "inner_html",
    "outer_html",
    "page_body",
    "raw",
    "raw_body",
    "raw_content",
    "raw_html",
    "response_body",
    "text",
}

_DOWNLOADED_PATH_KEYS = {
    "archive_path",
    "download_path",
    "downloaded_path",
    "file_path",
    "filesystem_path",
    "har_path",
    "local_file",
    "local_path",
    "pdf_path",
    "screenshot_path",
    "trace_path",
    "warc_path",
}

_REVIEW_REQUIRED_STATUSES = {
    "needs_review",
    "review_required",
    "human_review_required",
    "pending_review",
    "requires_human_review",
}

_PROMOTED_STATUSES = {
    "approved",
    "compiled",
    "promoted",
    "ready",
    "validated",
}


@dataclass(frozen=True)
class SourceChangeReportViolation:
    """A deterministic validation failure for a source change report."""

    code: str
    message: str
    location: str


class SourceChangeReportValidationError(ValueError):
    """Raised when a source change monitoring report is not commit-safe."""

    def __init__(self, violations: Sequence[SourceChangeReportViolation]) -> None:
        self.violations = tuple(violations)
        details = "; ".join(
            f"{violation.location}: {violation.code}: {violation.message}"
            for violation in self.violations
        )
        super().__init__(details)


def validate_source_change_report(report: Mapping[str, Any]) -> None:
    """Validate a PP&D source change monitoring report.

    The accepted shape is intentionally dict-based so the monitor can validate
    JSON before promotion into richer contracts. A valid report must include a
    ``source_evidence`` list and a ``changes`` list. Each change must cite prior
    and current evidence records, and every affected requirement or guardrail ID
    must be tied to at least one citation evidence ID.
    """

    violations: list[SourceChangeReportViolation] = []

    if not isinstance(report, Mapping):
        raise TypeError("source change report must be a mapping")

    _scan_for_forbidden_payloads(report, "$", violations)

    evidence_by_id = _collect_source_evidence(report, violations)
    citation_ids = set(evidence_by_id)

    changes = report.get("changes")
    if not isinstance(changes, list) or not changes:
        violations.append(
            SourceChangeReportViolation(
                code="missing_changes",
                message="change report must include at least one change",
                location="$.changes",
            )
        )
        changes = []

    for index, change in enumerate(changes):
        location = f"$.changes[{index}]"
        if not isinstance(change, Mapping):
            violations.append(
                SourceChangeReportViolation(
                    code="invalid_change",
                    message="each change must be an object",
                    location=location,
                )
            )
            continue
        _validate_change_evidence(change, location, evidence_by_id, violations)
        _validate_affected_id_citations(change, location, citation_ids, violations)
        _validate_guardrail_promotion(change, location, violations)

    _validate_top_level_affected_id_citations(report, citation_ids, violations)
    _validate_top_level_guardrail_promotion(report, violations)

    if violations:
        raise SourceChangeReportValidationError(violations)


def source_change_report_violations(
    report: Mapping[str, Any],
) -> tuple[SourceChangeReportViolation, ...]:
    """Return validation failures without raising."""

    try:
        validate_source_change_report(report)
    except SourceChangeReportValidationError as exc:
        return exc.violations
    return ()


def _collect_source_evidence(
    report: Mapping[str, Any],
    violations: list[SourceChangeReportViolation],
) -> dict[str, Mapping[str, Any]]:
    evidence = report.get("source_evidence")
    if not isinstance(evidence, list) or not evidence:
        violations.append(
            SourceChangeReportViolation(
                code="missing_source_evidence",
                message="report must include previous and current public source evidence",
                location="$.source_evidence",
            )
        )
        return {}

    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(evidence):
        location = f"$.source_evidence[{index}]"
        if not isinstance(item, Mapping):
            violations.append(
                SourceChangeReportViolation(
                    code="invalid_source_evidence",
                    message="source evidence entries must be objects",
                    location=location,
                )
            )
            continue

        evidence_id = item.get("evidence_id") or item.get("source_evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            violations.append(
                SourceChangeReportViolation(
                    code="missing_evidence_id",
                    message="source evidence must have a stable evidence_id",
                    location=location,
                )
            )
            continue

        content_hash = item.get("content_hash")
        if not isinstance(content_hash, str) or not content_hash.strip():
            violations.append(
                SourceChangeReportViolation(
                    code="missing_content_hash",
                    message="source evidence must include the observed content_hash",
                    location=location,
                )
            )

        canonical_url = item.get("canonical_url") or item.get("url")
        if not isinstance(canonical_url, str) or not canonical_url.strip():
            violations.append(
                SourceChangeReportViolation(
                    code="missing_source_url",
                    message="source evidence must include a public canonical_url",
                    location=location,
                )
            )
        elif _is_private_or_authenticated_url(canonical_url):
            violations.append(
                SourceChangeReportViolation(
                    code="private_or_authenticated_url",
                    message="source evidence URL must be public and unauthenticated",
                    location=f"{location}.canonical_url",
                )
            )

        source_type = str(item.get("source_type", "")).lower()
        privacy = str(item.get("privacy_classification", "public")).lower()
        if source_type == "devhub_authenticated" or privacy not in {"", "public"}:
            violations.append(
                SourceChangeReportViolation(
                    code="private_or_authenticated_source",
                    message="change reports may only reference public source evidence",
                    location=location,
                )
            )

        evidence_by_id[evidence_id] = item

    return evidence_by_id


def _validate_change_evidence(
    change: Mapping[str, Any],
    location: str,
    evidence_by_id: Mapping[str, Mapping[str, Any]],
    violations: list[SourceChangeReportViolation],
) -> None:
    previous_id = change.get("previous_source_evidence_id")
    current_id = change.get("current_source_evidence_id")

    if not isinstance(previous_id, str) or previous_id not in evidence_by_id:
        violations.append(
            SourceChangeReportViolation(
                code="missing_previous_source_evidence",
                message="change must cite an existing previous source evidence record",
                location=f"{location}.previous_source_evidence_id",
            )
        )
    if not isinstance(current_id, str) or current_id not in evidence_by_id:
        violations.append(
            SourceChangeReportViolation(
                code="missing_current_source_evidence",
                message="change must cite an existing current source evidence record",
                location=f"{location}.current_source_evidence_id",
            )
        )

    if isinstance(previous_id, str) and previous_id in evidence_by_id:
        _validate_observed_hash(
            change,
            evidence_by_id[previous_id],
            "previous_hash",
            f"{location}.previous_hash",
            violations,
        )
    if isinstance(current_id, str) and current_id in evidence_by_id:
        _validate_observed_hash(
            change,
            evidence_by_id[current_id],
            "current_hash",
            f"{location}.current_hash",
            violations,
        )

    changed_hash = change.get("changed_source_hash") or change.get("changed_hash")
    if changed_hash is not None:
        known_hashes = {
            str(item.get("content_hash"))
            for item in evidence_by_id.values()
            if item.get("content_hash")
        }
        if changed_hash not in known_hashes:
            violations.append(
                SourceChangeReportViolation(
                    code="invented_changed_hash",
                    message="changed hash must match an observed source evidence content_hash",
                    location=f"{location}.changed_source_hash",
                )
            )


def _validate_observed_hash(
    change: Mapping[str, Any],
    evidence: Mapping[str, Any],
    field_name: str,
    location: str,
    violations: list[SourceChangeReportViolation],
) -> None:
    declared_hash = change.get(field_name)
    if declared_hash is None:
        return
    observed_hash = evidence.get("content_hash")
    if declared_hash != observed_hash:
        violations.append(
            SourceChangeReportViolation(
                code="invented_changed_hash",
                message=f"{field_name} must match cited source evidence content_hash",
                location=location,
            )
        )


def _validate_affected_id_citations(
    change: Mapping[str, Any],
    location: str,
    citation_ids: set[str],
    violations: list[SourceChangeReportViolation],
) -> None:
    affected_ids = _affected_ids(change)
    if not affected_ids:
        return

    citation_map = change.get("affected_id_citations")
    if not isinstance(citation_map, Mapping):
        violations.append(
            SourceChangeReportViolation(
                code="affected_ids_without_citations",
                message="affected requirement and guardrail IDs must have citation evidence IDs",
                location=location,
            )
        )
        return

    for affected_id in sorted(affected_ids):
        cited = citation_map.get(affected_id)
        cited_ids = _as_string_list(cited)
        if not cited_ids:
            violations.append(
                SourceChangeReportViolation(
                    code="affected_id_without_citation",
                    message=f"affected ID {affected_id!r} has no citation evidence IDs",
                    location=f"{location}.affected_id_citations.{affected_id}",
                )
            )
            continue
        unknown = sorted(set(cited_ids) - citation_ids)
        if unknown:
            violations.append(
                SourceChangeReportViolation(
                    code="unknown_citation_evidence",
                    message=f"affected ID {affected_id!r} cites unknown evidence IDs: {', '.join(unknown)}",
                    location=f"{location}.affected_id_citations.{affected_id}",
                )
            )


def _validate_top_level_affected_id_citations(
    report: Mapping[str, Any],
    citation_ids: set[str],
    violations: list[SourceChangeReportViolation],
) -> None:
    affected_ids = _affected_ids(report)
    if not affected_ids:
        return

    citation_map = report.get("affected_id_citations")
    if not isinstance(citation_map, Mapping):
        violations.append(
            SourceChangeReportViolation(
                code="affected_ids_without_citations",
                message="top-level affected IDs must have citation evidence IDs",
                location="$.affected_id_citations",
            )
        )
        return

    for affected_id in sorted(affected_ids):
        cited_ids = _as_string_list(citation_map.get(affected_id))
        if not cited_ids:
            violations.append(
                SourceChangeReportViolation(
                    code="affected_id_without_citation",
                    message=f"affected ID {affected_id!r} has no citation evidence IDs",
                    location=f"$.affected_id_citations.{affected_id}",
                )
            )
        elif not set(cited_ids).issubset(citation_ids):
            violations.append(
                SourceChangeReportViolation(
                    code="unknown_citation_evidence",
                    message=f"affected ID {affected_id!r} cites evidence outside source_evidence",
                    location=f"$.affected_id_citations.{affected_id}",
                )
            )


def _validate_guardrail_promotion(
    change: Mapping[str, Any],
    location: str,
    violations: list[SourceChangeReportViolation],
) -> None:
    review_status = str(change.get("human_review_status", "")).lower()
    validation_status = str(change.get("guardrail_validation_status", "")).lower()
    promotion = change.get("guardrail_promotion")
    auto_promote = bool(change.get("auto_promote_guardrails"))

    promoted = auto_promote or validation_status in _PROMOTED_STATUSES
    if isinstance(promotion, Mapping):
        promoted = promoted or bool(promotion.get("automatic"))
        promoted = promoted or str(promotion.get("status", "")).lower() in _PROMOTED_STATUSES

    if review_status in _REVIEW_REQUIRED_STATUSES and promoted:
        violations.append(
            SourceChangeReportViolation(
                code="guardrail_auto_promotion_review_required",
                message="guardrails cannot be automatically promoted while human review is required",
                location=location,
            )
        )


def _validate_top_level_guardrail_promotion(
    report: Mapping[str, Any],
    violations: list[SourceChangeReportViolation],
) -> None:
    _validate_guardrail_promotion(report, "$", violations)


def _affected_ids(item: Mapping[str, Any]) -> set[str]:
    affected: set[str] = set()
    for key in (
        "affected_ids",
        "affected_requirement_ids",
        "affected_guardrail_bundle_ids",
        "affected_guardrail_ids",
    ):
        affected.update(_as_string_list(item.get(key)))
    return affected


def _as_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Iterable) and not isinstance(value, (bytes, Mapping)):
        return [item for item in value if isinstance(item, str) and item]
    return []


def _scan_for_forbidden_payloads(
    value: Any,
    location: str,
    violations: list[SourceChangeReportViolation],
) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            key_lower = key.lower()
            child_location = f"{location}.{key}"
            if key_lower in _RAW_BODY_KEYS and isinstance(child, str) and child.strip():
                violations.append(
                    SourceChangeReportViolation(
                        code="raw_page_body_present",
                        message="change reports must not persist raw page bodies",
                        location=child_location,
                    )
                )
            if key_lower in _DOWNLOADED_PATH_KEYS and child not in (None, ""):
                violations.append(
                    SourceChangeReportViolation(
                        code="downloaded_path_present",
                        message="change reports must not persist downloaded or local file paths",
                        location=child_location,
                    )
                )
            if isinstance(child, str):
                if _looks_like_downloaded_path(child):
                    violations.append(
                        SourceChangeReportViolation(
                            code="downloaded_path_present",
                            message="change reports must not persist downloaded or local file paths",
                            location=child_location,
                        )
                    )
                if key_lower.endswith("url") and _is_private_or_authenticated_url(child):
                    violations.append(
                        SourceChangeReportViolation(
                            code="private_or_authenticated_url",
                            message="URLs in change reports must be public and unauthenticated",
                            location=child_location,
                        )
                    )
            _scan_for_forbidden_payloads(child, child_location, violations)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_forbidden_payloads(child, f"{location}[{index}]", violations)


def _is_private_or_authenticated_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return True
    if parsed.username or parsed.password:
        return True

    host = (parsed.hostname or "").lower()
    if host not in _ALLOWED_PUBLIC_HOSTS:
        return True

    path = parsed.path.lower().rstrip("/")
    if any(marker in path for marker in _PRIVATE_PATH_MARKERS):
        return True

    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    return bool(query_keys & _PRIVATE_QUERY_MARKERS)


def _looks_like_downloaded_path(value: str) -> bool:
    if not value:
        return False
    if value.startswith(("file://", "~/", "/home/", "/Users/", "/tmp/", "/var/tmp/")):
        return True
    if "\\" in value:
        windows_path = PureWindowsPath(value)
        if windows_path.drive or "downloads" in {part.lower() for part in windows_path.parts}:
            return True
    posix_path = PurePosixPath(value)
    parts = {part.lower() for part in posix_path.parts}
    return "downloads" in parts or ".daemon" in parts


__all__ = [
    "SourceChangeReportValidationError",
    "SourceChangeReportViolation",
    "source_change_report_violations",
    "validate_source_change_report",
]
