"""Fixture-first release rehearsal gate v2.

This module consumes committed packet fixtures only. It does not promote
artifacts, open DevHub, run live crawls, perform official actions, or handle
financial workflows.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

PACKET_VERSION = "release_rehearsal_gate_v2"

REQUIRED_INPUTS = (
    "reviewer_disposition_packet_v2",
    "inactive_promotion_patch_preview_v1",
    "action_journal_acceptance_packet_v1",
    "public_source_refresh_evidence_intake_packet_v1",
    "devhub_observation_evidence_intake_packet_v1",
)

REQUIRED_ATTESTATIONS = (
    "fixture_first",
    "no_live_execution",
    "no_authenticated_devhub_session",
    "no_private_artifacts",
    "no_official_actions",
    "no_financial_actions",
    "no_artifact_promotion",
)

MANUAL_ONLY_GATES = (
    "human_supervised_release_authorization",
    "authenticated_devhub_attendance",
    "official_record_change_checkpoint",
    "fee_workflow_checkpoint",
    "exact_confirmation_checkpoint",
)

VALIDATION_REPLAY_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/release_rehearsal_gate_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_release_rehearsal_gate_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_FORBIDDEN_KEYS = {
    "auth_artifact",
    "auth_state",
    "authenticated_artifact",
    "authenticated_session",
    "browser_artifact",
    "browser_state",
    "browser_trace",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session",
    "downloaded_data",
    "downloaded_document",
    "downloaded_pdf",
    "har",
    "local_private_path",
    "password",
    "payment_details",
    "pdf_artifact",
    "private_artifact",
    "private_path",
    "private_value",
    "private_values",
    "raw_body",
    "raw_crawl",
    "raw_crawl_output",
    "raw_data",
    "raw_download",
    "raw_downloaded_data",
    "raw_file",
    "raw_html",
    "raw_pdf",
    "raw_response_body",
    "screenshot",
    "session",
    "session_artifact",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "trace_file",
}

_MUTATION_FLAG_KEYS = {
    "active_agent_state_mutation",
    "active_document_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "agent_state_mutation_enabled",
    "document_mutation_enabled",
    "financial_action_performed",
    "guardrail_mutation_enabled",
    "live_execution_performed",
    "official_action_performed",
    "process_mutation_enabled",
    "promotion_executed",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "requirement_mutation_enabled",
    "source_mutation_enabled",
}

_NESTED_MUTATION_FLAG_KEYS = {
    "agent_state",
    "document",
    "documents",
    "guardrail",
    "guardrails",
    "process",
    "processes",
    "prompt",
    "prompts",
    "release_state",
    "requirement",
    "requirements",
    "source",
    "sources",
}

_UNSAFE_TEXT_PATTERNS = (
    re.compile(r"\braw\s+(?:body|crawl|data|download|downloaded data|html|pdf|response)\b", re.IGNORECASE),
    re.compile(r"\b(?:authenticated artifact|authenticated session|browser artifact|browser state|devhub session|downloaded document|downloaded pdf|har file|session artifact|session state|storage state|trace file)\b", re.IGNORECASE),
    re.compile(r"\b(?:active promotion|live execution|live crawl|live promotion|live run|promotion complete|promoted to active|release has been promoted)\b", re.IGNORECASE),
    re.compile(r"\b(?:approval guaranteed|city will approve|city will issue|guaranteed approval|guaranteed issuance|guaranteed permit outcome|legal outcome is guaranteed|legally compliant|legally sufficient|permit is approved|permit outcome guaranteed|permit will be approved)\b", re.IGNORECASE),
    re.compile(r"\b(?:cancel permit|certify acknowledgement|click submit|enter payment|final payment|final upload|make official changes|pay fees|purchase permit|reactivate permit|request extension|schedule inspection|submit the application|submit the permit|upload corrections|withdraw application)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class ReleaseRehearsalGateV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: Path | str) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return data


def build_release_rehearsal_gate_v2_from_fixture(path: Path | str) -> Dict[str, Any]:
    return build_release_rehearsal_gate_v2(load_json(path))


def build_release_rehearsal_gate_v2(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    missing = [name for name in REQUIRED_INPUTS if name not in inputs]
    if missing:
        raise ValueError("missing required release rehearsal gate inputs: " + ", ".join(missing))

    reviewer_packet = _mapping(inputs["reviewer_disposition_packet_v2"])
    preview_packet = _mapping(inputs["inactive_promotion_patch_preview_v1"])
    journal_packet = _mapping(inputs["action_journal_acceptance_packet_v1"])
    public_packet = _mapping(inputs["public_source_refresh_evidence_intake_packet_v1"])
    devhub_packet = _mapping(inputs["devhub_observation_evidence_intake_packet_v1"])

    preview_by_artifact = _preview_by_artifact(preview_packet)
    public_citations = _packet_citations(public_packet)
    devhub_citations = _packet_citations(devhub_packet)

    rows: List[Dict[str, Any]] = []
    for index, disposition in enumerate(_mapping_sequence(reviewer_packet.get("disposition_rows"))):
        artifact_id = _text(disposition.get("artifact_id")) or f"artifact-{index + 1}"
        status = "pass" if disposition.get("disposition") == "approve" else "block"
        reasons = _reasons(disposition, status)
        citations = _dedupe_strings(
            list(_string_sequence(disposition.get("citations")))
            + list(_string_sequence(preview_by_artifact.get(artifact_id, {}).get("source_evidence")))
            + [_text(preview_by_artifact.get(artifact_id, {}).get("citation"))]
            + public_citations
            + devhub_citations
        )
        rows.append(
            {
                "row_id": f"release-rehearsal-gate-v2-{index + 1:03d}",
                "artifact_id": artifact_id,
                "decision": status,
                "reviewer_owner": _text(disposition.get("reviewer_owner")),
                "reasons": reasons,
                "citations": citations,
                "manual_only_gate_refs": list(MANUAL_ONLY_GATES),
                "handoff_note_refs": ["future-human-supervised-release", "no-live-or-official-action-authorized"],
            }
        )

    packet = {
        "packet_version": PACKET_VERSION,
        "mode": "fixture_first_offline_release_rehearsal_gate_v2",
        "consumes": {name: _version_for(inputs[name]) for name in REQUIRED_INPUTS},
        "gate_rows": rows,
        "manual_only_gates": _manual_only_gates(),
        "validation_replay_commands": _validation_commands(reviewer_packet, preview_packet, journal_packet, public_packet, devhub_packet),
        "rollback_checkpoints": _rollback_checkpoints(reviewer_packet, preview_packet),
        "handoff_notes": _handoff_notes(rows),
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "overall_gate_status": "blocked" if any(row["decision"] == "block" for row in rows) else "pass",
    }
    require_release_rehearsal_gate_v2(packet)
    return packet


def validate_release_rehearsal_gate_v2(packet: Mapping[str, Any]) -> ReleaseRehearsalGateV2ValidationResult:
    errors: List[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append(f"packet_version must be {PACKET_VERSION}")
    if packet.get("mode") != "fixture_first_offline_release_rehearsal_gate_v2":
        errors.append("mode must be fixture_first_offline_release_rehearsal_gate_v2")

    consumes = packet.get("consumes")
    if not isinstance(consumes, Mapping):
        errors.append("consumes must be an object")
    else:
        for name in REQUIRED_INPUTS:
            if not _text(consumes.get(name)):
                errors.append(f"consumes.{name} must be present")

    rows = _mapping_sequence(packet.get("gate_rows"))
    if not rows:
        errors.append("gate_rows must be non-empty")
    seen_decisions = {_text(row.get("decision")) for row in rows}
    if not {"pass", "block"}.issubset(seen_decisions):
        errors.append("gate_rows must include pass and block decisions")
    for index, row in enumerate(rows):
        if _text(row.get("decision")) not in {"pass", "block"}:
            errors.append(f"gate_rows[{index}].decision must be pass or block")
        if not _text(row.get("row_id")):
            errors.append(f"gate_rows[{index}].row_id must be present")
        if not _text(row.get("artifact_id")):
            errors.append(f"gate_rows[{index}].artifact_id must be present")
        if not _text(row.get("reviewer_owner")):
            errors.append(f"gate_rows[{index}].reviewer_owner must be present")
        if not _string_sequence(row.get("reasons")):
            errors.append(f"gate_rows[{index}].reasons must be non-empty")
        if not _string_sequence(row.get("citations")):
            errors.append(f"gate_rows[{index}].citations must be non-empty")
        if set(_string_sequence(row.get("manual_only_gate_refs"))) != set(MANUAL_ONLY_GATES):
            errors.append(f"gate_rows[{index}].manual_only_gate_refs must reference every manual-only gate")

    manual_gates = _mapping_sequence(packet.get("manual_only_gates"))
    if {gate.get("gate_id") for gate in manual_gates} != set(MANUAL_ONLY_GATES):
        errors.append("manual_only_gates must include every required manual-only gate")
    for index, gate in enumerate(manual_gates):
        if gate.get("manual_only") is not True:
            errors.append(f"manual_only_gates[{index}].manual_only must be true")
        if not _string_sequence(gate.get("citations")):
            errors.append(f"manual_only_gates[{index}].citations must be non-empty")

    if not _command_sequence(packet.get("validation_replay_commands")):
        errors.append("validation_replay_commands must be a non-empty list of command lists")

    checkpoints = _mapping_sequence(packet.get("rollback_checkpoints"))
    if not checkpoints:
        errors.append("rollback_checkpoints must be non-empty")
    for index, checkpoint in enumerate(checkpoints):
        if not _text(checkpoint.get("checkpoint_id")):
            errors.append(f"rollback_checkpoints[{index}].checkpoint_id must be present")
        if not _text(checkpoint.get("action")):
            errors.append(f"rollback_checkpoints[{index}].action must be present")
        if not _string_sequence(checkpoint.get("citations")):
            errors.append(f"rollback_checkpoints[{index}].citations must be non-empty")

    notes = _mapping_sequence(packet.get("handoff_notes"))
    if not notes:
        errors.append("handoff_notes must be non-empty")
    for index, note in enumerate(notes):
        if not _text(note.get("note_id")):
            errors.append(f"handoff_notes[{index}].note_id must be present")
        if not _text(note.get("note")):
            errors.append(f"handoff_notes[{index}].note must be present")
        if not _string_sequence(note.get("citations")):
            errors.append(f"handoff_notes[{index}].citations must be non-empty")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
    else:
        for name in REQUIRED_ATTESTATIONS:
            if attestations.get(name) is not True:
                errors.append(f"attestations.{name} must be true")

    if packet.get("overall_gate_status") not in {"pass", "blocked"}:
        errors.append("overall_gate_status must be pass or blocked")

    _reject_unsafe_content(packet, "$", errors)
    return ReleaseRehearsalGateV2ValidationResult(not errors, tuple(errors))


def require_release_rehearsal_gate_v2(packet: Mapping[str, Any]) -> None:
    result = validate_release_rehearsal_gate_v2(packet)
    if not result.ok:
        raise ValueError("invalid release rehearsal gate v2: " + "; ".join(result.errors))


def _preview_by_artifact(packet: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    rows = _mapping_sequence(packet.get("preview_rows")) or _mapping_sequence(packet.get("promotion_candidates"))
    result: Dict[str, Mapping[str, Any]] = {}
    for row in rows:
        artifact_id = _text(row.get("artifact_id")) or _text(row.get("id"))
        if artifact_id:
            result[artifact_id] = row
    return result


def _packet_citations(packet: Mapping[str, Any]) -> List[str]:
    citations: List[str] = []
    for key in ("intake_rows", "refresh_evidence", "observations", "journal_events"):
        for row in _mapping_sequence(packet.get(key)):
            citations.extend(_string_sequence(row.get("citations")))
            citations.extend(_string_sequence(row.get("evidence_ids")))
            citation = _text(row.get("citation"))
            if citation:
                citations.append(citation)
    return _dedupe_strings(citations)


def _reasons(disposition: Mapping[str, Any], status: str) -> List[str]:
    reasons = list(_string_sequence(disposition.get("rationale")))
    if not reasons and _text(disposition.get("rationale")):
        reasons = [_text(disposition.get("rationale"))]
    if status == "block" and not reasons:
        reasons = ["reviewer disposition is not approved for rehearsal gate passage"]
    if status == "pass" and not reasons:
        reasons = ["reviewer disposition approves fixture-only rehearsal evidence"]
    return reasons


def _manual_only_gates() -> List[Dict[str, Any]]:
    return [
        {
            "gate_id": gate_id,
            "manual_only": True,
            "required_before": "future human-supervised release",
            "automated_action_allowed": False,
            "citations": [f"manual-gate:{gate_id}"],
        }
        for gate_id in MANUAL_ONLY_GATES
    ]


def _validation_commands(*packets: Mapping[str, Any]) -> List[List[str]]:
    commands: List[Sequence[str]] = [list(command) for command in VALIDATION_REPLAY_COMMANDS]
    for packet in packets:
        for key in ("exact_validation_commands", "offline_validation_commands", "validation_replay_commands"):
            for command in _sequence(packet.get(key)):
                if _is_command(command):
                    commands.append(command)
        for item in _sequence(packet.get("validation_inventory")):
            if _is_command(item):
                commands.append(item)
    return [list(command) for command in _dedupe_commands(commands)]


def _rollback_checkpoints(reviewer_packet: Mapping[str, Any], preview_packet: Mapping[str, Any]) -> List[Dict[str, Any]]:
    checkpoints: List[Dict[str, Any]] = []
    for index, checkpoint in enumerate(_mapping_sequence(reviewer_packet.get("rollback_checkpoints"))):
        checkpoints.append(
            {
                "checkpoint_id": f"reviewer-rollback-{index + 1:03d}",
                "action": _text(checkpoint.get("checkpoint")) or "restore reviewer disposition fixture before release rehearsal",
                "citations": [_text(checkpoint.get("citation")) or f"reviewer-rollback:{index + 1}"],
            }
        )
    for index, checkpoint in enumerate(_sequence(preview_packet.get("rollback_checkpoints"))):
        if isinstance(checkpoint, str) and checkpoint.strip():
            checkpoints.append(
                {
                    "checkpoint_id": f"preview-rollback-{index + 1:03d}",
                    "action": checkpoint.strip(),
                    "citations": [f"inactive-preview-rollback:{index + 1}"],
                }
            )
        elif isinstance(checkpoint, Mapping):
            checkpoints.append(
                {
                    "checkpoint_id": _text(checkpoint.get("checkpoint_id")) or f"preview-rollback-{index + 1:03d}",
                    "action": _text(checkpoint.get("action")) or _text(checkpoint.get("checkpoint")) or "restore inactive preview fixture",
                    "citations": list(_string_sequence(checkpoint.get("citations"))) or [_text(checkpoint.get("citation")) or f"inactive-preview-rollback:{index + 1}"],
                }
            )
    return checkpoints or [
        {
            "checkpoint_id": "fixture-baseline-rollback-001",
            "action": "retain last passing committed fixtures before any future human-supervised release",
            "citations": ["rollback:fixture-baseline"],
        }
    ]


def _handoff_notes(rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    cited_rows = [row for row in rows if _string_sequence(row.get("citations"))]
    citations = _dedupe_strings(citation for row in cited_rows for citation in _string_sequence(row.get("citations")))
    return [
        {
            "note_id": "future-human-supervised-release",
            "note": "Use this packet only as an offline rehearsal gate for a later human-supervised release decision.",
            "citations": citations[:3] or ["release-rehearsal-gate:v2"],
        },
        {
            "note_id": "no-live-or-official-action-authorized",
            "note": "This packet authorizes no live run, account session, artifact promotion, official record change, or financial workflow.",
            "citations": ["release-rehearsal-gate:v2:attestations"],
        },
    ]


def _version_for(packet: Any) -> str:
    if isinstance(packet, Mapping):
        for key in ("packet_version", "version", "schema_version", "id"):
            value = _text(packet.get(key))
            if value:
                return value
    return "fixture-input"


def _mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("release rehearsal gate inputs must be objects")
    return value


def _mapping_sequence(value: Any) -> List[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _sequence(value: Any) -> List[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return list(value)


def _string_sequence(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _is_command(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(part, str) and part for part in value)


def _command_sequence(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_is_command(command) for command in value)


def _dedupe_strings(values: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _dedupe_commands(commands: Iterable[Sequence[str]]) -> List[Sequence[str]]:
    seen: set[tuple[str, ...]] = set()
    result: List[Sequence[str]] = []
    for command in commands:
        key = tuple(command)
        if key not in seen:
            seen.add(key)
            result.append(command)
    return result


def _reject_unsafe_content(value: Any, path: str, errors: List[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            child_path = f"{path}.{key}"
            if normalized in _FORBIDDEN_KEYS and child not in (None, "", [], {}):
                errors.append(f"{child_path} is not allowed in release rehearsal gate v2")
            if normalized in _MUTATION_FLAG_KEYS and _active(child):
                errors.append(f"{child_path} declares a live, official, financial, promotion, or active mutation flag")
            if normalized == "mutation_flags" and _has_nested_active_mutation_flag(child):
                errors.append(f"{child_path} declares an active source, document, requirement, process, guardrail, prompt, release-state, or agent-state mutation flag")
            _reject_unsafe_content(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        for pattern in _UNSAFE_TEXT_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path} contains unsafe live, private, raw, guarantee, or consequential action language")
                break


def _has_nested_active_mutation_flag(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return _active(value)
    for key, child in value.items():
        normalized = str(key).lower().replace("-", "_")
        if normalized in _NESTED_MUTATION_FLAG_KEYS and _active(child):
            return True
    return False


def _active(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes", "complete", "completed"}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False
