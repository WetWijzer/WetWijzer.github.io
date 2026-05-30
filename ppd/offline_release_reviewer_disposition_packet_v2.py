"""Fixture-first offline release reviewer disposition packet v2.

This module consumes an offline release rehearsal gate v2 packet fixture and emits
ordered reviewer approve/hold/reject decisions. It is intentionally offline-only:
it does not promote artifacts, change release state, open DevHub, run live network
access, store private artifacts, or perform official actions.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

PACKET_VERSION = "offline_release_reviewer_disposition_packet_v2"
EXPECTED_GATE_VERSION = "release_rehearsal_gate_v2"
REQUIRED_DECISIONS = ("approve", "hold", "reject")
REQUIRED_ATTESTATIONS = (
    "fixture_first",
    "no_live_network_access",
    "no_devhub_opened",
    "no_private_artifacts",
    "no_official_actions",
    "no_active_promotion",
    "no_release_state_change",
)
DEFAULT_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/offline_release_reviewer_disposition_packet_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_offline_release_reviewer_disposition_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_FORBIDDEN_KEYS = {
    "auth_state",
    "authenticated_artifact",
    "authenticated_artifacts",
    "authenticated_session",
    "browser_artifact",
    "browser_artifacts",
    "browser_state",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session",
    "downloaded_document",
    "downloaded_documents",
    "downloaded_pdf",
    "har",
    "har_file",
    "local_private_path",
    "password",
    "payment_details",
    "private_artifact",
    "private_artifacts",
    "private_path",
    "raw_body",
    "raw_crawl",
    "raw_crawl_output",
    "raw_data",
    "raw_download",
    "raw_html",
    "raw_pdf",
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

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_document_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_promotion",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_requirement_mutation",
    "active_source_mutation",
    "agent_state_mutation_enabled",
    "document_mutation_enabled",
    "guardrail_mutation_enabled",
    "live_network_access",
    "official_action_performed",
    "process_mutation_enabled",
    "promotion_executed",
    "prompt_mutation_enabled",
    "release_state_changed",
    "release_state_mutation_enabled",
    "requirement_mutation_enabled",
    "source_mutation_enabled",
}

_UNSAFE_TEXT_PATTERNS = (
    re.compile(r"\b(?:raw crawl|raw data|raw download|raw html|raw pdf|downloaded document|downloaded pdf)\b", re.IGNORECASE),
    re.compile(r"\b(?:authenticated session|browser artifact|devhub session|private artifact|session state|storage state|trace file|har file)\b", re.IGNORECASE),
    re.compile(r"\b(?:active promotion|promoted to active|release state changed|release has been promoted|live network access|live crawl|opened devhub)\b", re.IGNORECASE),
    re.compile(r"\b(?:approval guaranteed|city will approve|city will issue|guaranteed approval|legal outcome is guaranteed|permit will be approved)\b", re.IGNORECASE),
    re.compile(r"\b(?:cancel permit|certify acknowledgement|click submit|enter payment|final payment|make official changes|pay fees|purchase permit|schedule inspection|submit the application|submit the permit|upload corrections|withdraw application)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class OfflineReleaseReviewerDispositionPacketV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: Path | str) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return data


def build_offline_release_reviewer_disposition_packet_v2_from_fixture(path: Path | str) -> Dict[str, Any]:
    return build_offline_release_reviewer_disposition_packet_v2(load_json(path))


def build_offline_release_reviewer_disposition_packet_v2(rehearsal_gate_v2: Mapping[str, Any]) -> Dict[str, Any]:
    if _text(rehearsal_gate_v2.get("packet_version")) != EXPECTED_GATE_VERSION:
        raise ValueError("offline release reviewer disposition packet v2 requires release_rehearsal_gate_v2 input")

    gate_rows = _mapping_sequence(rehearsal_gate_v2.get("gate_rows"))
    if not gate_rows:
        raise ValueError("release rehearsal gate v2 input must include gate_rows")

    decision_rows: List[Dict[str, Any]] = []
    evidence_bundle_references: List[Dict[str, Any]] = []
    unresolved_risk_notes: List[Dict[str, Any]] = []

    for index, gate_row in enumerate(gate_rows):
        decision = _reviewer_decision(gate_row)
        artifact_id = _text(gate_row.get("artifact_id")) or f"artifact-{index + 1}"
        row_id = f"offline-reviewer-disposition-v2-{index + 1:03d}"
        citations = _dedupe_strings(_string_sequence(gate_row.get("citations")))
        reasons = _string_sequence(gate_row.get("reasons")) or [_fallback_reason(decision)]
        evidence_ref_id = f"evidence-bundle-ref-{index + 1:03d}"

        decision_rows.append(
            {
                "row_id": row_id,
                "order": index + 1,
                "artifact_id": artifact_id,
                "gate_row_id": _text(gate_row.get("row_id")) or f"gate-row-{index + 1}",
                "reviewer_decision": decision,
                "reviewer_owner": _text(gate_row.get("reviewer_owner")) or "offline-release-reviewer",
                "rationale": reasons,
                "evidence_bundle_ref": evidence_ref_id,
                "validation_transcript_review_placeholder": {
                    "placeholder_id": f"validation-transcript-review-{index + 1:03d}",
                    "status": "pending_human_review",
                    "required_review": "review offline validation transcript before any future supervised release decision",
                    "no_transcript_artifact_stored": True,
                },
                "rollback_readiness_ref": f"rollback-readiness-{index + 1:03d}",
                "citations": citations,
            }
        )
        evidence_bundle_references.append(
            {
                "evidence_bundle_ref": evidence_ref_id,
                "artifact_id": artifact_id,
                "gate_row_id": _text(gate_row.get("row_id")) or f"gate-row-{index + 1}",
                "citation_refs": citations,
                "contains_private_or_raw_artifacts": False,
            }
        )
        if decision in {"hold", "reject"}:
            unresolved_risk_notes.append(
                {
                    "risk_note_id": f"unresolved-risk-{index + 1:03d}",
                    "artifact_id": artifact_id,
                    "reviewer_decision": decision,
                    "risk_status": "unresolved",
                    "note": "; ".join(reasons),
                    "citations": citations,
                }
            )

    packet = {
        "packet_version": PACKET_VERSION,
        "mode": "fixture_first_offline_release_reviewer_disposition_v2",
        "consumes": {
            "offline_release_rehearsal_gate_v2": _text(rehearsal_gate_v2.get("packet_version")),
            "offline_release_rehearsal_gate_v2_status": _text(rehearsal_gate_v2.get("overall_gate_status")),
        },
        "decision_order": [row["reviewer_decision"] for row in decision_rows],
        "reviewer_decisions": decision_rows,
        "evidence_bundle_references": evidence_bundle_references,
        "rollback_readiness_confirmations": _rollback_readiness_confirmations(rehearsal_gate_v2, decision_rows),
        "unresolved_risk_notes": unresolved_risk_notes,
        "exact_offline_validation_commands": _validation_commands(rehearsal_gate_v2),
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
    }
    require_offline_release_reviewer_disposition_packet_v2(packet)
    return packet


def validate_offline_release_reviewer_disposition_packet_v2(packet: Mapping[str, Any]) -> OfflineReleaseReviewerDispositionPacketV2ValidationResult:
    errors: List[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append(f"packet_version must be {PACKET_VERSION}")
    if packet.get("mode") != "fixture_first_offline_release_reviewer_disposition_v2":
        errors.append("mode must be fixture_first_offline_release_reviewer_disposition_v2")

    consumes = packet.get("consumes")
    if not isinstance(consumes, Mapping):
        errors.append("consumes must be an object")
    else:
        if _text(consumes.get("offline_release_rehearsal_gate_v2")) != EXPECTED_GATE_VERSION:
            errors.append("consumes.offline_release_rehearsal_gate_v2 must reference release_rehearsal_gate_v2")
        if not _text(consumes.get("offline_release_rehearsal_gate_v2_status")):
            errors.append("consumes.offline_release_rehearsal_gate_v2_status must be present")

    decisions = _mapping_sequence(packet.get("reviewer_decisions"))
    if not decisions:
        errors.append("reviewer_decisions must be non-empty")
    seen_decisions = [_text(row.get("reviewer_decision")) for row in decisions]
    if packet.get("decision_order") != seen_decisions:
        errors.append("decision_order must exactly match reviewer_decisions order")
    if tuple(seen_decisions) != REQUIRED_DECISIONS:
        errors.append("reviewer_decisions must be ordered approve, hold, reject")

    evidence_refs = {_text(ref.get("evidence_bundle_ref")) for ref in _mapping_sequence(packet.get("evidence_bundle_references"))}
    rollback_refs = {_text(ref.get("rollback_readiness_ref")) for ref in _mapping_sequence(packet.get("rollback_readiness_confirmations"))}
    artifact_ids: set[str] = set()
    for index, row in enumerate(decisions):
        artifact_id = _text(row.get("artifact_id"))
        decision = _text(row.get("reviewer_decision"))
        evidence_ref = _text(row.get("evidence_bundle_ref"))
        rollback_ref = _text(row.get("rollback_readiness_ref"))
        artifact_ids.add(artifact_id)
        if not _text(row.get("row_id")):
            errors.append(f"reviewer_decisions[{index}].row_id must be present")
        if row.get("order") != index + 1:
            errors.append(f"reviewer_decisions[{index}].order must preserve packet order")
        if not artifact_id:
            errors.append(f"reviewer_decisions[{index}].artifact_id must be present")
        if decision not in REQUIRED_DECISIONS:
            errors.append(f"reviewer_decisions[{index}].reviewer_decision must be approve, hold, or reject")
        if not _text(row.get("reviewer_owner")):
            errors.append(f"reviewer_decisions[{index}].reviewer_owner must be present")
        if not _string_sequence(row.get("rationale")):
            errors.append(f"reviewer_decisions[{index}].rationale must be non-empty")
        if not _string_sequence(row.get("citations")):
            errors.append(f"reviewer_decisions[{index}].citations must be non-empty")
        if evidence_ref not in evidence_refs:
            errors.append(f"reviewer_decisions[{index}].evidence_bundle_ref must reference evidence_bundle_references")
        if rollback_ref not in rollback_refs:
            errors.append(f"reviewer_decisions[{index}].rollback_readiness_ref must reference rollback_readiness_confirmations")
        _validate_transcript_placeholder(row.get("validation_transcript_review_placeholder"), index, errors)

    if not evidence_refs:
        errors.append("evidence_bundle_references must be non-empty")
    for index, ref in enumerate(_mapping_sequence(packet.get("evidence_bundle_references"))):
        if not _text(ref.get("evidence_bundle_ref")):
            errors.append(f"evidence_bundle_references[{index}].evidence_bundle_ref must be present")
        if not _text(ref.get("artifact_id")):
            errors.append(f"evidence_bundle_references[{index}].artifact_id must be present")
        if not _string_sequence(ref.get("citation_refs")):
            errors.append(f"evidence_bundle_references[{index}].citation_refs must be non-empty")
        if ref.get("contains_private_or_raw_artifacts") is not False:
            errors.append(f"evidence_bundle_references[{index}].contains_private_or_raw_artifacts must be false")

    confirmations = _mapping_sequence(packet.get("rollback_readiness_confirmations"))
    if not confirmations:
        errors.append("rollback_readiness_confirmations must be non-empty")
    for index, confirmation in enumerate(confirmations):
        if not _text(confirmation.get("rollback_readiness_ref")):
            errors.append(f"rollback_readiness_confirmations[{index}].rollback_readiness_ref must be present")
        if not _text(confirmation.get("artifact_id")):
            errors.append(f"rollback_readiness_confirmations[{index}].artifact_id must be present")
        if confirmation.get("ready_for_future_manual_release_review") is not True:
            errors.append(f"rollback_readiness_confirmations[{index}].ready_for_future_manual_release_review must be true")
        if confirmation.get("active_release_state_changed") is not False:
            errors.append(f"rollback_readiness_confirmations[{index}].active_release_state_changed must be false")
        if not _string_sequence(confirmation.get("citations")):
            errors.append(f"rollback_readiness_confirmations[{index}].citations must be non-empty")

    risk_notes = _mapping_sequence(packet.get("unresolved_risk_notes"))
    if not risk_notes:
        errors.append("unresolved_risk_notes must be non-empty")
    risk_artifacts = {_text(note.get("artifact_id")) for note in risk_notes}
    held_or_rejected = {_text(row.get("artifact_id")) for row in decisions if _text(row.get("reviewer_decision")) in {"hold", "reject"}}
    if held_or_rejected - risk_artifacts:
        errors.append("unresolved_risk_notes must cover every held or rejected reviewer decision")
    for index, note in enumerate(risk_notes):
        if not _text(note.get("risk_note_id")):
            errors.append(f"unresolved_risk_notes[{index}].risk_note_id must be present")
        if _text(note.get("reviewer_decision")) not in {"hold", "reject"}:
            errors.append(f"unresolved_risk_notes[{index}].reviewer_decision must be hold or reject")
        if _text(note.get("risk_status")) != "unresolved":
            errors.append(f"unresolved_risk_notes[{index}].risk_status must be unresolved")
        if not _text(note.get("note")):
            errors.append(f"unresolved_risk_notes[{index}].note must be present")
        if not _string_sequence(note.get("citations")):
            errors.append(f"unresolved_risk_notes[{index}].citations must be non-empty")

    if not _command_sequence(packet.get("exact_offline_validation_commands")):
        errors.append("exact_offline_validation_commands must be a non-empty list of command lists")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
    else:
        for name in REQUIRED_ATTESTATIONS:
            if attestations.get(name) is not True:
                errors.append(f"attestations.{name} must be true")

    if "" in artifact_ids:
        errors.append("reviewer_decisions artifact ids must be non-empty")

    _reject_unsafe_content(packet, "$", errors)
    return OfflineReleaseReviewerDispositionPacketV2ValidationResult(not errors, tuple(errors))


def require_offline_release_reviewer_disposition_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_offline_release_reviewer_disposition_packet_v2(packet)
    if not result.ok:
        raise ValueError("invalid offline release reviewer disposition packet v2: " + "; ".join(result.errors))


def _reviewer_decision(gate_row: Mapping[str, Any]) -> str:
    explicit = _text(gate_row.get("reviewer_disposition_hint"))
    if explicit in REQUIRED_DECISIONS:
        return explicit
    if _text(gate_row.get("decision")) == "pass":
        return "approve"
    severity = _text(gate_row.get("risk_severity"))
    if severity in {"critical", "reject"} or gate_row.get("release_blocker") is True:
        return "reject"
    return "hold"


def _fallback_reason(decision: str) -> str:
    if decision == "approve":
        return "offline release rehearsal gate passed with cited evidence"
    if decision == "hold":
        return "offline release rehearsal gate remains blocked pending reviewer follow-up"
    return "offline release rehearsal gate identifies a blocker requiring rejection for this review packet"


def _rollback_readiness_confirmations(rehearsal_gate_v2: Mapping[str, Any], decision_rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    checkpoint_citations = _dedupe_strings(
        citation
        for checkpoint in _mapping_sequence(rehearsal_gate_v2.get("rollback_checkpoints"))
        for citation in _string_sequence(checkpoint.get("citations"))
    )
    confirmations: List[Dict[str, Any]] = []
    for index, row in enumerate(decision_rows):
        row_citations = _string_sequence(row.get("citations"))
        confirmations.append(
            {
                "rollback_readiness_ref": f"rollback-readiness-{index + 1:03d}",
                "artifact_id": _text(row.get("artifact_id")),
                "ready_for_future_manual_release_review": True,
                "active_release_state_changed": False,
                "confirmation": "rollback path is fixture-referenced for later human-supervised release review only",
                "citations": _dedupe_strings(row_citations + checkpoint_citations) or ["rollback-readiness:offline-fixture"],
            }
        )
    return confirmations


def _validation_commands(rehearsal_gate_v2: Mapping[str, Any]) -> List[List[str]]:
    commands: List[Sequence[str]] = [list(command) for command in DEFAULT_VALIDATION_COMMANDS]
    for key in ("validation_replay_commands", "exact_validation_commands", "exact_offline_validation_commands"):
        for command in _sequence(rehearsal_gate_v2.get(key)):
            if _is_command(command):
                commands.append(command)
    return [list(command) for command in _dedupe_commands(commands)]


def _validate_transcript_placeholder(value: Any, index: int, errors: List[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"reviewer_decisions[{index}].validation_transcript_review_placeholder must be an object")
        return
    if not _text(value.get("placeholder_id")):
        errors.append(f"reviewer_decisions[{index}].validation_transcript_review_placeholder.placeholder_id must be present")
    if _text(value.get("status")) != "pending_human_review":
        errors.append(f"reviewer_decisions[{index}].validation_transcript_review_placeholder.status must be pending_human_review")
    if not _text(value.get("required_review")):
        errors.append(f"reviewer_decisions[{index}].validation_transcript_review_placeholder.required_review must be present")
    if value.get("no_transcript_artifact_stored") is not True:
        errors.append(f"reviewer_decisions[{index}].validation_transcript_review_placeholder.no_transcript_artifact_stored must be true")


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
                errors.append(f"{child_path} is not allowed in offline release reviewer disposition packet v2")
            if normalized in _MUTATION_KEYS and _active(child):
                errors.append(f"{child_path} declares live, official, promotion, release-state, or active mutation behavior")
            _reject_unsafe_content(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        for pattern in _UNSAFE_TEXT_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path} contains unsafe live, private, raw, guarantee, promotion, or consequential action language")
                break


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
