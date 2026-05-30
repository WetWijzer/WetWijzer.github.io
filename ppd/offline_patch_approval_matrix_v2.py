"""Fixture-first offline patch migration approval matrix v2.

This module intentionally accepts committed fixture data and produces a deterministic
review matrix. It does not crawl, authenticate, mutate registries, or change active
guardrails.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

REQUIRED_ATTESTATIONS = (
    "no_live_access",
    "no_auth_access",
    "no_official_action",
    "no_active_registry_mutation",
    "no_active_guardrail_mutation",
)

REQUIRED_OFFLINE_COMMANDS = (
    ["python3", "-m", "py_compile", "ppd/offline_patch_approval_matrix_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_offline_patch_approval_matrix_v2.py"],
)

SOURCE_KIND = "source"
DEVHUB_SURFACE_KIND = "devhub_surface"
GUARDRAIL_PREVIEW_KIND = "guardrail_preview"


@dataclass(frozen=True)
class MatrixRow:
    """One cited approval decision for a packet item."""

    row_id: str
    row_kind: str
    source_packet: str
    item_id: str
    title: str
    citation_ids: tuple[str, ...]
    decision: str
    decision_reason: str
    reviewer_owner: str
    dependency_order: int
    depends_on: tuple[str, ...]
    rollback_verification_notes: tuple[str, ...]
    required_offline_validation_commands: tuple[tuple[str, ...], ...]
    attestations: Mapping[str, bool]

    def as_dict(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "row_kind": self.row_kind,
            "source_packet": self.source_packet,
            "item_id": self.item_id,
            "title": self.title,
            "citation_ids": list(self.citation_ids),
            "decision": self.decision,
            "decision_reason": self.decision_reason,
            "reviewer_owner": self.reviewer_owner,
            "dependency_order": self.dependency_order,
            "depends_on": list(self.depends_on),
            "rollback_verification_notes": list(self.rollback_verification_notes),
            "required_offline_validation_commands": [
                list(command) for command in self.required_offline_validation_commands
            ],
            "attestations": dict(self.attestations),
        }


def build_approval_matrix_v2(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic approval matrix from combined offline packets.

    The packet must contain an ``offline_patch_rehearsal_packet_v2`` object and an
    ``offline_release_gate_readiness_packet_v2`` object. Each contributes sources,
    DevHub surfaces, and guardrail previews. Rows are sorted by dependency order
    and stable identifiers.
    """

    rehearsal = _required_mapping(packet, "offline_patch_rehearsal_packet_v2")
    readiness = _required_mapping(packet, "offline_release_gate_readiness_packet_v2")
    packet_attestations = _merge_attestations(rehearsal, readiness)

    rows: list[MatrixRow] = []
    rows.extend(_rows_for_packet("offline_patch_rehearsal_packet_v2", rehearsal, packet_attestations))
    rows.extend(_rows_for_packet("offline_release_gate_readiness_packet_v2", readiness, packet_attestations))
    rows.sort(key=lambda row: (row.dependency_order, row.row_kind, row.row_id))

    return {
        "matrix_id": _string(packet, "matrix_id", "offline_patch_migration_approval_matrix_v2"),
        "schema_version": "2",
        "source_packets": [
            _string(rehearsal, "packet_id", "offline_patch_rehearsal_packet_v2"),
            _string(readiness, "packet_id", "offline_release_gate_readiness_packet_v2"),
        ],
        "required_attestations": list(REQUIRED_ATTESTATIONS),
        "required_offline_validation_commands": [list(command) for command in REQUIRED_OFFLINE_COMMANDS],
        "rows": [row.as_dict() for row in rows],
    }


def _rows_for_packet(
    packet_name: str,
    packet: Mapping[str, Any],
    packet_attestations: Mapping[str, bool],
) -> Iterable[MatrixRow]:
    packet_id = _string(packet, "packet_id", packet_name)
    reviewer_defaults = _required_mapping(packet, "reviewer_owners")
    rollback_defaults = _string_list(packet, "rollback_verification_notes")

    for collection_key, row_kind in (
        ("sources", SOURCE_KIND),
        ("devhub_surfaces", DEVHUB_SURFACE_KIND),
        ("guardrail_previews", GUARDRAIL_PREVIEW_KIND),
    ):
        for item in _mapping_list(packet, collection_key):
            item_id = _required_string(item, "id")
            decision = _decision_for(item)
            owner = _string(item, "reviewer_owner", _required_string(reviewer_defaults, row_kind))
            rollback_notes = _string_list(item, "rollback_verification_notes") or rollback_defaults
            yield MatrixRow(
                row_id=f"{packet_id}:{row_kind}:{item_id}",
                row_kind=row_kind,
                source_packet=packet_id,
                item_id=item_id,
                title=_required_string(item, "title"),
                citation_ids=tuple(_string_list(item, "citation_ids")),
                decision=decision,
                decision_reason=_decision_reason(item, decision),
                reviewer_owner=owner,
                dependency_order=_int(item, "dependency_order", 100),
                depends_on=tuple(_string_list(item, "depends_on")),
                rollback_verification_notes=tuple(rollback_notes),
                required_offline_validation_commands=tuple(
                    tuple(command) for command in _commands_for(item)
                ),
                attestations=dict(packet_attestations),
            )


def _decision_for(item: Mapping[str, Any]) -> str:
    if bool(item.get("reject")):
        return "reject"
    if bool(item.get("defer")):
        return "defer"
    if not _string_list(item, "citation_ids"):
        return "reject"
    if _string_list(item, "blocking_findings"):
        return "reject"
    if _string_list(item, "open_questions"):
        return "defer"
    return "approve"


def _decision_reason(item: Mapping[str, Any], decision: str) -> str:
    explicit = _string(item, "decision_reason", "")
    if explicit:
        return explicit
    if decision == "approve":
        return "Cited fixture evidence is present and no offline blocking findings remain."
    if decision == "defer":
        return "Offline review is incomplete because open questions remain."
    return "Offline review failed because cited evidence is missing or blocking findings remain."


def _commands_for(item: Mapping[str, Any]) -> list[list[str]]:
    commands = item.get("required_offline_validation_commands")
    if commands is None:
        return [list(command) for command in REQUIRED_OFFLINE_COMMANDS]
    if not isinstance(commands, list):
        raise TypeError("required_offline_validation_commands must be a list")
    normalized: list[list[str]] = []
    for command in commands:
        if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
            raise TypeError("each validation command must be a list of strings")
        normalized.append(list(command))
    return normalized


def _merge_attestations(*packets: Mapping[str, Any]) -> dict[str, bool]:
    merged: dict[str, bool] = {}
    for name in REQUIRED_ATTESTATIONS:
        merged[name] = all(bool(_required_mapping(packet, "attestations").get(name)) for packet in packets)
    return merged


def _required_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    found = value.get(key)
    if not isinstance(found, Mapping):
        raise TypeError(f"{key} must be an object")
    return found


def _mapping_list(value: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    found = value.get(key, [])
    if not isinstance(found, list):
        raise TypeError(f"{key} must be a list")
    for item in found:
        if not isinstance(item, Mapping):
            raise TypeError(f"{key} entries must be objects")
    return found


def _string_list(value: Mapping[str, Any], key: str) -> list[str]:
    found = value.get(key, [])
    if found is None:
        return []
    if not isinstance(found, list) or not all(isinstance(item, str) for item in found):
        raise TypeError(f"{key} must be a list of strings")
    return list(found)


def _required_string(value: Mapping[str, Any], key: str) -> str:
    found = value.get(key)
    if not isinstance(found, str) or not found:
        raise TypeError(f"{key} must be a non-empty string")
    return found


def _string(value: Mapping[str, Any], key: str, default: str) -> str:
    found = value.get(key, default)
    if not isinstance(found, str):
        raise TypeError(f"{key} must be a string")
    return found


def _int(value: Mapping[str, Any], key: str, default: int) -> int:
    found = value.get(key, default)
    if not isinstance(found, int):
        raise TypeError(f"{key} must be an integer")
    return found
