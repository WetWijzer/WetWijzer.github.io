"""Validation for stale-source agent hold packet v1.

This module is intentionally standalone so PP&D retry proposals can validate
hold packets without touching shared contracts or crawl automation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

_REQUIRED_NON_EMPTY = {
    "monitoring_outcome_references": "missing monitoring outcome references",
    "affected_missing_information_rows": "missing affected missing-information rows",
    "blocked_action_rows": "missing blocked-action rows",
    "next_safe_action_rows": "missing next-safe-action rows",
    "citation_warnings": "missing citation warnings",
    "reviewer_holds": "missing reviewer holds",
    "validation_commands": "missing validation commands",
}

_BANNED_TEXT = {
    "private/session/browser/raw/downloaded artifacts": (
        "private artifact",
        "session file",
        "browser state",
        "auth state",
        "trace.zip",
        "raw crawl",
        "raw_crawl",
        "downloaded document",
        "downloaded_documents",
        "downloads/",
        ".har",
        ".storage_state",
    ),
    "live crawl or DevHub claims": (
        "live crawl",
        "live-crawl",
        "crawled live",
        "devhub",
        "dev hub",
        "authenticated automation",
    ),
    "official-action completion claims": (
        "official action completed",
        "official-action completed",
        "submitted to pp&d",
        "submitted to ppd",
        "submission completed",
        "permit action completed",
        "certification completed",
    ),
    "release activation claims": (
        "release activated",
        "activated release",
        "production release active",
        "release is live",
    ),
}

_MUTATION_KEYS = {
    "active_mutation",
    "active_mutations",
    "mutation_active",
    "mutations_enabled",
    "write_enabled",
    "writes_enabled",
    "can_mutate",
    "allow_mutation",
    "mutation_mode",
}

_MUTATION_VALUES = {"active", "enabled", "true", "write", "writes", "mutating", "mutation"}


def validate_stale_source_agent_hold_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a stale-source agent hold packet v1."""
    errors: list[str] = []

    version = packet.get("version") or packet.get("packet_version")
    packet_type = str(packet.get("packet_type") or packet.get("type") or "").lower()
    if version not in (1, "1", "v1"):
        errors.append("missing stale-source agent hold packet v1 version")
    if packet_type and "stale" not in packet_type:
        errors.append("packet type is not stale-source agent hold")

    for key, message in _REQUIRED_NON_EMPTY.items():
        if _is_empty(packet.get(key)):
            errors.append(message)

    flattened = "\n".join(_walk_text(packet)).lower()
    for message, needles in _BANNED_TEXT.items():
        if any(needle in flattened for needle in needles):
            errors.append(message)

    if _has_active_mutation_flag(packet):
        errors.append("active mutation flags")

    return sorted(set(errors))


def assert_valid_stale_source_agent_hold_packet_v1(packet: Mapping[str, Any]) -> None:
    errors = validate_stale_source_agent_hold_packet_v1(packet)
    if errors:
        raise ValueError("invalid stale-source agent hold packet v1: " + "; ".join(errors))


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Mapping):
        return not value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return len(value) == 0
    return False


def _walk_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        out: list[str] = []
        for key, item in value.items():
            out.extend(_walk_text(str(key)))
            out.extend(_walk_text(item))
        return out
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        out = []
        for item in value:
            out.extend(_walk_text(item))
        return out
    return []


def _has_active_mutation_flag(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in _MUTATION_KEYS:
                if item is True:
                    return True
                if isinstance(item, str) and item.strip().lower() in _MUTATION_VALUES:
                    return True
                if isinstance(item, Sequence) and not isinstance(item, (bytes, bytearray, str)) and len(item) > 0:
                    return True
            if _has_active_mutation_flag(item):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return any(_has_active_mutation_flag(item) for item in value)
    return False
