"""Fixture-first public source refresh launch rehearsal transcript packets.

This module assembles committed packet metadata into an operator rehearsal
transcript. It does not fetch public sources, download documents, invoke
processors, mutate registries, or mutate schedules.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.public_source_refresh_launch_rehearsal_transcript_packet.v1"
REQUIRED_INPUTS = (
    "public_source_refresh_launch_packet",
    "public_source_refresh_execution_readiness_packet",
    "post_release_monitoring_readiness_packet",
)
REQUIRED_ATTESTATIONS = (
    "no-live-fetch",
    "no-download",
    "no-processor",
    "no-registry-mutation",
    "no-schedule-mutation",
)


@dataclass(frozen=True)
class LaunchRehearsalTranscriptValidationResult:
    ready: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ready": self.ready, "problems": list(self.problems)}


def load_fixture_packet(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError("fixture packet must contain a JSON object")
    return loaded


def build_public_source_refresh_launch_rehearsal_transcript_packet(inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic metadata-only launch rehearsal transcript."""

    launch_packet = _required_mapping(inputs, "public_source_refresh_launch_packet")
    readiness_packet = _required_mapping(inputs, "public_source_refresh_execution_readiness_packet")
    monitoring_packet = _required_mapping(inputs, "post_release_monitoring_readiness_packet")

    launch_id = _packet_id(launch_packet)
    readiness_id = _packet_id(readiness_packet)
    monitoring_id = _packet_id(monitoring_packet)
    reviewer_owner_fields = _reviewer_owner_fields(launch_packet, readiness_packet, monitoring_packet)

    transcript = {
        "packet_type": PACKET_TYPE,
        "packet_id": str(inputs.get("packet_id") or "public-source-refresh-launch-rehearsal-transcript-fixture"),
        "fixture_first": True,
        "consumed_packets": [
            _consumed_packet_ref("public_source_refresh_launch_packet", launch_packet),
            _consumed_packet_ref("public_source_refresh_execution_readiness_packet", readiness_packet),
            _consumed_packet_ref("post_release_monitoring_readiness_packet", monitoring_packet),
        ],
        "operator_rehearsal_steps": _operator_rehearsal_steps(launch_id, readiness_id, monitoring_id, reviewer_owner_fields),
        "observed_preflight_gate_outcomes": _observed_preflight_gate_outcomes(launch_packet, readiness_packet),
        "abort_trigger_checks": _abort_trigger_checks(launch_packet, readiness_packet, monitoring_packet),
        "expected_metadata_only_result_placeholders": _metadata_only_placeholders(launch_packet, readiness_packet),
        "reviewer_owner_fields": reviewer_owner_fields,
        "attestations": {
            "no-live-fetch": True,
            "no-download": True,
            "no-processor": True,
            "no-registry-mutation": True,
            "no-schedule-mutation": True,
        },
        "execution_boundaries": {
            "live_fetch_allowed": False,
            "download_allowed": False,
            "processor_invocation_allowed": False,
            "registry_mutation_allowed": False,
            "schedule_mutation_allowed": False,
        },
    }
    require_public_source_refresh_launch_rehearsal_transcript_packet(transcript)
    return transcript


def validate_public_source_refresh_launch_rehearsal_transcript_packet(packet: Mapping[str, Any]) -> LaunchRehearsalTranscriptValidationResult:
    problems: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")

    consumed = _mapping_sequence(packet.get("consumed_packets"))
    consumed_kinds = {str(item.get("kind") or "") for item in consumed}
    for required in REQUIRED_INPUTS:
        if required not in consumed_kinds:
            problems.append(f"consumed_packets lacks {required}")
    for index, ref in enumerate(consumed):
        if not _text(ref.get("packet_id")):
            problems.append(f"consumed_packets[{index}] lacks packet_id")
        if not _text(ref.get("citation_ref")):
            problems.append(f"consumed_packets[{index}] lacks citation_ref")

    steps = _mapping_sequence(packet.get("operator_rehearsal_steps"))
    if not steps:
        problems.append("operator_rehearsal_steps must be non-empty")
    for index, step in enumerate(steps):
        path = f"operator_rehearsal_steps[{index}]"
        if not _text(step.get("step_id")):
            problems.append(f"{path} lacks step_id")
        if not _text(step.get("operator_action")):
            problems.append(f"{path} lacks operator_action")
        if not _text_list(step.get("citation_refs")):
            problems.append(f"{path} lacks citation_refs")
        if step.get("live_action_allowed") is not False:
            problems.append(f"{path} must keep live_action_allowed false")

    gates = _mapping_sequence(packet.get("observed_preflight_gate_outcomes"))
    if not gates:
        problems.append("observed_preflight_gate_outcomes must be non-empty")
    for index, gate in enumerate(gates):
        path = f"observed_preflight_gate_outcomes[{index}]"
        if not _text(gate.get("gate_id")):
            problems.append(f"{path} lacks gate_id")
        if gate.get("observed_state") != gate.get("required_state"):
            problems.append(f"{path} observed_state must match required_state")
        if gate.get("outcome") != "pass":
            problems.append(f"{path} outcome must be pass")
        if not _text_list(gate.get("citation_refs")):
            problems.append(f"{path} lacks citation_refs")

    abort_checks = _mapping_sequence(packet.get("abort_trigger_checks"))
    if not abort_checks:
        problems.append("abort_trigger_checks must be non-empty")
    for index, check in enumerate(abort_checks):
        path = f"abort_trigger_checks[{index}]"
        if not _text(check.get("trigger_id")):
            problems.append(f"{path} lacks trigger_id")
        if check.get("status") != "armed":
            problems.append(f"{path} status must be armed")
        if check.get("live_action_allowed") is not False:
            problems.append(f"{path} must keep live_action_allowed false")
        if not _text_list(check.get("citation_refs")):
            problems.append(f"{path} lacks citation_refs")

    placeholders = _mapping_sequence(packet.get("expected_metadata_only_result_placeholders"))
    if not placeholders:
        problems.append("expected_metadata_only_result_placeholders must be non-empty")
    for index, placeholder in enumerate(placeholders):
        path = f"expected_metadata_only_result_placeholders[{index}]"
        if not _text(placeholder.get("placeholder_id")):
            problems.append(f"{path} lacks placeholder_id")
        for key in ("live_fetch_performed", "document_downloaded", "processor_invoked", "registry_mutated", "schedule_mutated"):
            if placeholder.get(key) is not False:
                problems.append(f"{path}.{key} must be false")
        if not _text_list(placeholder.get("citation_refs")):
            problems.append(f"{path} lacks citation_refs")

    owners = _mapping(packet.get("reviewer_owner_fields"))
    for key in ("launch_owner", "rehearsal_reviewer", "monitoring_owner"):
        if not _text(owners.get(key)):
            problems.append(f"reviewer_owner_fields lacks {key}")

    attestations = _mapping(packet.get("attestations"))
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            problems.append(f"required attestation must be true: {key}")

    boundaries = _mapping(packet.get("execution_boundaries"))
    for key in ("live_fetch_allowed", "download_allowed", "processor_invocation_allowed", "registry_mutation_allowed", "schedule_mutation_allowed"):
        if boundaries.get(key) is not False:
            problems.append(f"execution boundary must be false: {key}")

    return LaunchRehearsalTranscriptValidationResult(ready=not problems, problems=tuple(problems))


def require_public_source_refresh_launch_rehearsal_transcript_packet(packet: Mapping[str, Any]) -> None:
    result = validate_public_source_refresh_launch_rehearsal_transcript_packet(packet)
    if not result.ready:
        raise ValueError("invalid_public_source_refresh_launch_rehearsal_transcript_packet: " + "; ".join(result.problems))


def _operator_rehearsal_steps(launch_id: str, readiness_id: str, monitoring_id: str, owners: Mapping[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": "load-cited-launch-packet",
            "operator_action": "Load the committed launch packet fixture and confirm its cited launch gates before any live refresh path is considered.",
            "expected_observation": "Launch packet is present and fixture-first.",
            "reviewer_owner": owners["launch_owner"],
            "citation_refs": [launch_id],
            "live_action_allowed": False,
        },
        {
            "step_id": "compare-execution-readiness-gates",
            "operator_action": "Compare readiness preflight outcomes with the launch gates and stop if any observed state differs from the required state.",
            "expected_observation": "Every cited readiness gate remains passing.",
            "reviewer_owner": owners["rehearsal_reviewer"],
            "citation_refs": [launch_id, readiness_id],
            "live_action_allowed": False,
        },
        {
            "step_id": "arm-abort-trigger-checks",
            "operator_action": "Review every cited abort trigger and confirm it is armed before rehearsal proceeds.",
            "expected_observation": "Abort triggers cover gate failure, fetch/download requests, processor requests, registry mutation, and schedule mutation.",
            "reviewer_owner": owners["rehearsal_reviewer"],
            "citation_refs": [launch_id, readiness_id],
            "live_action_allowed": False,
        },
        {
            "step_id": "stage-metadata-only-placeholders",
            "operator_action": "Prepare only placeholder result rows for expected metadata-only results; do not create raw archives or downloaded documents.",
            "expected_observation": "Placeholders contain required metadata fields and false execution flags.",
            "reviewer_owner": owners["launch_owner"],
            "citation_refs": [launch_id, readiness_id],
            "live_action_allowed": False,
        },
        {
            "step_id": "confirm-monitoring-handoff",
            "operator_action": "Confirm post-release monitoring owners and thresholds are ready to review metadata-only outcomes after a separately approved run.",
            "expected_observation": "Monitoring checks and rollback owners are cited and offline.",
            "reviewer_owner": owners["monitoring_owner"],
            "citation_refs": [monitoring_id],
            "live_action_allowed": False,
        },
    ]


def _observed_preflight_gate_outcomes(launch_packet: Mapping[str, Any], readiness_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    outcomes: list[dict[str, Any]] = []
    launch_id = _packet_id(launch_packet)
    readiness_id = _packet_id(readiness_packet)
    for gate in _mapping_sequence(launch_packet.get("operator_launch_gates")):
        required = str(gate.get("required_state") or "")
        observed = str(gate.get("observed_state") or "")
        outcomes.append(
            {
                "gate_id": str(gate.get("gate_id") or "launch-gate"),
                "required_state": required,
                "observed_state": observed,
                "outcome": "pass" if required and required == observed else "fail",
                "citation_refs": _text_list(gate.get("citation_refs")) or _text_list(gate.get("citation_ref")) or [launch_id],
            }
        )
    for gate in _mapping_sequence(readiness_packet.get("preflight_gate_outcomes") or readiness_packet.get("launch_gates")):
        required = str(gate.get("required_state") or gate.get("expected_state") or "passed")
        observed = str(gate.get("observed_state") or gate.get("state") or required)
        outcomes.append(
            {
                "gate_id": str(gate.get("gate_id") or gate.get("id") or "readiness-gate"),
                "required_state": required,
                "observed_state": observed,
                "outcome": "pass" if required and required == observed else "fail",
                "citation_refs": _text_list(gate.get("citation_refs")) or _text_list(gate.get("evidence_refs")) or [readiness_id],
            }
        )
    return outcomes


def _abort_trigger_checks(launch_packet: Mapping[str, Any], readiness_packet: Mapping[str, Any], monitoring_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for packet in (launch_packet, readiness_packet):
        packet_id = _packet_id(packet)
        for trigger in _mapping_sequence(packet.get("abort_triggers")):
            checks.append(
                {
                    "trigger_id": str(trigger.get("trigger_id") or trigger.get("id") or "abort-trigger"),
                    "condition": str(trigger.get("condition") or "Abort if the cited condition is observed."),
                    "status": "armed",
                    "citation_refs": _text_list(trigger.get("citation_refs")) or _text_list(trigger.get("evidence_refs")) or [packet_id],
                    "live_action_allowed": False,
                }
            )
    monitoring_id = _packet_id(monitoring_packet)
    for check in _mapping_sequence(monitoring_packet.get("monitoring_checks")):
        checks.append(
            {
                "trigger_id": "monitoring-threshold-" + str(check.get("check_id") or "check").replace(":", "-"),
                "condition": str(check.get("escalation_note") or "Abort promotion if monitoring threshold review is not owner-assigned."),
                "status": "armed",
                "citation_refs": _text_list(check.get("source_evidence_ids")) or [monitoring_id],
                "live_action_allowed": False,
            }
        )
    return checks


def _metadata_only_placeholders(launch_packet: Mapping[str, Any], readiness_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    placeholders: list[dict[str, Any]] = []
    launch_id = _packet_id(launch_packet)
    readiness_id = _packet_id(readiness_packet)
    records = _mapping_sequence(launch_packet.get("expected_metadata_only_result_records"))
    if not records:
        records = _mapping_sequence(readiness_packet.get("expected_metadata_only_outputs"))
    for index, record in enumerate(records):
        source_batch_id = str(record.get("source_batch_id") or record.get("batch_id") or record.get("source_id") or f"source-batch-{index + 1}")
        placeholders.append(
            {
                "placeholder_id": "metadata-only-result-placeholder-" + source_batch_id,
                "source_batch_id": source_batch_id,
                "result_type": str(record.get("result_type") or "metadata-only-refresh-record"),
                "required_fields": _text_list(record.get("required_fields")) or ["source_batch_id", "checked_at", "freshness_status", "reviewer_owner", "citation_refs"],
                "live_fetch_performed": False,
                "document_downloaded": False,
                "processor_invoked": False,
                "registry_mutated": False,
                "schedule_mutated": False,
                "citation_refs": _text_list(record.get("citation_refs")) or [launch_id, readiness_id],
            }
        )
    return placeholders


def _reviewer_owner_fields(launch_packet: Mapping[str, Any], readiness_packet: Mapping[str, Any], monitoring_packet: Mapping[str, Any]) -> dict[str, str]:
    launch_owner = _mapping(launch_packet.get("reviewer_owner_fields"))
    readiness_owner = _mapping(readiness_packet.get("reviewer_owner_fields"))
    monitoring_owner = _mapping(monitoring_packet.get("reviewer_owner_fields"))
    return {
        "launch_owner": _first_text(launch_owner, ("owner_name", "launch_owner", "release_owner"), "ppd-public-source-refresh-launch-owner"),
        "rehearsal_reviewer": _first_text(readiness_owner, ("rehearsal_reviewer", "validation_reviewer", "owner_name"), "ppd-public-source-refresh-rehearsal-reviewer"),
        "monitoring_owner": _first_text(monitoring_owner, ("monitoring_owner", "validation_reviewer", "release_owner"), "ppd-post-release-monitoring-owner"),
    }


def _consumed_packet_ref(kind: str, packet: Mapping[str, Any]) -> dict[str, str]:
    packet_id = _packet_id(packet)
    return {"kind": kind, "packet_id": packet_id, "citation_ref": packet_id}


def _packet_id(packet: Mapping[str, Any]) -> str:
    for key in ("packet_id", "checklist_id", "packet_type"):
        value = packet.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("consumed packet lacks packet_id")


def _required_mapping(packet: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = packet.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"packet field must be an object: {key}")
    return value


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _text(value: Any) -> str:
    return value if isinstance(value, str) and value else ""


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str) and value:
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, str) and item]
    return []


def _first_text(packet: Mapping[str, Any], keys: Sequence[str], fallback: str) -> str:
    for key in keys:
        value = packet.get(key)
        if isinstance(value, str) and value:
            return value
    return fallback
