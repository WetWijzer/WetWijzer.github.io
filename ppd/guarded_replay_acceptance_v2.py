"""Validation for guarded agent replay acceptance packet v2.

The validator is intentionally small and deterministic. It accepts plain Python
mappings so fixtures can stay local and no browser, session, crawl, or download
artifacts are needed during validation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


REQUIRED_REVIEW_PLACEHOLDERS = (
    "missing_fact_prompt_review",
    "blocked_action_review",
    "reversible_draft_preview_review",
)

MUTATION_FLAGS = (
    "active_prompt_mutation",
    "active_contract_mutation",
    "active_guardrail_mutation",
    "active_source_mutation",
    "active_surface_mutation",
    "active_release_state_mutation",
)

PROHIBITED_ARTIFACT_MARKERS = (
    "private",
    "session",
    "browser",
    "raw",
    "downloaded",
)

LIVE_OR_CRAWL_CLAIM_MARKERS = (
    "live_devhub",
    "live devhub",
    "devhub live",
    "crawl_claim",
    "crawl claim",
    "crawled",
    "live crawl",
)

CONSEQUENTIAL_OFFICIAL_ACTION_MARKERS = (
    "submitted permit",
    "filed permit",
    "certified",
    "approved by pp&d",
    "approved by ppd",
    "official approval",
    "official action completed",
    "inspection scheduled",
    "application submitted",
)

LEGAL_OR_PERMITTING_GUARANTEE_MARKERS = (
    "guarantee",
    "guaranteed",
    "legally sufficient",
    "legal advice",
    "permit will be approved",
    "approval is assured",
    "compliant with all laws",
    "no permit required",
)


class GuardedReplayAcceptanceV2Error(ValueError):
    """Raised when guarded replay acceptance packet v2 validation fails."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def validate_acceptance_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a guarded replay acceptance packet v2."""

    errors: list[str] = []

    if packet.get("version") != 2:
        errors.append("version must be 2")

    reviewer_rows = _as_sequence(packet.get("reviewer_acceptance_rows"))
    if not reviewer_rows:
        errors.append("missing reviewer acceptance rows")
    else:
        for index, row in enumerate(reviewer_rows):
            if not isinstance(row, Mapping):
                errors.append(f"reviewer acceptance row {index} must be an object")
                continue
            if not _non_empty_text(row.get("reviewer")):
                errors.append(f"reviewer acceptance row {index} missing reviewer")
            if row.get("accepted") is not True:
                errors.append(f"reviewer acceptance row {index} is not accepted")
            if not _non_empty_text(row.get("reviewed_at")):
                errors.append(f"reviewer acceptance row {index} missing reviewed_at")

    traces = _as_sequence(packet.get("scenario_to_evidence_traces"))
    if not traces:
        errors.append("missing scenario-to-evidence traces")
    else:
        for index, trace in enumerate(traces):
            if not isinstance(trace, Mapping):
                errors.append(f"scenario-to-evidence trace {index} must be an object")
                continue
            if not _non_empty_text(trace.get("scenario")):
                errors.append(f"scenario-to-evidence trace {index} missing scenario")
            if not _as_sequence(trace.get("evidence")):
                errors.append(f"scenario-to-evidence trace {index} missing evidence")

    review_placeholders = packet.get("review_placeholders")
    if not isinstance(review_placeholders, Mapping):
        errors.append("missing review placeholders")
    else:
        for key in REQUIRED_REVIEW_PLACEHOLDERS:
            if not _placeholder_present(review_placeholders.get(key)):
                errors.append(f"missing {key} placeholder")

    if not _as_sequence(packet.get("unresolved_risk_notes")):
        errors.append("missing unresolved-risk notes")

    if not _as_sequence(packet.get("validation_commands")):
        errors.append("missing validation commands")

    _reject_artifacts(packet.get("artifacts"), errors)
    _reject_text_claims(packet.get("claims"), errors)
    _reject_text_claims(packet.get("notes"), errors)
    _reject_text_claims(packet.get("summary"), errors)
    _reject_mutation_flags(packet.get("mutation_flags"), errors)

    return errors


def require_acceptance_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise when the packet is not acceptable."""

    errors = validate_acceptance_packet_v2(packet)
    if errors:
        raise GuardedReplayAcceptanceV2Error(errors)


def _as_sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, str):
        return ()
    if isinstance(value, Sequence):
        return value
    return ()


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _placeholder_present(value: Any) -> bool:
    if isinstance(value, Mapping):
        status = value.get("status")
        return status in {"pending_review", "not_applicable_reviewed"}
    return _non_empty_text(value)


def _reject_artifacts(value: Any, errors: list[str]) -> None:
    for artifact in _iter_text_values(value):
        lowered = artifact.lower()
        for marker in PROHIBITED_ARTIFACT_MARKERS:
            if marker in lowered:
                errors.append(f"prohibited artifact marker: {marker}")


def _reject_text_claims(value: Any, errors: list[str]) -> None:
    text = " ".join(_iter_text_values(value)).lower()
    if not text:
        return
    for marker in LIVE_OR_CRAWL_CLAIM_MARKERS:
        if marker in text:
            errors.append(f"prohibited live DevHub or crawl claim: {marker}")
    for marker in CONSEQUENTIAL_OFFICIAL_ACTION_MARKERS:
        if marker in text:
            errors.append(f"prohibited consequential official action language: {marker}")
    for marker in LEGAL_OR_PERMITTING_GUARANTEE_MARKERS:
        if marker in text:
            errors.append(f"prohibited legal or permitting guarantee: {marker}")


def _reject_mutation_flags(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        return
    for flag in MUTATION_FLAGS:
        if value.get(flag) is True:
            errors.append(f"active mutation flag is not allowed: {flag}")


def _iter_text_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        values: list[str] = []
        for key, item in value.items():
            values.extend(_iter_text_values(key))
            values.extend(_iter_text_values(item))
        return values
    if isinstance(value, Sequence):
        values = []
        for item in value:
            values.extend(_iter_text_values(item))
        return values
    return [str(value)]
