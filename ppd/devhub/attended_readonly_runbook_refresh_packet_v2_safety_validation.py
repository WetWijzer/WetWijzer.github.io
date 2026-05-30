"""Safety validation for DevHub attended read-only runbook refresh packet v2.

This validator is fixture-only. It rejects packet content that would move the
attended read-only runbook refresh out of offline, cited, non-mutating review.
"""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

FORBIDDEN_ARTIFACT_KEYS = {
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
    "har",
    "har_path",
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

ACTIVE_MUTATION_FLAGS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_runbook_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "guardrail_mutation",
    "monitoring_mutation",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_monitoring",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_runbook",
    "mutates_surface_registry",
    "prompt_mutation",
    "release_state_mutation",
    "runbook_mutation",
    "surface_registry_mutation",
}

PRIVATE_VALUE_RE = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|"
    r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b|"
    r"\b\d{3,6}\s+(?:N|NE|NW|S|SE|SW|E|W)\s+[A-Z][A-Z0-9 ]+\b|"
    r"\b(?:permit|invoice|account|license)\s*(?:number|no\.|#)?\s*[:#]\s*[A-Z0-9-]{4,}\b",
    re.IGNORECASE,
)

PRIVATE_ARTIFACT_RE = re.compile(
    r"(/home/|/users/|file://|trace\.zip|\.har\b|storage[_ -]?state\.json|auth[_ -]?state\.json|session[_ -]?state\.json|screenshot\.(?:png|jpe?g|webp))",
    re.IGNORECASE,
)

LIVE_EXECUTION_RE = re.compile(
    r"\b(launched|ran|executed|clicked|filled|captured|stored|opened|navigated|visited)\b.{0,80}\b(live devhub|live browser|playwright|browser session|auth state|screenshot|trace|har)\b|"
    r"\b(live devhub|live browser|playwright|browser session)\b.{0,80}\b(launched|ran|executed|clicked|filled|captured|stored|opened|navigated|visited)\b",
    re.IGNORECASE,
)

CREDENTIAL_AUTOMATION_RE = re.compile(
    r"\b(agent|automation|bot|script|playwright|worker)\b.{0,80}\b(enter|entered|fill|filled|request|requested|solve|solved|bypass|complete|completed|automate|automated|handle|handled)\b.{0,80}\b(credential|password|mfa|captcha|security prompt|login)\b|"
    r"\b(credential|password|mfa|captcha|security prompt|login)\b.{0,80}\b(entered|filled|requested|solved|bypassed|completed|automated|handled by (?:agent|automation|bot|script|playwright|worker))\b",
    re.IGNORECASE,
)

CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(click|clicked|continue|continued|execute|executed|fill|filled|press|pressed|select|selected|start|started|trigger|triggered|use|used|enable|enabled|allow|allowed)\b.{0,80}\b(submit|submission|upload|certif|pay|payment|purchase|schedule|cancel|withdraw|reactivat|save draft|attach)\b|"
    r"\b(submit|submission|upload|certif|pay|payment|purchase|schedule|cancel|withdraw|reactivat|save draft|attach)\b.{0,80}\b(allowed|complete|completed|done|enabled|executed|proceed|started|successful|triggered)\b",
    re.IGNORECASE,
)

LEGAL_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|ensure[sd]?|will|shall)\b.{0,80}\b(approval|approved|code compliant|compliance|issuance|issued|legal|permit outcome|permit will|pass inspection)\b|"
    r"\b(approval|approved|issuance|issued|legal compliance|permit outcome|pass inspection)\b.{0,80}\b(guarantee[sd]?|certain|assured|will|shall)\b",
    re.IGNORECASE,
)

ARTIFACT_REFERENCE_RE = re.compile(
    r"\b(stored screenshot|attached screenshot|screenshot path|browser trace|playwright trace|har file|\.har\b|storage state|auth state|session state|cookie jar)\b",
    re.IGNORECASE,
)


class RunbookRefreshPacketSafetyError(ValueError):
    """Raised when a runbook refresh packet contains unsafe content."""


def validate_attended_readonly_runbook_refresh_packet_v2_safety(packet: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ("packet must be a mapping",)

    if packet.get("packet_type") != "devhub_attended_readonly_runbook_refresh_packet_v2":
        errors.append("packet_type must be devhub_attended_readonly_runbook_refresh_packet_v2")
    if packet.get("packet_version") != 2:
        errors.append("packet_version must be 2")
    if packet.get("mode") != "fixture_first_offline_runbook_refresh":
        errors.append("mode must be fixture_first_offline_runbook_refresh")

    _validate_cited_checklist_deltas(errors, packet)
    _validate_manual_handoff_boundaries(errors, packet)
    _validate_allowed_read_only_steps(errors, packet)
    _scan(errors, packet)
    return _dedupe(errors)


def assert_attended_readonly_runbook_refresh_packet_v2_safe(packet: Mapping[str, Any]) -> None:
    errors = validate_attended_readonly_runbook_refresh_packet_v2_safety(packet)
    if errors:
        raise RunbookRefreshPacketSafetyError("; ".join(errors))


def _validate_cited_checklist_deltas(errors: list[str], packet: Mapping[str, Any]) -> None:
    deltas = _sequence(packet.get("operator_checklist_deltas"))
    if not deltas:
        errors.append("operator_checklist_deltas must be non-empty")
        return
    for index, delta in enumerate(deltas):
        item = _mapping(delta)
        if not _string_sequence(item.get("citations")):
            errors.append(f"operator_checklist_deltas[{index}].citations must be non-empty")


def _validate_manual_handoff_boundaries(errors: list[str], packet: Mapping[str, Any]) -> None:
    boundaries = _sequence(packet.get("manual_login_mfa_captcha_handoff_boundaries"))
    if not boundaries:
        errors.append("manual_login_mfa_captcha_handoff_boundaries must be non-empty")
        return

    saw_login_boundary = False
    for index, boundary in enumerate(boundaries):
        item = _mapping(boundary)
        prefix = f"manual_login_mfa_captcha_handoff_boundaries[{index}]"
        trigger = _text(item.get("trigger")).lower()
        if item.get("human_operator_required") is not True:
            errors.append(f"{prefix}.human_operator_required must be true")
        for field in (
            "agent_may_request_credentials",
            "agent_may_store_credentials",
            "agent_may_automate_mfa_or_captcha",
            "account_creation_allowed",
            "official_action_allowed_after_handoff",
        ):
            if item.get(field) is not False:
                errors.append(f"{prefix}.{field} must be false")
        if not _string_sequence(item.get("citations")):
            errors.append(f"{prefix}.citations must be non-empty")
        if all(term in trigger for term in ("login", "mfa", "captcha")):
            saw_login_boundary = True
    if not saw_login_boundary:
        errors.append("manual login/MFA/CAPTCHA handoff boundary is required")


def _validate_allowed_read_only_steps(errors: list[str], packet: Mapping[str, Any]) -> None:
    for index, step in enumerate(_sequence(packet.get("allowed_read_only_verification_steps"))):
        item = _mapping(step)
        prefix = f"allowed_read_only_verification_steps[{index}]"
        if item.get("read_only") is not True:
            errors.append(f"{prefix}.read_only must be true")
        if item.get("official_action_allowed") is not False:
            errors.append(f"{prefix}.official_action_allowed must be false")
        if not _string_sequence(item.get("citations")):
            errors.append(f"{prefix}.citations must be non-empty")


def _scan(errors: list[str], value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = _text(key)
            child_path = f"{path}.{key_text}"
            lowered_key = key_text.lower()
            if lowered_key in FORBIDDEN_ARTIFACT_KEYS:
                errors.append(f"{child_path} must not contain private DevHub, auth, session, screenshot, trace, or HAR artifact keys")
            if lowered_key in ACTIVE_MUTATION_FLAGS and child is True:
                errors.append(f"{child_path} must not enable active runbook, surface-registry, guardrail, prompt, monitoring, release-state, or agent-state mutation")
            _scan(errors, child, child_path)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan(errors, child, f"{path}[{index}]")
        return
    if isinstance(value, str):
        if PRIVATE_VALUE_RE.search(value):
            errors.append(f"{path} must not contain private or authenticated values")
        if PRIVATE_ARTIFACT_RE.search(value):
            errors.append(f"{path} must not contain session, auth, screenshot, trace, HAR, or private artifact paths")
        if ARTIFACT_REFERENCE_RE.search(value):
            errors.append(f"{path} must not reference screenshot, trace, HAR, auth state, storage state, or session artifacts")
        if LIVE_EXECUTION_RE.search(value):
            errors.append(f"{path} must not claim live DevHub or browser execution")
        if CREDENTIAL_AUTOMATION_RE.search(value):
            errors.append(f"{path} must not contain credential, MFA, CAPTCHA, or login automation language")
        if CONSEQUENTIAL_ACTION_RE.search(value) and not _is_refusal_or_handoff(path, value):
            errors.append(f"{path} must not enable consequential DevHub actions")
        if LEGAL_GUARANTEE_RE.search(value):
            errors.append(f"{path} must not guarantee legal compliance or permitting outcomes")


def _is_refusal_or_handoff(path: str, value: str) -> bool:
    lowered = value.lower()
    return "manual_login_mfa_captcha_handoff_boundaries" in path or "refusal" in lowered or "outside runbook automation" in lowered


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _string_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _dedupe(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)
