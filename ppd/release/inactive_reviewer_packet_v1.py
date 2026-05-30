"""Validation for inactive release application reviewer packet v1.

The validator is intentionally side-effect free. It checks committed packet data for
required reviewer evidence and rejects language or artifact references that would make
an inactive review packet look like a live release, legal outcome, or state mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class PacketValidationError:
    """A deterministic validation failure with a stable code."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class PacketValidationResult:
    """Validation result for a reviewer packet."""

    ok: bool
    errors: tuple[PacketValidationError, ...]


REQUIRED_SEQUENCE_FIELDS: Mapping[str, str] = {
    "reviewer_comparison_rows": "at least one reviewer comparison row is required",
    "prerequisite_gate_acknowledgements": "at least one prerequisite gate acknowledgement is required",
    "fixture_family_risk_notes": "at least one fixture-family risk note is required",
    "rollback_checkpoint_confirmations": "at least one rollback checkpoint confirmation is required",
    "validation_commands": "at least one validation command is required",
}

REQUIRED_HOLD_FIELDS: tuple[str, ...] = (
    "hold_id",
    "source",
    "carry_forward_reason",
    "next_review_action",
)

ACKNOWLEDGEMENT_FIELDS: tuple[str, ...] = ("acknowledged", "confirmed")

PRIVATE_KEY_TOKENS: tuple[str, ...] = (
    "cookie",
    "credential",
    "password",
    "secret",
    "session",
    "storage_state",
    "auth_state",
    "authorization",
    "bearer",
    "token",
    "trace",
    "har",
    "screenshot",
    "video",
    "browser_context",
    "playwright_state",
)

PRIVATE_VALUE_TOKENS: tuple[str, ...] = (
    ".har",
    ".trace",
    "trace.zip",
    "storage_state.json",
    "auth.json",
    "auth-state",
    "session.json",
    "cookies.json",
    "screenshot.png",
    "screenshot.jpg",
    "screenshot.jpeg",
    "playwright-report",
    "test-results/",
    "browser-state",
)

RAW_DATA_TOKENS: tuple[str, ...] = (
    "raw_crawl",
    "raw-crawl",
    "raw crawl",
    "downloaded_pdf",
    "downloaded-pdf",
    "downloaded pdf",
    "raw_pdf",
    "raw-pdf",
    "raw pdf",
    "downloaded_data",
    "downloaded-data",
    "downloaded data",
    "crawl_output",
    "crawl-output",
    "crawl output",
    "/downloads/",
    "/raw/",
)

LIVE_RELEASE_CLAIMS: tuple[str, ...] = (
    "applied to production",
    "applied live",
    "executed live",
    "live execution",
    "release complete",
    "released complete",
    "deployed live",
    "production release completed",
    "changes are live",
)

OUTCOME_GUARANTEES: tuple[str, ...] = (
    "permit will be approved",
    "permit is guaranteed",
    "approval is guaranteed",
    "guaranteed approval",
    "legally compliant",
    "legal compliance guaranteed",
    "will pass inspection",
    "inspection will pass",
    "city will approve",
)

CONSEQUENTIAL_ACTION_LANGUAGE: tuple[str, ...] = (
    "submit the permit",
    "submitted the permit",
    "certify the acknowledgement",
    "certified the acknowledgement",
    "upload corrections",
    "uploaded corrections",
    "pay the fee",
    "paid the fee",
    "schedule inspection",
    "scheduled inspection",
    "cancel permit",
    "cancelled permit",
    "finalize application",
    "purchase permit",
)

ACTIVE_MUTATION_KEYS: tuple[str, ...] = (
    "mutate_active_artifacts",
    "mutate_active_prompts",
    "mutate_release_state",
    "mutate_fixtures",
    "mutate_agent_state",
    "active_artifact_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_fixture_mutation",
    "active_agent_state_mutation",
)

ACTIVE_MUTATION_TEXT: tuple[str, ...] = (
    "mutate active artifact",
    "mutate active prompt",
    "mutate release state",
    "mutate active fixture",
    "mutate agent state",
    "active artifact mutation",
    "active prompt mutation",
    "active release-state mutation",
    "active fixture mutation",
    "active agent-state mutation",
)


def validate_inactive_release_application_reviewer_packet_v1(
    packet: Mapping[str, Any],
) -> PacketValidationResult:
    """Validate an inactive release application reviewer packet v1.

    The function accepts plain decoded JSON/YAML-like dictionaries so callers can use
    it from tests, daemon checks, or offline packet tooling without importing any
    browser or network dependencies.
    """

    errors: list[PacketValidationError] = []

    if packet.get("packet_version") not in ("inactive-release-application-reviewer-packet-v1", "v1"):
        errors.append(
            PacketValidationError(
                "packet_version.invalid",
                "packet_version",
                "packet_version must identify inactive release application reviewer packet v1",
            )
        )

    if packet.get("release_activity") != "inactive":
        errors.append(
            PacketValidationError(
                "release_activity.not_inactive",
                "release_activity",
                "release_activity must be inactive",
            )
        )

    for field, message in REQUIRED_SEQUENCE_FIELDS.items():
        if not _non_empty_sequence(packet.get(field)):
            errors.append(PacketValidationError(f"{field}.missing", field, message))

    _validate_acknowledgements(
        packet.get("prerequisite_gate_acknowledgements"),
        "prerequisite_gate_acknowledgements",
        errors,
    )
    _validate_acknowledgements(
        packet.get("rollback_checkpoint_confirmations"),
        "rollback_checkpoint_confirmations",
        errors,
    )
    _validate_hold_carry_forward(packet.get("unresolved_hold_carry_forward"), errors)
    _validate_validation_commands(packet.get("validation_commands"), errors)
    _scan_for_prohibited_content(packet, errors)

    return PacketValidationResult(ok=not errors, errors=tuple(errors))


def assert_inactive_release_application_reviewer_packet_v1(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the packet fails validation."""

    result = validate_inactive_release_application_reviewer_packet_v1(packet)
    if result.ok:
        return
    details = "; ".join(f"{error.code} at {error.path}: {error.message}" for error in result.errors)
    raise ValueError(details)


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _validate_acknowledgements(value: Any, path: str, errors: list[PacketValidationError]) -> None:
    if not _non_empty_sequence(value):
        return
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, Mapping):
            errors.append(PacketValidationError(f"{path}.item.invalid", item_path, "acknowledgement must be an object"))
            continue
        if not any(item.get(field) is True for field in ACKNOWLEDGEMENT_FIELDS):
            errors.append(
                PacketValidationError(
                    f"{path}.item.unconfirmed",
                    item_path,
                    "acknowledgement or confirmation must be explicitly true",
                )
            )


def _validate_hold_carry_forward(value: Any, errors: list[PacketValidationError]) -> None:
    path = "unresolved_hold_carry_forward"
    if not _non_empty_sequence(value):
        errors.append(
            PacketValidationError(
                "unresolved_hold_carry_forward.missing",
                path,
                "at least one unresolved hold carry-forward record is required",
            )
        )
        return

    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, Mapping):
            errors.append(PacketValidationError("unresolved_hold_carry_forward.item.invalid", item_path, "hold record must be an object"))
            continue
        for field in REQUIRED_HOLD_FIELDS:
            if not item.get(field):
                errors.append(
                    PacketValidationError(
                        f"unresolved_hold_carry_forward.{field}.missing",
                        f"{item_path}.{field}",
                        f"unresolved hold carry-forward field {field} is required",
                    )
                )


def _validate_validation_commands(value: Any, errors: list[PacketValidationError]) -> None:
    if not _non_empty_sequence(value):
        return
    for index, command in enumerate(value):
        path = f"validation_commands[{index}]"
        if not _non_empty_sequence(command) or not all(isinstance(part, str) and part for part in command):
            errors.append(
                PacketValidationError(
                    "validation_commands.item.invalid",
                    path,
                    "validation commands must be non-empty argv arrays of strings",
                )
            )


def _scan_for_prohibited_content(value: Any, errors: list[PacketValidationError]) -> None:
    for path, key, scalar in _walk(value):
        key_lower = key.lower() if key else ""
        scalar_lower = scalar.lower() if scalar else ""
        normalized_scalar = _normalize_pathish_text(scalar_lower)

        if any(token in key_lower for token in PRIVATE_KEY_TOKENS):
            errors.append(PacketValidationError("private_artifact.key", path, "private/authenticated/session/browser artifact keys are not allowed"))
        if any(token in normalized_scalar for token in PRIVATE_VALUE_TOKENS):
            errors.append(PacketValidationError("private_artifact.value", path, "screenshots, traces, HAR, auth, or browser state artifacts are not allowed"))
        if any(token in normalized_scalar for token in RAW_DATA_TOKENS):
            errors.append(PacketValidationError("raw_data_artifact.value", path, "raw crawl, PDF, downloaded, or scraped data artifacts are not allowed"))
        if any(token in scalar_lower for token in LIVE_RELEASE_CLAIMS):
            errors.append(PacketValidationError("live_release_claim.value", path, "live execution, applied, or release-complete claims are not allowed"))
        if any(token in scalar_lower for token in OUTCOME_GUARANTEES):
            errors.append(PacketValidationError("outcome_guarantee.value", path, "legal or permitting outcome guarantees are not allowed"))
        if any(token in scalar_lower for token in CONSEQUENTIAL_ACTION_LANGUAGE):
            errors.append(PacketValidationError("consequential_action.value", path, "consequential action language is not allowed in inactive reviewer packets"))
        if key_lower in ACTIVE_MUTATION_KEYS or any(token in scalar_lower for token in ACTIVE_MUTATION_TEXT):
            errors.append(PacketValidationError("active_mutation.value", path, "active artifact, prompt, release-state, fixture, or agent-state mutation flags are not allowed"))
        if key_lower in ACTIVE_MUTATION_KEYS and scalar_lower in ("true", "1", "yes"):
            errors.append(PacketValidationError("active_mutation.flag", path, "active mutation flags must not be enabled"))


def _walk(value: Any, path: str = "$", key: str = "") -> Iterable[tuple[str, str, str]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{path}.{child_key_text}" if path != "$" else child_key_text
            yield child_path, child_key_text, ""
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child_value in enumerate(value):
            yield from _walk(child_value, f"{path}[{index}]", key)
    elif value is not None:
        yield path, key, str(value)


def _normalize_pathish_text(value: str) -> str:
    if not value:
        return value
    normalized = value.replace("\\", "/")
    try:
        normalized = str(PurePosixPath(normalized))
    except ValueError:
        pass
    return normalized
