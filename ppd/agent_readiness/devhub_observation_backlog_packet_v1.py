"""Validation for attended DevHub read-only observation backlog packet v1.

The packet is a planning artifact only. It must describe manually attended,
redacted, read-only DevHub observations without browser/session artifacts,
private data, raw downloaded material, live execution claims, outcome promises,
or any active mutation flags.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

PACKET_VERSION = "attended-devhub-read-only-observation-backlog-packet-v1"
SAFE_READ_ONLY_CLASSIFICATIONS = frozenset({"safe_read_only", "safe-read-only", "read_only_observation"})

_REQUIRED_TOP_LEVEL_SEQUENCES = (
    "safe_read_only_classifications",
    "redaction_requirements",
    "manual_attendance_checkpoints",
    "blocked_consequential_actions",
    "validation_commands",
)

_PRIVATE_ARTIFACT_TERMS = (
    "auth state",
    "authenticated artifact",
    "browser profile",
    "cookie",
    "credential",
    "devhub session",
    "localstorage",
    "password",
    "private value",
    "session storage",
    "session_state",
    "storage_state",
    "token",
)

_CAPTURE_ARTIFACT_TERMS = (
    ".har",
    ".png",
    "auth file",
    "auth.json",
    "har file",
    "network trace",
    "screenshot",
    "storage_state.json",
    "trace.zip",
    "trace file",
)

_RAW_DATA_TERMS = (
    "downloaded data",
    "downloaded pdf",
    "pdf dump",
    "raw authenticated html",
    "raw crawl",
    "raw download",
    "raw pdf",
)

_LIVE_EXECUTION_TERMS = (
    "completed authenticated run",
    "executed in devhub",
    "live authenticated execution",
    "logged into devhub and ran",
    "ran against live devhub",
)

_OUTCOME_GUARANTEE_TERMS = (
    "approval guaranteed",
    "certification complete",
    "guaranteed permit",
    "legal advice",
    "permit approved",
    "permit issued",
    "will be approved",
    "will be issued",
)

_CONSEQUENTIAL_ACTION_TERMS = (
    "cancel",
    "cancellation",
    "certification",
    "certify",
    "payment",
    "pay",
    "schedule",
    "submit",
    "submission",
    "upload",
)

_MUTATION_FLAG_KEYS = (
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_surface_mutation",
    "agent_state_mutation_enabled",
    "guardrail_mutation_enabled",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_surfaces",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "surface_mutation_enabled",
)

_ARTIFACT_POLICY_KEYS = (
    "creates_auth_files",
    "creates_browser_artifacts",
    "creates_har_files",
    "creates_screenshots",
    "creates_session_state",
    "creates_traces",
    "captures_private_values",
    "stores_downloads",
    "stores_raw_crawl_output",
)


def validate_devhub_observation_backlog_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for a packet candidate."""

    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet must be an object"]

    version = packet.get("packet_version") or packet.get("packet_type")
    if version != PACKET_VERSION:
        errors.append("packet_version must be attended-devhub-read-only-observation-backlog-packet-v1")

    if packet.get("attendance_mode") not in {"manual_attended", "attended_manual"}:
        errors.append("attendance_mode must be manual_attended")
    if packet.get("observation_mode") not in {"read_only", "safe_read_only"}:
        errors.append("observation_mode must be read_only")

    for key in _REQUIRED_TOP_LEVEL_SEQUENCES:
        _require_non_empty_sequence(packet, key, errors)

    _validate_classifications(packet.get("safe_read_only_classifications"), "safe_read_only_classifications", errors)
    _validate_artifact_policy(packet.get("artifact_policy", {}), errors)
    _validate_mutation_flags(packet.get("mutation_flags", {}), errors)
    _validate_work_items(packet.get("work_items"), errors)
    _scan_packet_text(packet, errors)
    return _dedupe(errors)


def validate_packet(packet: Mapping[str, Any]) -> list[str]:
    return validate_devhub_observation_backlog_packet_v1(packet)


def assert_valid_devhub_observation_backlog_packet_v1(packet: Mapping[str, Any]) -> None:
    errors = validate_devhub_observation_backlog_packet_v1(packet)
    if errors:
        raise AssertionError("invalid attended DevHub read-only observation backlog packet v1: " + "; ".join(errors))


def _validate_work_items(value: Any, errors: list[str]) -> None:
    if not _is_non_empty_sequence(value):
        errors.append("work_items must be a non-empty list")
        return
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        path = f"work_items[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{path} must be an object")
            continue
        item_id = item.get("id") or item.get("work_item_id")
        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(f"{path}.id must be a non-empty string")
        elif item_id in seen_ids:
            errors.append(f"{path}.id must be unique")
        else:
            seen_ids.add(item_id)

        classification = item.get("classification") or item.get("action_classification")
        if classification not in SAFE_READ_ONLY_CLASSIFICATIONS:
            errors.append(f"{path}.classification must be safe_read_only")
        for key in (
            "redaction_requirements",
            "manual_attendance_checkpoints",
            "blocked_consequential_actions",
            "validation_commands",
        ):
            _require_non_empty_sequence(item, key, errors, path=f"{path}.{key}")


def _validate_classifications(value: Any, path: str, errors: list[str]) -> None:
    if not _is_non_empty_sequence(value):
        return
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if isinstance(item, str):
            if item not in SAFE_READ_ONLY_CLASSIFICATIONS:
                errors.append(f"{item_path} must be safe_read_only")
        elif isinstance(item, Mapping):
            classification = item.get("classification") or item.get("action_classification")
            if classification not in SAFE_READ_ONLY_CLASSIFICATIONS:
                errors.append(f"{item_path}.classification must be safe_read_only")
        else:
            errors.append(f"{item_path} must be a string or object")


def _validate_artifact_policy(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("artifact_policy must be an object")
        return
    for key in _ARTIFACT_POLICY_KEYS:
        if value.get(key) is not False:
            errors.append(f"artifact_policy.{key} must be false")


def _validate_mutation_flags(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("mutation_flags must be an object")
        return
    for key in _MUTATION_FLAG_KEYS:
        if value.get(key) not in (False, None):
            errors.append(f"mutation_flags.{key} must be false or absent")


def _scan_packet_text(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, text in _walk_text(packet):
        lowered = " ".join(text.lower().replace("_", " ").replace("-", " ").split())
        compact = lowered.replace(" ", "_")
        searchable = lowered + " " + compact

        if _contains_any(searchable, _PRIVATE_ARTIFACT_TERMS):
            errors.append(f"{path} contains private/authenticated/session artifact language")
        if _contains_any(searchable, _CAPTURE_ARTIFACT_TERMS):
            errors.append(f"{path} contains screenshot/trace/HAR/auth-file artifact language")
        if _contains_any(searchable, _RAW_DATA_TERMS):
            errors.append(f"{path} contains raw crawl/PDF/downloaded data language")
        if _contains_any(searchable, _LIVE_EXECUTION_TERMS):
            errors.append(f"{path} contains live authenticated execution claim")
        if _contains_any(searchable, _OUTCOME_GUARANTEE_TERMS):
            errors.append(f"{path} contains legal or permitting outcome guarantee")
        if not _is_blocked_consequential_path(path) and _contains_any(searchable, _CONSEQUENTIAL_ACTION_TERMS):
            errors.append(f"{path} contains consequential action language outside blocked rows")


def _walk_text(value: Any, path: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, Mapping):
        rows: list[tuple[str, str]] = []
        for key, child in value.items():
            rows.extend(_walk_text(child, f"{path}.{key}"))
        return rows
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        rows = []
        for index, child in enumerate(value):
            rows.extend(_walk_text(child, f"{path}[{index}]"))
        return rows
    return []


def _is_blocked_consequential_path(path: str) -> bool:
    return ".blocked_consequential_actions" in path or ".blocked_actions" in path


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _require_non_empty_sequence(mapping: Mapping[str, Any], key: str, errors: list[str], *, path: str | None = None) -> None:
    actual_path = path or key
    value = mapping.get(key)
    if not _is_non_empty_sequence(value):
        errors.append(f"{actual_path} must be a non-empty list")


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)) and len(value) > 0


def _dedupe(errors: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for error in errors:
        if error not in seen:
            seen.add(error)
            result.append(error)
    return result
