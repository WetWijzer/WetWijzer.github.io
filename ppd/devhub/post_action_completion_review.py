"""Validation for DevHub post-action completion hardening reviews.

This module is intentionally fixture-friendly and side-effect free. It validates
that a completed DevHub action is supported by user-visible outcome evidence,
source-backed classification, and redacted journal metadata rather than by a raw
click or fill attempt.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SAFE_ACTION_CLASSES = frozenset({"safe_read_only", "reversible_draft"})
COMPLETED_OUTCOMES = frozenset({"completed", "no_change"})
ATTEMPT_ONLY_TYPES = frozenset({"click", "fill", "click_attempt", "fill_attempt", "playwright_attempt"})
ALLOWED_COMPLETION_EVIDENCE_TYPES = frozenset(
    {"visible_status", "visible_confirmation", "visible_validation_message", "visible_saved_state"}
)
FORBIDDEN_JOURNAL_KEYS = frozenset(
    {
        "auth",
        "auth_state",
        "captcha",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "har",
        "local_private_path",
        "mfa",
        "password",
        "payment",
        "raw_crawl_output",
        "screenshot",
        "session",
        "session_file",
        "storage_state",
        "token",
        "trace",
        "upload",
    }
)
FORBIDDEN_VALUE_FRAGMENTS = (
    "/home/",
    "C:\\Users\\",
    ".auth/",
    "auth-state",
    "storage-state",
    "trace.zip",
    ".har",
    ".png",
    ".webm",
    "cookies.json",
)


def validate_post_action_completion_review(review: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a post-action completion review fixture."""

    errors: list[str] = []
    attempted_actions = _list(review.get("attemptedActions"))
    completion_evidence = _list(review.get("completionEvidence"))
    journal_events = _list(review.get("journalEvents"))

    journal_by_id = {_string(event.get("eventId")): event for event in journal_events if isinstance(event, Mapping)}
    evidence_by_action: dict[str, list[Mapping[str, Any]]] = {}
    for evidence in completion_evidence:
        if isinstance(evidence, Mapping):
            evidence_by_action.setdefault(_string(evidence.get("actionId")), []).append(evidence)

    for index, action in enumerate(attempted_actions):
        if not isinstance(action, Mapping):
            errors.append(f"attemptedActions[{index}] must be an object")
            continue

        action_id = _string(action.get("actionId"))
        if not action_id:
            errors.append(f"attemptedActions[{index}] actionId is required")
            continue

        outcome = _string(action.get("outcome"))
        action_class = _string(action.get("actionClass"))
        if outcome in COMPLETED_OUTCOMES:
            if action_class not in SAFE_ACTION_CLASSES:
                errors.append(f"completed action {action_id} must be safe read-only or reversible draft")
            if not _source_ids(action):
                errors.append(f"completed action {action_id} requires source-backed classification")

            action_evidence = evidence_by_action.get(action_id, [])
            if not action_evidence:
                errors.append(f"completed action {action_id} requires completion evidence")
            for evidence in action_evidence:
                errors.extend(_validate_completion_evidence(action_id, evidence, journal_by_id))

    for index, event in enumerate(journal_events):
        if not isinstance(event, Mapping):
            errors.append(f"journalEvents[{index}] must be an object")
            continue
        errors.extend(_validate_redacted_journal_event(event))

    return errors


def assert_valid_post_action_completion_review(review: Mapping[str, Any]) -> None:
    """Raise ValueError when a review fails completion hardening validation."""

    errors = validate_post_action_completion_review(review)
    if errors:
        raise ValueError("; ".join(errors))


def _validate_completion_evidence(
    action_id: str,
    evidence: Mapping[str, Any],
    journal_by_id: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []
    evidence_type = _string(evidence.get("evidenceType"))
    if evidence_type in ATTEMPT_ONLY_TYPES:
        errors.append(f"completion evidence for {action_id} cannot be only a click or fill attempt")
    if evidence_type not in ALLOWED_COMPLETION_EVIDENCE_TYPES:
        errors.append(f"completion evidence for {action_id} must be user-visible outcome evidence")
    if not _string(evidence.get("observedOutcome")):
        errors.append(f"completion evidence for {action_id} requires observedOutcome")
    if not _string(evidence.get("userVisibleOutcomeEvidence")):
        errors.append(f"completion evidence for {action_id} requires userVisibleOutcomeEvidence")
    if not _source_ids(evidence):
        errors.append(f"completion evidence for {action_id} requires source evidence")

    journal_event_id = _string(evidence.get("journalEventId"))
    if not journal_event_id:
        errors.append(f"completion evidence for {action_id} requires journalEventId")
    elif journal_event_id not in journal_by_id:
        errors.append(f"completion evidence for {action_id} references missing journal metadata")
    else:
        journal_errors = _validate_redacted_journal_event(journal_by_id[journal_event_id])
        if journal_errors:
            errors.append(f"completion evidence for {action_id} references unsafe journal metadata")
    return errors


def _validate_redacted_journal_event(event: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    event_id = _string(event.get("eventId"))
    if not event_id:
        errors.append("journal event id is required")
    if _string(event.get("redactionStatus")) != "redacted":
        errors.append(f"journal event {event_id or ''} must be redacted")

    metadata = event.get("metadata")
    if metadata is None and isinstance(event.get("payload"), Mapping):
        metadata = event["payload"].get("metadata")
    if not isinstance(metadata, Mapping):
        errors.append(f"journal event {event_id or ''} requires redacted metadata")
    else:
        if metadata.get("redacted") is not True:
            errors.append(f"journal event {event_id or ''} metadata must mark redacted=true")
        if metadata.get("containsPrivateValues") is not False:
            errors.append(f"journal event {event_id or ''} metadata must mark containsPrivateValues=false")
        errors.extend(_validate_no_private_values(metadata, f"journal event {event_id or ''} metadata"))

    payload = event.get("payload")
    if isinstance(payload, Mapping):
        errors.extend(_validate_no_private_values(payload, f"journal event {event_id or ''} payload"))
    return errors


def _validate_no_private_values(value: Any, context: str) -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized_key = _string(key).strip().lower().replace("-", "_")
            if normalized_key in FORBIDDEN_JOURNAL_KEYS:
                errors.append(f"{context} contains forbidden private key {key}")
            errors.extend(_validate_no_private_values(child, context))
    elif isinstance(value, list):
        for child in value:
            errors.extend(_validate_no_private_values(child, context))
    elif isinstance(value, str):
        for fragment in FORBIDDEN_VALUE_FRAGMENTS:
            if fragment in value:
                errors.append(f"{context} contains forbidden private value")
    return errors


def _source_ids(value: Mapping[str, Any]) -> list[str]:
    raw = value.get("classificationSourceEvidenceIds")
    if raw is None:
        raw = value.get("sourceEvidenceIds")
    return [_string(item) for item in _list(raw) if _string(item)]


def _list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
