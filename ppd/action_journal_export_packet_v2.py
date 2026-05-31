"""Validation for fixture-first PP&D action journal export packet v2."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping


PACKET_VERSION = "action-journal-export-packet-v2"

REQUIRED_EVENT_TYPES = (
    "public_crawl_preflight",
    "public_crawl_metadata_capture",
    "requirement_extraction",
    "user_gap_analysis",
    "reversible_draft_planning",
    "devhub_attended_preflight",
    "refusal",
    "manual_handoff",
    "completion_evidence",
)

REQUIRED_ATTESTATIONS = frozenset(
    {
        "no_credentials",
        "no_cookies",
        "no_auth_state",
        "no_screenshots",
        "no_traces",
        "no_har_data",
        "no_payment_details",
        "no_private_values",
        "no_raw_downloads",
        "no_local_private_paths",
        "no_official_action_completed",
        "offline_fixture_only",
    }
)

EXPECTED_OFFLINE_VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

_REQUIRED_PACKET_FLAGS = {
    "fixture_first": True,
    "commit_safe": True,
    "live_crawl_performed": False,
    "browser_automation_performed": False,
    "official_action_performed": False,
}

_REQUIRED_EVENT_FIELDS = frozenset(
    {
        "row_id",
        "event_type",
        "occurred_at",
        "actor",
        "source_evidence_ids",
        "guardrail_refs",
        "redacted_summary",
        "redaction_check",
        "commit_safe_reason",
        "offline_validation_commands",
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
        "download",
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
        "private_field_value",
        "private_field_values",
        "private_path",
        "private_value",
        "raw_body",
        "raw_crawl_output",
        "raw_download",
        "raw_downloads",
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

_PROHIBITED_VALUE_PATTERNS = {
    "browser artifact": re.compile(r"\.(?:har|trace|png|jpe?g|webp|zip)\b", re.IGNORECASE),
    "credential material": re.compile(
        r"\b(?:bearer\s+[A-Za-z0-9._~-]+|password|set-cookie|sessionid|xsrf|csrf|api[_ -]?key)\b",
        re.IGNORECASE,
    ),
    "local private path": re.compile(r"(?:file://|/(?:home|Users|private|tmp|var/folders)/[^\s]+|[A-Za-z]:\\\\[^\s]+)"),
    "payment number": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "private value": re.compile(r"\b(?:actual user value|private field value|unredacted field value|applicant ssn)\b", re.IGNORECASE),
    "raw material": re.compile(r"\b(?:raw crawl output|raw download|full html body|full pdf text)\b", re.IGNORECASE),
    "official completion claim": re.compile(
        r"\b(?:submitted|uploaded|scheduled|paid|receipt|official action completed|payment completed)\b",
        re.IGNORECASE,
    ),
}


@dataclass(frozen=True)
class ActionJournalExportPacketV2Result:
    """Validation result for a fixture-first action journal export packet v2."""

    ok: bool
    problems: tuple[str, ...]
    row_count: int
    event_types: tuple[str, ...]


def validate_action_journal_export_packet_v2(packet: Mapping[str, Any]) -> ActionJournalExportPacketV2Result:
    """Validate a committed v2 action journal export packet.

    The packet is intentionally fixture-first. It demonstrates journal rows and
    offline validation commands while rejecting committed private values,
    browser artifacts, raw downloads, payment details, and official action claims.
    """

    if not isinstance(packet, Mapping):
        return ActionJournalExportPacketV2Result(False, ("packet must be an object",), 0, ())

    problems: list[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be action-journal-export-packet-v2")

    for field, expected in _REQUIRED_PACKET_FLAGS.items():
        if packet.get(field) is not expected:
            problems.append(f"{field} must be {expected!r}")

    commands = packet.get("offline_validation_commands")
    if commands != EXPECTED_OFFLINE_VALIDATION_COMMANDS:
        problems.append("offline_validation_commands must exactly match the PP&D daemon self-test command")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        problems.append("attestations must be an object")
        attestations = {}
    for name in sorted(REQUIRED_ATTESTATIONS):
        if attestations.get(name) is not True:
            problems.append(f"attestations.{name} must be True")

    rows = packet.get("event_rows")
    if not isinstance(rows, list):
        problems.append("event_rows must be a list")
        rows = []

    seen_row_ids: set[str] = set()
    seen_event_types: list[str] = []
    for index, row in enumerate(rows):
        path = f"event_rows[{index}]"
        if not isinstance(row, Mapping):
            problems.append(f"{path} must be an object")
            continue
        problems.extend(_validate_row(row, path, seen_row_ids))
        event_type = row.get("event_type")
        if isinstance(event_type, str):
            seen_event_types.append(event_type)
        problems.extend(_walk_for_restricted_material(row, path))

    if tuple(seen_event_types) != REQUIRED_EVENT_TYPES:
        problems.append("event_rows must include required v2 event types in deterministic order")

    return ActionJournalExportPacketV2Result(
        ok=not problems,
        problems=tuple(problems),
        row_count=len(rows),
        event_types=tuple(seen_event_types),
    )


def assert_action_journal_export_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise AssertionError when a v2 export packet is not commit-safe."""

    result = validate_action_journal_export_packet_v2(packet)
    if not result.ok:
        raise AssertionError("invalid action journal export packet v2:\n" + "\n".join(result.problems))


def _validate_row(row: Mapping[str, Any], path: str, seen_row_ids: set[str]) -> list[str]:
    problems: list[str] = []
    for field in sorted(_REQUIRED_EVENT_FIELDS.difference(row)):
        problems.append(f"{path}.{field} is required")

    row_id = row.get("row_id")
    if not _is_non_empty_string(row_id):
        problems.append(f"{path}.row_id must be a non-empty string")
    elif row_id in seen_row_ids:
        problems.append(f"{path}.row_id is duplicated")
    else:
        seen_row_ids.add(row_id)

    if row.get("event_type") not in REQUIRED_EVENT_TYPES:
        problems.append(f"{path}.event_type is unsupported")

    for field in ("occurred_at", "actor", "redacted_summary", "commit_safe_reason"):
        if not _is_non_empty_string(row.get(field)):
            problems.append(f"{path}.{field} must be a non-empty string")

    for field in ("source_evidence_ids", "guardrail_refs"):
        if not _is_non_empty_string_list(row.get(field)):
            problems.append(f"{path}.{field} must be a non-empty list of strings")

    if row.get("offline_validation_commands") != EXPECTED_OFFLINE_VALIDATION_COMMANDS:
        problems.append(f"{path}.offline_validation_commands must exactly match packet commands")

    redaction = row.get("redaction_check")
    if not isinstance(redaction, Mapping):
        problems.append(f"{path}.redaction_check must be an object")
    else:
        if redaction.get("passed") is not True:
            problems.append(f"{path}.redaction_check.passed must be True")
        if redaction.get("raw_values_committed") is not False:
            problems.append(f"{path}.redaction_check.raw_values_committed must be False")
        checks = redaction.get("checks")
        if not _is_non_empty_string_list(checks):
            problems.append(f"{path}.redaction_check.checks must be a non-empty list of strings")

    return problems


def _walk_for_restricted_material(value: Any, path: str) -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized = _normalize_key(key_text)
            if normalized in _PROHIBITED_KEY_TERMS:
                problems.append(f"{child_path} uses a prohibited sensitive key")
            problems.extend(_walk_for_restricted_material(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_walk_for_restricted_material(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        for reason, pattern in _PROHIBITED_VALUE_PATTERNS.items():
            if pattern.search(value):
                problems.append(f"{path} contains prohibited {reason}")
    return problems


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_is_non_empty_string(item) for item in value)


__all__ = [
    "EXPECTED_OFFLINE_VALIDATION_COMMANDS",
    "PACKET_VERSION",
    "REQUIRED_ATTESTATIONS",
    "REQUIRED_EVENT_TYPES",
    "ActionJournalExportPacketV2Result",
    "assert_action_journal_export_packet_v2",
    "validate_action_journal_export_packet_v2",
]
