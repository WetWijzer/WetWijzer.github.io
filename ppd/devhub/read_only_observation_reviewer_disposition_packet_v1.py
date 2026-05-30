"""DevHub read-only observation reviewer disposition packet v1.

This packet is fixture-first and offline-only. It consumes the DevHub
read-only observation dry-run manifest v1 and prepares reviewer disposition
rows without opening DevHub, creating browser/session artifacts, storing private
values, or authorizing official actions.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.devhub.devhub_observation_dry_run import MANIFEST_SCHEMA_VERSION, validate_manifest

PACKET_SCHEMA_VERSION = "devhub_read_only_observation_reviewer_disposition_packet_v1"

OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/devhub/read_only_observation_reviewer_disposition_packet_v1.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_read_only_observation_reviewer_disposition_packet_v1.py"],
]

_REQUIRED_SECTIONS = (
    "ordered_reviewer_observations",
    "redaction_confirmation_placeholders",
    "read_only_surface_map_delta_placeholders",
    "blocked_consequential_action_confirmations",
    "manual_follow_up_notes",
    "offline_validation_commands",
)

_REQUIRED_APPROVED_REASON_CODES = frozenset(
    {
        "APPROVED_OFFLINE_FIXTURE_ONLY",
        "APPROVED_READ_ONLY_ACTION_REFS_ONLY",
        "APPROVED_NO_PRIVATE_VALUES_STORED",
    }
)
_REQUIRED_HOLD_REASON_CODES = frozenset({"HOLD_PENDING_HUMAN_REDACTION_CONFIRMATION"})
_REQUIRED_BLOCKED_ACTION_CATEGORIES = frozenset(
    {"certification", "payment", "purchase", "schedule", "submit", "upload", "withdraw"}
)

_ARTIFACT_KEYS = re.compile(
    r"(^|_)(auth|browser|cookie|credential|download|har|password|private|private_value|raw|screenshot|session|storage_state|token|trace|upload_payload)($|_)",
    re.IGNORECASE,
)
_PRIVATE_OR_ARTIFACT_TEXT = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|storage[_-]?state\.json|trace\.zip|\.har\b|\.png\b|\.webm\b|bearer\s+[A-Z0-9._-]+|password\s*[:=]|cookie\s*[:=]|session\s*[:=]|token\s*[:=]|private page value|private authenticated value",
    re.IGNORECASE,
)
_LIVE_OR_OFFICIAL_TEXT = re.compile(
    r"opened live devhub|ran live devhub|live devhub access|live authenticated|accessed authenticated devhub|observed in production|clicked submit|payment completed|scheduled inspection|uploaded correction|certified acknowledgement",
    re.IGNORECASE,
)
_CONSEQUENTIAL_ACTION_TEXT = re.compile(
    r"\b(cancel(?:lation|led)?|certif(?:y|ied|ication)|pay(?:ment)?|schedule(?:d|ing)?|submit(?:ted|sion)?|upload(?:ed|ing)?)\b",
    re.IGNORECASE,
)
_MUTATION_KEYS = frozenset(
    {
        "active_devhub_mutation",
        "active_fixture_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_surface_map_change",
        "active_surface_mutation",
        "mutates_devhub",
        "mutates_fixtures",
        "mutates_guardrails",
        "mutates_prompt",
        "mutates_release_state",
        "mutates_surface_map",
    }
)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data


def build_disposition_packet_v1(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic reviewer disposition packet from a dry-run manifest."""
    validate_manifest(manifest)

    steps = sorted(
        _sequence(manifest.get("synthetic_observation_steps")),
        key=lambda item: int(_mapping(item).get("synthetic_sequence", 0)),
    )
    stop_ids = [
        str(item.get("checkpoint_id"))
        for item in _sequence(manifest.get("manual_stop_checkpoints"))
        if isinstance(item, Mapping)
    ]

    ordered_observations: list[dict[str, Any]] = []
    surface_deltas: list[dict[str, Any]] = []
    follow_ups: list[dict[str, Any]] = []

    for index, raw_step in enumerate(steps, start=1):
        step = _mapping(raw_step)
        step_id = str(step.get("step_id", ""))
        surface_id = str(step.get("surface_id", ""))
        action_refs = [str(ref) for ref in _sequence(step.get("read_only_action_classification_refs"))]
        capture_fields = [_mapping(field) for field in _sequence(step.get("expected_accessible_role_capture_fields"))]
        observation_id = f"reviewer-observation-{index:02d}"

        ordered_observations.append(
            {
                "observation_id": observation_id,
                "observation_order": index,
                "source_manifest_step_id": step_id,
                "surface_id": surface_id,
                "surface_label": step.get("surface_label"),
                "reviewer_disposition": "approve_read_only_with_placeholders",
                "approved_reason_codes": sorted(_REQUIRED_APPROVED_REASON_CODES),
                "hold_reason_codes": sorted(_REQUIRED_HOLD_REASON_CODES),
                "read_only_action_classification_refs": action_refs,
                "redaction_placeholder_refs": [f"redaction-{field.get('field_key')}" for field in capture_fields],
                "surface_map_delta_placeholder_ref": f"surface-delta-{step_id}",
                "blocked_confirmation_ref": "blocked-consequential-actions-v1",
                "manual_follow_up_note_ref": f"manual-follow-up-{step_id}",
            }
        )
        surface_deltas.append(
            {
                "delta_id": f"surface-delta-{step_id}",
                "source_manifest_step_id": step_id,
                "surface_id": surface_id,
                "delta_status": "placeholder_only_no_active_surface_map_change",
                "registry_mutation_allowed": False,
                "proposed_delta": None,
                "field_delta_placeholders": [
                    {
                        "field_key": field.get("field_key"),
                        "expected_accessible_role": field.get("expected_accessible_role"),
                        "expected_accessible_name": field.get("expected_accessible_name"),
                        "observed_selector": None,
                        "observed_state": None,
                    }
                    for field in capture_fields
                ],
            }
        )
        follow_ups.append(
            {
                "note_id": f"manual-follow-up-{step_id}",
                "source_manifest_step_id": step_id,
                "surface_id": surface_id,
                "note_status": "placeholder_only_pending_reviewer",
                "reviewer_notes": None,
                "required_manual_checks": [
                    "confirm redaction placeholders remain value-free",
                    "confirm action refs remain read-only",
                    "confirm no surface-map mutation is requested",
                ],
            }
        )

    packet = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "packet_id": str(manifest.get("manifest_id", "devhub_read_only_observation_dry_run_manifest_v1")).replace(
            "dry_run_manifest", "reviewer_disposition_packet"
        ),
        "source_manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "source_manifest_id": manifest.get("manifest_id"),
        "mode": "offline_fixture_only",
        "devhub_opened": False,
        "browser_or_session_artifacts_created": False,
        "private_values_stored": False,
        "official_actions_allowed": False,
        "surface_map_mutation_allowed": False,
        "ordered_reviewer_observations": ordered_observations,
        "redaction_confirmation_placeholders": _redaction_placeholders(manifest),
        "read_only_surface_map_delta_placeholders": surface_deltas,
        "blocked_consequential_action_confirmations": [
            {
                "confirmation_id": "blocked-consequential-actions-v1",
                "confirmation_status": "blocked_by_policy",
                "blocked_action_categories": sorted(_REQUIRED_BLOCKED_ACTION_CATEGORIES),
                "manual_stop_checkpoint_refs": stop_ids,
                "official_action_allowed": False,
            }
        ],
        "manual_follow_up_notes": follow_ups,
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
    }
    validate_disposition_packet_v1(packet)
    return packet


def validate_disposition_packet_v1(packet: Mapping[str, Any]) -> None:
    """Reject incomplete or unsafe reviewer disposition packets."""
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        raise ValueError("packet must be a JSON object")
    if packet.get("schema_version") != PACKET_SCHEMA_VERSION:
        errors.append(f"schema_version must be {PACKET_SCHEMA_VERSION}")
    if packet.get("source_manifest_schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(f"source_manifest_schema_version must be {MANIFEST_SCHEMA_VERSION}")
    for key in (
        "devhub_opened",
        "browser_or_session_artifacts_created",
        "private_values_stored",
        "official_actions_allowed",
        "surface_map_mutation_allowed",
    ):
        if packet.get(key) is not False:
            errors.append(f"{key} must be false")
    for key in _REQUIRED_SECTIONS:
        if not _sequence(packet.get(key)):
            errors.append(f"{key} must be a non-empty list")
    if packet.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        errors.append("offline_validation_commands must match exact offline commands")

    observation_ids = _validate_observations(packet.get("ordered_reviewer_observations"), errors)
    redaction_ids = {str(item.get("placeholder_id")) for item in _sequence(packet.get("redaction_confirmation_placeholders")) if isinstance(item, Mapping)}
    delta_ids = {str(item.get("delta_id")) for item in _sequence(packet.get("read_only_surface_map_delta_placeholders")) if isinstance(item, Mapping)}
    blocked_ids = {str(item.get("confirmation_id")) for item in _sequence(packet.get("blocked_consequential_action_confirmations")) if isinstance(item, Mapping)}
    follow_up_ids = {str(item.get("note_id")) for item in _sequence(packet.get("manual_follow_up_notes")) if isinstance(item, Mapping)}

    for index, observation in enumerate(_sequence(packet.get("ordered_reviewer_observations"))):
        item = _mapping(observation)
        prefix = f"ordered_reviewer_observations[{index}]"
        redaction_refs = _string_set(item.get("redaction_placeholder_refs"))
        if not redaction_refs:
            errors.append(f"{prefix}.redaction_placeholder_refs must be non-empty")
        elif not redaction_refs.issubset(redaction_ids):
            errors.append(f"{prefix}.redaction_placeholder_refs must reference declared redaction placeholders")
        if item.get("surface_map_delta_placeholder_ref") not in delta_ids:
            errors.append(f"{prefix}.surface_map_delta_placeholder_ref must reference a declared delta placeholder")
        if item.get("blocked_confirmation_ref") not in blocked_ids:
            errors.append(f"{prefix}.blocked_confirmation_ref must reference a declared blocked-action confirmation")
        if item.get("manual_follow_up_note_ref") not in follow_up_ids:
            errors.append(f"{prefix}.manual_follow_up_note_ref must reference a declared follow-up note")

    _validate_redactions(packet.get("redaction_confirmation_placeholders"), errors)
    _validate_surface_deltas(packet.get("read_only_surface_map_delta_placeholders"), errors)
    _validate_blocked_confirmations(packet.get("blocked_consequential_action_confirmations"), errors)
    _validate_follow_ups(packet.get("manual_follow_up_notes"), observation_ids, errors)
    _scan_forbidden(packet, "$", errors)

    if errors:
        raise ValueError("invalid DevHub read-only observation reviewer disposition packet v1: " + "; ".join(errors))


def packet_to_json(packet: Mapping[str, Any]) -> str:
    validate_disposition_packet_v1(packet)
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def _redaction_placeholders(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    placeholders = []
    for item in _sequence(manifest.get("redacted_field_inventory_placeholders")):
        field = _mapping(item)
        field_key = str(field.get("field_key", ""))
        placeholders.append(
            {
                "placeholder_id": f"redaction-{field_key}",
                "field_key": field_key,
                "redaction_reason": field.get("redaction_reason"),
                "confirmation_status": "pending_human_confirmation",
                "stored_value": None,
                "reviewer_confirmation": None,
            }
        )
    return placeholders


def _validate_observations(value: Any, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    for expected_order, raw_item in enumerate(_sequence(value), start=1):
        item = _mapping(raw_item)
        prefix = f"ordered_reviewer_observations[{expected_order - 1}]"
        observation_id = str(item.get("observation_id", ""))
        if not observation_id:
            errors.append(f"{prefix}.observation_id is required")
        elif observation_id in ids:
            errors.append(f"{prefix}.observation_id must be unique")
        else:
            ids.add(observation_id)
        if item.get("observation_order") != expected_order:
            errors.append(f"{prefix}.observation_order must be sequential")
        if item.get("reviewer_disposition") != "approve_read_only_with_placeholders":
            errors.append(f"{prefix}.reviewer_disposition must approve read-only review with placeholders")
        if not _REQUIRED_APPROVED_REASON_CODES.issubset(_string_set(item.get("approved_reason_codes"))):
            errors.append(f"{prefix}.approved_reason_codes must include required offline read-only approval reason codes")
        if not _REQUIRED_HOLD_REASON_CODES.issubset(_string_set(item.get("hold_reason_codes"))):
            errors.append(f"{prefix}.hold_reason_codes must include required hold reason codes")
        refs = _sequence(item.get("read_only_action_classification_refs"))
        if not refs or any(not isinstance(ref, str) or not ref.startswith("read_only:") for ref in refs):
            errors.append(f"{prefix}.read_only_action_classification_refs must contain only read_only refs")
    return ids


def _validate_redactions(value: Any, errors: list[str]) -> None:
    for index, raw_item in enumerate(_sequence(value)):
        item = _mapping(raw_item)
        prefix = f"redaction_confirmation_placeholders[{index}]"
        if not item.get("placeholder_id") or not item.get("field_key"):
            errors.append(f"{prefix} must include placeholder_id and field_key")
        if item.get("placeholder_id") != f"redaction-{item.get('field_key')}":
            errors.append(f"{prefix}.placeholder_id must match field_key")
        if item.get("confirmation_status") != "pending_human_confirmation":
            errors.append(f"{prefix}.confirmation_status must remain pending_human_confirmation")
        if item.get("stored_value") is not None or item.get("reviewer_confirmation") is not None:
            errors.append(f"{prefix} must not store values or completed confirmations")


def _validate_surface_deltas(value: Any, errors: list[str]) -> None:
    for index, raw_item in enumerate(_sequence(value)):
        item = _mapping(raw_item)
        prefix = f"read_only_surface_map_delta_placeholders[{index}]"
        if item.get("delta_status") != "placeholder_only_no_active_surface_map_change":
            errors.append(f"{prefix}.delta_status must be placeholder-only")
        if item.get("registry_mutation_allowed") is not False:
            errors.append(f"{prefix}.registry_mutation_allowed must be false")
        if item.get("proposed_delta") is not None:
            errors.append(f"{prefix}.proposed_delta must remain null")
        if not _sequence(item.get("field_delta_placeholders")):
            errors.append(f"{prefix}.field_delta_placeholders must be non-empty")


def _validate_blocked_confirmations(value: Any, errors: list[str]) -> None:
    for index, raw_item in enumerate(_sequence(value)):
        item = _mapping(raw_item)
        prefix = f"blocked_consequential_action_confirmations[{index}]"
        if item.get("confirmation_status") != "blocked_by_policy":
            errors.append(f"{prefix}.confirmation_status must be blocked_by_policy")
        if item.get("official_action_allowed") is not False:
            errors.append(f"{prefix}.official_action_allowed must be false")
        if not _sequence(item.get("manual_stop_checkpoint_refs")):
            errors.append(f"{prefix}.manual_stop_checkpoint_refs must be non-empty")
        if not _REQUIRED_BLOCKED_ACTION_CATEGORIES.issubset(_string_set(item.get("blocked_action_categories"))):
            errors.append(f"{prefix}.blocked_action_categories must include all consequential categories")


def _validate_follow_ups(value: Any, observation_ids: set[str], errors: list[str]) -> None:
    del observation_ids
    for index, raw_item in enumerate(_sequence(value)):
        item = _mapping(raw_item)
        prefix = f"manual_follow_up_notes[{index}]"
        if item.get("note_status") != "placeholder_only_pending_reviewer":
            errors.append(f"{prefix}.note_status must remain placeholder_only_pending_reviewer")
        if item.get("reviewer_notes") is not None:
            errors.append(f"{prefix}.reviewer_notes must remain null")
        if not _sequence(item.get("required_manual_checks")):
            errors.append(f"{prefix}.required_manual_checks must be non-empty")


def _scan_forbidden(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            normalized_key = str(key).strip().lower()
            if normalized_key in _MUTATION_KEYS and _truthy(child):
                errors.append(f"{child_path} must not enable mutation")
            if _ARTIFACT_KEYS.search(normalized_key) and _present(child) and normalized_key not in _allowed_artifact_policy_keys():
                errors.append(f"{child_path} must not contain browser, session, artifact, raw, or private values")
            _scan_forbidden(child, child_path, errors)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]", errors)
        return
    if isinstance(value, str):
        if _PRIVATE_OR_ARTIFACT_TEXT.search(value) or _LIVE_OR_OFFICIAL_TEXT.search(value):
            errors.append(f"{path} contains prohibited private, artifact, live-run, or official-action text")
        if _CONSEQUENTIAL_ACTION_TEXT.search(value) and not _allowed_consequential_policy_path(path):
            errors.append(f"{path} contains prohibited consequential-action language")


def _allowed_artifact_policy_keys() -> set[str]:
    return {
        "browser_or_session_artifacts_created",
        "private_values_stored",
        "redaction_placeholder_refs",
        "redaction_confirmation_placeholders",
        "read_only_surface_map_delta_placeholders",
        "surface_map_delta_placeholder_ref",
    }


def _allowed_consequential_policy_path(path: str) -> bool:
    return "blocked_consequential_action_confirmations" in path or path.endswith(".blocked_confirmation_ref")


def _string_set(value: Any) -> set[str]:
    return {str(item) for item in _sequence(value) if isinstance(item, str) and item.strip()}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return []


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "enabled", "active"}
    return False
