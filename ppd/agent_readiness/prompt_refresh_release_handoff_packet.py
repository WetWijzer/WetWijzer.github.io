"""Fixture-first prompt refresh release handoff packet support.

This module assembles a metadata-only release handoff packet from two already
validated PP&D artifacts: the prompt refresh acceptance packet and the existing
agent release-consumer handoff packet. The result is a candidate prompt-version
manifest plus operator-facing compatibility, migration, rollback, validation,
and no-mutation attestations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ppd.agent_readiness.agent_prompt_refresh_acceptance_packet import (
    PACKET_TYPE as ACCEPTANCE_PACKET_TYPE,
    validate_agent_prompt_refresh_acceptance_packet,
)
from ppd.agent_readiness.release_consumer_handoff_packet import (
    PACKET_TYPE as CONSUMER_HANDOFF_PACKET_TYPE,
    validate_release_consumer_handoff_packet,
)

PACKET_TYPE = "ppd.prompt_refresh_release_handoff_packet.v1"

_REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub",
    "no_prompt_mutation",
    "no_guardrail_mutation",
    "no_release_state_mutation",
    "no_agent_state_mutation",
)
_MUTATION_FLAG_KEYS = {
    "agent_state_mutation_enabled",
    "devhub_enabled",
    "guardrail_mutation_enabled",
    "live_llm_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
}


@dataclass(frozen=True)
class PromptRefreshReleaseHandoffValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


class PromptRefreshReleaseHandoffPacketError(ValueError):
    """Raised when a prompt refresh release handoff packet is invalid."""


def build_prompt_refresh_release_handoff_packet(
    acceptance_packet: Mapping[str, Any],
    consumer_handoff_packet: Mapping[str, Any],
    *,
    candidate_prompt_version_id: str | None = None,
) -> dict[str, Any]:
    """Build a candidate prompt-version release handoff packet.

    Inputs must already be fixture-shaped packets. The builder validates them
    first and copies only metadata required for release handoff review.
    """

    acceptance_result = validate_agent_prompt_refresh_acceptance_packet(acceptance_packet)
    consumer_result = validate_release_consumer_handoff_packet(consumer_handoff_packet)
    problems = [f"acceptance packet: {problem}" for problem in acceptance_result.problems]
    problems.extend(f"consumer handoff packet: {problem}" for problem in consumer_result.problems)
    if problems:
        raise PromptRefreshReleaseHandoffPacketError("invalid source packets: " + "; ".join(problems))

    accepted_decisions = [
        decision
        for decision in _mapping_sequence(acceptance_packet.get("acceptance_decisions"))
        if str(decision.get("decision") or "").strip().lower() == "accepted"
    ]
    if not accepted_decisions:
        raise PromptRefreshReleaseHandoffPacketError("acceptance packet must include at least one accepted decision")

    accepted_decision_ids = [str(decision["decision_id"]) for decision in accepted_decisions]
    evidence_ids = sorted(_collect_evidence_refs(acceptance_packet) | _collect_evidence_refs(consumer_handoff_packet))
    guardrail_bundle_ids = sorted(_collect_values_for_key(consumer_handoff_packet, "guardrail_bundle_id")) or ["guardrail-bundle-manual-review"]
    offline_commands = _command_sequence(acceptance_packet.get("offline_validation_commands"))
    if not offline_commands:
        offline_commands = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

    source_acceptance_packet_id = str(acceptance_packet.get("packet_id") or "prompt-refresh-acceptance-fixture")
    source_consumer_handoff_packet_id = str(consumer_handoff_packet.get("packet_id") or "release-consumer-handoff-fixture")
    prompt_version_id = candidate_prompt_version_id or _candidate_id(source_acceptance_packet_id, accepted_decision_ids)

    packet = {
        "packet_type": PACKET_TYPE,
        "fixture_first": True,
        "metadata_only": True,
        "consumes": {
            "acceptance_packet_type": ACCEPTANCE_PACKET_TYPE,
            "acceptance_packet_id": source_acceptance_packet_id,
            "consumer_handoff_packet_type": CONSUMER_HANDOFF_PACKET_TYPE,
            "consumer_handoff_packet_id": source_consumer_handoff_packet_id,
        },
        "candidate_prompt_version_manifest": {
            "candidate_prompt_version_id": prompt_version_id,
            "source_acceptance_packet_id": source_acceptance_packet_id,
            "source_consumer_handoff_packet_id": source_consumer_handoff_packet_id,
            "accepted_decision_ids": accepted_decision_ids,
            "source_evidence_ids": evidence_ids,
            "promotion_status": "candidate_only",
        },
        "guardrail_bundle_compatibility_notes": [
            {
                "guardrail_bundle_id": guardrail_bundle_id,
                "compatibility_status": "compatible_with_manual_review",
                "note": "Prompt refresh can be handed to consumers only with the same refused-action and exact-confirmation gates.",
                "source_evidence_ids": evidence_ids,
            }
            for guardrail_bundle_id in guardrail_bundle_ids
        ],
        "consumer_migration_checklist": [
            {
                "checklist_id": "consumer-loads-candidate-prompt-version",
                "owner": "release-consumer-owner",
                "status": "pending_fixture_validation",
                "required": True,
                "source_evidence_ids": evidence_ids,
            },
            {
                "checklist_id": "consumer-keeps-refusal-examples-cited",
                "owner": "release-consumer-owner",
                "status": "pending_fixture_validation",
                "required": True,
                "source_evidence_ids": evidence_ids,
            },
            {
                "checklist_id": "consumer-confirms-no-consequential-controls-enabled",
                "owner": "release-consumer-owner",
                "status": "pending_fixture_validation",
                "required": True,
                "source_evidence_ids": evidence_ids,
            },
        ],
        "rollback_owner": {
            "owner_id": _first_owner_id(acceptance_packet) or _first_owner_id(consumer_handoff_packet) or "release-rollback-owner",
            "role": "prompt_refresh_release_rollback_owner",
            "activation_conditions": [
                "consumer fixture validation fails",
                "guardrail bundle compatibility review is rejected",
                "post-release smoke test blocks the candidate prompt version",
            ],
            "source_evidence_ids": evidence_ids,
        },
        "offline_validation_commands": offline_commands,
        "attestations": {key: True for key in _REQUIRED_ATTESTATIONS},
    }
    result = validate_prompt_refresh_release_handoff_packet(packet)
    if not result.valid:
        raise PromptRefreshReleaseHandoffPacketError("invalid generated packet: " + "; ".join(result.problems))
    return packet


def validate_prompt_refresh_release_handoff_packet(packet: Mapping[str, Any]) -> PromptRefreshReleaseHandoffValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return PromptRefreshReleaseHandoffValidationResult(False, ("packet must be an object",))
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        problems.append("metadata_only must be true")

    consumes = packet.get("consumes")
    if not isinstance(consumes, Mapping):
        problems.append("consumes must be an object")
    else:
        if consumes.get("acceptance_packet_type") != ACCEPTANCE_PACKET_TYPE:
            problems.append("consumes.acceptance_packet_type must reference the prompt refresh acceptance packet")
        if consumes.get("consumer_handoff_packet_type") != CONSUMER_HANDOFF_PACKET_TYPE:
            problems.append("consumes.consumer_handoff_packet_type must reference the release consumer handoff packet")
        for key in ("acceptance_packet_id", "consumer_handoff_packet_id"):
            if not _text(consumes.get(key)):
                problems.append(f"consumes.{key} is required")

    manifest = packet.get("candidate_prompt_version_manifest")
    if not isinstance(manifest, Mapping):
        problems.append("candidate_prompt_version_manifest must be an object")
    else:
        for key in ("candidate_prompt_version_id", "source_acceptance_packet_id", "source_consumer_handoff_packet_id"):
            if not _text(manifest.get(key)):
                problems.append(f"candidate_prompt_version_manifest.{key} is required")
        if not _string_sequence(manifest.get("accepted_decision_ids")):
            problems.append("candidate_prompt_version_manifest.accepted_decision_ids must be non-empty")
        if not _string_sequence(manifest.get("source_evidence_ids")):
            problems.append("candidate_prompt_version_manifest.source_evidence_ids must be non-empty")
        if manifest.get("promotion_status") != "candidate_only":
            problems.append("candidate_prompt_version_manifest.promotion_status must be candidate_only")

    problems.extend(_compatibility_note_problems(packet.get("guardrail_bundle_compatibility_notes")))
    problems.extend(_migration_checklist_problems(packet.get("consumer_migration_checklist")))
    problems.extend(_rollback_owner_problems(packet.get("rollback_owner")))
    if not _command_sequence(packet.get("offline_validation_commands")):
        problems.append("offline_validation_commands must be a non-empty list of command arrays")
    problems.extend(_attestation_problems(packet.get("attestations")))
    problems.extend(_unsafe_mutation_problems(packet))
    return PromptRefreshReleaseHandoffValidationResult(not problems, tuple(dict.fromkeys(problems)))


def assert_valid_prompt_refresh_release_handoff_packet(packet: Mapping[str, Any]) -> None:
    result = validate_prompt_refresh_release_handoff_packet(packet)
    if not result.valid:
        raise PromptRefreshReleaseHandoffPacketError("invalid prompt refresh release handoff packet: " + "; ".join(result.problems))


def _compatibility_note_problems(value: Any) -> list[str]:
    notes = _mapping_sequence(value)
    if not notes:
        return ["guardrail_bundle_compatibility_notes must be a non-empty list"]
    problems: list[str] = []
    for index, note in enumerate(notes):
        if not _text(note.get("guardrail_bundle_id")):
            problems.append(f"guardrail_bundle_compatibility_notes[{index}].guardrail_bundle_id is required")
        if str(note.get("compatibility_status") or "") not in {"compatible", "compatible_with_manual_review", "blocked"}:
            problems.append(f"guardrail_bundle_compatibility_notes[{index}].compatibility_status is invalid")
        if not _string_sequence(note.get("source_evidence_ids")):
            problems.append(f"guardrail_bundle_compatibility_notes[{index}].source_evidence_ids is required")
    return problems


def _migration_checklist_problems(value: Any) -> list[str]:
    items = _mapping_sequence(value)
    if not items:
        return ["consumer_migration_checklist must be a non-empty list"]
    problems: list[str] = []
    for index, item in enumerate(items):
        if not _text(item.get("checklist_id")):
            problems.append(f"consumer_migration_checklist[{index}].checklist_id is required")
        if not _text(item.get("owner")):
            problems.append(f"consumer_migration_checklist[{index}].owner is required")
        if item.get("required") is not True:
            problems.append(f"consumer_migration_checklist[{index}].required must be true")
        if not _string_sequence(item.get("source_evidence_ids")):
            problems.append(f"consumer_migration_checklist[{index}].source_evidence_ids is required")
    return problems


def _rollback_owner_problems(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["rollback_owner must be an object"]
    problems: list[str] = []
    if not _text(value.get("owner_id")):
        problems.append("rollback_owner.owner_id is required")
    if not _text(value.get("role")):
        problems.append("rollback_owner.role is required")
    if not _string_sequence(value.get("activation_conditions")):
        problems.append("rollback_owner.activation_conditions must be non-empty")
    if not _string_sequence(value.get("source_evidence_ids")):
        problems.append("rollback_owner.source_evidence_ids is required")
    return problems


def _attestation_problems(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["attestations must be an object"]
    return [f"attestations.{key} must be true" for key in _REQUIRED_ATTESTATIONS if value.get(key) is not True]


def _unsafe_mutation_problems(value: Any, path: str = "$", key_name: str = "") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized_key = str(key).lower().replace("-", "_")
            child_path = f"{path}.{key}"
            if normalized_key in _MUTATION_FLAG_KEYS and child is True:
                problems.append(f"active mutation or execution flag is not allowed at {child_path}")
            problems.extend(_unsafe_mutation_problems(child, child_path, normalized_key))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            problems.extend(_unsafe_mutation_problems(child, f"{path}[{index}]", key_name))
    return problems


def _candidate_id(source_packet_id: str, decision_ids: Sequence[str]) -> str:
    suffix = "-".join(decision_ids) if decision_ids else "accepted"
    return f"candidate-prompt-version-{source_packet_id}-{suffix}"


def _first_owner_id(packet: Mapping[str, Any]) -> str:
    owners = _mapping_sequence(packet.get("reviewer_owners") or packet.get("reviewers") or packet.get("operator_reviewers"))
    for owner in owners:
        for key in ("owner_id", "reviewer_owner_id", "reviewer_id", "owner"):
            value = _text(owner.get(key))
            if value:
                return value
    return ""


def _collect_values_for_key(value: Any, wanted_key: str) -> set[str]:
    values: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) == wanted_key and isinstance(child, str) and child.strip():
                values.add(child.strip())
            else:
                values.update(_collect_values_for_key(child, wanted_key))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            values.update(_collect_values_for_key(child, wanted_key))
    return values


def _collect_evidence_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, Mapping):
        for key in ("source_evidence_ids", "citation_ids", "evidence_ids"):
            refs.update(_string_sequence(value.get(key)))
        for key in ("source_evidence_id", "citation_id", "evidence_id"):
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                refs.add(raw.strip())
        for child in value.values():
            refs.update(_collect_evidence_refs(child))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            refs.update(_collect_evidence_refs(child))
    return refs


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


def _string_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


__all__ = [
    "PACKET_TYPE",
    "PromptRefreshReleaseHandoffPacketError",
    "PromptRefreshReleaseHandoffValidationResult",
    "assert_valid_prompt_refresh_release_handoff_packet",
    "build_prompt_refresh_release_handoff_packet",
    "validate_prompt_refresh_release_handoff_packet",
]
