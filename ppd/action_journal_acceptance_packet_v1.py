"""Validation for fixture-first action journal acceptance packet v1."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping


PACKET_VERSION = "action-journal-acceptance-packet-v1"

REQUIRED_EVENT_TYPES = frozenset(
    {
        "public_crawl_preflight",
        "requirement_extraction",
        "user_gap_analysis",
        "reversible_draft_preview",
        "devhub_read_only_observation",
        "refusal",
    }
)

REQUIRED_ATTESTATIONS = frozenset(
    {
        "no_credentials",
        "no_cookies",
        "no_auth_state",
        "no_private_values",
        "no_screenshots",
        "no_traces",
        "no_har",
        "no_payment",
        "no_private_local_paths",
        "no_raw_crawl_or_pdf_bodies",
        "no_uncited_event_evidence",
        "no_unsupported_event_types",
        "no_legal_or_permitting_outcome_guarantees",
        "no_official_action",
        "no_authenticated_devhub_session",
        "no_downloaded_documents",
        "no_active_source_mutation",
        "no_active_surface_registry_mutation",
        "no_active_guardrail_mutation",
        "no_active_prompt_mutation",
        "no_active_release_state_mutation",
        "no_active_agent_state_mutation",
    }
)

_REQUIRED_EVENT_FIELDS = frozenset(
    {
        "event_id",
        "event_type",
        "source_fixture",
        "owner",
        "reviewer",
        "citations",
        "redacted_evidence_summary",
        "commit_safe_reason",
    }
)

_PROHIBITED_KEY_TERMS = frozenset(
    {
        "absolute_path",
        "account_number",
        "auth",
        "auth_state",
        "bank",
        "card",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "csrf",
        "cvv",
        "downloaded_document",
        "field_value",
        "field_values",
        "form_value",
        "form_values",
        "har",
        "har_data",
        "local_path",
        "local_private_path",
        "page_value",
        "page_values",
        "password",
        "payment",
        "payment_detail",
        "payment_details",
        "pdf_body",
        "private_field_value",
        "private_field_values",
        "private_path",
        "private_value",
        "raw_body",
        "raw_crawl_body",
        "raw_crawl_output",
        "raw_pdf_body",
        "secret",
        "session",
        "screenshot",
        "screenshots",
        "ssn",
        "storage_state",
        "trace",
        "traces",
        "token",
        "upload_payload",
    }
)

_MUTATION_FLAG_KEYS = frozenset(
    {
        "source_mutation",
        "source_registry_mutation",
        "surface_mutation",
        "surface_registry_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "release_state_mutation",
        "agent_state_mutation",
    }
)

_PROHIBITED_VALUE_PATTERNS = {
    "credential": re.compile(r"\b(?:bearer\s+[A-Za-z0-9._~-]+|password|api[_ -]?key|secret token)\b", re.IGNORECASE),
    "cookie": re.compile(r"\b(?:set-cookie|cookie:|sessionid|xsrf|csrf)\b", re.IGNORECASE),
    "browser artifact": re.compile(r"\.(?:har|trace|png|jpe?g|webp|zip)\b", re.IGNORECASE),
    "private local path": re.compile(r"(?:file://|/(?:home|Users|private|tmp|var/folders)/[^\s]+|[A-Za-z]:\\\\[^\s]+)"),
    "payment details": re.compile(r"\b(?:cvv|card number|routing number|payment detail|(?:\d[ -]*?){13,19})\b", re.IGNORECASE),
    "private value": re.compile(r"\b(?:actual user value|private field value|unredacted field value|applicant ssn)\b", re.IGNORECASE),
    "raw body": re.compile(r"\b(?:raw crawl body|raw crawl output|raw pdf body|raw PDF body|full html body|full pdf text)\b", re.IGNORECASE),
    "outcome guarantee": re.compile(r"\b(?:guarantee[sd]?|will be approved|permit approval is assured|legal outcome is assured|issuance is guaranteed)\b", re.IGNORECASE),
}

_MUTATION_VALUE_PATTERN = re.compile(
    r"\b(?:mutate|write|promote|activate|update)\b.{0,80}\b(?:source registry|surface registry|guardrail|prompt|release state|agent state)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ActionJournalAcceptancePacketV1Result:
    """Validation result for an action journal acceptance packet v1."""

    ok: bool
    problems: tuple[str, ...]
    event_count: int
    event_types: tuple[str, ...]


def validate_action_journal_acceptance_packet_v1(packet: Mapping[str, Any]) -> ActionJournalAcceptancePacketV1Result:
    """Validate a commit-safe action journal acceptance packet v1.

    The validator is intentionally fixture-first and fail-closed. It accepts only
    the supported v1 event types, requires cited event evidence, and rejects
    sensitive committed artifacts, private values, raw bodies, outcome guarantees,
    and active mutation flags for PP&D source, surface, guardrail, prompt,
    release-state, or agent-state artifacts.
    """

    if not isinstance(packet, Mapping):
        return ActionJournalAcceptancePacketV1Result(False, ("packet must be an object",), 0, ())

    problems: list[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be action-journal-acceptance-packet-v1")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be True")
    if packet.get("commit_safe") is not True:
        problems.append("commit_safe must be True")

    commands = packet.get("offline_validation_commands")
    if commands != [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]:
        problems.append("offline_validation_commands must include the PP&D daemon self-test only")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        problems.append("attestations must be an object")
        attestations = {}
    for name in sorted(REQUIRED_ATTESTATIONS):
        if attestations.get(name) is not True:
            problems.append(f"attestations.{name} must be True")

    reviewer_fields = packet.get("reviewer_owner_fields")
    if not isinstance(reviewer_fields, Mapping):
        problems.append("reviewer_owner_fields must be an object")
    else:
        for field in ("packet_owner", "technical_reviewer", "policy_reviewer"):
            if not _is_non_empty_string(reviewer_fields.get(field)):
                problems.append(f"reviewer_owner_fields.{field} must be a non-empty string")

    coverage = packet.get("event_type_coverage")
    if not _is_non_empty_string_list(coverage):
        problems.append("event_type_coverage must be a non-empty list of strings")
        coverage_set: set[str] = set()
    else:
        coverage_set = set(coverage)
        if coverage_set != set(REQUIRED_EVENT_TYPES):
            problems.append("event_type_coverage must exactly match supported v1 event types")

    events = packet.get("journal_events")
    if not isinstance(events, list):
        problems.append("journal_events must be a list")
        events = []

    seen_event_ids: set[str] = set()
    seen_event_types: set[str] = set()
    for index, event in enumerate(events):
        path = f"journal_events[{index}]"
        if not isinstance(event, Mapping):
            problems.append(f"{path} must be an object")
            continue
        problems.extend(_validate_event(event, path, seen_event_ids))
        event_type = event.get("event_type")
        if isinstance(event_type, str):
            seen_event_types.add(event_type)
        problems.extend(_walk_for_restricted_material(event, path))

    if seen_event_types != set(REQUIRED_EVENT_TYPES):
        problems.append("journal_events must include exactly the supported v1 event types")
    if coverage_set and seen_event_types != coverage_set:
        problems.append("event_type_coverage must match journal event types")

    mutation_flags = packet.get("mutation_flags", {})
    if mutation_flags not in ({}, None):
        if not isinstance(mutation_flags, Mapping):
            problems.append("mutation_flags must be an object when present")
        else:
            problems.extend(_validate_mutation_flags(mutation_flags, "mutation_flags"))

    return ActionJournalAcceptancePacketV1Result(
        ok=not problems,
        problems=tuple(problems),
        event_count=len(events),
        event_types=tuple(sorted(seen_event_types)),
    )


def assert_action_journal_acceptance_packet_v1(packet: Mapping[str, Any]) -> None:
    """Raise AssertionError when a packet is not safe to accept."""

    result = validate_action_journal_acceptance_packet_v1(packet)
    if not result.ok:
        raise AssertionError("invalid action journal acceptance packet v1:\n" + "\n".join(result.problems))


def _validate_event(event: Mapping[str, Any], path: str, seen_event_ids: set[str]) -> list[str]:
    problems: list[str] = []
    missing = sorted(_REQUIRED_EVENT_FIELDS.difference(event))
    for field in missing:
        problems.append(f"{path}.{field} is required")

    event_id = event.get("event_id")
    if not _is_non_empty_string(event_id):
        problems.append(f"{path}.event_id must be a non-empty string")
    elif event_id in seen_event_ids:
        problems.append(f"{path}.event_id is duplicated")
    else:
        seen_event_ids.add(event_id)

    event_type = event.get("event_type")
    if event_type not in REQUIRED_EVENT_TYPES:
        problems.append(f"{path}.event_type is unsupported")

    source_fixture = event.get("source_fixture")
    if not _is_non_empty_string(source_fixture) or not source_fixture.startswith("ppd/tests/fixtures/"):
        problems.append(f"{path}.source_fixture must point under ppd/tests/fixtures")

    for field in ("owner", "reviewer", "commit_safe_reason"):
        if not _is_non_empty_string(event.get(field)):
            problems.append(f"{path}.{field} must be a non-empty string")

    citations = event.get("citations")
    if not isinstance(citations, list) or not citations:
        problems.append(f"{path}.citations must be a non-empty list")
    else:
        for index, citation in enumerate(citations):
            citation_path = f"{path}.citations[{index}]"
            if not isinstance(citation, Mapping):
                problems.append(f"{citation_path} must be an object")
                continue
            if not _is_non_empty_string(citation.get("label")):
                problems.append(f"{citation_path}.label must be a non-empty string")
            url = citation.get("url")
            if not _is_non_empty_string(url) or not url.startswith("https://"):
                problems.append(f"{citation_path}.url must be an https URL")

    summary = event.get("redacted_evidence_summary")
    if not isinstance(summary, Mapping):
        problems.append(f"{path}.redacted_evidence_summary must be an object")
    else:
        if not _is_non_empty_string(summary.get("summary")):
            problems.append(f"{path}.redacted_evidence_summary.summary must be a non-empty string")
        if not _is_non_empty_string_list(summary.get("redactions_applied")):
            problems.append(f"{path}.redacted_evidence_summary.redactions_applied must be a non-empty list of strings")
        if summary.get("raw_evidence_included") is not False:
            problems.append(f"{path}.redacted_evidence_summary.raw_evidence_included must be False")

    return problems


def _validate_mutation_flags(flags: Mapping[str, Any], path: str) -> list[str]:
    problems: list[str] = []
    for key, value in flags.items():
        normalized = _normalize_key(str(key))
        if normalized in _MUTATION_FLAG_KEYS and value not in (False, None):
            problems.append(f"{path}.{key} must not enable active mutation")
        if isinstance(value, Mapping):
            problems.extend(_validate_mutation_flags(value, f"{path}.{key}"))
        elif isinstance(value, list):
            if normalized in {"active_mutation_flags", "mutation_flags"} and value:
                problems.append(f"{path}.{key} must be empty")
            for index, item in enumerate(value):
                if isinstance(item, str) and _MUTATION_VALUE_PATTERN.search(item):
                    problems.append(f"{path}.{key}[{index}] contains active mutation language")
        elif isinstance(value, str) and _MUTATION_VALUE_PATTERN.search(value):
            problems.append(f"{path}.{key} contains active mutation language")
    return problems


def _walk_for_restricted_material(value: Any, path: str) -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized = _normalize_key(key_text)
            if _is_prohibited_key(normalized):
                problems.append(f"{child_path} uses a prohibited sensitive key")
            if normalized in _MUTATION_FLAG_KEYS:
                problems.append(f"{child_path} uses an active mutation flag key")
            problems.extend(_walk_for_restricted_material(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_walk_for_restricted_material(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        for reason, pattern in _PROHIBITED_VALUE_PATTERNS.items():
            if pattern.search(value):
                problems.append(f"{path} contains prohibited {reason}")
        if _MUTATION_VALUE_PATTERN.search(value):
            problems.append(f"{path} contains active mutation language")
    return problems


def _is_prohibited_key(normalized_key: str) -> bool:
    parts = set(normalized_key.split("_"))
    return normalized_key in _PROHIBITED_KEY_TERMS or bool(parts.intersection(_PROHIBITED_KEY_TERMS))


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_is_non_empty_string(item) for item in value)


__all__ = [
    "PACKET_VERSION",
    "REQUIRED_ATTESTATIONS",
    "REQUIRED_EVENT_TYPES",
    "ActionJournalAcceptancePacketV1Result",
    "assert_action_journal_acceptance_packet_v1",
    "validate_action_journal_acceptance_packet_v1",
]
