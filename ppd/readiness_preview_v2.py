"""Validation for reversible draft preview readiness packet v2.

This module is intentionally deterministic and offline-only. It validates the
preview readiness packet shape and rejects language or flags that would imply
private facts, authenticated values, live execution, final actions, guarantees,
or mutable process state.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

_REQUIRED_SECTIONS = (
    "readiness_decisions",
    "required_fact_checks",
    "missing_document_checks",
    "reversible_action_predicates",
    "exact_confirmation_checkpoints",
)

_MUTATION_FLAGS = {
    "active_pdf_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_gap_analysis_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "pdf_mutation_active",
    "guardrail_mutation_active",
    "process_mutation_active",
    "gap_analysis_mutation_active",
    "prompt_mutation_active",
    "release_state_mutation_active",
    "agent_state_mutation_active",
}

_PRIVATE_FACT_RE = re.compile(
    r"\b(private case fact|applicant ssn|social security|date of birth|dob|"
    r"driver'?s license|bank account|routing number)\b",
    re.IGNORECASE,
)

_LOCAL_PATH_RE = re.compile(
    r"(?:file://|\b[A-Za-z]:\\|/(?:Users|home|var/folders|tmp)/|\\\\[^\\]+\\[^\\]+)",
    re.IGNORECASE,
)

_AUTH_VALUE_RE = re.compile(
    r"\b(cookie|set-cookie|bearer\s+[a-z0-9._~+/=-]+|access[_-]?token|"
    r"refresh[_-]?token|id[_-]?token|auth[_-]?state|session[_-]?(?:id|token)|"
    r"csrf[_-]?token|password|api[_-]?key|secret)\b",
    re.IGNORECASE,
)

_LIVE_EXECUTION_RE = re.compile(
    r"\b(live devhub|opened browser|launched browser|browser session|"
    r"called the llm|llm run|crawler executed|ran crawler|processor executed|"
    r"ran processor|scraped live|downloaded from devhub|authenticated crawl)\b",
    re.IGNORECASE,
)

_GUARANTEE_RE = re.compile(
    r"\b(guarantee(?:d|s)?|will be approved|approval is certain|permit will issue|"
    r"legally sufficient|compliance guaranteed|no legal risk)\b",
    re.IGNORECASE,
)

_FINAL_ACTION_RE = re.compile(
    r"\b(final(?:ly)?\s+(?:submit|submitted|submission|pay|paid|payment|upload|"
    r"schedule|scheduled|cancel|cancelled|canceled)|submit(?:ted)?\s+to\s+devhub|"
    r"pay(?:ment)?\s+completed|uploaded\s+documents|scheduled\s+inspection|"
    r"cancelled\s+permit|canceled\s+permit)\b",
    re.IGNORECASE,
)


def validate_reversible_draft_preview_readiness_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a reversible draft preview readiness packet."""
    errors: list[str] = []

    if not isinstance(packet, Mapping):
        return ["packet must be a mapping"]

    for section in _REQUIRED_SECTIONS:
        value = packet.get(section)
        if not isinstance(value, list) or not value:
            errors.append(f"{section} must be a non-empty list")

    _validate_cited_items(packet, "readiness_decisions", errors)
    _validate_cited_items(packet, "required_fact_checks", errors)
    _validate_cited_items(packet, "missing_document_checks", errors)
    _validate_reversible_action_predicates(packet, errors)
    _validate_exact_confirmation_checkpoints(packet, errors)
    _validate_mutation_flags(packet, errors)
    _validate_text_guards(packet, errors)

    return errors


def assert_reversible_draft_preview_readiness_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the packet is not preview-ready."""
    errors = validate_reversible_draft_preview_readiness_packet_v2(packet)
    if errors:
        raise ValueError("reversible draft preview readiness packet v2 rejected: " + "; ".join(errors))


def _validate_cited_items(packet: Mapping[str, Any], section: str, errors: list[str]) -> None:
    value = packet.get(section)
    if not isinstance(value, list):
        return
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"{section}[{index}] must be a mapping")
            continue
        if not _has_citation(item):
            errors.append(f"{section}[{index}] must include citations")


def _validate_reversible_action_predicates(packet: Mapping[str, Any], errors: list[str]) -> None:
    value = packet.get("reversible_action_predicates")
    if not isinstance(value, list):
        return
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"reversible_action_predicates[{index}] must be a mapping")
            continue
        if item.get("satisfied") is not True and item.get("reversible") is not True:
            errors.append(f"reversible_action_predicates[{index}] must affirm reversibility")
        if not _has_citation(item):
            errors.append(f"reversible_action_predicates[{index}] must include citations")


def _validate_exact_confirmation_checkpoints(packet: Mapping[str, Any], errors: list[str]) -> None:
    value = packet.get("exact_confirmation_checkpoints")
    if not isinstance(value, list):
        return
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"exact_confirmation_checkpoints[{index}] must be a mapping")
            continue
        if item.get("exact_confirmation") is not True and item.get("confirmed") is not True:
            errors.append(f"exact_confirmation_checkpoints[{index}] must affirm exact confirmation")
        if not _has_citation(item):
            errors.append(f"exact_confirmation_checkpoints[{index}] must include citations")


def _validate_mutation_flags(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        key = path[-1] if path else ""
        if key in _MUTATION_FLAGS and value is True:
            errors.append(f"{'.'.join(path)} must not be active")
        if isinstance(value, Mapping):
            for flag in _MUTATION_FLAGS:
                if value.get(flag) is True:
                    errors.append(f"{'.'.join(path + (flag,))} must not be active")


def _validate_text_guards(packet: Mapping[str, Any], errors: list[str]) -> None:
    checks = (
        (_PRIVATE_FACT_RE, "private case facts are not allowed"),
        (_LOCAL_PATH_RE, "local private document paths are not allowed"),
        (_AUTH_VALUE_RE, "raw authenticated values are not allowed"),
        (_LIVE_EXECUTION_RE, "live DevHub/browser/LLM/crawler/processor execution claims are not allowed"),
        (_GUARANTEE_RE, "legal or permitting outcome guarantees are not allowed"),
        (_FINAL_ACTION_RE, "final submission/payment/upload/scheduling/cancellation language is not allowed"),
    )
    for path, value in _walk(packet):
        if not isinstance(value, str):
            continue
        for pattern, message in checks:
            if pattern.search(value):
                errors.append(f"{'.'.join(path)}: {message}")


def _has_citation(item: Mapping[str, Any]) -> bool:
    citations = item.get("citations", item.get("citation"))
    if isinstance(citations, str):
        return bool(citations.strip())
    if isinstance(citations, Iterable):
        return any(isinstance(citation, str) and citation.strip() for citation in citations)
    return False


def _walk(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, path + (str(index),))
