"""Fixture-first attended DevHub observation handoff checklists.

This module consumes already-redacted read-only DevHub observation rehearsal
fixtures and action classification fixtures. It produces reviewer-ready manual
observation checklists without launching DevHub, using browser state, clicking
through controls, uploading, submitting, paying, scheduling, canceling, or
certifying official actions.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


PACKET_TYPE = "ppd.devhub.attended_observation_handoff_checklist.v1"
REQUIRED_ATTESTATIONS = (
    "no_login_automation",
    "no_session_state",
    "no_click_through",
    "no_upload",
    "no_submit",
    "no_payment",
    "no_scheduling",
)
REQUIRED_REDACTION_CHECKS = (
    "no_auth_state",
    "no_cookies",
    "no_har_or_traces",
    "no_screenshots",
    "no_raw_authenticated_values",
    "no_downloaded_documents",
)
STOP_GATE_TERMS = {
    "upload": ("upload", "attach"),
    "submit": ("submit", "submission"),
    "payment": ("pay", "payment", "fee"),
    "scheduling": ("schedule", "inspection"),
    "certification": ("certify", "acknowledge", "attest"),
    "cancellation": ("cancel", "withdraw"),
}
REQUIRED_STOP_GATES = ("upload", "submit", "payment", "scheduling")
FORBIDDEN_KEY_RE = re.compile(
    r"(auth_state|storage_state|cookie|credential|password|token|session_state|session_file|session_path|screenshot|trace|har|raw_authenticated|raw_value|download_path|upload_payload|payment_details)",
    re.IGNORECASE,
)
PRIVATE_ACCOUNT_KEY_RE = re.compile(
    r"(account_value|account_number|account_id|account_email|email_address|phone_number|display_name_value|user_name_value|permit_number_value|case_number_value)",
    re.IGNORECASE,
)
FORBIDDEN_TEXT_RE = re.compile(
    r"(/home/|/Users/|C:\\\\Users\\\\|storage[-_ ]?state|auth[-_ ]?state|session[-_ ]?state|trace\.zip|\.har\b|screenshot|raw authenticated|payment details|card number|password|cookie=|token=)",
    re.IGNORECASE,
)
LIVE_ACTION_RE = re.compile(
    r"(clicked|click through|uploaded|submitted|paid|scheduled|cancelled|canceled|certified|logged in|automated login|launched devhub|opened live devhub)",
    re.IGNORECASE,
)
OFFICIAL_ACTION_LANGUAGE_RE = re.compile(
    r"\b(upload|attach|submit|submission|certify|certification|acknowledge|payment|pay fees?|schedule|scheduling|cancel|cancellation|withdraw)\b",
    re.IGNORECASE,
)
SAFE_OFFICIAL_ACTION_CONTEXT_RE = re.compile(
    r"\b(stop before|stop observation|no |without |must not|not allowed|confirm no|consequential control|official action|stop gate|blocked)\b",
    re.IGNORECASE,
)
ACTIVE_MUTATION_KEY_RE = re.compile(
    r"(active_.*(devhub|surface|registry|guardrail|prompt|release|agent).*mutation|.*(devhub|surface_registry|surface-registry|guardrail|prompt|release_state|release-state|agent_state|agent-state).*mutation.*enabled|mutate_(devhub|surface_registry|guardrail|prompt|release_state|agent_state))",
    re.IGNORECASE,
)
ACTIVE_MUTATION_TEXT_RE = re.compile(
    r"\b(active devhub mutation|active surface-registry mutation|active surface registry mutation|active guardrail mutation|active prompt mutation|active release-state mutation|active agent-state mutation|mutate devhub|mutate surface registry|mutate guardrail|mutate prompt|mutate release state|mutate agent state)\b",
    re.IGNORECASE,
)
WRITE_CAPABLE_KEY_RE = re.compile(r"(write_capable|write_enabled|can_write|allows_write|execute_write|mutation_enabled)", re.IGNORECASE)


def load_json_object(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("fixture must contain a JSON object")
    return data


def build_attended_observation_handoff_checklist(
    observation_rehearsal: Mapping[str, Any],
    action_classification: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic manual observation checklist packet."""

    surfaces = _observation_surfaces(observation_rehearsal)
    actions = _classification_actions(action_classification)
    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": "attended-devhub-observation-handoff-checklist-v1-fixture",
        "fixture_first": True,
        "offline_only": True,
        "devhub_launched": False,
        "browser_automation_performed": False,
        "source_packets": {
            "devhub_read_only_observation_rehearsal_v1": {
                "consumed": True,
                "fixture_id": _text(observation_rehearsal.get("fixture_id") or observation_rehearsal.get("observation_id")),
            },
            "action_classification_fixture": {
                "consumed": True,
                "fixture_id": _text(action_classification.get("fixture_id")),
            },
        },
        "manual_observation_checklists": [_surface_checklist(surface) for surface in surfaces],
        "visible_ui_evidence_expectations": _visible_ui_evidence(surfaces),
        "redaction_checks": _redaction_checks(),
        "attendance_checkpoints": _attendance_checkpoints(surfaces),
        "stop_before_action_gates": _stop_gates(actions),
        "rollback_notes": [
            {
                "note_id": "rollback-close-review-only-session",
                "manual_only": True,
                "note": "If the reviewer sees a consequential control, stop observation and close the attended browser without saving or confirming any official action.",
            },
            {
                "note_id": "rollback-discard-local-packet",
                "manual_only": True,
                "note": "Discard the generated checklist packet if any private value, browser artifact, upload path, payment detail, or unredacted account data is found.",
            },
        ],
        "offline_validation_commands": [
            ["python3", "-m", "py_compile", "ppd/devhub/attended_observation_handoff_checklist_v1.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_attended_observation_handoff_checklist_v1.py"],
        ],
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }
    assert_valid_attended_observation_handoff_checklist(packet)
    return packet


def validate_attended_observation_handoff_checklist(packet: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    for field in ("fixture_first", "offline_only"):
        if packet.get(field) is not True:
            errors.append(f"{field} must be true")
    for field in ("devhub_launched", "browser_automation_performed"):
        if packet.get(field) is not False:
            errors.append(f"{field} must be false")

    sources = _mapping(packet.get("source_packets"))
    for key in ("devhub_read_only_observation_rehearsal_v1", "action_classification_fixture"):
        source = _mapping(sources.get(key))
        if source.get("consumed") is not True:
            errors.append(f"source_packets.{key}.consumed must be true")
        if not _text(source.get("fixture_id")):
            errors.append(f"source_packets.{key}.fixture_id is required")

    _require_sequence(errors, packet, "manual_observation_checklists")
    _require_sequence(errors, packet, "visible_ui_evidence_expectations")
    _require_sequence(errors, packet, "redaction_checks")
    _require_sequence(errors, packet, "attendance_checkpoints")
    _require_sequence(errors, packet, "stop_before_action_gates")
    _require_sequence(errors, packet, "rollback_notes")
    _require_sequence(errors, packet, "offline_validation_commands")

    redaction_ids = {_text(item.get("check_id")) for item in _sequence(packet.get("redaction_checks")) if isinstance(item, Mapping)}
    for check_id in REQUIRED_REDACTION_CHECKS:
        if check_id not in redaction_ids:
            errors.append(f"redaction_checks missing {check_id}")

    for index, item in enumerate(_sequence(packet.get("visible_ui_evidence_expectations"))):
        row = _mapping(item)
        prefix = f"visible_ui_evidence_expectations[{index}]"
        if not _text(row.get("surface_id")):
            errors.append(f"{prefix}.surface_id is required")
        if not _text_list(row.get("expected_visible_labels")):
            errors.append(f"{prefix}.expected_visible_labels must be non-empty")
        if row.get("requires_screenshot") is not False:
            errors.append(f"{prefix}.requires_screenshot must be false")
        if row.get("raw_values_allowed") is not False:
            errors.append(f"{prefix}.raw_values_allowed must be false")

    for index, item in enumerate(_sequence(packet.get("attendance_checkpoints"))):
        row = _mapping(item)
        prefix = f"attendance_checkpoints[{index}]"
        if row.get("reviewer_present") is not True:
            errors.append(f"{prefix}.reviewer_present must be true")
        if row.get("manual_login_only") is not True:
            errors.append(f"{prefix}.manual_login_only must be true")
        if row.get("automates_login") is not False:
            errors.append(f"{prefix}.automates_login must be false")

    gates = _sequence(packet.get("stop_before_action_gates"))
    gate_text = " ".join(_text(gate.get("action_kind")) for gate in gates if isinstance(gate, Mapping)).lower()
    for required in REQUIRED_STOP_GATES:
        if required not in gate_text:
            errors.append(f"stop_before_action_gates must cover {required}")
    for index, item in enumerate(gates):
        row = _mapping(item)
        prefix = f"stop_before_action_gates[{index}]"
        if row.get("stop_before_action") is not True:
            errors.append(f"{prefix}.stop_before_action must be true")
        if row.get("automated_execution_allowed") is not False:
            errors.append(f"{prefix}.automated_execution_allowed must be false")
        if row.get("requires_attendance") is not True:
            errors.append(f"{prefix}.requires_attendance must be true")
        if row.get("requires_exact_confirmation") is not True:
            errors.append(f"{prefix}.requires_exact_confirmation must be true")

    attestations = _mapping(packet.get("attestations"))
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            errors.append(f"attestations.{key} must be true")

    _scan_forbidden(packet, "$", errors)
    return tuple(errors)


def assert_valid_attended_observation_handoff_checklist(packet: Mapping[str, Any]) -> None:
    errors = validate_attended_observation_handoff_checklist(packet)
    if errors:
        raise AssertionError("; ".join(errors))


def _surface_checklist(surface: Mapping[str, Any]) -> dict[str, Any]:
    surface_id = _text(surface.get("surface_id")) or "unknown-surface"
    return {
        "checklist_id": f"manual-observe-{surface_id}",
        "surface_id": surface_id,
        "manual_only": True,
        "reviewer_ready": True,
        "items": [
            "Confirm only visible headings, labels, landmarks, and redacted field categories are reviewed.",
            "Confirm no private value, screenshot, trace, HAR, auth state, cookie, or downloaded document is captured.",
            "Stop before any control that would upload, submit, certify, pay, schedule, cancel, or change an official record.",
        ],
    }


def _visible_ui_evidence(surfaces: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for surface in surfaces:
        labels = [_text(surface.get("page_heading"))]
        labels.extend(_text(action.get("label") or action.get("action_id")) for action in _sequence(surface.get("actions")) if isinstance(action, Mapping))
        labels.extend(_text(field.get("label") or field.get("field_id")) for field in _sequence(surface.get("fields")) if isinstance(field, Mapping))
        rows.append(
            {
                "surface_id": _text(surface.get("surface_id")) or "unknown-surface",
                "expected_visible_labels": [label for label in labels if label][:6],
                "requires_screenshot": False,
                "raw_values_allowed": False,
                "reviewer_evidence_note": "Reviewer confirms visible UI labels from the attended screen; committed packet stores labels and redaction states only.",
            }
        )
    return rows


def _redaction_checks() -> list[dict[str, Any]]:
    return [
        {"check_id": check_id, "required": True, "allowed": False, "reviewer_must_confirm_absent": True}
        for check_id in REQUIRED_REDACTION_CHECKS
    ]


def _attendance_checkpoints(surfaces: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "checkpoint_id": "attendance-before-" + (_text(surface.get("surface_id")) or "unknown-surface"),
            "surface_id": _text(surface.get("surface_id")) or "unknown-surface",
            "reviewer_present": True,
            "manual_login_only": True,
            "automates_login": False,
            "stop_if_user_absent": True,
        }
        for surface in surfaces
    ]


def _stop_gates(actions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    for action in actions:
        text = (_text(action.get("action_id")) + " " + _text(action.get("label")) + " " + _text(action.get("classification"))).lower()
        for kind, terms in STOP_GATE_TERMS.items():
            if any(term in text for term in terms):
                gates.append(
                    {
                        "gate_id": "stop-before-" + (_text(action.get("action_id")) or kind),
                        "action_kind": kind,
                        "action_id": _text(action.get("action_id")) or kind,
                        "classification": _text(action.get("classification")) or "consequential_or_financial",
                        "stop_before_action": True,
                        "requires_attendance": True,
                        "requires_exact_confirmation": True,
                        "automated_execution_allowed": False,
                    }
                )
                break
    existing = {_text(gate.get("action_kind")) for gate in gates}
    for required in REQUIRED_STOP_GATES:
        if required not in existing:
            gates.append(
                {
                    "gate_id": f"stop-before-{required}",
                    "action_kind": required,
                    "action_id": required,
                    "classification": "required_stop_gate",
                    "stop_before_action": True,
                    "requires_attendance": True,
                    "requires_exact_confirmation": True,
                    "automated_execution_allowed": False,
                }
            )
    return gates


def _observation_surfaces(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    surfaces = packet.get("observed_surfaces") or packet.get("observations") or packet.get("surfaces") or []
    return [item for item in _sequence(surfaces) if isinstance(item, Mapping)] or [{"surface_id": "manual-devhub-observation", "page_heading": "DevHub attended observation"}]


def _classification_actions(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    candidates: list[Mapping[str, Any]] = []
    for key in ("actions", "classified_actions", "decision_cases", "stop_gates"):
        candidates.extend(item for item in _sequence(packet.get(key)) if isinstance(item, Mapping))
    for surface in _sequence(packet.get("surfaces")):
        if isinstance(surface, Mapping):
            candidates.extend(item for item in _sequence(surface.get("actions")) if isinstance(item, Mapping))
    return candidates


def _scan_forbidden(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if FORBIDDEN_KEY_RE.search(key_text) and child not in (False, None, "[NOT_STORED]", "[REDACTED]"):
                errors.append(f"{child_path} contains forbidden private/browser artifact field")
            if PRIVATE_ACCOUNT_KEY_RE.search(key_text) and child not in (False, None, "", "[REDACTED]", "[NOT_STORED]"):
                errors.append(f"{child_path} contains forbidden private account value")
            if ACTIVE_MUTATION_KEY_RE.search(key_text) and _truthy_or_nonempty(child):
                errors.append(f"{child_path} contains active DevHub, surface-registry, guardrail, prompt, release-state, or agent-state mutation flag")
            if WRITE_CAPABLE_KEY_RE.search(key_text) and child not in (False, None, "", "blocked", "not_allowed"):
                errors.append(f"{child_path} contains write-capable action flag")
            _scan_forbidden(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        if FORBIDDEN_TEXT_RE.search(value):
            errors.append(f"{path} contains forbidden private/browser artifact text")
        if LIVE_ACTION_RE.search(value):
            errors.append(f"{path} claims live login, click-through, upload, submit, payment, scheduling, cancellation, certification, or DevHub execution")
        if ACTIVE_MUTATION_TEXT_RE.search(value):
            errors.append(f"{path} contains active DevHub, surface-registry, guardrail, prompt, release-state, or agent-state mutation text")
        if OFFICIAL_ACTION_LANGUAGE_RE.search(value) and not _official_action_language_is_safe(path, value):
            errors.append(f"{path} contains unsafe certification, submission, payment, upload, scheduling, or cancellation language")


def _official_action_language_is_safe(path: str, value: str) -> bool:
    if ".stop_before_action_gates" in path:
        return True
    if ".attestations." in path:
        return True
    if SAFE_OFFICIAL_ACTION_CONTEXT_RE.search(value):
        return True
    return False


def _truthy_or_nonempty(value: Any) -> bool:
    if value in (False, None, "", [], {}):
        return False
    return True


def _require_sequence(errors: list[str], packet: Mapping[str, Any], key: str) -> None:
    if not _sequence(packet.get(key)):
        errors.append(f"{key} must be non-empty")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _text_list(value: Any) -> list[str]:
    return [_text(item) for item in _sequence(value) if _text(item)]
