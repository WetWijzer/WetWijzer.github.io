"""Validation for public recrawl dry-run evidence envelopes v2.

This module is intentionally narrow: it validates deterministic evidence envelopes
and does not crawl, download, authenticate, mutate source state, or inspect live
systems.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


_MUTATION_FLAG_NAMES = {
    "active_source_mutation",
    "source_mutation",
    "schedule_mutation",
    "requirement_mutation",
    "process_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "monitoring_mutation",
    "release_state_mutation",
    "agent_state_mutation",
    "mutates_active_sources",
    "mutates_schedule",
    "mutates_requirements",
    "mutates_process",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_monitoring",
    "mutates_release_state",
    "mutates_agent_state",
}

_PROHIBITED_REFERENCE_KEYS = {
    "raw_body",
    "body",
    "html_body",
    "response_body",
    "download_path",
    "download_url",
    "archive_path",
    "archive_url",
    "raw_crawl_output",
}

_PROHIBITED_CLAIM_TERMS = (
    "crawler completed",
    "crawl completed",
    "processor completed",
    "processing completed",
    "live crawler",
    "live crawl",
    "permit approved",
    "permit will be approved",
    "guaranteed approval",
    "guarantees approval",
    "legal guarantee",
    "legally guaranteed",
    "permitting outcome guaranteed",
    "outcome guaranteed",
)

_REQUIRED_DECISIONS = ("robots", "rate_limit", "skip")


@dataclass(frozen=True)
class EvidenceValidationResult:
    ok: bool
    errors: tuple[str, ...]


def validate_public_recrawl_dry_run_evidence_v2(envelope: dict[str, Any]) -> EvidenceValidationResult:
    """Validate a public recrawl dry-run evidence envelope v2."""

    errors: list[str] = []

    if envelope.get("schema_version") != "public-recrawl-dry-run-evidence-v2":
        errors.append("schema_version must be public-recrawl-dry-run-evidence-v2")

    citations = _citation_ids(envelope.get("citations"))
    observations = envelope.get("observations")
    if not isinstance(observations, list) or not observations:
        errors.append("observations must be a non-empty list")
    else:
        for index, observation in enumerate(observations):
            if not isinstance(observation, dict):
                errors.append(f"observations[{index}] must be an object")
                continue
            cited_by = observation.get("citation_ids")
            if not isinstance(cited_by, list) or not cited_by:
                errors.append(f"observations[{index}] must include citation_ids")
            elif any(citation_id not in citations for citation_id in cited_by):
                errors.append(f"observations[{index}] references unknown citation_ids")
            _reject_prohibited_claims(observation, f"observations[{index}]", errors)

    allowlisted_hosts = _allowlisted_hosts(envelope.get("url_allowlist"))
    _validate_citations(envelope.get("citations"), allowlisted_hosts, errors)
    _validate_decisions(envelope.get("decisions"), errors)
    _reject_prohibited_references(envelope, "$", errors)
    _reject_prohibited_claims(envelope, "$", errors)
    _reject_mutation_flags(envelope, "$", errors)

    return EvidenceValidationResult(ok=not errors, errors=tuple(errors))


def require_public_recrawl_dry_run_evidence_v2(envelope: dict[str, Any]) -> None:
    """Raise ValueError when an envelope fails validation."""

    result = validate_public_recrawl_dry_run_evidence_v2(envelope)
    if not result.ok:
        raise ValueError("invalid public recrawl dry-run evidence envelope v2: " + "; ".join(result.errors))


def _citation_ids(citations: Any) -> set[str]:
    if not isinstance(citations, list):
        return set()
    ids: set[str] = set()
    for citation in citations:
        if isinstance(citation, dict) and isinstance(citation.get("id"), str):
            ids.add(citation["id"])
    return ids


def _allowlisted_hosts(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    hosts: set[str] = set()
    for item in value:
        if isinstance(item, str) and item.strip():
            parsed = urlparse(item if "://" in item else "https://" + item)
            host = parsed.hostname
            if host:
                hosts.add(host.lower())
    return hosts


def _validate_citations(citations: Any, allowlisted_hosts: set[str], errors: list[str]) -> None:
    if not isinstance(citations, list) or not citations:
        errors.append("citations must be a non-empty list")
        return
    if not allowlisted_hosts:
        errors.append("url_allowlist must include at least one public host")
    seen_ids: set[str] = set()
    for index, citation in enumerate(citations):
        if not isinstance(citation, dict):
            errors.append(f"citations[{index}] must be an object")
            continue
        citation_id = citation.get("id")
        if not isinstance(citation_id, str) or not citation_id.strip():
            errors.append(f"citations[{index}] must include id")
        elif citation_id in seen_ids:
            errors.append(f"citations[{index}] duplicates citation id {citation_id}")
        else:
            seen_ids.add(citation_id)
        url = citation.get("url")
        if not isinstance(url, str) or not url.strip():
            errors.append(f"citations[{index}] must include url")
            continue
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            errors.append(f"citations[{index}] url must be an https public URL")
            continue
        host = parsed.hostname.lower()
        if allowlisted_hosts and host not in allowlisted_hosts:
            errors.append(f"citations[{index}] url host is not allowlisted")
        if "@" in parsed.netloc or parsed.username or parsed.password:
            errors.append(f"citations[{index}] url must not contain authentication material")
        if parsed.query:
            lowered_query = parsed.query.lower()
            if any(token in lowered_query for token in ("token=", "key=", "password=", "session=", "auth=")):
                errors.append(f"citations[{index}] url query appears to contain authentication material")


def _validate_decisions(decisions: Any, errors: list[str]) -> None:
    if not isinstance(decisions, dict):
        errors.append("decisions must include robots, rate_limit, and skip objects")
        return
    for name in _REQUIRED_DECISIONS:
        value = decisions.get(name)
        if not isinstance(value, dict):
            errors.append(f"decisions.{name} must be an object")
            continue
        decision = value.get("decision")
        reason = value.get("reason")
        if not isinstance(decision, str) or not decision.strip():
            errors.append(f"decisions.{name}.decision is required")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"decisions.{name}.reason is required")


def _reject_prohibited_references(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _PROHIBITED_REFERENCE_KEYS:
                errors.append(f"{child_path} is prohibited in dry-run evidence")
            _reject_prohibited_references(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_references(child, f"{path}[{index}]", errors)


def _reject_prohibited_claims(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        for term in _PROHIBITED_CLAIM_TERMS:
            if term in lowered:
                errors.append(f"{path} contains prohibited completion, legal, or permitting outcome claim")
                break
    elif isinstance(value, dict):
        for key, child in value.items():
            _reject_prohibited_claims(child, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_claims(child, f"{path}[{index}]", errors)


def _reject_mutation_flags(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _MUTATION_FLAG_NAMES and child is True:
                errors.append(f"{child_path} must not be true in dry-run evidence")
            _reject_mutation_flags(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_mutation_flags(child, f"{path}[{index}]", errors)
