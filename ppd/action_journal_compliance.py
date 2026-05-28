"""Fixture-first compliance validation for PP&D action journal packets."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping


ALLOWED_COMPLIANCE_EVENT_TYPES = frozenset(
    {
        "public crawl preflight",
        "public crawl metadata capture",
        "requirement extraction",
        "local PDF preview",
        "DevHub attended preflight",
        "manual handoff",
        "refused action",
        "completion evidence",
    }
)

_REQUIRED_PACKET_FLAGS = {
    "synthetic_metadata_only": True,
    "redacted_user_visible_summaries_only": True,
    "private_artifacts_committed": False,
    "raw_crawl_output_committed": False,
    "downloaded_documents_committed": False,
}

_REQUIRED_EVENT_FIELDS = frozenset(
    {
        "event_id",
        "event_type",
        "occurred_at",
        "actor",
        "source_evidence_ids",
        "guardrail_evidence_ids",
        "user_visible_summary",
        "synthetic_metadata",
        "redaction",
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
        "payment_detail",
        "payment_details",
        "private_field_value",
        "private_field_values",
        "private_path",
        "private_value",
        "raw_body",
        "raw_crawl_output",
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
        r"\b(?:bearer\s+[A-Za-z0-9._~-]+|password|set-cookie|sessionid|xsrf|csrf)\b",
        re.IGNORECASE,
    ),
    "local private path": re.compile(
        r"(?:file://|/(?:home|Users|private|tmp|var/folders)/[^\s]+|[A-Za-z]:\\\\[^\s]+)"
    ),
    "payment number": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "private field value": re.compile(
        r"\b(?:actual user value|private field value|unredacted field value)\b",
        re.IGNORECASE,
    ),
    "raw crawl output": re.compile(r"\braw crawl output\b", re.IGNORECASE),
}

_OFFICIAL_COMPLETION_CLAIM_PATTERNS = (
    re.compile(
        r"\b(?:official\s+)?(?:upload|submission|submit|scheduling|schedule|payment|pay)\b.{0,80}"
        r"\b(?:complete|completed|succeeded|success|submitted|uploaded|scheduled|paid|receipt|confirmation)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:complete|completed|succeeded|success|submitted|uploaded|scheduled|paid|receipt|confirmation)\b.{0,80}"
        r"\b(?:official\s+)?(?:upload|submission|submit|scheduling|schedule|payment|pay)\b",
        re.IGNORECASE,
    ),
)


@dataclass(frozen=True)
class ActionJournalComplianceResult:
    """Validation result for a committed action journal compliance packet."""

    ok: bool
    problems: tuple[str, ...]
    event_count: int
    event_types: tuple[str, ...]


def validate_action_journal_compliance_packet(packet: Mapping[str, Any]) -> ActionJournalComplianceResult:
    """Validate that a committed action journal packet is synthetic and redacted.

    The validator accepts only the journal event types needed by the PP&D
    automation plan and rejects credentials, cookies, auth state, screenshots,
    traces, HAR data, payment details, private field values, local private paths,
    raw crawl output, and claims that official upload/submission/scheduling or
    payment actions were completed. Every event must cite both source evidence
    and guardrail evidence so journals cannot stand alone as unsupported claims.
    """

    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return ActionJournalComplianceResult(False, ("packet must be an object",), 0, ())

    fixture_id = packet.get("fixture_id")
    if not isinstance(fixture_id, str) or not fixture_id.strip():
        problems.append("fixture_id is required")

    policy = packet.get("commit_policy")
    if not isinstance(policy, Mapping):
        problems.append("commit_policy must be an object")
        policy = {}
    for key, expected in _REQUIRED_PACKET_FLAGS.items():
        if policy.get(key) is not expected:
            problems.append(f"commit_policy.{key} must be {expected!r}")

    events = packet.get("events")
    if not isinstance(events, list):
        problems.append("events must be a list")
        events = []

    seen_event_ids: set[str] = set()
    seen_event_types: set[str] = set()
    for index, raw_event in enumerate(events):
        path = f"events[{index}]"
        if not isinstance(raw_event, Mapping):
            problems.append(f"{path} must be an object")
            continue
        problems.extend(_validate_event(raw_event, path, seen_event_ids))
        event_type = raw_event.get("event_type")
        if isinstance(event_type, str):
            seen_event_types.add(event_type)

    missing_types = sorted(ALLOWED_COMPLIANCE_EVENT_TYPES.difference(seen_event_types))
    if missing_types:
        problems.append("events missing required compliance event types: " + ", ".join(missing_types))

    problems.extend(_walk_for_sensitive_material(packet, "$"))
    return ActionJournalComplianceResult(
        ok=not problems,
        problems=tuple(problems),
        event_count=len(events),
        event_types=tuple(sorted(seen_event_types)),
    )


def assert_action_journal_compliance_packet(packet: Mapping[str, Any]) -> None:
    """Raise AssertionError when the packet is unsafe for committed fixtures."""

    result = validate_action_journal_compliance_packet(packet)
    if not result.ok:
        raise AssertionError("unsafe action journal compliance packet:\n" + "\n".join(result.problems))


def _validate_event(event: Mapping[str, Any], path: str, seen_event_ids: set[str]) -> list[str]:
    problems: list[str] = []
    missing = sorted(_REQUIRED_EVENT_FIELDS.difference(event))
    for field in missing:
        problems.append(f"{path}.{field} is required")

    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id.strip():
        problems.append(f"{path}.event_id must be a non-empty string")
    elif event_id in seen_event_ids:
        problems.append(f"{path}.event_id is duplicated")
    else:
        seen_event_ids.add(event_id)

    event_type = event.get("event_type")
    if event_type not in ALLOWED_COMPLIANCE_EVENT_TYPES:
        problems.append(f"{path}.event_type is not an allowed compliance event type")

    for field in ("occurred_at", "actor", "user_visible_summary"):
        value = event.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{path}.{field} must be a non-empty string")

    source_evidence_ids = event.get("source_evidence_ids")
    if not _is_non_empty_string_list(source_evidence_ids):
        problems.append(f"{path}.source_evidence_ids must be a non-empty list of strings")

    guardrail_evidence_ids = event.get("guardrail_evidence_ids")
    if not _is_non_empty_string_list(guardrail_evidence_ids):
        problems.append(f"{path}.guardrail_evidence_ids must be a non-empty list of strings")

    synthetic_metadata = event.get("synthetic_metadata")
    if not isinstance(synthetic_metadata, Mapping):
        problems.append(f"{path}.synthetic_metadata must be an object")
    else:
        problems.extend(_validate_metadata(synthetic_metadata, f"{path}.synthetic_metadata"))
        problems.extend(_validate_event_specific_metadata(event_type, synthetic_metadata, path))

    redaction = event.get("redaction")
    if not isinstance(redaction, Mapping):
        problems.append(f"{path}.redaction must be an object")
    else:
        if redaction.get("raw_values_committed") is not False:
            problems.append(f"{path}.redaction.raw_values_committed must be False")
        if redaction.get("private_artifacts_committed") is not False:
            problems.append(f"{path}.redaction.private_artifacts_committed must be False")
        categories = redaction.get("redaction_categories")
        if not _is_non_empty_string_list(categories):
            problems.append(f"{path}.redaction.redaction_categories must be a non-empty list of strings")

    return problems


def _validate_event_specific_metadata(event_type: Any, metadata: Mapping[str, Any], path: str) -> list[str]:
    problems: list[str] = []
    if event_type in {"public crawl preflight", "public crawl metadata capture"}:
        if metadata.get("live_network_used") is not False:
            problems.append(f"{path}.synthetic_metadata.live_network_used must be False")
        if metadata.get("no_raw_body_persisted") is not True:
            problems.append(f"{path}.synthetic_metadata.no_raw_body_persisted must be True")
    if event_type == "requirement extraction" and metadata.get("source_backed") is not True:
        problems.append(f"{path}.synthetic_metadata.source_backed must be True")
    if event_type == "local PDF preview":
        if metadata.get("private_file_reference_committed") is not False:
            problems.append(f"{path}.synthetic_metadata.private_file_reference_committed must be False")
        if metadata.get("official_action_attempted") is not False:
            problems.append(f"{path}.synthetic_metadata.official_action_attempted must be False")
    if event_type == "DevHub attended preflight" and metadata.get("attended_required") is not True:
        problems.append(f"{path}.synthetic_metadata.attended_required must be True")
    if event_type == "manual handoff":
        if metadata.get("attended_required") is not True:
            problems.append(f"{path}.synthetic_metadata.attended_required must be True")
        if not isinstance(metadata.get("handoff_reason"), str):
            problems.append(f"{path}.synthetic_metadata.handoff_reason must be present")
    if event_type == "refused action":
        if metadata.get("requires_manual_handoff") is not True:
            problems.append(f"{path}.synthetic_metadata.requires_manual_handoff must be True")
        if not isinstance(metadata.get("blocked_reason"), str):
            problems.append(f"{path}.synthetic_metadata.blocked_reason must be present")
    if event_type == "completion evidence":
        if not _is_non_empty_string_list(metadata.get("completion_evidence_ids")):
            problems.append(f"{path}.synthetic_metadata.completion_evidence_ids must be a non-empty list of strings")
        if metadata.get("user_visible_outcome_confirmed") is not True:
            problems.append(f"{path}.synthetic_metadata.user_visible_outcome_confirmed must be True")
    return problems


def _validate_metadata(metadata: Mapping[str, Any], path: str) -> list[str]:
    problems: list[str] = []
    for key, value in metadata.items():
        if not isinstance(key, str) or not key.strip():
            problems.append(f"{path} contains an invalid key")
            continue
        if not _is_metadata_value(value):
            problems.append(f"{path}.{key} must be a primitive value or list of primitive values")
    return problems


def _is_metadata_value(value: Any) -> bool:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return True
    if isinstance(value, list):
        return all(isinstance(item, (str, int, float, bool)) or item is None for item in value)
    return False


def _is_non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _walk_for_sensitive_material(value: Any, path: str) -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized_key = key_text.lower().replace("-", "_")
            if _is_prohibited_key(normalized_key):
                problems.append(f"{child_path} uses a prohibited sensitive key")
            problems.extend(_walk_for_sensitive_material(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_walk_for_sensitive_material(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        for reason, pattern in _PROHIBITED_VALUE_PATTERNS.items():
            if pattern.search(value):
                problems.append(f"{path} contains prohibited sensitive value: {reason}")
        for pattern in _OFFICIAL_COMPLETION_CLAIM_PATTERNS:
            if pattern.search(value):
                problems.append(f"{path} contains prohibited official completion claim")
                break
    return problems


def _is_prohibited_key(normalized_key: str) -> bool:
    parts = set(normalized_key.split("_"))
    return normalized_key in _PROHIBITED_KEY_TERMS or bool(parts.intersection(_PROHIBITED_KEY_TERMS))
