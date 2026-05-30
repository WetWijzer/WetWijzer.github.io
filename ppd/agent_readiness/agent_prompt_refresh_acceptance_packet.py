"""Validation for PP&D agent prompt refresh acceptance packets.

Acceptance packets are review artifacts only. They may record accepted,
deferred, or rejected prompt-refresh decisions, but they must not carry private
case facts, raw authenticated values, live execution claims, outcome guarantees,
enabled consequential controls, or active mutation flags.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence


PACKET_TYPE = "ppd.agent_prompt_refresh_acceptance_packet.v1"
_ALLOWED_DECISIONS = {"accepted", "deferred", "rejected"}

_PRIVATE_CASE_FACT_KEYS = {
    "applicant_name",
    "case_fact",
    "case_facts",
    "case_notes",
    "email",
    "phone",
    "private_case_fact",
    "private_case_facts",
    "property_owner",
    "user_case_facts",
}
_RAW_AUTH_VALUE_KEYS = {
    "access_token",
    "auth_state",
    "authenticated_value",
    "browser_state",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "entered_value",
    "field_value",
    "password",
    "raw_authenticated_value",
    "raw_authenticated_values",
    "raw_devhub_value",
    "refresh_token",
    "secret",
    "session_cookie",
    "session_state",
    "storage_state",
    "token",
    "value",
}
_LOCAL_PATH_KEYS = {"download_path", "file_path", "local_file_path", "local_path", "path", "private_file_path"}
_MUTATION_KEY_FRAGMENTS = (
    "agent_state",
    "guardrail",
    "monitoring",
    "prompt",
    "release_state",
    "surface_registry",
    "surface-registry",
)
_CONSEQUENTIAL_CONTROL_WORDS = (
    "cancel",
    "certify",
    "consequential",
    "payment",
    "pay",
    "purchase",
    "schedule",
    "submit",
    "submission",
    "upload",
    "withdraw",
)
_FALSEY_MARKERS = {False, None, "", "disabled", "false", "manual_handoff_required", "not_enabled", "off", "review_only"}

_LOCAL_PRIVATE_PATH_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/private/)|(^~?/\.devhub/)|(^[A-Za-z]:\\Users\\[^\\]+\\)",
    re.IGNORECASE,
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live\s+(llm|devhub|crawl|crawler|processor)|called\s+the\s+llm|opened\s+devhub|"
    r"ran\s+the\s+(crawler|processor)|executed\s+the\s+(crawler|processor)|"
    r"submitted\s+to\s+devhub|uploaded\s+to\s+devhub|paid\s+fees?|scheduled\s+inspection)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?\s+(approval|issuance|permit|legal|compliance|outcome)|"
    r"(permit|application|inspection|appeal)\s+(will|shall)\s+be\s+(approved|issued|accepted|granted|upheld)|"
    r"legally\s+guaranteed|guaranteed\s+code\s+compliance)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AgentPromptRefreshAcceptanceValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


class AgentPromptRefreshAcceptancePacketError(ValueError):
    """Raised when an agent prompt refresh acceptance packet is invalid."""


def validate_agent_prompt_refresh_acceptance_packet(packet: Mapping[str, Any]) -> AgentPromptRefreshAcceptanceValidationResult:
    """Return fail-closed validation for a prompt refresh acceptance packet."""

    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return AgentPromptRefreshAcceptanceValidationResult(False, ("packet must be an object",))

    problems.extend(_unsafe_content_problems(packet))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append("packet_type must be ppd.agent_prompt_refresh_acceptance_packet.v1")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")

    decisions = _mapping_sequence(packet.get("acceptance_decisions"))
    if not decisions:
        problems.append("acceptance_decisions must be a non-empty list")
    for index, decision in enumerate(decisions):
        path = f"acceptance_decisions[{index}]"
        decision_value = str(decision.get("decision") or "").strip().lower()
        if not decision.get("decision_id"):
            problems.append(f"{path}.decision_id is required")
        if decision_value not in _ALLOWED_DECISIONS:
            problems.append(f"{path}.decision must be accepted, deferred, or rejected")
        if not _evidence_ids(decision):
            problems.append(f"{path}.source_evidence_ids is required")
        rationale_key = f"{decision_value}_rationale" if decision_value in _ALLOWED_DECISIONS else "decision_rationale"
        if not _text(decision.get(rationale_key)):
            problems.append(f"{path}.{rationale_key} is required")
        if not _string_list(decision.get("scenario_refs")) and not _string_list(decision.get("blocked_action_refs")):
            problems.append(f"{path} must reference scenario_refs or blocked_action_refs")

    rollback_notes = _mapping_sequence(packet.get("rollback_notes"))
    if not rollback_notes:
        problems.append("rollback_notes must be a non-empty list")
    for index, note in enumerate(rollback_notes):
        if not _text(note.get("note_id")):
            problems.append(f"rollback_notes[{index}].note_id is required")
        if not _text(note.get("instruction")):
            problems.append(f"rollback_notes[{index}].instruction is required")
        if not _evidence_ids(note):
            problems.append(f"rollback_notes[{index}].source_evidence_ids is required")

    reviewer_owners = _mapping_sequence(packet.get("reviewer_owners")) or _mapping_sequence(packet.get("reviewer_owner_fields"))
    if not reviewer_owners:
        problems.append("reviewer_owners must be a non-empty list")
    for index, owner in enumerate(reviewer_owners):
        if not _text(owner.get("owner") or owner.get("reviewer_owner_id") or owner.get("owner_id")):
            problems.append(f"reviewer_owners[{index}].owner is required")
        if not _evidence_ids(owner):
            problems.append(f"reviewer_owners[{index}].source_evidence_ids is required")

    if not _command_sequence(packet.get("offline_validation_commands")):
        problems.append("offline_validation_commands must be a non-empty list of commands")

    return AgentPromptRefreshAcceptanceValidationResult(valid=not problems, problems=tuple(dict.fromkeys(problems)))


def assert_valid_agent_prompt_refresh_acceptance_packet(packet: Mapping[str, Any]) -> None:
    result = validate_agent_prompt_refresh_acceptance_packet(packet)
    if not result.valid:
        raise AgentPromptRefreshAcceptancePacketError("invalid agent prompt refresh acceptance packet: " + "; ".join(result.problems))


def _unsafe_content_problems(value: Any, path: str = "$", key_name: str = "") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized_key in _PRIVATE_CASE_FACT_KEYS and child not in (None, "", [], {}):
                problems.append(f"private case facts are not allowed at {child_path}")
            if normalized_key in _RAW_AUTH_VALUE_KEYS and child not in (None, "", [], {}):
                problems.append(f"raw authenticated values are not allowed at {child_path}")
            if normalized_key in _LOCAL_PATH_KEYS and _contains_local_private_path(child):
                problems.append(f"local private paths are not allowed at {child_path}")
            if _is_enabled_mutation_key(normalized_key, child):
                problems.append(f"active mutation flag is not allowed at {child_path}")
            if _is_enabled_consequential_control(normalized_key, child):
                problems.append(f"enabled consequential controls are not allowed at {child_path}")
            problems.extend(_unsafe_content_problems(child, child_path, normalized_key))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            problems.extend(_unsafe_content_problems(child, f"{path}[{index}]", key_name))
    elif isinstance(value, str):
        if key_name in _LOCAL_PATH_KEYS and _LOCAL_PRIVATE_PATH_RE.search(value):
            problems.append(f"local private paths are not allowed at {path}")
        if _LIVE_EXECUTION_RE.search(value):
            problems.append(f"live LLM, DevHub, crawler, or processor execution claims are not allowed at {path}")
        if _OUTCOME_GUARANTEE_RE.search(value):
            problems.append(f"legal or permitting outcome guarantees are not allowed at {path}")
    return problems


def _is_enabled_mutation_key(key: str, value: Any) -> bool:
    if not any(fragment in key for fragment in _MUTATION_KEY_FRAGMENTS):
        return False
    if not any(marker in key for marker in ("active", "apply", "enable", "enabled", "mutate", "mutation", "write")):
        return False
    return not _is_falsey_marker(value)


def _is_enabled_consequential_control(key: str, value: Any) -> bool:
    if not any(word in key for word in _CONSEQUENTIAL_CONTROL_WORDS):
        return False
    if not any(marker in key for marker in ("active", "allow", "control", "enable", "enabled", "execute", "execution")):
        return False
    return not _is_falsey_marker(value)


def _is_falsey_marker(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in _FALSEY_MARKERS
    return value in _FALSEY_MARKERS


def _contains_local_private_path(value: Any) -> bool:
    if isinstance(value, str):
        return bool(_LOCAL_PRIVATE_PATH_RE.search(value))
    if isinstance(value, Mapping):
        return any(_contains_local_private_path(child) for child in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_local_private_path(child) for child in value)
    return False


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _command_sequence(value: Any) -> list[list[str]]:
    commands: list[list[str]] = []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return commands
    for command in value:
        if isinstance(command, Sequence) and not isinstance(command, (str, bytes)) and all(isinstance(part, str) and part for part in command):
            commands.append(list(command))
    return commands


def _evidence_ids(value: Mapping[str, Any]) -> list[str]:
    return _string_list(value.get("source_evidence_ids") or value.get("source_evidence_id"))


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


__all__ = [
    "AgentPromptRefreshAcceptancePacketError",
    "AgentPromptRefreshAcceptanceValidationResult",
    "PACKET_TYPE",
    "assert_valid_agent_prompt_refresh_acceptance_packet",
    "validate_agent_prompt_refresh_acceptance_packet",
]
