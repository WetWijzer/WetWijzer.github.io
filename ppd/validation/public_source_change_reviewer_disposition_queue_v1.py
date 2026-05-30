"""Validation for public source change reviewer disposition queue v1."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import re
from typing import Any

QUEUE_VERSION = "public_source_change_reviewer_disposition_queue_v1"
REQUIRED_BUCKETS = ("changed", "unchanged", "needs_review")

PRIVATE_ARTIFACT_KEYS = {
    "auth_state",
    "browser_context",
    "cookies",
    "credentials",
    "devhub_session",
    "har",
    "local_storage",
    "password",
    "private_file_path",
    "session_storage",
    "screenshot",
    "trace",
}

RAW_DATA_KEYS = {
    "downloaded_data",
    "downloaded_file",
    "pdf_bytes",
    "raw_body",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "response_body",
}

MUTATION_FLAG_KEYS = {
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_release_state_mutation",
    "active_prompt_mutation",
    "active_fixture_mutation",
    "active_agent_state_mutation",
    "source_mutation",
    "document_mutation",
    "requirement_mutation",
    "process_mutation",
    "guardrail_mutation",
    "release_state_mutation",
    "prompt_mutation",
    "fixture_mutation",
    "agent_state_mutation",
}

LIVE_CLAIM_PATTERNS = (
    re.compile(r"\blive\s+crawl\b", re.IGNORECASE),
    re.compile(r"\brefresh(?:ed)?\s+complete\b", re.IGNORECASE),
    re.compile(r"\brecrawl(?:ed)?\s+complete\b", re.IGNORECASE),
    re.compile(r"\bcrawl(?:ed)?\s+(?:is\s+)?complete\b", re.IGNORECASE),
)

GUARANTEE_PATTERNS = (
    re.compile(r"\bguarantee(?:d|s)?\b.*\b(?:approval|issuance|permit|legal|compliance)\b", re.IGNORECASE),
    re.compile(r"\bwill\s+be\s+(?:approved|issued|accepted|legal|compliant)\b", re.IGNORECASE),
    re.compile(r"\bensures?\s+(?:approval|issuance|acceptance|legal\s+compliance)\b", re.IGNORECASE),
    re.compile(r"\blegal\s+advice\b", re.IGNORECASE),
)

CONSEQUENTIAL_ACTION_PATTERNS = (
    re.compile(r"\b(?:agent|automation|worker|system)\s+(?:will|may|can|should|must)\s+(?:submit|certify|upload|pay|purchase|schedule|cancel)\b", re.IGNORECASE),
    re.compile(r"\b(?:submit|certify|upload|pay|purchase|schedule|cancel)\s+(?:the\s+)?(?:permit|application|correction|payment|inspection|request)\b", re.IGNORECASE),
    re.compile(r"\b(?:ready|cleared|approved)\s+to\s+(?:submit|certify|upload|pay|purchase|schedule|cancel)\b", re.IGNORECASE),
)


def validate_queue(queue: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a reviewer disposition queue."""
    errors: list[str] = []

    if queue.get("version") != QUEUE_VERSION:
        errors.append("version must be public_source_change_reviewer_disposition_queue_v1")

    rows = queue.get("reviewer_decision_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("reviewer_decision_rows must contain at least one reviewer decision row")
        rows = []

    buckets = queue.get("buckets")
    if not isinstance(buckets, Mapping):
        errors.append("buckets must include changed, unchanged, and needs_review lists")
        buckets = {}

    for bucket in REQUIRED_BUCKETS:
        if bucket not in buckets or not isinstance(buckets.get(bucket), list):
            errors.append(f"buckets.{bucket} must be present as a list")

    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"reviewer_decision_rows[{index}] must be an object")
            continue
        _validate_row(row, index, errors)

    rollback_checkpoints = queue.get("rollback_checkpoints")
    if not _non_empty_string_list(rollback_checkpoints):
        errors.append("rollback_checkpoints must contain at least one checkpoint")

    validation_commands = queue.get("validation_commands")
    if not _valid_validation_commands(validation_commands):
        errors.append("validation_commands must contain at least one command array")

    _scan_for_forbidden_content(queue, "$", errors)
    return errors


def assert_valid_queue(queue: Mapping[str, Any]) -> None:
    """Raise ValueError when a queue is not valid."""
    errors = validate_queue(queue)
    if errors:
        raise ValueError("public source change reviewer disposition queue rejected: " + "; ".join(errors))


def _validate_row(row: Mapping[str, Any], index: int, errors: list[str]) -> None:
    disposition = row.get("disposition")
    if disposition not in REQUIRED_BUCKETS:
        errors.append(f"reviewer_decision_rows[{index}].disposition must be changed, unchanged, or needs_review")

    impact_references = row.get("impact_references")
    if not isinstance(impact_references, list) or not impact_references:
        errors.append(f"reviewer_decision_rows[{index}].impact_references must cite at least one source")
    else:
        for ref_index, reference in enumerate(impact_references):
            if not _is_cited_reference(reference):
                errors.append(f"reviewer_decision_rows[{index}].impact_references[{ref_index}] must include citation, source_evidence_id, or canonical_url")

    blocked = row.get("promotion_blocked") is True or row.get("promote") is False or disposition == "needs_review"
    if blocked and not _non_empty_string(row.get("blocked_promotion_reason")):
        errors.append(f"reviewer_decision_rows[{index}].blocked_promotion_reason is required when promotion is blocked or needs review")


def _is_cited_reference(reference: Any) -> bool:
    if isinstance(reference, str):
        return bool(reference.strip())
    if not isinstance(reference, Mapping):
        return False
    for key in ("citation", "source_evidence_id", "canonical_url", "url"):
        value = reference.get(key)
        if isinstance(value, str) and value.strip():
            return True
    return False


def _valid_validation_commands(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for command in value:
        if not isinstance(command, list) or not command:
            return False
        if not all(isinstance(part, str) and part.strip() for part in command):
            return False
    return True


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_non_empty_string(item) for item in value)


def _scan_for_forbidden_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"

            if normalized_key in PRIVATE_ARTIFACT_KEYS:
                errors.append(f"{child_path} must not include private, authenticated, session, or browser artifacts")
            if normalized_key in RAW_DATA_KEYS:
                errors.append(f"{child_path} must not include raw crawl, PDF, or downloaded data")
            if normalized_key in MUTATION_FLAG_KEYS and bool(child):
                errors.append(f"{child_path} must not set active mutation flags")

            _scan_for_forbidden_content(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_forbidden_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        _scan_string(value, path, errors)


def _scan_string(value: str, path: str, errors: list[str]) -> None:
    for pattern in LIVE_CLAIM_PATTERNS:
        if pattern.search(value):
            errors.append(f"{path} must not claim live crawl or refresh completion")
            break
    for pattern in GUARANTEE_PATTERNS:
        if pattern.search(value):
            errors.append(f"{path} must not include legal or permitting outcome guarantees")
            break
    for pattern in CONSEQUENTIAL_ACTION_PATTERNS:
        if pattern.search(value):
            errors.append(f"{path} must not include consequential action language")
            break
