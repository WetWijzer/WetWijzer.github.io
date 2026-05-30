"""Fixture-first rollback activation decision packet compiler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence


REQUIRED_INPUTS = (
    "post_release_monitoring_readiness_packet",
    "release_rollback_drill_outcome_review_packet",
    "release_blocker_closure_review_packet",
)

ATTESTATION_KEYS = (
    "no_live_crawl",
    "no_devhub",
    "no_prompt",
    "no_guardrail_change",
    "no_release_state_mutation",
)

OFFLINE_VALIDATION_COMMANDS = (
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ["python3", "-m", "pytest", "ppd/tests/test_rollback_activation_decision.py"],
)


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, packet: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(packet, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _citation(source_id: str, field: str, value: Any) -> Dict[str, Any]:
    return {"source_packet": source_id, "field": field, "observed_value": value}


def _source_id(packet: Mapping[str, Any], fallback: str) -> str:
    value = packet.get("packet_id") or packet.get("id") or fallback
    return str(value)


def _collect_acknowledgements(inputs: Mapping[str, Mapping[str, Any]]) -> List[Dict[str, str]]:
    acknowledgements: List[Dict[str, str]] = []
    seen = set()
    for fallback, packet in inputs.items():
        source_id = _source_id(packet, fallback)
        for item in _as_list(packet.get("owner_acknowledgements")):
            if not isinstance(item, Mapping):
                continue
            owner = str(item.get("owner", "")).strip()
            status = str(item.get("status", "")).strip()
            if not owner or not status:
                continue
            key = (owner, status, source_id)
            if key in seen:
                continue
            seen.add(key)
            acknowledgements.append({"owner": owner, "status": status, "source_packet": source_id})
    return acknowledgements


def _evaluate_triggers(inputs: Mapping[str, Mapping[str, Any]]) -> List[Dict[str, Any]]:
    monitoring = inputs["post_release_monitoring_readiness_packet"]
    drill = inputs["release_rollback_drill_outcome_review_packet"]
    blockers = inputs["release_blocker_closure_review_packet"]

    monitoring_id = _source_id(monitoring, "post_release_monitoring_readiness_packet")
    drill_id = _source_id(drill, "release_rollback_drill_outcome_review_packet")
    blockers_id = _source_id(blockers, "release_blocker_closure_review_packet")

    checks = _as_list(monitoring.get("readiness_checks"))
    failed_checks = [item for item in checks if isinstance(item, Mapping) and str(item.get("status", "")).lower() not in {"ready", "pass", "passed"}]
    drill_status = str(drill.get("rollback_drill_status", drill.get("status", "unknown"))).lower()
    blocker_status = str(blockers.get("closure_status", blockers.get("status", "unknown"))).lower()
    open_blockers = _as_list(blockers.get("open_blockers"))

    return [
        {
            "trigger_id": "monitoring-readiness",
            "description": "Post-release monitoring must be ready before rollback activation remains in no-rollback posture.",
            "triggered": bool(failed_checks),
            "severity": "high" if failed_checks else "none",
            "citations": [_citation(monitoring_id, "readiness_checks", checks)],
        },
        {
            "trigger_id": "rollback-drill-outcome",
            "description": "Rollback drill outcome must be passing before release rollback activation is deferred.",
            "triggered": drill_status not in {"passed", "pass", "complete", "completed"},
            "severity": "critical" if drill_status not in {"passed", "pass", "complete", "completed"} else "none",
            "citations": [_citation(drill_id, "rollback_drill_status", drill_status)],
        },
        {
            "trigger_id": "release-blocker-closure",
            "description": "Release blockers must be closed before rollback activation remains inactive.",
            "triggered": blocker_status not in {"closed", "complete", "completed"} or bool(open_blockers),
            "severity": "critical" if blocker_status not in {"closed", "complete", "completed"} or bool(open_blockers) else "none",
            "citations": [
                _citation(blockers_id, "closure_status", blocker_status),
                _citation(blockers_id, "open_blockers", open_blockers),
            ],
        },
    ]


def build_packet(source_packets: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    missing = [name for name in REQUIRED_INPUTS if name not in source_packets]
    if missing:
        raise ValueError("missing source packets: " + ", ".join(missing))

    trigger_evaluations = _evaluate_triggers(source_packets)
    activate = any(item["triggered"] and item["severity"] == "critical" for item in trigger_evaluations)
    acknowledgements = _collect_acknowledgements(source_packets)

    return {
        "packet_id": "rollback-activation-decision-fixture-v1",
        "packet_type": "rollback_activation_decision",
        "fixture_first": True,
        "source_packets": {name: _source_id(source_packets[name], name) for name in REQUIRED_INPUTS},
        "trigger_evaluations": trigger_evaluations,
        "decision": {
            "rollback_activation": "rollback" if activate else "no-rollback",
            "reason": "critical rollback trigger present" if activate else "all cited rollback triggers cleared",
            "release_state_mutated": False,
        },
        "owner_acknowledgements": acknowledgements,
        "reviewer_owner_fields": {
            "reviewer": "ppd-release-reviewer-fixture",
            "owner": "ppd-release-owner-fixture",
            "acknowledgement_count": len(acknowledgements),
        },
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": {key: True for key in ATTESTATION_KEYS},
    }


def validate_packet(packet: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if packet.get("packet_type") != "rollback_activation_decision":
        errors.append("packet_type must be rollback_activation_decision")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if not packet.get("trigger_evaluations"):
        errors.append("trigger_evaluations must not be empty")
    for key in ATTESTATION_KEYS:
        if packet.get("attestations", {}).get(key) is not True:
            errors.append(f"attestation {key} must be true")
    decision = packet.get("decision", {})
    if decision.get("rollback_activation") not in {"rollback", "no-rollback"}:
        errors.append("decision.rollback_activation must be rollback or no-rollback")
    if decision.get("release_state_mutated") is not False:
        errors.append("decision.release_state_mutated must be false")
    return errors


def build_packet_from_fixture(path: Path) -> Dict[str, Any]:
    fixture = load_json(path)
    source_packets = fixture.get("source_packets")
    if not isinstance(source_packets, Mapping):
        raise ValueError("fixture must include source_packets object")
    packet = build_packet(source_packets)  # type: ignore[arg-type]
    errors = validate_packet(packet)
    if errors:
        raise ValueError("invalid rollback activation packet: " + "; ".join(errors))
    return packet
