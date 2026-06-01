"""Fixture-first guardrail bundle recompile candidate v4.

This module builds an inactive, deterministic guardrail recompile candidate from
process model impact candidate v4 fixtures and guardrail bundle placeholder
fixtures only. It does not mutate active guardrail bundles, open DevHub, plan or
perform autonomous completion, upload, submit, certify, pay, schedule, or make
legal/permitting guarantees.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.guardrail_bundle_recompile_candidate.v4"
PACKET_VERSION = "v4"
MODE = "fixture_first_inactive_guardrail_bundle_recompile_candidate_only"

PROCESS_IMPACT_TYPE = "ppd.process_model_impact_candidate.v4"
PLACEHOLDER_TYPE = "ppd.guardrail_bundle_placeholders.v1"

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/guardrail_bundle_recompile_candidate_v4.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_guardrail_bundle_recompile_candidate_v4"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

REQUIRED_CHANGE_CATEGORIES = (
    "reversible_action_predicates",
    "exact_confirmation_predicates",
    "refused_consequential_action_predicates",
    "stale_evidence_block_predicates",
    "explanation_templates",
    "validation_status",
    "reviewer_holds",
    "rollback_notes",
    "offline_validation_commands",
)

REQUIRED_ATTESTATIONS = {
    "fixture_first": True,
    "process_model_impact_candidate_v4_only": True,
    "guardrail_bundle_placeholders_only": True,
    "inactive_candidate_only": True,
    "deterministic": True,
    "no_active_guardrail_bundle_mutation": True,
    "no_autonomous_completion_plan": True,
    "no_devhub_open": True,
    "no_upload": True,
    "no_submission": True,
    "no_certification": True,
    "no_payment": True,
    "no_scheduling": True,
    "no_legal_or_permitting_guarantee": True,
}

MUTATION_FLAGS = (
    "active_guardrail_mutation",
    "active_guardrail_bundle_mutation",
    "active_prompt_mutation",
    "active_process_model_mutation",
    "guardrails_changed",
    "guardrail_bundles_changed",
    "prompts_changed",
    "process_models_changed",
    "opens_devhub",
    "plans_autonomous_completion",
    "uploads",
    "submits",
    "certifies",
    "pays",
    "schedules",
)

FORBIDDEN_CLAIM_FRAGMENTS = (
    "opened devhub",
    "autonomous completion",
    "certified acknowledgement",
    "paid fee",
    "payment completed",
    "scheduled inspection",
    "submitted permit",
    "uploaded correction",
    "permit will be approved",
    "guarantee approval",
    "legal guarantee",
    "permitting guarantee",
)


@dataclass(frozen=True)
class GuardrailBundleRecompileCandidateV4Result:
    valid: bool
    problems: tuple[str, ...]


class GuardrailBundleRecompileCandidateV4Error(ValueError):
    """Raised when a guardrail bundle recompile candidate v4 is invalid."""


def load_guardrail_bundle_recompile_candidate_v4_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    manifest = _load_json_object(manifest_path)
    process_ref = _text(manifest.get("process_model_impact_candidate_v4_fixture"))
    placeholder_ref = _text(manifest.get("guardrail_bundle_placeholders_fixture"))
    if not process_ref:
        raise ValueError("manifest must include process_model_impact_candidate_v4_fixture")
    if not placeholder_ref:
        raise ValueError("manifest must include guardrail_bundle_placeholders_fixture")
    process_fixture = _load_json_object(manifest_path.parent / process_ref)
    placeholder_fixture = _load_json_object(manifest_path.parent / placeholder_ref)
    return build_guardrail_bundle_recompile_candidate_v4(
        process_model_impact_candidate_v4=process_fixture,
        guardrail_bundle_placeholders=placeholder_fixture,
        source_manifest_id=_text(manifest.get("manifest_id"), "inline-guardrail-bundle-recompile-candidate-v4"),
        process_fixture_ref=process_ref,
        placeholder_fixture_ref=placeholder_ref,
    )


def build_guardrail_bundle_recompile_candidate_v4(
    process_model_impact_candidate_v4: Mapping[str, Any],
    guardrail_bundle_placeholders: Mapping[str, Any],
    source_manifest_id: str = "inline-fixtures",
    process_fixture_ref: str = "process_model_impact_candidate_v4.json",
    placeholder_fixture_ref: str = "guardrail_bundle_placeholders.json",
) -> dict[str, Any]:
    process_errors = _validate_process_impact_fixture(process_model_impact_candidate_v4)
    placeholder_errors = _validate_placeholder_fixture(guardrail_bundle_placeholders)
    if process_errors or placeholder_errors:
        raise GuardrailBundleRecompileCandidateV4Error("; ".join(process_errors + placeholder_errors))

    impact_rows = _mapping_sequence(process_model_impact_candidate_v4.get("impact_rows"))
    placeholders = _mapping_sequence(guardrail_bundle_placeholders.get("placeholders"))
    placeholder_by_process = {_text(row.get("process_id")): row for row in placeholders}
    change_rows = [_change_row(category, impact_rows, placeholder_by_process) for category in REQUIRED_CHANGE_CATEGORIES]

    candidate = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "mode": MODE,
        "source_manifest_id": source_manifest_id,
        "consumes": {
            "process_model_impact_candidate_v4_fixture": process_fixture_ref,
            "guardrail_bundle_placeholders_fixture": placeholder_fixture_ref,
        },
        "inactive_deterministic_predicate_changes": change_rows,
        "candidate_guardrail_bundle_ids": sorted({_text(row.get("guardrail_bundle_id")) for row in placeholders if _text(row.get("guardrail_bundle_id"))}),
        "validation_status": {
            "status": "inactive_candidate_validated_offline_only",
            "validation_commands": OFFLINE_VALIDATION_COMMANDS,
            "active_bundle_mutation": False,
        },
        "reviewer_holds": [
            {
                "hold_id": "hold-review-before-activation",
                "reason": "Human reviewer must approve inactive predicate changes before any future promotion task can consider activation.",
                "release_state": "held",
            }
        ],
        "rollback_notes": [
            {
                "rollback_id": "rollback-discard-inactive-candidate-v4",
                "action": "discard_candidate_fixture_only",
                "verification": "No active guardrail bundle, prompt, DevHub state, source registry, or process model artifact is changed by this candidate.",
            }
        ],
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "attestations": dict(REQUIRED_ATTESTATIONS),
    }
    require_valid_guardrail_bundle_recompile_candidate_v4(candidate)
    return candidate


def validate_guardrail_bundle_recompile_candidate_v4(packet: Mapping[str, Any]) -> GuardrailBundleRecompileCandidateV4Result:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return GuardrailBundleRecompileCandidateV4Result(False, ("packet must be an object",))
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v4")
    if packet.get("mode") != MODE:
        problems.append(f"mode must be {MODE}")

    consumes = _mapping(packet.get("consumes"))
    if set(consumes) != {"process_model_impact_candidate_v4_fixture", "guardrail_bundle_placeholders_fixture"}:
        problems.append("consumes must contain only process_model_impact_candidate_v4_fixture and guardrail_bundle_placeholders_fixture")
    for key, value in consumes.items():
        if not _text(value).endswith(".json"):
            problems.append(f"consumes.{key} must point to a JSON fixture")

    rows = _mapping_sequence(packet.get("inactive_deterministic_predicate_changes"))
    categories = [_text(row.get("category")) for row in rows]
    if tuple(categories) != REQUIRED_CHANGE_CATEGORIES:
        problems.append("inactive_deterministic_predicate_changes must cover required categories in deterministic order")
    for index, row in enumerate(rows):
        prefix = f"inactive_deterministic_predicate_changes[{index}]"
        if row.get("inactive") is not True:
            problems.append(f"{prefix}.inactive must be true")
        if row.get("deterministic") is not True:
            problems.append(f"{prefix}.deterministic must be true")
        if row.get("proposed_change_kind") != "inactive_predicate_change_candidate":
            problems.append(f"{prefix}.proposed_change_kind must be inactive_predicate_change_candidate")
        if not _mapping_sequence(row.get("source_impact_refs")):
            problems.append(f"{prefix}.source_impact_refs must cite process model impact fixture rows")
        if not _text(row.get("placeholder_guardrail_bundle_id")):
            problems.append(f"{prefix}.placeholder_guardrail_bundle_id must be present")
        if not _text(row.get("proposed_inactive_predicate")):
            problems.append(f"{prefix}.proposed_inactive_predicate must be present")

    if packet.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        problems.append("offline_validation_commands must exactly match the offline command bundle")
    validation_status = _mapping(packet.get("validation_status"))
    if validation_status.get("validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        problems.append("validation_status.validation_commands must exactly match offline_validation_commands")
    if validation_status.get("active_bundle_mutation") is not False:
        problems.append("validation_status.active_bundle_mutation must be false")
    if not _mapping_sequence(packet.get("reviewer_holds")):
        problems.append("reviewer_holds must be non-empty")
    if not _mapping_sequence(packet.get("rollback_notes")):
        problems.append("rollback_notes must be non-empty")

    attestations = _mapping(packet.get("attestations"))
    for key, expected in REQUIRED_ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            problems.append(f"attestations.{key} must be true")

    _validate_no_forbidden_state(packet, problems)
    return GuardrailBundleRecompileCandidateV4Result(not problems, tuple(problems))


def require_valid_guardrail_bundle_recompile_candidate_v4(packet: Mapping[str, Any]) -> None:
    result = validate_guardrail_bundle_recompile_candidate_v4(packet)
    if not result.valid:
        raise GuardrailBundleRecompileCandidateV4Error("invalid guardrail bundle recompile candidate v4: " + "; ".join(result.problems))


def _change_row(category: str, impact_rows: Sequence[Mapping[str, Any]], placeholder_by_process: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    matching_impacts = [row for row in impact_rows if category in _text_sequence(row.get("guardrail_categories"))]
    if not matching_impacts:
        matching_impacts = list(impact_rows)
    first = matching_impacts[0]
    process_id = _text(first.get("process_id"))
    placeholder = placeholder_by_process.get(process_id) or next(iter(placeholder_by_process.values()))
    bundle_id = _text(placeholder.get("guardrail_bundle_id"))
    predicate_slot = _predicate_slot_for_category(placeholder, category)
    return {
        "change_id": f"candidate-v4-{category}",
        "category": category,
        "proposed_change_kind": "inactive_predicate_change_candidate",
        "inactive": True,
        "deterministic": True,
        "placeholder_guardrail_bundle_id": bundle_id,
        "placeholder_predicate_slot": predicate_slot,
        "source_impact_refs": [
            {
                "impact_id": _text(row.get("impact_id")),
                "process_id": _text(row.get("process_id")),
                "citation_refs": _text_sequence(row.get("citation_refs")),
            }
            for row in matching_impacts
        ],
        "proposed_inactive_predicate": _predicate_text(category),
        "review_status": "inactive_reviewer_hold",
        "rollback_note_ref": "rollback-discard-inactive-candidate-v4",
    }


def _predicate_slot_for_category(placeholder: Mapping[str, Any], category: str) -> str:
    slots = _mapping_sequence(placeholder.get("predicate_slots"))
    for slot in slots:
        if _text(slot.get("category")) == category:
            return _text(slot.get("slot_id"))
    return f"placeholder-slot-{category}"


def _predicate_text(category: str) -> str:
    mapping = {
        "reversible_action_predicates": "Allow only local draft or read-only preparation when source impact rows show no consequential action boundary.",
        "exact_confirmation_predicates": "Require action-specific exact user confirmation before any consequential boundary can be presented for attended handling.",
        "refused_consequential_action_predicates": "Refuse official action execution and return an attended handoff explanation instead.",
        "stale_evidence_block_predicates": "Block recommendations when cited process evidence is stale, conflicting, or marked for reviewer hold.",
        "explanation_templates": "Use cited fixture references and state that the candidate is inactive and review-only.",
        "validation_status": "Report offline fixture validation status without implying activation or official completion.",
        "reviewer_holds": "Carry reviewer holds forward until a separate reviewed promotion task clears them.",
        "rollback_notes": "Rollback means discarding this inactive candidate fixture only.",
        "offline_validation_commands": "Expose only the exact offline validation command list for this candidate.",
    }
    return mapping[category]


def _validate_process_impact_fixture(packet: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    if packet.get("packet_type") != PROCESS_IMPACT_TYPE:
        problems.append(f"process impact fixture packet_type must be {PROCESS_IMPACT_TYPE}")
    if packet.get("packet_version") != "v4":
        problems.append("process impact fixture packet_version must be v4")
    if packet.get("fixture_first") is not True:
        problems.append("process impact fixture fixture_first must be true")
    rows = _mapping_sequence(packet.get("impact_rows"))
    if not rows:
        problems.append("process impact fixture impact_rows must be non-empty")
    for index, row in enumerate(rows):
        for key in ("impact_id", "process_id", "guardrail_categories", "citation_refs"):
            if key not in row:
                problems.append(f"process impact fixture impact_rows[{index}].{key} is required")
    return problems


def _validate_placeholder_fixture(packet: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    if packet.get("packet_type") != PLACEHOLDER_TYPE:
        problems.append(f"placeholder fixture packet_type must be {PLACEHOLDER_TYPE}")
    placeholders = _mapping_sequence(packet.get("placeholders"))
    if not placeholders:
        problems.append("placeholder fixture placeholders must be non-empty")
    for index, row in enumerate(placeholders):
        if row.get("active") is not False:
            problems.append(f"placeholder fixture placeholders[{index}].active must be false")
        for key in ("guardrail_bundle_id", "process_id", "predicate_slots"):
            if key not in row:
                problems.append(f"placeholder fixture placeholders[{index}].{key} is required")
    return problems


def _validate_no_forbidden_state(value: Any, problems: list[str], path: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_").replace(" ", "_")
            child_path = f"{path}.{key_text}"
            if normalized in MUTATION_FLAGS and child is not False:
                problems.append(f"{child_path} must be false or absent")
            _validate_no_forbidden_state(child, problems, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _validate_no_forbidden_state(child, problems, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        for fragment in FORBIDDEN_CLAIM_FRAGMENTS:
            if fragment in lowered:
                problems.append(f"{path} must not contain forbidden live, official-action, or guarantee claim: {fragment}")


def _load_json_object(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return loaded


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _text_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in (_text(item) for item in value) if item]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default
