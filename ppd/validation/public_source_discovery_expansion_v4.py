"""Validation for public source discovery expansion packet v4.

The validator is intentionally data-shape tolerant: callers may pass a decoded
JSON object from fixtures, daemon proposals, or handoff packets. It returns a
stable list of human-readable errors rather than mutating the packet.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

_ALLOWED_ALLOWLIST_DECISIONS = {"allow", "skip", "reject", "deny", "blocked"}
_ACTIVE_MUTATION_VALUES = {True, "true", "yes", "on", "enabled", "active"}
_RAW_ARTIFACT_KEYS = {
    "raw_artifacts",
    "downloaded_artifacts",
    "raw_crawl_output",
    "downloads",
    "downloaded_documents",
}
_PRIVATE_ARTIFACT_KEYS = {
    "auth_state",
    "browser_state",
    "browser_artifacts",
    "session_files",
    "session_artifacts",
    "traces",
    "trace_files",
    "cookies",
    "local_storage",
}
_LIVE_CRAWL_TERMS = ("live crawl", "live_crawl", "devhub crawl", "devhub automation")
_LEGAL_GUARANTEE_TERMS = (
    "legal guarantee",
    "permitting guarantee",
    "guaranteed permit",
    "guarantees approval",
    "guaranteed approval",
)


def validate_public_source_discovery_expansion_packet_v4(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a public source discovery expansion packet v4."""

    errors: list[str] = []

    if packet.get("packet_version") not in {4, "4", "v4"}:
        errors.append("packet_version must be v4")

    sources = _as_sequence(packet.get("sources"))
    if not sources:
        errors.append("sources must include at least one public source row")
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            errors.append(f"sources[{index}] must be an object")
            continue
        if not _non_empty_string(source.get("canonical_url")):
            errors.append(f"sources[{index}].canonical_url is required")
        if not _non_empty_string(source.get("source_page")):
            errors.append(f"sources[{index}].source_page evidence is required")
        if not _non_empty_string(source.get("link_text")):
            errors.append(f"sources[{index}].link_text evidence is required")
        decision = source.get("allowlist_decision")
        if not _non_empty_string(decision):
            errors.append(f"sources[{index}].allowlist_decision is required")
        elif str(decision).strip().lower() not in _ALLOWED_ALLOWLIST_DECISIONS:
            errors.append(f"sources[{index}].allowlist_decision is not recognized")
        if _claims_outside_allowlist_promotion(source):
            errors.append(f"sources[{index}] claims promotion outside the public allowlist")

    duplicate_rows = _as_sequence(packet.get("duplicate_normalization"))
    if not duplicate_rows:
        errors.append("duplicate_normalization must include at least one row")
    for index, row in enumerate(duplicate_rows):
        if not isinstance(row, Mapping):
            errors.append(f"duplicate_normalization[{index}] must be an object")
            continue
        if not _non_empty_string(row.get("input_url")):
            errors.append(f"duplicate_normalization[{index}].input_url is required")
        if not _non_empty_string(row.get("normalized_url")):
            errors.append(f"duplicate_normalization[{index}].normalized_url is required")

    skipped_rows = _as_sequence(packet.get("skipped_urls"))
    for index, row in enumerate(skipped_rows):
        if not isinstance(row, Mapping):
            errors.append(f"skipped_urls[{index}] must be an object")
            continue
        if not _non_empty_string(row.get("url")):
            errors.append(f"skipped_urls[{index}].url is required")
        if not _non_empty_string(row.get("reason")):
            errors.append(f"skipped_urls[{index}].reason is required")

    if not _as_sequence(packet.get("validation_commands")):
        errors.append("validation_commands must include at least one command")

    _reject_present_keys(packet, _RAW_ARTIFACT_KEYS, "raw or downloaded artifacts are not allowed", errors)
    _reject_present_keys(packet, _PRIVATE_ARTIFACT_KEYS, "private session/browser artifacts are not allowed", errors)

    if _contains_term(packet, _LIVE_CRAWL_TERMS):
        errors.append("live crawl or DevHub automation claims are not allowed")
    if _contains_term(packet, _LEGAL_GUARANTEE_TERMS):
        errors.append("legal or permitting guarantees are not allowed")
    if _has_active_mutation_flag(packet):
        errors.append("active mutation flags are not allowed")

    return errors


def assert_valid_public_source_discovery_expansion_packet_v4(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when packet v4 validation fails."""

    errors = validate_public_source_discovery_expansion_packet_v4(packet)
    if errors:
        raise ValueError("public source discovery expansion packet v4 failed validation: " + "; ".join(errors))


def _as_sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _reject_present_keys(packet: Mapping[str, Any], keys: set[str], message: str, errors: list[str]) -> None:
    present = sorted(key for key in keys if key in packet and packet.get(key) not in (None, [], {}, ""))
    if present:
        errors.append(f"{message}: {', '.join(present)}")


def _claims_outside_allowlist_promotion(source: Mapping[str, Any]) -> bool:
    if source.get("outside_allowlist_promotion") in _ACTIVE_MUTATION_VALUES:
        return True
    claim = source.get("promotion_claim")
    return isinstance(claim, str) and "outside" in claim.lower() and "allowlist" in claim.lower()


def _has_active_mutation_flag(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized_key = str(key).lower()
            if normalized_key in {"active_mutation", "mutate", "mutation_enabled", "write_enabled"} and child in _ACTIVE_MUTATION_VALUES:
                return True
            if _has_active_mutation_flag(child):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_has_active_mutation_flag(child) for child in value)
    return False


def _contains_term(value: Any, terms: tuple[str, ...]) -> bool:
    if isinstance(value, str):
        normalized = value.lower()
        return any(term in normalized for term in terms)
    if isinstance(value, Mapping):
        return any(_contains_term(child, terms) for child in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_term(child, terms) for child in value)
    return False
