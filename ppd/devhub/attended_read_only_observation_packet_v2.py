"""Fixture-first DevHub attended read-only observation packet v2 validation.

This module is intentionally offline-only. It validates committed synthetic
observation packets that cite prior DevHub read-only planning fixtures without
opening DevHub, storing browser state, or mutating the surface registry.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


REQUIRED_PACKET_TYPE = "ppd.devhub.attended_read_only_observation_packet.v2"
REQUIRED_MODE = "fixture_first_devhub_attended_read_only_observation_v2"
REQUIRED_SOURCE_KEYS = (
    "devhub_attended_read_only_pilot_runbook",
    "devhub_attended_read_only_launch_readiness_packet",
    "devhub_read_only_observation_redaction_review_packet",
)
REQUIRED_SECTIONS = (
    "observed_surfaces",
    "allowed_read_only_actions",
    "manual_handoff_checkpoints",
    "redaction_attestations",
    "safety_attestations",
    "offline_validation_commands",
)
REQUIRED_REDACTION_ATTESTATIONS = (
    "no_credentials_or_secrets",
    "no_private_field_values",
    "no_raw_authenticated_text",
    "no_local_private_paths",
    "no_payment_details",
)
REQUIRED_SAFETY_ATTESTATIONS = (
    "no_live_devhub",
    "no_auth_state",
    "no_screenshot",
    "no_trace",
    "no_har",
    "no_surface_registry_mutation",
    "no_private_session_files",
)
REQUIRED_FALSE_FLAGS = (
    "launches_browser",
    "launches_playwright",
    "launches_devhub",
    "network_requests_made",
    "mutates_surface_registry",
)
FORBIDDEN_PACKET_KEYS = frozenset(
    {
        "auth",
        "auth_state",
        "auth_state_path",
        "authenticated_value",
        "browser_context",
        "browser_state",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "download_path",
        "downloaded_document",
        "har",
        "har_path",
        "har_url",
        "password",
        "private_value",
        "private_values",
        "raw_authenticated_text",
        "raw_authenticated_value",
        "raw_dom",
        "screenshot",
        "screenshot_path",
        "session",
        "session_file",
        "session_state",
        "storage_state",
        "storage_state_path",
        "trace",
        "trace_path",
        "token",
    }
)
FORBIDDEN_MUTATION_FLAGS = frozenset(
    {
        "active_agent_state_mutation",
        "active_guardrail_mutation",
        "active_monitoring_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_surface_registry_mutation",
        "agent_state_mutation",
        "guardrail_mutation",
        "monitoring_mutation",
        "mutates_agent_state",
        "mutates_guardrails",
        "mutates_monitoring",
        "mutates_prompts",
        "mutates_release_state",
        "mutates_surface_registry",
        "prompt_mutation",
        "release_state_mutation",
        "surface_registry_mutation",
    }
)
PRIVATE_VALUE_KEY_RE = re.compile(
    r"(^|_)(account|address|email|invoice|license|name|phone|permit|private|property|secret|token|user)(_.*)?$",
    re.IGNORECASE,
)
PRIVATE_VALUE_RE = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|"
    r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b|"
    r"\b\d{3,6}\s+(?:N|NE|NW|S|SE|SW|E|W)\s+[A-Z][A-Z0-9 ]+\b|"
    r"\b(?:permit|invoice|account|license)\s*(?:number|no\.|#)?\s*[:#]\s*[A-Z0-9-]{4,}\b",
    re.IGNORECASE,
)
PRIVATE_ARTIFACT_RE = re.compile(
    r"(/home/|/users/|c:\\\\users\\\\|file://|trace\.zip|\.har\b|storage[_ -]?state\.json|auth[_ -]?state\.json|screenshot\.(?:png|jpe?g|webp))",
    re.IGNORECASE,
)
ARTIFACT_REFERENCE_RE = re.compile(
    r"\b(screenshot|screen shot|trace\.zip|browser trace|playwright trace|har file|\.har\b|storage state|auth state|session state)\b",
    re.IGNORECASE,
)
LIVE_EXECUTION_RE = re.compile(
    r"\b(launched|ran|executed|clicked|filled|captured|stored|opened|navigated)\b.{0,80}\b(live devhub|live browser|playwright|auth state|screenshot|trace|har)\b|"
    r"\b(live devhub|live browser|playwright)\b.{0,80}\b(launched|ran|executed|clicked|filled|captured|stored|opened|navigated)\b",
    re.IGNORECASE,
)
CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(click|clicked|continue|continued|execute|executed|fill|filled|press|pressed|select|selected|start|started|trigger|triggered|use|used)\b.{0,80}\b(submit|submission|upload|certif|pay|payment|purchase|schedule|cancel|withdraw|reactivat|save draft|attach)\b|"
    r"\b(submit|submission|upload|certif|pay|payment|purchase|schedule|cancel|withdraw|reactivat|save draft|attach)\b.{0,80}\b(allowed|complete|completed|done|executed|proceed|started|successful|triggered)\b",
    re.IGNORECASE,
)
LEGAL_OR_PERMITTING_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|ensure[sd]?|will|shall)\b.{0,80}\b(approval|approved|code compliant|compliance|issuance|issued|legal|permit outcome|permit will|pass inspection)\b|"
    r"\b(approval|approved|issuance|issued|legal compliance|permit outcome|pass inspection)\b.{0,80}\b(guarantee[sd]?|certain|assured|will|shall)\b",
    re.IGNORECASE,
)
SAFE_ARTIFACT_ATTESTATION_PATH_RE = re.compile(
    r"^\$\.safety_attestations\.no_(?:auth_state|har|screenshot|trace|private_session_files)$|"
    r"^\$\.redaction_attestations\[\d+\]\.attestation_id$|"
    r"^\$\.redaction_attestations\[\d+\]\.review_note$",
    re.IGNORECASE,
)
CONSEQUENTIAL_TERMS = (
    "submit",
    "submission",
    "upload",
    "certify",
    "payment",
    "pay",
    "purchase",
    "schedule",
    "cancel",
    "withdraw",
    "reactivate",
)


class AttendedReadOnlyObservationPacketV2Error(ValueError):
    """Raised when a v2 observation packet is not commit-safe."""


def load_json_packet(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise AttendedReadOnlyObservationPacketV2Error("packet fixture must be a JSON object")
    return packet


def validate_attended_read_only_observation_packet_v2(packet: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    _require(errors, isinstance(packet, Mapping), "packet must be a JSON object")
    if not isinstance(packet, Mapping):
        return tuple(errors)

    _require(errors, packet.get("packet_type") == REQUIRED_PACKET_TYPE, f"packet_type must be {REQUIRED_PACKET_TYPE}")
    _require(errors, packet.get("mode") == REQUIRED_MODE, f"mode must be {REQUIRED_MODE}")
    for field in ("fixture_first", "offline_only", "synthetic_only", "read_only_only"):
        _require(errors, packet.get(field) is True, f"{field} must be true")
    for field in REQUIRED_FALSE_FLAGS:
        _require(errors, packet.get(field) is False, f"{field} must be false")

    sources = _mapping(packet.get("source_packets"))
    for key in REQUIRED_SOURCE_KEYS:
        source = _mapping(sources.get(key))
        _require(errors, bool(_text(source.get("packet_id"))), f"source_packets.{key}.packet_id is required")
        _require(errors, source.get("consumed") is True, f"source_packets.{key}.consumed must be true")

    for section in REQUIRED_SECTIONS:
        rows = _sequence(packet.get(section)) if section != "safety_attestations" else _mapping(packet.get(section))
        _require(errors, bool(rows), f"{section} must be non-empty")

    for index, surface in enumerate(_sequence(packet.get("observed_surfaces"))):
        item = _mapping(surface)
        prefix = f"observed_surfaces[{index}]"
        _require(errors, bool(_text(item.get("surface_id"))), f"{prefix}.surface_id is required")
        _require(errors, item.get("synthetic_only") is True, f"{prefix}.synthetic_only must be true")
        _require(errors, item.get("no_raw_values") is True, f"{prefix}.no_raw_values must be true")
        _require(errors, bool(_sequence(item.get("observed_elements"))), f"{prefix}.observed_elements must be non-empty")
        _require(errors, bool(_sequence(item.get("citations"))), f"{prefix}.citations must be non-empty")
        _require(errors, _is_string_sequence(item.get("citations")), f"{prefix}.citations must be a list of strings")

    for index, action in enumerate(_sequence(packet.get("allowed_read_only_actions"))):
        item = _mapping(action)
        prefix = f"allowed_read_only_actions[{index}]"
        _require(errors, _text(item.get("action_class")) == "read_only_metadata_observation", f"{prefix}.action_class must be read_only_metadata_observation")
        _require(errors, item.get("allowed") is True, f"{prefix}.allowed must be true")
        _require(errors, item.get("no_state_change") is True, f"{prefix}.no_state_change must be true")
        _require(errors, bool(_sequence(item.get("citations"))), f"{prefix}.citations must be non-empty")
        label = " ".join(_text(item.get(key)) for key in ("action_id", "label", "description")).lower()
        _require(errors, not any(term in label for term in CONSEQUENTIAL_TERMS), f"{prefix} must not describe consequential DevHub action")

    for index, checkpoint in enumerate(_sequence(packet.get("manual_handoff_checkpoints"))):
        item = _mapping(checkpoint)
        prefix = f"manual_handoff_checkpoints[{index}]"
        _require(errors, _text(item.get("agent_action")) == "stop_and_handoff_to_operator", f"{prefix}.agent_action must stop and hand off")
        _require(errors, item.get("agent_may_continue") is False, f"{prefix}.agent_may_continue must be false")
        _require(errors, item.get("official_action_allowed") is False, f"{prefix}.official_action_allowed must be false")
        _require(errors, bool(_sequence(item.get("citations"))), f"{prefix}.citations must be non-empty")

    attestation_rows = _sequence(packet.get("redaction_attestations"))
    attestation_by_id = {_text(_mapping(row).get("attestation_id")): _mapping(row) for row in attestation_rows}
    for name in REQUIRED_REDACTION_ATTESTATIONS:
        row = attestation_by_id.get(name, {})
        _require(errors, row.get("attested") is True, f"redaction_attestations.{name} must be attested")
        _require(errors, bool(_sequence(row.get("citations"))), f"redaction_attestations.{name}.citations must be non-empty")

    safety = _mapping(packet.get("safety_attestations"))
    for name in REQUIRED_SAFETY_ATTESTATIONS:
        _require(errors, safety.get(name) is True, f"safety_attestations.{name} must be true")

    for index, command in enumerate(_sequence(packet.get("offline_validation_commands"))):
        _require(errors, _is_string_sequence(command), f"offline_validation_commands[{index}] must be a list of strings")

    _scan_for_unsafe_content(errors, packet)
    return _dedupe(errors)


def assert_valid_attended_read_only_observation_packet_v2(packet: Mapping[str, Any]) -> None:
    errors = validate_attended_read_only_observation_packet_v2(packet)
    if errors:
        raise AttendedReadOnlyObservationPacketV2Error("; ".join(errors))


def _scan_for_unsafe_content(errors: list[str], value: Any, path: str = "$", parent_key: str = "") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = _text(key)
            key_lower = key_text.lower()
            child_path = f"{path}.{key_text}"
            if key_lower in FORBIDDEN_PACKET_KEYS:
                errors.append(f"{child_path} must not contain private DevHub artifact keys")
            if key_lower in FORBIDDEN_MUTATION_FLAGS and child is True:
                errors.append(f"{child_path} must not enable active registry, guardrail, prompt, monitoring, release-state, or agent-state mutation")
            if PRIVATE_VALUE_KEY_RE.search(key_text) and key_lower not in _safe_metadata_keys() and _looks_like_private_value(child):
                errors.append(f"{child_path} must not contain private or authenticated values")
            _scan_for_unsafe_content(errors, child, child_path, key_text)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_for_unsafe_content(errors, child, f"{path}[{index}]", parent_key)
        return
    if isinstance(value, str):
        if PRIVATE_ARTIFACT_RE.search(value):
            errors.append(f"{path} must not contain private artifact paths or filenames")
        if ARTIFACT_REFERENCE_RE.search(value) and not SAFE_ARTIFACT_ATTESTATION_PATH_RE.search(path):
            errors.append(f"{path} must not reference screenshots, traces, HAR, auth state, storage state, or session artifacts")
        if LIVE_EXECUTION_RE.search(value):
            errors.append(f"{path} must not claim live DevHub or browser execution")
        if CONSEQUENTIAL_ACTION_RE.search(value) and "manual_handoff_checkpoints" not in path:
            errors.append(f"{path} must not contain consequential DevHub action language")
        if LEGAL_OR_PERMITTING_GUARANTEE_RE.search(value):
            errors.append(f"{path} must not guarantee legal compliance or permitting outcomes")
        if PRIVATE_VALUE_RE.search(value):
            errors.append(f"{path} must not contain private or authenticated values")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _is_string_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and all(isinstance(item, str) for item in value)


def _looks_like_private_value(value: Any) -> bool:
    if isinstance(value, str):
        stripped = value.strip()
        return bool(stripped) and not stripped.startswith(("devhub-", "ppd."))
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_looks_like_private_value(item) for item in value)
    if isinstance(value, Mapping):
        return any(_looks_like_private_value(item) for item in value.values())
    return value is not None


def _safe_metadata_keys() -> set[str]:
    return {
        "action_id",
        "attestation_id",
        "checkpoint_id",
        "citations",
        "mode",
        "packet_id",
        "packet_type",
        "source_packets",
        "surface_id",
        "surface_kind",
    }


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def _dedupe(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return tuple(result)
