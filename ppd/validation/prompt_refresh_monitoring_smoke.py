"""Validation for PP&D prompt refresh monitoring smoke transcript packets.

The validator is intentionally narrow and deterministic. It accepts already-built
packet dictionaries and rejects transcript content that would imply unsupported
monitoring authority, live execution, private/authenticated facts, raw crawl
material, or active state mutation.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

MUTATION_SURFACES = (
    "source",
    "schedule",
    "prompt",
    "guardrail",
    "surface_registry",
    "monitoring",
    "release_state",
    "agent_state",
)

_ALLOWED_COMMANDS = {
    "python3 ppd/daemon/ppd_daemon.py --self-test",
    "python3 -m pytest ppd/tests/test_prompt_refresh_monitoring_smoke.py",
}

_PRIVATE_OR_AUTH_PATTERNS = (
    re.compile(r"\b(authenticated|private|nonpublic|logged[- ]?in|session|cookie|bearer token|api key|password|secret)\b", re.I),
    re.compile(r"\bDevHub\b.*\b(account|case|permit|record|session|authenticated|private)\b", re.I),
)

_RAW_CRAWL_PATTERNS = (
    re.compile(r"\b(raw crawl output|raw html|dom dump|page source|crawler log|network trace|screenshot bytes)\b", re.I),
    re.compile(r"]", re.I),
)

_LIVE_EXECUTION_PATTERNS = (
    re.compile(r"\b(live|real[- ]?time|production)\b.*\b(monitoring|crawler|processor|DevHub|LLM)\b", re.I),
    re.compile(r"\b(ran|executed|started|launched|queried)\b.*\b(crawler|processor|DevHub|LLM|live monitoring)\b", re.I),
)

_OUTCOME_GUARANTEE_PATTERNS = (
    re.compile(r"\b(guarantee|guaranteed|will be approved|approval assured|permit will issue|legally sufficient)\b", re.I),
    re.compile(r"\b(no appeal risk|no legal risk|certain permitting outcome)\b", re.I),
)

_RAW_CRAWL_KEYS = {
    "raw_crawl_output",
    "raw_html",
    "html",
    "dom_dump",
    "page_source",
    "network_trace",
    "screenshot_bytes",
    "crawler_log",
}


def validate_packet(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a prompt refresh monitoring smoke packet."""
    errors: list[str] = []

    _validate_observations(packet, errors)
    _validate_escalation_decision(packet, errors)
    _validate_rollback_trigger_checks(packet, errors)
    _validate_allowed_validation_commands(packet, errors)
    _validate_text_and_keys(packet, errors)
    _validate_mutation_flags(packet, errors)

    return errors


def assert_valid_packet(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the packet fails validation."""
    errors = validate_packet(packet)
    if errors:
        raise ValueError("; ".join(errors))


def _validate_observations(packet: Mapping[str, Any], errors: list[str]) -> None:
    observations = packet.get("observations")
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)) or not observations:
        errors.append("observations must be a non-empty list")
        return

    for index, observation in enumerate(observations):
        if not isinstance(observation, Mapping):
            errors.append(f"observations[{index}] must be an object")
            continue
        citations = observation.get("citations") or observation.get("source_refs")
        if not isinstance(citations, Sequence) or isinstance(citations, (str, bytes)) or not citations:
            errors.append(f"observations[{index}] is missing citations")


def _validate_escalation_decision(packet: Mapping[str, Any], errors: list[str]) -> None:
    decision = packet.get("escalation_decision")
    if not isinstance(decision, Mapping):
        errors.append("escalation_decision is required")
        return
    if not decision.get("decision"):
        errors.append("escalation_decision.decision is required")
    if not decision.get("rationale"):
        errors.append("escalation_decision.rationale is required")


def _validate_rollback_trigger_checks(packet: Mapping[str, Any], errors: list[str]) -> None:
    checks = packet.get("rollback_trigger_checks")
    if not isinstance(checks, Sequence) or isinstance(checks, (str, bytes)) or not checks:
        errors.append("rollback_trigger_checks must be a non-empty list")
        return
    for index, check in enumerate(checks):
        if not isinstance(check, Mapping):
            errors.append(f"rollback_trigger_checks[{index}] must be an object")
            continue
        if check.get("checked") is not True:
            errors.append(f"rollback_trigger_checks[{index}].checked must be true")


def _validate_allowed_validation_commands(packet: Mapping[str, Any], errors: list[str]) -> None:
    commands = packet.get("allowed_validation_commands")
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes)) or not commands:
        errors.append("allowed_validation_commands must be a non-empty list")
        return
    for index, command in enumerate(commands):
        command_text = _command_to_text(command)
        if command_text not in _ALLOWED_COMMANDS:
            errors.append(f"allowed_validation_commands[{index}] is not an approved deterministic command")


def _validate_text_and_keys(value: Any, errors: list[str], path: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.replace("-", "_")
            if normalized_key in _RAW_CRAWL_KEYS:
                errors.append(f"{path}.{key_text} contains raw crawl output")
            _validate_text_and_keys(child, errors, f"{path}.{key_text}")
        return

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _validate_text_and_keys(child, errors, f"{path}[{index}]")
        return

    if isinstance(value, bytes):
        errors.append(f"{path} contains raw binary crawl output")
        return

    if isinstance(value, str):
        _reject_patterns(value, path, _PRIVATE_OR_AUTH_PATTERNS, "private or authenticated fact", errors)
        _reject_patterns(value, path, _RAW_CRAWL_PATTERNS, "raw crawl output", errors)
        _reject_patterns(value, path, _LIVE_EXECUTION_PATTERNS, "live execution claim", errors)
        _reject_patterns(value, path, _OUTCOME_GUARANTEE_PATTERNS, "legal or permitting outcome guarantee", errors)


def _validate_mutation_flags(packet: Mapping[str, Any], errors: list[str]) -> None:
    for surface in MUTATION_SURFACES:
        candidate_keys = (
            f"mutate_{surface}",
            f"{surface}_mutation",
            f"active_{surface}_mutation",
            f"enable_{surface}_mutation",
            f"write_{surface}",
        )
        for key in candidate_keys:
            if packet.get(key) is True:
                errors.append(f"{key} must not be true")

    flags = packet.get("mutation_flags")
    if isinstance(flags, Mapping):
        for surface in MUTATION_SURFACES:
            if flags.get(surface) is True:
                errors.append(f"mutation_flags.{surface} must not be true")


def _reject_patterns(text: str, path: str, patterns: Sequence[re.Pattern[str]], label: str, errors: list[str]) -> None:
    if any(pattern.search(text) for pattern in patterns):
        errors.append(f"{path} contains {label}")


def _command_to_text(command: Any) -> str:
    if isinstance(command, str):
        return " ".join(command.split())
    if isinstance(command, Sequence) and not isinstance(command, (bytes, str)):
        return " ".join(str(part) for part in command)
    return str(command)
