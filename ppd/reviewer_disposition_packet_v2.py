"""Fixture-first reviewer disposition packet v2 builder and validator.

This module intentionally consumes committed JSON fixtures only. It does not start
DevHub sessions, read private artifacts, crawl live sites, or perform official
actions.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence

REQUIRED_ATTESTATIONS = (
    "no_live_crawl",
    "no_devhub_session",
    "no_private_artifact",
    "no_official_action",
)

REQUIRED_DISPOSITIONS = {"approve", "block", "defer"}

_FORBIDDEN_KEYS = {
    "auth_state",
    "authenticated_artifact",
    "authenticated_artifacts",
    "authenticated_fact",
    "authenticated_facts",
    "authenticated_value",
    "authenticated_values",
    "browser_artifact",
    "browser_artifacts",
    "browser_state",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "crawl_artifact",
    "crawl_artifacts",
    "crawl_output",
    "devhub_session",
    "downloaded_data",
    "downloaded_document",
    "downloaded_documents",
    "downloaded_pdf",
    "har",
    "har_file",
    "password",
    "payment_details",
    "pdf_artifact",
    "pdf_artifacts",
    "private_artifact",
    "private_artifacts",
    "private_fact",
    "private_facts",
    "private_file",
    "private_path",
    "raw_authenticated_fact",
    "raw_authenticated_value",
    "raw_browser_artifact",
    "raw_crawl",
    "raw_crawl_output",
    "raw_data",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "raw_session_artifact",
    "screenshot",
    "session_artifact",
    "session_artifacts",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "trace_file",
    "upload_payload",
}

_MUTATION_FLAG_KEYS = {
    "active_agent_state",
    "active_agent_state_mutation",
    "active_document",
    "active_document_mutation",
    "active_guardrail",
    "active_guardrail_mutation",
    "active_process",
    "active_process_mutation",
    "active_prompt",
    "active_prompt_mutation",
    "active_release_state",
    "active_release_state_mutation",
    "active_requirement",
    "active_requirement_mutation",
    "active_source",
    "active_source_mutation",
    "agent_state_mutation",
    "agent_state_mutation_enabled",
    "document_mutation",
    "document_mutation_enabled",
    "guardrail_mutation",
    "guardrail_mutation_enabled",
    "mutates_agent_state",
    "mutates_documents",
    "mutates_guardrails",
    "mutates_processes",
    "mutates_prompt",
    "mutates_release_state",
    "mutates_requirements",
    "mutates_sources",
    "process_mutation",
    "process_mutation_enabled",
    "prompt_mutation",
    "prompt_mutation_enabled",
    "release_state_mutation",
    "release_state_mutation_enabled",
    "requirement_mutation",
    "requirement_mutation_enabled",
    "source_mutation",
    "source_mutation_enabled",
}

_FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"\b(?:raw crawl|raw pdf|raw html|raw downloaded|downloaded document|downloaded pdf|browser artifact|session artifact|session state|storage state|trace file|har file|crawl artifact|pdf artifact)\b", re.IGNORECASE),
    re.compile(r"\b(?:private|authenticated)\s+(?:artifact|fact|facts|value|values|devhub value|case fact|session)\b", re.IGNORECASE),
    re.compile(r"\b(?:permit|approval|issuance|inspection|application|upload|payment)\s+(?:will|is guaranteed to|is certain to)\s+(?:be\s+)?(?:approved|issued|pass|accepted|processed|completed)\b", re.IGNORECASE),
    re.compile(r"\bguarantee(?:d|s)?\s+(?:approval|issuance|acceptance|permit outcome|inspection passage|legal outcome|permitting outcome)\b", re.IGNORECASE),
    re.compile(r"\b(?:legal|permitting)\s+outcome\s+(?:is|will be|is guaranteed|is certain)\b", re.IGNORECASE),
    re.compile(r"\b(?:finally|final|officially)\s+(?:submit|submitted|submission|pay|paid|payment|upload|uploaded|schedule|scheduled|cancel|cancelled|canceled)\b", re.IGNORECASE),
    re.compile(r"\b(?:submitted|uploaded|paid|scheduled|cancelled|canceled)\s+(?:the\s+)?(?:application|permit|payment|inspection|record|upload)\b", re.IGNORECASE),
    re.compile(r"\b(?:click|press|select|perform|complete)\s+(?:the\s+)?(?:submit|certify|upload|pay|payment|schedule|cancel|withdraw)\b", re.IGNORECASE),
    re.compile(r"\b(?:make|enter|submit)\s+(?:the\s+)?payment\b", re.IGNORECASE),
    re.compile(r"\b(?:upload corrections|schedule inspection|certify acknowledgement|submit application|purchase permit|cancel permit|withdraw application)\b", re.IGNORECASE),
)

DispositionPacket = Dict[str, Any]


@dataclass(frozen=True)
class ReviewerDispositionPacketV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON object fixture from disk."""
    with path.open("r", encoding="utf-8") as fixture_file:
        data = json.load(fixture_file)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return data


def build_packet(
    inactive_promotion_patch_preview_v1: Mapping[str, Any],
    promotion_readiness_checklist_v2: Mapping[str, Any],
    offline_acceptance_rehearsal_evidence: Mapping[str, Any],
) -> DispositionPacket:
    """Build cited approve/block/defer reviewer disposition packet rows."""
    candidates = _require_list(inactive_promotion_patch_preview_v1, "promotion_candidates")
    checklist_items = _require_list(promotion_readiness_checklist_v2, "checklist_items")
    rehearsals = _require_list(offline_acceptance_rehearsal_evidence, "rehearsals")

    checklist_by_artifact = _group_by_artifact(checklist_items)
    rehearsals_by_artifact = _group_by_artifact(rehearsals)

    rows: List[Dict[str, Any]] = []
    unresolved_blockers: List[Dict[str, Any]] = []
    reviewer_owner_assignments: MutableMapping[str, List[str]] = {}
    validation_commands: List[List[str]] = []
    rollback_checkpoints: List[Dict[str, str]] = []

    for candidate in candidates:
        artifact_id = _string(candidate, "artifact_id")
        owner = _string(candidate, "reviewer_owner")
        related_checklist = checklist_by_artifact.get(artifact_id, [])
        related_rehearsals = rehearsals_by_artifact.get(artifact_id, [])
        status, reasons = _disposition_for(related_checklist, related_rehearsals)
        citations = _citations([candidate], related_checklist, related_rehearsals)

        rows.append(
            {
                "artifact_id": artifact_id,
                "title": _string(candidate, "title"),
                "disposition": status,
                "reviewer_owner": owner,
                "rationale": reasons,
                "citations": citations,
            }
        )
        reviewer_owner_assignments.setdefault(owner, []).append(artifact_id)
        rollback_checkpoints.append(
            {
                "artifact_id": artifact_id,
                "checkpoint": _string(candidate, "rollback_checkpoint"),
                "citation": _string(candidate, "citation"),
            }
        )

        for item in related_checklist:
            if item.get("status") == "blocked":
                unresolved_blockers.append(_blocker(artifact_id, item, "readiness_checklist"))
            command = item.get("validation_command")
            if isinstance(command, list) and all(isinstance(part, str) and part for part in command):
                validation_commands.append(command)

        for rehearsal in related_rehearsals:
            if rehearsal.get("outcome") == "failed":
                unresolved_blockers.append(_blocker(artifact_id, rehearsal, "offline_acceptance_rehearsal"))
            command = rehearsal.get("validation_command")
            if isinstance(command, list) and all(isinstance(part, str) and part for part in command):
                validation_commands.append(command)

    packet = {
        "packet_version": "reviewer_disposition_packet_v2",
        "source_versions": {
            "inactive_promotion_patch_preview": inactive_promotion_patch_preview_v1.get("version"),
            "promotion_readiness_checklist": promotion_readiness_checklist_v2.get("version"),
            "offline_acceptance_rehearsal_evidence": offline_acceptance_rehearsal_evidence.get("version"),
        },
        "disposition_rows": rows,
        "unresolved_blocker_inventory": unresolved_blockers,
        "reviewer_owner_assignments": dict(sorted(reviewer_owner_assignments.items())),
        "exact_validation_commands": _dedupe_commands(validation_commands),
        "rollback_checkpoints": rollback_checkpoints,
        "attestations": _attestations(),
    }
    require_reviewer_disposition_packet_v2(packet)
    return packet


def build_packet_from_paths(preview_path: Path, checklist_path: Path, evidence_path: Path) -> DispositionPacket:
    return build_packet(load_json(preview_path), load_json(checklist_path), load_json(evidence_path))


def validate_reviewer_disposition_packet_v2(packet: Mapping[str, Any]) -> ReviewerDispositionPacketV2ValidationResult:
    errors: list[str] = []
    if packet.get("packet_version") != "reviewer_disposition_packet_v2":
        errors.append("packet_version must be reviewer_disposition_packet_v2")

    rows = _mapping_sequence(packet.get("disposition_rows"))
    if not rows:
        errors.append("disposition_rows must be non-empty")
    seen_dispositions: set[str] = set()
    artifact_ids: set[str] = set()
    for index, row in enumerate(rows):
        artifact_id = _text(row.get("artifact_id"))
        disposition = _text(row.get("disposition"))
        if not artifact_id:
            errors.append(f"disposition_rows[{index}].artifact_id must be present")
        else:
            artifact_ids.add(artifact_id)
        if disposition not in REQUIRED_DISPOSITIONS:
            errors.append(f"disposition_rows[{index}].disposition must be approve, block, or defer")
        else:
            seen_dispositions.add(disposition)
        if not _text(row.get("reviewer_owner")):
            errors.append(f"disposition_rows[{index}].reviewer_owner must be present")
        if not _has_citations(row.get("citations")):
            errors.append(f"disposition_rows[{index}].citations must be non-empty")
        if not _has_rationale(row.get("rationale")):
            errors.append(f"disposition_rows[{index}].rationale must be present")

    missing_dispositions = REQUIRED_DISPOSITIONS - seen_dispositions
    if missing_dispositions:
        errors.append("disposition_rows must include approve, block, and defer dispositions")

    blockers = _mapping_sequence(packet.get("unresolved_blocker_inventory"))
    if not blockers:
        errors.append("unresolved_blocker_inventory must be non-empty")
    for index, blocker in enumerate(blockers):
        if not _text(blocker.get("blocker_id")):
            errors.append(f"unresolved_blocker_inventory[{index}].blocker_id must be present")
        if not _text(blocker.get("artifact_id")):
            errors.append(f"unresolved_blocker_inventory[{index}].artifact_id must be present")
        if not _text(blocker.get("owner")):
            errors.append(f"unresolved_blocker_inventory[{index}].owner must be present")
        if not _text(blocker.get("summary")):
            errors.append(f"unresolved_blocker_inventory[{index}].summary must be present")
        if not _text(blocker.get("citation")):
            errors.append(f"unresolved_blocker_inventory[{index}].citation must be present")

    assignments = packet.get("reviewer_owner_assignments")
    if not isinstance(assignments, Mapping) or not assignments:
        errors.append("reviewer_owner_assignments must be non-empty")
    else:
        assigned_pairs = set()
        for owner, assigned_artifacts in assignments.items():
            if not isinstance(owner, str) or not owner:
                errors.append("reviewer_owner_assignments owner keys must be non-empty strings")
                continue
            if not _string_sequence(assigned_artifacts):
                errors.append(f"reviewer_owner_assignments.{owner} must be a non-empty string list")
                continue
            for artifact_id in assigned_artifacts:
                assigned_pairs.add((owner, artifact_id))
        for index, row in enumerate(rows):
            owner = _text(row.get("reviewer_owner"))
            artifact_id = _text(row.get("artifact_id"))
            if owner and artifact_id and (owner, artifact_id) not in assigned_pairs:
                errors.append(f"disposition_rows[{index}] must be represented in reviewer_owner_assignments")

    commands = packet.get("exact_validation_commands")
    if not _command_sequence(commands):
        errors.append("exact_validation_commands must be a non-empty list of command lists")

    checkpoints = _mapping_sequence(packet.get("rollback_checkpoints"))
    if not checkpoints:
        errors.append("rollback_checkpoints must be non-empty")
    checkpoint_artifacts: set[str] = set()
    for index, checkpoint in enumerate(checkpoints):
        artifact_id = _text(checkpoint.get("artifact_id"))
        if not artifact_id:
            errors.append(f"rollback_checkpoints[{index}].artifact_id must be present")
        else:
            checkpoint_artifacts.add(artifact_id)
        if not _text(checkpoint.get("checkpoint")):
            errors.append(f"rollback_checkpoints[{index}].checkpoint must be present")
        if not _text(checkpoint.get("citation")):
            errors.append(f"rollback_checkpoints[{index}].citation must be present")
    for artifact_id in sorted(artifact_ids - checkpoint_artifacts):
        errors.append(f"rollback_checkpoints must cover disposition artifact {artifact_id}")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be present")
    else:
        for name in REQUIRED_ATTESTATIONS:
            attestation = attestations.get(name)
            if not isinstance(attestation, Mapping) or attestation.get("attested") is not True:
                errors.append(f"attestations.{name}.attested must be true")

    _reject_unsafe_content(packet, "$", errors)
    return ReviewerDispositionPacketV2ValidationResult(not errors, tuple(errors))


def require_reviewer_disposition_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_reviewer_disposition_packet_v2(packet)
    if not result.ok:
        raise ValueError("invalid reviewer disposition packet v2: " + "; ".join(result.errors))


def _require_list(data: Mapping[str, Any], key: str) -> List[Mapping[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"required list missing: {key}")
    if not all(isinstance(item, dict) for item in value):
        raise ValueError(f"all entries must be objects: {key}")
    return value


def _string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"required string missing: {key}")
    return value


def _group_by_artifact(items: Iterable[Mapping[str, Any]]) -> Dict[str, List[Mapping[str, Any]]]:
    grouped: Dict[str, List[Mapping[str, Any]]] = {}
    for item in items:
        artifact_id = _string(item, "artifact_id")
        grouped.setdefault(artifact_id, []).append(item)
    return grouped


def _disposition_for(checklist_items: Sequence[Mapping[str, Any]], rehearsals: Sequence[Mapping[str, Any]]) -> tuple[str, List[str]]:
    reasons: List[str] = []
    if any(item.get("status") == "blocked" for item in checklist_items):
        reasons.append("readiness checklist contains unresolved blocker")
    if any(rehearsal.get("outcome") == "failed" for rehearsal in rehearsals):
        reasons.append("offline acceptance rehearsal failed")
    if reasons:
        return "block", reasons
    if any(item.get("status") == "deferred" for item in checklist_items):
        return "defer", ["readiness checklist contains deferred item"]
    if any(rehearsal.get("outcome") == "not_run" for rehearsal in rehearsals):
        return "defer", ["offline acceptance rehearsal was not run"]
    return "approve", ["fixture evidence supports offline promotion readiness"]


def _citations(*groups: Sequence[Mapping[str, Any]]) -> List[str]:
    citations: List[str] = []
    for group in groups:
        for item in group:
            citation = item.get("citation")
            if isinstance(citation, str) and citation and citation not in citations:
                citations.append(citation)
    return citations


def _blocker(artifact_id: str, item: Mapping[str, Any], source: str) -> Dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "source": source,
        "blocker_id": _string(item, "id"),
        "owner": _string(item, "owner"),
        "summary": _string(item, "summary"),
        "citation": _string(item, "citation"),
    }


def _dedupe_commands(commands: Sequence[Sequence[str]]) -> List[List[str]]:
    seen = set()
    deduped: List[List[str]] = []
    for command in commands:
        key = tuple(command)
        if key not in seen:
            seen.add(key)
            deduped.append(list(command))
    return deduped


def _attestations() -> Dict[str, Dict[str, Any]]:
    return {
        name: {
            "attested": True,
            "basis": "fixture-only reviewer disposition packet generation",
        }
        for name in REQUIRED_ATTESTATIONS
    }


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_sequence(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def _command_sequence(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_string_sequence(command) for command in value)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _has_citations(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


def _has_rationale(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(isinstance(item, str) and item.strip() for item in value)
    return False


def _reject_unsafe_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized in _FORBIDDEN_KEYS and child not in (None, "", [], {}):
                errors.append(f"{child_path} is not allowed in reviewer disposition packet v2")
            if normalized in _MUTATION_FLAG_KEYS and _is_active_flag(child):
                errors.append(f"{child_path} declares an active source, document, requirement, process, guardrail, prompt, release-state, or agent-state mutation flag")
            _reject_unsafe_content(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        for pattern in _FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path} contains unsafe private, raw, outcome, mutation, or consequential action language")
                break


def _is_active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes"}
    if isinstance(value, Mapping) or isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False
