"""Fixture-first process model assembly packet v4 validation."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.process_model_assembly_packet.v4"
PACKET_VERSION = "v4"
VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

REQUIRED_TOP_LEVEL_SEQUENCES = (
    "synthetic_requirement_nodes",
    "eligibility_rule_rows",
    "required_user_fact_rows",
    "document_requirement_matrix_rows",
    "fee_deadline_trigger_rows",
    "unsupported_path_notes",
    "devhub_boundary_rows",
    "citation_spans",
    "stale_evidence_holds",
    "reviewer_dispositions",
    "inactive_process_model_assembly_recommendations",
    "validation_commands",
)

ACTIVE_MUTATION_FLAGS = (
    "active_process_model_mutation",
    "active_requirement_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_contract_mutation",
    "active_source_registry_mutation",
    "active_devhub_surface_mutation",
    "active_release_state_mutation",
    "active_process_models_changed",
    "requirements_changed",
    "guardrails_changed",
    "prompts_changed",
    "contracts_changed",
    "source_registries_changed",
    "devhub_surfaces_changed",
    "release_state_changed",
)

FORBIDDEN_KEY_TERMS = (
    "auth",
    "browser",
    "captcha",
    "cookie",
    "credential",
    "devhub_session",
    "download",
    "har",
    "live",
    "mfa",
    "payment",
    "private",
    "raw",
    "screenshot",
    "session",
    "submission",
    "token",
    "trace",
    "upload",
)

FORBIDDEN_VALUE_TERMS = (
    "authenticated devhub",
    "browser state",
    "cookie jar",
    "downloaded document",
    "har file",
    "live crawl",
    "live devhub",
    "payment detail",
    "private file",
    "raw crawl",
    "raw download",
    "session storage",
    "submitted to devhub",
    "uploaded to devhub",
)

FORBIDDEN_CLAIM_TERMS = (
    "certified acknowledgement",
    "enter payment",
    "official action completed",
    "official filing completed",
    "permit will be approved",
    "permitting guarantee",
    "purchase permit",
    "schedule inspection",
    "submit payment",
    "submit permit",
    "upload correction",
)

REQUIRED_SYNTHETIC_NODE_FIELDS = (
    "requirement_id",
    "requirement_type",
    "subject",
    "action",
    "object",
    "process_stage",
    "source_evidence_ids",
    "formalization_status",
)

REQUIRED_RECOMMENDATION_FIELDS = (
    "recommendation_id",
    "process_id",
    "permit_type",
    "requirement_node_refs",
    "eligibility_rule_refs",
    "required_user_fact_refs",
    "document_matrix_refs",
    "fee_deadline_trigger_refs",
    "unsupported_path_refs",
    "devhub_boundary_refs",
    "citation_span_refs",
    "stale_evidence_hold_refs",
    "reviewer_disposition_refs",
    "status",
    "activation_blockers",
    "validation_commands",
)


@dataclass(frozen=True)
class ProcessModelAssemblyPacketV4ValidationResult:
    valid: bool
    problems: tuple[str, ...]


class ProcessModelAssemblyPacketV4Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid process model assembly packet v4: " + "; ".join(self.problems))


def load_process_model_assembly_packet_v4(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("process model assembly packet v4 fixture must be a JSON object")
    assert_valid_process_model_assembly_packet_v4(loaded)
    return loaded


def assert_valid_process_model_assembly_packet_v4(packet: Mapping[str, Any]) -> None:
    result = validate_process_model_assembly_packet_v4(packet)
    if not result.valid:
        raise ProcessModelAssemblyPacketV4Error(result.problems)


def validate_process_model_assembly_packet_v4(packet: Mapping[str, Any]) -> ProcessModelAssemblyPacketV4ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return ProcessModelAssemblyPacketV4ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v4")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")
    if packet.get("recommendation_mode") != "inactive_process_model_assembly_recommendations_only":
        problems.append("recommendation_mode must be inactive_process_model_assembly_recommendations_only")
    if packet.get("validation_commands") != VALIDATION_COMMANDS:
        problems.append("validation_commands must contain the PP&D daemon self-test command")

    for key in REQUIRED_TOP_LEVEL_SEQUENCES:
        if not _non_empty_sequence(packet.get(key)):
            problems.append(f"{key} must be a non-empty list")

    for flag in ACTIVE_MUTATION_FLAGS:
        if packet.get(flag) is not False:
            problems.append(f"{flag} must be false")

    _validate_synthetic_nodes(packet.get("synthetic_requirement_nodes"), problems)
    _validate_recommendations(packet.get("inactive_process_model_assembly_recommendations"), problems)
    _validate_cross_refs(packet, problems)
    _validate_no_forbidden_payload(packet, problems)
    return ProcessModelAssemblyPacketV4ValidationResult(not problems, tuple(problems))


def _validate_synthetic_nodes(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"synthetic_requirement_nodes[{index}]"
        for field in REQUIRED_SYNTHETIC_NODE_FIELDS:
            if field not in row:
                problems.append(f"{prefix}.{field} is required")
        if row.get("formalization_status") != "synthetic_fixture_for_review":
            problems.append(f"{prefix}.formalization_status must remain synthetic_fixture_for_review")
        if not _evidence_refs(row.get("source_evidence_ids")):
            problems.append(f"{prefix}.source_evidence_ids must cite fixture or citation evidence")


def _validate_recommendations(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"inactive_process_model_assembly_recommendations[{index}]"
        for field in REQUIRED_RECOMMENDATION_FIELDS:
            if field not in row:
                problems.append(f"{prefix}.{field} is required")
        if row.get("status") != "inactive_recommendation_only":
            problems.append(f"{prefix}.status must be inactive_recommendation_only")
        if row.get("validation_commands") != VALIDATION_COMMANDS:
            problems.append(f"{prefix}.validation_commands must contain the PP&D daemon self-test command")
        if not _non_empty_sequence(row.get("activation_blockers")):
            problems.append(f"{prefix}.activation_blockers must be a non-empty list")


def _validate_cross_refs(packet: Mapping[str, Any], problems: list[str]) -> None:
    ref_sets = {
        "requirement_node_refs": _ids(packet.get("synthetic_requirement_nodes"), "requirement_id"),
        "eligibility_rule_refs": _ids(packet.get("eligibility_rule_rows"), "eligibility_rule_id"),
        "required_user_fact_refs": _ids(packet.get("required_user_fact_rows"), "fact_row_id"),
        "document_matrix_refs": _ids(packet.get("document_requirement_matrix_rows"), "matrix_row_id"),
        "fee_deadline_trigger_refs": _ids(packet.get("fee_deadline_trigger_rows"), "trigger_id"),
        "unsupported_path_refs": _ids(packet.get("unsupported_path_notes"), "unsupported_path_id"),
        "devhub_boundary_refs": _ids(packet.get("devhub_boundary_rows"), "boundary_id"),
        "citation_span_refs": _ids(packet.get("citation_spans"), "citation_span_id"),
        "stale_evidence_hold_refs": _ids(packet.get("stale_evidence_holds"), "hold_id"),
        "reviewer_disposition_refs": _ids(packet.get("reviewer_dispositions"), "disposition_id"),
    }
    for index, row in enumerate(_mapping_sequence(packet.get("inactive_process_model_assembly_recommendations"))):
        prefix = f"inactive_process_model_assembly_recommendations[{index}]"
        for field, allowed in ref_sets.items():
            _require_refs(prefix, field, row.get(field), allowed, problems)


def _validate_no_forbidden_payload(value: Any, problems: list[str], path: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            lowered_key = key_text.lower()
            if any(term in lowered_key for term in FORBIDDEN_KEY_TERMS):
                problems.append(f"{child_path} must not contain live, private, raw, upload, payment, submission, or session artifacts")
            if key_text in ACTIVE_MUTATION_FLAGS and child is not False:
                problems.append(f"{child_path} must be false")
            _validate_no_forbidden_payload(child, problems, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _validate_no_forbidden_payload(child, problems, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered_value = value.lower()
        if any(term in lowered_value for term in FORBIDDEN_VALUE_TERMS):
            problems.append(f"{path} must not contain live, private, raw, uploaded, payment, submission, or session values")
        if any(term in lowered_value for term in FORBIDDEN_CLAIM_TERMS):
            problems.append(f"{path} must not contain consequential action instructions, official-action completion claims, or permitting guarantees")


def _require_refs(prefix: str, field: str, value: Any, allowed: set[str], problems: list[str]) -> None:
    refs = [item for item in _text_sequence(value) if item]
    if not refs:
        problems.append(f"{prefix}.{field} must be a non-empty list")
        return
    for ref in refs:
        if ref not in allowed:
            problems.append(f"{prefix}.{field} contains unknown ref {ref}")


def _ids(value: Any, field: str) -> set[str]:
    return {_text(row.get(field)) for row in _mapping_sequence(value) if _text(row.get(field))}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _text_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in (_text(item) for item in value) if item]


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _evidence_refs(value: Any) -> bool:
    refs = _text_sequence(value)
    return bool(refs) and all(ref.startswith(("fixture-source:", "citation:", "synthetic:")) for ref in refs)
