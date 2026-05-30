"""Fixture-first attended DevHub observation prep packet v1.

This module transforms an attended read-only DevHub observation backlog packet
into an operator prep packet. It is deliberately offline-only: it does not open
browsers, contact DevHub, persist auth state, save screenshots, create traces,
create HAR files, store private values, download records, upload files, submit,
pay, certify, cancel, or schedule anything.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ppd.agent_readiness.devhub_observation_backlog_packet_v1 import (
    assert_valid_devhub_observation_backlog_packet_v1,
)

PREP_PACKET_VERSION = "attended-devhub-observation-prep-packet-v1"

_ARTIFACT_POLICY_KEYS = (
    "creates_auth_state",
    "creates_auth_files",
    "creates_browser_artifacts",
    "creates_har_files",
    "creates_screenshots",
    "creates_session_state",
    "creates_traces",
    "captures_private_values",
    "stores_downloads",
    "stores_pdf_downloads",
    "stores_raw_crawl_output",
    "creates_uploads",
    "creates_submissions",
    "creates_payments",
    "creates_certifications",
    "creates_cancellations",
    "creates_scheduling_artifacts",
)

_MUTATION_FLAG_KEYS = (
    "active_surface_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
)

_REQUIRED_SECTIONS = (
    "manual_attendance_preflight_rows",
    "allowed_read_only_surface_targets",
    "redaction_inventory",
    "blocked_consequential_action_reminders",
    "abort_conditions",
    "reviewer_prompts",
    "offline_validation_commands",
)

_DEFAULT_ABORT_CONDITIONS = (
    "Abort if the operator is no longer present and attentive.",
    "Abort if credentials, MFA, CAPTCHA, or account recovery appears outside manual operator control.",
    "Abort before any official-record, draft, fee, inspection, attachment, attestation, withdrawal, or calendar-changing control.",
    "Abort if visible account-scoped values cannot be represented as bracketed placeholders.",
    "Abort if any tool attempts to create or persist non-commit-safe browser evidence.",
)

_DEFAULT_REVIEWER_PROMPTS = (
    "Do the ordered rows remain read-only and manually attended?",
    "Are all surface targets limited to labels, headings, status text, notices, lists, or navigation structure?",
    "Does the redaction inventory replace account, address, contact, permit, invoice, license, fee, and document values with placeholders?",
    "Are all consequential controls represented only as blocked reminders?",
    "Are the offline validation commands exact, deterministic, and free of live DevHub automation?",
)

_DEFAULT_REDACTION_INVENTORY = (
    ("private_values", "account, address, contact, permit, invoice, license, fee, and document values", "replace with bracketed placeholders"),
    ("manual_login_secrets", "credentials, MFA, CAPTCHA, password recovery, and account prompts", "operator-only handling with no recorded values"),
    ("browser_evidence_artifacts", "screenshots, traces, HAR exports, storage state, cookies, and auth files", "must not be created or committed"),
    ("downloads_and_raw_data", "raw crawl output, downloaded files, PDF payloads, and authenticated page bodies", "must not be stored in this packet"),
    ("live_execution_claims", "live authenticated browser execution claims", "must be absent from prep evidence"),
)

_CONSEQUENTIAL_TERMS = (
    "submit",
    "submission",
    "upload",
    "pay",
    "payment",
    "purchase",
    "checkout",
    "certify",
    "certification",
    "schedule",
    "scheduling",
    "cancel",
    "cancellation",
)

_CONCRETE_ARTIFACT_TERMS = (
    "screenshot.png",
    "trace.zip",
    ".har",
    "storage_state.json",
    "auth_state.json",
    "auth.json",
    "cookies.json",
    "session.json",
    "playwright-report",
    "test-results/",
    "/downloads/",
    "downloaded pdf",
    "pdf bytes",
    "raw crawl output",
    "raw downloaded data",
)

_LIVE_AUTH_CLAIMS = (
    "ran live authenticated",
    "executed live authenticated",
    "opened authenticated devhub",
    "logged into devhub",
    "captured authenticated",
    "used saved session",
    "loaded auth state",
    "reused cookies",
)

_OUTCOME_GUARANTEE_TERMS = (
    "guarantee approval",
    "guaranteed approval",
    "permit will be approved",
    "permit will be issued",
    "legal guarantee",
    "permitting outcome guarantee",
    "approval is guaranteed",
)

_MUTATING_CLASSIFICATION_TERMS = (
    "active",
    "write",
    "mutat",
    "edit",
    "draft-fill",
    "draft_fill",
    "interactive",
)

_PRIVATE_ARTIFACT_FIELD_NAMES = (
    "auth",
    "auth_state",
    "browser_context",
    "cookie",
    "credential",
    "download",
    "har",
    "password",
    "pdf_bytes",
    "private_value",
    "raw_crawl",
    "raw_data",
    "screenshot",
    "session",
    "storage_state",
    "token",
    "trace",
)


def load_json_packet(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError(f"packet must be a JSON object: {packet_path}")
    return packet


def build_attended_observation_prep_packet_v1(backlog_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic prep packet from a validated read-only backlog."""

    assert_valid_devhub_observation_backlog_packet_v1(backlog_packet)
    work_items = list(backlog_packet.get("work_items", ()))

    rows = []
    for order, item in enumerate(work_items, start=1):
        if not isinstance(item, Mapping):
            continue
        rows.append(
            {
                "order": order,
                "source_work_item_id": str(item.get("id") or item.get("work_item_id")),
                "surface": str(item.get("surface")),
                "objective": _readonly_objective(item),
                "attendance_checkpoint": _first_string(item.get("manual_attendance_checkpoints")),
                "redaction_checkpoint": _first_string(item.get("redaction_requirements")),
                "allowed_operator_result": "record only redacted read-only observations and reviewer notes",
            }
        )

    packet = {
        "packet_version": PREP_PACKET_VERSION,
        "packet_id": "attended-devhub-observation-prep-packet-v1",
        "source_backlog_packet_id": str(backlog_packet.get("packet_id")),
        "mode": "fixture_first_manual_attendance_prep",
        "artifact_policy": {key: False for key in _ARTIFACT_POLICY_KEYS},
        "mutation_flags": {key: False for key in _MUTATION_FLAG_KEYS},
        "manual_attendance_preflight_rows": rows,
        "allowed_read_only_surface_targets": _surface_targets(backlog_packet),
        "redaction_inventory": _redaction_inventory(backlog_packet),
        "blocked_consequential_action_reminders": _blocked_action_reminders(backlog_packet),
        "abort_conditions": list(_DEFAULT_ABORT_CONDITIONS),
        "reviewer_prompts": list(_DEFAULT_REVIEWER_PROMPTS),
        "offline_validation_commands": _offline_validation_commands(backlog_packet),
    }
    assert_valid_attended_observation_prep_packet_v1(packet)
    return packet


def validate_attended_observation_prep_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet must be an object"]
    if packet.get("packet_version") != PREP_PACKET_VERSION:
        errors.append(f"packet_version must be {PREP_PACKET_VERSION}")
    if packet.get("mode") != "fixture_first_manual_attendance_prep":
        errors.append("mode must be fixture_first_manual_attendance_prep")

    _validate_artifact_policy(packet.get("artifact_policy"), errors)
    _validate_mutation_flags(packet.get("mutation_flags"), errors)

    for section in _REQUIRED_SECTIONS:
        value = packet.get(section)
        if not isinstance(value, list) or not value:
            errors.append(f"{section} must be a non-empty list")

    _validate_preflight_rows(packet.get("manual_attendance_preflight_rows"), errors)
    _validate_surface_targets(packet.get("allowed_read_only_surface_targets"), errors)
    _validate_redaction_inventory(packet.get("redaction_inventory"), errors)
    _validate_blocked_action_reminders(packet.get("blocked_consequential_action_reminders"), errors)
    _validate_abort_conditions(packet.get("abort_conditions"), errors)
    _validate_reviewer_prompts(packet.get("reviewer_prompts"), errors)
    _validate_command_rows(packet.get("offline_validation_commands"), errors)
    _scan_text(packet, errors)
    return list(dict.fromkeys(errors))


def assert_valid_attended_observation_prep_packet_v1(packet: Mapping[str, Any]) -> None:
    errors = validate_attended_observation_prep_packet_v1(packet)
    if errors:
        raise AssertionError("invalid attended DevHub observation prep packet v1: " + "; ".join(errors))


def _validate_artifact_policy(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("artifact_policy must be an object")
        return
    for key in _ARTIFACT_POLICY_KEYS:
        if value.get(key) is not False:
            errors.append(f"artifact_policy.{key} must be false")
    unknown_enabled = [key for key, flag in value.items() if key not in _ARTIFACT_POLICY_KEYS and flag is not False]
    for key in unknown_enabled:
        errors.append(f"artifact_policy.{key} must not enable private, browser, session, raw-data, or consequential artifacts")


def _validate_mutation_flags(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("mutation_flags must be an object")
        return
    for key in _MUTATION_FLAG_KEYS:
        if value.get(key) is not False:
            errors.append(f"mutation_flags.{key} must be false")
    unknown_enabled = [key for key, flag in value.items() if key not in _MUTATION_FLAG_KEYS and flag is not False]
    for key in unknown_enabled:
        errors.append(f"mutation_flags.{key} must be false")


def _surface_targets(backlog_packet: Mapping[str, Any]) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in backlog_packet.get("safe_read_only_classifications", ()):
        if isinstance(item, Mapping):
            surface = str(item.get("surface") or "").strip()
            classification = str(item.get("classification") or "").strip()
        else:
            surface = str(item).strip()
            classification = "safe_read_only"
        if surface and surface not in seen:
            targets.append({"surface": surface, "classification": classification or "safe_read_only", "allowed_result": "redacted_read_only_metadata"})
            seen.add(surface)
    for item in backlog_packet.get("work_items", ()):
        if isinstance(item, Mapping):
            surface = str(item.get("surface") or "").strip()
            if surface and surface not in seen:
                targets.append({"surface": surface, "classification": "safe_read_only", "allowed_result": "redacted_read_only_metadata"})
                seen.add(surface)
    return targets


def _validate_surface_targets(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    seen: set[str] = set()
    for index, row in enumerate(value):
        path = f"allowed_read_only_surface_targets[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        surface = _required_string(row.get("surface"), f"{path}.surface", errors)
        classification = _required_string(row.get("classification"), f"{path}.classification", errors)
        if surface:
            if surface in seen:
                errors.append(f"{path}.surface must be unique")
            seen.add(surface)
        lowered = classification.lower()
        if "read_only" not in lowered and "read-only" not in lowered:
            errors.append(f"{path}.classification must be read-only")
        if any(term in lowered for term in _MUTATING_CLASSIFICATION_TERMS):
            errors.append(f"{path}.classification must not allow active surface mutation")


def _redaction_inventory(backlog_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item_id, target, handling in _DEFAULT_REDACTION_INVENTORY:
        rows.append({"item_id": item_id, "source": "prep_default", "target": target, "handling": handling, "required": True})
    for order, requirement in enumerate(_strings(backlog_packet.get("redaction_requirements")), start=1):
        rows.append({"item_id": f"packet_requirement_{order}", "source": "packet", "target": requirement, "handling": "enforce before reviewer use", "required": True})
    for item in backlog_packet.get("work_items", ()):
        if not isinstance(item, Mapping):
            continue
        source = str(item.get("id") or item.get("work_item_id"))
        for requirement in _strings(item.get("redaction_requirements")):
            rows.append({"item_id": f"{source}_redaction_{len(rows) + 1}", "source": source, "target": requirement, "handling": "enforce before reviewer use", "required": True})
    return rows


def _validate_redaction_inventory(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    coverage = {key: False for key, _, _ in _DEFAULT_REDACTION_INVENTORY}
    for index, row in enumerate(value):
        path = f"redaction_inventory[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        item_id = _required_string(row.get("item_id"), f"{path}.item_id", errors)
        _required_string(row.get("source"), f"{path}.source", errors)
        _required_string(row.get("target"), f"{path}.target", errors)
        _required_string(row.get("handling"), f"{path}.handling", errors)
        if row.get("required") is not True:
            errors.append(f"{path}.required must be true")
        if item_id in coverage:
            coverage[item_id] = True
    missing = [key for key, present in coverage.items() if not present]
    if missing:
        errors.append("redaction_inventory missing required coverage: " + ", ".join(missing))


def _blocked_action_reminders(backlog_packet: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for action in backlog_packet.get("blocked_consequential_actions", ()):
        if isinstance(action, Mapping):
            label = str(action.get("action") or action.get("name") or "").strip()
            classification = str(action.get("classification") or "consequential").strip()
        else:
            label = str(action).strip()
            classification = "consequential"
        if label:
            rows.append({"action": label, "classification": classification, "required_operator_behavior": "stop and leave blocked"})
    for item in backlog_packet.get("work_items", ()):
        if not isinstance(item, Mapping):
            continue
        source = str(item.get("id") or item.get("work_item_id"))
        for action in _strings(item.get("blocked_consequential_actions")):
            rows.append({"action": action, "classification": "consequential", "source_work_item_id": source, "required_operator_behavior": "stop and leave blocked"})
    return rows


def _validate_blocked_action_reminders(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    combined = []
    for index, row in enumerate(value):
        path = f"blocked_consequential_action_reminders[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        action = _required_string(row.get("action"), f"{path}.action", errors)
        _required_string(row.get("classification"), f"{path}.classification", errors)
        behavior = _required_string(row.get("required_operator_behavior"), f"{path}.required_operator_behavior", errors)
        combined.append(action.lower())
        if behavior and not any(term in behavior.lower() for term in ("block", "stop", "refuse", "leave")):
            errors.append(f"{path}.required_operator_behavior must instruct the operator to block or stop")
    missing = [term for term in ("submit", "upload", "pay", "payment", "schedule", "cancel", "certify") if not any(term in action for action in combined)]
    if missing:
        errors.append("blocked_consequential_action_reminders missing required action coverage: " + ", ".join(missing))


def _validate_abort_conditions(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    for index, condition in enumerate(value):
        text = _required_string(condition, f"abort_conditions[{index}]", errors)
        if text and not any(term in text.lower() for term in ("abort", "stop", "refuse")):
            errors.append(f"abort_conditions[{index}] must use abort, stop, or refuse language")


def _validate_reviewer_prompts(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    for index, prompt in enumerate(value):
        text = _required_string(prompt, f"reviewer_prompts[{index}]", errors)
        if text and not text.endswith("?"):
            errors.append(f"reviewer_prompts[{index}] must be phrased as a reviewer question")


def _offline_validation_commands(backlog_packet: Mapping[str, Any]) -> list[list[str]]:
    commands: list[list[str]] = []
    for command in backlog_packet.get("validation_commands", ()):
        command_row = _command(command)
        if command_row:
            commands.append(command_row)
    for item in backlog_packet.get("work_items", ()):
        if not isinstance(item, Mapping):
            continue
        for command in item.get("validation_commands", ()):
            command_row = _command(command)
            if command_row:
                commands.append(command_row)
    commands.append(["python3", "ppd/daemon/ppd_daemon.py", "--self-test"])
    deduped: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for command in commands:
        key = tuple(command)
        if key not in seen:
            deduped.append(command)
            seen.add(key)
    return deduped


def _validate_preflight_rows(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    expected_order = list(range(1, len(value) + 1))
    observed_order: list[int] = []
    seen_sources: set[str] = set()
    for index, row in enumerate(value):
        path = f"manual_attendance_preflight_rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        order = row.get("order")
        if isinstance(order, int):
            observed_order.append(order)
        else:
            errors.append(f"{path}.order must be an integer")
        source = _required_string(row.get("source_work_item_id"), f"{path}.source_work_item_id", errors)
        if source:
            if source in seen_sources:
                errors.append(f"{path}.source_work_item_id must be unique")
            seen_sources.add(source)
        for key in ("surface", "objective", "attendance_checkpoint", "redaction_checkpoint", "allowed_operator_result"):
            _required_string(row.get(key), f"{path}.{key}", errors)
        attendance = str(row.get("attendance_checkpoint") or "").lower()
        result = str(row.get("allowed_operator_result") or "").lower()
        if "present" not in attendance and "manual" not in attendance and "operator" not in attendance:
            errors.append(f"{path}.attendance_checkpoint must require manual attendance")
        if "read-only" not in result and "read only" not in result:
            errors.append(f"{path}.allowed_operator_result must stay read-only")
    if observed_order and observed_order != expected_order:
        errors.append("manual_attendance_preflight_rows order must be contiguous starting at 1")


def _validate_command_rows(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    if ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] not in value:
        errors.append("offline_validation_commands must include the daemon self-test command")
    for index, command in enumerate(value):
        command_row = _command(command)
        if not command_row:
            errors.append(f"offline_validation_commands[{index}] must be a non-empty string array")
            continue
        lowered = " ".join(command_row).lower()
        if any(term in lowered for term in ("curl", "wget", "playwright open", "devhub.portlandoregon.gov", "--headed", "storage-state")):
            errors.append(f"offline_validation_commands[{index}] must be offline and deterministic")


def _scan_text(value: Any, errors: list[str], path: str = "$") -> None:
    if isinstance(value, str):
        lowered = " ".join(value.lower().split())
        if any(term in lowered for term in _CONCRETE_ARTIFACT_TERMS):
            errors.append(f"{path} contains private/session/browser artifact or raw data language")
        if any(term in lowered for term in _LIVE_AUTH_CLAIMS):
            errors.append(f"{path} contains live authenticated execution claim")
        if any(term in lowered for term in _OUTCOME_GUARANTEE_TERMS):
            errors.append(f"{path} contains legal or permitting outcome guarantee")
        if not _path_allows_consequential_terms(path) and any(term in lowered for term in _CONSEQUENTIAL_TERMS):
            errors.append(f"{path} contains consequential action language outside blocked reminders")
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if _private_artifact_field_name(str(key)) and not _path_allows_private_artifact_keys(child_path):
                errors.append(f"{child_path} is a private/session/browser artifact field")
            _scan_text(child, errors, child_path)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for index, child in enumerate(value):
            _scan_text(child, errors, f"{path}[{index}]")


def _path_allows_consequential_terms(path: str) -> bool:
    return ".blocked_consequential_action_reminders" in path or ".abort_conditions" in path or ".reviewer_prompts" in path


def _path_allows_private_artifact_keys(path: str) -> bool:
    return ".artifact_policy." in path or ".redaction_inventory" in path or ".abort_conditions" in path or ".reviewer_prompts" in path


def _private_artifact_field_name(key: str) -> bool:
    lowered = key.lower()
    return any(term in lowered for term in _PRIVATE_ARTIFACT_FIELD_NAMES)


def _readonly_objective(item: Mapping[str, Any]) -> str:
    surface = str(item.get("surface") or "target surface").strip() or "target surface"
    return f"Observe redacted read-only labels, headings, status categories, notices, lists, and navigation structure for {surface}."


def _required_string(value: Any, path: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")
        return ""
    return value.strip()


def _first_string(value: Any) -> str:
    strings = _strings(value)
    if not strings:
        return "operator remains present and records redacted read-only observations only"
    return strings[0]


def _strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray, str)):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _command(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray, str)):
        return []
    if not all(isinstance(part, str) and part for part in value):
        return []
    return list(value)
