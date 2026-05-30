"""Fixture-first PP&D prompt consumer dry-run transcript packet.

This module intentionally consumes committed fixtures only. It does not call live
LLMs, DevHub, private document stores, browser automation, or mutable agent
state. The packet is meant to be used by tests and supervisors as a deterministic
expected-response transcript for prompt-consumer behavior.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

SCHEMA_VERSION = "ppd.prompt_consumer_dry_run_transcript_packet.v1"

REQUIRED_RESPONSE_IDS = (
    "missing_information_prompt",
    "safe_read_only_summary",
    "draft_preview_boundaries",
    "refusal_explanation",
    "exact_confirmation_checkpoint",
    "offline_validation_commands",
    "side_effect_attestations",
)

DISALLOWED_ATTESTATION_FLAGS = (
    "live_llm_used",
    "devhub_accessed",
    "private_documents_loaded",
    "system_prompt_disclosed",
    "agent_state_mutated",
)


def build_prompt_consumer_dry_run_transcript_packet(
    prompt_refresh_release_handoff: dict[str, Any],
    user_gap_analysis: dict[str, Any],
    guarded_actions: dict[str, Any],
    reversible_draft_previews: dict[str, Any],
) -> dict[str, Any]:
    """Build a deterministic dry-run packet from already-committed fixtures."""

    release_id = _packet_id(prompt_refresh_release_handoff)
    gap_id = _packet_id(user_gap_analysis)
    guard_id = _packet_id(guarded_actions)
    draft_id = _packet_id(reversible_draft_previews)

    missing_facts = user_gap_analysis.get("missing_facts", [])
    missing_documents = user_gap_analysis.get("missing_documents", [])
    next_safe_actions = user_gap_analysis.get("next_safe_actions", [])
    guarded_action_items = guarded_actions.get("guarded_actions", [])
    draft_preview_items = reversible_draft_previews.get("draft_previews", [])

    missing_fact_labels = [_label(item) for item in missing_facts]
    missing_document_labels = [_label(item) for item in missing_documents]
    read_only_labels = [_label(item) for item in next_safe_actions]
    guarded_labels = [_label(item) for item in guarded_action_items]
    preview_labels = [_label(item) for item in draft_preview_items]

    missing_citations = _citations(gap_id, missing_facts + missing_documents)
    read_only_citations = _citations(gap_id, next_safe_actions)
    guarded_citations = _citations(guard_id, guarded_action_items)
    preview_citations = _citations(draft_id, draft_preview_items)
    release_citations = _citations(
        release_id,
        prompt_refresh_release_handoff.get("release_evidence", []),
    )

    consumed_packets = [
        {"role": "prompt_refresh_release_handoff", "packet_id": release_id},
        {"role": "user_gap_analysis", "packet_id": gap_id},
        {"role": "guarded_actions", "packet_id": guard_id},
        {"role": "reversible_draft_previews", "packet_id": draft_id},
    ]

    responses = [
        {
            "response_id": "missing_information_prompt",
            "response_type": "expected_agent_response",
            "expected_agent_response": (
                "I need the following missing information before I can say this PP&D workflow is ready: "
                + _join_or_none(missing_fact_labels + missing_document_labels)
                + ". I will not infer these facts from silence or substitute uncited assumptions."
            ),
            "citations": missing_citations,
            "assertions": [
                "asks only for missing fixture facts and documents",
                "does not invent permit facts",
                "does not request credentials or private session material",
            ],
        },
        {
            "response_id": "safe_read_only_summary",
            "response_type": "expected_agent_response",
            "expected_agent_response": (
                "Based on the fixture, I can safely summarize the current case and offer read-only next steps: "
                + _join_or_none(read_only_labels)
                + ". These steps do not change DevHub, submit forms, upload files, schedule inspections, or pay fees."
            ),
            "citations": read_only_citations,
            "assertions": [
                "summary is limited to fixture-provided facts",
                "safe actions are read-only",
                "no authenticated DevHub action is implied",
            ],
        },
        {
            "response_id": "draft_preview_boundaries",
            "response_type": "expected_agent_response",
            "expected_agent_response": (
                "I can prepare reversible local draft previews for: "
                + _join_or_none(preview_labels)
                + ". A draft preview is not an upload, certification, submission, inspection request, cancellation, or payment."
            ),
            "citations": preview_citations,
            "assertions": [
                "draft work remains reversible",
                "preview output is local and fixture-derived",
                "official actions remain gated",
            ],
        },
        {
            "response_id": "refusal_explanation",
            "response_type": "expected_agent_response",
            "expected_agent_response": (
                "I cannot perform consequential PP&D actions from this dry run. The guarded actions are: "
                + _join_or_none(guarded_labels)
                + ". They require attendance, source-backed review, and action-specific confirmation before any live step."
            ),
            "citations": guarded_citations,
            "assertions": [
                "refuses unattended upload, submission, certification, scheduling, cancellation, and payment",
                "explains the boundary without exposing hidden prompts",
                "keeps private user material out of the transcript",
            ],
        },
        {
            "response_id": "exact_confirmation_checkpoint",
            "response_type": "expected_agent_response",
            "expected_agent_response": (
                "Before any live consequential action, I would stop at an exact-confirmation checkpoint naming the action, target permit or application, affected document or fee, expected result, and irreversible risk. This packet does not execute that action."
            ),
            "citations": guarded_citations + release_citations,
            "assertions": [
                "requires action-specific confirmation text",
                "does not treat general approval as enough",
                "does not execute the guarded action in dry-run mode",
            ],
        },
        {
            "response_id": "offline_validation_commands",
            "response_type": "expected_agent_response",
            "expected_agent_response": (
                "Offline validation is limited to deterministic local checks: python3 -m py_compile ppd/prompt_consumer_dry_run_transcript_packet.py; python3 -m unittest ppd.tests.test_prompt_consumer_dry_run_transcript_packet; python3 ppd/daemon/ppd_daemon.py --self-test."
            ),
            "citations": release_citations,
            "assertions": [
                "validation commands are local and offline",
                "no live crawl is required",
                "no authenticated browser or DevHub session is required",
            ],
        },
        {
            "response_id": "side_effect_attestations",
            "response_type": "expected_agent_response",
            "expected_agent_response": (
                "Attestation: this dry-run transcript used committed fixtures only; no live LLM call, no DevHub access, no private document access, no hidden prompt disclosure, and no agent state mutation occurred."
            ),
            "citations": release_citations + missing_citations + guarded_citations + preview_citations,
            "assertions": [
                "no-live-LLM",
                "no-DevHub",
                "no-private-document",
                "no-prompt-disclosure",
                "no-agent-state-mutation",
            ],
        },
    ]

    packet = {
        "schema_version": SCHEMA_VERSION,
        "packet_id": "prompt-consumer-dry-run-transcript-001",
        "mode": "fixture_first_offline_dry_run",
        "consumed_fixture_packets": consumed_packets,
        "side_effects": {
            "live_llm_used": False,
            "devhub_accessed": False,
            "private_documents_loaded": False,
            "system_prompt_disclosed": False,
            "agent_state_mutated": False,
        },
        "expected_agent_responses": responses,
    }
    return deepcopy(packet)


def validate_prompt_consumer_dry_run_transcript_packet(packet: dict[str, Any]) -> list[str]:
    """Return validation errors for a generated or fixture packet."""

    errors: list[str] = []
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append("unexpected schema_version")
    if packet.get("mode") != "fixture_first_offline_dry_run":
        errors.append("mode must be fixture_first_offline_dry_run")

    consumed = packet.get("consumed_fixture_packets")
    if not isinstance(consumed, list) or len(consumed) != 4:
        errors.append("packet must consume exactly four fixture packets")
    elif {item.get("role") for item in consumed if isinstance(item, dict)} != {
        "prompt_refresh_release_handoff",
        "user_gap_analysis",
        "guarded_actions",
        "reversible_draft_previews",
    }:
        errors.append("consumed fixture packet roles are incomplete")

    side_effects = packet.get("side_effects")
    if not isinstance(side_effects, dict):
        errors.append("side_effects must be a mapping")
    else:
        for flag in DISALLOWED_ATTESTATION_FLAGS:
            if side_effects.get(flag) is not False:
                errors.append(f"{flag} must be false")

    responses = packet.get("expected_agent_responses")
    if not isinstance(responses, list):
        errors.append("expected_agent_responses must be a list")
        return errors

    response_ids = [item.get("response_id") for item in responses if isinstance(item, dict)]
    if tuple(response_ids) != REQUIRED_RESPONSE_IDS:
        errors.append("expected response ids or order do not match the dry-run contract")

    for response in responses:
        if not isinstance(response, dict):
            errors.append("response entries must be mappings")
            continue
        response_id = response.get("response_id", "")
        text = response.get("expected_agent_response")
        citations = response.get("citations")
        assertions = response.get("assertions")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"{response_id} must include expected response text")
        if not isinstance(citations, list) or not citations:
            errors.append(f"{response_id} must include citations")
        elif any(not isinstance(citation, str) or "#" not in citation for citation in citations):
            errors.append(f"{response_id} citations must be packet-scoped strings")
        if not isinstance(assertions, list) or not assertions:
            errors.append(f"{response_id} must include assertions")

    return errors


def _packet_id(packet: dict[str, Any]) -> str:
    packet_id = packet.get("packet_id") or packet.get("case_id") or packet.get("fixture_id")
    if not isinstance(packet_id, str) or not packet_id:
        raise ValueError("fixture packet is missing a stable packet_id")
    return packet_id


def _label(item: dict[str, Any]) -> str:
    for key in ("label", "prompt", "name", "action", "summary"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fixture item is missing a display label")


def _citation_id(item: dict[str, Any]) -> str:
    value = item.get("citation_id") or item.get("evidence_id") or item.get("id")
    if not isinstance(value, str) or not value:
        raise ValueError("fixture item is missing a citation_id")
    return value


def _citations(packet_id: str, items: list[dict[str, Any]]) -> list[str]:
    citations: list[str] = []
    for item in items:
        citation = f"{packet_id}#{_citation_id(item)}"
        if citation not in citations:
            citations.append(citation)
    return citations


def _join_or_none(values: list[str]) -> str:
    if not values:
        return "none in this fixture"
    if len(values) == 1:
        return values[0]
    return "; ".join(values)
