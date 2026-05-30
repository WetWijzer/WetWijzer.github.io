"""Fixture-first active promotion preflight gate.

This module intentionally performs no filesystem writes, network access, release-state
updates, active-artifact mutation, DevHub access, or official actions. It converts an
inactive sandbox rehearsal packet into a deterministic readiness report that a human
can review before any separate active promotion workflow exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

PACKET_VERSION = "inactive_promotion_sandbox_rehearsal_packet_v1"
REPORT_VERSION = "active_promotion_preflight_gate_v1"

_MUTATION_BLOCKERS = (
    "fixture_promotion_apply",
    "active_artifact_write",
    "release_state_update",
    "prompt_change",
    "live_source_crawl",
    "devhub_access",
    "official_action",
)

_REQUIRED_REPLAY_CHECKS = (
    "packet_schema_loaded_from_fixture",
    "inactive_rehearsal_status_verified",
    "planned_active_mutations_blocked",
    "validation_evidence_replayed",
    "rollback_inputs_present",
    "release_state_left_unchanged",
)


@dataclass(frozen=True)
class PreflightDecision:
    """Single final go/no-go row for the active promotion preflight."""

    row_id: str
    gate: str
    decision: str
    rationale: str
    evidence_refs: tuple[str, ...]
    human_approval_required: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "gate": self.gate,
            "decision": self.decision,
            "rationale": self.rationale,
            "evidence_refs": list(self.evidence_refs),
            "human_approval_required": self.human_approval_required,
        }


def build_active_promotion_preflight(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic active-promotion preflight report from a fixture packet.

    The packet is expected to be an inactive sandbox rehearsal packet. The returned
    report is deliberately non-mutating and uses explicit BLOCKED rows for any active
    mutation, release-state, DevHub, live-crawl, prompt, or official-action request.
    """

    packet_id = _text(packet.get("packet_id"), "unknown-packet")
    packet_version = _text(packet.get("packet_version"), "")
    rehearsal_state = _text(packet.get("rehearsal_state"), "")
    source_fixture = _text(packet.get("source_fixture"), "unrecorded fixture")
    validations = _string_list(packet.get("validation_evidence"))
    rollback_inputs = _string_list(packet.get("rollback_inputs"))
    requested_actions = tuple(_string_list(packet.get("requested_actions")))
    release_state_before = _text(packet.get("release_state_before"), "unknown")

    rows = [
        PreflightDecision(
            row_id="go-no-go-001",
            gate="packet version",
            decision="GO" if packet_version == PACKET_VERSION else "NO_GO",
            rationale=(
                "Fixture packet declares the expected inactive sandbox rehearsal schema."
                if packet_version == PACKET_VERSION
                else "Fixture packet does not declare the expected inactive sandbox rehearsal schema."
            ),
            evidence_refs=(source_fixture,),
        ),
        PreflightDecision(
            row_id="go-no-go-002",
            gate="inactive rehearsal state",
            decision="GO" if rehearsal_state == "inactive_sandbox" else "NO_GO",
            rationale=(
                "Packet is marked as an inactive sandbox rehearsal, so it is eligible for preflight review only."
                if rehearsal_state == "inactive_sandbox"
                else "Packet is not marked as an inactive sandbox rehearsal."
            ),
            evidence_refs=(packet_id,),
        ),
        PreflightDecision(
            row_id="go-no-go-003",
            gate="validation replay evidence",
            decision="GO" if validations else "NO_GO",
            rationale=(
                "Validation evidence is present for fixture replay."
                if validations
                else "No validation evidence was provided for replay."
            ),
            evidence_refs=tuple(validations),
        ),
        PreflightDecision(
            row_id="go-no-go-004",
            gate="rollback readiness",
            decision="GO" if rollback_inputs else "NO_GO",
            rationale=(
                "Rollback inputs are identified for human review before any separate active workflow."
                if rollback_inputs
                else "Rollback inputs are missing."
            ),
            evidence_refs=tuple(rollback_inputs),
            human_approval_required=True,
        ),
        PreflightDecision(
            row_id="go-no-go-005",
            gate="active mutation boundary",
            decision="BLOCKED" if requested_actions else "GO",
            rationale=(
                "Requested active-side actions are inventoried and blocked by this fixture-first preflight."
                if requested_actions
                else "No active-side actions were requested by the rehearsal packet."
            ),
            evidence_refs=requested_actions or ("no requested active mutation",),
            human_approval_required=bool(requested_actions),
        ),
    ]

    blocker_inventory = [
        {
            "blocker_id": f"active-mutation-blocker-{index:03d}",
            "blocked_action": action,
            "status": "BLOCKED",
            "reason": "The active promotion preflight gate is fixture-only and non-mutating.",
        }
        for index, action in enumerate(_MUTATION_BLOCKERS, start=1)
    ]

    replay_checklist = [
        {
            "check_id": f"validation-replay-{index:03d}",
            "check": check,
            "status": _check_status(check, packet_version, rehearsal_state, validations, rollback_inputs),
        }
        for index, check in enumerate(_REQUIRED_REPLAY_CHECKS, start=1)
    ]

    row_decisions = [row.decision for row in rows]
    final_decision = "NO_GO" if "NO_GO" in row_decisions else "GO_WITH_HUMAN_APPROVAL_REQUIRED"
    if "BLOCKED" in row_decisions:
        final_decision = "NO_GO_ACTIVE_MUTATION_BLOCKED"

    return {
        "report_version": REPORT_VERSION,
        "source_packet_id": packet_id,
        "source_packet_version": packet_version,
        "source_fixture": source_fixture,
        "final_decision": final_decision,
        "go_no_go_rows": [row.as_dict() for row in rows],
        "human_approval_placeholders": [
            {
                "approval_id": "human-approval-001",
                "label": "Promotion owner approval",
                "status": "PENDING_HUMAN_REVIEW",
                "required_before": "any separate active promotion workflow",
            },
            {
                "approval_id": "human-approval-002",
                "label": "Rollback owner approval",
                "status": "PENDING_HUMAN_REVIEW",
                "required_before": "any release-state mutation",
            },
        ],
        "active_mutation_blocker_inventory": blocker_inventory,
        "validation_replay_checklist": replay_checklist,
        "rollback_readiness_summary": {
            "status": "READY_FOR_HUMAN_REVIEW" if rollback_inputs else "MISSING_ROLLBACK_INPUTS",
            "rollback_inputs": rollback_inputs,
            "release_state_before": release_state_before,
            "release_state_after": release_state_before,
        },
        "release_state_nonmutation_notes": [
            "No fixture promotion was applied.",
            "No active artifact was changed.",
            "No prompt was changed.",
            "No release state was updated.",
            "No live source was crawled.",
            "No DevHub session was opened or accessed.",
            "No official action was performed.",
        ],
        "nonmutation_flags": {
            "fixture_promotion_applied": False,
            "active_artifacts_mutated": False,
            "prompts_changed": False,
            "release_state_updated": False,
            "live_sources_crawled": False,
            "devhub_accessed": False,
            "official_actions_performed": False,
        },
    }


def _check_status(
    check: str,
    packet_version: str,
    rehearsal_state: str,
    validations: list[str],
    rollback_inputs: list[str],
) -> str:
    if check == "packet_schema_loaded_from_fixture":
        return "PASS" if packet_version == PACKET_VERSION else "FAIL"
    if check == "inactive_rehearsal_status_verified":
        return "PASS" if rehearsal_state == "inactive_sandbox" else "FAIL"
    if check == "validation_evidence_replayed":
        return "PASS" if validations else "FAIL"
    if check == "rollback_inputs_present":
        return "PASS" if rollback_inputs else "FAIL"
    return "PASS"


def _text(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item.strip())
    return result
