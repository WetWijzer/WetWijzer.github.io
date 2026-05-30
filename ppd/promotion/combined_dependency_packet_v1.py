"""Fixture-first combined promotion dependency packet v1.

This module intentionally works from committed fixtures and plain dictionaries. It does
not crawl, authenticate, inspect DevHub, download documents, or mutate official state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

REQUIRED_INPUT_PACKETS = (
    "public_source_refresh_patch_plan_v1",
    "devhub_read_only_observation_promotion_plan_v1",
    "reviewer_disposition_ledger_v1",
    "supervised_offline_release_rehearsal_v1",
)

REQUIRED_ATTESTATIONS = (
    "no_live_crawl",
    "no_devhub_session",
    "no_private_artifact",
    "no_official_action",
    "no_active_mutation",
)


@dataclass(frozen=True)
class PacketError(Exception):
    """Raised when fixture input cannot produce a promotion packet."""

    message: str

    def __str__(self) -> str:
        return self.message


def build_combined_promotion_dependency_packet_v1(inputs: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic combined promotion dependency packet from fixtures."""

    packets = _require_mapping(inputs, "packets")
    missing_packets = [packet_id for packet_id in REQUIRED_INPUT_PACKETS if packet_id not in packets]
    if missing_packets:
        raise PacketError(f"missing required input packets: {', '.join(missing_packets)}")

    public_plan = _require_mapping(packets, "public_source_refresh_patch_plan_v1")
    devhub_plan = _require_mapping(packets, "devhub_read_only_observation_promotion_plan_v1")
    reviewer_ledger = _require_mapping(packets, "reviewer_disposition_ledger_v1")
    rehearsal = _require_mapping(packets, "supervised_offline_release_rehearsal_v1")

    attestations = _merge_attestations(public_plan, devhub_plan, reviewer_ledger, rehearsal)
    failed_attestations = [name for name in REQUIRED_ATTESTATIONS if attestations.get(name) is not True]
    if failed_attestations:
        raise PacketError(f"required attestations are not true: {', '.join(failed_attestations)}")

    reviewer_owners = _reviewer_owners(reviewer_ledger)
    prerequisites = _ordered_prerequisites(public_plan, devhub_plan, reviewer_ledger, rehearsal, reviewer_owners)

    return {
        "packet_id": "combined_promotion_dependency_packet_v1",
        "schema_version": "1.0",
        "mode": "fixture_first_offline_promotion",
        "consumes": list(REQUIRED_INPUT_PACKETS),
        "ordered_promotion_prerequisites": prerequisites,
        "reviewer_owners": reviewer_owners,
        "affected_fixture_families": _sorted_unique(
            _list(public_plan, "affected_fixture_families")
            + _list(devhub_plan, "affected_fixture_families")
            + _list(rehearsal, "affected_fixture_families")
        ),
        "rollback_checkpoints": _rollback_checkpoints(public_plan, devhub_plan, rehearsal),
        "offline_validation_commands": _offline_validation_commands(public_plan, devhub_plan, rehearsal),
        "attestations": {name: attestations[name] for name in REQUIRED_ATTESTATIONS},
        "promotion_blockers": _promotion_blockers(reviewer_ledger, rehearsal),
    }


def _ordered_prerequisites(
    public_plan: dict[str, Any],
    devhub_plan: dict[str, Any],
    reviewer_ledger: dict[str, Any],
    rehearsal: dict[str, Any],
    reviewer_owners: dict[str, str],
) -> list[dict[str, Any]]:
    prerequisite_specs = (
        (10, "public_source_refresh_patch_plan_accepted", public_plan, "public_source_refresh", "public_refresh"),
        (20, "devhub_read_only_observation_plan_accepted", devhub_plan, "devhub_read_only_observation", "devhub_observation"),
        (30, "reviewer_disposition_ledger_accepted", reviewer_ledger, "reviewer_disposition", "reviewer_disposition"),
        (40, "supervised_offline_release_rehearsal_passed", rehearsal, "offline_release_rehearsal", "offline_rehearsal"),
    )
    prerequisites: list[dict[str, Any]] = []
    for sequence, prerequisite_id, source, owner_key, fallback_owner in prerequisite_specs:
        prerequisites.append(
            {
                "sequence": sequence,
                "prerequisite_id": prerequisite_id,
                "source_packet_id": str(source.get("packet_id", "")),
                "source_evidence_ids": _list(source, "source_evidence_ids"),
                "reviewer_owner": reviewer_owners.get(owner_key, fallback_owner),
                "required_disposition": str(source.get("promotion_disposition", "accepted")),
                "fixture_families": _list(source, "affected_fixture_families"),
                "offline_only": True,
            }
        )
    return prerequisites


def _reviewer_owners(reviewer_ledger: dict[str, Any]) -> dict[str, str]:
    owners = _require_mapping(reviewer_ledger, "reviewer_owners")
    required_owner_keys = (
        "public_source_refresh",
        "devhub_read_only_observation",
        "reviewer_disposition",
        "offline_release_rehearsal",
    )
    missing = [key for key in required_owner_keys if not str(owners.get(key, "")).strip()]
    if missing:
        raise PacketError(f"missing reviewer owners: {', '.join(missing)}")
    return {key: str(owners[key]) for key in required_owner_keys}


def _rollback_checkpoints(*sources: dict[str, Any]) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in sources:
        for checkpoint in _list(source, "rollback_checkpoints"):
            if not isinstance(checkpoint, dict):
                raise PacketError("rollback checkpoints must be objects")
            checkpoint_id = str(checkpoint.get("checkpoint_id", "")).strip()
            if not checkpoint_id:
                raise PacketError("rollback checkpoint is missing checkpoint_id")
            if checkpoint_id in seen:
                continue
            seen.add(checkpoint_id)
            checkpoints.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "description": str(checkpoint.get("description", "")),
                    "restore_fixture_family": str(checkpoint.get("restore_fixture_family", "")),
                    "source_packet_id": str(source.get("packet_id", "")),
                }
            )
    return checkpoints


def _offline_validation_commands(*sources: dict[str, Any]) -> list[list[str]]:
    commands: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for source in sources:
        for command in _list(source, "offline_validation_commands"):
            if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
                raise PacketError("offline validation commands must be non-empty string lists")
            command_key = tuple(command)
            if command_key in seen:
                continue
            seen.add(command_key)
            commands.append(command)
    return commands


def _merge_attestations(*sources: dict[str, Any]) -> dict[str, bool]:
    merged = {name: True for name in REQUIRED_ATTESTATIONS}
    for source in sources:
        source_attestations = _require_mapping(source, "attestations")
        for name in REQUIRED_ATTESTATIONS:
            merged[name] = merged[name] and source_attestations.get(name) is True
    return merged


def _promotion_blockers(reviewer_ledger: dict[str, Any], rehearsal: dict[str, Any]) -> list[str]:
    blockers = _list(reviewer_ledger, "promotion_blockers") + _list(rehearsal, "promotion_blockers")
    return [str(blocker) for blocker in blockers]


def _require_mapping(mapping: dict[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key)
    if not isinstance(value, dict):
        raise PacketError(f"{key} must be an object")
    return value


def _list(mapping: dict[str, Any], key: str) -> list[Any]:
    value = mapping.get(key, [])
    if not isinstance(value, list):
        raise PacketError(f"{key} must be a list")
    return value


def _sorted_unique(values: Iterable[Any]) -> list[str]:
    return sorted({str(value) for value in values})
