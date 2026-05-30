from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_TYPE = "ppd.rollback_activation_decision_packet.v1"

_DECISIONS = {"rollback", "no_rollback"}

_MUTATION_FLAG_KEYS = {
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "guardrail_mutation_active",
    "guardrail_mutation_enabled",
    "monitoring_mutation_active",
    "monitoring_mutation_enabled",
    "mutates_guardrail_bundle",
    "mutates_guardrails",
    "mutates_monitoring",
    "mutates_process_model",
    "mutates_process_models",
    "mutates_processes",
    "mutates_prompt",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_requirements",
    "mutates_source_registry",
    "mutates_sources",
    "mutates_surface_registry",
    "process_mutation_active",
    "process_mutation_enabled",
    "prompt_mutation_active",
    "prompt_mutation_enabled",
    "release_state_mutation_active",
    "release_state_mutation_enabled",
    "requirement_mutation_active",
    "requirement_mutation_enabled",
    "source_mutation_active",
    "source_mutation_enabled",
    "surface_registry_mutation_active",
    "surface_registry_mutation_enabled",
    "writes_active_guardrails",
    "writes_active_monitoring",
    "writes_active_processes",
    "writes_active_prompts",
    "writes_active_release_state",
    "writes_active_requirements",
    "writes_active_sources",
    "writes_active_surface_registry",
}

_RAW_OR_PRIVATE_KEYS = {
    "archive_artifact_ref",
    "archive_path",
    "archive_ref",
    "archive_url",
    "auth_state",
    "browser_state",
    "cookie",
    "credential",
    "download_path",
    "download_ref",
    "download_url",
    "har_path",
    "local_private_path",
    "private_artifact_ref",
    "private_path",
    "raw_archive_ref",
    "raw_body",
    "raw_body_ref",
    "raw_crawl_output",
    "raw_download_ref",
    "session_artifact",
    "session_path",
    "session_state",
    "screenshot_path",
    "storage_state",
    "trace_path",
}

_RAW_OR_PRIVATE_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|(^[A-Za-z]:\\Users\\[^\\]+\\)|"
    r"(auth[_-]?state|browser[_-]?state|cookie|credential|download[_-]?(path|url|ref)?|har|password|"
    r"private[_-]?(artifact|path|url)|raw[_-]?(archive|body|crawl|download|html)|session[_-]?(artifact|path|state)|"
    r"screenshot|secret|storage[_-]?state|token|trace\.zip|warc|\.warc(\.gz)?)",
    re.IGNORECASE,
)

_LIVE_EXECUTION_RE = re.compile(
    r"\b(live\s+(crawl|crawler|devhub|processor|llm|model)|executed\s+(crawler|processor|devhub|llm)|"
    r"invoked\s+(crawler|processor|devhub|llm)|ran\s+(crawler|processor|devhub|llm)|submitted\s+to\s+devhub|"
    r"uploaded\s+to\s+devhub|paid\s+fees?|scheduled\s+inspection|called\s+the\s+llm)\b",
    re.IGNORECASE,
)

_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?\s+(approval|issuance|permit|legal|compliance|outcome)|"
    r"(permit|application|inspection|appeal)\s+(will|shall)\s+be\s+(approved|issued|accepted|granted|upheld)|"
    r"legally\s+guaranteed|guaranteed\s+code\s+compliance)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RollbackActivationDecisionValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


def validate_rollback_activation_decision_packet(packet: Mapping[str, Any]) -> RollbackActivationDecisionValidationResult:
    problems: list[str] = []

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append("packet_type must be ppd.rollback_activation_decision_packet.v1")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")

    decision = packet.get("rollback_decision")
    if decision not in _DECISIONS:
        problems.append("rollback_decision must be either rollback or no_rollback")

    trigger_evaluations = _mapping_sequence(packet.get("trigger_evaluations"))
    if not trigger_evaluations:
        problems.append("trigger_evaluations must include at least one cited trigger evaluation")
    for index, trigger in enumerate(trigger_evaluations):
        if not trigger.get("trigger_id"):
            problems.append(f"trigger_evaluations[{index}] lacks trigger_id")
        if not trigger.get("evaluation"):
            problems.append(f"trigger_evaluations[{index}] lacks evaluation")
        if not _evidence_ids(trigger):
            problems.append(f"trigger_evaluations[{index}] lacks source_evidence_ids")

    owner_acknowledgements = _mapping_sequence(packet.get("owner_acknowledgements"))
    if not owner_acknowledgements:
        problems.append("owner_acknowledgements must include at least one owner acknowledgement")
    for index, acknowledgement in enumerate(owner_acknowledgements):
        if not acknowledgement.get("owner_id"):
            problems.append(f"owner_acknowledgements[{index}] lacks owner_id")
        if acknowledgement.get("acknowledged") is not True:
            problems.append(f"owner_acknowledgements[{index}] must be acknowledged")
        if not acknowledgement.get("acknowledgement"):
            problems.append(f"owner_acknowledgements[{index}] lacks acknowledgement")
        if not _evidence_ids(acknowledgement):
            problems.append(f"owner_acknowledgements[{index}] lacks source_evidence_ids")

    commands = _mapping_sequence(packet.get("offline_validation_commands"))
    if not commands:
        problems.append("offline_validation_commands must include at least one offline validation command")
    for index, command in enumerate(commands):
        if not _command_parts(command.get("command")):
            problems.append(f"offline_validation_commands[{index}] lacks command")
        if "returncode" not in command:
            problems.append(f"offline_validation_commands[{index}] lacks returncode")
        if command.get("offline_only") is not True:
            problems.append(f"offline_validation_commands[{index}] must be marked offline_only")
        if not _evidence_ids(command):
            problems.append(f"offline_validation_commands[{index}] lacks source_evidence_ids")

    problems.extend(_recursive_safety_problems(packet))
    return RollbackActivationDecisionValidationResult(valid=not problems, problems=tuple(_dedupe(problems)))


def assert_valid_rollback_activation_decision_packet(packet: Mapping[str, Any]) -> None:
    result = validate_rollback_activation_decision_packet(packet)
    if not result.valid:
        raise ValueError("invalid_rollback_activation_decision_packet: " + "; ".join(result.problems))


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _evidence_ids(item: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("source_evidence_ids", "citation_ids", "evidence_ids", "validation_evidence_ids"):
        raw = item.get(key)
        if isinstance(raw, str) and raw:
            values.append(raw)
        elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
            values.extend(str(value) for value in raw if str(value))
    return _dedupe(values)


def _command_parts(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(part) for part in value if str(part)]
    return []


def _recursive_safety_problems(value: Any) -> list[str]:
    problems: list[str] = []
    for path, child in _walk(value):
        leaf = _path_leaf(path).lower()
        if isinstance(child, bool) and child is True and leaf in _MUTATION_FLAG_KEYS:
            problems.append(f"active mutation flag must be false at {path}")
        if leaf in _RAW_OR_PRIVATE_KEYS and child not in (None, "", [], {}):
            problems.append(f"raw, download, archive, private, or session artifact reference is not allowed at {path}")
        if isinstance(child, str):
            if _RAW_OR_PRIVATE_RE.search(child):
                problems.append(f"raw, download, archive, private, or session artifact reference is not allowed at {path}")
            if _LIVE_EXECUTION_RE.search(child):
                problems.append(f"live crawler, processor, DevHub, or LLM execution claim is not allowed at {path}")
            if _OUTCOME_GUARANTEE_RE.search(child):
                problems.append(f"legal or permitting outcome guarantee is not allowed at {path}")
    return problems


def _walk(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            rows.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            rows.extend(_walk(child, f"{path}[{index}]"))
    return rows


def _path_leaf(path: str) -> str:
    normalized = path.replace("]", "").replace("[", ".")
    parts = [part for part in normalized.split(".") if part and not part.isdigit() and part != "$"]
    return parts[-1] if parts else ""


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
