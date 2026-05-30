"""Validation for offline PP&D release candidate checklist packets.

The checklist validator is intentionally metadata-only. It verifies that a
release candidate review packet is fully cited, owner-assigned, tied back to
consumed packets, and free of live execution claims or mutation controls.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


PACKET_TYPE = "ppd.offline_release_candidate_validation_checklist.v1"

_GATE_DECISIONS = {"go", "no_go", "blocked", "needs_review"}
_CLOSED_BLOCKER_DISPOSITIONS = {
    "accepted_blocker",
    "deferred_with_owner",
    "resolved_by_fixture",
    "not_applicable_with_citation",
    "no_go_blocker",
}

_RAW_OR_PRIVATE_KEYS = {
    "archive_artifact_ref",
    "archive_path",
    "archive_ref",
    "archive_url",
    "auth_state",
    "authenticated_url",
    "browser_state",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session",
    "download_path",
    "download_ref",
    "download_url",
    "downloaded_document_path",
    "field_value",
    "har",
    "local_path",
    "password",
    "private_artifact",
    "private_path",
    "private_url",
    "private_value",
    "raw_archive_ref",
    "raw_body",
    "raw_body_ref",
    "raw_crawl_output",
    "raw_download_ref",
    "raw_html",
    "raw_value",
    "screenshot",
    "secret",
    "session",
    "session_cookie",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "value",
    "warc_path",
}

_LIVE_EXECUTION_KEYS = {
    "calls_llm",
    "devhub_execution_performed",
    "devhub_run_performed",
    "launch_devhub",
    "live_actions_performed",
    "live_crawl_executed",
    "live_crawler_executed",
    "live_devhub_execution",
    "live_llm_execution",
    "live_network_called",
    "live_network_execution",
    "live_processor_execution",
    "llm_execution_performed",
    "processor_execution_performed",
    "uses_authenticated_session",
}

_MUTATION_KEYS = {
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "apply_source_update",
    "commit_to_registry",
    "guardrail_mutation_active",
    "guardrail_promotion_enabled",
    "mutate_guardrail_bundle",
    "mutate_process_model",
    "mutate_prompt",
    "mutate_registry",
    "mutate_release_state",
    "mutate_requirement",
    "mutate_source",
    "mutate_surface_registry",
    "process_mutation_active",
    "prompt_mutation_active",
    "release_state_mutation_active",
    "requirement_mutation_active",
    "source_mutation_active",
    "surface_registry_mutation_active",
    "write_active_guardrails",
    "write_active_process_model",
    "write_active_prompts",
    "write_active_registry",
    "write_active_release_state",
    "write_active_requirements",
    "write_active_sources",
    "write_active_surface_registry",
}

_RAW_OR_PRIVATE_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|"
    r"(^[A-Za-z]:\\Users\\[^\\]+\\)|"
    r"(https?://[^\s?#]+/(?:auth|authenticated|private|session|download|downloads|archive|archives|raw)(?:[/?#]|$))|"
    r"(https?://[^\s?#]+[^\s]*(?:[?&](?:access_token|auth|password|session|token)=))|"
    r"(auth[_-]?state|browser[_-]?state|cookie|credential|har|password|raw[_-]?(body|crawl|html)|"
    r"session[_-]?state|screenshot|secret|storage[_-]?state|token|trace\.zip|warc)",
    re.IGNORECASE,
)

_LIVE_EXECUTION_TEXT_RE = re.compile(
    r"\b(live\s+(crawl|crawler|processor|devhub|llm|network)|"
    r"ran\s+(the\s+)?live\s+(crawler|processor|devhub|llm)|"
    r"executed\s+(the\s+)?live\s+(crawler|processor|devhub|llm)|"
    r"devhub\s+(automation|session)\s+(ran|executed|completed)|"
    r"llm\s+(call|execution)\s+(ran|executed|completed)|"
    r"submitted\s+to\s+devhub|uploaded\s+to\s+devhub|paid\s+fees?|scheduled\s+inspection|certified\s+application)\b",
    re.IGNORECASE,
)

_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?\s+(approval|issuance|permit|legal|compliance|outcome)|"
    r"(permit|application|inspection|appeal)\s+(will|shall)\s+be\s+(approved|issued|accepted|granted|upheld)|"
    r"legally\s+guaranteed|guaranteed\s+code\s+compliance|permitting\s+outcome\s+guarantee)\b",
    re.IGNORECASE,
)

_LIVE_COMMAND_RE = re.compile(
    r"\b(curl|wget|playwright|devhub|crawl|crawler|scrape|processor|llm|openai|anthropic)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OfflineReleaseCandidateValidationChecklistResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


def validate_offline_release_candidate_validation_checklist(
    packet: Mapping[str, Any],
) -> OfflineReleaseCandidateValidationChecklistResult:
    problems: list[str] = []
    problems.extend(_walk_safety_errors(packet, "$"))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if packet.get("metadata_only") is not True:
        problems.append("metadata_only must be true")

    consumed_packets = _mapping_sequence(packet.get("consumed_packets"))
    consumed_ids = _consumed_packet_ids(consumed_packets, problems)
    if not consumed_ids:
        problems.append("consumed_packets must include at least one packet reference")

    reviewer_owner_ids = _reviewer_owner_ids(packet.get("reviewer_owners"), problems)
    gates = _mapping_sequence(packet.get("go_no_go_gates"))
    if not gates:
        problems.append("go_no_go_gates must include at least one cited gate")
    for index, gate in enumerate(gates):
        path = f"go_no_go_gates[{index}]"
        _require_identifier(gate, "gate_id", path, problems)
        if gate.get("decision") not in _GATE_DECISIONS:
            problems.append(f"{path}.decision must be one of {sorted(_GATE_DECISIONS)}")
        _require_citations(gate, path, problems)
        _require_consumed_packet_refs(gate, path, consumed_ids, problems)
        _require_owner(gate, path, reviewer_owner_ids, problems)

    residual_blockers = _mapping_sequence(packet.get("residual_blockers"))
    blocker_dispositions = _mapping_sequence(packet.get("residual_blocker_dispositions"))
    disposition_ids = {str(item.get("blocker_id") or "") for item in blocker_dispositions}
    for blocker in residual_blockers:
        blocker_id = str(blocker.get("blocker_id") or "")
        if blocker_id and blocker_id not in disposition_ids:
            problems.append(f"residual_blocker_dispositions missing blocker_id {blocker_id}")
    if residual_blockers and not blocker_dispositions:
        problems.append("residual_blocker_dispositions must cover residual_blockers")
    for index, disposition in enumerate(blocker_dispositions):
        path = f"residual_blocker_dispositions[{index}]"
        _require_identifier(disposition, "blocker_id", path, problems)
        if disposition.get("disposition") not in _CLOSED_BLOCKER_DISPOSITIONS:
            problems.append(f"{path}.disposition must be a closed cited disposition")
        _require_citations(disposition, path, problems)
        _require_consumed_packet_refs(disposition, path, consumed_ids, problems)
        _require_owner(disposition, path, reviewer_owner_ids, problems)

    rollback_drills = _mapping_sequence(packet.get("rollback_drill_references"))
    if not rollback_drills:
        problems.append("rollback_drill_references must include at least one rollback drill reference")
    for index, drill in enumerate(rollback_drills):
        path = f"rollback_drill_references[{index}]"
        _require_identifier(drill, "rollback_drill_id", path, problems)
        _require_citations(drill, path, problems)
        _require_consumed_packet_refs(drill, path, consumed_ids, problems)
        _require_owner(drill, path, reviewer_owner_ids, problems)

    commands = _mapping_sequence(packet.get("offline_validation_commands"))
    if not commands:
        problems.append("offline_validation_commands must include at least one offline validation command")
    for index, command_ref in enumerate(commands):
        path = f"offline_validation_commands[{index}]"
        _require_identifier(command_ref, "command_id", path, problems)
        command = _command_parts(command_ref.get("command"))
        if not command:
            problems.append(f"{path}.command must be a non-empty list or string")
        elif _LIVE_COMMAND_RE.search(" ".join(command)):
            problems.append(f"{path}.command must be offline and must not invoke live crawlers, processors, DevHub, or LLMs")
        _require_citations(command_ref, path, problems)
        _require_consumed_packet_refs(command_ref, path, consumed_ids, problems)
        _require_owner(command_ref, path, reviewer_owner_ids, problems)

    return OfflineReleaseCandidateValidationChecklistResult(valid=not problems, problems=tuple(_dedupe(problems)))


def assert_valid_offline_release_candidate_validation_checklist(packet: Mapping[str, Any]) -> None:
    result = validate_offline_release_candidate_validation_checklist(packet)
    if not result.valid:
        raise ValueError("invalid offline release candidate validation checklist: " + "; ".join(result.problems))


def _consumed_packet_ids(consumed_packets: Sequence[Mapping[str, Any]], problems: list[str]) -> set[str]:
    consumed_ids: set[str] = set()
    for index, packet in enumerate(consumed_packets):
        path = f"consumed_packets[{index}]"
        packet_id = str(packet.get("packet_id") or "")
        if not packet_id:
            problems.append(f"{path}.packet_id is required")
        else:
            consumed_ids.add(packet_id)
        if not str(packet.get("packet_role") or packet.get("input_role") or ""):
            problems.append(f"{path}.packet_role or input_role is required")
        _require_citations(packet, path, problems)
    return consumed_ids


def _reviewer_owner_ids(raw: Any, problems: list[str]) -> set[str]:
    owners = _mapping_sequence(raw)
    owner_ids: set[str] = set()
    if not owners:
        problems.append("reviewer_owners must include at least one reviewer owner")
    for index, owner in enumerate(owners):
        path = f"reviewer_owners[{index}]"
        owner_id = str(owner.get("owner_id") or "")
        if not owner_id:
            problems.append(f"{path}.owner_id is required")
        else:
            owner_ids.add(owner_id)
        if not str(owner.get("role") or ""):
            problems.append(f"{path}.role is required")
    return owner_ids


def _require_identifier(record: Mapping[str, Any], key: str, path: str, problems: list[str]) -> None:
    if not str(record.get(key) or ""):
        problems.append(f"{path}.{key} is required")


def _require_citations(record: Mapping[str, Any], path: str, problems: list[str]) -> None:
    if not _string_list(record.get("source_evidence_ids") or record.get("citation_ids") or record.get("evidence_ids")):
        problems.append(f"{path} lacks source_evidence_ids")


def _require_consumed_packet_refs(
    record: Mapping[str, Any],
    path: str,
    consumed_ids: set[str],
    problems: list[str],
) -> None:
    refs = _string_list(record.get("consumed_packet_ids") or record.get("source_packet_ids"))
    if not refs:
        problems.append(f"{path} lacks consumed_packet_ids")
        return
    unknown = sorted(ref for ref in refs if ref not in consumed_ids)
    if unknown:
        problems.append(f"{path} references unknown consumed packets: {', '.join(unknown)}")


def _require_owner(record: Mapping[str, Any], path: str, owner_ids: set[str], problems: list[str]) -> None:
    owner = str(record.get("reviewer_owner") or record.get("owner_id") or record.get("owner") or "")
    if not owner:
        problems.append(f"{path} lacks reviewer owner")
    elif owner_ids and owner not in owner_ids:
        problems.append(f"{path} references unknown reviewer owner: {owner}")


def _walk_safety_errors(value: Any, path: str) -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            child_path = f"{path}.{key_text}"
            if key_lower in _RAW_OR_PRIVATE_KEYS and child not in (None, "", [], {}):
                errors.append(f"{child_path} uses a forbidden raw, download, archive, private, or session artifact field")
            if key_lower in _LIVE_EXECUTION_KEYS and child is True:
                errors.append(f"{child_path} claims live crawler, processor, DevHub, or LLM execution")
            if key_lower in _MUTATION_KEYS and child is True:
                errors.append(f"{child_path} enables active source, requirement, process, guardrail, prompt, surface-registry, or release-state mutation")
            errors.extend(_walk_safety_errors(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            errors.extend(_walk_safety_errors(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        if _RAW_OR_PRIVATE_TEXT_RE.search(value):
            errors.append(f"{path} references a forbidden raw, download, archive, private, or session artifact")
        if _LIVE_EXECUTION_TEXT_RE.search(value):
            errors.append(f"{path} claims live crawler, processor, DevHub, or LLM execution")
        if _OUTCOME_GUARANTEE_RE.search(value):
            errors.append(f"{path} makes a legal or permitting outcome guarantee")
    return errors


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if str(item)]
    return []


def _command_parts(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    return _string_list(value)


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped
