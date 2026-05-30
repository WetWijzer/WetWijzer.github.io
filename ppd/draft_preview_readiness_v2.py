"""Fixture-first draft preview readiness packet v2 builder.

This module is intentionally local-only. It consumes already-collected refresh
packets and emits deterministic readiness decisions for draft-fill previews.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


ATTESTATIONS = {
    "no_live_devhub": True,
    "no_private_documents": True,
    "no_pdf_write": True,
    "no_upload": True,
    "no_guardrail_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/draft_preview_readiness_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_draft_preview_readiness_v2.py"],
]


def build_draft_preview_readiness_packet_v2(source_packets: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic readiness packet from three refresh packets.

    Expected input keys:
    - guardrail_refresh_regression_matrix_v2
    - process_to_gap_analysis_refresh_packet_v2
    - surface_registry_refresh_acceptance_packet_v2
    """

    guardrails = _require_packet(source_packets, "guardrail_refresh_regression_matrix_v2")
    gaps = _require_packet(source_packets, "process_to_gap_analysis_refresh_packet_v2")
    surfaces = _require_packet(source_packets, "surface_registry_refresh_acceptance_packet_v2")

    local_preview_allowed = _truthy(guardrails, "local_draft_preview_allowed")
    private_document_blocked = _truthy(guardrails, "private_document_inputs_blocked")
    live_devhub_blocked = _truthy(guardrails, "live_devhub_actions_blocked")
    pdf_write_blocked = _truthy(guardrails, "pdf_write_blocked")
    upload_blocked = _truthy(guardrails, "upload_blocked")
    guardrail_mutation_blocked = _truthy(guardrails, "guardrail_mutation_blocked")
    registry_accepted = _truthy(surfaces, "accepted_for_local_preview")

    missing_user_facts = _as_list(gaps.get("required_user_facts"))
    missing_documents = _as_list(gaps.get("missing_document_checks"))
    exact_confirmations = _as_list(gaps.get("exact_confirmation_checkpoints"))
    reversible_predicates = _as_list(gaps.get("reversible_action_predicates"))
    reviewer_owner_fields = _as_list(gaps.get("reviewer_owner_fields"))

    required_inputs_ready = not missing_user_facts and not missing_documents
    safety_ready = all(
        [
            local_preview_allowed,
            private_document_blocked,
            live_devhub_blocked,
            pdf_write_blocked,
            upload_blocked,
            guardrail_mutation_blocked,
            registry_accepted,
        ]
    )

    ready_for_local_draft_preview = safety_ready and required_inputs_ready

    return {
        "packet_id": "draft_preview_readiness_packet_v2",
        "version": 2,
        "mode": "fixture_first_offline_only",
        "ready_for_local_draft_preview": ready_for_local_draft_preview,
        "readiness_decisions": [
            _decision(
                "local_draft_fill_preview",
                "allow" if ready_for_local_draft_preview else "block",
                [
                    _citation(guardrails, "guardrail_refresh_regression_matrix_v2"),
                    _citation(gaps, "process_to_gap_analysis_refresh_packet_v2"),
                    _citation(surfaces, "surface_registry_refresh_acceptance_packet_v2"),
                ],
                "Local preview is allowed only when guardrails pass, the surface registry accepts the flow, and no required facts or document checks are missing.",
            ),
            _decision(
                "live_devhub_or_upload_actions",
                "block",
                [_citation(guardrails, "guardrail_refresh_regression_matrix_v2")],
                "Draft preview readiness does not permit live DevHub sessions, uploads, PDF writes, or guardrail mutation.",
            ),
        ],
        "required_user_facts": missing_user_facts,
        "missing_document_checks": missing_documents,
        "reversible_action_predicates": reversible_predicates,
        "exact_confirmation_checkpoints": exact_confirmations,
        "reviewer_owner_fields": reviewer_owner_fields,
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
        "attestations": deepcopy(ATTESTATIONS),
        "source_packet_ids": {
            "guardrail_refresh_regression_matrix_v2": guardrails.get("packet_id"),
            "process_to_gap_analysis_refresh_packet_v2": gaps.get("packet_id"),
            "surface_registry_refresh_acceptance_packet_v2": surfaces.get("packet_id"),
        },
    }


def _require_packet(source_packets: dict[str, Any], key: str) -> dict[str, Any]:
    packet = source_packets.get(key)
    if not isinstance(packet, dict):
        raise ValueError(f"missing packet: {key}")
    return packet


def _truthy(packet: dict[str, Any], key: str) -> bool:
    return bool(packet.get(key))


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return deepcopy(value)
    return [deepcopy(value)]


def _citation(packet: dict[str, Any], fallback: str) -> dict[str, Any]:
    return {
        "packet_id": packet.get("packet_id", fallback),
        "reference": packet.get("reference", fallback),
    }


def _decision(name: str, outcome: str, citations: list[dict[str, Any]], rationale: str) -> dict[str, Any]:
    return {
        "decision": name,
        "outcome": outcome,
        "citations": citations,
        "rationale": rationale,
    }
