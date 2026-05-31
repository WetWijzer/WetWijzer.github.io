"""Validation for attended DevHub read-only session preflight packets.

The validator is intentionally data-only and deterministic. It does not open a
browser, perform login, inspect private DevHub pages, or persist artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


PACKET_VERSION = "attended_devhub_read_only_session_preflight_packet_v2"

_REQUIRED_LIST_FIELDS = (
    "manual_login_readiness_checks",
    "allowed_read_only_destinations",
    "attendance_statements",
    "redaction_requirements",
    "abort_conditions",
    "no_private_artifact_commitments",
)

_MUTATION_FLAG_FIELDS = (
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_devhub_surface_mutation",
    "active_source_mutation",
    "active_contract_mutation",
    "active_release_state_mutation",
)

_PRIVATE_ARTIFACT_MARKERS = (
    "auth_state",
    "storage_state",
    "session_state",
    "browser_state",
    "browser_context_artifact",
    "cookie",
    "cookies",
    "local_storage",
    "session_storage",
    "trace",
    "traces",
    "har",
    "screenshot",
    "screenshots",
    "video",
    "recording",
    "raw_html",
    "raw_dom",
    "raw_crawl",
    "raw_page",
    "downloaded_document",
    "downloaded_documents",
    "download_dir",
    "downloads",
    "private_artifact",
    "private_artifacts",
    "password",
    "credential",
    "credentials",
    "token",
    "secret",
)

_AUTOMATED_LOGIN_MARKERS = (
    "automate login",
    "automated login",
    "auto login",
    "autologin",
    "automate sign in",
    "automated sign in",
    "automate sign-in",
    "automated sign-in",
    "fill password",
    "enter password",
    "submit password",
    "bypass captcha",
    "solve captcha",
    "automate captcha",
    "automate mfa",
    "automated mfa",
    "bypass mfa",
    "complete mfa",
    "submit mfa",
    "enter mfa",
    "otp code",
    "one-time code",
)

_OFFICIAL_ACTION_MARKERS = (
    "official action completed",
    "official-action completed",
    "completed official action",
    "submission completed",
    "submitted permit",
    "permit submitted",
    "payment completed",
    "paid fee",
    "inspection scheduled",
    "scheduled inspection",
    "correction uploaded",
    "uploaded correction",
    "certification completed",
    "certified acknowledgement",
    "application submitted",
)

_GUARANTEE_MARKERS = (
    "guarantee approval",
    "guaranteed approval",
    "permit will be approved",
    "approval is certain",
    "legally sufficient",
    "legal advice",
    "legal determination",
    "compliance guaranteed",
    "guarantee compliance",
    "permitting guarantee",
    "permit guarantee",
)

_READ_ONLY_TERMS = (
    "home",
    "my permits",
    "my permits & requests",
    "permit details",
    "status",
    "fee notice review",
    "correction request review",
    "attachment list review",
    "inspection results review",
    "read-only",
    "readonly",
)

_WRITE_ACTION_TERMS = (
    "submit",
    "certify",
    "upload",
    "pay",
    "payment",
    "purchase",
    "schedule",
    "cancel",
    "withdraw",
    "request extension",
    "save draft",
    "edit",
    "delete",
)


@dataclass(frozen=True)
class PreflightValidationResult:
    """Result of validating an attended DevHub read-only preflight packet."""

    ok: bool
    errors: tuple[str, ...]


def validate_attended_read_only_preflight_packet_v2(
    packet: Mapping[str, Any],
) -> PreflightValidationResult:
    """Validate a v2 attended DevHub read-only preflight packet.

    The packet is accepted only when it explicitly documents manual login,
    allowed read-only destinations, user attendance, redaction, abort behavior,
    no-private-artifact commitments, validation commands, and inactive mutation
    flags for active prompt/guardrail/surface/source/contract/release state.
    """

    errors: list[str] = []

    if not isinstance(packet, Mapping):
        return PreflightValidationResult(False, ("packet must be a mapping",))

    if packet.get("version") != PACKET_VERSION:
        errors.append(f"version must be {PACKET_VERSION!r}")

    for field in _REQUIRED_LIST_FIELDS:
        values = packet.get(field)
        if not _is_non_empty_string_sequence(values):
            errors.append(f"{field} must be a non-empty list of strings")

    validation_commands = packet.get("validation_commands")
    if not _is_validation_command_sequence(validation_commands):
        errors.append("validation_commands must be a non-empty list of command argument lists")

    destinations = packet.get("allowed_read_only_destinations")
    if _is_non_empty_string_sequence(destinations):
        for index, destination in enumerate(destinations):
            normalized = _normalize(destination)
            if not any(term in normalized for term in _READ_ONLY_TERMS):
                errors.append(
                    "allowed_read_only_destinations "
                    f"entry {index} must name a recognized read-only DevHub destination"
                )
            if any(term in normalized for term in _WRITE_ACTION_TERMS):
                errors.append(
                    "allowed_read_only_destinations "
                    f"entry {index} includes a write or official-action term"
                )

    for field in _MUTATION_FLAG_FIELDS:
        if packet.get(field) is not False:
            errors.append(f"{field} must be false")

    flattened = tuple(_flatten_text(packet))
    for marker in _PRIVATE_ARTIFACT_MARKERS:
        if _contains_marker(flattened, marker):
            errors.append(f"packet must not include private/session/browser/raw/downloaded artifact marker: {marker}")

    for marker in _AUTOMATED_LOGIN_MARKERS:
        if _contains_marker(flattened, marker):
            errors.append(f"packet must not claim automated login, CAPTCHA, or MFA handling: {marker}")

    for marker in _OFFICIAL_ACTION_MARKERS:
        if _contains_marker(flattened, marker):
            errors.append(f"packet must not claim official-action completion: {marker}")

    for marker in _GUARANTEE_MARKERS:
        if _contains_marker(flattened, marker):
            errors.append(f"packet must not make legal or permitting guarantees: {marker}")

    return PreflightValidationResult(not errors, tuple(errors))


def assert_attended_read_only_preflight_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a preflight packet fails validation."""

    result = validate_attended_read_only_preflight_packet_v2(packet)
    if not result.ok:
        raise ValueError("invalid attended DevHub read-only preflight packet v2: " + "; ".join(result.errors))


def _is_non_empty_string_sequence(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _is_validation_command_sequence(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for command in value:
        if not isinstance(command, list) or not command:
            return False
        if not all(isinstance(part, str) and part.strip() for part in command):
            return False
    return True


def _flatten_text(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            yield str(key)
            yield from _flatten_text(nested)
    elif isinstance(value, str):
        yield value
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for nested in value:
            yield from _flatten_text(nested)
    elif value is not None:
        yield str(value)


def _contains_marker(values: Iterable[str], marker: str) -> bool:
    normalized_marker = _normalize(marker)
    return any(normalized_marker in _normalize(value) for value in values)


def _normalize(value: str) -> str:
    return " ".join(value.replace("-", "_").lower().split())
