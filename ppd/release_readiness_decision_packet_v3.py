"""Fixture-first release readiness decision packets for PP&D.

This module intentionally produces synthetic, offline-only decision packets. It does
not read DevHub, crawl public sources, promote artifacts, or mutate release state.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

SCENARIOS = {"release-ready", "release-held", "release-rejected"}

OFFLINE_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "-m", "py_compile", "ppd/release_readiness_decision_packet_v3.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_release_readiness_decision_packet_v3.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)


@dataclass(frozen=True)
class DecisionPacket:
    packet_version: str
    scenario: str
    release_state_changed: bool
    artifact_promotion_allowed: bool
    live_source_access_allowed: bool
    devhub_access_allowed: bool
    private_file_access_allowed: bool
    inactive_process_model_gate_recommendations: tuple[Mapping[str, Any], ...]
    inactive_guardrail_gate_recommendations: tuple[Mapping[str, Any], ...]
    agent_readiness_replay: Mapping[str, Any]
    devhub_observation_delta_holds: tuple[Mapping[str, Any], ...]
    public_refresh_impact_summary: Mapping[str, Any]
    reviewer_dispositions: tuple[Mapping[str, Any], ...]
    rollback_notes: tuple[str, ...]
    offline_validation_commands: tuple[tuple[str, ...], ...]
    decision: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_version": self.packet_version,
            "scenario": self.scenario,
            "release_state_changed": self.release_state_changed,
            "artifact_promotion_allowed": self.artifact_promotion_allowed,
            "live_source_access_allowed": self.live_source_access_allowed,
            "devhub_access_allowed": self.devhub_access_allowed,
            "private_file_access_allowed": self.private_file_access_allowed,
            "inactive_process_model_gate_recommendations": [dict(item) for item in self.inactive_process_model_gate_recommendations],
            "inactive_guardrail_gate_recommendations": [dict(item) for item in self.inactive_guardrail_gate_recommendations],
            "agent_readiness_replay": deepcopy(dict(self.agent_readiness_replay)),
            "devhub_observation_delta_holds": [dict(item) for item in self.devhub_observation_delta_holds],
            "public_refresh_impact_summary": deepcopy(dict(self.public_refresh_impact_summary)),
            "reviewer_dispositions": [dict(item) for item in self.reviewer_dispositions],
            "rollback_notes": list(self.rollback_notes),
            "offline_validation_commands": [list(command) for command in self.offline_validation_commands],
            "decision": deepcopy(dict(self.decision)),
        }


def build_release_readiness_decision_packet_v3(scenario: str) -> dict[str, Any]:
    """Build a deterministic synthetic release readiness decision packet."""
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported synthetic scenario: {scenario}")

    held = scenario == "release-held"
    rejected = scenario == "release-rejected"
    ready = scenario == "release-ready"

    packet = DecisionPacket(
        packet_version="release-readiness-decision-packet-v3",
        scenario=scenario,
        release_state_changed=False,
        artifact_promotion_allowed=False,
        live_source_access_allowed=False,
        devhub_access_allowed=False,
        private_file_access_allowed=False,
        inactive_process_model_gate_recommendations=(
            {
                "gate": "process-model-coverage",
                "mode": "inactive-recommendation-only",
                "recommendation": "pass" if ready else "hold" if held else "reject",
                "reason": "synthetic replay evidence only; no active process-model mutation",
            },
            {
                "gate": "process-model-drift",
                "mode": "inactive-recommendation-only",
                "recommendation": "pass" if ready else "hold" if held else "reject",
                "reason": "fixture delta reviewed without changing requirements or contracts",
            },
        ),
        inactive_guardrail_gate_recommendations=(
            {
                "gate": "automation-safety",
                "mode": "inactive-recommendation-only",
                "recommendation": "pass" if ready else "hold" if held else "reject",
                "reason": "no CAPTCHA, MFA, upload, payment, scheduling, submission, or certification automation",
            },
            {
                "gate": "source-access",
                "mode": "inactive-recommendation-only",
                "recommendation": "pass",
                "reason": "packet is fixture-first and does not crawl live sources or open DevHub",
            },
        ),
        agent_readiness_replay={
            "source": "synthetic-fixture",
            "replayed_at": "2026-05-31T00:00:00Z",
            "result": "passed" if ready else "needs-review" if held else "failed",
            "release_state_mutation": False,
            "active_prompt_mutation": False,
        },
        devhub_observation_delta_holds=(
            {
                "surface": "DevHub permit observation",
                "delta": "none" if ready else "unverified fixture delta" if held else "conflicting fixture delta",
                "hold_required": not ready,
                "reason": "DevHub was not opened; disposition is synthetic and offline",
            },
        ),
        public_refresh_impact_summary={
            "source": "synthetic public refresh fixture",
            "crawl_performed": False,
            "impact": "no public refresh blocker" if ready else "public refresh requires reviewer hold" if held else "public refresh indicates release rejection",
            "artifact_promotion": False,
        },
        reviewer_dispositions=(
            {
                "reviewer": "release-captain",
                "disposition": "approve" if ready else "hold" if held else "reject",
                "notes": "synthetic disposition only; no forms, uploads, submissions, or certifications drafted",
            },
            {
                "reviewer": "automation-guardrail",
                "disposition": "approve" if ready else "hold" if held else "reject",
                "notes": "offline evidence packet preserves active guardrail and daemon state",
            },
        ),
        rollback_notes=(
            "No release state was changed by this packet.",
            "No artifacts were promoted; rollback is limited to discarding this synthetic packet.",
            "No DevHub session, private file, trace, crawl output, or downloaded document was created.",
        ),
        offline_validation_commands=OFFLINE_VALIDATION_COMMANDS,
        decision={
            "status": "ready" if ready else "held" if held else "rejected",
            "release_allowed": ready,
            "hold_required": held,
            "rejection_required": rejected,
            "basis": "synthetic offline fixture decision packet v3",
        },
    )
    return packet.to_dict()


def build_all_release_readiness_decision_packets_v3() -> dict[str, dict[str, Any]]:
    return {scenario: build_release_readiness_decision_packet_v3(scenario) for scenario in sorted(SCENARIOS)}
