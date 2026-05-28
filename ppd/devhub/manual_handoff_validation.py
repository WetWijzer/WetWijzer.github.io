"""Validation for unsupported/manual-handoff PP&D decision packets.

The validator is intentionally schema-light: supervisor and guardrail code can pass
plain dictionaries without depending on a shared contract rewrite. It only applies
the strict checks to packets whose decision/status/category marks them as an
unsupported or manual-handoff outcome.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


MANUAL_HANDOFF_DECISIONS = {
    "manual_handoff",
    "manual-handoff",
    "manual handoff",
    "unsupported",
    "unsupported_manual_handoff",
    "unsupported-manual-handoff",
    "refused_manual_handoff",
    "blocked_manual_handoff",
}

_CREDENTIAL_PROMPT_RE = re.compile(
    r"\b(?:enter|provide|share|send|type|paste|give(?: me)?|tell(?: me)?)\b"
    r"[^.\n]{0,80}\b(?:password|passcode|one[- ]?time code|otp|mfa code|2fa code|security answer|security question|credential|login code)\b",
    re.IGNORECASE,
)
_AUTOMATED_ACCOUNT_SECURITY_RE = re.compile(
    r"\b(?:i|agent|automation|browser|script|worker|we)\s+(?:will|can|should|may|must|am going to)?\s*"
    r"(?:sign in|log in|login|register|create (?:an? )?account|reset (?:your )?password|change (?:your )?password|answer security|complete mfa|complete 2fa|solve captcha|bypass captcha|enroll mfa|change security settings)\b",
    re.IGNORECASE,
)
_PAYMENT_ENTRY_RE = re.compile(
    r"\b(?:enter|type|fill|save|submit|provide|add)\b[^.\n]{0,80}"
    r"\b(?:credit card|debit card|card number|cvv|cvc|expiration date|routing number|bank account|payment details|billing address)\b",
    re.IGNORECASE,
)
_OFFICIAL_ACTION_CLAIM_RE = re.compile(
    r"\b(?:i|agent|automation|browser|script|worker|we)\s+(?:will|can|should|may|must|already|have|has)?\s*"
    r"(?:submit|submitted|schedule|scheduled|certify|certified|upload|uploaded|purchase|purchased|pay|paid|cancel|cancelled|withdraw|withdrew|request extension|reactivate)\b",
    re.IGNORECASE,
)
_CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(?:submit|certify|upload(?: corrections?)?|attach to official record|schedule(?: inspection)?|cancel|withdraw|purchase|pay|enter payment|save payment|request extension|reactivate|create account|reset password|change security settings)\b",
    re.IGNORECASE,
)
_LOCAL_PRIVATE_PATH_RE = re.compile(
    r"(?:file://|~[/\\]|/(?:Users|home)/[^\s/'\"]+|[A-Za-z]:\\Users\\[^\s\\\"]+)",
    re.IGNORECASE,
)
_PRIVATE_VALUE_KEY_RE = re.compile(
    r"(?:password|passcode|otp|mfa|2fa|token|secret|cookie|session|auth|ssn|social_security|dob|date_of_birth|card_number|cvv|cvc|routing_number|bank_account|payment_detail|private_value|local_path)",
    re.IGNORECASE,
)
_REDACTED_VALUES = {"", "redacted", "[redacted]", "", "***", "none", "null"}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    issues: tuple[ValidationIssue, ...]

    def require_ok(self) -> None:
        if self.ok:
            return
        details = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in self.issues)
        raise ValueError(details)


def validate_manual_handoff_decision_packet(packet: Mapping[str, Any]) -> ValidationResult:
    """Return validation issues for an unsupported/manual-handoff decision packet."""

    if not _is_manual_handoff_packet(packet):
        return ValidationResult(ok=True, issues=())

    issues: list[ValidationIssue] = []
    strings = list(_walk_strings(packet))

    for path, value in strings:
        _check_text_rules(path, value, issues)

    _check_private_key_values(packet, issues)
    _check_handoff_reasons(packet, issues)
    _check_blocked_action_links(packet, issues)
    _check_alternatives(packet, issues)

    return ValidationResult(ok=not issues, issues=tuple(issues))


def assert_valid_manual_handoff_decision_packet(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a manual-handoff packet violates PP&D boundaries."""

    validate_manual_handoff_decision_packet(packet).require_ok()


def _is_manual_handoff_packet(packet: Mapping[str, Any]) -> bool:
    candidates = (
        packet.get("decision"),
        packet.get("status"),
        packet.get("outcome"),
        packet.get("category"),
        packet.get("type"),
    )
    return any(_normalise_marker(value) in MANUAL_HANDOFF_DECISIONS for value in candidates)


def _normalise_marker(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("_", "-")


def _walk_strings(value: Any, path: str = "$", seen: set[int] | None = None) -> Iterable[tuple[str, str]]:
    if seen is None:
        seen = set()
    value_id = id(value)
    if value_id in seen:
        return
    seen.add(value_id)

    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            safe_key = str(key).replace(".", "_")
            yield from _walk_strings(child, f"{path}.{safe_key}", seen)
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{path}[{index}]", seen)


def _check_text_rules(path: str, value: str, issues: list[ValidationIssue]) -> None:
    if _CREDENTIAL_PROMPT_RE.search(value):
        issues.append(ValidationIssue("credential_prompt", path, "manual handoff text asks the user to provide credentials or security codes"))
    if _AUTOMATED_ACCOUNT_SECURITY_RE.search(value):
        issues.append(ValidationIssue("automated_account_security_step", path, "manual handoff text suggests automating account, login, MFA, CAPTCHA, or security settings"))
    if _PAYMENT_ENTRY_RE.search(value):
        issues.append(ValidationIssue("payment_entry_instruction", path, "manual handoff text instructs entry or storage of payment details"))
    if _OFFICIAL_ACTION_CLAIM_RE.search(value):
        issues.append(ValidationIssue("official_action_claim", path, "manual handoff text claims or proposes an official consequential action"))
    if _LOCAL_PRIVATE_PATH_RE.search(value):
        issues.append(ValidationIssue("local_private_path", path, "manual handoff text contains a local private filesystem path"))


def _check_private_key_values(value: Any, issues: list[ValidationIssue], path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{str(key).replace('.', '_')}"
            if _PRIVATE_VALUE_KEY_RE.search(str(key)) and _has_non_redacted_value(child):
                issues.append(ValidationIssue("private_value", child_path, "packet contains a non-redacted private value"))
            _check_private_key_values(child, issues, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _check_private_key_values(child, issues, f"{path}[{index}]")


def _has_non_redacted_value(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in _REDACTED_VALUES
    if value is None:
        return False
    if isinstance(value, Mapping):
        return any(_has_non_redacted_value(child) for child in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_has_non_redacted_value(child) for child in value)
    return True


def _check_handoff_reasons(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    reasons = packet.get("handoff_reasons") or packet.get("reasons") or packet.get("manual_handoff_reasons")
    if not isinstance(reasons, Sequence) or isinstance(reasons, (str, bytes, bytearray)) or not reasons:
        issues.append(ValidationIssue("uncited_handoff_reason", "$.handoff_reasons", "manual handoff packets must include cited handoff reasons"))
        return

    for index, reason in enumerate(reasons):
        if not isinstance(reason, Mapping):
            issues.append(ValidationIssue("uncited_handoff_reason", f"$.handoff_reasons[{index}]", "handoff reason must include source evidence"))
            continue
        if not _has_source_link(reason):
            issues.append(ValidationIssue("uncited_handoff_reason", f"$.handoff_reasons[{index}]", "handoff reason is missing a citation/source URL/evidence link"))


def _check_blocked_action_links(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    blocked_actions = packet.get("blocked_actions") or packet.get("blocked_action_links")
    if not isinstance(blocked_actions, Sequence) or isinstance(blocked_actions, (str, bytes, bytearray)) or not blocked_actions:
        issues.append(ValidationIssue("missing_blocked_action_link", "$.blocked_actions", "manual handoff packets must include cited blocked actions"))
        return

    for index, action in enumerate(blocked_actions):
        if not isinstance(action, Mapping) or not _has_source_link(action):
            issues.append(ValidationIssue("missing_blocked_action_link", f"$.blocked_actions[{index}]", "blocked action is missing a source URL/citation/evidence link"))


def _check_alternatives(packet: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    alternatives = packet.get("alternatives") or packet.get("next_safe_actions") or packet.get("safe_alternatives") or []
    if isinstance(alternatives, (str, bytes, bytearray)):
        alternatives = [alternatives]
    if not isinstance(alternatives, Sequence):
        return

    for index, alternative in enumerate(alternatives):
        text = " ".join(value for _, value in _walk_strings(alternative, f"$.alternatives[{index}]"))
        if _CONSEQUENTIAL_ACTION_RE.search(text):
            issues.append(ValidationIssue("consequential_alternative", f"$.alternatives[{index}]", "alternative would perform or advance a consequential official action"))


def _has_source_link(value: Mapping[str, Any]) -> bool:
    source_keys = (
        "citation",
        "citation_url",
        "source",
        "source_url",
        "evidence",
        "evidence_id",
        "evidence_url",
        "blocked_action_link",
        "url",
    )
    for key in source_keys:
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate.strip():
            return True
        if isinstance(candidate, Mapping) and _has_source_link(candidate):
            return True
    return False
