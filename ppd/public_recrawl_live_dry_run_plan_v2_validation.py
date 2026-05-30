"""Fail-closed validation for public recrawl live-dry-run plan v2.

The validator is intentionally small and dependency-free so it can be used by
planning code, daemon preflight checks, or tests before any live crawl or
authenticated automation is attempted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse


_ALLOWED_HOSTS = frozenset(
    {
        "www.portland.gov",
        "portland.gov",
        "www.portlandmaps.com",
        "portlandmaps.com",
    }
)

_AUTH_URL_MARKERS = (
    "/login",
    "/log-in",
    "/logout",
    "/sign-in",
    "/signin",
    "/account",
    "/accounts",
    "/oauth",
    "/saml",
    "/session",
    "/sessions",
    "/admin",
    "/wp-admin",
)

_RAW_REFERENCE_KEYS = (
    "raw_body",
    "rawBody",
    "body",
    "html",
    "download",
    "download_url",
    "downloadUrl",
    "archive",
    "archive_url",
    "archiveUrl",
    "snapshot",
    "screenshot",
    "trace",
)

_COMPLETION_CLAIM_KEYS = (
    "live_crawl_completed",
    "liveCrawlCompleted",
    "crawl_completed",
    "crawlCompleted",
    "processor_completed",
    "processorCompleted",
    "processing_completed",
    "processingCompleted",
)

_OUTCOME_GUARANTEE_KEYS = (
    "guarantees_outcome",
    "guaranteesOutcome",
    "permit_approved",
    "permitApproved",
    "approval_guaranteed",
    "approvalGuaranteed",
    "legal_advice",
    "legalAdvice",
    "legal_conclusion",
    "legalConclusion",
)

_MUTATION_FLAG_KEYS = (
    "mutate_sources",
    "mutateSources",
    "update_sources",
    "updateSources",
    "mutate_schedule",
    "mutateSchedule",
    "update_schedule",
    "updateSchedule",
    "mutate_requirements",
    "mutateRequirements",
    "update_requirements",
    "updateRequirements",
    "mutate_process",
    "mutateProcess",
    "update_process",
    "updateProcess",
    "mutate_guardrails",
    "mutateGuardrails",
    "update_guardrails",
    "updateGuardrails",
    "mutate_prompts",
    "mutatePrompts",
    "update_prompts",
    "updatePrompts",
    "mutate_monitoring",
    "mutateMonitoring",
    "update_monitoring",
    "updateMonitoring",
    "mutate_release_state",
    "mutateReleaseState",
    "update_release_state",
    "updateReleaseState",
    "mutate_agent_state",
    "mutateAgentState",
    "update_agent_state",
    "updateAgentState",
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


def validate_public_recrawl_live_dry_run_plan_v2(plan: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return validation issues for an unsafe public recrawl dry-run plan.

    A valid plan must be citation-backed, public-only, allowlisted, robots-aware,
    rate-limited, dry-run-only, and free of mutation or completion claims.
    """

    issues: list[ValidationIssue] = []

    if not isinstance(plan, Mapping):
        return [ValidationIssue("invalid_plan", "$", "plan must be a mapping")]

    _validate_seed_selections(plan, issues)
    _validate_policy_decisions(plan, issues)
    _scan_mapping(plan, "$", issues)
    return issues


def assert_public_recrawl_live_dry_run_plan_v2(plan: Mapping[str, Any]) -> None:
    """Raise ValueError when the plan is not safe to execute."""

    issues = validate_public_recrawl_live_dry_run_plan_v2(plan)
    if issues:
        details = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in issues)
        raise ValueError(details)


def _validate_seed_selections(plan: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    seeds = plan.get("seed_selections", plan.get("seeds", ()))
    if not isinstance(seeds, Sequence) or isinstance(seeds, (str, bytes, bytearray)):
        issues.append(ValidationIssue("invalid_seed_selections", "$.seed_selections", "seed selections must be a list"))
        return

    for index, seed in enumerate(seeds):
        path = f"$.seed_selections[{index}]"
        if not isinstance(seed, Mapping):
            issues.append(ValidationIssue("invalid_seed", path, "seed selection must be a mapping"))
            continue

        citations = seed.get("citations") or seed.get("citation") or seed.get("source_citations")
        if not citations:
            issues.append(ValidationIssue("uncited_seed_selection", path, "seed selection must include citations"))

        url = seed.get("url") or seed.get("source_url") or seed.get("href")
        if isinstance(url, str):
            _validate_public_url(url, f"{path}.url", issues)
        else:
            issues.append(ValidationIssue("missing_seed_url", path, "seed selection must include a URL"))


def _validate_policy_decisions(plan: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    robots = plan.get("robots_decision") or plan.get("robotsDecision") or plan.get("robots")
    if not _has_positive_decision(robots):
        issues.append(ValidationIssue("missing_robots_decision", "$.robots_decision", "robots decision is required"))

    rate_limit = plan.get("rate_limit_decision") or plan.get("rateLimitDecision") or plan.get("rate_limit")
    if not _has_positive_decision(rate_limit):
        issues.append(ValidationIssue("missing_rate_limit_decision", "$.rate_limit_decision", "rate-limit decision is required"))


def _has_positive_decision(value: Any) -> bool:
    if isinstance(value, Mapping):
        decision = value.get("decision") or value.get("status") or value.get("allowed")
        if decision is True:
            return True
        if isinstance(decision, str):
            return decision.strip().lower() in {"allow", "allowed", "approved", "yes"}
        return bool(value.get("citation") or value.get("citations"))
    if isinstance(value, str):
        return bool(value.strip())
    return value is True


def _scan_mapping(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            _validate_key_value(key_text, child, child_path, issues)
            _scan_mapping(child, child_path, issues)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_mapping(child, f"{path}[{index}]", issues)
    elif isinstance(value, str) and value.startswith(("http://", "https://")):
        _validate_public_url(value, path, issues)


def _validate_key_value(key: str, value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if key in _RAW_REFERENCE_KEYS and value:
        issues.append(ValidationIssue("raw_artifact_reference", path, "raw body, download, archive, trace, or snapshot references are not allowed"))

    if key in _COMPLETION_CLAIM_KEYS and bool(value):
        issues.append(ValidationIssue("completion_claim", path, "live crawl or processor completion claims are not allowed in a dry-run plan"))

    if key in _OUTCOME_GUARANTEE_KEYS and bool(value):
        issues.append(ValidationIssue("outcome_guarantee", path, "legal or permitting outcome guarantees are not allowed"))

    if key in _MUTATION_FLAG_KEYS and bool(value):
        issues.append(ValidationIssue("mutation_flag", path, "active source, schedule, requirement, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are not allowed"))

    if isinstance(value, str) and key.lower().endswith("url"):
        _validate_public_url(value, path, issues)


def _validate_public_url(url: str, path: str, issues: list[ValidationIssue]) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    scheme = parsed.scheme.lower()
    lowered_path = parsed.path.lower()

    if scheme != "https":
        issues.append(ValidationIssue("non_https_url", path, "URL must use https"))

    if host not in _ALLOWED_HOSTS:
        issues.append(ValidationIssue("non_allowlisted_url", path, "URL host is not allowlisted"))

    if any(marker in lowered_path for marker in _AUTH_URL_MARKERS):
        issues.append(ValidationIssue("authenticated_url", path, "authenticated or administrative URLs are not allowed"))
