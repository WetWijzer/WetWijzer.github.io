"""Validation for reversible DevHub draft executor dry-run packets.

The checks in this module are intentionally deterministic and side-effect free.
They validate packet-shaped dictionaries before any Playwright page, browser
state, upload control, payment control, or official DevHub action can be used.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any


MIN_SELECTOR_CONFIDENCE = 0.85

PRIVATE_VALUE_KEYS = {
    "account_number",
    "bank_account",
    "card_number",
    "credential",
    "credentials",
    "credit_card",
    "cvc",
    "cvv",
    "date_of_birth",
    "dob",
    "field_value",
    "password",
    "payment_details",
    "private_value",
    "raw_private_value",
    "routing_number",
    "secret",
    "security_answer",
    "social_security_number",
    "ssn",
    "token",
    "value",
}

BROWSER_ARTIFACT_KEYS = {
    "browser_context",
    "browser_state",
    "cookie",
    "cookie_jar",
    "cookies",
    "har",
    "har_data",
    "har_path",
    "network_har",
    "screenshot",
    "screenshot_path",
    "screenshots",
    "session_state",
    "storage_state",
    "trace",
    "trace_path",
    "traces",
}

CONSEQUENTIAL_CONTROL_WORDS = {
    "certify",
    "continue",
    "pay",
    "payment",
    "save",
    "schedule",
    "submit",
    "upload",
}

CONSEQUENTIAL_ACTIONS = {
    "accept_certification",
    "attach_document",
    "book_inspection",
    "certify",
    "continue",
    "continue_application",
    "continue_draft",
    "enter_card",
    "enter_payment_details",
    "official_attach",
    "official_upload",
    "pay_fee",
    "purchase_trade_permit",
    "save",
    "save_and_continue",
    "save_draft",
    "schedule",
    "schedule_inspection",
    "sign_certification",
    "submit",
    "submit_application",
    "submit_payment",
    "submit_permit_request",
    "upload",
    "upload_correction",
}

OFFICIAL_STATE_CLAIM_KEYS = {
    "changes_official_state",
    "devhub_state_changed",
    "made_official_change",
    "official_devhub_state_changed",
    "official_record_changed",
    "official_state_change",
    "official_state_changed",
    "state_changed",
}

STATE_CHANGED_WORDS = {"changed", "submitted", "saved", "uploaded", "scheduled", "paid", "certified"}

GENERIC_SELECTORS = {"a", "button", "input", "select", "textarea", "[role=button]"}


@dataclass(frozen=True)
class DryRunPacketIssue:
    code: str
    message: str
    location: str


def validate_dry_run_packet(packet: Mapping[str, Any]) -> list[DryRunPacketIssue]:
    """Return all safety issues found in a reversible draft dry-run packet."""

    issues: list[DryRunPacketIssue] = []
    facts = _fact_provenance(packet, issues)
    steps = _sequence(packet.get("steps") or packet.get("actions") or packet.get("ordered_steps"))
    if not steps:
        issues.append(DryRunPacketIssue("missing_steps", "Dry-run packets must contain ordered reversible steps.", "steps"))

    for index, step in enumerate(steps):
        location = f"steps[{index}]"
        if not isinstance(step, Mapping):
            issues.append(DryRunPacketIssue("invalid_step", "Each dry-run step must be an object.", location))
            continue
        issues.extend(_step_issues(step, location, facts))

    for location, value in _walk(packet):
        key = _normalized_key(location.rsplit(".", 1)[-1])
        if key in PRIVATE_VALUE_KEYS and _present(value):
            issues.append(DryRunPacketIssue("private_value", "Dry-run packets must reference user fact IDs, not private values.", location))
        if key in BROWSER_ARTIFACT_KEYS and _present(value):
            issues.append(DryRunPacketIssue("browser_artifact", "Browser state, screenshots, traces, HAR data, and cookies are not commit-safe dry-run data.", location))
        if key in OFFICIAL_STATE_CLAIM_KEYS and value is True:
            issues.append(DryRunPacketIssue("official_state_changed", "A reversible dry-run packet must not claim official DevHub state changed.", location))
        if key in {"state_change_result", "result", "outcome"} and isinstance(value, str):
            if _normalized_key(value) in STATE_CHANGED_WORDS:
                issues.append(DryRunPacketIssue("official_state_changed", "Dry-run outcomes must not claim official DevHub state changed.", location))

    return _dedupe(issues)


def assert_dry_run_packet(packet: Mapping[str, Any]) -> None:
    issues = validate_dry_run_packet(packet)
    if issues:
        detail = "; ".join(f"{issue.code} at {issue.location}" for issue in issues)
        raise ValueError(f"Invalid reversible DevHub draft executor dry-run packet: {detail}")


def _fact_provenance(packet: Mapping[str, Any], issues: list[DryRunPacketIssue]) -> set[str]:
    facts = _sequence(packet.get("required_user_facts") or packet.get("facts"))
    fact_ids: set[str] = set()
    if not facts:
        issues.append(DryRunPacketIssue("missing_fact_provenance", "Dry-run packets must include source-backed user fact provenance.", "required_user_facts"))
        return fact_ids
    for index, fact in enumerate(facts):
        location = f"required_user_facts[{index}]"
        if not isinstance(fact, Mapping):
            issues.append(DryRunPacketIssue("missing_fact_provenance", "Each required user fact must be an object with provenance.", location))
            continue
        fact_id = _text(fact.get("fact_id") or fact.get("id") or fact.get("user_fact_id"))
        if fact_id:
            fact_ids.add(fact_id)
        evidence = _sequence(fact.get("source_evidence_ids"))
        provenance = fact.get("provenance")
        if not evidence and isinstance(provenance, Mapping):
            evidence = _sequence(provenance.get("source_evidence_ids"))
        if not fact_id or not evidence or any(not _text(item) for item in evidence):
            issues.append(DryRunPacketIssue("missing_fact_provenance", "Each required user fact must cite source_evidence_ids.", location))
    return fact_ids


def _step_issues(step: Mapping[str, Any], location: str, facts: set[str]) -> list[DryRunPacketIssue]:
    issues: list[DryRunPacketIssue] = []
    action = _normalized_key(step.get("action") or step.get("action_type") or step.get("kind"))
    if action in CONSEQUENTIAL_ACTIONS:
        issues.append(DryRunPacketIssue("consequential_control", "Save, continue, submit, certify, upload, payment, and schedule controls are not reversible dry-run actions.", f"{location}.action"))
    for key in ("label", "button_text", "aria_label", "control_text", "description", "selector"):
        text = _normalized_key(step.get(key))
        if any(word in text.split("_") or word in text for word in CONSEQUENTIAL_CONTROL_WORDS):
            issues.append(DryRunPacketIssue("consequential_control", "Consequential DevHub controls must be blocked before dry-run execution.", f"{location}.{key}"))
    selector_issue = _selector_issue(step)
    if selector_issue:
        issues.append(DryRunPacketIssue("low_confidence_selector", selector_issue, f"{location}.selector"))
    value_ref = _text(step.get("value_ref") or step.get("user_fact_id") or step.get("fact_id"))
    if action in {"fill_field", "set_checkbox", "set_radio", "select_option", "select_permit_type"}:
        if not value_ref or value_ref not in facts:
            issues.append(DryRunPacketIssue("missing_fact_provenance", "Draft-fill steps must reference a required user fact with provenance.", f"{location}.value_ref"))
    return issues


def _selector_issue(step: Mapping[str, Any]) -> str:
    selector = step.get("selector")
    selectors = step.get("selectors")
    if isinstance(selectors, Sequence) and not isinstance(selectors, str):
        concrete = [_text(item) for item in selectors if _text(item)]
        if len(concrete) != 1:
            return "Each dry-run step must identify exactly one stable selector."
        selector = concrete[0]
    if not _text(selector):
        return "Each dry-run step must include one stable selector."
    if _normalized_key(selector) in GENERIC_SELECTORS:
        return "Generic selectors are too ambiguous for draft execution."
    confidence = step.get("selector_confidence")
    if isinstance(confidence, str) and _normalized_key(confidence) == "high":
        return ""
    try:
        if not isinstance(confidence, bool) and float(confidence) >= MIN_SELECTOR_CONFIDENCE:
            return ""
    except (TypeError, ValueError):
        pass
    return "Low-confidence or unverified selectors are not allowed."


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, list) or isinstance(value, tuple):
        return value
    return ()


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _normalized_key(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _walk(value: Any, location: str = "packet") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            yield child_location, child
            yield from _walk(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_location = f"{location}[{index}]"
            yield child_location, child
            yield from _walk(child, child_location)


def _dedupe(issues: Sequence[DryRunPacketIssue]) -> list[DryRunPacketIssue]:
    seen: set[tuple[str, str]] = set()
    deduped: list[DryRunPacketIssue] = []
    for issue in issues:
        key = (issue.code, issue.location)
        if key not in seen:
            seen.add(key)
            deduped.append(issue)
    return deduped
