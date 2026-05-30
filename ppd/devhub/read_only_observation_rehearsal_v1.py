"""Fixture-first DevHub read-only observation rehearsal v1.

This module builds deterministic rehearsal artifacts from committed synthetic
DevHub surface-map and action-classification fixtures. It intentionally does not
open a browser, authenticate, click through workflows, upload files, submit
forms, schedule inspections, or pay fees.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

REHEARSAL_VERSION = "devhub-read-only-observation-rehearsal-v1"

PROHIBITED_ATTESTATIONS = {
    "no_login": "No login, account creation, password recovery, MFA, or CAPTCHA automation is performed.",
    "no_session_state": "No cookies, storage state, HAR, trace, screenshot, credential, or private session artifact is created or persisted.",
    "no_click_through": "No click-through navigation or workflow advancement is performed; fixture actions are observed as policy records only.",
    "no_upload": "No file chooser, upload control, correction upload, or document transfer is invoked.",
    "no_submit": "No application, acknowledgement, certification, correction, cancellation, or official request is submitted.",
    "no_payment": "No payment-detail entry, fee acceptance, or final payment execution is performed.",
    "no_scheduling": "No inspection scheduling, rescheduling, cancellation, or appointment confirmation is performed.",
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/devhub/read_only_observation_rehearsal_v1.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_read_only_observation_rehearsal_v1.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

READ_ONLY_ACTION_KEYWORDS = (
    "observe",
    "view",
    "read",
    "inspect",
    "review",
    "verify",
    "check status",
    "copy visible text",
)

PROHIBITED_ACTION_KEYWORDS = (
    "login",
    "sign in",
    "register",
    "create account",
    "mfa",
    "captcha",
    "click",
    "continue",
    "next",
    "save",
    "upload",
    "submit",
    "certify",
    "acknowledge",
    "pay",
    "payment",
    "schedule",
    "cancel",
    "reschedule",
)

SENSITIVE_FIELD_KEYWORDS = (
    "password",
    "credential",
    "cookie",
    "token",
    "secret",
    "ssn",
    "social security",
    "card",
    "payment",
    "bank",
    "routing",
    "account number",
    "phone",
    "email",
    "address",
    "owner",
    "applicant",
    "contractor license",
    "permit number",
)


@dataclass(frozen=True)
class FixtureSource:
    """Small citation wrapper for fixture-derived evidence."""

    fixture: str
    pointer: str

    def as_dict(self) -> dict[str, str]:
        return {"fixture": self.fixture, "pointer": self.pointer}


def load_json_fixture(path: str | Path) -> Any:
    """Load a committed JSON fixture without side effects."""

    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_read_only_observation_rehearsal(
    surface_map_fixture: str | Path,
    action_classification_fixture: str | Path,
) -> dict[str, Any]:
    """Build the DevHub read-only observation rehearsal artifact.

    The returned object is intentionally serializable and deterministic so tests
    and the daemon can validate it offline from committed fixtures.
    """

    surface_map_path = Path(surface_map_fixture)
    action_fixture_path = Path(action_classification_fixture)
    surface_map = load_json_fixture(surface_map_path)
    classifications = load_json_fixture(action_fixture_path)

    surfaces = _surface_records(surface_map)
    actions_by_surface = _actions_by_surface(classifications)

    steps: list[dict[str, Any]] = []
    for index, surface in enumerate(surfaces, start=1):
        surface_id = str(surface.get("surface_id") or surface.get("id") or f"surface-{index}")
        source = FixtureSource(surface_map_path.name, f"/surfaces/{index - 1}")
        surface_actions = actions_by_surface.get(surface_id, [])
        surface_actions.extend(_surface_embedded_actions(surface, surface_map_path.name, index - 1))
        actions = _dedupe_actions(surface_actions)

        steps.append(
            {
                "step_id": f"read-only-observe-{index:02d}",
                "surface_id": surface_id,
                "title": _surface_title(surface, surface_id),
                "read_only_instruction": _read_only_instruction(surface, actions),
                "citations": [source.as_dict()],
                "visible_ui_evidence_expectations": _visible_evidence(surface, actions),
                "redaction_requirements": _redaction_requirements(surface, actions),
                "manual_attendance_checkpoints": _manual_attendance_checkpoints(surface, actions),
                "blocked_action_evidence": _blocked_action_evidence(actions),
                "allowed_observation_evidence": _allowed_observation_evidence(actions),
                "attestations": dict(PROHIBITED_ATTESTATIONS),
            }
        )

    return {
        "rehearsal_id": REHEARSAL_VERSION,
        "version": 1,
        "mode": "fixture-first-offline-read-only",
        "input_fixtures": [surface_map_path.name, action_fixture_path.name],
        "source_policy": {
            "fixture_only": True,
            "live_crawl": False,
            "authenticated_automation": False,
            "raw_private_artifacts": False,
        },
        "steps": steps,
        "redaction_requirements": _global_redaction_requirements(steps),
        "manual_attendance_checkpoints": _global_manual_attendance_checkpoints(steps),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(PROHIBITED_ATTESTATIONS),
    }


def rehearsal_to_json(rehearsal: dict[str, Any]) -> str:
    """Serialize a rehearsal artifact with deterministic formatting."""

    return json.dumps(rehearsal, indent=2, sort_keys=True) + "\n"


def _surface_records(surface_map: Any) -> list[dict[str, Any]]:
    if isinstance(surface_map, list):
        return [item for item in surface_map if isinstance(item, dict)]
    if not isinstance(surface_map, dict):
        return []
    for key in ("surfaces", "surface_maps", "devhub_surfaces", "items"):
        value = surface_map.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    if "surface_id" in surface_map or "id" in surface_map:
        return [surface_map]
    return []


def _classification_records(classifications: Any) -> list[dict[str, Any]]:
    if isinstance(classifications, list):
        return [item for item in classifications if isinstance(item, dict)]
    if not isinstance(classifications, dict):
        return []
    for key in ("actions", "classifications", "action_classifications", "items"):
        value = classifications.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    if "action_id" in classifications or "label" in classifications:
        return [classifications]
    return []


def _actions_by_surface(classifications: Any) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for index, action in enumerate(_classification_records(classifications)):
        surface_id = str(action.get("surface_id") or action.get("surface_ref") or "unmapped")
        copied = dict(action)
        copied.setdefault("citation", {"fixture": "action-classification", "pointer": f"/actions/{index}"})
        grouped.setdefault(surface_id, []).append(copied)
    return grouped


def _surface_embedded_actions(surface: dict[str, Any], fixture_name: str, surface_index: int) -> list[dict[str, Any]]:
    actions = surface.get("actions")
    if not isinstance(actions, list):
        return []
    records: list[dict[str, Any]] = []
    for action_index, action in enumerate(actions):
        if isinstance(action, dict):
            record = dict(action)
        else:
            record = {"label": str(action)}
        record.setdefault("surface_id", surface.get("surface_id") or surface.get("id"))
        record.setdefault(
            "citation",
            {"fixture": fixture_name, "pointer": f"/surfaces/{surface_index}/actions/{action_index}"},
        )
        records.append(record)
    return records


def _dedupe_actions(actions: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for action in actions:
        action_id = str(action.get("action_id") or action.get("id") or action.get("label") or action.get("name") or "action")
        label = str(action.get("label") or action.get("name") or action_id)
        key = (action_id, label)
        if key in seen:
            continue
        seen.add(key)
        copied = dict(action)
        copied.setdefault("action_id", action_id)
        copied.setdefault("label", label)
        result.append(copied)
    return result


def _surface_title(surface: dict[str, Any], surface_id: str) -> str:
    for key in ("page_heading", "heading", "title", "name"):
        value = surface.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return surface_id


def _read_only_instruction(surface: dict[str, Any], actions: list[dict[str, Any]]) -> str:
    heading = _surface_title(surface, str(surface.get("surface_id") or surface.get("id") or "surface"))
    action_labels = ", ".join(_action_label(action) for action in actions[:4])
    if action_labels:
        return f"Observe the visible DevHub surface '{heading}' and record only whether the cited UI labels are present: {action_labels}."
    return f"Observe the visible DevHub surface '{heading}' and record only non-private page structure and public guidance text."


def _visible_evidence(surface: dict[str, Any], actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expectations: list[dict[str, Any]] = []
    for field_name in ("page_heading", "accessible_landmarks", "validation_messages", "upload_controls", "state_transitions"):
        value = surface.get(field_name)
        if value:
            expectations.append({"kind": field_name, "expected_visible_evidence": value})
    for action in actions:
        expectations.append(
            {
                "kind": "action_label",
                "expected_visible_evidence": _action_label(action),
                "classification": _classification(action),
                "citation": _action_citation(action),
            }
        )
    return expectations


def _redaction_requirements(surface: dict[str, Any], actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = [
        {
            "scope": "all_steps",
            "requirement": "Record labels, headings, and policy classifications only; redact user-entered values and private case data.",
        }
    ]
    fields = surface.get("fields")
    if isinstance(fields, list):
        for field in fields:
            label = _field_label(field)
            if _is_sensitive_text(label):
                requirements.append(
                    {
                        "scope": "field",
                        "field_label": label,
                        "requirement": "Redact the value entirely and retain only the field label and sensitivity reason.",
                    }
                )
    for action in actions:
        label = _action_label(action)
        if _is_sensitive_text(label) or _classification(action) != "read_only_observation":
            requirements.append(
                {
                    "scope": "action",
                    "action_label": label,
                    "requirement": "Do not capture resulting page values, confirmation numbers, payment details, uploaded file names, or session artifacts.",
                    "citation": _action_citation(action),
                }
            )
    return requirements


def _manual_attendance_checkpoints(surface: dict[str, Any], actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    if bool(surface.get("requires_attendance")):
        checkpoints.append(
            {
                "checkpoint": "surface_requires_attendance",
                "requirement": "A human must be present before this surface is observed in a real account-owned session.",
            }
        )
    if bool(surface.get("requires_exact_confirmation")):
        checkpoints.append(
            {
                "checkpoint": "surface_requires_exact_confirmation",
                "requirement": "Exact user confirmation is required before any consequential action beyond observation.",
            }
        )
    for action in actions:
        classification = _classification(action)
        if classification != "read_only_observation" or _has_prohibited_keyword(_action_label(action)):
            checkpoints.append(
                {
                    "checkpoint": f"manual_gate_for_{action['action_id']}",
                    "action_label": _action_label(action),
                    "classification": classification,
                    "requirement": "Stop at observation; require attended review and action-specific confirmation before any real interaction.",
                    "citation": _action_citation(action),
                }
            )
    return checkpoints


def _blocked_action_evidence(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    for action in actions:
        label = _action_label(action)
        classification = _classification(action)
        if classification != "read_only_observation" or _has_prohibited_keyword(label):
            blocked.append(
                {
                    "action_id": action["action_id"],
                    "action_label": label,
                    "classification": classification,
                    "reason": "Action is outside read-only observation or contains a prohibited workflow keyword.",
                    "citation": _action_citation(action),
                }
            )
    return blocked


def _allowed_observation_evidence(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed: list[dict[str, Any]] = []
    for action in actions:
        label = _action_label(action)
        if _classification(action) == "read_only_observation" and not _has_prohibited_keyword(label):
            allowed.append(
                {
                    "action_id": action["action_id"],
                    "action_label": label,
                    "reason": "Fixture classifies this as observation-only and no prohibited workflow keyword is present.",
                    "citation": _action_citation(action),
                }
            )
    return allowed


def _global_redaction_requirements(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for step in steps:
        for requirement in step.get("redaction_requirements", []):
            key = json.dumps(requirement, sort_keys=True)
            if key not in seen:
                seen.add(key)
                result.append(requirement)
    return result


def _global_manual_attendance_checkpoints(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    for step in steps:
        checkpoints.extend(step.get("manual_attendance_checkpoints", []))
    return checkpoints


def _field_label(field: Any) -> str:
    if isinstance(field, dict):
        for key in ("label", "name", "field_id", "id"):
            value = field.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return json.dumps(field, sort_keys=True)
    return str(field)


def _action_label(action: dict[str, Any]) -> str:
    return str(action.get("label") or action.get("name") or action.get("action_id") or "action")


def _classification(action: dict[str, Any]) -> str:
    value = action.get("classification") or action.get("action_class") or action.get("policy")
    if isinstance(value, str) and value.strip():
        return value.strip()
    label = _action_label(action).lower()
    if any(keyword in label for keyword in READ_ONLY_ACTION_KEYWORDS) and not _has_prohibited_keyword(label):
        return "read_only_observation"
    if _has_prohibited_keyword(label):
        return "consequential_action"
    return "unknown"


def _action_citation(action: dict[str, Any]) -> dict[str, str]:
    citation = action.get("citation")
    if isinstance(citation, dict):
        fixture = str(citation.get("fixture") or "action-classification")
        pointer = str(citation.get("pointer") or f"/actions/{action.get('action_id', 'unknown')}")
        return {"fixture": fixture, "pointer": pointer}
    return {"fixture": "action-classification", "pointer": f"/actions/{action.get('action_id', 'unknown')}"}


def _is_sensitive_text(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in SENSITIVE_FIELD_KEYWORDS)


def _has_prohibited_keyword(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in PROHIBITED_ACTION_KEYWORDS)
