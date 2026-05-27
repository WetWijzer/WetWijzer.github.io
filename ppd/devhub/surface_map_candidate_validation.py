"""Validate DevHubSurfaceMap candidates before reversible draft use.

This module is deterministic and fixture-only. It does not open DevHub, launch a
browser, authenticate, upload, submit, certify, schedule, cancel, or pay.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

MINIMUM_REVERSIBLE_SELECTOR_CONFIDENCE = 0.85
REVERSIBLE_CLASSIFICATIONS = frozenset(
    {
        "reversible",
        "reversible_draft",
        "reversible_draft_edit",
        "reversible_draft_fill",
        "draft_edit",
    }
)
CONSEQUENTIAL_CONTROL_TOKENS = frozenset(
    {
        "upload",
        "submit",
        "certify",
        "certification",
        "acknowledgment",
        "schedule",
        "inspection",
        "cancel",
        "payment",
        "pay",
        "fee",
    }
)
CONTROL_COLLECTIONS = (
    "actions",
    "controls",
    "upload_controls",
    "submit_controls",
    "certification_controls",
    "schedule_controls",
    "cancel_controls",
    "payment_controls",
)


@dataclass(frozen=True)
class SurfaceMapCandidateViolation:
    candidate_id: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "candidate_id": self.candidate_id,
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class SurfaceMapCandidateValidationResult:
    candidate_id: str
    reversible_draft_allowed: bool
    violations: tuple[SurfaceMapCandidateViolation, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "reversible_draft_allowed": self.reversible_draft_allowed,
            "violations": [violation.as_dict() for violation in self.violations],
        }


@dataclass(frozen=True)
class SurfaceMapCandidateBatchValidationResult:
    reversible_draft_allowed: bool
    results: tuple[SurfaceMapCandidateValidationResult, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "reversible_draft_allowed": self.reversible_draft_allowed,
            "results": [result.as_dict() for result in self.results],
        }


def validate_surface_map_candidate(
    candidate: Mapping[str, Any],
    *,
    minimum_selector_confidence: float = MINIMUM_REVERSIBLE_SELECTOR_CONFIDENCE,
) -> SurfaceMapCandidateValidationResult:
    """Return fail-closed reversible draft validation for one candidate."""

    candidate_id = _candidate_id(candidate)
    violations: list[SurfaceMapCandidateViolation] = []

    confidence = candidate.get("selector_confidence")
    if not _confidence_at_or_above(confidence, minimum_selector_confidence):
        violations.append(
            _violation(
                candidate_id,
                "low_selector_confidence",
                f"selector_confidence must be numeric and at least {minimum_selector_confidence}",
            )
        )

    if not _has_route_evidence(candidate):
        violations.append(
            _violation(
                candidate_id,
                "missing_route_evidence",
                "route or url_pattern evidence is required before reversible draft actions",
            )
        )

    if not _has_heading_evidence(candidate):
        violations.append(
            _violation(
                candidate_id,
                "missing_heading_evidence",
                "page heading or heading evidence is required before reversible draft actions",
            )
        )

    violations.extend(_required_label_violations(candidate_id, candidate))
    violations.extend(_consequential_reversible_control_violations(candidate_id, candidate))

    return SurfaceMapCandidateValidationResult(
        candidate_id=candidate_id,
        reversible_draft_allowed=not violations,
        violations=tuple(violations),
    )


def validate_surface_map_candidates(
    candidates: Sequence[Mapping[str, Any]],
    *,
    minimum_selector_confidence: float = MINIMUM_REVERSIBLE_SELECTOR_CONFIDENCE,
) -> SurfaceMapCandidateBatchValidationResult:
    results = tuple(
        validate_surface_map_candidate(
            candidate,
            minimum_selector_confidence=minimum_selector_confidence,
        )
        for candidate in candidates
    )
    return SurfaceMapCandidateBatchValidationResult(
        reversible_draft_allowed=all(result.reversible_draft_allowed for result in results),
        results=results,
    )


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    for key in ("candidate_id", "surface_id", "id"):
        value = candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown_surface_candidate"


def _violation(candidate_id: str, code: str, message: str) -> SurfaceMapCandidateViolation:
    return SurfaceMapCandidateViolation(candidate_id=candidate_id, code=code, message=message)


def _confidence_at_or_above(value: Any, minimum: float) -> bool:
    if isinstance(value, bool):
        return False
    try:
        return float(value) >= minimum
    except (TypeError, ValueError):
        return False


def _has_route_evidence(candidate: Mapping[str, Any]) -> bool:
    route_values = _string_values(
        candidate.get("route_evidence"),
        candidate.get("routes"),
        candidate.get("url_pattern"),
    )
    return bool(route_values)


def _has_heading_evidence(candidate: Mapping[str, Any]) -> bool:
    heading_values = _string_values(
        candidate.get("heading_evidence"),
        candidate.get("headings"),
        candidate.get("page_heading"),
    )
    return bool(heading_values)


def _required_label_violations(
    candidate_id: str,
    candidate: Mapping[str, Any],
) -> tuple[SurfaceMapCandidateViolation, ...]:
    violations: list[SurfaceMapCandidateViolation] = []
    labels_by_value: dict[str, list[str]] = {}

    for field in _mapping_items(candidate.get("fields")):
        if field.get("required") is not True:
            continue
        field_id = _item_id(field, "field")
        labels = _label_values(field)
        if len(labels) != 1:
            violations.append(
                _violation(
                    candidate_id,
                    "ambiguous_required_label",
                    f"required field {field_id!r} must have exactly one non-empty label",
                )
            )
            continue
        labels_by_value.setdefault(_normalize(labels[0]), []).append(field_id)

    for label, field_ids in sorted(labels_by_value.items()):
        if len(field_ids) > 1:
            joined = ", ".join(sorted(field_ids))
            violations.append(
                _violation(
                    candidate_id,
                    "ambiguous_required_label",
                    f"required label {label!r} is shared by fields: {joined}",
                )
            )

    return tuple(violations)


def _consequential_reversible_control_violations(
    candidate_id: str,
    candidate: Mapping[str, Any],
) -> tuple[SurfaceMapCandidateViolation, ...]:
    violations: list[SurfaceMapCandidateViolation] = []

    for collection_name in CONTROL_COLLECTIONS:
        for control in _mapping_items(candidate.get(collection_name)):
            if not _is_reversible_control(control):
                continue
            if collection_name != "actions" or _looks_consequential(control):
                control_id = _item_id(control, "control")
                violations.append(
                    _violation(
                        candidate_id,
                        "consequential_control_marked_reversible",
                        f"{collection_name} item {control_id!r} must not be classified as reversible",
                    )
                )

    return tuple(violations)


def _is_reversible_control(control: Mapping[str, Any]) -> bool:
    if control.get("reversible") is True:
        return True
    for key in ("classification", "action_class", "actionClass", "class"):
        value = control.get(key)
        if isinstance(value, str) and _normalize(value) in REVERSIBLE_CLASSIFICATIONS:
            return True
    return False


def _looks_consequential(control: Mapping[str, Any]) -> bool:
    values = _string_values(
        control.get("id"),
        control.get("kind"),
        control.get("type"),
        control.get("label"),
        control.get("name"),
        control.get("text"),
        control.get("aria_label"),
        control.get("ariaLabel"),
    )
    tokens = " ".join(values).replace("_", "-").replace("/", "-").split()
    expanded: set[str] = set()
    for token in tokens:
        expanded.update(part for part in token.split("-") if part)
    return bool(expanded.intersection(CONSEQUENTIAL_CONTROL_TOKENS))


def _mapping_items(raw: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(raw, Mapping):
        return (raw,)
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        return tuple(item for item in raw if isinstance(item, Mapping))
    return ()


def _item_id(item: Mapping[str, Any], fallback: str) -> str:
    for key in ("id", "field_id", "action_id", "control_id", "name"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _label_values(item: Mapping[str, Any]) -> tuple[str, ...]:
    return _string_values(
        item.get("label"),
        item.get("labels"),
        item.get("label_evidence"),
        item.get("accessible_name"),
        item.get("aria_label"),
        item.get("ariaLabel"),
    )


def _string_values(*raw_values: Any) -> tuple[str, ...]:
    values: list[str] = []
    for raw in raw_values:
        values.extend(_flatten_strings(raw))
    return tuple(value for value in (_clean(value) for value in values) if value)


def _flatten_strings(raw: Any) -> list[str]:
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, Mapping):
        values: list[str] = []
        for key in ("text", "label", "name", "title", "heading", "path", "href", "route", "value"):
            value = raw.get(key)
            if isinstance(value, str):
                values.append(value)
        return values
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        values = []
        for item in raw:
            values.extend(_flatten_strings(item))
        return values
    return []


def _clean(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize(value: str) -> str:
    return _clean(value).casefold()
