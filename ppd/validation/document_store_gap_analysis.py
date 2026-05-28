"""Validation for user document-store gap-analysis packets.

The validator is intentionally schema-light: callers may pass packet dictionaries from
fixtures, daemon messages, or future document-store adapters. It focuses on safety
properties that must hold regardless of the exact packet producer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


PRIVATE_VALUE_KEYS = {
    "password",
    "passcode",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "session",
    "ssn",
    "tax_id",
    "ein",
    "driver_license",
    "credit_card",
    "card_number",
    "bank_account",
    "routing_number",
    "dob",
    "date_of_birth",
    "phone",
    "email",
    "address",
}

LOCAL_PRIVATE_PATH_RE = re.compile(
    r"(?:^|[\s'\"])(?:/home/[^\s'\"]+|/Users/[^\s'\"]+|/private/[^\s'\"]+|/var/folders/[^\s'\"]+|[A-Za-z]:\\Users\\[^\s'\"]+)"
)
RAW_CONTENT_KEYS = {"raw_content", "raw_document", "document_text", "page_text", "html", "body", "ocr_text", "full_text"}
READY_STATUSES = {"ready", "ready_to_submit", "submit_ready", "approved_for_submission", "complete"}
CONSEQUENTIAL_ACTION_WORDS = {
    "submit",
    "upload",
    "certify",
    "sign",
    "pay",
    "cancel",
    "schedule",
    "reschedule",
    "approve",
    "file",
}
FRESHNESS_WORDS = {"fresh", "current", "latest", "verified", "last_verified", "checked", "as_of"}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


def validate_gap_analysis_packet(packet: Mapping[str, Any]) -> list[ValidationIssue]:
    """Return validation issues for a user document-store gap-analysis packet."""
    issues: list[ValidationIssue] = []

    for path, key, value in _walk(packet):
        lowered_key = key.lower() if key else ""
        if lowered_key in PRIVATE_VALUE_KEYS and _has_value(value):
            issues.append(ValidationIssue("private_value", path, "private values are not allowed in gap-analysis packets"))
        if lowered_key in RAW_CONTENT_KEYS and _has_value(value):
            issues.append(ValidationIssue("raw_document_content", path, "raw document content must not be stored in gap-analysis packets"))
        if isinstance(value, str) and LOCAL_PRIVATE_PATH_RE.search(value):
            issues.append(ValidationIssue("local_private_path", path, "local private paths must not be included"))

    requirements = _list_at(packet, "process_requirements")
    for index, requirement in enumerate(requirements):
        req_path = f"process_requirements[{index}]"
        if not isinstance(requirement, Mapping):
            issues.append(ValidationIssue("uncited_process_requirement", req_path, "process requirements must be objects with citations"))
            continue
        if not _has_citation(requirement):
            issues.append(ValidationIssue("uncited_process_requirement", req_path, "process requirements need at least one source citation"))

    for field in ("freshness_evidence", "freshness", "source_freshness"):
        evidence = packet.get(field)
        if evidence is None:
            continue
        evidence_items = evidence if isinstance(evidence, list) else [evidence]
        for index, item in enumerate(evidence_items):
            item_path = f"{field}[{index}]"
            if not isinstance(item, Mapping) or not _has_citation(item) or not _has_any(item, ("observed_at", "retrieved_at", "source_date", "published_at")):
                issues.append(ValidationIssue("invented_freshness_evidence", item_path, "freshness evidence needs a citation and an exact observed or source date"))

    for field in ("conflicts", "staleness", "stale_sources"):
        entries = _list_at(packet, field)
        for index, entry in enumerate(entries):
            entry_path = f"{field}[{index}]"
            if not isinstance(entry, Mapping) or not _has_text(entry.get("explanation")):
                issues.append(ValidationIssue("missing_conflict_staleness_explanation", entry_path, "conflict and staleness entries require explanations"))

    status = str(packet.get("status", "")).strip().lower()
    if status in READY_STATUSES and not packet.get("ready_to_submit_gate_confirmed"):
        issues.append(ValidationIssue("premature_ready_to_submit", "status", "ready-to-submit status requires an explicit confirmation gate"))

    actions = _list_at(packet, "next_actions") + _list_at(packet, "recommended_actions")
    for index, action in enumerate(actions):
        action_path = f"next_actions[{index}]"
        action_text = _action_text(action).lower()
        if any(word in action_text for word in CONSEQUENTIAL_ACTION_WORDS):
            if not isinstance(action, Mapping) or action.get("exact_confirmation_required") is not True:
                issues.append(ValidationIssue("missing_exact_confirmation_gate", action_path, "consequential next actions require exact-confirmation gates"))

    for path, _key, value in _walk(packet):
        if isinstance(value, str) and any(word in value.lower() for word in FRESHNESS_WORDS):
            if "freshness_evidence" not in packet and "source_freshness" not in packet:
                issues.append(ValidationIssue("invented_freshness_evidence", path, "freshness claims require cited freshness evidence"))
                break

    return issues


def issue_codes(packet: Mapping[str, Any]) -> set[str]:
    return {issue.code for issue in validate_gap_analysis_packet(packet)}


def _walk(value: Any, path: str = "$", key: str = "") -> Iterable[tuple[str, str, Any]]:
    yield path, key, value
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            yield from _walk(child_value, f"{path}.{child_key_text}", child_key_text)
    elif isinstance(value, list):
        for index, child_value in enumerate(value):
            yield from _walk(child_value, f"{path}[{index}]", key)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_any(item: Mapping[str, Any], keys: tuple[str, ...]) -> bool:
    return any(_has_value(item.get(key)) for key in keys)


def _has_citation(item: Mapping[str, Any]) -> bool:
    citations = item.get("citations") or item.get("sources") or item.get("source_citations")
    if not isinstance(citations, list) or not citations:
        return False
    for citation in citations:
        if isinstance(citation, Mapping) and _has_text(citation.get("url")) and _has_text(citation.get("title")):
            return True
        if isinstance(citation, str) and citation.startswith("http"):
            return True
    return False


def _list_at(packet: Mapping[str, Any], key: str) -> list[Any]:
    value = packet.get(key)
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _action_text(action: Any) -> str:
    if isinstance(action, Mapping):
        return " ".join(str(action.get(key, "")) for key in ("label", "action", "description", "title"))
    return str(action)
