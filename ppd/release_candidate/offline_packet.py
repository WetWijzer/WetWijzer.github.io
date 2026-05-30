"""Fixture-first offline release candidate packet assembly and validation.

This module intentionally accepts already-committed packet fixtures and produces a
release-candidate assembly packet without crawling public sources, opening DevHub,
calling prompts, compiling guardrails, or mutating a release ledger.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any


class PacketAssemblyError(ValueError):
    """Raised when an offline release candidate packet cannot be assembled."""


REQUIRED_PACKET_TYPES = (
    "public_source_refresh_execution_readiness",
    "requirement_regeneration_promotion_approval",
    "agent_readiness_final_smoke",
    "devhub_attended_read_only_pilot_evidence_review",
)

REQUIRED_ATTESTATIONS = (
    "no_crawl_performed",
    "no_processor_executed",
    "no_devhub_session_started",
    "no_prompt_invoked",
    "no_guardrail_compiled",
    "no_release_mutation_performed",
)

RELEASE_DECISION_ORDER = (
    "public_source_refresh",
    "requirement_regeneration",
    "agent_readiness",
    "devhub_read_only_pilot",
)

PACKET_TO_DECISION = {
    "public_source_refresh_execution_readiness": "public_source_refresh",
    "requirement_regeneration_promotion_approval": "requirement_regeneration",
    "agent_readiness_final_smoke": "agent_readiness",
    "devhub_attended_read_only_pilot_evidence_review": "devhub_read_only_pilot",
}

APPROVED_STATUSES = {"ready", "approved", "passed", "reviewed"}

PRIVATE_OR_RAW_KEYS = {
    "access_token",
    "archive_artifact_ref",
    "archive_path",
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
    "download_url",
    "har",
    "local_path",
    "password",
    "private_path",
    "private_url",
    "raw_archive_ref",
    "raw_body",
    "raw_body_ref",
    "raw_download_ref",
    "raw_html",
    "raw_output",
    "raw_text",
    "raw_value",
    "refresh_token",
    "screenshot",
    "secret",
    "session",
    "session_cookie",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "user_input",
}

ACTIVE_MUTATION_KEYS = {
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "apply_update",
    "commit_to_registry",
    "execute_release",
    "guardrail_promotion_enabled",
    "mutate_guardrail_bundle",
    "mutate_process_model",
    "mutate_prompt",
    "mutate_release_state",
    "mutate_requirement",
    "mutate_source",
    "mutate_surface_registry",
    "perform_release",
    "processor_execution_enabled",
    "prompt_mutation_enabled",
    "release_mutation_enabled",
    "source_mutation_enabled",
    "surface_registry_mutation_enabled",
    "write_active_guardrail",
    "write_active_process",
    "write_active_prompt",
    "write_active_release_state",
    "write_active_requirement",
    "write_active_source",
    "write_active_surface_registry",
}

RAW_OR_PRIVATE_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|(^[A-Za-z]:\\Users\\[^\\]+\\)|"
    r"(/(?:raw|download|downloads|archive|archives|session|private)(?:/|$))|"
    r"(https?://[^\s?#]+/(?:auth|authenticated|private|session|download|downloads|archive|archives|raw)(?:[/?#]|$))|"
    r"(https?://[^\s?#]+[^\s]*(?:[?&](?:access_token|auth|password|session|token)=))|"
    r"(auth[_-]?state|browser[_-]?state|cookie|credential|har|password|raw[_-]?(body|crawl|html)|"
    r"session[_-]?state|screenshot|secret|storage[_-]?state|token|trace\.zip|warc)",
    re.IGNORECASE,
)

LIVE_EXECUTION_RE = re.compile(
    r"\b(live\s+(crawl|crawler|processor|devhub|llm)|crawler\s+(ran|executed)|processor\s+(ran|executed)|"
    r"devhub\s+(ran|executed|submitted|uploaded)|llm\s+(ran|executed|called)|submitted\s+to\s+devhub|"
    r"uploaded\s+to\s+devhub|called\s+the\s+live\s+llm|ran\s+the\s+live\s+processor)\b",
    re.IGNORECASE,
)

OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?\s+(approval|issuance|permit|legal|compliance|outcome)|"
    r"(permit|application|inspection|appeal)\s+(will|shall)\s+be\s+(approved|issued|accepted|granted|upheld)|"
    r"legally\s+guaranteed|guaranteed\s+code\s+compliance)\b",
    re.IGNORECASE,
)


def load_fixture_packet(path: Path | str) -> dict[str, Any]:
    """Load an assembly input fixture from disk."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as fixture_file:
        loaded = json.load(fixture_file)
    if not isinstance(loaded, dict):
        raise PacketAssemblyError("release candidate fixture must contain a JSON object")
    return loaded


def assemble_release_candidate_packet(source_packet: dict[str, Any]) -> dict[str, Any]:
    """Assemble a deterministic offline release candidate packet."""

    if not isinstance(source_packet, dict):
        raise PacketAssemblyError("source_packet must be a dictionary")
    _raise_if_unsafe(source_packet)

    attestations = _validate_attestations(source_packet.get("attestations"))
    packets = _index_required_packets(source_packet.get("packets"))
    decisions = _build_release_inclusion_decisions(packets)
    residual_blockers = _collect_residual_blockers(packets)
    validation_commands = _collect_validation_commands(packets)
    rollback_owners = _collect_rollback_owners(packets)
    release_ready = all(decision["included"] for decision in decisions) and not residual_blockers

    assembled = {
        "packet_type": "offline_release_candidate_assembly",
        "packet_id": source_packet.get("packet_id", "offline-release-candidate-assembly-fixture"),
        "assembled_from": list(REQUIRED_PACKET_TYPES),
        "mode": "fixture_first_offline",
        "release_ready": release_ready,
        "release_inclusion_decisions": decisions,
        "residual_blockers": residual_blockers,
        "validation_command_set": validation_commands,
        "rollback_owner_fields": rollback_owners,
        "attestations": attestations,
        "release_state_effects": {
            "active_source_mutation": False,
            "active_requirement_mutation": False,
            "active_process_mutation": False,
            "active_guardrail_mutation": False,
            "active_prompt_mutation": False,
            "active_surface_registry_mutation": False,
            "active_release_state_mutation": False,
            "live_crawler_execution": False,
            "live_processor_execution": False,
            "live_devhub_execution": False,
            "live_llm_execution": False,
        },
    }
    assert_valid_release_candidate_packet(assembled)
    return assembled


def validate_release_candidate_packet(packet: Mapping[str, Any]) -> list[str]:
    """Return validation problems for an offline release candidate assembly packet."""

    problems: list[str] = []
    try:
        _raise_if_unsafe(packet)
    except PacketAssemblyError as exc:
        problems.append(str(exc))

    if packet.get("packet_type") != "offline_release_candidate_assembly":
        problems.append("packet_type must be offline_release_candidate_assembly")
    if packet.get("mode") != "fixture_first_offline":
        problems.append("mode must be fixture_first_offline")

    assembled_from = packet.get("assembled_from")
    if not _is_string_list(assembled_from):
        problems.append("assembled_from must list consumed packet types")
    else:
        missing = [packet_type for packet_type in REQUIRED_PACKET_TYPES if packet_type not in assembled_from]
        if missing:
            problems.append("assembled_from is missing consumed packet references: " + ", ".join(missing))

    decisions = list(_mapping_sequence(packet.get("release_inclusion_decisions")))
    if not decisions:
        problems.append("release_inclusion_decisions must be non-empty")
    for index, decision in enumerate(decisions):
        if decision.get("decision_id") not in RELEASE_DECISION_ORDER:
            problems.append(f"release_inclusion_decisions[{index}] has unknown decision_id")
        if not isinstance(decision.get("included"), bool):
            problems.append(f"release_inclusion_decisions[{index}] must include boolean included")
        if not _is_string_list(decision.get("citations")):
            problems.append(f"release_inclusion_decisions[{index}] lacks citations")
        if not decision.get("source_packet_type") or not decision.get("source_packet_id"):
            problems.append(f"release_inclusion_decisions[{index}] lacks source packet reference")

    blockers = list(_mapping_sequence(packet.get("residual_blockers")))
    if not isinstance(packet.get("residual_blockers"), list):
        problems.append("residual_blockers must be a list")
    for index, blocker in enumerate(blockers):
        if not blocker.get("blocker_id"):
            problems.append(f"residual_blockers[{index}] lacks blocker_id")
        if not blocker.get("status"):
            problems.append(f"residual_blockers[{index}] lacks status")
        if not _is_string_list(blocker.get("citations")):
            problems.append(f"residual_blockers[{index}] lacks citations")
        if not blocker.get("source_packet_type"):
            problems.append(f"residual_blockers[{index}] lacks source_packet_type")

    if not packet.get("validation_command_set"):
        problems.append("validation_command_set must be non-empty")
    for index, command in enumerate(packet.get("validation_command_set", [])):
        if not _is_string_list(command):
            problems.append(f"validation_command_set[{index}] must be a string list")

    owners = packet.get("rollback_owner_fields")
    if not isinstance(owners, Mapping):
        problems.append("rollback_owner_fields must be a mapping")
    else:
        for decision_id in RELEASE_DECISION_ORDER:
            owner = owners.get(decision_id)
            if not isinstance(owner, Mapping):
                problems.append(f"rollback_owner_fields.{decision_id} is missing")
                continue
            for field in ("owner", "escalation", "rollback_action"):
                if not isinstance(owner.get(field), str) or not owner.get(field):
                    problems.append(f"rollback_owner_fields.{decision_id}.{field} is missing")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        problems.append("attestations must be a mapping")
    else:
        for name in REQUIRED_ATTESTATIONS:
            if attestations.get(name) is not True:
                problems.append(f"required attestation is not true: {name}")

    effects = packet.get("release_state_effects")
    if not isinstance(effects, Mapping):
        problems.append("release_state_effects must be present")
    else:
        for key in ACTIVE_MUTATION_KEYS:
            if key in effects and effects.get(key) is not False:
                problems.append(f"release_state_effects.{key} must be false")

    return problems


def assert_valid_release_candidate_packet(packet: Mapping[str, Any]) -> None:
    problems = validate_release_candidate_packet(packet)
    if problems:
        raise PacketAssemblyError("invalid offline release candidate assembly packet: " + "; ".join(problems))


def _validate_attestations(raw_attestations: Any) -> dict[str, bool]:
    if not isinstance(raw_attestations, dict):
        raise PacketAssemblyError("source packet must include attestation fields")

    attestations: dict[str, bool] = {}
    for name in REQUIRED_ATTESTATIONS:
        value = raw_attestations.get(name)
        if value is not True:
            raise PacketAssemblyError(f"required attestation is not true: {name}")
        attestations[name] = True
    return attestations


def _index_required_packets(raw_packets: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(raw_packets, list):
        raise PacketAssemblyError("source packet must include a packets list")

    indexed: dict[str, dict[str, Any]] = {}
    for packet in raw_packets:
        if not isinstance(packet, dict):
            raise PacketAssemblyError("each source packet entry must be a dictionary")
        packet_type = packet.get("packet_type")
        if not isinstance(packet_type, str):
            raise PacketAssemblyError("each source packet must include packet_type")
        if packet_type in indexed:
            raise PacketAssemblyError(f"duplicate source packet type: {packet_type}")
        indexed[packet_type] = packet

    missing = [packet_type for packet_type in REQUIRED_PACKET_TYPES if packet_type not in indexed]
    if missing:
        raise PacketAssemblyError("missing required source packets: " + ", ".join(missing))
    return indexed


def _build_release_inclusion_decisions(packets: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    decisions_by_id: dict[str, dict[str, Any]] = {}
    for packet_type, decision_id in PACKET_TO_DECISION.items():
        packet = packets[packet_type]
        status = _normalized_status(packet)
        evidence_ids = _require_evidence_ids(packet, packet_type)
        blockers = _packet_blockers(packet)
        included = status in APPROVED_STATUSES and not blockers
        decisions_by_id[decision_id] = {
            "decision_id": decision_id,
            "included": included,
            "source_packet_type": packet_type,
            "source_packet_id": packet.get("packet_id", packet_type),
            "status": status,
            "citations": evidence_ids,
            "rationale": _decision_rationale(decision_id, included, status, blockers),
        }

    return [decisions_by_id[decision_id] for decision_id in RELEASE_DECISION_ORDER]


def _collect_residual_blockers(packets: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    residual_blockers: list[dict[str, Any]] = []
    for packet_type in REQUIRED_PACKET_TYPES:
        packet = packets[packet_type]
        for blocker in _packet_blockers(packet):
            if not isinstance(blocker, dict):
                raise PacketAssemblyError(f"blocker in {packet_type} must be a dictionary")
            if not blocker.get("status"):
                raise PacketAssemblyError(f"blocker in {packet_type} must include status")
            copied = deepcopy(blocker)
            copied.setdefault("source_packet_type", packet_type)
            copied.setdefault("citations", _require_evidence_ids(packet, packet_type))
            residual_blockers.append(copied)
    return residual_blockers


def _collect_validation_commands(packets: dict[str, dict[str, Any]]) -> list[list[str]]:
    commands: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for packet_type in REQUIRED_PACKET_TYPES:
        packet = packets[packet_type]
        raw_commands = packet.get("validation_commands")
        if not isinstance(raw_commands, list) or not raw_commands:
            raise PacketAssemblyError(f"validation_commands in {packet_type} must be a non-empty list")
        for command in raw_commands:
            if not _is_string_list(command):
                raise PacketAssemblyError(f"validation command in {packet_type} must be a string list")
            command_key = tuple(command)
            if command_key not in seen:
                seen.add(command_key)
                commands.append(list(command))
    if not commands:
        raise PacketAssemblyError("validation_command_set must be non-empty")
    return commands


def _collect_rollback_owners(packets: dict[str, dict[str, Any]]) -> dict[str, dict[str, str]]:
    rollback_owners: dict[str, dict[str, str]] = {}
    for packet_type in REQUIRED_PACKET_TYPES:
        decision_id = PACKET_TO_DECISION[packet_type]
        packet = packets[packet_type]
        owner_fields = packet.get("rollback_owner")
        if not isinstance(owner_fields, dict):
            raise PacketAssemblyError(f"rollback_owner in {packet_type} must be a dictionary")
        owner = owner_fields.get("owner")
        escalation = owner_fields.get("escalation")
        rollback_action = owner_fields.get("rollback_action")
        if not all(isinstance(value, str) and value for value in (owner, escalation, rollback_action)):
            raise PacketAssemblyError(f"rollback_owner in {packet_type} is incomplete")
        rollback_owners[decision_id] = {
            "owner": owner,
            "escalation": escalation,
            "rollback_action": rollback_action,
        }
    return rollback_owners


def _normalized_status(packet: dict[str, Any]) -> str:
    status = packet.get("status")
    if not isinstance(status, str) or not status:
        raise PacketAssemblyError(f"packet {packet.get('packet_type', '')} must include status")
    return status.strip().lower()


def _require_evidence_ids(packet: dict[str, Any], packet_type: str) -> list[str]:
    evidence_ids = packet.get("evidence_ids")
    if not _is_string_list(evidence_ids):
        raise PacketAssemblyError(f"{packet_type} must include evidence_ids as a non-empty string list")
    if not evidence_ids:
        raise PacketAssemblyError(f"{packet_type} must include at least one evidence id")
    return list(evidence_ids)


def _packet_blockers(packet: dict[str, Any]) -> list[Any]:
    blockers = packet.get("residual_blockers", [])
    if not isinstance(blockers, list):
        raise PacketAssemblyError(f"residual_blockers in {packet.get('packet_type', '')} must be a list")
    return blockers


def _decision_rationale(decision_id: str, included: bool, status: str, blockers: list[Any]) -> str:
    if included:
        return f"{decision_id} is included because its source packet is {status} and reports no residual blockers."
    if blockers:
        return f"{decision_id} is excluded because residual blockers remain in its source packet."
    return f"{decision_id} is excluded because its source packet status is {status}."


def _raise_if_unsafe(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            key_normalized = key_text.lower()
            child_path = f"{path}.{key_text}"
            if key_normalized in PRIVATE_OR_RAW_KEYS and child not in (None, "", [], {}):
                raise PacketAssemblyError(f"private or raw artifact field is not allowed at {child_path}")
            if key_normalized in ACTIVE_MUTATION_KEYS and child is True:
                raise PacketAssemblyError(f"active mutation flag must be false at {child_path}")
            _raise_if_unsafe(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _raise_if_unsafe(child, f"{path}[{index}]")
    elif isinstance(value, str):
        if RAW_OR_PRIVATE_RE.search(value):
            raise PacketAssemblyError(f"raw, download, archive, private, or session artifact reference is not allowed at {path}")
        if LIVE_EXECUTION_RE.search(value):
            raise PacketAssemblyError(f"live crawler, processor, DevHub, or LLM execution claim is not allowed at {path}")
        if OUTCOME_GUARANTEE_RE.search(value):
            raise PacketAssemblyError(f"legal or permitting outcome guarantee is not allowed at {path}")


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)
