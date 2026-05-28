"""Validation for commit-safe DevHub read-only observation packets.

Read-only observation packets may describe attended, user-visible DevHub UI
structure, but they must not contain session artifacts, private values, or
controls for consequential official actions.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable


@dataclass(frozen=True)
class ObservationValidationError:
    """A single policy violation found in a read-only observation packet."""

    path: str
    reason: str


class ObservationPacketRejected(ValueError):
    """Raised when a read-only observation packet contains prohibited data."""

    def __init__(self, errors: Iterable[ObservationValidationError]) -> None:
        self.errors = tuple(errors)
        message = "; ".join(f"{error.path}: {error.reason}" for error in self.errors)
        super().__init__(message or "observation packet rejected")


_PROHIBITED_KEY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(^|_)(browser_)?state($|_)", re.IGNORECASE), "browser state is prohibited"),
    (re.compile(r"(^|_)(storage_)?state($|_)", re.IGNORECASE), "browser state is prohibited"),
    (re.compile(r"(^|_)cookies?($|_)", re.IGNORECASE), "cookies are prohibited"),
    (re.compile(r"(^|_)(credential|credentials|password|passcode|token|secret)($|_)", re.IGNORECASE), "credentials or secrets are prohibited"),
    (re.compile(r"(^|_)(screen_?shot|screenshots?)($|_)", re.IGNORECASE), "screenshots are prohibited"),
    (re.compile(r"(^|_)(trace|traces|trace_?path)($|_)", re.IGNORECASE), "traces are prohibited"),
    (re.compile(r"(^|_)(har|har_?path|har_?data)($|_)", re.IGNORECASE), "HAR data is prohibited"),
    (re.compile(r"(^|_)(private_)?field_?(value|values)($|_)", re.IGNORECASE), "private field values are prohibited"),
    (re.compile(r"(^|_)(raw|actual|entered|input|user)_?value($|_)", re.IGNORECASE), "private field values are prohibited"),
)

_CONSEQUENTIAL_CONTROL_RE = re.compile(
    r"\b(upload|attach|submit|submission|certify|acknowledge|schedule|reschedule|cancel|withdraw|payment|pay|purchase|checkout)\b",
    re.IGNORECASE,
)

_AUTOMATED_AUTH_CLAIM_RE = re.compile(
    r"\b(automated|auto(?:matically)?|scripted|solved|bypassed|handled|completed)\b.{0,60}\b(login|sign\s*in|mfa|multi[-\s]?factor|captcha)\b|"
    r"\b(login|sign\s*in|mfa|multi[-\s]?factor|captcha)\b.{0,60}\b(automated|auto(?:matically)?|scripted|solved|bypassed|handled|completed)\b",
    re.IGNORECASE,
)

_AUTH_CHALLENGE_KEY_RE = re.compile(r"\b(login|sign_?in|mfa|multi_?factor|captcha)\b", re.IGNORECASE)
_AUTOMATION_KEY_RE = re.compile(r"\b(automated|automation|scripted|bypassed|solved)\b", re.IGNORECASE)
_CONTROL_CONTAINER_KEYS = frozenset({"control", "controls", "action", "actions", "button", "buttons", "link", "links"})


def validate_read_only_observation_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Return ``packet`` when it is safe to persist, otherwise raise.

    The validator is intentionally conservative. It accepts structural UI
    observations from an attended DevHub session and rejects data that would
    persist browser/session state, user-private values, consequential controls,
    or claims that authentication challenges were automated.
    """

    errors: list[ObservationValidationError] = []

    if not isinstance(packet, dict):
        raise TypeError("read-only observation packet must be a dict")

    _walk(packet, "$", errors)

    if errors:
        raise ObservationPacketRejected(errors)

    return packet


def is_read_only_observation_packet_safe(packet: dict[str, Any]) -> bool:
    """Return whether ``packet`` passes read-only observation validation."""

    try:
        validate_read_only_observation_packet(packet)
    except ObservationPacketRejected:
        return False
    return True


def _walk(value: Any, path: str, errors: list[ObservationValidationError]) -> None:
    if isinstance(value, dict):
        _check_dict(value, path, errors)
        for key, child in value.items():
            _walk(child, f"{path}.{key}", errors)
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _walk(child, f"{path}[{index}]", errors)
        return

    if isinstance(value, str):
        _check_string(value, path, errors)


def _check_dict(value: dict[str, Any], path: str, errors: list[ObservationValidationError]) -> None:
    joined_keys = " ".join(str(key) for key in value)

    for key, child in value.items():
        key_text = str(key)
        for pattern, reason in _PROHIBITED_KEY_PATTERNS:
            if pattern.search(key_text):
                errors.append(ObservationValidationError(f"{path}.{key_text}", reason))

        if _AUTH_CHALLENGE_KEY_RE.search(key_text) and _automation_truthy(child):
            errors.append(
                ObservationValidationError(
                    f"{path}.{key_text}",
                    "claims that login, MFA, or CAPTCHA was automated are prohibited",
                )
            )

    if _AUTH_CHALLENGE_KEY_RE.search(joined_keys) and _AUTOMATION_KEY_RE.search(joined_keys):
        errors.append(
            ObservationValidationError(
                path,
                "claims that login, MFA, or CAPTCHA was automated are prohibited",
            )
        )

    if _looks_like_consequential_control(value):
        errors.append(
            ObservationValidationError(
                path,
                "upload, submission, scheduling, cancellation, and payment controls are prohibited",
            )
        )


def _check_string(value: str, path: str, errors: list[ObservationValidationError]) -> None:
    if _AUTOMATED_AUTH_CLAIM_RE.search(value):
        errors.append(
            ObservationValidationError(
                path,
                "claims that login, MFA, or CAPTCHA was automated are prohibited",
            )
        )

    if path.split(".")[-2:-1] and path.split(".")[-2] in _CONTROL_CONTAINER_KEYS:
        if _CONSEQUENTIAL_CONTROL_RE.search(value):
            errors.append(
                ObservationValidationError(
                    path,
                    "upload, submission, scheduling, cancellation, and payment controls are prohibited",
                )
            )


def _automation_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(_AUTOMATION_KEY_RE.search(value))
    if isinstance(value, dict):
        return any(_AUTOMATION_KEY_RE.search(str(key)) and bool(child) for key, child in value.items())
    return False


def _looks_like_consequential_control(value: dict[str, Any]) -> bool:
    searchable_parts: list[str] = []

    for key, child in value.items():
        key_text = str(key)
        if key_text.lower() in _CONTROL_CONTAINER_KEYS:
            searchable_parts.append(key_text)
            searchable_parts.append(_stringify_shallow(child))
        elif key_text.lower() in {"label", "name", "text", "accessible_name", "aria_label", "test_id", "selector"}:
            searchable_parts.append(str(child))
        elif key_text.lower() in {"type", "role"} and str(child).lower() in {"button", "submit", "file", "link"}:
            searchable_parts.append(str(child))

    searchable = " ".join(searchable_parts)
    return bool(searchable and _CONSEQUENTIAL_CONTROL_RE.search(searchable))


def _stringify_shallow(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(str(item) for pair in value.items() for item in pair)
    if isinstance(value, list):
        return " ".join(_stringify_shallow(item) for item in value)
    return str(value)
