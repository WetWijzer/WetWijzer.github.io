"""Fixture-first DevHub attended observation preflight packet v1.

This module consumes the offline DevHub attended observation renewal queue v1
and produces ordered observation-session readiness rows. It never opens DevHub,
creates browser evidence, stores account-scoped values, changes prompts, or
performs official actions.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ppd.agent_readiness.devhub_attended_observation_renewal_queue_v1 import (
    assert_valid_devhub_attended_observation_renewal_queue_v1,
)

PREFLIGHT_PACKET_VERSION = "devhub_attended_observation_preflight_packet_v1"

_REQUIRED_LISTS = (
    "observation_session_readiness_rows",
    "manual_login_handoff_placeholders",
    "redaction_checklist_confirmations",
    "read_only_surface_scope_citations",
    "blocked_consequential_action_reminders",
    "reviewer_approval_placeholders",
    "offline_validation_commands",
)

_ARTIFACT_POLICY_KEYS = (
    "captures_auth_files",
    "captures_browser_artifacts",
    "captures_har_files",
    "captures_private_page_values",
    "captures_private_values",
    "captures_screenshots",
    "captures_session_state",
    "captures_traces",
    "creates_auth_files",
    "creates_browser_artifacts",
    "creates_har_files",
    "creates_screenshots",
    "creates_session_state",
    "creates_traces",
    "stores_downloads",
    "stores_raw_crawl_output",
    "stores_raw_private_output",
)

_MUTATION_FLAG_KEYS = (
    "active_surface_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
)

_MUTATION_KEY_TERMS = (
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_surface_mutation",
    "agent_state_mutation_enabled",
    "guardrail_mutation_enabled",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_prompt",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_surface",
    "mutates_surfaces",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "surface_mutation_enabled",
)

_BLOCKED_ACTION_TERMS = (
    "cancel",
    "cancellation",
    "certification",
    "certify",
    "payment",
    "pay fee",
    "pay the fee",
    "schedule",
    "scheduling",
    "submit",
    "submission",
    "upload",
)

_PRIVATE_ARTIFACT_TERMS = (
    ".har",
    ".png",
    "auth file",
    "auth json",
    "auth state",
    "auth.json",
    "authenticated artifact",
    "browser artifact",
    "browser profile",
    "browser state",
    "cookie",
    "credential",
    "devhub session",
    "har file",
    "local private path",
    "localstorage",
    "network trace",
    "password",
    "private artifact",
    "private page value",
    "private value",
    "screenshot",
    "session artifact",
    "session state",
    "session storage",
    "session_state",
    "storage state",
    "storage_state",
    "token",
    "trace file",
    "trace zip",
    "trace.zip",
)

_LIVE_ACCESS_TERMS = (
    "accessed live devhub",
    "completed authenticated run",
    "executed in devhub",
    "live authenticated execution",
    "live devhub access",
    "logged into devhub",
    "opened devhub",
    "ran against live devhub",
)

_OFFLINE_COMMAND_DENY_TERMS = (
    "curl",
    "devhub.portlandoregon.gov",
    "headed",
    "playwright",
    "storage-state",
    "storage_state",
    "wget",
)


def load_json_packet(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError(f"packet must be a JSON object: {packet_path}")
    return packet


def build_devhub_attended_observation_preflight_packet_v1(queue: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic offline preflight packet from a validated queue."""

    assert_valid_devhub_attended_observation_renewal_queue_v1(queue)

    manual_placeholders = _manual_login_handoff_placeholders(queue)
    redaction_confirmations = _redaction_checklist_confirmations(queue)
    scope_citations = _read_only_scope_citations(queue)
    reviewer_placeholders = _reviewer_approval_placeholders(queue)

    packet = {
        "packet_version": PREFLIGHT_PACKET_VERSION,
        "packet_id": "fixture-devhub-attended-observation-preflight-packet-v1",
        "source_queue_id": str(queue.get("queue_id") or ""),
        "mode": "fixture_first_attended_read_only_preflight",
        "artifact_policy": {key: False for key in _ARTIFACT_POLICY_KEYS},
        "mutation_flags": {key: False for key in _MUTATION_FLAG_KEYS},
        "observation_session_readiness_rows": _readiness_rows(queue, scope_citations),
        "manual_login_handoff_placeholders": manual_placeholders,
        "redaction_checklist_confirmations": redaction_confirmations,
        "read_only_surface_scope_citations": scope_citations,
        "blocked_consequential_action_reminders": _blocked_reminders(queue),
        "reviewer_approval_placeholders": reviewer_placeholders,
        "offline_validation_commands": _offline_validation_commands(queue),
    }
    assert_valid_devhub_attended_observation_preflight_packet_v1(packet)
    return packet


def validate_devhub_attended_observation_preflight_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet must be an object"]
    if packet.get("packet_version") != PREFLIGHT_PACKET_VERSION:
        errors.append(f"packet_version must be {PREFLIGHT_PACKET_VERSION}")
    if packet.get("mode") != "fixture_first_attended_read_only_preflight":
        errors.append("mode must be fixture_first_attended_read_only_preflight")

    for key in _REQUIRED_LISTS:
        if not isinstance(packet.get(key), list) or not packet.get(key):
            errors.append(f"{key} must be a non-empty list")

    _validate_false_flags(packet.get("artifact_policy"), _ARTIFACT_POLICY_KEYS, "artifact_policy", errors)
    _validate_false_flags(packet.get("mutation_flags"), _MUTATION_FLAG_KEYS, "mutation_flags", errors)
    _validate_no_active_mutation_flags(packet, "$", errors)
    _validate_packet_references(packet, errors)
    _validate_readiness_rows(packet.get("observation_session_readiness_rows"), errors)
    _validate_placeholders(packet.get("manual_login_handoff_placeholders"), "manual_login_handoff_placeholder_id", errors)
    _validate_redaction_confirmations(packet.get("redaction_checklist_confirmations"), errors)
    _validate_scope_citations(packet.get("read_only_surface_scope_citations"), errors)
    _validate_blocked_reminders(packet.get("blocked_consequential_action_reminders"), errors)
    _validate_reviewer_placeholders(packet.get("reviewer_approval_placeholders"), errors)
    _validate_commands(packet.get("offline_validation_commands"), errors)
    _scan_text(packet, "$", errors)
    return list(dict.fromkeys(errors))


def assert_valid_devhub_attended_observation_preflight_packet_v1(packet: Mapping[str, Any]) -> None:
    errors = validate_devhub_attended_observation_preflight_packet_v1(packet)
    if errors:
        raise AssertionError("invalid DevHub attended observation preflight packet v1: " + "; ".join(errors))


def _readiness_rows(queue: Mapping[str, Any], citations: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    citation_ids_by_candidate: dict[str, list[str]] = {}
    for citation in citations:
        citation_ids_by_candidate.setdefault(citation["source_candidate_id"], []).append(citation["scope_citation_id"])
    for order, candidate in enumerate(queue.get("observation_candidate_rows", ()), start=1):
        if not isinstance(candidate, Mapping):
            continue
        candidate_id = str(candidate.get("candidate_id") or "")
        rows.append(
            {
                "order": order,
                "source_candidate_id": candidate_id,
                "surface_id": str(candidate.get("surface_id") or ""),
                "renewal_reason": str(candidate.get("renewal_reason") or ""),
                "readiness_status": "ready_for_manual_observation_preflight",
                "manual_login_handoff_placeholder_id": str(candidate.get("attendance_preflight_placeholder_id") or ""),
                "redaction_checklist_confirmation_id": str(candidate.get("redaction_checklist_reference_id") or ""),
                "read_only_surface_scope_citation_ids": citation_ids_by_candidate.get(candidate_id, []),
                "blocked_consequential_action_reminder_id": str(candidate.get("blocked_consequential_action_reminder_id") or ""),
                "reviewer_approval_placeholder_id": str(candidate.get("reviewer_approval_placeholder_id") or ""),
                "allowed_result": "redacted read-only observation metadata for reviewer approval",
            }
        )
    return rows


def _manual_login_handoff_placeholders(queue: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in queue.get("attendance_preflight_placeholders", ()):
        if not isinstance(item, Mapping):
            continue
        placeholder_id = str(item.get("attendance_preflight_placeholder_id") or item.get("id") or "")
        rows.append(
            {
                "manual_login_handoff_placeholder_id": placeholder_id,
                "source_attendance_preflight_placeholder_id": placeholder_id,
                "handoff_state": "manual_operator_only_placeholder",
                "status": "pending_manual_login_handoff",
                "operator_note": "Operator handles sign-in and human verification directly; packet records placeholders only.",
            }
        )
    return rows


def _redaction_checklist_confirmations(queue: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in queue.get("redaction_checklist_references", ()):
        if not isinstance(item, Mapping):
            continue
        reference_id = str(item.get("redaction_checklist_reference_id") or item.get("id") or "")
        rows.append(
            {
                "redaction_checklist_confirmation_id": reference_id,
                "source_redaction_checklist_reference_id": reference_id,
                "checklist_ref": str(item.get("checklist_ref") or ""),
                "confirmation_status": "pending_reviewer_confirmation",
                "required": True,
                "note": str(item.get("note") or ""),
            }
        )
    return rows


def _read_only_scope_citations(queue: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for candidate in queue.get("observation_candidate_rows", ()):
        if not isinstance(candidate, Mapping):
            continue
        candidate_id = str(candidate.get("candidate_id") or "")
        surface_id = str(candidate.get("surface_id") or "")
        evidence_ids = [str(item) for item in candidate.get("source_evidence_ids", ()) if isinstance(item, str) and item.strip()]
        for citation in candidate.get("citations", ()):
            if isinstance(citation, str) and citation.strip():
                evidence_ids.append(citation.strip())
            elif isinstance(citation, Mapping):
                value = str(citation.get("source_evidence_id") or citation.get("source_id") or citation.get("fixture") or citation.get("url") or "").strip()
                if value:
                    evidence_ids.append(value)
        for evidence_id in evidence_ids:
            key = (candidate_id, evidence_id)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "scope_citation_id": f"scope-{len(rows) + 1}",
                    "source_candidate_id": candidate_id,
                    "surface_id": surface_id,
                    "source_evidence_id": evidence_id,
                    "citation_scope": "read_only_public_or_offline_fixture_scope",
                }
            )
    return rows


def _blocked_reminders(queue: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = []
    for item in queue.get("blocked_consequential_action_reminders", ()):
        if not isinstance(item, Mapping):
            continue
        rows.append(
            {
                "blocked_consequential_action_reminder_id": str(item.get("blocked_consequential_action_reminder_id") or item.get("id") or ""),
                "reminder": str(item.get("reminder") or item.get("note") or ""),
                "required_behavior": "stop and leave blocked",
            }
        )
    return rows


def _reviewer_approval_placeholders(queue: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = []
    for item in queue.get("reviewer_approval_placeholders", ()):
        if not isinstance(item, Mapping):
            continue
        placeholder_id = str(item.get("reviewer_approval_placeholder_id") or item.get("id") or "")
        rows.append(
            {
                "reviewer_approval_placeholder_id": placeholder_id,
                "status": "pending_reviewer_approval",
                "note": str(item.get("note") or ""),
            }
        )
    return rows


def _offline_validation_commands(queue: Mapping[str, Any]) -> list[list[str]]:
    commands = [_command(row) for row in queue.get("validation_commands", ())]
    commands.extend(
        [
            ["python3", "-m", "py_compile", "ppd/devhub/devhub_attended_observation_preflight_packet_v1.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_devhub_attended_observation_preflight_packet_v1.py"],
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ]
    )
    deduped: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for command in commands:
        if command and tuple(command) not in seen:
            deduped.append(command)
            seen.add(tuple(command))
    return deduped


def _validate_packet_references(packet: Mapping[str, Any], errors: list[str]) -> None:
    manual_ids = _ids(packet.get("manual_login_handoff_placeholders"), "manual_login_handoff_placeholder_id")
    redaction_ids = _ids(packet.get("redaction_checklist_confirmations"), "redaction_checklist_confirmation_id")
    citation_ids = _ids(packet.get("read_only_surface_scope_citations"), "scope_citation_id")
    blocked_ids = _ids(packet.get("blocked_consequential_action_reminders"), "blocked_consequential_action_reminder_id")
    reviewer_ids = _ids(packet.get("reviewer_approval_placeholders"), "reviewer_approval_placeholder_id")

    rows = packet.get("observation_session_readiness_rows")
    if not isinstance(rows, list):
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            continue
        path = f"observation_session_readiness_rows[{index}]"
        _require_known_ref(row, "manual_login_handoff_placeholder_id", manual_ids, path, errors)
        _require_known_ref(row, "redaction_checklist_confirmation_id", redaction_ids, path, errors)
        _require_known_ref(row, "blocked_consequential_action_reminder_id", blocked_ids, path, errors)
        _require_known_ref(row, "reviewer_approval_placeholder_id", reviewer_ids, path, errors)
        citation_refs = row.get("read_only_surface_scope_citation_ids")
        if isinstance(citation_refs, list):
            for ref_index, citation_ref in enumerate(citation_refs):
                if not isinstance(citation_ref, str) or citation_ref not in citation_ids:
                    errors.append(f"{path}.read_only_surface_scope_citation_ids[{ref_index}] must reference a declared read-only scope citation")


def _validate_readiness_rows(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    observed_order = []
    seen: set[str] = set()
    for index, row in enumerate(value):
        path = f"observation_session_readiness_rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        if isinstance(row.get("order"), int):
            observed_order.append(row["order"])
        else:
            errors.append(f"{path}.order must be an integer")
        source_id = _required_string(row.get("source_candidate_id"), f"{path}.source_candidate_id", errors)
        if source_id in seen:
            errors.append(f"{path}.source_candidate_id must be unique")
        seen.add(source_id)
        for key in ("surface_id", "renewal_reason", "readiness_status", "manual_login_handoff_placeholder_id", "redaction_checklist_confirmation_id", "blocked_consequential_action_reminder_id", "reviewer_approval_placeholder_id", "allowed_result"):
            _required_string(row.get(key), f"{path}.{key}", errors)
        if row.get("readiness_status") != "ready_for_manual_observation_preflight":
            errors.append(f"{path}.readiness_status must be ready_for_manual_observation_preflight")
        if not isinstance(row.get("read_only_surface_scope_citation_ids"), list) or not row.get("read_only_surface_scope_citation_ids"):
            errors.append(f"{path}.read_only_surface_scope_citation_ids must be a non-empty list")
        if "read-only" not in str(row.get("allowed_result", "")).lower() and "read only" not in str(row.get("allowed_result", "")).lower():
            errors.append(f"{path}.allowed_result must remain read-only")
    if observed_order != list(range(1, len(value) + 1)):
        errors.append("observation_session_readiness_rows order must be contiguous starting at 1")


def _validate_placeholders(value: Any, id_key: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    for index, row in enumerate(value):
        path = f"manual_login_handoff_placeholders[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        _required_string(row.get(id_key), f"{path}.{id_key}", errors)
        if row.get("status") != "pending_manual_login_handoff":
            errors.append(f"{path}.status must be pending_manual_login_handoff")
        if row.get("handoff_state") != "manual_operator_only_placeholder":
            errors.append(f"{path}.handoff_state must be manual_operator_only_placeholder")


def _validate_redaction_confirmations(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    for index, row in enumerate(value):
        path = f"redaction_checklist_confirmations[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        for key in ("redaction_checklist_confirmation_id", "source_redaction_checklist_reference_id", "checklist_ref", "confirmation_status", "note"):
            _required_string(row.get(key), f"{path}.{key}", errors)
        if row.get("confirmation_status") != "pending_reviewer_confirmation":
            errors.append(f"{path}.confirmation_status must be pending_reviewer_confirmation")
        if row.get("required") is not True:
            errors.append(f"{path}.required must be true")


def _validate_scope_citations(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    seen: set[str] = set()
    for index, row in enumerate(value):
        path = f"read_only_surface_scope_citations[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        citation_id = _required_string(row.get("scope_citation_id"), f"{path}.scope_citation_id", errors)
        if citation_id in seen:
            errors.append(f"{path}.scope_citation_id must be unique")
        seen.add(citation_id)
        for key in ("source_candidate_id", "surface_id", "source_evidence_id", "citation_scope"):
            _required_string(row.get(key), f"{path}.{key}", errors)
        if "read_only" not in str(row.get("citation_scope") or ""):
            errors.append(f"{path}.citation_scope must be read_only")


def _validate_blocked_reminders(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    combined = " ".join(str(row.get("reminder") or "").lower() for row in value if isinstance(row, Mapping))
    for index, row in enumerate(value):
        path = f"blocked_consequential_action_reminders[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        for key in ("blocked_consequential_action_reminder_id", "reminder", "required_behavior"):
            _required_string(row.get(key), f"{path}.{key}", errors)
        if "stop" not in str(row.get("required_behavior") or "").lower() and "block" not in str(row.get("required_behavior") or "").lower():
            errors.append(f"{path}.required_behavior must stop or block the action")
    for term in ("payment", "submission", "scheduling", "cancellation", "certification", "upload"):
        if term not in combined:
            errors.append(f"blocked_consequential_action_reminders missing {term}")


def _validate_reviewer_placeholders(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    for index, row in enumerate(value):
        path = f"reviewer_approval_placeholders[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{path} must be an object")
            continue
        _required_string(row.get("reviewer_approval_placeholder_id"), f"{path}.reviewer_approval_placeholder_id", errors)
        if row.get("status") != "pending_reviewer_approval":
            errors.append(f"{path}.status must be pending_reviewer_approval")
        _required_string(row.get("note"), f"{path}.note", errors)


def _validate_commands(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        return
    if ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] not in value:
        errors.append("offline_validation_commands must include the daemon self-test command")
    for index, command in enumerate(value):
        parsed = _command(command)
        if not parsed:
            errors.append(f"offline_validation_commands[{index}] must be a non-empty string array")
            continue
        lowered = _normalize_text(" ".join(parsed))
        if any(term in lowered for term in _OFFLINE_COMMAND_DENY_TERMS):
            errors.append(f"offline_validation_commands[{index}] must stay offline")


def _validate_false_flags(value: Any, keys: Sequence[str], path: str, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{path} must be an object")
        return
    for key in keys:
        if value.get(key) is not False:
            errors.append(f"{path}.{key} must be false")
    for key, flag in value.items():
        if key not in keys and flag is not False:
            errors.append(f"{path}.{key} must be false")


def _validate_no_active_mutation_flags(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _MUTATION_KEY_TERMS and _active_flag(child):
                errors.append(f"{child_path} must be false")
            _validate_no_active_mutation_flags(child, child_path, errors)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for index, child in enumerate(value):
            _validate_no_active_mutation_flags(child, f"{path}[{index}]", errors)


def _scan_text(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, str):
        text = _normalize_text(value)
        if any(term in text for term in _PRIVATE_ARTIFACT_TERMS):
            errors.append(f"{path} contains private or browser evidence language")
        if any(term in text for term in _LIVE_ACCESS_TERMS):
            errors.append(f"{path} contains live DevHub access language")
        if not _allows_blocked_terms(path) and any(term in text for term in _BLOCKED_ACTION_TERMS):
            errors.append(f"{path} contains consequential action language outside blocked reminders")
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            _scan_text(child, f"{path}.{key}", errors)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for index, child in enumerate(value):
            _scan_text(child, f"{path}[{index}]", errors)


def _allows_blocked_terms(path: str) -> bool:
    return ".blocked_consequential_action_reminders" in path


def _require_known_ref(row: Mapping[str, Any], key: str, known_ids: set[str], path: str, errors: list[str]) -> None:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        return
    if value not in known_ids:
        errors.append(f"{path}.{key} must reference a declared preflight packet item")


def _ids(value: Any, key: str) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(row.get(key)).strip() for row in value if isinstance(row, Mapping) and str(row.get(key) or "").strip()}


def _required_string(value: Any, path: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")
        return ""
    return value.strip()


def _command(value: Any) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)) and all(isinstance(part, str) and part for part in value):
        return list(value)
    return []


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes"}
    return False


def _normalize_text(value: str) -> str:
    lowered = value.lower().replace("_", " ").replace("-", " ")
    normalized = " ".join(lowered.split())
    return normalized + " " + normalized.replace(" ", "_")
