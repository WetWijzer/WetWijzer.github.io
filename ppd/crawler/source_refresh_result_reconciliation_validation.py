"""Validation for offline source refresh result reconciliation packets."""

from __future__ import annotations

import re
from typing import Any, Mapping
from urllib.parse import urlparse, parse_qsl

ALLOWLISTED_HOSTS = {
    "portland.gov",
    "www.portland.gov",
    "www.portlandmaps.com",
    "portlandmaps.com",
}

RAW_REFERENCE_RE = re.compile(
    r"\b(raw[_ -]?(body|crawl|response|download|archive)|downloaded[_ -]?document|"
    r"download[_ -]?path|archive[_ -]?path|warc|har|browser[_ -]?trace|trace[_ -]?zip)\b",
    re.IGNORECASE,
)
PRIVATE_REFERENCE_RE = re.compile(
    r"(^|[/:\\])(?:tmp|private|sessions?|credentials?|secrets?|playwright|screenshots?|traces?)(?:[/:\\]|$)",
    re.IGNORECASE,
)
LIVE_EXECUTION_RE = re.compile(
    r"\b(live[_ -]?(crawler|crawl|scrape).*(ran|executed|completed|enabled)|"
    r"processor[_ -]?execution.*(ran|executed|completed|enabled)|processor\s+ran)\b",
    re.IGNORECASE,
)
LEGAL_GUARANTEE_RE = re.compile(
    r"\b(permit(?:ting)?\s+(?:approval|outcome)\s+(?:is\s+)?guaranteed|"
    r"guarantees?\s+(?:permit|legal|approval)|will\s+be\s+(?:approved|issued)|"
    r"legally\s+compliant|permit\s+approved)\b",
    re.IGNORECASE,
)
AUTH_QUERY_KEYS = {"token", "auth", "apikey", "api_key", "key", "session", "sid", "password", "signature"}
MUTATION_TARGETS = (
    "source",
    "schedule",
    "requirement",
    "process",
    "guardrail",
    "prompt",
    "monitoring",
    "release_state",
    "releasestate",
)


class SourceRefreshResultReconciliationValidationError(ValueError):
    """Raised when a reconciliation packet is unsafe for offline review."""


def validate_source_refresh_result_reconciliation_packet(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a source refresh result reconciliation packet."""
    errors: list[str] = []
    if packet.get("packet_type") != "source_refresh_result_reconciliation":
        errors.append("packet_type must be source_refresh_result_reconciliation")

    reviewer_owner = packet.get("reviewer_owner")
    if not _non_empty_text(reviewer_owner):
        errors.append("reviewer_owner is required")

    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("offline_validation_commands must contain at least one offline command")
    else:
        for index, command in enumerate(commands):
            if not isinstance(command, list) or not command or not all(_non_empty_text(part) for part in command):
                errors.append(f"offline_validation_commands[{index}] must be a non-empty argv list")

    decisions = packet.get("source_decisions")
    if not isinstance(decisions, list) or not decisions:
        errors.append("source_decisions must contain at least one decision")
    else:
        for index, decision in enumerate(decisions):
            _validate_decision(decision, index, reviewer_owner, errors)

    _walk_packet(packet, "$", errors)
    return errors


def assert_valid_source_refresh_result_reconciliation_packet(packet: Mapping[str, Any]) -> None:
    errors = validate_source_refresh_result_reconciliation_packet(packet)
    if errors:
        raise SourceRefreshResultReconciliationValidationError("; ".join(errors))


def _validate_decision(decision: Any, index: int, packet_reviewer_owner: Any, errors: list[str]) -> None:
    path = f"source_decisions[{index}]"
    if not isinstance(decision, Mapping):
        errors.append(f"{path} must be an object")
        return
    if not _non_empty_text(decision.get("source_id")):
        errors.append(f"{path}.source_id is required")
    if decision.get("decision") not in {"accepted", "deferred", "escalated"}:
        errors.append(f"{path}.decision must be accepted, deferred, or escalated")
    if not _non_empty_text(decision.get("reviewer_owner")):
        errors.append(f"{path}.reviewer_owner is required")
    elif _non_empty_text(packet_reviewer_owner) and decision.get("reviewer_owner") != packet_reviewer_owner:
        errors.append(f"{path}.reviewer_owner must match packet reviewer_owner")

    citations = decision.get("citations")
    if not isinstance(citations, list) or not citations:
        errors.append(f"{path}.citations must contain at least one public citation")
    else:
        for citation_index, citation in enumerate(citations):
            citation_path = f"{path}.citations[{citation_index}]"
            if not isinstance(citation, Mapping):
                errors.append(f"{citation_path} must be an object")
                continue
            if not _non_empty_text(citation.get("label")):
                errors.append(f"{citation_path}.label is required")
            href = citation.get("href") or citation.get("url")
            if not _non_empty_text(href):
                errors.append(f"{citation_path}.href is required")
            else:
                url_error = _public_url_error(str(href))
                if url_error:
                    errors.append(f"{citation_path}.href {url_error}")

    for field in ("affected_requirement_ids", "affected_process_ids", "affected_guardrail_ids"):
        value = decision.get(field)
        if not isinstance(value, list) or not any(_non_empty_text(item) for item in value):
            errors.append(f"{path}.{field} must contain at least one affected artifact id")


def _walk_packet(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_text = str(key)
            if RAW_REFERENCE_RE.search(key_text):
                errors.append(f"raw body/download/archive reference is not allowed at {child_path}")
            if _is_active_mutation_flag(key_text, child):
                errors.append(f"active mutation flag is not allowed at {child_path}")
            _walk_packet(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_packet(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        url_error = _url_like_error(value)
        if url_error:
            errors.append(f"{path} {url_error}")
        if RAW_REFERENCE_RE.search(value):
            errors.append(f"raw body/download/archive reference is not allowed at {path}")
        if PRIVATE_REFERENCE_RE.search(value):
            errors.append(f"private/session artifact reference is not allowed at {path}")
        if LIVE_EXECUTION_RE.search(value):
            errors.append(f"live crawler or processor execution claim is not allowed at {path}")
        if LEGAL_GUARANTEE_RE.search(value):
            errors.append(f"legal or permitting outcome guarantee is not allowed at {path}")


def _is_active_mutation_flag(key: str, value: Any) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
    if normalized.startswith("no_"):
        return False
    compact = normalized.replace("_", "")
    has_target = any(target in normalized or target in compact for target in MUTATION_TARGETS)
    has_mutation = "mutation" in normalized or "mutation" in compact or normalized.endswith("mutated")
    has_active = normalized.startswith("active_") or normalized.endswith("_enabled") or normalized.endswith("_allowed")
    if not (has_target and has_mutation and has_active):
        return False
    return _active_value(value)


def _active_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "enabled", "allowed", "active", "mutated"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return False


def _url_like_error(value: str) -> str | None:
    if not re.match(r"^[a-z][a-z0-9+.-]*://", value, re.IGNORECASE):
        return None
    return _public_url_error(value)


def _public_url_error(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return "must use https public URLs"
    if parsed.username or parsed.password:
        return "must not contain authenticated URL credentials"
    hostname = (parsed.hostname or "").lower()
    if hostname not in ALLOWLISTED_HOSTS:
        return "host is not allowlisted"
    for key, _value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in AUTH_QUERY_KEYS:
            return "must not contain authenticated URL query parameters"
    return None


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
