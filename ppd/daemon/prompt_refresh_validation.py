"""Validation for agent prompt refresh candidate packets.

The validator is intentionally schema-tolerant because supervisor candidate packets may
arrive from multiple producers during isolated PP&D implementation work. It enforces
non-negotiable safety properties without requiring live DevHub, crawler, processor, or
LLM execution.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


_PATH_PATTERN = re.compile(
    r"(?i)(?:file://|/(?:home|users|var/folders|private|tmp)/[^\s,;]+|[a-z]:\\\\users\\\\[^\s,;]+)"
)

_PRIVATE_FACT_KEYS = {
    "address",
    "applicant",
    "case_fact",
    "case_facts",
    "customer",
    "email",
    "known_facts",
    "owner",
    "parcel",
    "permit_number",
    "phone",
    "private_case_facts",
    "project_address",
    "property",
    "site_address",
}

_AUTH_VALUE_KEYS = {
    "access_token",
    "auth_state",
    "authenticated_value",
    "authenticated_values",
    "authorization",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_raw_value",
    "har",
    "id_token",
    "password",
    "raw_authenticated_value",
    "raw_authenticated_values",
    "refresh_token",
    "secret",
    "session",
    "session_state",
    "trace",
}

_MUTATION_FLAGS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation_enabled",
    "guardrail_mutation_enabled",
    "monitoring_mutation_enabled",
    "mutate_agent_state",
    "mutate_guardrails",
    "mutate_monitoring",
    "mutate_prompt",
    "mutate_surface_registry",
    "prompt_mutation_enabled",
    "surface_registry_mutation_enabled",
}

_LIVE_EXECUTION_PATTERN = re.compile(
    r"(?i)\b("
    r"called\s+(?:the\s+)?(?:llm|devhub|crawler|processor)|"
    r"executed\s+(?:against\s+)?(?:devhub|crawler|processor|live)|"
    r"ran\s+(?:the\s+)?(?:llm|devhub|crawler|processor|live)|"
    r"live\s+(?:llm|devhub|crawl|crawler|processor|execution|run)|"
    r"submitted\s+(?:to\s+)?devhub|"
    r"uploaded\s+(?:to\s+)?devhub|"
    r"scheduled\s+(?:an\s+)?inspection|"
    r"paid\s+(?:a\s+)?fee"
    r")\b"
)

_GUARANTEE_PATTERN = re.compile(
    r"(?i)\b("
    r"approval\s+is\s+guaranteed|"
    r"guarantee(?:d|s)?\s+(?:approval|issuance|compliance|permit|legal|outcome)|"
    r"legally\s+compliant\s+without\s+review|"
    r"permit\s+will\s+be\s+(?:approved|issued)|"
    r"will\s+pass\s+(?:inspection|review)|"
    r"will\s+be\s+approved"
    r")\b"
)

_LIVE_COMMAND_TOKENS = {
    "crawl",
    "crawler",
    "devhub",
    "hf",
    "llm",
    "playwright",
    "processor",
    "scrape",
}

_PLACEHOLDER_OWNERS = {"", "owner", "reviewer", "tbd", "todo", "unknown", "none"}


@dataclass(frozen=True)
class PromptRefreshValidationReport:
    """Result of prompt refresh packet validation."""

    ok: bool
    errors: tuple[str, ...]

    def raise_for_errors(self) -> None:
        if not self.ok:
            raise ValueError("prompt refresh packet rejected: " + "; ".join(self.errors))


def validate_prompt_refresh_candidate_packet(packet: Mapping[str, Any]) -> PromptRefreshValidationReport:
    """Return validation errors for a PP&D agent prompt refresh candidate packet."""

    errors: list[str] = []

    if not isinstance(packet, Mapping):
        return PromptRefreshValidationReport(False, ("packet must be a mapping",))

    _validate_prompt_change_candidates(packet, errors)
    _require_non_empty_reference(packet, errors, ("supported_scenario_refs", "supported_scenarios"), "supported scenario references")
    _require_non_empty_reference(packet, errors, ("blocked_scenario_refs", "blocked_scenarios"), "blocked scenario references")
    _require_non_empty_reference(packet, errors, ("rollback_notes", "rollback_plan"), "rollback notes")
    _require_reviewer_owners(packet, errors)
    _require_offline_validation_commands(packet, errors)
    _reject_sensitive_material(packet, errors)
    _reject_live_execution_claims(packet, errors)
    _reject_outcome_guarantees(packet, errors)
    _reject_consequential_controls(packet, errors)
    _reject_mutation_flags(packet, errors)

    return PromptRefreshValidationReport(not errors, tuple(errors))


def assert_valid_prompt_refresh_candidate_packet(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a packet violates PP&D prompt refresh rules."""

    validate_prompt_refresh_candidate_packet(packet).raise_for_errors()


def _validate_prompt_change_candidates(packet: Mapping[str, Any], errors: list[str]) -> None:
    candidates = packet.get("prompt_change_candidates", packet.get("candidates", ()))
    if not _is_non_empty_sequence(candidates):
        errors.append("prompt-change candidates are required")
        return

    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, Mapping):
            errors.append(f"prompt-change candidate {index} must be a mapping")
            continue
        if not _has_citation(candidate):
            errors.append(f"prompt-change candidate {index} is missing citations or source evidence")


def _require_non_empty_reference(
    packet: Mapping[str, Any],
    errors: list[str],
    keys: Sequence[str],
    label: str,
) -> None:
    for key in keys:
        if _meaningful(packet.get(key)):
            return
    errors.append(f"missing {label}")


def _require_reviewer_owners(packet: Mapping[str, Any], errors: list[str]) -> None:
    owners = packet.get("reviewer_owners", packet.get("reviewers", packet.get("owners")))
    if not _is_non_empty_sequence(owners):
        errors.append("missing reviewer owners")
        return

    for owner in owners:
        normalized = str(owner).strip().lower()
        if normalized in _PLACEHOLDER_OWNERS:
            errors.append("reviewer owners must be concrete non-placeholder values")
            return


def _require_offline_validation_commands(packet: Mapping[str, Any], errors: list[str]) -> None:
    commands = packet.get("offline_validation_commands", packet.get("validation_commands"))
    if not _is_non_empty_sequence(commands):
        errors.append("missing offline validation commands")
        return

    for command in commands:
        tokens = _command_tokens(command)
        if not tokens:
            errors.append("offline validation commands must contain command tokens")
            continue
        lowered = {token.lower() for token in tokens}
        if lowered & _LIVE_COMMAND_TOKENS:
            errors.append("offline validation commands must not invoke live LLM, DevHub, crawler, or processor execution")


def _reject_sensitive_material(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, key, value in _walk(packet):
        lowered_key = key.lower()
        if lowered_key in _AUTH_VALUE_KEYS and _meaningful(value):
            errors.append(f"raw authenticated value is not allowed at {path}")
        if lowered_key in _PRIVATE_FACT_KEYS and _contains_unredacted_private_value(value):
            errors.append(f"private case fact is not allowed at {path}")
        if isinstance(value, str) and _PATH_PATTERN.search(value):
            errors.append(f"local private path is not allowed at {path}")


def _reject_live_execution_claims(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, _key, value in _walk(packet):
        if isinstance(value, str) and _LIVE_EXECUTION_PATTERN.search(value):
            errors.append(f"live LLM, DevHub, crawler, or processor execution claim is not allowed at {path}")


def _reject_outcome_guarantees(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, _key, value in _walk(packet):
        if isinstance(value, str) and _GUARANTEE_PATTERN.search(value):
            errors.append(f"legal or permitting outcome guarantee is not allowed at {path}")


def _reject_consequential_controls(packet: Mapping[str, Any], errors: list[str]) -> None:
    controls = packet.get("consequential_controls", packet.get("controls"))
    if isinstance(controls, Mapping):
        for name, value in controls.items():
            if _is_enabled(value):
                errors.append(f"consequential control must not be enabled: {name}")
    elif _is_enabled(controls):
        errors.append("consequential controls must not be enabled")


def _reject_mutation_flags(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, key, value in _walk(packet):
        if key.lower() in _MUTATION_FLAGS and _is_enabled(value):
            errors.append(f"active mutation flag is not allowed at {path}")


def _has_citation(candidate: Mapping[str, Any]) -> bool:
    citation_keys = (
        "citation_refs",
        "citations",
        "source_evidence_ids",
        "source_refs",
        "evidence_refs",
    )
    return any(_meaningful(candidate.get(key)) for key in citation_keys)


def _meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)


def _contains_unredacted_private_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        stripped = value.strip().lower()
        return bool(stripped) and stripped not in {"redacted", "[redacted]", "", "not collected"}
    if isinstance(value, Mapping):
        return any(_contains_unredacted_private_value(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_unredacted_private_value(item) for item in value)
    return True


def _command_tokens(command: Any) -> tuple[str, ...]:
    if isinstance(command, str):
        return tuple(part for part in command.split() if part)
    if isinstance(command, Sequence) and not isinstance(command, (bytes, bytearray)):
        return tuple(str(part) for part in command if str(part).strip())
    return ()


def _is_enabled(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "enabled", "on", "true", "yes"}
    if isinstance(value, Mapping):
        return any(_is_enabled(item) for item in value.values())
    return False


def _walk(value: Any, path: str = "$", key: str = "") -> Iterable[tuple[str, str, Any]]:
    yield path, key, value
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            yield from _walk(child_value, f"{path}.{child_key_text}", child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child_value in enumerate(value):
            yield from _walk(child_value, f"{path}[{index}]", key)
