"""Fail-closed validation for formal PP&D guardrail bundles.

This module is intentionally deterministic and side-effect free. It validates the
small JSON-like bundle shape an LLM agent must pass before it may plan
autonomous completion. Missing citations, stale evidence, private values, and
consequential or financial actions are proof-obligation failures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

CURRENT_EVIDENCE_STATES = frozenset({"current", "verified", "fresh"})
SAFE_ACTION_KINDS = frozenset({"analysis", "read_only", "local_preview", "draft", "reversible_draft"})
FINANCIAL_ACTION_KINDS = frozenset({"fee", "pay", "payment", "purchase", "refund", "enter_payment_details"})
CONSEQUENTIAL_ACTION_KINDS = frozenset(
    {
        "acknowledge",
        "cancel",
        "certify",
        "official_change",
        "reactivate",
        "schedule",
        "submit",
        "upload",
        "withdraw",
    }
)
PROOF_OBLIGATION_CODES = frozenset(
    {
        "missing_citation",
        "stale_evidence",
        "private_value_required",
        "consequential_action_blocked",
        "financial_action_blocked",
    }
)


@dataclass(frozen=True)
class FormalGuardrailFinding:
    """One deterministic reason autonomous planning must fail closed."""

    code: str
    message: str
    path: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "path": self.path}


def validate_formal_guardrail_bundle(bundle: Mapping[str, Any]) -> list[dict[str, str]]:
    """Return validation findings for a formal guardrail bundle.

    The accepted shape is deliberately small: source evidence, freshness,
    private-value predicates, fail-closed proof obligations, and a proposed
    autonomous plan. Any ambiguity is rejected because the caller is asking
    whether an LLM may plan without attended user confirmation.
    """

    findings: list[FormalGuardrailFinding] = []

    bundle_id = _non_empty_text(bundle.get("guardrail_bundle_id"))
    if bundle_id is None:
        findings.append(_finding("missing_bundle_id", "Formal guardrail bundle requires an id.", "guardrail_bundle_id"))

    validation_status = _normalized_text(bundle.get("validation_status"))
    if validation_status not in {"validated", "current"}:
        findings.append(
            _finding(
                "bundle_not_validated",
                "Formal guardrail bundle must be validated before autonomous planning.",
                "validation_status",
            )
        )

    source_evidence_ids = _string_list(bundle.get("source_evidence_ids"))
    if not source_evidence_ids:
        findings.append(
            _finding(
                "missing_source_evidence",
                "Autonomous planning requires at least one public source evidence id.",
                "source_evidence_ids",
            )
        )

    predicates = _mapping(bundle.get("deterministic_predicates"))
    if predicates is None:
        findings.append(
            _finding(
                "missing_deterministic_predicates",
                "Formal guardrail bundle requires deterministic predicates.",
                "deterministic_predicates",
            )
        )
        predicates = {}

    plan = _mapping(bundle.get("proposed_autonomous_plan"))
    if plan is None:
        findings.append(
            _finding(
                "missing_autonomous_plan",
                "Formal guardrail bundle requires a proposed autonomous plan to validate.",
                "proposed_autonomous_plan",
            )
        )
        plan = {}

    findings.extend(_validate_proof_obligation_inventory(bundle))
    findings.extend(_validate_citations(source_evidence_ids, plan))
    findings.extend(_validate_evidence_freshness(source_evidence_ids, predicates, plan))
    findings.extend(_validate_private_values(predicates, plan))
    findings.extend(_validate_actions(plan))

    return [finding.as_dict() for finding in findings]


def formal_guardrail_bundle_allows_autonomous_planning(bundle: Mapping[str, Any]) -> bool:
    """Return True only when the formal bundle has no fail-closed findings."""

    return not validate_formal_guardrail_bundle(bundle)


def _validate_proof_obligation_inventory(bundle: Mapping[str, Any]) -> list[FormalGuardrailFinding]:
    findings: list[FormalGuardrailFinding] = []
    obligations = bundle.get("fail_closed_proof_obligations") or bundle.get("proof_obligations")
    codes = set()
    for item in _sequence(obligations):
        if isinstance(item, Mapping):
            code = _normalized_text(item.get("code"))
            status = _normalized_text(item.get("status"))
            if code:
                codes.add(code)
            if code in PROOF_OBLIGATION_CODES and status not in {"fail_closed", "blocked"}:
                findings.append(
                    _finding(
                        "proof_obligation_not_fail_closed",
                        "Formal proof obligations must explicitly fail closed.",
                        "fail_closed_proof_obligations",
                    )
                )
        else:
            code = _normalized_text(item)
            if code:
                codes.add(code)

    missing = sorted(PROOF_OBLIGATION_CODES - codes)
    for code in missing:
        findings.append(
            _finding(
                "missing_proof_obligation",
                "Formal guardrail bundle is missing a required fail-closed proof obligation.",
                f"fail_closed_proof_obligations.{code}",
            )
        )
    return findings


def _validate_citations(source_evidence_ids: Sequence[str], plan: Mapping[str, Any]) -> list[FormalGuardrailFinding]:
    cited_ids = set(_string_list(plan.get("cited_evidence_ids")))
    findings: list[FormalGuardrailFinding] = []
    for evidence_id in sorted(set(source_evidence_ids) - cited_ids):
        findings.append(
            _finding(
                "missing_citation",
                "Every required source evidence id must be cited before autonomous planning.",
                f"proposed_autonomous_plan.cited_evidence_ids.{evidence_id}",
            )
        )
    return findings


def _validate_evidence_freshness(
    source_evidence_ids: Sequence[str],
    predicates: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> list[FormalGuardrailFinding]:
    freshness: dict[str, Any] = {}
    predicate_freshness = _mapping(predicates.get("evidence_freshness"))
    plan_freshness = _mapping(plan.get("evidence_freshness"))
    if predicate_freshness is not None:
        freshness.update(predicate_freshness)
    if plan_freshness is not None:
        freshness.update(plan_freshness)

    findings: list[FormalGuardrailFinding] = []
    for evidence_id in sorted(set(source_evidence_ids)):
        state = _normalized_text(freshness.get(evidence_id))
        if state not in CURRENT_EVIDENCE_STATES:
            findings.append(
                _finding(
                    "stale_evidence",
                    "Required source evidence must be verified current before autonomous planning.",
                    f"deterministic_predicates.evidence_freshness.{evidence_id}",
                )
            )
    return findings


def _validate_private_values(predicates: Mapping[str, Any], plan: Mapping[str, Any]) -> list[FormalGuardrailFinding]:
    fields = _string_list(predicates.get("private_value_fields")) + _string_list(plan.get("private_value_fields"))
    findings: list[FormalGuardrailFinding] = []
    for field in sorted(set(fields)):
        findings.append(
            _finding(
                "private_value_required",
                "Private user values must not be required for autonomous completion planning.",
                f"private_value_fields.{field}",
            )
        )
    return findings


def _validate_actions(plan: Mapping[str, Any]) -> list[FormalGuardrailFinding]:
    findings: list[FormalGuardrailFinding] = []
    for index, action in enumerate(_sequence(plan.get("proposed_actions") or plan.get("actions"))):
        if not isinstance(action, Mapping):
            findings.append(
                _finding(
                    "invalid_action",
                    "Proposed actions must be mappings with explicit safe classifications.",
                    f"proposed_autonomous_plan.proposed_actions.{index}",
                )
            )
            continue
        kind = _action_kind(action)
        action_path = f"proposed_autonomous_plan.proposed_actions.{index}"
        if kind in FINANCIAL_ACTION_KINDS:
            findings.append(
                _finding(
                    "financial_action_blocked",
                    "Financial actions fail closed before autonomous planning.",
                    action_path,
                )
            )
        elif kind in CONSEQUENTIAL_ACTION_KINDS:
            findings.append(
                _finding(
                    "consequential_action_blocked",
                    "Consequential official actions fail closed before autonomous planning.",
                    action_path,
                )
            )
        elif kind not in SAFE_ACTION_KINDS:
            findings.append(
                _finding(
                    "unsafe_action_kind",
                    "Only read-only, analysis, local preview, or reversible draft actions may be planned autonomously.",
                    action_path,
                )
            )
    return findings


def _action_kind(action: Mapping[str, Any]) -> str:
    for key in ("kind", "action_type", "classification", "action_class", "category"):
        value = _normalized_text(action.get(key))
        if value:
            return value
    action_text = " ".join(
        text
        for text in (
            _normalized_text(action.get("id")),
            _normalized_text(action.get("action_id")),
            _normalized_text(action.get("name")),
            _normalized_text(action.get("label")),
            _normalized_text(action.get("action")),
        )
        if text
    )
    for token in FINANCIAL_ACTION_KINDS | CONSEQUENTIAL_ACTION_KINDS:
        if token in action_text:
            return token
    return action_text or "unknown"


def _finding(code: str, message: str, path: str) -> FormalGuardrailFinding:
    return FormalGuardrailFinding(code=code, message=message, path=path)


def _mapping(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return value
    return None


def _sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        return [value]
    if isinstance(value, Sequence):
        return list(value)
    return []


def _string_list(value: Any) -> list[str]:
    result: list[str] = []
    for item in _sequence(value):
        text = _non_empty_text(item)
        if text is not None:
            result.append(text)
    return result


def _non_empty_text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _normalized_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().lower()
    return ""


__all__ = [
    "FormalGuardrailFinding",
    "formal_guardrail_bundle_allows_autonomous_planning",
    "validate_formal_guardrail_bundle",
]
