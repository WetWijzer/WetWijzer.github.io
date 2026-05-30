"""Validation for guarded agent readiness delta packet v2.

The packet is intentionally conservative: readiness deltas may describe
placeholders, expectations, citations, reviewer gates, and validation commands,
but must not contain private artifacts, live crawl claims, guarantees, official
action claims, or active mutation flags.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_VERSION = "guarded-agent-readiness-delta-v2"

REQUIRED_TOP_LEVEL_FIELDS = (
    "packet_version",
    "schema_delta_placeholders",
    "expectations",
    "citation_coverage_placeholders",
    "reviewer_acceptance_placeholders",
    "validation_commands",
)

REQUIRED_EXPECTATION_FIELDS = (
    "missing_information_prompts",
    "blocked_action_explanations",
    "reversible_draft_previews",
)

MUTATION_FLAG_FIELDS = (
    "active_prompt_mutation",
    "active_contract_mutation",
    "active_source_mutation",
    "active_surface_mutation",
    "active_guardrail_mutation",
    "active_release_state_mutation",
)

_PRIVATE_ARTIFACT_PATTERNS = (
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "password",
    "auth_state",
    "storage_state",
    "session_state",
    "session_storage",
    "local_storage",
    "playwright_trace",
    "trace.zip",
    "har",
    "screenshot",
    "raw_html",
    "raw_body",
    "raw_crawl",
    "downloaded_document",
    "downloaded_pdf",
    "downloads/",
    "private_devhub",
)

_LIVE_CLAIM_PATTERNS = (
    "live crawl",
    "live devhub",
    "crawled devhub",
    "scraped devhub",
    "authenticated crawl",
    "authenticated devhub crawl",
    "ran playwright against devhub",
    "downloaded from devhub",
    "captured devhub session",
)

_OFFICIAL_ACTION_PATTERNS = (
    "submitted the permit",
    "submit the permit",
    "submitted application",
    "certified acknowledgement",
    "paid the fee",
    "made payment",
    "scheduled inspection",
    "cancelled inspection",
    "canceled inspection",
    "uploaded correction",
    "purchased permit",
    "issued permit",
)

_GUARANTEE_PATTERNS = (
    "guaranteed approval",
    "guarantees approval",
    "will be approved",
    "permit is approved",
    "legally sufficient",
    "legal advice",
    "complies with all code",
    "no review required",
    "approval is certain",
)


@dataclass(frozen=True)
class ReadinessDeltaValidationError:
    """A single deterministic packet validation error."""

    code: str
    path: str
    message: str


def validate_guarded_agent_readiness_delta_packet_v2(
    packet: Mapping[str, Any],
) -> list[ReadinessDeltaValidationError]:
    """Return all validation errors for a guarded readiness delta packet v2."""

    errors: list[ReadinessDeltaValidationError] = []

    if not isinstance(packet, Mapping):
        return [
            ReadinessDeltaValidationError(
                "packet_not_mapping",
                "$",
                "Readiness delta packet must be a mapping.",
            )
        ]

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in packet:
            errors.append(
                ReadinessDeltaValidationError(
                    "missing_required_field",
                    f"$.{field}",
                    f"Missing required field: {field}.",
                )
            )

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append(
            ReadinessDeltaValidationError(
                "invalid_packet_version",
                "$.packet_version",
                f"packet_version must be {PACKET_VERSION!r}.",
            )
        )

    _require_non_empty_sequence(
        packet,
        "schema_delta_placeholders",
        "missing_schema_delta_placeholders",
        errors,
    )
    _require_non_empty_sequence(
        packet,
        "citation_coverage_placeholders",
        "missing_citation_coverage_placeholders",
        errors,
    )
    _require_non_empty_sequence(
        packet,
        "reviewer_acceptance_placeholders",
        "missing_reviewer_acceptance_placeholders",
        errors,
    )
    _validate_expectations(packet.get("expectations"), errors)
    _validate_commands(packet.get("validation_commands"), errors)
    _validate_mutation_flags(packet, errors)
    _scan_forbidden_content(packet, errors)

    return errors


def assert_guarded_agent_readiness_delta_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a readiness delta packet v2 is invalid."""

    errors = validate_guarded_agent_readiness_delta_packet_v2(packet)
    if errors:
        details = "; ".join(f"{error.code} at {error.path}" for error in errors)
        raise ValueError(f"Invalid guarded agent readiness delta packet v2: {details}")


def _require_non_empty_sequence(
    packet: Mapping[str, Any],
    field: str,
    code: str,
    errors: list[ReadinessDeltaValidationError],
) -> None:
    value = packet.get(field)
    if not _is_non_empty_sequence(value):
        errors.append(
            ReadinessDeltaValidationError(
                code,
                f"$.{field}",
                f"{field} must be a non-empty sequence of placeholders.",
            )
        )


def _validate_expectations(
    expectations: Any,
    errors: list[ReadinessDeltaValidationError],
) -> None:
    if not isinstance(expectations, Mapping):
        errors.append(
            ReadinessDeltaValidationError(
                "missing_expectations",
                "$.expectations",
                "expectations must be a mapping.",
            )
        )
        return

    for field in REQUIRED_EXPECTATION_FIELDS:
        if not _is_non_empty_sequence(expectations.get(field)):
            errors.append(
                ReadinessDeltaValidationError(
                    f"missing_{field}",
                    f"$.expectations.{field}",
                    f"expectations.{field} must be a non-empty sequence.",
                )
            )


def _validate_commands(
    commands: Any,
    errors: list[ReadinessDeltaValidationError],
) -> None:
    if not _is_non_empty_sequence(commands):
        errors.append(
            ReadinessDeltaValidationError(
                "missing_validation_commands",
                "$.validation_commands",
                "validation_commands must be a non-empty sequence.",
            )
        )
        return

    for index, command in enumerate(commands):
        if not _is_non_empty_sequence(command) or not all(
            isinstance(part, str) and part.strip() for part in command
        ):
            errors.append(
                ReadinessDeltaValidationError(
                    "invalid_validation_command",
                    f"$.validation_commands[{index}]",
                    "Each validation command must be a non-empty sequence of strings.",
                )
            )


def _validate_mutation_flags(
    packet: Mapping[str, Any],
    errors: list[ReadinessDeltaValidationError],
) -> None:
    for field in MUTATION_FLAG_FIELDS:
        if packet.get(field) is True:
            errors.append(
                ReadinessDeltaValidationError(
                    "active_mutation_flag",
                    f"$.{field}",
                    f"{field} must not be active in a readiness delta packet.",
                )
            )


def _scan_forbidden_content(
    value: Any,
    errors: list[ReadinessDeltaValidationError],
    path: str = "$",
) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_path = f"{path}.{key}" if isinstance(key, str) else f"{path}[{key!r}]"
            _scan_text(str(key), key_path, errors)
            _scan_forbidden_content(child, errors, key_path)
        return

    if isinstance(value, str):
        _scan_text(value, path, errors)
        return

    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_forbidden_content(child, errors, f"{path}[{index}]")


def _scan_text(
    text: str,
    path: str,
    errors: list[ReadinessDeltaValidationError],
) -> None:
    normalized = text.lower().replace("\\", "/")
    checks = (
        ("private_or_session_artifact", _PRIVATE_ARTIFACT_PATTERNS),
        ("live_devhub_or_crawl_claim", _LIVE_CLAIM_PATTERNS),
        ("consequential_official_action_language", _OFFICIAL_ACTION_PATTERNS),
        ("legal_or_permitting_guarantee", _GUARANTEE_PATTERNS),
    )
    for code, patterns in checks:
        if any(pattern in normalized for pattern in patterns):
            errors.append(
                ReadinessDeltaValidationError(
                    code,
                    path,
                    f"Forbidden readiness delta content matched {code}.",
                )
            )


def _is_non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)
