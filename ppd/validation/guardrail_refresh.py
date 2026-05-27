"""Validate guardrail bundle refreshes after high-risk PP&D requirement deltas.

This module is intentionally small and deterministic. It does not crawl DevHub,
open sessions, upload documents, or mutate daemon ledgers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

HIGH_RISK_REQUIREMENT_DELTA_TYPES = frozenset(
    {
        "fee",
        "fees",
        "deadline",
        "deadlines",
        "required_document",
        "required_documents",
        "unsupported_path",
        "unsupported_paths",
        "upload_rule",
        "upload_rules",
        "devhub_action_gate",
        "devhub_action_gates",
    }
)


@dataclass(frozen=True)
class GuardrailRefreshFinding:
    """A blocked affected bundle missing refreshed process-model evidence."""

    bundle_id: str
    delta_id: str
    delta_type: str
    reason: str


@dataclass(frozen=True)
class GuardrailRefreshValidation:
    """Validation result for affected guardrail bundle refresh state."""

    ok: bool
    findings: tuple[GuardrailRefreshFinding, ...]


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _sequence(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        item = value.strip()
        return (item,) if item else ()
    if isinstance(value, Iterable):
        items = []
        for item in value:
            text = _text(item)
            if text:
                items.append(text)
        return tuple(items)
    text = _text(value)
    return (text,) if text else ()


def is_high_risk_requirement_delta(delta: Mapping[str, object]) -> bool:
    """Return true when a requirement delta touches a guarded high-risk area."""

    delta_type = _text(delta.get("type") or delta.get("delta_type")).lower()
    if delta_type in HIGH_RISK_REQUIREMENT_DELTA_TYPES:
        return True

    categories = {item.lower() for item in _sequence(delta.get("categories"))}
    return bool(categories.intersection(HIGH_RISK_REQUIREMENT_DELTA_TYPES))


def affected_guardrail_bundles(delta: Mapping[str, object]) -> tuple[str, ...]:
    """Return affected guardrail bundle identifiers declared by a delta."""

    return _sequence(
        delta.get("affected_guardrail_bundles")
        or delta.get("guardrail_bundles")
        or delta.get("affected_bundles")
        or delta.get("bundles")
    )


def has_refreshed_process_model_evidence(
    bundle_id: str,
    delta: Mapping[str, object],
    evidence_records: Sequence[Mapping[str, object]],
) -> bool:
    """Return true when refreshed process-model evidence covers a bundle/delta pair."""

    delta_id = _text(delta.get("id") or delta.get("delta_id"))
    for evidence in evidence_records:
        if _text(evidence.get("kind") or evidence.get("evidence_type")) != "process_model_refresh":
            continue
        if _text(evidence.get("status")) not in {"present", "refreshed", "verified"}:
            continue
        if bundle_id not in _sequence(evidence.get("guardrail_bundles") or evidence.get("bundle_id")):
            continue
        evidence_delta_ids = _sequence(evidence.get("requirement_delta_ids") or evidence.get("delta_id"))
        if delta_id and delta_id not in evidence_delta_ids:
            continue
        source = _text(evidence.get("source") or evidence.get("process_model_source"))
        refreshed_at = _text(evidence.get("refreshed_at") or evidence.get("captured_at"))
        if source and refreshed_at:
            return True
    return False


def validate_guardrail_refresh(
    requirement_deltas: Sequence[Mapping[str, object]],
    guardrail_bundles: Sequence[Mapping[str, object]],
    evidence_records: Sequence[Mapping[str, object]],
) -> GuardrailRefreshValidation:
    """Validate affected guardrail bundles remain blocked until refresh evidence exists."""

    bundle_state = {
        _text(bundle.get("id") or bundle.get("bundle_id")): _text(bundle.get("state") or bundle.get("status")).lower()
        for bundle in guardrail_bundles
    }
    findings = []

    for delta in requirement_deltas:
        if not is_high_risk_requirement_delta(delta):
            continue
        delta_id = _text(delta.get("id") or delta.get("delta_id")) or "unknown-delta"
        delta_type = _text(delta.get("type") or delta.get("delta_type")) or "unknown"
        for bundle_id in affected_guardrail_bundles(delta):
            evidence_present = has_refreshed_process_model_evidence(bundle_id, delta, evidence_records)
            state = bundle_state.get(bundle_id, "blocked")
            if evidence_present:
                continue
            if state != "blocked":
                findings.append(
                    GuardrailRefreshFinding(
                        bundle_id=bundle_id,
                        delta_id=delta_id,
                        delta_type=delta_type,
                        reason="affected guardrail bundle must remain blocked until refreshed process-model evidence is present",
                    )
                )

    return GuardrailRefreshValidation(ok=not findings, findings=tuple(findings))


__all__ = [
    "HIGH_RISK_REQUIREMENT_DELTA_TYPES",
    "GuardrailRefreshFinding",
    "GuardrailRefreshValidation",
    "affected_guardrail_bundles",
    "has_refreshed_process_model_evidence",
    "is_high_risk_requirement_delta",
    "validate_guardrail_refresh",
]
