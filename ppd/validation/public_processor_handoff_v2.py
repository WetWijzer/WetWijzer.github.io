"""Validation for public processor handoff packet v2.

The public processor handoff packet is intentionally evidence-only. It may carry
placeholders and validation metadata, but it must not carry private automation
state, raw downloaded content, live-crawl assertions, legal guarantees, or active
mutation requests.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


_MUTATION_FLAG_KEYS = (
    "active_crawler_mutation",
    "active_source_mutation",
    "active_archive_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "mutate_crawlers",
    "mutate_sources",
    "mutate_archives",
    "mutate_documents",
    "mutate_requirements",
    "mutate_guardrails",
    "mutate_prompts",
    "mutate_release_state",
)

_PRIVATE_ARTIFACT_TERMS = (
    "private",
    "session",
    "browser",
    "auth",
    "trace",
    "raw",
    "downloaded",
    "devhub_session",
)

_GUARANTEE_TERMS = (
    "guarantee",
    "guaranteed",
    "certify",
    "certified",
    "legal advice",
    "permit approval",
    "permitting approval",
    "will be approved",
)


class PublicProcessorHandoffV2ValidationError(ValueError):
    """Raised when a public processor handoff packet v2 is invalid."""


def validate_public_processor_handoff_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a public processor handoff packet v2."""

    errors: list[str] = []

    if packet.get("packet_version") != 2:
        errors.append("packet_version must be 2")

    _require_non_empty(packet, "allowlist_decisions", errors)
    _require_non_empty(packet, "robots_preflight_evidence", errors)
    _require_non_empty(packet, "policy_preflight_evidence", errors)
    _require_non_empty(packet, "archive_manifest_placeholders", errors)
    _require_non_empty(packet, "normalized_document_placeholders", errors)
    _require_non_empty(packet, "validation_commands", errors)

    if packet.get("no_raw_body") is not True:
        errors.append("no_raw_body must be true")

    skipped_items = packet.get("skipped_items")
    if not _is_non_empty_sequence(skipped_items):
        errors.append("skipped_items must be a non-empty list with reasons")
    else:
        for index, item in enumerate(skipped_items):
            if not isinstance(item, Mapping) or not str(item.get("reason", "")).strip():
                errors.append(f"skipped_items[{index}] must include a non-empty reason")

    artifacts = packet.get("artifacts", [])
    if artifacts is None:
        artifacts = []
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
        errors.append("artifacts must be a list when present")
    else:
        for index, artifact in enumerate(artifacts):
            artifact_text = _artifact_text(artifact).lower()
            for term in _PRIVATE_ARTIFACT_TERMS:
                if term in artifact_text:
                    errors.append(f"artifacts[{index}] references disallowed {term} artifact")
                    break

    if packet.get("live_crawl") is True or packet.get("live_crawl_claim") is True:
        errors.append("live crawl claims are not allowed")

    for key in _MUTATION_FLAG_KEYS:
        if packet.get(key) is True:
            errors.append(f"{key} must not be true")

    packet_text = _walk_text(packet).lower()
    for term in _GUARANTEE_TERMS:
        if term in packet_text:
            errors.append(f"legal or permitting guarantee is not allowed: {term}")
            break

    return errors


def assert_valid_public_processor_handoff_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise when a public processor handoff packet v2 is invalid."""

    errors = validate_public_processor_handoff_packet_v2(packet)
    if errors:
        raise PublicProcessorHandoffV2ValidationError("; ".join(errors))


def _require_non_empty(packet: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if not _is_non_empty(packet.get(key)):
        errors.append(f"{key} is required")


def _is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return len(value) > 0
    return True


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _artifact_text(artifact: Any) -> str:
    if isinstance(artifact, Mapping):
        return " ".join(str(value) for value in artifact.values())
    return str(artifact)


def _walk_text(value: Any) -> str:
    parts: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            parts.append(str(key))
            parts.append(_walk_text(item))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            parts.append(_walk_text(item))
    else:
        parts.append(str(value))
    return " ".join(parts)
