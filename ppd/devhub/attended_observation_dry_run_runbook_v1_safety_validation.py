"""Safety validation for attended DevHub observation dry-run runbook v1.

The checks in this module are fixture-first and side-effect free. They validate
that a committed runbook remains an offline review artifact and does not encode
instructions or flags that would automate login, security challenges, private
account handling, browser artifacts, official DevHub actions, or state mutation.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

PACKET_TYPE = "ppd.devhub.attended_observation_dry_run_runbook.v1"

_NEGATION_MARKERS = (
    "do not",
    "does not",
    "must not",
    "may not",
    "not allowed",
    "without",
    "no ",
    "stop before",
    "reject ",
    "abort ",
)

_AUTOMATED_LOGIN_AND_SECURITY_PHRASES = (
    "automate login",
    "automated login",
    "automation logs in",
    "automation signs in",
    "enter credentials",
    "fill password",
    "submit password",
    "solve captcha",
    "complete captcha",
    "handle captcha",
    "solve mfa",
    "complete mfa",
    "handle mfa",
    "approve mfa",
    "create account",
    "register account",
    "complete account creation",
    "perform account creation",
    "start account creation",
)

_PRIVATE_OR_ARTIFACT_TEXT = (
    "raw authenticated",
    "private account value",
    "private account values",
    "account number:",
    "permit number:",
    "password:",
    "cookie=",
    "token=",
    "storage_state",
    "auth_state",
    "session file",
    "session_file",
    "session.json",
    "cookies.json",
    "playwright/.auth",
    "trace.zip",
    "network.har",
    ".har",
    "screenshot",
    "/home/",
    "/users/",
    "c:\\users\\",
)

_CONSEQUENTIAL_ACTION_PHRASES = (
    "click through",
    "click submit",
    "press submit",
    "select submit",
    "submit application",
    "submit permit",
    "upload document",
    "upload correction",
    "upload file",
    "attach file",
    "pay fee",
    "pay fees",
    "make payment",
    "submit payment",
    "schedule inspection",
    "cancel permit",
    "cancel request",
    "cancel inspection",
    "certify acknowledgement",
    "certify application",
    "complete certification",
    "write-capable",
    "write capable",
)

_PRIVATE_OR_ARTIFACT_KEY_TERMS = (
    "password",
    "credential",
    "cookie",
    "token",
    "secret",
    "auth_state",
    "storage_state",
    "session_file",
    "session_path",
    "session_state_path",
    "screenshot_path",
    "trace_path",
    "har_path",
    "raw_authenticated_value",
    "raw_account_value",
    "private_account_value",
    "private_value",
    "account_number",
    "permit_number_value",
    "payment_detail",
    "card_number",
)

_WRITE_CAPABLE_TRUE_KEYS = (
    "automated_login",
    "automation_may_login",
    "automation_may_enter_credentials",
    "automation_may_handle_captcha",
    "automation_may_handle_mfa",
    "automation_may_create_account",
    "captcha_automation",
    "mfa_automation",
    "account_creation_automation",
    "click_through_allowed",
    "write_capable",
    "write_capable_action",
    "may_write",
    "may_click_through",
    "may_submit",
    "may_upload",
    "may_pay",
    "may_schedule",
    "may_cancel",
    "may_certify",
    "enabled_submit",
    "enabled_upload",
    "enabled_payment",
    "enabled_scheduling",
    "enabled_cancellation",
    "enabled_certification",
)

_MUTATION_DOMAINS = (
    "devhub",
    "surface_registry",
    "guardrail",
    "prompt",
    "release_state",
    "agent_state",
)

_MUTATION_TERMS = ("mutation", "mutates", "write", "update", "promote", "publish")


def validate_attended_observation_dry_run_runbook_v1_safety(packet: Mapping[str, Any]) -> tuple[str, ...]:
    """Return deterministic safety errors for an unsafe dry-run runbook."""

    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ("packet must be a mapping",)
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")

    _validate_offline_flags(packet, errors)
    _validate_manual_login_boundaries(packet, errors)
    _validate_read_only_evidence(packet, errors)
    _validate_stop_gates(packet, errors)
    _scan(packet, "$", errors)
    return tuple(errors)


def assert_attended_observation_dry_run_runbook_v1_safe(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the dry-run runbook contains unsafe content."""

    errors = validate_attended_observation_dry_run_runbook_v1_safety(packet)
    if errors:
        raise ValueError("unsafe attended observation dry-run runbook v1: " + "; ".join(errors))


def _validate_offline_flags(packet: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("fixture_first", "offline_only"):
        if packet.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in ("live_devhub_session", "browser_launched", "browser_automation_performed", "auth_state_saved"):
        if packet.get(key) is not False:
            errors.append(f"{key} must be false")


def _validate_manual_login_boundaries(packet: Mapping[str, Any], errors: list[str]) -> None:
    boundaries = _mapping(packet.get("manual_login_boundaries"))
    for key in ("automation_may_enter_credentials", "automation_may_handle_captcha", "automation_may_handle_mfa", "automation_may_create_account"):
        if boundaries.get(key) is not False:
            errors.append(f"manual_login_boundaries.{key} must be false")
    if boundaries.get("manual_login_only") is not True:
        errors.append("manual_login_boundaries.manual_login_only must be true")


def _validate_read_only_evidence(packet: Mapping[str, Any], errors: list[str]) -> None:
    for index, item in enumerate(_sequence(packet.get("read_only_page_evidence_expectations"))):
        row = _mapping(item)
        prefix = f"read_only_page_evidence_expectations[{index}]"
        if row.get("raw_values_allowed") is not False:
            errors.append(f"{prefix}.raw_values_allowed must be false")
        if row.get("screenshots_allowed") is not False:
            errors.append(f"{prefix}.screenshots_allowed must be false")
        if row.get("read_only_only") is not True:
            errors.append(f"{prefix}.read_only_only must be true")


def _validate_stop_gates(packet: Mapping[str, Any], errors: list[str]) -> None:
    for index, item in enumerate(_sequence(packet.get("stop_before_action_gates"))):
        row = _mapping(item)
        prefix = f"stop_before_action_gates[{index}]"
        if row.get("stop_before_action") is not True:
            errors.append(f"{prefix}.stop_before_action must be true")
        if row.get("automated_execution_allowed") is not False:
            errors.append(f"{prefix}.automated_execution_allowed must be false")


def _scan(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        _scan_mapping(value, path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        _scan_text(value, path, errors)


def _scan_mapping(value: Mapping[str, Any], path: str, errors: list[str]) -> None:
    for key, child in value.items():
        key_text = str(key)
        key_name = _normalize_key(key_text)
        child_path = f"{path}.{key_text}"
        if _is_active_mutation_flag(key_name, child):
            errors.append(f"{child_path} contains active DevHub, registry, guardrail, prompt, release-state, or agent-state mutation flag")
        if _is_write_capable_true_key(key_name, child):
            errors.append(f"{child_path} enables automated login, security handling, click-through, or write-capable action")
        if _is_private_or_artifact_key(key_name) and _is_present(child):
            errors.append(f"{child_path} contains private account, session, screenshot, trace, HAR, or raw authenticated artifact value")
        _scan(child, child_path, errors)


def _scan_text(value: str, path: str, errors: list[str]) -> None:
    lowered = value.lower()
    if any(term in lowered for term in _PRIVATE_OR_ARTIFACT_TEXT):
        errors.append(f"{path} references private account values, session files, screenshots, traces, HAR artifacts, or local private paths")
    if _has_unnegated_phrase(lowered, _AUTOMATED_LOGIN_AND_SECURITY_PHRASES):
        errors.append(f"{path} contains automated login, CAPTCHA/MFA handling, or account-creation handling instructions")
    if _has_unnegated_phrase(lowered, _CONSEQUENTIAL_ACTION_PHRASES):
        errors.append(f"{path} contains click-through, write-capable, upload, submission, payment, scheduling, cancellation, or certification language")


def _has_unnegated_phrase(text: str, phrases: Iterable[str]) -> bool:
    for phrase in phrases:
        index = text.find(phrase)
        if index == -1:
            continue
        window = text[max(0, index - 40) : index]
        if not any(marker in window for marker in _NEGATION_MARKERS):
            return True
    return False


def _is_private_or_artifact_key(key_name: str) -> bool:
    return not key_name.startswith("no_") and any(term in key_name for term in _PRIVATE_OR_ARTIFACT_KEY_TERMS)


def _is_write_capable_true_key(key_name: str, value: Any) -> bool:
    return not key_name.startswith("no_") and key_name in _WRITE_CAPABLE_TRUE_KEYS and _is_truthy(value)


def _is_active_mutation_flag(key_name: str, value: Any) -> bool:
    if key_name.startswith("no_") or not _is_truthy(value):
        return False
    has_domain = any(domain in key_name for domain in _MUTATION_DOMAINS)
    has_mutation = any(term in key_name for term in _MUTATION_TERMS)
    return has_domain and has_mutation


def _is_truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "enabled", "active", "allowed"}
    return False


def _is_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip() not in {"[REDACTED]", "[NOT_STORED]"}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return []


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


__all__ = [
    "assert_attended_observation_dry_run_runbook_v1_safe",
    "validate_attended_observation_dry_run_runbook_v1_safety",
]
