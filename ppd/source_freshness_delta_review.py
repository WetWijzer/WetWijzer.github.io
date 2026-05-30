"""Validation for PP&D source freshness delta review packets.

The validator is intentionally conservative: review packets are evidence records,
not crawler instructions or legal/permitting determinations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import urlparse

_ALLOWED_URL_HOSTS = frozenset(
    {
        "www.portland.gov",
        "portland.gov",
        "www.portlandmaps.com",
        "portlandmaps.com",
    }
)

_DECISIONS = frozenset({"changed", "unchanged", "stale"})
_MUTATION_FLAGS = frozenset(
    {
        "active_source_mutation",
        "active_schedule_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "mutates_active_sources",
        "mutates_active_schedules",
        "mutates_active_requirements",
        "mutates_active_processes",
        "mutates_active_guardrails",
        "mutates_active_prompts",
        "mutates_active_release_state",
    }
)

_AUTH_QUERY_MARKERS = ("token", "auth", "session", "key", "secret", "password", "cookie")
_AUTH_PATH_MARKERS = ("/login", "/signin", "/sign-in", "/oauth", "/saml", "/admin")
_RAW_REFERENCE_MARKERS = (
    "raw_body",
    "raw body",
    "response_body",
    "downloaded_body",
    "download_url",
    "download url",
    "archive_url",
    "archive url",
    "wayback",
    "raw crawl",
    "raw_crawl",
    "raw html",
    "raw_html",
)
_LIVE_EXECUTION_MARKERS = (
    "ran crawler",
    "run crawler",
    "live crawler",
    "executed crawler",
    "ran processor",
    "run processor",
    "live processor",
    "executed processor",
    "started crawl",
    "performed crawl",
    "fetched live",
)
_OUTCOME_GUARANTEE_MARKERS = (
    "guarantee approval",
    "guarantees approval",
    "will be approved",
    "permit approved",
    "permit will issue",
    "legally sufficient",
    "legal determination",
    "binding determination",
    "permits are guaranteed",
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str


def validate_source_freshness_delta_review_packet(packet: dict[str, Any]) -> list[ValidationIssue]:
    """Return validation issues for a source freshness delta review packet."""

    issues: list[ValidationIssue] = []
    if not isinstance(packet, dict):
        return [ValidationIssue("packet_type", "review packet must be an object")]

    affected_source_ids = _string_list(packet.get("affected_source_ids"))
    if not affected_source_ids:
        issues.append(ValidationIssue("affected_source_ids_missing", "packet must list affected source ids"))

    follow_up_queues = _string_list(packet.get("recommended_offline_follow_up_queues"))
    if not follow_up_queues:
        follow_up_queues = _string_list(packet.get("recommended_offline_follow_up_queue"))
    if not follow_up_queues:
        issues.append(
            ValidationIssue(
                "offline_follow_up_queue_missing",
                "packet must recommend at least one offline follow-up queue",
            )
        )

    reviewer_owners = _string_list(packet.get("reviewer_owners"))
    if not reviewer_owners:
        reviewer_owners = _string_list(packet.get("reviewer_owner"))
    if not reviewer_owners:
        issues.append(ValidationIssue("reviewer_owner_missing", "packet must identify reviewer owners"))

    decisions = packet.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        issues.append(ValidationIssue("decisions_missing", "packet must include review decisions"))
    else:
        issues.extend(_validate_decisions(decisions))

    issues.extend(_validate_urls(packet))
    issues.extend(_validate_text_markers(packet))
    issues.extend(_validate_mutation_flags(packet))
    return issues


def assert_source_freshness_delta_review_packet(packet: dict[str, Any]) -> None:
    """Raise ValueError when a review packet fails validation."""

    issues = validate_source_freshness_delta_review_packet(packet)
    if issues:
        details = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        raise ValueError(details)


def _validate_decisions(decisions: list[Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for index, decision in enumerate(decisions):
        prefix = f"decisions[{index}]"
        if not isinstance(decision, dict):
            issues.append(ValidationIssue("decision_type", f"{prefix} must be an object"))
            continue

        value = str(decision.get("decision", "")).strip().lower()
        if value not in _DECISIONS:
            issues.append(ValidationIssue("decision_value", f"{prefix} must be changed, unchanged, or stale"))
            continue

        citations = _string_list(decision.get("citations"))
        source_ids = _string_list(decision.get("source_ids"))
        evidence_ids = _string_list(decision.get("evidence_ids"))
        if not citations and not source_ids and not evidence_ids:
            issues.append(ValidationIssue("decision_uncited", f"{prefix} {value} decision must be cited"))

        affected_source_ids = _string_list(decision.get("affected_source_ids"))
        if not affected_source_ids and not source_ids:
            issues.append(
                ValidationIssue(
                    "decision_affected_source_ids_missing",
                    f"{prefix} must identify affected source ids",
                )
            )
    return issues


def _validate_urls(packet: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, value in _walk(packet):
        if not isinstance(value, str) or not _looks_like_url(value):
            continue
        parsed = urlparse(value)
        host = parsed.netloc.lower().split("@")[-1]
        if parsed.username or parsed.password or "@" in parsed.netloc:
            issues.append(ValidationIssue("authenticated_url", f"{path} must not contain URL credentials"))
        if host not in _ALLOWED_URL_HOSTS:
            issues.append(ValidationIssue("url_not_allowlisted", f"{path} host is not allowlisted: {host}"))
        lowered_path = parsed.path.lower()
        lowered_query = parsed.query.lower()
        if any(marker in lowered_path for marker in _AUTH_PATH_MARKERS):
            issues.append(ValidationIssue("authenticated_url", f"{path} must not reference authenticated paths"))
        if any(marker in lowered_query for marker in _AUTH_QUERY_MARKERS):
            issues.append(ValidationIssue("authenticated_url", f"{path} must not include auth-like query parameters"))
    return issues


def _validate_text_markers(packet: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, value in _walk(packet):
        text = str(value).lower() if isinstance(value, str) else ""
        key = path.lower()
        combined = f"{key} {text}"
        if any(marker in combined for marker in _RAW_REFERENCE_MARKERS):
            issues.append(ValidationIssue("raw_reference", f"{path} must not reference raw bodies, downloads, or archives"))
        if any(marker in text for marker in _LIVE_EXECUTION_MARKERS):
            issues.append(ValidationIssue("live_execution_claim", f"{path} must not claim live crawler or processor execution"))
        if any(marker in text for marker in _OUTCOME_GUARANTEE_MARKERS):
            issues.append(ValidationIssue("outcome_guarantee", f"{path} must not guarantee legal or permitting outcomes"))
    return issues


def _validate_mutation_flags(packet: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, value in _walk(packet):
        key = path.rsplit(".", 1)[-1].lower().replace("-", "_")
        if key in _MUTATION_FLAGS and value:
            issues.append(ValidationIssue("active_mutation_flag", f"{path} must not request active state mutation"))
    return issues


def _walk(value: Any, path: str = "packet") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item.strip())
    return result


def _looks_like_url(value: str) -> bool:
    lowered = value.lower().strip()
    return lowered.startswith("http://") or lowered.startswith("https://")
