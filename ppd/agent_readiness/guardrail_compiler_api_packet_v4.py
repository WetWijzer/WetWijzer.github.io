"""Fixture-first guardrail compiler API packet v4.

This module converts synthetic inactive process-model assembly recommendations into
inactive guardrail compiler API rows. It intentionally does not promote guardrails
or mutate active prompts, requirements, process models, contracts, source
registries, DevHub surfaces, or release state.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ppd.agent_readiness.process_model_assembly_packet_v4 import (
    VALIDATION_COMMANDS,
    assert_valid_process_model_assembly_packet_v4,
)

PACKET_TYPE = "ppd.guardrail_compiler_api_packet.v4"
PACKET_VERSION = "v4"
RECOMMENDATION_MODE = "inactive_guardrail_compiler_rows_only"

ACTIVE_MUTATION_FLAGS = (
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_requirement_mutation",
    "active_process_model_mutation",
    "active_contract_mutation",
    "active_source_registry_mutation",
    "active_devhub_surface_mutation",
    "active_release_state_mutation",
    "guardrails_promoted",
    "prompts_changed",
    "requirements_changed",
    "process_models_changed",
    "contracts_changed",
    "source_registries_changed",
    "devhub_surfaces_changed",
    "release_state_changed",
)

REQUIRED_ROW_SEQUENCES = (
    "deterministic_predicate_rows",
    "deontic_rule_rows",
    "temporal_rule_rows",
    "reversible_action_rows",
    "exact_confirmation_rows",
    "refused_action_rows",
    "missing_information_rows",
    "explanation_template_rows",
    "stale_source_hold_rows",
    "reviewer_disposition_rows",
    "offline_validation_command_rows",
)

FORBIDDEN_VALUE_TERMS = (
    "active guardrail",
    "active prompt",
    "active requirement",
    "active process model",
    "auth state",
    "browser state",
    "captcha",
    "certification completed",
    "completed official action",
    "cookie",
    "credential",
    "downloaded document",
    "downloaded pdf",
    "final payment",
    "form filling completed",
    "guarantee",
    "guaranteed",
    "har file",
    "legal advice",
    "legally valid",
    "live crawl",
    "live devhub",
    "mfa",
    "official action completed",
    "payment details entered",
    "permit approved",
    "permitting guarantee",
    "private artifact",
    "private session",
    "raw crawl",
    "raw downloaded",
    "scheduled inspection",
    "screenshot",
    "session storage",
    "storage_state",
    "submitted to devhub",
    "trace.zip",
    "uploaded to devhub",
    "will be approved",
)

DEONTIC_MODALITIES = frozenset(("obligation", "prohibition", "permission"))


@dataclass(frozen=True)
class GuardrailCompilerApiPacketV4ValidationResult:
    valid: bool
    problems: tuple[str, ...]


class GuardrailCompilerApiPacketV4Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid guardrail compiler API packet v4: " + "; ".join(self.problems))


def load_guardrail_compiler_api_packet_v4(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("guardrail compiler API packet v4 fixture must be a JSON object")
    assert_valid_guardrail_compiler_api_packet_v4(loaded)
    return loaded


def assert_valid_guardrail_compiler_api_packet_v4(packet: Mapping[str, Any]) -> None:
    result = validate_guardrail_compiler_api_packet_v4(packet)
    if not result.valid:
        raise GuardrailCompilerApiPacketV4Error(result.problems)


def validate_guardrail_compiler_api_packet_v4(packet: Mapping[str, Any]) -> GuardrailCompilerApiPacketV4ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return GuardrailCompilerApiPacketV4ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v4")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")
    if packet.get("recommendation_mode") != RECOMMENDATION_MODE:
        problems.append(f"recommendation_mode must be {RECOMMENDATION_MODE}")
    if packet.get("validation_commands") != VALIDATION_COMMANDS:
        problems.append("validation_commands must contain the exact PP&D daemon self-test command")

    for flag in ACTIVE_MUTATION_FLAGS:
        if packet.get(flag) is not False:
            problems.append(f"{flag} must be false")

    for key in REQUIRED_ROW_SEQUENCES:
        if not _non_empty_sequence(packet.get(key)):
            problems.append(f"{key} must be a non-empty list")

    _validate_common_rows(packet, problems)
    _validate_required_row_fields(packet, problems)
    _validate_cross_refs(packet, problems)
    _validate_validation_command_rows(packet.get("offline_validation_command_rows"), problems)
    _validate_no_forbidden_values(packet, problems)
    return GuardrailCompilerApiPacketV4ValidationResult(not problems, tuple(problems))


def compile_guardrail_compiler_api_packet_v4(assembly_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build deterministic inactive compiler rows from an assembly packet v4."""

    assert_valid_process_model_assembly_packet_v4(assembly_packet)
    recommendation = _first_mapping(assembly_packet.get("inactive_process_model_assembly_recommendations"))
    process_id = _text(recommendation.get("process_id")) or "inactive-process-model"
    recommendation_id = _text(recommendation.get("recommendation_id")) or "inactive-recommendation"
    permit_type = _text(recommendation.get("permit_type")) or "inactive permit type"
    requirement_refs = _text_sequence(recommendation.get("requirement_node_refs"))
    first_requirement_ref = requirement_refs[0] if requirement_refs else "synthetic-requirement"
    stale_refs = _text_sequence(recommendation.get("stale_evidence_hold_refs"))
    reviewer_refs = _text_sequence(recommendation.get("reviewer_disposition_refs"))

    packet: dict[str, Any] = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "fixture_first": True,
        "recommendation_mode": RECOMMENDATION_MODE,
        "source_packet_type": _text(assembly_packet.get("packet_type")),
        "source_recommendation_id": recommendation_id,
        "process_id": process_id,
        "permit_type": permit_type,
        "active_guardrail_mutation": False,
        "active_prompt_mutation": False,
        "active_requirement_mutation": False,
        "active_process_model_mutation": False,
        "active_contract_mutation": False,
        "active_source_registry_mutation": False,
        "active_devhub_surface_mutation": False,
        "active_release_state_mutation": False,
        "guardrails_promoted": False,
        "prompts_changed": False,
        "requirements_changed": False,
        "process_models_changed": False,
        "contracts_changed": False,
        "source_registries_changed": False,
        "devhub_surfaces_changed": False,
        "release_state_changed": False,
        "deterministic_predicate_rows": [
            {
                "row_id": f"predicate-{process_id}-fixture-first",
                "process_id": process_id,
                "requirement_node_ref": first_requirement_ref,
                "predicate_name": "has_fixture_backed_inactive_assembly_recommendation",
                "deterministic_expression": "source_recommendation_id_present AND status_is_inactive_recommendation_only",
                "output_status": "inactive_compiler_row_only",
            }
        ],
        "deontic_rule_rows": [
            {
                "row_id": f"deontic-{process_id}-attended-boundary",
                "process_id": process_id,
                "requirement_node_refs": requirement_refs,
                "modality": "prohibition",
                "rule_text": "Agent must not perform consequential official actions from synthetic inactive recommendations.",
                "output_status": "inactive_compiler_row_only",
            }
        ],
        "temporal_rule_rows": [
            {
                "row_id": f"temporal-{process_id}-stale-source-hold",
                "process_id": process_id,
                "stale_source_hold_refs": stale_refs,
                "temporal_condition": "until_current_official_source_refresh_and_reviewer_approval",
                "output_status": "inactive_compiler_row_only",
            }
        ],
        "reversible_action_rows": [
            {
                "row_id": f"reversible-{process_id}-offline-draft-planning",
                "process_id": process_id,
                "allowed_action": "offline draft planning from fixture rows",
                "reversibility_basis": "No public or authenticated system side effects are performed.",
                "output_status": "inactive_compiler_row_only",
            }
        ],
        "exact_confirmation_rows": [
            {
                "row_id": f"exact-confirmation-{process_id}-consequential-boundary",
                "process_id": process_id,
                "confirmation_scope": "consequential official PP&D or DevHub action",
                "required_confirmation": "user-attended action-specific confirmation required before any future active workflow",
                "output_status": "inactive_compiler_row_only",
            }
        ],
        "refused_action_rows": [
            {
                "row_id": f"refused-{process_id}-official-actions",
                "process_id": process_id,
                "refused_action_family": "official PP&D account, filing, attachment, payment, scheduling, and certification actions",
                "refusal_reason": "Synthetic inactive compiler packet cannot authorize consequential external effects.",
                "output_status": "inactive_compiler_row_only",
            }
        ],
        "missing_information_rows": [
            {
                "row_id": f"missing-info-{process_id}-source-refresh-review",
                "process_id": process_id,
                "missing_information": "current official-source evidence and reviewer disposition",
                "ask_policy": "ask only for missing, stale, ambiguous, or conflicting facts before active use",
                "output_status": "inactive_compiler_row_only",
            }
        ],
        "explanation_template_rows": [
            {
                "row_id": f"explanation-{process_id}-inactive-source-hold",
                "process_id": process_id,
                "template_key": "inactive_guardrail_compiler_source_hold",
                "template_text": "I can use this only as an offline fixture row because {hold_reason}; reviewer disposition is {reviewer_disposition}.",
                "placeholders": ["hold_reason", "reviewer_disposition"],
                "output_status": "inactive_compiler_row_only",
            }
        ],
        "stale_source_hold_rows": [
            {
                "row_id": f"stale-source-hold-{process_id}-001",
                "process_id": process_id,
                "source_hold_refs": stale_refs,
                "hold_reason": "Synthetic fixture evidence cannot become active without current official-source refresh.",
                "release_condition": "exact offline validation commands pass and reviewer disposition approves refreshed evidence",
                "output_status": "hold_active",
            }
        ],
        "reviewer_disposition_rows": [
            {
                "row_id": f"reviewer-disposition-{process_id}-001",
                "process_id": process_id,
                "reviewer_disposition_refs": reviewer_refs,
                "decision": "pending",
                "required_review": "predicate, deontic, temporal, reversible action, exact confirmation, refused action, missing information, explanation, stale source hold, and validation rows",
                "output_status": "pending_manual_review",
            }
        ],
        "offline_validation_command_rows": [
            {
                "row_id": "offline-validation-command-ppd-self-test",
                "command": VALIDATION_COMMANDS[0],
                "exact": True,
                "output_status": "inactive_compiler_row_only",
            }
        ],
        "validation_commands": VALIDATION_COMMANDS,
    }
    assert_valid_guardrail_compiler_api_packet_v4(packet)
    return packet


def _validate_common_rows(packet: Mapping[str, Any], problems: list[str]) -> None:
    for key in REQUIRED_ROW_SEQUENCES:
        for index, row in enumerate(_mapping_sequence(packet.get(key))):
            prefix = f"{key}[{index}]"
            if not _text(row.get("row_id")):
                problems.append(f"{prefix}.row_id is required")
            if key != "offline_validation_command_rows" and not _text(row.get("process_id")):
                problems.append(f"{prefix}.process_id is required")
            status = _text(row.get("output_status"))
            if key == "stale_source_hold_rows":
                if status != "hold_active":
                    problems.append(f"{prefix}.output_status must be hold_active")
            elif key == "reviewer_disposition_rows":
                if status != "pending_manual_review":
                    problems.append(f"{prefix}.output_status must be pending_manual_review")
            elif status != "inactive_compiler_row_only":
                problems.append(f"{prefix}.output_status must be inactive_compiler_row_only")


def _validate_required_row_fields(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(packet.get("deterministic_predicate_rows"))):
        prefix = f"deterministic_predicate_rows[{index}]"
        _require_text(row, "requirement_node_ref", prefix, problems)
        _require_text(row, "predicate_name", prefix, problems)
        expression = _require_text(row, "deterministic_expression", prefix, problems)
        if expression and " AND " not in expression and " OR " not in expression:
            problems.append(f"{prefix}.deterministic_expression must be an explicit deterministic predicate expression")

    for index, row in enumerate(_mapping_sequence(packet.get("deontic_rule_rows"))):
        prefix = f"deontic_rule_rows[{index}]"
        _require_non_empty_text_sequence(row, "requirement_node_refs", prefix, problems)
        modality = _require_text(row, "modality", prefix, problems)
        if modality and modality not in DEONTIC_MODALITIES:
            problems.append(f"{prefix}.modality must be obligation, prohibition, or permission")
        _require_text(row, "rule_text", prefix, problems)

    for index, row in enumerate(_mapping_sequence(packet.get("temporal_rule_rows"))):
        prefix = f"temporal_rule_rows[{index}]"
        _require_non_empty_text_sequence(row, "stale_source_hold_refs", prefix, problems)
        _require_text(row, "temporal_condition", prefix, problems)

    for index, row in enumerate(_mapping_sequence(packet.get("reversible_action_rows"))):
        prefix = f"reversible_action_rows[{index}]"
        _require_text(row, "allowed_action", prefix, problems)
        _require_text(row, "reversibility_basis", prefix, problems)

    for index, row in enumerate(_mapping_sequence(packet.get("exact_confirmation_rows"))):
        prefix = f"exact_confirmation_rows[{index}]"
        _require_text(row, "confirmation_scope", prefix, problems)
        _require_text(row, "required_confirmation", prefix, problems)

    for index, row in enumerate(_mapping_sequence(packet.get("refused_action_rows"))):
        prefix = f"refused_action_rows[{index}]"
        _require_text(row, "refused_action_family", prefix, problems)
        _require_text(row, "refusal_reason", prefix, problems)

    for index, row in enumerate(_mapping_sequence(packet.get("missing_information_rows"))):
        prefix = f"missing_information_rows[{index}]"
        _require_text(row, "missing_information", prefix, problems)
        _require_text(row, "ask_policy", prefix, problems)

    for index, row in enumerate(_mapping_sequence(packet.get("explanation_template_rows"))):
        prefix = f"explanation_template_rows[{index}]"
        _require_text(row, "template_key", prefix, problems)
        template_text = _require_text(row, "template_text", prefix, problems)
        placeholders = _require_non_empty_text_sequence(row, "placeholders", prefix, problems)
        for placeholder in placeholders:
            if "{" + placeholder + "}" not in template_text:
                problems.append(f"{prefix}.template_text must include placeholder {{{placeholder}}}")

    for index, row in enumerate(_mapping_sequence(packet.get("stale_source_hold_rows"))):
        prefix = f"stale_source_hold_rows[{index}]"
        _require_non_empty_text_sequence(row, "source_hold_refs", prefix, problems)
        _require_text(row, "hold_reason", prefix, problems)
        _require_text(row, "release_condition", prefix, problems)

    for index, row in enumerate(_mapping_sequence(packet.get("reviewer_disposition_rows"))):
        prefix = f"reviewer_disposition_rows[{index}]"
        _require_non_empty_text_sequence(row, "reviewer_disposition_refs", prefix, problems)
        decision = _require_text(row, "decision", prefix, problems)
        if decision and decision != "pending":
            problems.append(f"{prefix}.decision must be pending")
        _require_text(row, "required_review", prefix, problems)


def _validate_cross_refs(packet: Mapping[str, Any], problems: list[str]) -> None:
    process_id = _text(packet.get("process_id"))
    if not process_id:
        problems.append("process_id is required")
        return
    for key in REQUIRED_ROW_SEQUENCES:
        if key == "offline_validation_command_rows":
            continue
        for index, row in enumerate(_mapping_sequence(packet.get(key))):
            if row.get("process_id") != process_id:
                problems.append(f"{key}[{index}].process_id must match packet process_id")


def _validate_validation_command_rows(value: Any, problems: list[str]) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f"offline_validation_command_rows[{index}]"
        if row.get("command") != VALIDATION_COMMANDS[0]:
            problems.append(f"{prefix}.command must be the exact PP&D daemon self-test argv")
        if row.get("exact") is not True:
            problems.append(f"{prefix}.exact must be true")


def _validate_no_forbidden_values(value: Any, problems: list[str], path: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if str(key) in ACTIVE_MUTATION_FLAGS and child is not False:
                problems.append(f"{child_path} must be false")
            _validate_no_forbidden_values(child, problems, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _validate_no_forbidden_values(child, problems, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in FORBIDDEN_VALUE_TERMS):
            problems.append(f"{path} must not contain live, private, active-promotion, guarantee, artifact, or consequential-action completion values")


def _require_text(row: Mapping[str, Any], field: str, prefix: str, problems: list[str]) -> str:
    value = _text(row.get(field))
    if not value:
        problems.append(f"{prefix}.{field} is required")
    return value


def _require_non_empty_text_sequence(row: Mapping[str, Any], field: str, prefix: str, problems: list[str]) -> list[str]:
    values = _text_sequence(row.get(field))
    if not values:
        problems.append(f"{prefix}.{field} must be a non-empty list of strings")
    return values


def _first_mapping(value: Any) -> Mapping[str, Any]:
    rows = _mapping_sequence(value)
    return rows[0] if rows else {}


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
