"""Fixture-first inactive promotion candidate packet v2 validation.

Consumes approved combined recrawl-and-DevHub inactive dependency rehearsal rows
and emits inactive candidate deltas only. This module never crawls, opens DevHub,
creates browser/session artifacts, downloads documents, or mutates active PP&D
artifacts.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.inactive_promotion_candidate_packet.v2"
PACKET_VERSION = "v2"
EXPECTED_REHEARSAL_ID = "combined_recrawl_devhub_inactive_patch_dependency_rehearsal_v1"
EXACT_OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/inactive_promotion_candidate_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_inactive_promotion_candidate_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

REQUIRED_PACKET_SECTIONS = (
    "consumed_approved_dependency_row_ids",
    "inactive_source_registry_candidate_deltas",
    "inactive_archive_manifest_candidate_deltas",
    "inactive_normalized_document_candidate_references",
    "inactive_devhub_surface_candidate_deltas",
    "guardrail_replay_prerequisites",
    "reviewer_signoff_placeholders",
)

MUTATION_FLAGS = {
    "active_archive_manifest_mutation",
    "active_artifact_mutation",
    "active_devhub_surface_mutation",
    "active_document_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_source_registry_mutation",
    "active_surface_mutation",
    "archive_manifest_mutated",
    "devhub_surface_mutated",
    "document_mutated",
    "guardrail_mutated",
    "process_mutated",
    "prompt_mutated",
    "release_state_mutated",
    "source_mutated",
    "source_registry_mutated",
    "surface_mutated",
}

PRIVATE_OR_RAW_KEY_TOKENS = (
    "auth",
    "browser",
    "cookie",
    "credential",
    "devhub_session",
    "download",
    "downloaded",
    "har",
    "password",
    "payment",
    "private",
    "raw",
    "screenshot",
    "session",
    "storage_state",
    "token",
    "trace",
    "warc",
)

PRIVATE_OR_RAW_VALUE_TOKENS = (
    "auth state",
    "browser state",
    "cookie jar",
    "downloaded document",
    "har file",
    "private devhub",
    "raw crawl",
    "raw body",
    "raw html",
    "raw pdf",
    "session storage",
    "storage state",
    "trace.zip",
    "warc payload",
)

LIVE_EXECUTION_TOKENS = (
    "live crawl completed",
    "live devhub access",
    "live execution completed",
    "opened browser",
    "promotion completed",
    "promoted to active",
    "release state updated",
)

OFFICIAL_ACTION_TOKENS = (
    "agent may certify",
    "agent may pay",
    "agent may schedule",
    "agent may submit",
    "agent may upload",
    "certify acknowledgement",
    "click submit",
    "official action",
    "pay fees",
    "schedule inspection",
    "submit payment",
    "submit permit",
    "upload corrections",
)

GUARANTEE_TOKENS = (
    "approval guaranteed",
    "guaranteed approval",
    "legal advice",
    "legal guarantee",
    "legally compliant",
    "permit will be approved",
    "permit will issue",
)


@dataclass(frozen=True)
class InactivePromotionCandidatePacketV2ValidationResult:
    valid: bool
    problems: tuple[str, ...]


class InactivePromotionCandidatePacketV2Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid inactive promotion candidate packet v2: " + "; ".join(self.problems))


def load_json_object(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object at {path}")
    return value


def build_inactive_promotion_candidate_packet_v2_from_file(path: str | Path) -> dict[str, Any]:
    return build_inactive_promotion_candidate_packet_v2(load_json_object(path))


def build_inactive_promotion_candidate_packet_v2(rehearsal: Mapping[str, Any]) -> dict[str, Any]:
    problems = _validate_rehearsal_input(rehearsal)
    if problems:
        raise InactivePromotionCandidatePacketV2Error(problems)

    rows = sorted(_mapping_sequence(rehearsal.get("dependency_rows")), key=lambda row: int(row.get("dependency_order", 9999)))
    packet: dict[str, Any] = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "mode": "fixture_first_inactive_candidate_only",
        "candidate_only": True,
        "metadata_only": True,
        "source_rehearsal_id": str(rehearsal.get("rehearsal_id")),
        "consumed_approved_dependency_row_ids": [str(row.get("dependency_id")) for row in rows],
        "inactive_source_registry_candidate_deltas": [_source_registry_delta(row) for row in rows],
        "inactive_archive_manifest_candidate_deltas": [_archive_manifest_delta(row) for row in rows],
        "inactive_normalized_document_candidate_references": [_document_reference(row) for row in rows],
        "inactive_devhub_surface_candidate_deltas": [_devhub_surface_delta(row) for row in rows],
        "guardrail_replay_prerequisites": [_guardrail_prerequisite(row) for row in rows],
        "reviewer_signoff_placeholders": [_reviewer_signoff(row) for row in rows],
        "exact_offline_validation_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
        "side_effect_attestations": {
            "active_source_registry_mutation": False,
            "active_source_mutation": False,
            "active_archive_manifest_mutation": False,
            "active_document_mutation": False,
            "active_devhub_surface_mutation": False,
            "active_surface_mutation": False,
            "active_guardrail_mutation": False,
            "active_prompt_mutation": False,
            "active_release_state_mutation": False,
            "active_process_mutation": False,
            "live_crawl_performed": False,
            "devhub_accessed": False,
            "official_action_performed": False,
        },
    }
    assert_valid_inactive_promotion_candidate_packet_v2(packet)
    return packet


def assert_valid_inactive_promotion_candidate_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_inactive_promotion_candidate_packet_v2(packet)
    if not result.valid:
        raise InactivePromotionCandidatePacketV2Error(result.problems)


def validate_inactive_promotion_candidate_packet_v2(packet: Mapping[str, Any]) -> InactivePromotionCandidatePacketV2ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return InactivePromotionCandidatePacketV2ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v2")
    for key in ("candidate_only", "metadata_only"):
        if packet.get(key) is not True:
            problems.append(f"{key} must be true")
    for key in REQUIRED_PACKET_SECTIONS:
        if not _non_empty_sequence(packet.get(key)):
            problems.append(f"{key} must be a non-empty list")
    if packet.get("exact_offline_validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        problems.append("exact_offline_validation_commands must match the required offline replay commands")

    _validate_delta_rows(packet, problems)
    _validate_cross_refs(packet, problems)
    _validate_no_forbidden_payload(packet, problems)
    return InactivePromotionCandidatePacketV2ValidationResult(not problems, tuple(problems))


def _validate_rehearsal_input(rehearsal: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    if not isinstance(rehearsal, Mapping):
        return ["approved combined rehearsal must be an object"]
    if rehearsal.get("rehearsal_id") != EXPECTED_REHEARSAL_ID:
        problems.append(f"rehearsal_id must be {EXPECTED_REHEARSAL_ID}")
    rows = _mapping_sequence(rehearsal.get("dependency_rows"))
    if not rows:
        problems.append("dependency_rows must be non-empty")
    for index, row in enumerate(rows):
        prefix = f"dependency_rows[{index}]"
        if row.get("reviewer_approval_status") != "approved_for_inactive_candidate_packet_v2":
            problems.append(f"{prefix}.reviewer_approval_status must approve inactive candidate packet v2 consumption")
        if not _text(row.get("dependency_id")):
            problems.append(f"{prefix}.dependency_id is required")
        public_patch = _mapping(row.get("public_source_patch"))
        surface_patch = _mapping(row.get("devhub_surface_patch"))
        if not public_patch:
            problems.append(f"{prefix}.public_source_patch is required")
        if not surface_patch:
            problems.append(f"{prefix}.devhub_surface_patch is required")
        if not _text(public_patch.get("source_id")):
            problems.append(f"{prefix}.public_source_patch.source_id is required")
        if not _string_sequence(public_patch.get("evidence_ids")):
            problems.append(f"{prefix}.public_source_patch.evidence_ids must be non-empty")
        if not _text(surface_patch.get("surface_id")):
            problems.append(f"{prefix}.devhub_surface_patch.surface_id is required")
        if surface_patch.get("requires_attendance") is not True:
            problems.append(f"{prefix}.devhub_surface_patch.requires_attendance must be true")
    _validate_no_forbidden_payload(rehearsal, problems)
    return problems


def _source_registry_delta(row: Mapping[str, Any]) -> dict[str, Any]:
    public_patch = _mapping(row.get("public_source_patch"))
    source_id = _text(public_patch.get("source_id"))
    return {
        "candidate_delta_id": f"inactive-source-registry-delta:{source_id}",
        "dependency_row_id": _text(row.get("dependency_id")),
        "source_id": source_id,
        "canonical_url": _text(public_patch.get("canonical_url")),
        "candidate_status": "inactive_pending_manual_signoff",
        "owning_surface": "ppd_public_source_registry",
        "evidence_ids": _string_sequence(public_patch.get("evidence_ids")),
        "changed_requirement_ids": _string_sequence(public_patch.get("changed_requirement_ids")),
        "active_source_registry_mutation": False,
        "active_source_mutation": False,
    }


def _archive_manifest_delta(row: Mapping[str, Any]) -> dict[str, Any]:
    public_patch = _mapping(row.get("public_source_patch"))
    source_id = _text(public_patch.get("source_id"))
    return {
        "candidate_delta_id": f"inactive-archive-manifest-delta:{source_id}",
        "dependency_row_id": _text(row.get("dependency_id")),
        "source_id": source_id,
        "manifest_id": f"inactive-candidate-manifest:{source_id}",
        "canonical_url": _text(public_patch.get("canonical_url")),
        "archive_artifact_ref": "placeholder:inactive-metadata-only-no-artifact",
        "normalized_document_ref": f"inactive-normalized-document:{source_id}",
        "raw_body_persisted": False,
        "active_archive_manifest_mutation": False,
    }


def _document_reference(row: Mapping[str, Any]) -> dict[str, Any]:
    public_patch = _mapping(row.get("public_source_patch"))
    source_id = _text(public_patch.get("source_id"))
    return {
        "candidate_reference_id": f"inactive-normalized-document:{source_id}",
        "dependency_row_id": _text(row.get("dependency_id")),
        "source_id": source_id,
        "document_id": f"inactive-doc-candidate:{source_id}",
        "source_evidence_ids": _string_sequence(public_patch.get("evidence_ids")),
        "candidate_status": "inactive_reference_only",
        "active_document_mutation": False,
    }


def _devhub_surface_delta(row: Mapping[str, Any]) -> dict[str, Any]:
    surface_patch = _mapping(row.get("devhub_surface_patch"))
    surface_id = _text(surface_patch.get("surface_id"))
    return {
        "candidate_delta_id": f"inactive-devhub-surface-delta:{surface_id}",
        "dependency_row_id": _text(row.get("dependency_id")),
        "surface_id": surface_id,
        "observed_surface_ref": _text(surface_patch.get("observed_surface_ref")),
        "related_source_ids": _string_sequence(surface_patch.get("related_source_ids")),
        "action_labels": _string_sequence(surface_patch.get("action_labels")),
        "requires_attendance": True,
        "requires_exact_confirmation": True,
        "candidate_status": "inactive_pending_manual_signoff",
        "active_devhub_surface_mutation": False,
        "active_surface_mutation": False,
    }


def _guardrail_prerequisite(row: Mapping[str, Any]) -> dict[str, Any]:
    dependency_id = _text(row.get("dependency_id"))
    public_patch = _mapping(row.get("public_source_patch"))
    surface_patch = _mapping(row.get("devhub_surface_patch"))
    return {
        "guardrail_replay_ref": f"guardrail-replay-prerequisite:{dependency_id}",
        "dependency_row_id": dependency_id,
        "required_source_evidence_ids": _string_sequence(public_patch.get("evidence_ids")),
        "required_requirement_ids": _string_sequence(public_patch.get("changed_requirement_ids")),
        "required_surface_ids": [_text(surface_patch.get("surface_id"))],
        "expected_replay_mode": "offline_fixture_only",
        "required_commands": EXACT_OFFLINE_VALIDATION_COMMANDS,
        "active_guardrail_mutation": False,
    }


def _reviewer_signoff(row: Mapping[str, Any]) -> dict[str, Any]:
    dependency_id = _text(row.get("dependency_id"))
    return {
        "signoff_id": f"reviewer-signoff:{dependency_id}",
        "dependency_row_id": dependency_id,
        "reviewer": "",
        "reviewed_at": "",
        "decision": "pending_manual_review",
        "notes": "",
    }


def _validate_delta_rows(packet: Mapping[str, Any], problems: list[str]) -> None:
    for key in REQUIRED_PACKET_SECTIONS:
        for index, row in enumerate(_mapping_sequence(packet.get(key))):
            prefix = f"{key}[{index}]"
            if not _text(row.get("dependency_row_id")):
                problems.append(f"{prefix}.dependency_row_id is required")
            if row.get("candidate_status") == "active":
                problems.append(f"{prefix}.candidate_status must not be active")

    for index, row in enumerate(_mapping_sequence(packet.get("guardrail_replay_prerequisites"))):
        prefix = f"guardrail_replay_prerequisites[{index}]"
        if row.get("expected_replay_mode") != "offline_fixture_only":
            problems.append(f"{prefix}.expected_replay_mode must be offline_fixture_only")
        if row.get("required_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
            problems.append(f"{prefix}.required_commands must match the required offline replay commands")
        for field in ("required_source_evidence_ids", "required_requirement_ids", "required_surface_ids"):
            if not _string_sequence(row.get(field)):
                problems.append(f"{prefix}.{field} must be a non-empty list")

    for index, row in enumerate(_mapping_sequence(packet.get("inactive_devhub_surface_candidate_deltas"))):
        if row.get("requires_attendance") is not True:
            problems.append(f"inactive_devhub_surface_candidate_deltas[{index}].requires_attendance must be true")
        if row.get("requires_exact_confirmation") is not True:
            problems.append(f"inactive_devhub_surface_candidate_deltas[{index}].requires_exact_confirmation must be true")

    for index, row in enumerate(_mapping_sequence(packet.get("reviewer_signoff_placeholders"))):
        prefix = f"reviewer_signoff_placeholders[{index}]"
        for field in ("signoff_id", "dependency_row_id", "reviewer", "reviewed_at", "decision", "notes"):
            if field not in row:
                problems.append(f"{prefix}.{field} is required")
        if row.get("decision") != "pending_manual_review":
            problems.append(f"{prefix}.decision must be pending_manual_review")
        if row.get("reviewer") != "" or row.get("reviewed_at") != "" or row.get("notes") != "":
            problems.append(f"{prefix} must remain an unsigned reviewer placeholder")


def _validate_cross_refs(packet: Mapping[str, Any], problems: list[str]) -> None:
    consumed = set(_string_sequence(packet.get("consumed_approved_dependency_row_ids")))
    for key in REQUIRED_PACKET_SECTIONS[1:]:
        refs = {_text(row.get("dependency_row_id")) for row in _mapping_sequence(packet.get(key))}
        if refs != consumed:
            problems.append(f"{key} must reference every consumed approved dependency row")


def _validate_no_forbidden_payload(packet: Mapping[str, Any], problems: list[str]) -> None:
    for path, key, value in _walk(packet):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in MUTATION_FLAGS and value is not False:
            problems.append(f"{path} must be false")
        if any(token in normalized_key for token in PRIVATE_OR_RAW_KEY_TOKENS) and _truthy(value):
            problems.append(f"{path} must not include private, session, browser, raw, downloaded, or payment artifacts")
        if isinstance(value, str):
            text = value.lower()
            if any(token in text for token in PRIVATE_OR_RAW_VALUE_TOKENS):
                problems.append(f"{path} must not reference private, session, browser, raw, downloaded, or payment artifacts")
            if any(token in text for token in LIVE_EXECUTION_TOKENS):
                problems.append(f"{path} must not claim live execution or active promotion")
            if any(token in text for token in OFFICIAL_ACTION_TOKENS):
                problems.append(f"{path} must not include official-action language")
            if any(token in text for token in GUARANTEE_TOKENS):
                problems.append(f"{path} must not guarantee permitting or legal outcomes")


def _walk(value: Any, prefix: str = "packet", key: str = "packet") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{prefix}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{prefix}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and bool(value)


def _string_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == "":
        return False
    if isinstance(value, Mapping) and not value:
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
