"""Fixture-first PP&D process model impact candidate v4.

The builder consumes committed requirement re-extraction delta queue v4 fixtures
and prior process model placeholders. It emits inactive reviewer candidates only;
it never mutates active process models, opens DevHub, stores sessions, completes
official actions, or makes legal/permitting guarantees.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

PACKET_VERSION = "process_model_impact_candidate_v4"
SOURCE_MODE = "fixture_only_requirement_reextraction_delta_queue_v4"
REQUIREMENT_QUEUE_PREFIX = "public-refresh-requirement-reextraction-delta-queue-v4"

IMPACT_AREAS = {
    "eligibility_rules",
    "required_facts",
    "required_documents",
    "file_rules",
    "fees",
    "deadlines",
    "unsupported_paths",
    "devhub_surface_refs",
}

REQUIRED_IMPACT_LABELS = {
    "eligibility_rules": "eligibility-impact",
    "required_facts": "required-fact-impact",
    "required_documents": "document-impact",
    "file_rules": "file-rule-impact",
    "fees": "fee-impact",
    "deadlines": "deadline-impact",
    "unsupported_paths": "unsupported-path-impact",
    "devhub_surface_refs": "devhub-surface-ref-impact",
}

REQUIRED_FIXTURE_KEYS = {
    "requirement_reextraction_delta_queue_v4",
    "process_model_placeholders",
}

REQUIRED_DELTA_KEYS = {
    "delta_id",
    "requirement_id",
    "requirement_queue_ref",
    "operation",
    "process_model_id",
    "prior_process_model_placeholder_ref",
    "impact_area",
    "impact_label",
    "candidate_text",
    "source_evidence_ids",
    "rationale",
}

ALLOWED_OPERATIONS = {"add", "change", "remove", "hold"}
ALLOWED_REVIEWER_HOLDS = {
    "needs_source_review",
    "needs_process_owner_review",
    "needs_surface_review",
    "needs_rollback_review",
}

DEFAULT_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/process_model_impact_candidate_v4.py"],
    ["python3", "-m", "py_compile", "ppd/tests/test_process_model_impact_candidate_v4.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_process_model_impact_candidate_v4"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

FORBIDDEN_MUTATION_TARGETS = {
    "active_process_models",
    "active_guardrails",
    "active_requirements",
    "active_devhub_surfaces",
    "release_state",
}

PRIVATE_OR_LIVE_KEY_TOKENS = (
    "auth",
    "browser",
    "cookie",
    "credential",
    "download",
    "har",
    "password",
    "payment",
    "private",
    "session",
    "screenshot",
    "storage_state",
    "trace",
)

FORBIDDEN_VALUE_TOKENS = (
    "approval guaranteed",
    "certified submission",
    "completed official action",
    "downloaded document",
    "final payment",
    "guaranteed approval",
    "legal advice",
    "opened devhub",
    "permit will be approved",
    "permit will issue",
    "raw crawl output",
    "scheduled inspection",
    "submitted form",
)

ACTIVE_MUTATION_FLAG_TOKENS = (
    "active_process_models_mutated",
    "active_requirements_mutated",
    "active_guardrails_mutated",
    "active_devhub_surfaces_mutated",
    "active_mutation",
    "mutates_active",
    "promote_to_active",
)


def load_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    return payload


def build_process_model_impact_candidate_v4(
    fixture: Mapping[str, Any],
    *,
    packet_id: str = "process-model-impact-candidate-v4-fixture",
    generated_at: str = "2026-06-01T00:00:00Z",
) -> dict[str, Any]:
    _validate_fixture_shape(fixture)
    placeholders = _placeholder_map(fixture["process_model_placeholders"])
    delta_rows = fixture["requirement_reextraction_delta_queue_v4"]

    inactive_changes: list[dict[str, Any]] = []
    reviewer_holds: list[dict[str, Any]] = []
    rollback_notes: list[dict[str, Any]] = []

    for index, row_value in enumerate(delta_rows):
        row = _normalized_delta_row(index, row_value)
        placeholder = placeholders.get(row["process_model_id"])
        if placeholder is None:
            raise ValueError(f"delta {row['delta_id']} references unknown process_model_id")
        if row["prior_process_model_placeholder_ref"] != row["process_model_id"]:
            raise ValueError(f"delta {row['delta_id']} missing prior process model placeholder reference")

        inactive_change = _inactive_change(row, placeholder)
        inactive_changes.append(inactive_change)
        reviewer_holds.append(_reviewer_hold(row, inactive_change["change_id"]))
        rollback_notes.append(_rollback_note(row, inactive_change["change_id"]))

    packet = {
        "packet_version": PACKET_VERSION,
        "packet_id": packet_id,
        "generated_at": generated_at,
        "source_mode": SOURCE_MODE,
        "status": "inactive_candidate",
        "fixture_first": True,
        "input_fixture_refs": {
            "requirement_reextraction_delta_queue_v4": fixture.get("fixture_id", "inline_fixture"),
            "requirement_queue_refs": sorted({row["requirement_queue_ref"] for row in delta_rows}),
            "process_model_placeholders": sorted(placeholders),
        },
        "side_effects": {
            "active_process_models_mutated": False,
            "active_requirements_mutated": False,
            "active_guardrails_mutated": False,
            "active_devhub_surfaces_mutated": False,
            "devhub_opened": False,
            "documents_downloaded": False,
            "forms_submitted": False,
            "fees_paid": False,
            "inspections_scheduled": False,
            "official_actions_completed": False,
        },
        "forbidden_mutation_targets": sorted(FORBIDDEN_MUTATION_TARGETS),
        "inactive_changes": inactive_changes,
        "reviewer_holds": reviewer_holds,
        "rollback_notes": rollback_notes,
        "exact_offline_validation_commands": deepcopy(DEFAULT_VALIDATION_COMMANDS),
        "limitations": [
            "candidate packet only",
            "requires human review before any separate activation proposal",
            "does not determine permit eligibility or approval outcome",
            "does not complete official PP&D or DevHub actions",
        ],
    }
    validate_candidate_packet(packet)
    return packet


def validate_candidate_packet(packet: Mapping[str, Any]) -> None:
    _require(packet.get("packet_version") == PACKET_VERSION, "unexpected packet_version")
    _require(packet.get("status") == "inactive_candidate", "status must be inactive_candidate")
    _require(packet.get("fixture_first") is True, "packet must be fixture_first")
    _require(packet.get("source_mode") == SOURCE_MODE, "packet must use the v4 fixture source mode")

    refs = packet.get("input_fixture_refs")
    _require(isinstance(refs, Mapping), "input_fixture_refs must be an object")
    queue_refs = refs.get("requirement_queue_refs")
    _require(isinstance(queue_refs, list) and queue_refs, "missing requirement queue references")
    _require(all(isinstance(ref, str) and ref.startswith(REQUIREMENT_QUEUE_PREFIX) for ref in queue_refs), "invalid requirement queue reference")
    placeholder_refs = refs.get("process_model_placeholders")
    _require(isinstance(placeholder_refs, list) and placeholder_refs, "missing prior process model placeholders")

    side_effects = packet.get("side_effects")
    _require(isinstance(side_effects, Mapping), "side_effects must be an object")
    for key, value in side_effects.items():
        _require(value is False, f"side_effects.{key} must be false")

    forbidden_targets = set(packet.get("forbidden_mutation_targets", []))
    _require(FORBIDDEN_MUTATION_TARGETS.issubset(forbidden_targets), "missing forbidden mutation target")

    changes = packet.get("inactive_changes")
    _require(isinstance(changes, list) and changes, "missing inactive change rows")
    seen_change_ids: set[str] = set()
    seen_areas: set[str] = set()
    for index, value in enumerate(changes):
        _validate_inactive_change(index, value, seen_change_ids, seen_areas)

    missing_areas = IMPACT_AREAS.difference(seen_areas)
    _require(not missing_areas, f"missing impact labels: {sorted(missing_areas)}")
    _validate_reviewer_holds(packet.get("reviewer_holds"), seen_change_ids)
    _validate_rollback_notes(packet.get("rollback_notes"), seen_change_ids)
    _validate_commands(packet.get("exact_offline_validation_commands"))
    _validate_no_forbidden_payload(packet)


def _validate_fixture_shape(fixture: Mapping[str, Any]) -> None:
    missing = REQUIRED_FIXTURE_KEYS.difference(fixture)
    _require(not missing, f"fixture missing keys: {sorted(missing)}")
    deltas = fixture["requirement_reextraction_delta_queue_v4"]
    placeholders = fixture["process_model_placeholders"]
    _require(isinstance(deltas, list) and deltas, "requirement_reextraction_delta_queue_v4 must be non-empty")
    _require(isinstance(placeholders, list) and placeholders, "process_model_placeholders must be non-empty")


def _placeholder_map(placeholders: Sequence[Any]) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(placeholders):
        _require(isinstance(value, Mapping), f"process_model_placeholders[{index}] must be an object")
        process_model_id = value.get("process_model_id")
        _require(isinstance(process_model_id, str) and process_model_id, f"placeholder {index} missing process_model_id")
        _require(process_model_id not in mapped, f"duplicate process_model_id: {process_model_id}")
        _require(value.get("placeholder_only") is True, f"placeholder {process_model_id} must be placeholder_only")
        _require(value.get("active_model_ref") in {None, ""}, f"placeholder {process_model_id} must not reference an active model")
        mapped[process_model_id] = dict(value)
    return mapped


def _normalized_delta_row(index: int, row_value: Any) -> dict[str, Any]:
    _require(isinstance(row_value, Mapping), f"delta row {index} must be an object")
    row = dict(row_value)
    missing = REQUIRED_DELTA_KEYS.difference(row)
    _require(not missing, f"delta row {index} missing keys: {sorted(missing)}")

    delta_id = row["delta_id"]
    operation = row["operation"]
    impact_area = row["impact_area"]
    evidence_ids = row["source_evidence_ids"]
    queue_ref = row["requirement_queue_ref"]

    _require(isinstance(delta_id, str) and delta_id.startswith("req-redelta-v4-"), f"invalid delta_id at row {index}")
    _require(isinstance(queue_ref, str) and queue_ref.startswith(REQUIREMENT_QUEUE_PREFIX), f"delta {delta_id} missing requirement queue reference")
    _require(operation in ALLOWED_OPERATIONS, f"delta {delta_id} has unsupported operation")
    _require(impact_area in IMPACT_AREAS, f"delta {delta_id} has unsupported impact_area")
    _require(row.get("impact_label") == REQUIRED_IMPACT_LABELS[impact_area], f"delta {delta_id} missing {impact_area} impact label")
    _require(isinstance(row["process_model_id"], str) and row["process_model_id"], f"delta {delta_id} missing process_model_id")
    _require(isinstance(row["prior_process_model_placeholder_ref"], str) and row["prior_process_model_placeholder_ref"], f"delta {delta_id} missing prior process model placeholder reference")
    _require(isinstance(row["requirement_id"], str) and row["requirement_id"], f"delta {delta_id} missing requirement_id")
    _require(isinstance(row["candidate_text"], str) and row["candidate_text"].strip(), f"delta {delta_id} missing candidate_text")
    _require(isinstance(row["rationale"], str) and row["rationale"].strip(), f"delta {delta_id} missing rationale")
    _require(isinstance(evidence_ids, list) and evidence_ids, f"delta {delta_id} missing source_evidence_ids")
    _require(all(isinstance(item, str) and item for item in evidence_ids), f"delta {delta_id} evidence ids must be strings")
    if impact_area == "unsupported_paths":
        _require("unsupported" in row["candidate_text"].lower(), f"delta {delta_id} missing unsupported-path handling")
    if impact_area == "devhub_surface_refs":
        _require(isinstance(row.get("devhub_surface_ref"), str) and row.get("devhub_surface_ref"), f"delta {delta_id} missing DevHub surface reference handling")
    return row


def _inactive_change(row: Mapping[str, Any], placeholder: Mapping[str, Any]) -> dict[str, Any]:
    change_id = f"inactive-pm-impact-v4-{row['delta_id'].removeprefix('req-redelta-v4-')}"
    change = {
        "change_id": change_id,
        "status": "inactive_candidate",
        "requirement_queue_ref": row["requirement_queue_ref"],
        "prior_process_model_placeholder_ref": row["prior_process_model_placeholder_ref"],
        "process_model_id": row["process_model_id"],
        "permit_type": placeholder.get("permit_type", "placeholder_permit_type"),
        "impact_area": row["impact_area"],
        "impact_label": row["impact_label"],
        "operation": row["operation"],
        "candidate_text": row["candidate_text"],
        "requirement_id": row["requirement_id"],
        "source_evidence_ids": list(row["source_evidence_ids"]),
        "rationale": row["rationale"],
        "activation_policy": "do_not_apply_without_human_review_and_separate_activation",
        "active_process_model_mutation": False,
    }
    if row["impact_area"] == "unsupported_paths":
        change["unsupported_path_handling"] = "block_or_route_to_human_review_until_placeholder_is_promoted"
    if row["impact_area"] == "devhub_surface_refs":
        change["devhub_surface_ref"] = row["devhub_surface_ref"]
        change["devhub_surface_ref_handling"] = "reference_only_no_authenticated_observation_claim"
    return change


def _reviewer_hold(row: Mapping[str, Any], change_id: str) -> dict[str, Any]:
    hold_reason = row.get("reviewer_hold", "needs_process_owner_review")
    _require(hold_reason in ALLOWED_REVIEWER_HOLDS, f"delta {row['delta_id']} has unsupported reviewer_hold")
    return {
        "change_id": change_id,
        "status": "held_for_review",
        "hold_reason": hold_reason,
        "reviewer": "unassigned",
        "notes": "Review source evidence, placeholder fit, inactive status, and rollback note before any separate activation proposal.",
    }


def _rollback_note(row: Mapping[str, Any], change_id: str) -> dict[str, Any]:
    return {
        "change_id": change_id,
        "rollback_scope": "inactive_candidate_only",
        "rollback_note": row.get(
            "rollback_note",
            "Discard this inactive candidate row; no active process model state is changed by this packet.",
        ),
    }


def _validate_inactive_change(index: int, value: Any, seen_change_ids: set[str], seen_areas: set[str]) -> None:
    _require(isinstance(value, Mapping), f"inactive_changes[{index}] must be an object")
    change_id = value.get("change_id")
    _require(isinstance(change_id, str) and change_id.startswith("inactive-pm-impact-v4-"), f"invalid change_id at row {index}")
    _require(change_id not in seen_change_ids, f"duplicate change_id: {change_id}")
    seen_change_ids.add(change_id)
    _require(value.get("status") == "inactive_candidate", f"{change_id} must be inactive_candidate")
    _require(value.get("activation_policy") == "do_not_apply_without_human_review_and_separate_activation", f"{change_id} has unsafe activation_policy")
    _require(value.get("active_process_model_mutation") is False, f"{change_id} must not claim active process-model mutation")
    _require(isinstance(value.get("requirement_queue_ref"), str) and value.get("requirement_queue_ref", "").startswith(REQUIREMENT_QUEUE_PREFIX), f"{change_id} missing requirement queue reference")
    _require(isinstance(value.get("prior_process_model_placeholder_ref"), str) and value.get("prior_process_model_placeholder_ref"), f"{change_id} missing prior process model placeholder reference")
    impact_area = value.get("impact_area")
    _require(impact_area in IMPACT_AREAS, f"{change_id} has unsupported impact_area")
    _require(value.get("impact_label") == REQUIRED_IMPACT_LABELS[impact_area], f"{change_id} missing {impact_area} impact label")
    seen_areas.add(str(impact_area))
    _require(value.get("operation") in ALLOWED_OPERATIONS, f"{change_id} has unsupported operation")
    _require(isinstance(value.get("source_evidence_ids"), list) and value.get("source_evidence_ids"), f"{change_id} missing source evidence")
    if impact_area == "unsupported_paths":
        _require(value.get("unsupported_path_handling") == "block_or_route_to_human_review_until_placeholder_is_promoted", f"{change_id} missing unsupported-path handling")
    if impact_area == "devhub_surface_refs":
        _require(isinstance(value.get("devhub_surface_ref"), str) and value.get("devhub_surface_ref"), f"{change_id} missing DevHub surface reference handling")
        _require(value.get("devhub_surface_ref_handling") == "reference_only_no_authenticated_observation_claim", f"{change_id} has unsafe DevHub surface reference handling")


def _validate_reviewer_holds(value: Any, change_ids: set[str]) -> None:
    _require(isinstance(value, list) and value, "reviewer_holds must be non-empty")
    hold_change_ids = set()
    for index, hold in enumerate(value):
        _require(isinstance(hold, Mapping), f"reviewer_holds[{index}] must be an object")
        change_id = hold.get("change_id")
        _require(change_id in change_ids, f"reviewer hold references unknown change_id: {change_id}")
        _require(hold.get("status") == "held_for_review", f"reviewer hold {change_id} must be held_for_review")
        _require(hold.get("hold_reason") in ALLOWED_REVIEWER_HOLDS, f"reviewer hold {change_id} has unsupported hold_reason")
        _require(hold.get("reviewer") == "unassigned", f"reviewer hold {change_id} must remain unassigned")
        hold_change_ids.add(str(change_id))
    _require(hold_change_ids == change_ids, "each inactive change must have a reviewer hold")


def _validate_rollback_notes(value: Any, change_ids: set[str]) -> None:
    _require(isinstance(value, list) and value, "rollback_notes must be non-empty")
    rollback_change_ids = set()
    for index, note in enumerate(value):
        _require(isinstance(note, Mapping), f"rollback_notes[{index}] must be an object")
        change_id = note.get("change_id")
        _require(change_id in change_ids, f"rollback note references unknown change_id: {change_id}")
        _require(note.get("rollback_scope") == "inactive_candidate_only", f"rollback note {change_id} has unsafe scope")
        _require(isinstance(note.get("rollback_note"), str) and note.get("rollback_note"), f"rollback note {change_id} missing text")
        rollback_change_ids.add(str(change_id))
    _require(rollback_change_ids == change_ids, "each inactive change must have a rollback note")


def _validate_commands(commands: Any) -> None:
    _require(isinstance(commands, list) and commands, "exact_offline_validation_commands must be non-empty")
    required = {tuple(command) for command in DEFAULT_VALIDATION_COMMANDS}
    actual = set()
    for command in commands:
        _require(isinstance(command, list) and command, "each validation command must be an argv list")
        _require(all(isinstance(part, str) and part for part in command), "validation command parts must be non-empty strings")
        actual.add(tuple(command))
    _require(required.issubset(actual), "missing validation commands")


def _validate_no_forbidden_payload(value: Any) -> None:
    for path, key, child in _walk(value):
        normalized_key = key.lower().replace("-", "_")
        if any(token in normalized_key for token in PRIVATE_OR_LIVE_KEY_TOKENS):
            _require(child is False or child in {None, ""}, f"{path} must not include private, live, financial, or browser artifacts")
        if any(token in normalized_key for token in ACTIVE_MUTATION_FLAG_TOKENS):
            _require(child is False or child in {None, ""}, f"{path} must not include active mutation flags")
        if isinstance(child, str):
            text = child.lower()
            _require(not any(token in text for token in FORBIDDEN_VALUE_TOKENS), f"{path} contains forbidden live-action or guarantee text")


def _walk(value: Any, prefix: str = "packet", key: str = "packet") -> list[tuple[str, str, Any]]:
    rows: list[tuple[str, str, Any]] = []
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{prefix}.{child_key_text}"
            rows.append((child_path, child_key_text, child_value))
            rows.extend(_walk(child_value, child_path, child_key_text))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{prefix}[{index}]"
            rows.append((child_path, key, child_value))
            rows.extend(_walk(child_value, child_path, key))
    return rows


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and validate a fixture-first process model impact candidate v4 packet")
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    packet = build_process_model_impact_candidate_v4(load_fixture(args.fixture))
    if args.output:
        args.output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
