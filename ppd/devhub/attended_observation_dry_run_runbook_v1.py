"""Fixture-first attended DevHub observation dry-run runbook v1.

This module converts an already-redacted attended observation handoff checklist
into reviewer-ready dry-run steps. It is deterministic and side-effect free: it
never launches DevHub, stores session state, creates accounts, solves CAPTCHA or
MFA, clicks through consequential controls, uploads, submits, pays, or schedules.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.devhub.attended_observation_handoff_checklist_v1 import (
    validate_attended_observation_handoff_checklist,
)


PACKET_TYPE = "ppd.devhub.attended_observation_dry_run_runbook.v1"
SOURCE_PACKET_TYPE = "ppd.devhub.attended_observation_handoff_checklist.v1"
REQUIRED_ATTESTATIONS = (
    "no_captcha_automation",
    "no_mfa_automation",
    "no_account_creation",
    "no_click_through",
    "no_session_state",
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
    "no_private_file_paths",
    "no_payment_details",
)
REQUIRED_STOP_GATE_KINDS = (
    "captcha",
    "mfa",
    "account_creation",
    "click_through",
    "upload",
    "submit",
    "payment",
    "scheduling",
    "certification",
    "cancellation",
)
FORBIDDEN_KEY_RE = re.compile(
    r"(auth_state|storage_state|cookie|credential|password|token|session_state|session_file|session_path|screenshot|trace|har|raw_authenticated|raw_value|download_path|upload_payload|payment_details|card_number)",
    re.IGNORECASE,
)
FORBIDDEN_TEXT_RE = re.compile(
    r"(/home/|/Users/|C:\\\\Users\\\\|storage[-_ ]?state|auth[-_ ]?state|session[-_ ]?state|trace\.zip|\.har\b|screenshot|raw authenticated|payment details|card number|password|cookie=|token=)",
    re.IGNORECASE,
)
LIVE_ACTION_RE = re.compile(
    r"(automated login|solved captcha|completed mfa|created account|clicked through|uploaded|submitted|paid|scheduled|cancelled|canceled|certified|stored session|saved session)",
    re.IGNORECASE,
)


class AttendedObservationDryRunRunbookError(ValueError):
    """Raised when the dry-run runbook is unsafe or incomplete."""


@dataclass(frozen=True)
class AttendedObservationDryRunRunbookResult:
    runbook_id: str
    step_count: int
    stop_gate_count: int
    redaction_check_count: int
    attestation_count: int


def load_runbook(path: str | Path) -> Mapping[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AttendedObservationDryRunRunbookError("runbook fixture must contain a JSON object")
    return data


def validate_runbook_file(path: str | Path) -> AttendedObservationDryRunRunbookResult:
    return validate_runbook(load_runbook(path))


def build_runbook_from_handoff_checklist(checklist: Mapping[str, Any]) -> dict[str, Any]:
    checklist_errors = validate_attended_observation_handoff_checklist(checklist)
    if checklist_errors:
        raise AttendedObservationDryRunRunbookError("handoff checklist is invalid: " + "; ".join(checklist_errors))

    source_packet_id = _required_text(checklist, "packet_id")
    manual_checklists = _required_list(checklist, "manual_observation_checklists")
    evidence_expectations = _required_list(checklist, "visible_ui_evidence_expectations")
    checklist_stop_gates = _required_list(checklist, "stop_before_action_gates")

    runbook = {
        "packet_type": PACKET_TYPE,
        "runbook_id": "fixture-first-attended-devhub-observation-dry-run-runbook-v1",
        "source_handoff_checklist": {
            "packet_type": SOURCE_PACKET_TYPE,
            "packet_id": source_packet_id,
            "converted_fixture_first": True,
        },
        "fixture_first": True,
        "offline_only": True,
        "live_devhub_session": False,
        "browser_launched": False,
        "browser_automation_performed": False,
        "auth_state_saved": False,
        "manual_login_boundaries": {
            "reviewer_attends_login": True,
            "manual_login_only": True,
            "automation_may_enter_credentials": False,
            "automation_may_handle_captcha": False,
            "automation_may_handle_mfa": False,
            "automation_may_create_account": False,
            "stop_if_reviewer_absent": True,
        },
        "dry_run_steps": _dry_run_steps(manual_checklists, evidence_expectations),
        "read_only_page_evidence_expectations": _read_only_evidence(evidence_expectations),
        "redaction_checklist": _redaction_checklist(checklist),
        "stop_before_action_gates": _stop_before_action_gates(checklist_stop_gates),
        "rollback_notes": _rollback_notes(checklist),
        "offline_validation_commands": [
            ["python3", "-m", "py_compile", "ppd/devhub/attended_observation_dry_run_runbook_v1.py"],
            ["python3", "-m", "pytest", "ppd/tests/test_attended_observation_dry_run_runbook_v1.py"],
        ],
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }
    validate_runbook(runbook)
    return runbook


def validate_runbook(runbook: Mapping[str, Any]) -> AttendedObservationDryRunRunbookResult:
    errors: list[str] = []
    if runbook.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    for field in ("fixture_first", "offline_only"):
        if runbook.get(field) is not True:
            errors.append(f"{field} must be true")
    for field in ("live_devhub_session", "browser_launched", "browser_automation_performed", "auth_state_saved"):
        if runbook.get(field) is not False:
            errors.append(f"{field} must be false")

    source = _mapping(runbook.get("source_handoff_checklist"))
    if source.get("packet_type") != SOURCE_PACKET_TYPE:
        errors.append(f"source_handoff_checklist.packet_type must be {SOURCE_PACKET_TYPE}")
    if source.get("converted_fixture_first") is not True:
        errors.append("source_handoff_checklist.converted_fixture_first must be true")
    if not _text(source.get("packet_id")):
        errors.append("source_handoff_checklist.packet_id is required")

    boundaries = _mapping(runbook.get("manual_login_boundaries"))
    for key in ("reviewer_attends_login", "manual_login_only", "stop_if_reviewer_absent"):
        if boundaries.get(key) is not True:
            errors.append(f"manual_login_boundaries.{key} must be true")
    for key in ("automation_may_enter_credentials", "automation_may_handle_captcha", "automation_may_handle_mfa", "automation_may_create_account"):
        if boundaries.get(key) is not False:
            errors.append(f"manual_login_boundaries.{key} must be false")

    steps = _sequence(runbook.get("dry_run_steps"))
    evidence = _sequence(runbook.get("read_only_page_evidence_expectations"))
    redactions = _sequence(runbook.get("redaction_checklist"))
    gates = _sequence(runbook.get("stop_before_action_gates"))
    rollback_notes = _sequence(runbook.get("rollback_notes"))
    commands = _sequence(runbook.get("offline_validation_commands"))

    for key, value in (
        ("dry_run_steps", steps),
        ("read_only_page_evidence_expectations", evidence),
        ("redaction_checklist", redactions),
        ("stop_before_action_gates", gates),
        ("rollback_notes", rollback_notes),
        ("offline_validation_commands", commands),
    ):
        if not value:
            errors.append(f"{key} must be non-empty")

    for index, step in enumerate(steps):
        row = _mapping(step)
        prefix = f"dry_run_steps[{index}]"
        if not _text(row.get("step_id")):
            errors.append(f"{prefix}.step_id is required")
        if row.get("manual_only") is not True:
            errors.append(f"{prefix}.manual_only must be true")
        if row.get("may_touch_live_devhub") is not False:
            errors.append(f"{prefix}.may_touch_live_devhub must be false")
        if row.get("may_change_official_state") is not False:
            errors.append(f"{prefix}.may_change_official_state must be false")
        if not _text_list(row.get("reviewer_actions")):
            errors.append(f"{prefix}.reviewer_actions must be non-empty")

    for index, item in enumerate(evidence):
        row = _mapping(item)
        prefix = f"read_only_page_evidence_expectations[{index}]"
        if not _text(row.get("surface_id")):
            errors.append(f"{prefix}.surface_id is required")
        if row.get("read_only_only") is not True:
            errors.append(f"{prefix}.read_only_only must be true")
        if row.get("raw_values_allowed") is not False:
            errors.append(f"{prefix}.raw_values_allowed must be false")
        if row.get("screenshots_allowed") is not False:
            errors.append(f"{prefix}.screenshots_allowed must be false")
        if not _text_list(row.get("expected_visible_labels")):
            errors.append(f"{prefix}.expected_visible_labels must be non-empty")

    redaction_ids = {_text(_mapping(item).get("check_id")) for item in redactions}
    for check_id in REQUIRED_REDACTION_CHECKS:
        if check_id not in redaction_ids:
            errors.append(f"redaction_checklist missing {check_id}")
    for index, item in enumerate(redactions):
        row = _mapping(item)
        if row.get("must_be_absent") is not True or row.get("commit_safe") is not True:
            errors.append(f"redaction_checklist[{index}] must be absent and commit safe")

    gate_kinds = {_text(_mapping(item).get("action_kind")) for item in gates}
    for action_kind in REQUIRED_STOP_GATE_KINDS:
        if action_kind not in gate_kinds:
            errors.append(f"stop_before_action_gates missing {action_kind}")
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

    attestations = _mapping(runbook.get("attestations"))
    for attestation in REQUIRED_ATTESTATIONS:
        if attestations.get(attestation) is not True:
            errors.append(f"attestations.{attestation} must be true")

    _scan_forbidden(runbook, "$", errors)
    if errors:
        raise AttendedObservationDryRunRunbookError("; ".join(errors))

    return AttendedObservationDryRunRunbookResult(
        runbook_id=_required_text(runbook, "runbook_id"),
        step_count=len(steps),
        stop_gate_count=len(gates),
        redaction_check_count=len(redactions),
        attestation_count=len(attestations),
    )


def _dry_run_steps(manual_checklists: Sequence[Any], evidence_expectations: Sequence[Any]) -> list[dict[str, Any]]:
    surface_ids = [_text(_mapping(item).get("surface_id")) for item in evidence_expectations]
    steps: list[dict[str, Any]] = [
        {
            "step_id": "prepare-fixture-packet",
            "sequence": 1,
            "manual_only": True,
            "may_touch_live_devhub": False,
            "may_change_official_state": False,
            "reviewer_actions": [
                "Open the committed handoff checklist fixture and this runbook fixture.",
                "Confirm the dry run is fixture-first and offline before any attended browser work is considered.",
            ],
            "expected_evidence": ["Checklist packet id", "Runbook packet id", "Offline-only flags"],
        },
        {
            "step_id": "manual-login-boundary-review",
            "sequence": 2,
            "manual_only": True,
            "may_touch_live_devhub": False,
            "may_change_official_state": False,
            "reviewer_actions": [
                "Confirm any future DevHub login is performed by the reviewer only.",
                "Confirm automation does not enter credentials, solve CAPTCHA, complete MFA, create accounts, or store session state.",
            ],
            "expected_evidence": ["Manual login boundary", "No session-state attestation"],
        },
    ]
    sequence = 3
    for checklist in manual_checklists:
        row = _mapping(checklist)
        surface_id = _text(row.get("surface_id")) or "unknown-surface"
        steps.append(
            {
                "step_id": f"observe-read-only-{surface_id}",
                "sequence": sequence,
                "surface_id": surface_id,
                "manual_only": True,
                "may_touch_live_devhub": False,
                "may_change_official_state": False,
                "reviewer_actions": [
                    "Review only headings, labels, landmarks, and redacted field categories listed in the fixture.",
                    "Record pass or fail against expected labels without retaining raw page values.",
                    "Stop before any consequential, financial, upload, scheduling, certification, cancellation, or account-control action.",
                ],
                "expected_evidence": ["Visible labels", "Redaction states", "Stop-before-action check"],
            }
        )
        sequence += 1
    steps.append(
        {
            "step_id": "final-redaction-and-rollback-review",
            "sequence": sequence,
            "manual_only": True,
            "may_touch_live_devhub": False,
            "may_change_official_state": False,
            "surface_ids_reviewed": [surface_id for surface_id in surface_ids if surface_id],
            "reviewer_actions": [
                "Confirm no private values, browser artifacts, screenshots, downloaded documents, payment details, or private file paths are present.",
                "Apply rollback notes if any evidence item fails redaction or stop-gate review.",
            ],
            "expected_evidence": ["Redaction checklist complete", "Rollback decision"],
        }
    )
    return steps


def _read_only_evidence(evidence_expectations: Sequence[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in evidence_expectations:
        row = _mapping(item)
        rows.append(
            {
                "surface_id": _text(row.get("surface_id")) or "unknown-surface",
                "read_only_only": True,
                "expected_visible_labels": _text_list(row.get("expected_visible_labels")),
                "raw_values_allowed": False,
                "screenshots_allowed": False,
                "page_evidence_allowed": ["visible_heading", "visible_label", "accessible_landmark", "redacted_field_category"],
                "page_evidence_disallowed": ["raw_account_value", "permit_number_value", "session_state", "screenshot", "downloaded_document"],
            }
        )
    return rows


def _redaction_checklist(checklist: Mapping[str, Any]) -> list[dict[str, Any]]:
    existing = {_text(_mapping(item).get("check_id")) for item in _sequence(checklist.get("redaction_checks"))}
    ordered = list(REQUIRED_REDACTION_CHECKS)
    for check_id in sorted(existing - set(ordered)):
        if check_id:
            ordered.append(check_id)
    return [
        {
            "check_id": check_id,
            "must_be_absent": True,
            "commit_safe": True,
            "reviewer_action": "Confirm this artifact or value class is absent from committed dry-run evidence.",
        }
        for check_id in ordered
    ]


def _stop_before_action_gates(checklist_stop_gates: Sequence[Any]) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in checklist_stop_gates:
        row = _mapping(item)
        action_kind = _text(row.get("action_kind"))
        if action_kind:
            seen.add(action_kind)
            gates.append(_gate(action_kind, _text(row.get("action_id")) or action_kind, _text(row.get("classification")) or "handoff_stop_gate"))
    for action_kind in REQUIRED_STOP_GATE_KINDS:
        if action_kind not in seen:
            gates.append(_gate(action_kind, action_kind, "required_attended_dry_run_stop_gate"))
    return gates


def _gate(action_kind: str, action_id: str, classification: str) -> dict[str, Any]:
    return {
        "gate_id": f"stop-before-{action_id}",
        "action_kind": action_kind,
        "action_id": action_id,
        "classification": classification,
        "stop_before_action": True,
        "requires_attendance": True,
        "requires_exact_confirmation": True,
        "automated_execution_allowed": False,
        "reviewer_instruction": "Stop the dry run before this action and require a separate attended handoff with exact user confirmation.",
    }


def _rollback_notes(checklist: Mapping[str, Any]) -> list[dict[str, Any]]:
    notes = [
        {
            "note_id": "rollback-close-attended-browser",
            "manual_only": True,
            "commit_safe": True,
            "note": "If a consequential or financial control is reached, stop observation and close the attended browser without saving or confirming any official action.",
        },
        {
            "note_id": "rollback-discard-redaction-failure",
            "manual_only": True,
            "commit_safe": True,
            "note": "Discard the dry-run packet if it contains a private value, browser artifact, downloaded document, payment detail, upload path, or private file path.",
        },
    ]
    for item in _sequence(checklist.get("rollback_notes")):
        row = _mapping(item)
        note_id = _text(row.get("note_id"))
        if note_id and note_id not in {note["note_id"] for note in notes}:
            notes.append(
                {
                    "note_id": note_id,
                    "manual_only": True,
                    "commit_safe": True,
                    "note": _text(row.get("note")) or "Follow the source checklist rollback note.",
                }
            )
    return notes


def _scan_forbidden(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if FORBIDDEN_KEY_RE.search(str(key)) and child not in (False, None, "", "[REDACTED]", "[NOT_STORED]"):
                errors.append(f"{child_path} contains forbidden private/browser artifact field")
            _scan_forbidden(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        if FORBIDDEN_TEXT_RE.search(value):
            errors.append(f"{path} contains forbidden private/browser artifact text")
        if LIVE_ACTION_RE.search(value):
            errors.append(f"{path} claims forbidden live automation or consequential action")


def _required_mapping(mapping: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AttendedObservationDryRunRunbookError(f"{key} must be an object")
    return value


def _required_list(mapping: Mapping[str, Any], key: str) -> Sequence[Any]:
    value = mapping.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)) or not value:
        raise AttendedObservationDryRunRunbookError(f"{key} must be a non-empty list")
    return value


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = _text(mapping.get(key))
    if not value:
        raise AttendedObservationDryRunRunbookError(f"{key} is required")
    return value


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
