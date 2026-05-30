"""Validation for PP&D agent-facing readiness contract coverage packet v3."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

PACKET_TYPE = "ppd.agent_readiness_contract_coverage_packet.v3"
PACKET_VERSION = 3
MODE = "fixture_first_offline_validation_only"

REQUIRED_INPUT_FAMILIES = frozenset(
    {
        "combined_promotion_rehearsal_v3",
        "process_model_fixtures",
        "user_gap_analysis_fixtures",
        "guardrail_bundle_fixtures",
    }
)

REQUIRED_OUTPUT_KINDS = frozenset(
    {
        "missing_information_prompt",
        "stale_conflicting_evidence_notice",
        "reversible_draft_preview",
        "blocked_action_explanation",
        "next_safe_read_only_action",
    }
)

ALLOWED_NEXT_ACTION_CLASSIFICATIONS = frozenset(
    {
        "ask_for_missing_public_fact",
        "surface_stale_or_conflicting_evidence_notice",
        "render_reversible_draft_preview",
        "refuse_consequential_action",
        "prepare_safe_read_only_review_notes",
    }
)

REQUIRED_ATTESTATIONS = frozenset(
    {
        "no_live_llm",
        "no_devhub_access",
        "no_user_data",
        "no_official_action",
    }
)

MUTATION_FLAGS = frozenset(
    {
        "active_prompt_mutation",
        "active_guardrail_mutation",
        "active_source_mutation",
        "active_surface_registry_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    }
)

PRIVATE_USER_FACT_KEYS = frozenset(
    {
        "user_name",
        "applicant_name",
        "owner_name",
        "property_address",
        "site_address",
        "mailing_address",
        "phone",
        "phone_number",
        "email",
        "tax_account",
        "account_number",
        "private_document_path",
        "local_file_path",
    }
)

AUTHENTICATED_DEVHUB_VALUE_KEYS = frozenset(
    {
        "devhub_session",
        "devhub_account_id",
        "devhub_record_id",
        "authenticated_devhub_value",
        "authenticated_field_value",
        "permit_number",
        "application_number",
        "ivr_number",
        "invoice_number",
        "balance_due",
    }
)

RAW_ARTIFACT_KEYS = frozenset(
    {
        "raw_document",
        "raw_document_bytes",
        "downloaded_document",
        "browser_trace",
        "trace_zip",
        "screenshot",
        "har",
        "cookies",
        "local_storage",
        "session_storage",
        "browser_session",
        "auth_state",
        "playwright_state",
    }
)

FORBIDDEN_TEXT_PATTERNS = (
    ("private user facts", re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")),
    ("private user facts", re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b")),
    (
        "private user facts",
        re.compile(r"\b\d{3,6}\s+[A-Za-z0-9 .'-]+\s+(?:st|street|ave|avenue|blvd|road|rd|drive|dr|way|court|ct)\b", re.IGNORECASE),
    ),
    (
        "live LLM or DevHub completion claims",
        re.compile(r"\b(?:live llm|llm completed|devhub completed|devhub submitted|devhub confirmed|completed in devhub|live devhub run)\b", re.IGNORECASE),
    ),
    (
        "legal or permitting outcome guarantees",
        re.compile(r"\b(?:guarantee(?:d|s)?|will be approved|approval is certain|legally sufficient|legal outcome|permit outcome is assured)\b", re.IGNORECASE),
    ),
    (
        "final submission/payment/upload/scheduling/cancellation language",
        re.compile(r"\b(?:final submit|submit the application|submit payment|pay the fee|upload to the official record|schedule the inspection|cancel the permit|certify the acknowledgement|purchase the permit)\b", re.IGNORECASE),
    ),
)


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def _iter_key_values(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(key, str):
                yield key, item
            yield from _iter_key_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_key_values(item)


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def _validate_forbidden_payloads(packet: Mapping[str, Any], errors: list[str]) -> None:
    reported: set[str] = set()
    for key, value in _iter_key_values(packet):
        if key in MUTATION_FLAGS and value:
            errors.append(f"mutation flag {key} must be absent or false")
        if key in PRIVATE_USER_FACT_KEYS:
            reported.add("private user facts")
        if key in AUTHENTICATED_DEVHUB_VALUE_KEYS:
            reported.add("authenticated DevHub values")
        if key in RAW_ARTIFACT_KEYS:
            reported.add("raw document/session/browser artifacts")

    for text in _iter_strings(packet):
        for label, pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(text):
                reported.add(label)

    for label in sorted(reported):
        errors.append(f"coverage packet must not contain {label}")


def validate_contract_coverage_packet_v3(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for the packet. An empty list means valid."""

    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be ppd.agent_readiness_contract_coverage_packet.v3")
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be 3")
    if packet.get("mode") != MODE:
        errors.append("mode must be fixture_first_offline_validation_only")

    consumed = packet.get("consumed_fixture_packets")
    if not isinstance(consumed, list):
        errors.append("consumed_fixture_packets must be a list")
        consumed = []
    families = {source.get("family") for source in consumed if isinstance(source, Mapping)}
    if families != REQUIRED_INPUT_FAMILIES:
        errors.append("consumed_fixture_packets must cover all required input families")
    for source in consumed:
        if not isinstance(source, Mapping):
            errors.append("consumed fixture packet entries must be objects")
            continue
        family = source.get("family", "unknown")
        if source.get("offline_only") is not True:
            errors.append(f"consumed fixture packet {family} must be offline_only")
        fixture_path = source.get("fixture_path")
        if not isinstance(fixture_path, str) or not fixture_path.startswith("ppd/tests/fixtures/"):
            errors.append(f"consumed fixture packet {family} must use a ppd/tests/fixtures path")
        if not _string_list(source.get("citation_evidence_ids")):
            errors.append(f"consumed fixture packet {family} must cite source evidence")

    evidence = packet.get("source_evidence")
    if not isinstance(evidence, list):
        errors.append("source_evidence must be a list")
        evidence = []
    evidence_ids = {item.get("evidence_id") for item in evidence if isinstance(item, Mapping)}
    for item in evidence:
        if not isinstance(item, Mapping):
            errors.append("source evidence entries must be objects")
            continue
        if not item.get("evidence_id") or not item.get("source_family") or not item.get("summary"):
            errors.append("source evidence entries need evidence_id, source_family, and summary")

    outputs = packet.get("expected_api_outputs")
    if not isinstance(outputs, list):
        errors.append("expected_api_outputs must be a list")
        outputs = []
    kinds = {output.get("kind") for output in outputs if isinstance(output, Mapping)}
    if kinds != REQUIRED_OUTPUT_KINDS:
        errors.append("expected_api_outputs must cover all required output kinds")

    for output in outputs:
        if not isinstance(output, Mapping):
            errors.append("expected API output entries must be objects")
            continue
        kind = output.get("kind", "unknown")
        if output.get("kind") not in REQUIRED_OUTPUT_KINDS:
            errors.append(f"output {kind} has unsupported kind")
        citations = output.get("citations")
        if not _string_list(citations):
            errors.append(f"output {kind} must include citations")
        elif not set(citations).issubset(evidence_ids):
            errors.append(f"output {kind} cites unknown evidence")
        if output.get("next_action_classification") not in ALLOWED_NEXT_ACTION_CLASSIFICATIONS:
            errors.append(f"output {kind} has unsupported next_action_classification")
        if not _string_list(output.get("process_refs")):
            errors.append(f"output {kind} needs process_refs")
        if not _string_list(output.get("gap_analysis_refs")):
            errors.append(f"output {kind} needs gap_analysis_refs")
        if not _string_list(output.get("guardrail_refs")):
            errors.append(f"output {kind} needs guardrail_refs")
        api_output = output.get("expected_api_output")
        if not isinstance(api_output, Mapping):
            errors.append(f"output {kind} needs expected_api_output")
        elif not api_output.get("message"):
            errors.append(f"output {kind} expected_api_output needs message")

    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("offline_validation_commands are required")
    elif any(not isinstance(command, list) or not command or command[0] != "python3" for command in commands):
        errors.append("offline_validation_commands must be python3 argv lists")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
    else:
        for key in REQUIRED_ATTESTATIONS:
            if attestations.get(key) is not True:
                errors.append(f"attestation {key} must be true")

    _validate_forbidden_payloads(packet, errors)
    return errors


def assert_valid_contract_coverage_packet_v3(packet: Mapping[str, Any]) -> None:
    """Raise ValueError if the packet violates the v3 coverage contract."""

    errors = validate_contract_coverage_packet_v3(packet)
    if errors:
        raise ValueError("invalid agent readiness contract coverage packet v3: " + "; ".join(errors))
