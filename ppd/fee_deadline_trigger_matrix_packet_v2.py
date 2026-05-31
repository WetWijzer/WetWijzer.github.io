"""Validation for PP&D fee and deadline trigger matrix packet v2.

The packet is a review artifact, not an authority source and not an action plan.
It must stay fixture-first, source-placeholder based, and free of payment,
private browser/session, live crawl, DevHub, guarantee, or mutation claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


PACKET_VERSION = "fee_deadline_trigger_matrix_packet_v2"

REQUIRED_TOP_LEVEL_FIELDS = (
    "packet_version",
    "fee_trigger_rows",
    "deadline_or_expiration_cues",
    "payment_boundary_warnings",
    "source_evidence_placeholders",
    "stale_source_hold_notes",
    "blocked_financial_action_reminders",
    "reviewer_dispositions",
    "validation_commands",
)

MUTATION_FLAG_FIELDS = (
    "active_requirement_mutation",
    "active_process_model_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_contract_mutation",
    "active_source_mutation",
    "active_devhub_surface_mutation",
    "active_release_state_mutation",
)

PAYMENT_DETAIL_MARKERS = (
    "card_number",
    "credit_card",
    "debit_card",
    "cvv",
    "cvc",
    "routing_number",
    "account_number",
    "bank_account",
    "payment_token",
    "billing_zip",
)

PRIVATE_ARTIFACT_MARKERS = (
    "cookie",
    "session_storage",
    "local_storage",
    "auth_state",
    "storage_state",
    "trace.zip",
    ".har",
    "screenshot",
    "browser_profile",
    "downloaded_document",
    "raw_html",
    "raw_pdf",
    "private_upload",
)

LIVE_OR_DEVHUB_CLAIM_MARKERS = (
    "live crawl completed",
    "live crawl verified",
    "crawled devhub",
    "authenticated devhub",
    "devhub session captured",
    "browser automation completed",
    "logged in to devhub",
)

GUARANTEE_MARKERS = (
    "legal advice",
    "legally guaranteed",
    "permit guaranteed",
    "approval guaranteed",
    "will be approved",
    "guarantees issuance",
    "guarantees compliance",
)


@dataclass(frozen=True)
class ValidationFinding:
    """A deterministic packet validation finding."""

    code: str
    path: str
    message: str


def validate_fee_deadline_trigger_matrix_packet_v2(packet: Mapping[str, Any]) -> list[ValidationFinding]:
    """Return validation findings for a fee/deadline trigger matrix packet."""

    findings: list[ValidationFinding] = []

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in packet:
            findings.append(
                ValidationFinding(
                    code="missing_required_field",
                    path=field,
                    message=f"Missing required packet field: {field}",
                )
            )

    if packet.get("packet_version") != PACKET_VERSION:
        findings.append(
            ValidationFinding(
                code="invalid_packet_version",
                path="packet_version",
                message=f"packet_version must be {PACKET_VERSION}",
            )
        )

    _require_non_empty_sequence(findings, packet, "fee_trigger_rows", "missing_fee_trigger_rows")
    _require_non_empty_sequence(
        findings,
        packet,
        "deadline_or_expiration_cues",
        "missing_deadline_or_expiration_cues",
    )
    _require_non_empty_sequence(
        findings,
        packet,
        "payment_boundary_warnings",
        "missing_payment_boundary_warnings",
    )
    _require_non_empty_sequence(
        findings,
        packet,
        "source_evidence_placeholders",
        "missing_source_evidence_placeholders",
    )
    _require_non_empty_sequence(
        findings,
        packet,
        "stale_source_hold_notes",
        "missing_stale_source_hold_notes",
    )
    _require_non_empty_sequence(
        findings,
        packet,
        "blocked_financial_action_reminders",
        "missing_blocked_financial_action_reminders",
    )
    _require_non_empty_sequence(
        findings,
        packet,
        "reviewer_dispositions",
        "missing_reviewer_dispositions",
    )
    _require_validation_commands(findings, packet.get("validation_commands"))
    _require_fee_row_evidence_and_disposition(findings, packet.get("fee_trigger_rows"))
    _reject_mutation_flags(findings, packet)
    _reject_prohibited_text(findings, packet)

    return findings


def is_valid_fee_deadline_trigger_matrix_packet_v2(packet: Mapping[str, Any]) -> bool:
    """Return True when the packet has no validation findings."""

    return not validate_fee_deadline_trigger_matrix_packet_v2(packet)


def _require_non_empty_sequence(
    findings: list[ValidationFinding],
    packet: Mapping[str, Any],
    field: str,
    code: str,
) -> None:
    value = packet.get(field)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        findings.append(
            ValidationFinding(
                code=code,
                path=field,
                message=f"{field} must be a non-empty list",
            )
        )


def _require_validation_commands(findings: list[ValidationFinding], value: Any) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        findings.append(
            ValidationFinding(
                code="missing_validation_commands",
                path="validation_commands",
                message="validation_commands must contain at least one command list",
            )
        )
        return

    for index, command in enumerate(value):
        if (
            not isinstance(command, Sequence)
            or isinstance(command, (str, bytes))
            or not command
            or not all(isinstance(part, str) and part for part in command)
        ):
            findings.append(
                ValidationFinding(
                    code="invalid_validation_command",
                    path=f"validation_commands[{index}]",
                    message="Each validation command must be a non-empty list of strings",
                )
            )


def _require_fee_row_evidence_and_disposition(
    findings: list[ValidationFinding], value: Any
) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return

    for index, row in enumerate(value):
        if not isinstance(row, Mapping):
            findings.append(
                ValidationFinding(
                    code="invalid_fee_trigger_row",
                    path=f"fee_trigger_rows[{index}]",
                    message="Each fee trigger row must be an object",
                )
            )
            continue

        if not row.get("source_evidence_placeholder"):
            findings.append(
                ValidationFinding(
                    code="missing_fee_row_source_evidence_placeholder",
                    path=f"fee_trigger_rows[{index}].source_evidence_placeholder",
                    message="Each fee trigger row must carry a source evidence placeholder",
                )
            )
        if not row.get("reviewer_disposition"):
            findings.append(
                ValidationFinding(
                    code="missing_fee_row_reviewer_disposition",
                    path=f"fee_trigger_rows[{index}].reviewer_disposition",
                    message="Each fee trigger row must carry a reviewer disposition",
                )
            )


def _reject_mutation_flags(findings: list[ValidationFinding], packet: Mapping[str, Any]) -> None:
    mutation_flags = packet.get("mutation_flags", {})
    if mutation_flags is None:
        mutation_flags = {}
    if not isinstance(mutation_flags, Mapping):
        findings.append(
            ValidationFinding(
                code="invalid_mutation_flags",
                path="mutation_flags",
                message="mutation_flags must be an object when present",
            )
        )
        return

    for field in MUTATION_FLAG_FIELDS:
        value = mutation_flags.get(field, packet.get(field, False))
        if value is True:
            findings.append(
                ValidationFinding(
                    code="active_mutation_flag",
                    path=f"mutation_flags.{field}" if field in mutation_flags else field,
                    message=f"Active mutation flag is not allowed: {field}",
                )
            )


def _reject_prohibited_text(findings: list[ValidationFinding], packet: Mapping[str, Any]) -> None:
    haystack = "\n".join(_flatten_text(packet)).lower()
    marker_groups = (
        (PAYMENT_DETAIL_MARKERS, "payment_detail_present", "Packet must not contain payment details"),
        (
            PRIVATE_ARTIFACT_MARKERS,
            "private_or_raw_artifact_present",
            "Packet must not contain private/session/browser/raw/downloaded artifact references",
        ),
        (
            LIVE_OR_DEVHUB_CLAIM_MARKERS,
            "live_crawl_or_devhub_claim_present",
            "Packet must not claim live crawl or authenticated DevHub completion",
        ),
        (
            GUARANTEE_MARKERS,
            "legal_or_permitting_guarantee_present",
            "Packet must not contain legal or permitting guarantees",
        ),
    )

    for markers, code, message in marker_groups:
        for marker in markers:
            if marker in haystack:
                findings.append(ValidationFinding(code=code, path="$", message=message))
                break


def _flatten_text(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for key, nested in value.items():
            yield str(key)
            yield from _flatten_text(nested)
    elif isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        for nested in value:
            yield from _flatten_text(nested)
    elif value is not None:
        yield str(value)
