"""Fixture-first launch packet compiler for PP&D public source refreshes.

The compiler is intentionally metadata-only. It does not fetch sources, invoke
processors, update registries, or mutate schedules.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


Packet = dict[str, Any]


def load_fixture_packet(path: str | Path) -> Packet:
    """Load a JSON fixture packet from disk."""
    with Path(path).open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError("launch packet fixture must contain a JSON object")
    return loaded


def build_public_source_refresh_launch_packet(inputs: Packet) -> Packet:
    """Build a cited public source refresh launch packet from fixture inputs."""
    readiness = _require_packet(inputs, "public_source_refresh_execution_readiness_packet")
    checklist = _require_packet(inputs, "offline_release_candidate_validation_checklist_packet")
    disposition = _require_packet(inputs, "source_freshness_watchlist_reviewer_disposition_packet")

    source_batches = readiness.get("allowlisted_source_batches", [])
    if not isinstance(source_batches, list) or not source_batches:
        raise ValueError("readiness packet must provide allowlisted_source_batches")

    reviewer_owner = _require_mapping(disposition, "reviewer_owner")
    citations = [_citation(readiness), _citation(checklist), _citation(disposition)]

    allowlisted_batches = []
    for batch in source_batches:
        if not isinstance(batch, dict):
            raise ValueError("allowlisted source batch entries must be objects")
        batch_id = _require_text(batch, "batch_id")
        allowlisted_batches.append(
            {
                "batch_id": batch_id,
                "source_name": _require_text(batch, "source_name"),
                "source_url": _require_text(batch, "source_url"),
                "allowed_scope": list(batch.get("allowed_scope", ["metadata-refresh"])),
                "reviewer_owner": dict(reviewer_owner),
                "citation_refs": [citation["packet_id"] for citation in citations],
            }
        )

    packet = {
        "packet_id": "public-source-refresh-launch-20260529-fixture-first",
        "packet_type": "public_source_refresh_launch_packet",
        "mode": "fixture-first",
        "consumes": citations,
        "operator_launch_gates": [
            {
                "gate_id": "execution-readiness-approved",
                "required_state": "ready",
                "observed_state": _require_text(readiness, "status"),
                "citation_ref": readiness["packet_id"],
            },
            {
                "gate_id": "offline-release-candidate-validated",
                "required_state": "passed",
                "observed_state": _require_text(checklist, "status"),
                "citation_ref": checklist["packet_id"],
            },
            {
                "gate_id": "watchlist-reviewer-disposition-approved",
                "required_state": "approved",
                "observed_state": _require_text(disposition, "disposition"),
                "citation_ref": disposition["packet_id"],
            },
            {
                "gate_id": "metadata-only-attestations-present",
                "required_state": "attested",
                "observed_state": "attested",
                "citation_ref": checklist["packet_id"],
            },
        ],
        "allowlisted_source_batches": allowlisted_batches,
        "abort_triggers": _abort_triggers(readiness, checklist, disposition),
        "expected_metadata_only_result_records": [
            {
                "source_batch_id": batch["batch_id"],
                "result_type": "metadata-only-refresh-record",
                "document_downloaded": False,
                "processor_invoked": False,
                "registry_mutated": False,
                "schedule_mutated": False,
                "required_fields": [
                    "source_batch_id",
                    "source_name",
                    "source_url",
                    "checked_at",
                    "freshness_status",
                    "reviewer_owner",
                    "citation_refs",
                ],
            }
            for batch in allowlisted_batches
        ],
        "reviewer_owner_fields": dict(reviewer_owner),
        "attestations": {
            "no_download": True,
            "no_processor": True,
            "no_registry_mutation": True,
            "no_schedule_mutation": True,
        },
    }
    validate_public_source_refresh_launch_packet(packet)
    return packet


def validate_public_source_refresh_launch_packet(packet: Packet) -> None:
    """Validate the launch packet gates and metadata-only constraints."""
    for gate in packet.get("operator_launch_gates", []):
        if gate.get("observed_state") != gate.get("required_state"):
            raise ValueError(f"launch gate failed: {gate.get('gate_id')}")

    attestations = packet.get("attestations", {})
    for key in ("no_download", "no_processor", "no_registry_mutation", "no_schedule_mutation"):
        if attestations.get(key) is not True:
            raise ValueError(f"missing required attestation: {key}")

    for record in packet.get("expected_metadata_only_result_records", []):
        if record.get("document_downloaded") is not False:
            raise ValueError("metadata-only record cannot allow downloads")
        if record.get("processor_invoked") is not False:
            raise ValueError("metadata-only record cannot invoke processors")
        if record.get("registry_mutated") is not False:
            raise ValueError("metadata-only record cannot mutate registries")
        if record.get("schedule_mutated") is not False:
            raise ValueError("metadata-only record cannot mutate schedules")


def _require_packet(inputs: Packet, key: str) -> Packet:
    packet = inputs.get(key)
    if not isinstance(packet, dict):
        raise ValueError(f"missing packet: {key}")
    _require_text(packet, "packet_id")
    return packet


def _require_mapping(packet: Packet, key: str) -> Packet:
    value = packet.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"missing mapping: {key}")
    return value


def _require_text(packet: Packet, key: str) -> str:
    value = packet.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"missing text field: {key}")
    return value


def _citation(packet: Packet) -> Packet:
    return {
        "packet_id": _require_text(packet, "packet_id"),
        "title": packet.get("title", packet["packet_id"]),
        "fixture_path": packet.get("fixture_path", "ppd/tests/fixtures/public_source_refresh_launch/inputs.json"),
    }


def _abort_triggers(readiness: Packet, checklist: Packet, disposition: Packet) -> list[Packet]:
    triggers = [
        {
            "trigger_id": "gate-state-not-approved",
            "condition": "Any launch gate observed_state differs from required_state.",
            "citation_refs": [readiness["packet_id"], checklist["packet_id"], disposition["packet_id"]],
        },
        {
            "trigger_id": "download-or-processor-requested",
            "condition": "Any run path requests document download or processor invocation.",
            "citation_refs": [checklist["packet_id"]],
        },
        {
            "trigger_id": "registry-or-schedule-mutation-requested",
            "condition": "Any run path requests registry or schedule mutation.",
            "citation_refs": [checklist["packet_id"]],
        },
        {
            "trigger_id": "source-outside-allowlist",
            "condition": "Any source batch is absent from the cited readiness allowlist.",
            "citation_refs": [readiness["packet_id"]],
        },
    ]
    for packet in (readiness, checklist, disposition):
        for trigger in packet.get("abort_triggers", []):
            if isinstance(trigger, dict) and trigger.get("trigger_id"):
                copied = dict(trigger)
                copied.setdefault("citation_refs", [packet["packet_id"]])
                triggers.append(copied)
    return triggers
