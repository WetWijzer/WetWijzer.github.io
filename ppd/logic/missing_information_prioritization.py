"""Deterministic validation for PP&D missing-information prioritization.

The helpers in this module are side-effect free. They validate already-assembled
case facts and return only prompts that are safe to ask before the next PP&D
planning step. They also block consequential actions unless an exact user
confirmation is present in the input.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence


UNRESOLVED_STATUSES = {"missing", "stale", "ambiguous", "conflicting"}
KNOWN_STATUSES = {"complete", "known", "resolved"}
FRESH_STATUSES = {"fresh", "current", "verified_current"}
SENSITIVE_TERMS = (
    "password",
    "credential",
    "username",
    "mfa",
    "multi-factor",
    "captcha",
    "auth state",
    "authentication state",
    "cookie",
    "session",
    "token",
    "payment",
    "credit card",
    "debit card",
    "card number",
    "cvv",
    "bank account",
    "routing number",
)
CONSEQUENTIAL_ACTION_TERMS = (
    "submit",
    "submission",
    "upload",
    "certify",
    "certification",
    "payment",
    "pay fee",
    "schedule",
    "cancel",
    "cancellation",
    "official change",
)


class MissingInformationPrioritizationError(ValueError):
    """Raised when a missing-information prioritization request is unsafe."""


def prioritize_missing_information(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and prioritize safe missing-information prompts.

    Returned prompts preserve citation-backed reasons. Consequential actions are
    reported as blocked until an exact confirmation record is supplied.
    """

    if not isinstance(payload, Mapping):
        raise MissingInformationPrioritizationError("payload must be a mapping")

    fixture_id = _text(payload.get("fixture_id"))
    case_id = _text(payload.get("case_id"))
    process_id = _text(payload.get("process_id"))
    if not fixture_id:
        raise MissingInformationPrioritizationError("fixture_id is required")
    if not case_id:
        raise MissingInformationPrioritizationError("case_id is required")
    if not process_id:
        raise MissingInformationPrioritizationError("process_id is required")

    facts = _as_list(payload.get("facts"))
    if not facts:
        raise MissingInformationPrioritizationError("facts must include at least one fact")

    errors: list[str] = []
    prompts: list[dict[str, Any]] = []
    for index, raw_fact in enumerate(facts):
        fact = _mapping(raw_fact)
        fact_id = _text(fact.get("fact_id"))
        if not fact_id:
            errors.append(f"fact at index {index} requires fact_id")
            continue

        status = _text(fact.get("status")).lower()
        needed = fact.get("needed_for_next_safe_action") is True
        if _is_known_and_fresh(fact) and needed:
            errors.append(f"fact {fact_id} is already known and fresh")
            continue
        if status in UNRESOLVED_STATUSES and needed and _contains_sensitive_request(fact):
            errors.append(f"fact {fact_id} requests refused sensitive information")
            continue
        if status not in UNRESOLVED_STATUSES or not needed:
            continue

        reason = _text(fact.get("reason"))
        source_requirement_ids = _string_list(fact.get("source_requirement_ids"))
        reason_citation_ids = _string_list(
            fact.get("reason_citation_ids") or fact.get("source_citation_ids") or fact.get("citation_ids")
        )
        if not reason:
            errors.append(f"fact {fact_id} requires a reason")
        if not source_requirement_ids:
            errors.append(f"fact {fact_id} requires source_requirement_ids")
        if not reason_citation_ids:
            errors.append(f"fact {fact_id} requires reason_citation_ids")
        if errors and errors[-1].startswith(f"fact {fact_id} requires"):
            continue

        prompts.append(
            {
                "prompt_id": _text(fact.get("prompt_id")) or f"ask_{fact_id}",
                "fact_id": fact_id,
                "status": status,
                "prompt": _text(fact.get("prompt")),
                "reason": reason,
                "source_requirement_ids": source_requirement_ids,
                "reason_citation_ids": reason_citation_ids,
                "blocked_next_safe_action": _text(fact.get("blocked_next_safe_action")),
            }
        )

    if errors:
        raise MissingInformationPrioritizationError("; ".join(errors))

    requested_actions = _requested_actions(payload)
    confirmations = _confirmation_records(payload.get("required_confirmations"))
    blocked_actions = [
        action for action in requested_actions if _is_consequential_action(action) and not _has_exact_confirmation(action, confirmations)
    ]

    return {
        "fixture_id": fixture_id,
        "case_id": case_id,
        "process_id": process_id,
        "prompts": prompts,
        "blocked_actions": blocked_actions,
        "required_confirmations": [
            {"action": action, "required_exact_text": _required_confirmation_text(action)} for action in blocked_actions
        ],
    }


def validate_missing_information_prioritization(payload: Mapping[str, Any]) -> list[str]:
    """Return validation errors instead of raising."""

    try:
        prioritize_missing_information(payload)
    except MissingInformationPrioritizationError as exc:
        return [str(exc)]
    return []


def _is_known_and_fresh(fact: Mapping[str, Any]) -> bool:
    status = _text(fact.get("status")).lower()
    freshness_status = _text(fact.get("freshness_status")).lower()
    has_known_value = fact.get("known_value_present") is True or fact.get("current_value") not in (None, "")
    return status in KNOWN_STATUSES and freshness_status in FRESH_STATUSES and has_known_value


def _contains_sensitive_request(fact: Mapping[str, Any]) -> bool:
    text = " ".join(
        _text(fact.get(key)).lower()
        for key in ("fact_id", "prompt_id", "prompt", "reason", "blocked_next_safe_action")
    )
    return any(term in text for term in SENSITIVE_TERMS)


def _requested_actions(payload: Mapping[str, Any]) -> list[str]:
    actions = _string_list(payload.get("requested_actions"))
    next_safe_action = _text(payload.get("next_safe_action"))
    if next_safe_action:
        actions.append(next_safe_action)
    return _dedupe(actions)


def _is_consequential_action(action: str) -> bool:
    lowered = action.lower().replace("_", " ")
    return any(term in lowered for term in CONSEQUENTIAL_ACTION_TERMS)


def _confirmation_records(value: Any) -> list[Mapping[str, Any]]:
    return [_mapping(item) for item in _as_list(value)]


def _has_exact_confirmation(action: str, confirmations: Sequence[Mapping[str, Any]]) -> bool:
    required_text = _required_confirmation_text(action)
    for confirmation in confirmations:
        if _text(confirmation.get("action")) != action:
            continue
        if confirmation.get("explicit") is not True:
            continue
        if _text(confirmation.get("confirmation_text")) == required_text:
            return True
    return False


def _required_confirmation_text(action: str) -> str:
    return f"CONFIRM {action}"


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _string_list(value: Any) -> list[str]:
    return _dedupe([_text(item) for item in _as_list(value) if _text(item)])


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


__all__ = [
    "MissingInformationPrioritizationError",
    "prioritize_missing_information",
    "validate_missing_information_prioritization",
]
