"""Build fixture-first PP&D agent consumer release handoff packets.

The compiler in this module is intentionally offline and deterministic. It
combines already-produced release validation packets into a consumer-facing
handoff summary without live LLM calls, DevHub access, prompt mutation,
guardrail mutation, or agent state mutation.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub_access",
    "no_prompt_mutation",
    "no_guardrail_mutation",
    "no_agent_state_mutation",
)

SOURCE_PACKET_KEYS = (
    "offline_release_candidate_validation_checklist_packet",
    "agent_release_consumer_handoff_packet",
    "agent_readiness_final_smoke_packet",
)

CONSEQUENTIAL_ACTIONS = (
    "submit_permit_request",
    "certify_acknowledgement",
    "upload_correction_to_official_record",
    "purchase_trade_permit",
    "schedule_inspection",
    "cancel_or_withdraw",
    "request_extension_or_reactivation",
    "enter_payment_detail",
    "submit_payment",
)


class ConsumerHandoffError(ValueError):
    """Raised when source packets cannot support a release handoff."""


@dataclass(frozen=True)
class EvidenceIndex:
    """Small helper that enforces cited consumer claims."""

    records: Mapping[str, Mapping[str, Any]]

    def require(self, evidence_ids: list[str], context: str) -> list[dict[str, str]]:
        if not evidence_ids:
            raise ConsumerHandoffError(f"{context} must include at least one evidence id")

        citations: list[dict[str, str]] = []
        for evidence_id in evidence_ids:
            record = self.records.get(evidence_id)
            if record is None:
                raise ConsumerHandoffError(f"{context} references unknown evidence id: {evidence_id}")
            citations.append(
                {
                    "evidence_id": evidence_id,
                    "source_packet": str(record["source_packet"]),
                    "claim": str(record["claim"]),
                }
            )
        return citations


def build_agent_consumer_release_handoff(source_packets: Mapping[str, Any]) -> dict[str, Any]:
    """Return a cited consumer-facing PP&D agent release handoff packet."""

    _require_source_packets(source_packets)
    evidence_index = EvidenceIndex(_build_evidence_index(source_packets))

    consumer_packet = source_packets["agent_release_consumer_handoff_packet"]
    checklist_packet = source_packets["offline_release_candidate_validation_checklist_packet"]
    smoke_packet = source_packets["agent_readiness_final_smoke_packet"]

    packet = {
        "packet_id": "ppd-agent-consumer-release-handoff-v1",
        "packet_type": "agent_consumer_release_handoff",
        "release_candidate_id": str(source_packets.get("release_candidate_id", "offline-fixture-rc")),
        "source_packet_ids": {
            key: str(source_packets[key]["packet_id"])
            for key in SOURCE_PACKET_KEYS
        },
        "consumer_facing_capability_limits": _compile_cited_items(
            consumer_packet.get("capability_limits", []), evidence_index, "capability limit"
        ),
        "supported_safe_read_only_scenarios": _compile_cited_items(
            consumer_packet.get("safe_read_only_scenarios", []), evidence_index, "safe read-only scenario"
        ),
        "reversible_draft_preview_boundaries": _compile_cited_items(
            consumer_packet.get("reversible_draft_preview_boundaries", []),
            evidence_index,
            "reversible draft-preview boundary",
        ),
        "blocked_consequential_action_messages": _blocked_action_messages(
            consumer_packet.get("blocked_consequential_actions", []), evidence_index
        ),
        "reviewer_owner_fields": _reviewer_owner_fields(checklist_packet, consumer_packet, smoke_packet),
        "attestations": _attestations(checklist_packet, consumer_packet, smoke_packet, evidence_index),
        "validation_inputs": {
            "offline_checklist_status": str(checklist_packet.get("status")),
            "consumer_handoff_status": str(consumer_packet.get("status")),
            "final_smoke_status": str(smoke_packet.get("status")),
        },
    }
    _validate_packet(packet)
    return packet


def _require_source_packets(source_packets: Mapping[str, Any]) -> None:
    missing = [key for key in SOURCE_PACKET_KEYS if key not in source_packets]
    if missing:
        raise ConsumerHandoffError(f"missing required source packet(s): {', '.join(missing)}")

    for key in SOURCE_PACKET_KEYS:
        packet = source_packets[key]
        if not isinstance(packet, Mapping):
            raise ConsumerHandoffError(f"{key} must be an object")
        if not packet.get("packet_id"):
            raise ConsumerHandoffError(f"{key} must include packet_id")


def _build_evidence_index(source_packets: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    evidence: dict[str, Mapping[str, Any]] = {}
    for packet_key in SOURCE_PACKET_KEYS:
        packet = source_packets[packet_key]
        for record in packet.get("evidence", []):
            evidence_id = str(record.get("evidence_id", ""))
            if not evidence_id:
                raise ConsumerHandoffError(f"{packet_key} includes evidence without evidence_id")
            if evidence_id in evidence:
                raise ConsumerHandoffError(f"duplicate evidence id: {evidence_id}")
            evidence[evidence_id] = {
                "source_packet": packet_key,
                "claim": str(record.get("claim", "")),
            }
    return evidence


def _compile_cited_items(
    items: list[Mapping[str, Any]], evidence_index: EvidenceIndex, context: str
) -> list[dict[str, Any]]:
    compiled: list[dict[str, Any]] = []
    for item in items:
        item_id = str(item.get("id", ""))
        statement = str(item.get("statement", ""))
        if not item_id or not statement:
            raise ConsumerHandoffError(f"{context} entries require id and statement")
        compiled.append(
            {
                "id": item_id,
                "statement": statement,
                "citations": evidence_index.require(list(item.get("evidence_ids", [])), f"{context} {item_id}"),
            }
        )
    if not compiled:
        raise ConsumerHandoffError(f"at least one {context} is required")
    return compiled


def _blocked_action_messages(
    blocked_actions: list[Mapping[str, Any]], evidence_index: EvidenceIndex
) -> list[dict[str, Any]]:
    actions_by_id = {str(action.get("action")): action for action in blocked_actions}
    missing = [action for action in CONSEQUENTIAL_ACTIONS if action not in actions_by_id]
    if missing:
        raise ConsumerHandoffError(
            "blocked consequential-action coverage is incomplete: " + ", ".join(missing)
        )

    messages: list[dict[str, Any]] = []
    for action_id in CONSEQUENTIAL_ACTIONS:
        action = actions_by_id[action_id]
        message = str(action.get("message", ""))
        if not message:
            raise ConsumerHandoffError(f"blocked action {action_id} requires a message")
        messages.append(
            {
                "action": action_id,
                "message": message,
                "required_handoff": str(action.get("required_handoff", "attended user action")),
                "citations": evidence_index.require(
                    list(action.get("evidence_ids", [])), f"blocked action {action_id}"
                ),
            }
        )
    return messages


def _reviewer_owner_fields(
    checklist_packet: Mapping[str, Any],
    consumer_packet: Mapping[str, Any],
    smoke_packet: Mapping[str, Any],
) -> dict[str, str]:
    owners = {
        "release_owner": consumer_packet.get("release_owner"),
        "policy_reviewer": checklist_packet.get("policy_reviewer"),
        "consumer_handoff_reviewer": consumer_packet.get("consumer_handoff_reviewer"),
        "smoke_reviewer": smoke_packet.get("smoke_reviewer"),
    }
    missing = [key for key, value in owners.items() if not value]
    if missing:
        raise ConsumerHandoffError("missing reviewer-owner field(s): " + ", ".join(missing))
    return {key: str(value) for key, value in owners.items()}


def _attestations(
    checklist_packet: Mapping[str, Any],
    consumer_packet: Mapping[str, Any],
    smoke_packet: Mapping[str, Any],
    evidence_index: EvidenceIndex,
) -> dict[str, dict[str, Any]]:
    source_attestations: dict[str, Any] = {}
    for packet in (checklist_packet, consumer_packet, smoke_packet):
        source_attestations.update(deepcopy(packet.get("attestations", {})))

    compiled: dict[str, dict[str, Any]] = {}
    for attestation_id in REQUIRED_ATTESTATIONS:
        attestation = source_attestations.get(attestation_id)
        if not isinstance(attestation, Mapping) or attestation.get("value") is not True:
            raise ConsumerHandoffError(f"required attestation is missing or false: {attestation_id}")
        compiled[attestation_id] = {
            "value": True,
            "statement": str(attestation.get("statement", "")),
            "citations": evidence_index.require(
                list(attestation.get("evidence_ids", [])), f"attestation {attestation_id}"
            ),
        }
    return compiled


def _validate_packet(packet: Mapping[str, Any]) -> None:
    for field in (
        "consumer_facing_capability_limits",
        "supported_safe_read_only_scenarios",
        "reversible_draft_preview_boundaries",
        "blocked_consequential_action_messages",
    ):
        for item in packet[field]:
            if not item.get("citations"):
                raise ConsumerHandoffError(f"{field} item is uncited")

    if set(packet["attestations"].keys()) != set(REQUIRED_ATTESTATIONS):
        raise ConsumerHandoffError("attestation set does not match required release handoff attestations")
