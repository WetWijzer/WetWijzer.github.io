"""Fixture-first DevHub manual observation reviewer queue v1.

This module converts a synthetic DevHub observation evidence intake packet and a
release gate decision matrix into read-only reviewer queue items. It is designed
for committed fixtures and offline validation only; it does not open browsers,
log in, click through flows, upload files, submit forms, schedule inspections,
process payments, or persist private session artifacts.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

REQUIRED_ATTESTATIONS: Sequence[str] = (
    "no_login_automation",
    "no_session_state",
    "no_screenshot",
    "no_trace",
    "no_har",
    "no_click_through",
    "no_upload",
    "no_submit",
    "no_payment",
    "no_scheduling",
    "no_write_capable_action_evidence",
)

REQUIRED_REVIEW_FIELDS: Sequence[str] = (
    "page_heading",
    "accessible_landmarks",
    "validation_message_expectations",
    "redaction_checks",
    "attendance_requirements",
    "stop_before_action_gates",
    "reviewer_owner",
    "rollback_notes",
    "offline_validation_commands",
)

MUTATION_FLAG_FIELDS: Sequence[str] = (
    "active_devhub_mutation",
    "active_surface_registry_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
)

PRIVATE_KEY_PATTERNS: Sequence[str] = (
    "password",
    "credential",
    "cookie",
    "token",
    "secret",
    "auth_state",
    "session_state",
    "storage_state",
    "account_email",
    "account_name",
    "private_account_value",
    "raw_authenticated_page_value",
    "payment_detail",
)

ARTIFACT_KEY_PATTERNS: Sequence[str] = (
    "session_file",
    "session_path",
    "screenshot",
    "trace",
    "har",
    "download_path",
    "local_private_file_path",
)

AUTOMATION_KEY_PATTERNS: Sequence[str] = (
    "captcha",
    "mfa",
    "totp",
    "otp",
    "automated_login",
    "login_automation",
    "account_creation",
    "password_recovery",
)

WRITE_ACTION_VALUES: Sequence[str] = (
    "click_submit",
    "submit_permit",
    "submit_payment",
    "enter_payment_details",
    "upload_file",
    "upload_correction",
    "schedule_inspection",
    "cancel_permit",
    "withdraw_request",
    "certify_acknowledgement",
    "create_account",
    "solve_captcha",
    "complete_mfa",
)

PRIVATE_VALUE_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"),
    re.compile(r"\\b(?:password|credential|cookie|bearer token|session token)\\s*[:=]", re.IGNORECASE),
    re.compile(r"\\b(?:storage_state|auth_state|session)\\.(?:json|yaml|yml)\\b", re.IGNORECASE),
    re.compile(r"(?:^|[\\s'/\\\\])(?:trace\\.zip|[^\\s]+\\.har|[^\\s]+\\.(?:png|jpg|jpeg))\\b", re.IGNORECASE),
    re.compile(r"\\b(?:permit|application|ivr)[-_ ]?(?:number|id)\\s*[:=]\\s*[A-Z0-9-]{4,}", re.IGNORECASE),
)

UNSAFE_LANGUAGE_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"\\b(?:automate|complete|bypass|solve)\\s+(?:login|captcha|mfa|multi-factor|account creation|account setup)\\b", re.IGNORECASE),
    re.compile(r"\\b(?:click|press|select|execute|perform)\\s+(?:submit|certify|pay|payment|upload|schedule|cancel|withdraw|create account)\\b", re.IGNORECASE),
    re.compile(r"\\b(?:submit|certify|pay|upload|schedule|cancel|withdraw)\\s+(?:the\\s+)?(?:permit|application|request|payment|fee|document|correction|inspection)\\b", re.IGNORECASE),
)

SAFE_LANGUAGE_PREFIXES: Sequence[str] = (
    "stop before",
    "do not",
    "does not",
    "must not",
    "must be absent",
    "no ",
    "without ",
    "blocked before",
    "refuse ",
    "refuses ",
)


class ReviewerQueueError(ValueError):
    """Raised when fixture data cannot produce a valid reviewer queue."""


@dataclass(frozen=True)
class ReviewerQueueItem:
    """A cited read-only DevHub manual observation review item."""

    queue_item_id: str
    surface_id: str
    title: str
    page_heading: str
    accessible_landmarks: List[str]
    validation_message_expectations: List[str]
    redaction_checks: List[str]
    attendance_requirements: List[str]
    stop_before_action_gates: List[str]
    reviewer_owner: str
    rollback_notes: List[str]
    offline_validation_commands: List[List[str]]
    citations: List[Dict[str, str]]
    attestations: Dict[str, bool]
    mutation_flags: Dict[str, bool]
    release_gate_decision: str
    release_gate_reasons: List[str]
    read_only_scope: bool
    synthetic_fixture: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "queue_item_id": self.queue_item_id,
            "surface_id": self.surface_id,
            "title": self.title,
            "page_heading": self.page_heading,
            "accessible_landmarks": list(self.accessible_landmarks),
            "validation_message_expectations": list(self.validation_message_expectations),
            "redaction_checks": list(self.redaction_checks),
            "attendance_requirements": list(self.attendance_requirements),
            "stop_before_action_gates": list(self.stop_before_action_gates),
            "reviewer_owner": self.reviewer_owner,
            "rollback_notes": list(self.rollback_notes),
            "offline_validation_commands": [list(command) for command in self.offline_validation_commands],
            "citations": [dict(citation) for citation in self.citations],
            "attestations": dict(self.attestations),
            "mutation_flags": dict(self.mutation_flags),
            "release_gate_decision": self.release_gate_decision,
            "release_gate_reasons": list(self.release_gate_reasons),
            "read_only_scope": self.read_only_scope,
            "synthetic_fixture": self.synthetic_fixture,
        }


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ReviewerQueueError(f"{path} must contain a JSON object")
    return data


def build_reviewer_queue(
    evidence_packet: Mapping[str, Any],
    release_gate_matrix: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    """Build cited synthetic reviewer queue items from fixture dictionaries."""

    _validate_packet_header(evidence_packet)
    _validate_commit_safe_payload(evidence_packet, "evidence_packet")
    matrix_by_surface = _release_gates_by_surface(release_gate_matrix)
    _validate_commit_safe_payload(release_gate_matrix, "release_gate_matrix")
    observations = evidence_packet.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ReviewerQueueError("evidence packet requires at least one observation")

    items: List[ReviewerQueueItem] = []
    for index, observation in enumerate(observations, start=1):
        if not isinstance(observation, dict):
            raise ReviewerQueueError("each observation must be an object")
        _validate_commit_safe_payload(observation, f"observations[{index}]")
        surface_id = _required_text(observation, "surface_id")
        gate = matrix_by_surface.get(surface_id)
        if gate is None:
            raise ReviewerQueueError(f"missing release gate decision for surface {surface_id}")
        _validate_commit_safe_payload(gate, f"release_gate[{surface_id}]")
        item = _build_item(index, observation, gate)
        _validate_item(item)
        items.append(item)

    return [item.to_dict() for item in items]


def build_reviewer_queue_from_files(evidence_packet_path: Path, release_gate_matrix_path: Path) -> List[Dict[str, Any]]:
    return build_reviewer_queue(load_json(evidence_packet_path), load_json(release_gate_matrix_path))


def _build_item(index: int, observation: Mapping[str, Any], gate: Mapping[str, Any]) -> ReviewerQueueItem:
    surface_id = _required_text(observation, "surface_id")
    title = _required_text(observation, "title")
    evidence_ids = _required_text_list(observation, "source_evidence_ids")
    citations = _citations(observation, gate, evidence_ids)
    attestations = _attestations(observation, gate)
    mutation_flags = _mutation_flags(observation, gate)

    return ReviewerQueueItem(
        queue_item_id=f"devhub-manual-observation-review-v1-{index:03d}",
        surface_id=surface_id,
        title=title,
        page_heading=_required_text(observation, "page_heading"),
        accessible_landmarks=_required_text_list(observation, "accessible_landmarks"),
        validation_message_expectations=_required_text_list(observation, "validation_message_expectations"),
        redaction_checks=_required_text_list(observation, "redaction_checks"),
        attendance_requirements=_required_text_list(observation, "attendance_requirements"),
        stop_before_action_gates=_combined_unique_text(
            observation.get("stop_before_action_gates"),
            gate.get("required_stop_gates"),
        ),
        reviewer_owner=_required_text(gate, "reviewer_owner"),
        rollback_notes=_required_text_list(gate, "rollback_notes"),
        offline_validation_commands=_offline_commands(gate),
        citations=citations,
        attestations=attestations,
        mutation_flags=mutation_flags,
        release_gate_decision=_required_text(gate, "decision"),
        release_gate_reasons=_required_text_list(gate, "decision_reasons"),
        read_only_scope=_required_bool(observation, "read_only_scope") and _required_bool(gate, "read_only_scope"),
        synthetic_fixture=_required_bool(observation, "synthetic_fixture") and _required_bool(gate, "synthetic_fixture"),
    )


def _validate_packet_header(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_version") != "devhub_observation_evidence_intake_packet_v1":
        raise ReviewerQueueError("unsupported evidence packet version")
    if packet.get("capture_mode") != "synthetic_fixture_only":
        raise ReviewerQueueError("evidence packet must be synthetic fixture only")


def _release_gates_by_surface(matrix: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    if matrix.get("matrix_version") != "devhub_release_gate_decision_matrix_v1":
        raise ReviewerQueueError("unsupported release gate matrix version")
    decisions = matrix.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ReviewerQueueError("release gate matrix requires decisions")

    by_surface: Dict[str, Mapping[str, Any]] = {}
    for decision in decisions:
        if not isinstance(decision, dict):
            raise ReviewerQueueError("each release gate decision must be an object")
        surface_id = _required_text(decision, "surface_id")
        if surface_id in by_surface:
            raise ReviewerQueueError(f"duplicate release gate decision for surface {surface_id}")
        by_surface[surface_id] = decision
    return by_surface


def _validate_item(item: ReviewerQueueItem) -> None:
    item_dict = item.to_dict()
    missing = [field for field in REQUIRED_REVIEW_FIELDS if not item_dict.get(field)]
    if missing:
        raise ReviewerQueueError(f"queue item {item.queue_item_id} missing fields: {', '.join(missing)}")
    if item.release_gate_decision != "manual_review_required_read_only":
        raise ReviewerQueueError(f"queue item {item.queue_item_id} has unsupported release gate decision")
    if not item.read_only_scope or not item.synthetic_fixture:
        raise ReviewerQueueError(f"queue item {item.queue_item_id} must remain read-only synthetic fixture data")
    failed_attestations = [name for name, value in item.attestations.items() if not value]
    if failed_attestations:
        raise ReviewerQueueError(
            f"queue item {item.queue_item_id} failed attestations: {', '.join(failed_attestations)}"
        )
    missing_attestations = [name for name in REQUIRED_ATTESTATIONS if name not in item.attestations]
    if missing_attestations:
        raise ReviewerQueueError(
            f"queue item {item.queue_item_id} missing attestations: {', '.join(missing_attestations)}"
        )
    active_mutations = [name for name, value in item.mutation_flags.items() if value]
    if active_mutations:
        raise ReviewerQueueError(
            f"queue item {item.queue_item_id} has active mutation flags: {', '.join(active_mutations)}"
        )
    if not item.citations:
        raise ReviewerQueueError(f"queue item {item.queue_item_id} requires citations")


def _validate_commit_safe_payload(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ReviewerQueueError(f"{path} contains a non-string key")
            normalized_key = key.lower().replace("-", "_")
            if any(pattern in normalized_key for pattern in PRIVATE_KEY_PATTERNS):
                raise ReviewerQueueError(f"{path}.{key} contains private account or credential material")
            if any(pattern in normalized_key for pattern in ARTIFACT_KEY_PATTERNS):
                raise ReviewerQueueError(f"{path}.{key} contains prohibited browser artifact evidence")
            if any(pattern in normalized_key for pattern in AUTOMATION_KEY_PATTERNS):
                raise ReviewerQueueError(f"{path}.{key} contains prohibited login/CAPTCHA/MFA/account automation handling")
            if normalized_key in MUTATION_FLAG_FIELDS and child is True:
                raise ReviewerQueueError(f"{path}.{key} is an active mutation flag")
            _validate_commit_safe_payload(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_commit_safe_payload(child, f"{path}[{index}]")
    elif isinstance(value, str):
        _validate_commit_safe_text(value, path)


def _validate_commit_safe_text(value: str, path: str) -> None:
    for pattern in PRIVATE_VALUE_PATTERNS:
        if pattern.search(value):
            raise ReviewerQueueError(f"{path} contains private value or browser artifact text")
    normalized = " ".join(value.lower().split())
    if normalized in WRITE_ACTION_VALUES:
        raise ReviewerQueueError(f"{path} contains write-capable action evidence")
    if any(normalized.startswith(prefix) for prefix in SAFE_LANGUAGE_PREFIXES):
        return
    for pattern in UNSAFE_LANGUAGE_PATTERNS:
        if pattern.search(value):
            raise ReviewerQueueError(f"{path} contains prohibited automation or consequential action language")


def _citations(
    observation: Mapping[str, Any],
    gate: Mapping[str, Any],
    evidence_ids: Iterable[str],
) -> List[Dict[str, str]]:
    packet_citations = observation.get("citations")
    if not isinstance(packet_citations, list) or not packet_citations:
        raise ReviewerQueueError("observation requires citations")

    citations: List[Dict[str, str]] = []
    for citation in packet_citations:
        if not isinstance(citation, dict):
            raise ReviewerQueueError("citations must be objects")
        citations.append(
            {
                "source_evidence_id": _required_text(citation, "source_evidence_id"),
                "source_label": _required_text(citation, "source_label"),
                "quote_or_note": _required_text(citation, "quote_or_note"),
            }
        )

    gate_citation = gate.get("citation")
    if isinstance(gate_citation, dict):
        citations.append(
            {
                "source_evidence_id": _required_text(gate_citation, "source_evidence_id"),
                "source_label": _required_text(gate_citation, "source_label"),
                "quote_or_note": _required_text(gate_citation, "quote_or_note"),
            }
        )

    cited_ids = {citation["source_evidence_id"] for citation in citations}
    uncited_ids = [evidence_id for evidence_id in evidence_ids if evidence_id not in cited_ids]
    if uncited_ids:
        raise ReviewerQueueError(f"uncited evidence ids: {', '.join(uncited_ids)}")
    return citations


def _attestations(observation: Mapping[str, Any], gate: Mapping[str, Any]) -> Dict[str, bool]:
    merged: Dict[str, bool] = {}
    for source in (observation.get("attestations"), gate.get("attestations")):
        if not isinstance(source, dict):
            raise ReviewerQueueError("attestations must be objects")
        for name, value in source.items():
            if not isinstance(name, str) or not isinstance(value, bool):
                raise ReviewerQueueError("attestation keys must be strings and values must be booleans")
            merged[name] = value
    return merged


def _mutation_flags(observation: Mapping[str, Any], gate: Mapping[str, Any]) -> Dict[str, bool]:
    flags = {name: False for name in MUTATION_FLAG_FIELDS}
    for source in (observation, gate):
        source_flags = source.get("mutation_flags")
        if isinstance(source_flags, Mapping):
            for name in MUTATION_FLAG_FIELDS:
                value = source_flags.get(name)
                if value is not None and not isinstance(value, bool):
                    raise ReviewerQueueError(f"{name} must be a boolean mutation flag")
                if value is True:
                    flags[name] = True
        for name in MUTATION_FLAG_FIELDS:
            value = source.get(name)
            if value is not None and not isinstance(value, bool):
                raise ReviewerQueueError(f"{name} must be a boolean mutation flag")
            if value is True:
                flags[name] = True
    return flags


def _offline_commands(gate: Mapping[str, Any]) -> List[List[str]]:
    commands = gate.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        raise ReviewerQueueError("offline validation commands are required")
    normalized: List[List[str]] = []
    for command in commands:
        if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
            raise ReviewerQueueError("offline validation commands must be non-empty string arrays")
        normalized.append(list(command))
    return normalized


def _combined_unique_text(first: Any, second: Any) -> List[str]:
    values: List[str] = []
    for source in (first, second):
        if not isinstance(source, list):
            raise ReviewerQueueError("stop-before-action gates must be arrays")
        for value in source:
            if not isinstance(value, str) or not value.strip():
                raise ReviewerQueueError("stop-before-action gates must be non-empty strings")
            if value not in values:
                values.append(value)
    return values


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ReviewerQueueError(f"{key} must be a non-empty string")
    return value


def _required_text_list(mapping: Mapping[str, Any], key: str) -> List[str]:
    value = mapping.get(key)
    if not isinstance(value, list) or not value:
        raise ReviewerQueueError(f"{key} must be a non-empty string array")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ReviewerQueueError(f"{key} must contain only non-empty strings")
    return list(value)


def _required_bool(mapping: Mapping[str, Any], key: str) -> bool:
    value = mapping.get(key)
    if not isinstance(value, bool):
        raise ReviewerQueueError(f"{key} must be a boolean")
    return value
