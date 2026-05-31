"""Fixture-first PP&D action journal retention and redaction audit packet v1."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any, Mapping


PACKET_VERSION = "action-journal-retention-redaction-audit-packet-v1"

EXPECTED_OFFLINE_VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

REQUIRED_EVENT_TYPES = (
    "synthetic_public_crawl",
    "requirement_extraction",
    "user_gap_analysis",
    "reversible_draft_plan",
    "devhub_attended_preflight",
    "manual_handoff",
    "refused_action",
    "completion_evidence",
)

ALLOWED_RETENTION_LABELS = frozenset(
    {
        "commit_safe_synthetic_public_metadata_90d",
        "commit_safe_requirement_summary_180d",
        "commit_safe_gap_summary_180d",
        "commit_safe_reversible_draft_summary_90d",
        "commit_safe_attended_preflight_summary_90d",
        "commit_safe_manual_handoff_summary_90d",
        "commit_safe_refusal_summary_180d",
        "commit_safe_completion_evidence_summary_180d",
    }
)

_REQUIRED_PACKET_FLAGS = {
    "fixture_first": True,
    "synthetic_only": True,
    "public_crawl_performed": False,
    "live_source_crawl_performed": False,
    "devhub_opened": False,
    "browser_artifacts_stored": False,
    "private_files_read": False,
    "real_forms_drafted": False,
    "official_action_attempted": False,
    "active_journal_mutated": False,
    "active_export_state_mutated": False,
}

_REQUIRED_EVENT_FIELDS = frozenset(
    {
        "event_id",
        "event_type",
        "occurred_at",
        "actor",
        "citation_refs",
        "retention_label",
        "redacted_values",
        "redaction_audit",
        "commit_safe_reason",
        "offline_validation_commands",
    }
)

_PROHIBITED_KEY_TERMS = frozenset(
    {
        "absolute_path",
        "account_number",
        "active_mutation",
        "active_mutation_flags",
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
        "downloaded_document_ref",
        "downloaded_document_refs",
        "downloaded_document_reference",
        "downloaded_document_references",
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
        "private_values",
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
    "raw material": re.compile(r"\b(?:raw crawl output|raw download|full html body|full pdf text)\b", re.IGNORECASE),
    "downloaded document reference": re.compile(
        r"\b(?:downloaded document|downloaded pdf|download reference|downloaded file)\b",
        re.IGNORECASE,
    ),
}

_PROHIBITED_CLAIM_PATTERNS = {
    "live crawl claim": re.compile(
        r"\b(?:live\s+(?:source\s+)?crawl|live\s+network|recrawled\s+portland|fetched\s+from\s+portland\.gov)\b",
        re.IGNORECASE,
    ),
    "DevHub access claim": re.compile(
        r"\b(?:opened\s+DevHub|logged\s+in(?:to)?\s+DevHub|authenticated\s+DevHub|DevHub\s+session)\b",
        re.IGNORECASE,
    ),
    "official completion claim": re.compile(
        r"\b(?:official\s+action\s+completed|submitted|uploaded|scheduled|paid|certified|payment\s+completed|permit\s+issued|inspection\s+scheduled)\b",
        re.IGNORECASE,
    ),
    "legal or permitting guarantee": re.compile(
        r"\b(?:guarantee(?:d|s)?|will\s+be\s+approved|permit\s+approval\s+is\s+certain|legally\s+valid|legal\s+advice|compliance\s+guarantee)\b",
        re.IGNORECASE,
    ),
}

_REDACTED_VALUE_PATTERN = re.compile(r"^\[REDACTED:[a-z0-9_.-]+\]$")


@dataclass(frozen=True)
class RetentionRedactionAuditResult:
    """Validation result for the v1 fixture-first audit packet."""

    ok: bool
    problems: tuple[str, ...]
    event_count: int
    event_types: tuple[str, ...]


def load_action_journal_retention_redaction_audit_packet_v1(path: str | Path) -> dict[str, Any]:
    """Load a packet JSON object from a committed fixture path."""

    parsed = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("audit packet fixture must contain a JSON object")
    return parsed


def validate_action_journal_retention_redaction_audit_packet_v1(
    packet: Mapping[str, Any],
) -> RetentionRedactionAuditResult:
    """Validate that a synthetic audit packet is commit-safe and complete."""

    if not isinstance(packet, Mapping):
        return RetentionRedactionAuditResult(False, ("packet must be an object",), 0, ())

    problems: list[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append(f"packet_version must be {PACKET_VERSION}")

    for field, expected in _REQUIRED_PACKET_FLAGS.items():
        if packet.get(field) is not expected:
            problems.append(f"{field} must be {expected!r}")

    if packet.get("offline_validation_commands") != EXPECTED_OFFLINE_VALIDATION_COMMANDS:
        problems.append("offline_validation_commands must exactly match the PP&D daemon self-test command")

    citations = packet.get("source_citations")
    citation_ids: set[str] = set()
    if not isinstance(citations, list) or not citations:
        problems.append("source_citations must be a non-empty list")
    else:
        for index, citation in enumerate(citations):
            if not isinstance(citation, Mapping):
                problems.append(f"source_citations[{index}] must be an object")
                continue
            citation_id = citation.get("citation_id")
            if not _is_non_empty_string(citation_id):
                problems.append(f"source_citations[{index}].citation_id must be a non-empty string")
            else:
                citation_ids.add(str(citation_id))
            if not _is_non_empty_string(citation.get("source_kind")):
                problems.append(f"source_citations[{index}].source_kind must be a non-empty string")
            if not _is_non_empty_string(citation.get("synthetic_excerpt_ref")):
                problems.append(f"source_citations[{index}].synthetic_excerpt_ref must be a non-empty string")

    events = packet.get("journal_events")
    if not isinstance(events, list):
        problems.append("journal_events must be a list")
        events = []

    seen_ids: set[str] = set()
    seen_types: list[str] = []
    for index, event in enumerate(events):
        path = f"journal_events[{index}]"
        if not isinstance(event, Mapping):
            problems.append(f"{path} must be an object")
            continue
        problems.extend(_validate_event(event, path, seen_ids, citation_ids))
        event_type = event.get("event_type")
        if isinstance(event_type, str):
            seen_types.append(event_type)
        problems.extend(_walk_for_restricted_material(event, path))

    if tuple(seen_types) != REQUIRED_EVENT_TYPES:
        problems.append("journal_events must include required v1 event types in deterministic order")

    problems.extend(_walk_for_restricted_material(packet, "packet"))

    return RetentionRedactionAuditResult(
        ok=not problems,
        problems=tuple(dict.fromkeys(problems)),
        event_count=len(events),
        event_types=tuple(seen_types),
    )


def assert_action_journal_retention_redaction_audit_packet_v1(packet: Mapping[str, Any]) -> None:
    """Raise AssertionError when the v1 retention/redaction packet is invalid."""

    result = validate_action_journal_retention_redaction_audit_packet_v1(packet)
    if not result.ok:
        raise AssertionError("invalid action journal retention/redaction audit packet v1:\n" + "\n".join(result.problems))


def _validate_event(
    event: Mapping[str, Any],
    path: str,
    seen_ids: set[str],
    citation_ids: set[str],
) -> list[str]:
    problems: list[str] = []
    for field in sorted(_REQUIRED_EVENT_FIELDS.difference(event)):
        problems.append(f"{path}.{field} is required")

    event_id = event.get("event_id")
    if not _is_non_empty_string(event_id):
        problems.append(f"{path}.event_id must be a non-empty string")
    elif str(event_id) in seen_ids:
        problems.append(f"{path}.event_id is duplicated")
    else:
        seen_ids.add(str(event_id))

    if event.get("event_type") not in REQUIRED_EVENT_TYPES:
        problems.append(f"{path}.event_type is unsupported")

    for field in ("occurred_at", "actor", "commit_safe_reason"):
        if not _is_non_empty_string(event.get(field)):
            problems.append(f"{path}.{field} must be a non-empty string")

    refs = event.get("citation_refs")
    if not _is_non_empty_string_list(refs):
        problems.append(f"{path}.citation_refs must be a non-empty list of strings")
    else:
        for ref in refs:
            if ref not in citation_ids:
                problems.append(f"{path}.citation_refs contains unknown citation ref {ref}")

    if event.get("retention_label") not in ALLOWED_RETENTION_LABELS:
        problems.append(f"{path}.retention_label is unsupported")

    if event.get("offline_validation_commands") != EXPECTED_OFFLINE_VALIDATION_COMMANDS:
        problems.append(f"{path}.offline_validation_commands must exactly match packet commands")

    problems.extend(_validate_redacted_values(event.get("redacted_values"), f"{path}.redacted_values"))
    problems.extend(_validate_redaction_audit(event.get("redaction_audit"), f"{path}.redaction_audit"))
    return problems


def _validate_redacted_values(value: Any, path: str) -> list[str]:
    if not isinstance(value, Mapping) or not value:
        return [f"{path} must be a non-empty object"]
    problems: list[str] = []
    for key, item in value.items():
        if not _is_non_empty_string(key):
            problems.append(f"{path} keys must be non-empty strings")
        if not isinstance(item, str) or not _REDACTED_VALUE_PATTERN.match(item):
            problems.append(f"{path}.{key} must be an explicit redaction marker")
    return problems


def _validate_redaction_audit(value: Any, path: str) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{path} must be an object"]
    problems: list[str] = []
    expected_false = (
        "raw_values_committed",
        "private_files_read",
        "browser_artifacts_stored",
        "official_action_attempted",
        "active_journal_mutated",
        "active_export_state_mutated",
    )
    for field in expected_false:
        if field in value and value.get(field) is not False:
            problems.append(f"{path}.{field} must be False")
        if field not in value and field in {"raw_values_committed", "private_files_read", "browser_artifacts_stored", "official_action_attempted"}:
            problems.append(f"{path}.{field} must be False")
    checks = value.get("checks")
    if not _is_non_empty_string_list(checks):
        problems.append(f"{path}.checks must be a non-empty list of strings")
    return problems


def _walk_for_restricted_material(value: Any, path: str) -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if _is_prohibited_key(_normalize_key(key_text)):
                problems.append(f"{child_path} uses a prohibited sensitive key")
            problems.extend(_walk_for_restricted_material(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_walk_for_restricted_material(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        for reason, pattern in _PROHIBITED_VALUE_PATTERNS.items():
            if pattern.search(value):
                problems.append(f"{path} contains prohibited {reason}")
        for reason, pattern in _PROHIBITED_CLAIM_PATTERNS.items():
            if pattern.search(value):
                problems.append(f"{path} contains prohibited {reason}")
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
    "ALLOWED_RETENTION_LABELS",
    "EXPECTED_OFFLINE_VALIDATION_COMMANDS",
    "PACKET_VERSION",
    "REQUIRED_EVENT_TYPES",
    "RetentionRedactionAuditResult",
    "assert_action_journal_retention_redaction_audit_packet_v1",
    "load_action_journal_retention_redaction_audit_packet_v1",
    "validate_action_journal_retention_redaction_audit_packet_v1",
]
