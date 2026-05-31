"""Fixture-first guarded action preflight decision table v2.

This module is intentionally offline-only. It evaluates reversible draft preview
packet v2 data and action classification fixtures into guarded preflight
outcomes. It also validates that committed decision tables carry the required
safety metadata and do not claim private artifacts, live automation, official
completion, legal guarantees, or active surface/source/contract/release changes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

Decision = dict[str, Any]
Violation = dict[str, str]

BLOCKED_ACTION_CLASSES = {
    "account_change",
    "captcha",
    "cancellation",
    "certification",
    "mfa",
    "official_draft_save",
    "payment",
    "scheduling",
    "submission",
    "upload",
}

ALLOWED_DECISIONS = {"allow-draft", "block", "manual-handoff"}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/action_preflight_decision_table_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_action_preflight_decision_table_v2.py"],
]

REFUSED_ACTION_EXAMPLES = {
    "account_change": "Do not change DevHub profile, contact, password, or account settings.",
    "captcha": "Do not automate CAPTCHA solving or bypass challenges.",
    "cancellation": "Do not cancel an inspection, appointment, permit, application, or request.",
    "certification": "Do not certify, attest, sign, swear, or acknowledge an official statement.",
    "mfa": "Do not automate MFA enrollment, challenge handling, or recovery flows.",
    "official_draft_save": "Do not save an official draft in DevHub or another city system.",
    "payment": "Do not enter payment details, authorize charges, or submit payment.",
    "scheduling": "Do not schedule or reschedule inspections, appointments, or hearings.",
    "submission": "Do not submit, file, issue, or transmit an official application or request.",
    "upload": "Do not upload plans, documents, images, or supporting materials.",
}

FORBIDDEN_TEXT_PATTERNS = {
    "private_or_session_artifact": (
        "auth_state",
        "storage_state",
        "session_state",
        "session cookie",
        "session_storage",
        "local_storage",
        "credential",
        "password",
        "private file",
        "private_path",
        "private upload",
    ),
    "browser_artifact": (
        "screenshot",
        "trace.zip",
        "playwright trace",
        "har file",
        ".har",
        "browser artifact",
        "browser state",
    ),
    "raw_or_downloaded_artifact": (
        "raw crawl",
        "raw html",
        "raw body",
        "downloaded document",
        "downloaded pdf",
        "download path",
    ),
    "live_automation_claim": (
        "live automation completed",
        "clicked in devhub",
        "filled live devhub",
        "ran playwright",
        "opened authenticated devhub",
        "executed browser action",
    ),
    "official_completion_claim": (
        "officially completed",
        "submission completed",
        "payment completed",
        "inspection scheduled",
        "permit issued",
        "application filed",
        "uploaded to devhub",
    ),
    "legal_or_permitting_guarantee": (
        "guarantee approval",
        "guaranteed approval",
        "will be approved",
        "legally sufficient",
        "permit is valid",
        "complies with all code",
    ),
}

ACTIVE_MUTATION_FLAGS = {
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_devhub_surface_mutation",
    "active_source_mutation",
    "active_contract_mutation",
    "active_release_state_mutation",
}


def load_json_file(path: str | Path) -> dict[str, Any]:
    """Load a JSON object fixture from disk."""
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object fixture at {path}")
    return value


def evaluate_preflight_packet(packet: dict[str, Any], classifications: dict[str, Any]) -> list[Decision]:
    """Return ordered guarded preflight decisions for packet actions."""
    preview = packet.get("preview_packet", {})
    actions = packet.get("actions", [])
    if not isinstance(preview, dict):
        raise ValueError("preview_packet must be an object")
    if not isinstance(actions, list):
        raise ValueError("actions must be a list")

    classification_by_id = {
        item["action_id"]: item
        for item in classifications.get("classifications", [])
        if isinstance(item, dict) and "action_id" in item
    }

    decisions: list[Decision] = []
    for action in actions:
        if not isinstance(action, dict):
            raise ValueError("each action must be an object")
        action_id = str(action.get("action_id", ""))
        classification = classification_by_id.get(action_id, {})
        decisions.append(_decide_action(action, classification, preview))
    return decisions


def validate_preflight_decision_table_v2(decisions: Any) -> list[Violation]:
    """Return validation violations for a guarded action preflight table v2."""
    violations: list[Violation] = []
    if not isinstance(decisions, list) or not decisions:
        return [_violation("", "missing_decisions", "decision table must contain at least one decision")]

    for index, decision in enumerate(decisions):
        path = f"decisions[{index}]"
        if not isinstance(decision, dict):
            violations.append(_violation(path, "invalid_decision", "decision must be an object"))
            continue
        action_id = str(decision.get("action_id") or path)
        _validate_required_decision_fields(action_id, decision, violations)
        _validate_forbidden_content(action_id, decision, violations)
    return violations


def assert_valid_preflight_decision_table_v2(decisions: Any) -> None:
    """Raise ValueError when a guarded action preflight table v2 is unsafe."""
    violations = validate_preflight_decision_table_v2(decisions)
    if violations:
        summary = "; ".join(f"{item['action_id']}:{item['code']}" for item in violations)
        raise ValueError(f"invalid guarded action preflight decision table v2: {summary}")


def _decide_action(action: dict[str, Any], classification: dict[str, Any], preview: dict[str, Any]) -> Decision:
    action_id = str(action.get("action_id", ""))
    action_class = str(classification.get("action_class", action.get("action_class", "unknown")))
    evidence = action.get("source_evidence", [])
    selector_confidence = action.get("selector_confidence", {})
    attendance = action.get("attendance_indicators", [])

    base: Decision = {
        "action_id": action_id,
        "action_class": action_class,
        "required_attendance_indicators": attendance,
        "source_evidence_requirements": {
            "required": True,
            "present": bool(evidence),
            "minimum_items": 1,
        },
        "selector_confidence_placeholders": {
            "required": True,
            "present": bool(selector_confidence),
            "value": selector_confidence,
        },
        "preview_required": True,
        "refused_action_examples": [],
        "validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }

    if action_class in BLOCKED_ACTION_CLASSES:
        base.update(
            {
                "decision": "block",
                "reason": "blocked_action_class",
                "refused_action_examples": [REFUSED_ACTION_EXAMPLES[action_class]],
            }
        )
        return base

    preview_ok = _preview_allows_reversible_draft(preview)
    if not preview_ok:
        base.update(
            {
                "decision": "manual-handoff",
                "reason": "missing_or_unsafe_reversible_draft_preview_packet_v2",
            }
        )
        return base

    if not evidence:
        base.update({"decision": "manual-handoff", "reason": "missing_source_evidence"})
        return base

    if not selector_confidence:
        base.update({"decision": "manual-handoff", "reason": "missing_selector_confidence_placeholder"})
        return base

    if action.get("requires_attendance") and not attendance:
        base.update({"decision": "manual-handoff", "reason": "missing_required_attendance_indicator"})
        return base

    if action_class == "reversible_draft_preview":
        base.update({"decision": "allow-draft", "reason": "reversible_draft_preview_only"})
        return base

    base.update({"decision": "manual-handoff", "reason": "unrecognized_non_blocked_action_class"})
    return base


def _preview_allows_reversible_draft(preview: dict[str, Any]) -> bool:
    return (
        preview.get("packet_version") == 2
        and preview.get("reversible") is True
        and preview.get("draft_preview_only") is True
        and preview.get("executes_playwright_actions") is False
        and preview.get("opens_devhub") is False
        and preview.get("stores_browser_artifacts") is False
        and preview.get("enables_privileged_actions") is False
        and preview.get("stores_official_draft") is False
    )


def _validate_required_decision_fields(action_id: str, decision: Decision, violations: list[Violation]) -> None:
    if decision.get("decision") not in ALLOWED_DECISIONS:
        violations.append(_violation(action_id, "missing_decision", "decision must be one of the v2 outcomes"))

    attendance = decision.get("required_attendance_indicators")
    if not isinstance(attendance, list):
        violations.append(_violation(action_id, "missing_attendance_indicators", "required_attendance_indicators must be a list"))

    source_requirements = decision.get("source_evidence_requirements")
    if not _valid_source_requirements(source_requirements):
        violations.append(_violation(action_id, "missing_source_evidence_requirements", "source evidence requirements must require at least one item and record presence"))

    selector_placeholders = decision.get("selector_confidence_placeholders")
    if not _valid_selector_placeholders(selector_placeholders):
        violations.append(_violation(action_id, "missing_selector_confidence_placeholders", "selector confidence placeholders must be required and present"))

    if decision.get("preview_required") is not True:
        violations.append(_violation(action_id, "missing_preview_required_flag", "preview_required must be true"))

    refused_examples = decision.get("refused_action_examples")
    if not isinstance(refused_examples, list):
        violations.append(_violation(action_id, "missing_refused_action_examples", "refused_action_examples must be a list"))
    elif decision.get("decision") == "block" and not _non_empty_string_list(refused_examples):
        violations.append(_violation(action_id, "missing_refused_action_examples", "blocked decisions must include refused-action examples"))

    if not _valid_validation_commands(decision.get("validation_commands")):
        violations.append(_violation(action_id, "missing_validation_commands", "validation_commands must be non-empty offline command arrays"))


def _validate_forbidden_content(action_id: str, value: Any, violations: list[Violation]) -> None:
    for key, child in _walk(value):
        if key in ACTIVE_MUTATION_FLAGS and child is True:
            violations.append(_violation(action_id, "active_mutation_flag", f"{key} must not be true in preflight fixtures"))
        if isinstance(child, str):
            lowered = child.lower()
            for code, patterns in FORBIDDEN_TEXT_PATTERNS.items():
                if any(pattern in lowered for pattern in patterns):
                    violations.append(_violation(action_id, code, "decision table contains a forbidden artifact or claim"))
                    break


def _valid_source_requirements(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("required") is True
        and isinstance(value.get("present"), bool)
        and isinstance(value.get("minimum_items"), int)
        and value.get("minimum_items", 0) >= 1
    )


def _valid_selector_placeholders(value: Any) -> bool:
    if not isinstance(value, dict) or value.get("required") is not True or not isinstance(value.get("present"), bool):
        return False
    if value.get("present") is not True:
        return False
    placeholder_value = value.get("value")
    return isinstance(placeholder_value, dict) and bool(str(placeholder_value.get("placeholder", "")).strip())


def _valid_validation_commands(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for command in value:
        if not isinstance(command, list) or not command:
            return False
        if not all(isinstance(part, str) and part.strip() for part in command):
            return False
        joined = " ".join(command).lower()
        if any(token in joined for token in ("playwright", "crawl", "devhub", "browser", "download")):
            return False
    return True


def _non_empty_string_list(value: list[Any]) -> bool:
    return all(isinstance(item, str) and item.strip() for item in value) and bool(value)


def _walk(value: Any) -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            found.append((key_text, child))
            found.extend(_walk(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_walk(child))
    return found


def _violation(action_id: str, code: str, message: str) -> Violation:
    return {"action_id": action_id, "code": code, "message": message}


__all__ = [
    "BLOCKED_ACTION_CLASSES",
    "OFFLINE_VALIDATION_COMMANDS",
    "REFUSED_ACTION_EXAMPLES",
    "assert_valid_preflight_decision_table_v2",
    "evaluate_preflight_packet",
    "load_json_file",
    "validate_preflight_decision_table_v2",
]
