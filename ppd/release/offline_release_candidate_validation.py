"""Fixture-first offline release candidate validation checklist assembly.

This module intentionally consumes already-assembled offline packets. It does
not crawl live sources, open DevHub, mutate guardrails, prompt users, or write
release state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

REQUIRED_ATTESTATIONS = (
    "no_live_crawl",
    "no_devhub",
    "no_prompt",
    "no_guardrail_mutation",
    "no_release_mutation",
)


@dataclass(frozen=True)
class ReleaseGate:
    """One ordered release candidate decision gate."""

    gate_id: str
    order: int
    title: str
    decision: str
    owner: str
    reviewer: str
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    blocker_dispositions: tuple[dict[str, str], ...] = field(default_factory=tuple)
    rollback_drill_refs: tuple[str, ...] = field(default_factory=tuple)
    attestations: dict[str, bool] = field(default_factory=dict)
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def go(self) -> bool:
        return self.decision == "go"

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "order": self.order,
            "title": self.title,
            "decision": self.decision,
            "owner": self.owner,
            "reviewer": self.reviewer,
            "evidence_refs": list(self.evidence_refs),
            "blocker_dispositions": list(self.blocker_dispositions),
            "rollback_drill_refs": list(self.rollback_drill_refs),
            "attestations": dict(self.attestations),
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class OfflineReleaseCandidateChecklist:
    """Complete offline release candidate checklist packet."""

    checklist_id: str
    release_candidate_id: str
    source_packet_ids: tuple[str, str, str]
    final_decision: str
    gates: tuple[ReleaseGate, ...]
    residual_blocker_dispositions: tuple[dict[str, str], ...]
    rollback_drill_refs: tuple[str, ...]
    reviewer_owner_fields: dict[str, str]
    attestations: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {
            "checklist_id": self.checklist_id,
            "release_candidate_id": self.release_candidate_id,
            "source_packet_ids": list(self.source_packet_ids),
            "final_decision": self.final_decision,
            "gates": [gate.to_dict() for gate in self.gates],
            "residual_blocker_dispositions": list(self.residual_blocker_dispositions),
            "rollback_drill_refs": list(self.rollback_drill_refs),
            "reviewer_owner_fields": dict(self.reviewer_owner_fields),
            "attestations": dict(self.attestations),
        }


def load_json_packet(path: Path) -> dict[str, Any]:
    """Load a deterministic fixture packet."""

    with path.open("r", encoding="utf-8") as packet_file:
        packet = json.load(packet_file)
    if not isinstance(packet, dict):
        raise ValueError(f"packet must be a JSON object: {path}")
    return packet


def build_offline_release_candidate_checklist(
    assembly_packet: dict[str, Any],
    acceptance_review_packet: dict[str, Any],
    rollback_drill_packet: dict[str, Any],
) -> OfflineReleaseCandidateChecklist:
    """Build ordered offline go/no-go gates from release candidate packets."""

    release_candidate_id = _required_text(assembly_packet, "release_candidate_id")
    reviewer_owner_fields = _reviewer_owner_fields(
        assembly_packet,
        acceptance_review_packet,
        rollback_drill_packet,
    )
    attestations = _combined_attestations(
        assembly_packet,
        acceptance_review_packet,
        rollback_drill_packet,
    )
    residual_blockers = _residual_blocker_dispositions(acceptance_review_packet)
    rollback_refs = tuple(_as_text_list(rollback_drill_packet.get("rollback_drill_refs", ())))

    gates = (
        ReleaseGate(
            gate_id="gate-01-fixture-source-integrity",
            order=1,
            title="Fixture source integrity",
            decision=_decision(all(attestations.values())),
            owner=reviewer_owner_fields["release_owner"],
            reviewer=reviewer_owner_fields["validation_reviewer"],
            evidence_refs=tuple(_as_text_list(assembly_packet.get("fixture_refs", ()))),
            attestations=attestations,
            notes=("Consumes committed fixture packets only.",),
        ),
        ReleaseGate(
            gate_id="gate-02-offline-assembly-packet",
            order=2,
            title="Offline release candidate assembly packet",
            decision=_decision(assembly_packet.get("assembly_status") == "assembled"),
            owner=reviewer_owner_fields["release_owner"],
            reviewer=reviewer_owner_fields["assembly_reviewer"],
            evidence_refs=tuple(_as_text_list(assembly_packet.get("evidence_refs", ()))),
            notes=tuple(_as_text_list(assembly_packet.get("notes", ()))),
        ),
        ReleaseGate(
            gate_id="gate-03-release-acceptance-review",
            order=3,
            title="Release acceptance review packet",
            decision=_decision(acceptance_review_packet.get("acceptance_decision") == "accepted"),
            owner=reviewer_owner_fields["release_owner"],
            reviewer=reviewer_owner_fields["acceptance_reviewer"],
            evidence_refs=tuple(_as_text_list(acceptance_review_packet.get("evidence_refs", ()))),
            blocker_dispositions=residual_blockers,
        ),
        ReleaseGate(
            gate_id="gate-04-rollback-drill-outcome",
            order=4,
            title="Rollback drill outcome review packet",
            decision=_decision(rollback_drill_packet.get("drill_outcome") == "passed"),
            owner=reviewer_owner_fields["rollback_owner"],
            reviewer=reviewer_owner_fields["rollback_reviewer"],
            evidence_refs=tuple(_as_text_list(rollback_drill_packet.get("evidence_refs", ()))),
            rollback_drill_refs=rollback_refs,
        ),
        ReleaseGate(
            gate_id="gate-05-residual-blocker-disposition",
            order=5,
            title="Residual blocker dispositions",
            decision=_decision(_all_residual_blockers_disposed(residual_blockers)),
            owner=reviewer_owner_fields["release_owner"],
            reviewer=reviewer_owner_fields["validation_reviewer"],
            blocker_dispositions=residual_blockers,
        ),
        ReleaseGate(
            gate_id="gate-06-reviewer-owner-fields",
            order=6,
            title="Reviewer and owner fields",
            decision=_decision(all(reviewer_owner_fields.values())),
            owner=reviewer_owner_fields["release_owner"],
            reviewer=reviewer_owner_fields["validation_reviewer"],
            notes=tuple(f"{key}: {value}" for key, value in sorted(reviewer_owner_fields.items())),
        ),
        ReleaseGate(
            gate_id="gate-07-offline-boundary-attestations",
            order=7,
            title="Offline boundary attestations",
            decision=_decision(all(attestations.values())),
            owner=reviewer_owner_fields["release_owner"],
            reviewer=reviewer_owner_fields["validation_reviewer"],
            attestations=attestations,
        ),
    )

    final_decision = _decision(all(gate.go for gate in gates))
    return OfflineReleaseCandidateChecklist(
        checklist_id=f"offline-rc-validation-{release_candidate_id}",
        release_candidate_id=release_candidate_id,
        source_packet_ids=(
            _required_text(assembly_packet, "packet_id"),
            _required_text(acceptance_review_packet, "packet_id"),
            _required_text(rollback_drill_packet, "packet_id"),
        ),
        final_decision=final_decision,
        gates=gates,
        residual_blocker_dispositions=residual_blockers,
        rollback_drill_refs=rollback_refs,
        reviewer_owner_fields=reviewer_owner_fields,
        attestations=attestations,
    )


def _decision(condition: bool) -> str:
    return "go" if condition else "no-go"


def _required_text(packet: dict[str, Any], key: str) -> str:
    value = packet.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"packet field must be non-empty text: {key}")
    return value


def _as_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) and not isinstance(value, tuple):
        raise ValueError("expected a list of text values")
    text_values: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("expected a list of non-empty text values")
        text_values.append(item)
    return text_values


def _reviewer_owner_fields(
    assembly_packet: dict[str, Any],
    acceptance_review_packet: dict[str, Any],
    rollback_drill_packet: dict[str, Any],
) -> dict[str, str]:
    return {
        "release_owner": _required_text(assembly_packet, "release_owner"),
        "assembly_reviewer": _required_text(assembly_packet, "assembly_reviewer"),
        "acceptance_reviewer": _required_text(acceptance_review_packet, "acceptance_reviewer"),
        "rollback_owner": _required_text(rollback_drill_packet, "rollback_owner"),
        "rollback_reviewer": _required_text(rollback_drill_packet, "rollback_reviewer"),
        "validation_reviewer": _required_text(acceptance_review_packet, "validation_reviewer"),
    }


def _combined_attestations(*packets: dict[str, Any]) -> dict[str, bool]:
    combined = {attestation: True for attestation in REQUIRED_ATTESTATIONS}
    for packet in packets:
        packet_attestations = packet.get("attestations", {})
        if not isinstance(packet_attestations, dict):
            raise ValueError("attestations must be an object")
        for attestation in REQUIRED_ATTESTATIONS:
            combined[attestation] = combined[attestation] and packet_attestations.get(attestation) is True
    return combined


def _residual_blocker_dispositions(packet: dict[str, Any]) -> tuple[dict[str, str], ...]:
    dispositions = packet.get("residual_blocker_dispositions", [])
    if not isinstance(dispositions, list):
        raise ValueError("residual_blocker_dispositions must be a list")

    normalized: list[dict[str, str]] = []
    for disposition in dispositions:
        if not isinstance(disposition, dict):
            raise ValueError("each residual blocker disposition must be an object")
        normalized.append(
            {
                "blocker_id": _required_text(disposition, "blocker_id"),
                "severity": _required_text(disposition, "severity"),
                "disposition": _required_text(disposition, "disposition"),
                "owner": _required_text(disposition, "owner"),
                "reviewer": _required_text(disposition, "reviewer"),
            }
        )
    return tuple(normalized)


def _all_residual_blockers_disposed(dispositions: tuple[dict[str, str], ...]) -> bool:
    allowed = {"accepted-risk", "deferred", "resolved", "not-applicable"}
    return all(disposition["disposition"] in allowed for disposition in dispositions)
