"""Fixture-first PP&D agent response recommendations.

This module is intentionally side-effect free. It accepts a ready-to-draft
packet plus a refreshed guardrail status object and emits the small set of
agent-facing recommendations needed by the synthetic PP&D case fixture.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


RECOMMENDATION_ORDER = (
    "cited_ask",
    "local_preview",
    "reversible_draft",
    "manual_handoff",
    "refused_action",
)


@dataclass(frozen=True)
class Recommendation:
    kind: str
    status: str
    title: str
    summary: str
    reasons: list[str]
    citations: list[dict[str, str]]
    requires_user_attendance: bool
    reversible: bool
    blocked_actions: list[str]
    next_action: str


def build_agent_recommendations(
    ready_to_draft_packet: Mapping[str, Any],
    refreshed_guardrail_status: Mapping[str, Any],
) -> dict[str, Any]:
    """Convert a ready-to-draft packet and guardrail refresh into recommendations.

    The contract is deliberately conservative: it can recommend local preview
    and reversible draft preparation, but official DevHub actions remain either
    manual handoff or refused action recommendations.
    """

    _require_mapping(ready_to_draft_packet, "ready_to_draft_packet")
    _require_mapping(refreshed_guardrail_status, "refreshed_guardrail_status")

    evidence = _index_evidence(ready_to_draft_packet)
    evidence_refs = refreshed_guardrail_status.get("recommendation_evidence", {})
    if not isinstance(evidence_refs, Mapping):
        evidence_refs = {}

    gap_analysis = refreshed_guardrail_status.get("gap_analysis", {})
    if not isinstance(gap_analysis, Mapping):
        gap_analysis = {}

    required_confirmations = _string_list(gap_analysis.get("required_confirmations"))
    missing_facts = _string_list(gap_analysis.get("missing_facts"))
    missing_documents = _string_list(gap_analysis.get("missing_documents"))
    stale_evidence = _string_list(gap_analysis.get("stale_evidence"))
    conflicting_evidence = _string_list(gap_analysis.get("conflicting_evidence"))

    draft_targets = _string_list(ready_to_draft_packet.get("draft_targets"))
    blocked_actions = _string_list(refreshed_guardrail_status.get("blocked_actions"))
    manual_handoffs = _string_list(refreshed_guardrail_status.get("manual_handoffs"))
    refused_actions = _string_list(refreshed_guardrail_status.get("refused_actions"))

    ready_for_reversible_draft = (
        ready_to_draft_packet.get("readiness") == "ready_to_draft"
        and refreshed_guardrail_status.get("validation_status") == "current"
        and not missing_facts
        and not missing_documents
        and not stale_evidence
        and not conflicting_evidence
    )

    recommendations = [
        Recommendation(
            kind="cited_ask",
            status="recommended",
            title="Confirm cited case facts before drafting",
            summary="Ask only for source-backed confirmations that remain necessary before preparing the local draft packet.",
            reasons=required_confirmations or missing_facts or missing_documents,
            citations=_citations(evidence_refs.get("cited_ask"), evidence),
            requires_user_attendance=False,
            reversible=False,
            blocked_actions=[],
            next_action="Ask the user for the listed confirmations and keep the answers in the case facts, not in committed fixtures.",
        ),
        Recommendation(
            kind="local_preview",
            status="available",
            title="Generate a local preview",
            summary="Prepare a local-only preview of the field mapping and document checklist without signing in to DevHub or uploading files.",
            reasons=["Local preview is read-only and can be regenerated from the fixture packet."],
            citations=_citations(evidence_refs.get("local_preview"), evidence),
            requires_user_attendance=False,
            reversible=True,
            blocked_actions=[],
            next_action="Render a local preview for: " + _join_or_none(draft_targets),
        ),
        Recommendation(
            kind="reversible_draft",
            status="available" if ready_for_reversible_draft else "blocked",
            title="Prepare reversible draft values",
            summary="Draft form values and PDF mappings locally while stopping before certification, upload, payment, or submission.",
            reasons=_draft_reasons(ready_for_reversible_draft, stale_evidence, conflicting_evidence),
            citations=_citations(evidence_refs.get("reversible_draft"), evidence),
            requires_user_attendance=False,
            reversible=True,
            blocked_actions=blocked_actions,
            next_action="Create local draft values only; do not attach, certify, submit, schedule, cancel, or pay.",
        ),
        Recommendation(
            kind="manual_handoff",
            status="handoff_required",
            title="Hand off attended DevHub-only steps",
            summary="Require the user to complete account, authentication, security, and exact-confirmation steps in an attended browser session.",
            reasons=manual_handoffs,
            citations=_citations(evidence_refs.get("manual_handoff"), evidence),
            requires_user_attendance=True,
            reversible=False,
            blocked_actions=manual_handoffs,
            next_action="Pause automation and show the user which DevHub step needs attended handling.",
        ),
        Recommendation(
            kind="refused_action",
            status="refused",
            title="Refuse consequential official actions",
            summary="Do not perform official PP&D actions that would submit, certify, upload to the record, schedule, cancel, or pay fees.",
            reasons=refused_actions,
            citations=_citations(evidence_refs.get("refused_action"), evidence),
            requires_user_attendance=True,
            reversible=False,
            blocked_actions=refused_actions,
            next_action="Explain the refusal with citations and offer a local preview or reversible draft instead.",
        ),
    ]

    return {
        "case_id": str(ready_to_draft_packet.get("case_id", "")),
        "process_id": str(ready_to_draft_packet.get("process_id", "")),
        "guardrail_refreshed_at": str(refreshed_guardrail_status.get("refreshed_at", "")),
        "recommendation_order": list(RECOMMENDATION_ORDER),
        "recommendations": [asdict(recommendation) for recommendation in recommendations],
    }


def _require_mapping(value: Mapping[str, Any], name: str) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")


def _index_evidence(packet: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for raw_item in packet.get("source_evidence", []):
        if not isinstance(raw_item, Mapping):
            continue
        evidence_id = str(raw_item.get("evidence_id") or raw_item.get("id") or "")
        if not evidence_id:
            continue
        indexed[evidence_id] = {
            "evidence_id": evidence_id,
            "title": str(raw_item.get("title", "")),
            "url": str(raw_item.get("url", "")),
            "accessed_at": str(raw_item.get("accessed_at", "")),
            "quote": str(raw_item.get("quote") or raw_item.get("snippet") or ""),
        }
    return indexed


def _citations(raw_ids: Any, evidence: Mapping[str, dict[str, str]]) -> list[dict[str, str]]:
    citation_ids = _string_list(raw_ids)
    citations = [evidence[evidence_id] for evidence_id in citation_ids if evidence_id in evidence]
    if citations:
        return citations
    return list(evidence.values())[:1]


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _join_or_none(values: list[str]) -> str:
    if not values:
        return "no declared draft targets"
    return ", ".join(values)


def _draft_reasons(
    ready_for_reversible_draft: bool,
    stale_evidence: list[str],
    conflicting_evidence: list[str],
) -> list[str]:
    if ready_for_reversible_draft:
        return ["The refreshed guardrail status is current and the packet has no missing, stale, or conflicting required inputs."]
    reasons: list[str] = []
    reasons.extend(f"Stale evidence: {item}" for item in stale_evidence)
    reasons.extend(f"Conflicting evidence: {item}" for item in conflicting_evidence)
    if not reasons:
        reasons.append("The packet is not ready for reversible draft preparation.")
    return reasons
