"""Fixture-first guardrail bundle refresh planning for changed PP&D requirements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

REQUIRED_CHANGE_TYPES = frozenset(
    {
        "fee",
        "deadline",
        "upload_rule",
        "required_document",
        "unsupported_path",
        "devhub_action_gate",
    }
)

SUPPORTED_REQUIREMENT_TYPES = frozenset(
    {
        "obligation",
        "prohibition",
        "permission",
        "precondition",
        "exception",
        "deadline",
        "fee_trigger",
        "license_requirement",
        "document_requirement",
        "action_gate",
    }
)

REVIEW_COMPLETE_STATUSES = frozenset({"reviewed", "approved", "accepted"})
READY_STATUSES = frozenset(
    {
        "ready",
        "ready_after_review",
        "ready_for_bundle_publish",
        "publish_ready",
        "validated_ready",
    }
)
CONSEQUENTIAL_ACTION_TERMS = frozenset(
    {
        "submit",
        "certify",
        "upload",
        "schedule",
        "cancel",
        "withdraw",
        "payment",
        "pay",
        "purchase",
        "extension",
        "reactivation",
    }
)


@dataclass(frozen=True)
class GuardrailDelta:
    """A draft guardrail change derived from one changed requirement fixture."""

    delta_id: str
    requirement_id: str
    requirement_type: str
    change_type: str
    draft_version: str
    target_guardrail_bundle_id: str
    readiness_status: str
    review_status: str
    blocked_reason: str
    source_evidence_ids: tuple[str, ...]
    required_guardrail_updates: tuple[str, ...]
    predicate_deltas: tuple[dict[str, Any], ...]
    manual_handoff_predicates: tuple[str, ...]
    exact_confirmation_predicates: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "delta_id": self.delta_id,
            "requirement_id": self.requirement_id,
            "requirement_type": self.requirement_type,
            "change_type": self.change_type,
            "draft_version": self.draft_version,
            "target_guardrail_bundle_id": self.target_guardrail_bundle_id,
            "readiness_status": self.readiness_status,
            "review_status": self.review_status,
            "blocked_reason": self.blocked_reason,
            "source_evidence_ids": list(self.source_evidence_ids),
            "required_guardrail_updates": list(self.required_guardrail_updates),
            "predicate_deltas": list(self.predicate_deltas),
            "manual_handoff_predicates": list(self.manual_handoff_predicates),
            "exact_confirmation_predicates": list(self.exact_confirmation_predicates),
        }


def build_guardrail_bundle_refresh_plan(fixture: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic draft refresh plan from a committed fixture.

    The planner is intentionally fixture-only. It does not crawl public sources or
    touch authenticated DevHub state. Draft deltas remain blocked unless every
    changed requirement has a review-complete status.
    """

    fixture_id = _required_text(fixture, "fixture_id")
    current_bundle_id = _required_text(fixture, "current_guardrail_bundle_id")
    draft_bundle_id = _required_text(fixture, "draft_guardrail_bundle_id")
    draft_version = _required_text(fixture, "draft_version")
    changed_requirements = fixture.get("changed_requirements")
    if not isinstance(changed_requirements, list) or not changed_requirements:
        raise ValueError("changed_requirements must be a non-empty array")

    deltas = [_build_delta(item, draft_bundle_id, draft_version) for item in changed_requirements]
    covered_change_types = {delta.change_type for delta in deltas}
    missing_change_types = sorted(REQUIRED_CHANGE_TYPES - covered_change_types)
    if missing_change_types:
        raise ValueError("fixture is missing changed requirement types: " + ", ".join(missing_change_types))

    has_pending_review = any(delta.review_status not in REVIEW_COMPLETE_STATUSES for delta in deltas)
    readiness_status = "blocked_pending_review" if has_pending_review else "ready_for_bundle_publish"
    blocked_reasons = sorted({delta.blocked_reason for delta in deltas if delta.blocked_reason})

    return {
        "fixture_id": fixture_id,
        "current_guardrail_bundle_id": current_bundle_id,
        "draft_guardrail_bundle_id": draft_bundle_id,
        "draft_version": draft_version,
        "refresh_strategy": "fixture_first_guardrail_delta_review",
        "readiness_status": readiness_status,
        "publish_allowed": readiness_status == "ready_for_bundle_publish",
        "blocked_reasons": blocked_reasons,
        "covered_change_types": sorted(covered_change_types),
        "required_change_types": sorted(REQUIRED_CHANGE_TYPES),
        "deltas": [delta.to_dict() for delta in sorted(deltas, key=lambda item: item.delta_id)],
    }


def _build_delta(item: Any, draft_bundle_id: str, draft_version: str) -> GuardrailDelta:
    if not isinstance(item, Mapping):
        raise ValueError("each changed requirement must be an object")

    requirement_id = _required_text(item, "requirement_id")
    change_type = _required_text(item, "change_type")
    if change_type not in REQUIRED_CHANGE_TYPES:
        raise ValueError(f"unsupported changed requirement type: {change_type}")

    requirement_type = _required_text(item, "requirement_type")
    if requirement_type not in SUPPORTED_REQUIREMENT_TYPES:
        raise ValueError(f"unsupported requirement_type for {requirement_id}: {requirement_type}")

    source_evidence_ids = tuple(_required_text_list(item, "source_evidence_ids"))
    review_status = str(item.get("review_status", "needs_review")).strip().lower() or "needs_review"
    _reject_premature_ready_status(item, requirement_id, review_status)

    predicate_deltas = tuple(_predicate_deltas(item, requirement_id, review_status))
    manual_handoff_predicates = tuple(_optional_text_list(item, "manual_handoff_predicates"))
    exact_confirmation_predicates = tuple(_optional_text_list(item, "exact_confirmation_predicates"))
    if _is_consequential_devhub_gate(item, change_type, requirement_type):
        if not manual_handoff_predicates:
            raise ValueError(f"consequential DevHub action gate {requirement_id} requires manual_handoff_predicates")
        if not exact_confirmation_predicates:
            raise ValueError(f"consequential DevHub action gate {requirement_id} requires exact_confirmation_predicates")

    readiness_status = "ready_after_review" if review_status in REVIEW_COMPLETE_STATUSES else "blocked_pending_review"
    blocked_reason = "" if readiness_status == "ready_after_review" else f"{change_type}_change_requires_human_review"

    return GuardrailDelta(
        delta_id=f"delta-{draft_version}-{change_type}-{requirement_id}",
        requirement_id=requirement_id,
        requirement_type=requirement_type,
        change_type=change_type,
        draft_version=draft_version,
        target_guardrail_bundle_id=draft_bundle_id,
        readiness_status=readiness_status,
        review_status=review_status,
        blocked_reason=blocked_reason,
        source_evidence_ids=source_evidence_ids,
        required_guardrail_updates=tuple(_required_text_list(item, "required_guardrail_updates")),
        predicate_deltas=predicate_deltas,
        manual_handoff_predicates=manual_handoff_predicates,
        exact_confirmation_predicates=exact_confirmation_predicates,
    )


def _predicate_deltas(item: Mapping[str, Any], requirement_id: str, review_status: str) -> list[dict[str, Any]]:
    value = item.get("predicate_deltas", [])
    if not isinstance(value, list):
        raise ValueError(f"predicate_deltas for {requirement_id} must be an array")
    result: list[dict[str, Any]] = []
    for index, predicate in enumerate(value):
        if not isinstance(predicate, Mapping):
            raise ValueError(f"predicate_deltas[{index}] for {requirement_id} must be an object")
        predicate_id = _required_text(predicate, "predicate_id")
        _reject_premature_ready_status(predicate, f"{requirement_id}:{predicate_id}", review_status)
        result.append(
            {
                "predicate_id": predicate_id,
                "operation": _required_text(predicate, "operation"),
                "source_evidence_ids": _required_text_list(predicate, "source_evidence_ids"),
            }
        )
    return result


def _reject_premature_ready_status(item: Mapping[str, Any], label: str, review_status: str) -> None:
    if review_status in REVIEW_COMPLETE_STATUSES:
        return
    for key in ("readiness_status", "validation_status", "publish_status", "guardrail_validation_status"):
        value = item.get(key)
        if not isinstance(value, str):
            continue
        status = value.strip().lower()
        if status in READY_STATUSES or status.startswith("ready_"):
            raise ValueError(f"{label} cannot declare {key}={status} before human review is complete")


def _is_consequential_devhub_gate(item: Mapping[str, Any], change_type: str, requirement_type: str) -> bool:
    if change_type != "devhub_action_gate" and requirement_type != "action_gate":
        return False
    surface = str(item.get("surface", item.get("surface_id", ""))).strip().lower()
    consequence = str(item.get("action_consequence", item.get("consequence", ""))).strip().lower()
    action = str(item.get("action", " ".join(_optional_text_list(item, "required_guardrail_updates")))).strip().lower()
    if "devhub" in surface or change_type == "devhub_action_gate":
        if consequence in {"consequential", "official", "financial"}:
            return True
        return any(term in action for term in CONSEQUENTIAL_ACTION_TERMS)
    return False


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing non-empty {key}")
    return value.strip()


def _required_text_list(mapping: Mapping[str, Any], key: str) -> list[str]:
    value = mapping.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty array")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key} must contain only non-empty strings")
        result.append(item.strip())
    return result


def _optional_text_list(mapping: Mapping[str, Any], key: str) -> list[str]:
    value = mapping.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{key} must be an array")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key} must contain only non-empty strings")
        result.append(item.strip())
    return result
