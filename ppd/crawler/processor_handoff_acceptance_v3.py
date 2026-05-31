"""Fixture-first PP&D processor handoff acceptance packet v3 validation.

This module validates a committed synthetic handoff packet before any live
processor execution. It is intentionally side-effect free: it reads caller
provided data, performs deterministic checks, and returns diagnostics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence
from urllib.parse import urlparse

ALLOWED_PUBLIC_HOSTS = {
    "www.portland.gov",
    "devhub.portlandoregon.gov",
    "www.portlandoregon.gov",
    "www.portlandmaps.com",
}

REQUIRED_TOP_LEVEL_FALSE_FLAGS = (
    "live_processor_execution_allowed",
    "network_access_allowed",
    "raw_downloads_allowed",
    "devhub_access_allowed",
    "private_file_access_allowed",
    "active_crawler_mutation_allowed",
    "active_source_mutation_allowed",
    "active_archive_mutation_allowed",
    "active_document_mutation_allowed",
    "active_requirement_mutation_allowed",
    "process_model_mutation_allowed",
    "guardrail_mutation_allowed",
    "prompt_mutation_allowed",
    "contract_mutation_allowed",
    "release_state_change_allowed",
)

REQUIRED_SKIP_REASON_CODES = {
    "outside_allowlist",
    "unsupported_scheme",
    "private_authenticated",
    "disallowed_by_robots_or_policy",
    "raw_download_not_permitted",
    "too_large",
    "unsupported_content_type",
}

REQUIRED_ARCHIVE_MANIFEST_FIELDS = {
    "manifest_id",
    "source_id",
    "canonical_url",
    "requested_url",
    "redirect_chain",
    "http_status",
    "content_type",
    "content_hash",
    "capture_started_at",
    "capture_finished_at",
    "processor_name",
    "processor_version",
    "archive_artifact_ref",
    "normalized_document_id",
    "skipped_reason",
    "no_raw_body_persisted",
}

REQUIRED_PROCESSOR_CAPABILITIES = {
    "html_metadata",
    "pdf_metadata",
    "link_inventory",
    "archive_manifest_projection",
}

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class AcceptancePacketError(ValueError):
    """Raised when a processor handoff acceptance packet is invalid."""


def load_acceptance_packet(path: Path) -> Dict[str, Any]:
    """Load a JSON acceptance packet from a committed fixture path."""
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise AcceptancePacketError("acceptance packet must be a JSON object")
    return loaded


def validate_acceptance_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Return deterministic validation diagnostics for a v3 handoff packet."""
    errors: List[str] = []

    _validate_packet_header(packet, errors)
    _validate_false_flags(packet, errors)

    seed_urls = _validate_seed_urls(packet.get("seed_urls"), errors)
    allowlist = _validate_allowlist_decisions(packet.get("allowlist_decisions"), seed_urls, errors)
    allowed_seed_urls = [url for url in seed_urls if allowlist.get(url) == "allow"]

    _validate_policy_rows(packet.get("robots_policy_preflight_rows"), allowed_seed_urls, errors)
    _validate_processor_selections(packet.get("processor_capability_selections"), allowed_seed_urls, errors)
    _validate_archive_expectations(packet.get("archive_manifest_expectations"), allowed_seed_urls, errors)
    _validate_skipped_urls(packet.get("skipped_urls"), errors)
    _validate_retry_backoff(packet.get("retry_backoff_expectations"), errors)
    _validate_persistence_flags(packet.get("persistence_flags"), errors)
    _validate_handoff_gate(packet.get("handoff_gate"), errors)

    return {
        "packet_version": packet.get("packet_version"),
        "valid": not errors,
        "errors": errors,
        "reviewed_seed_url_count": len(seed_urls),
        "allowed_seed_url_count": len(allowed_seed_urls),
        "skipped_url_count": len(_as_list(packet.get("skipped_urls"))),
    }


def assert_acceptance_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a packet and raise AcceptancePacketError on failure."""
    result = validate_acceptance_packet(packet)
    if not result["valid"]:
        raise AcceptancePacketError("; ".join(result["errors"]))
    return result


def _validate_packet_header(packet: Mapping[str, Any], errors: List[str]) -> None:
    if packet.get("packet_version") != "v3":
        errors.append("packet_version must be v3")
    if packet.get("packet_type") != "processor_handoff_acceptance":
        errors.append("packet_type must be processor_handoff_acceptance")
    if packet.get("mode") != "fixture_first_offline":
        errors.append("mode must be fixture_first_offline")


def _validate_false_flags(packet: Mapping[str, Any], errors: List[str]) -> None:
    for field in REQUIRED_TOP_LEVEL_FALSE_FLAGS:
        if packet.get(field) is not False:
            errors.append(field + " must be false")


def _validate_seed_urls(value: Any, errors: List[str]) -> List[str]:
    rows = _as_list(value)
    if not rows:
        errors.append("seed_urls must include at least one synthetic PP&D public seed")
        return []

    urls: List[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append("seed_urls[" + str(index) + "] must be an object")
            continue
        url = _string_value(row, "url")
        if not url:
            errors.append("seed_urls[" + str(index) + "].url is required")
            continue
        parsed = urlparse(url)
        if parsed.scheme != "https":
            errors.append(url + " must use https")
        if parsed.hostname not in ALLOWED_PUBLIC_HOSTS:
            errors.append(url + " must use an allowed PP&D public host")
        if row.get("synthetic") is not True:
            errors.append(url + " must be marked synthetic")
        if row.get("public_seed") is not True:
            errors.append(url + " must be marked public_seed")
        urls.append(url)
    return urls


def _validate_allowlist_decisions(value: Any, seed_urls: Sequence[str], errors: List[str]) -> Dict[str, str]:
    rows = _as_list(value)
    decisions: Dict[str, str] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append("allowlist_decisions[" + str(index) + "] must be an object")
            continue
        url = _string_value(row, "url")
        decision = _string_value(row, "decision")
        if decision not in {"allow", "skip"}:
            errors.append("allowlist decision for " + url + " must be allow or skip")
        if row.get("checked_live") is not False:
            errors.append("allowlist decision for " + url + " must not be checked live")
        if decision == "allow":
            host = urlparse(url).hostname
            if host not in ALLOWED_PUBLIC_HOSTS:
                errors.append("allowlisted URL " + url + " is outside the public host allowlist")
        if url:
            decisions[url] = decision

    for url in seed_urls:
        if url not in decisions:
            errors.append("seed URL " + url + " is missing an allowlist decision")
    return decisions


def _validate_policy_rows(value: Any, allowed_seed_urls: Sequence[str], errors: List[str]) -> None:
    rows = _as_list(value)
    rows_by_url = _rows_by_url(rows)
    for url in allowed_seed_urls:
        row = rows_by_url.get(url)
        if row is None:
            errors.append("allowed seed URL " + url + " is missing a robots/policy preflight row")
            continue
        if row.get("checked_live") is not False:
            errors.append("robots/policy preflight for " + url + " must be fixture-only")
        if row.get("robots_status") != "synthetic_allow":
            errors.append("robots_status for " + url + " must be synthetic_allow")
        if row.get("policy_status") != "allowed_by_fixture_policy":
            errors.append("policy_status for " + url + " must be allowed_by_fixture_policy")
        if row.get("raw_body_requested") is not False:
            errors.append("robots/policy preflight for " + url + " must not request raw bodies")


def _validate_processor_selections(value: Any, allowed_seed_urls: Sequence[str], errors: List[str]) -> None:
    rows = _as_list(value)
    rows_by_url = _rows_by_url(rows)
    for url in allowed_seed_urls:
        row = rows_by_url.get(url)
        if row is None:
            errors.append("allowed seed URL " + url + " is missing a processor capability selection")
            continue
        if row.get("live_execution") is not False:
            errors.append("processor selection for " + url + " must disable live execution")
        if row.get("selected") is not True:
            errors.append("processor selection for " + url + " must be selected for review")
        capabilities = set(_as_string_list(row.get("capabilities")))
        missing = sorted(REQUIRED_PROCESSOR_CAPABILITIES.difference(capabilities))
        if missing:
            errors.append("processor selection for " + url + " is missing capabilities: " + ", ".join(missing))


def _validate_archive_expectations(value: Any, allowed_seed_urls: Sequence[str], errors: List[str]) -> None:
    rows = _as_list(value)
    rows_by_url = _rows_by_url(rows)
    for url in allowed_seed_urls:
        row = rows_by_url.get(url)
        if row is None:
            errors.append("allowed seed URL " + url + " is missing archive manifest expectations")
            continue
        if row.get("no_raw_body_persisted") is not True:
            errors.append("archive expectation for " + url + " must require no_raw_body_persisted")
        if row.get("raw_body_artifact_ref") is not None:
            errors.append("archive expectation for " + url + " must not include a raw_body_artifact_ref")
        expected_fields = set(_as_string_list(row.get("expected_fields")))
        missing = sorted(REQUIRED_ARCHIVE_MANIFEST_FIELDS.difference(expected_fields))
        if missing:
            errors.append("archive expectation for " + url + " is missing fields: " + ", ".join(missing))


def _validate_skipped_urls(value: Any, errors: List[str]) -> None:
    rows = _as_list(value)
    seen_reasons = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append("skipped_urls[" + str(index) + "] must be an object")
            continue
        url = _string_value(row, "url")
        reason = _string_value(row, "reason_code")
        if row.get("decision") != "skip":
            errors.append("skipped URL " + url + " must have decision skip")
        if reason not in REQUIRED_SKIP_REASON_CODES:
            errors.append("skipped URL " + url + " has unsupported reason_code " + reason)
        else:
            seen_reasons.add(reason)
        if row.get("raw_body_requested") is not False:
            errors.append("skipped URL " + url + " must not request raw bodies")
        if row.get("live_checked") is not False:
            errors.append("skipped URL " + url + " must not be live checked")
    missing_reasons = sorted(REQUIRED_SKIP_REASON_CODES.difference(seen_reasons))
    if missing_reasons:
        errors.append("skipped_urls must cover reason codes: " + ", ".join(missing_reasons))


def _validate_retry_backoff(value: Any, errors: List[str]) -> None:
    if not isinstance(value, dict):
        errors.append("retry_backoff_expectations must be an object")
        return
    if value.get("live_retry_allowed") is not False:
        errors.append("retry_backoff_expectations.live_retry_allowed must be false")
    if value.get("max_attempts") != 3:
        errors.append("retry_backoff_expectations.max_attempts must be 3")
    if value.get("initial_delay_seconds") != 2:
        errors.append("retry_backoff_expectations.initial_delay_seconds must be 2")
    if value.get("multiplier") != 2:
        errors.append("retry_backoff_expectations.multiplier must be 2")
    if value.get("jitter") is not False:
        errors.append("retry_backoff_expectations.jitter must be false for deterministic fixtures")
    retryable = set(_as_int_list(value.get("retryable_statuses")))
    if retryable != RETRYABLE_STATUS_CODES:
        errors.append("retry_backoff_expectations.retryable_statuses must be 429,500,502,503,504")


def _validate_persistence_flags(value: Any, errors: List[str]) -> None:
    if not isinstance(value, dict):
        errors.append("persistence_flags must be an object")
        return
    required_true = (
        "no_raw_body_persisted",
        "no_private_files",
        "no_auth_state",
        "no_screenshots",
        "no_traces",
        "no_har",
        "no_downloaded_documents",
    )
    for field in required_true:
        if value.get(field) is not True:
            errors.append("persistence_flags." + field + " must be true")


def _validate_handoff_gate(value: Any, errors: List[str]) -> None:
    if not isinstance(value, dict):
        errors.append("handoff_gate must be an object")
        return
    if value.get("accepted_for_live_processor_execution") is not False:
        errors.append("handoff_gate.accepted_for_live_processor_execution must be false")
    if value.get("requires_human_review_before_live") is not True:
        errors.append("handoff_gate.requires_human_review_before_live must be true")
    if value.get("fixture_review_complete") is not True:
        errors.append("handoff_gate.fixture_review_complete must be true")


def _rows_by_url(rows: Iterable[Any]) -> Dict[str, Mapping[str, Any]]:
    indexed: Dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict):
            url = row.get("url")
            if isinstance(url, str):
                indexed[url] = row
    return indexed


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _as_string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    strings: List[str] = []
    for item in value:
        if isinstance(item, str):
            strings.append(item)
    return strings


def _as_int_list(value: Any) -> List[int]:
    if not isinstance(value, list):
        return []
    integers: List[int] = []
    for item in value:
        if isinstance(item, int):
            integers.append(item)
    return integers


def _string_value(row: Mapping[str, Any], field: str) -> str:
    value = row.get(field)
    if isinstance(value, str):
        return value
    return ""


__all__ = [
    "AcceptancePacketError",
    "ALLOWED_PUBLIC_HOSTS",
    "REQUIRED_ARCHIVE_MANIFEST_FIELDS",
    "REQUIRED_PROCESSOR_CAPABILITIES",
    "REQUIRED_SKIP_REASON_CODES",
    "assert_acceptance_packet",
    "load_acceptance_packet",
    "validate_acceptance_packet",
]
