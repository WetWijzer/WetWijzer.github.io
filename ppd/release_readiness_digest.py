"""Fixture-first inactive release promotion readiness digest v1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ReadinessRow:
    """One ordered readiness summary row for an inactive release item."""

    order: int
    artifact_id: str
    title: str
    readiness: str
    decision: str
    unresolved_holds: tuple[str, ...]
    unresolved_blockers: tuple[str, ...]
    rollback_rehearsal_ref: str
    prerequisite_validation_commands: tuple[str, ...]
    reviewer_handoff_placeholder: str
    no_go_reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "order": self.order,
            "artifact_id": self.artifact_id,
            "title": self.title,
            "readiness": self.readiness,
            "decision": self.decision,
            "unresolved_holds": list(self.unresolved_holds),
            "unresolved_blockers": list(self.unresolved_blockers),
            "rollback_rehearsal_ref": self.rollback_rehearsal_ref,
            "prerequisite_validation_commands": list(self.prerequisite_validation_commands),
            "reviewer_handoff_placeholder": self.reviewer_handoff_placeholder,
            "no_go_reasons": list(self.no_go_reasons),
        }


def _strings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value if str(item))
    return (str(value),)


def _item_key(item: Mapping[str, Any]) -> tuple[int, str]:
    order = item.get("order", item.get("sequence", 999999))
    try:
        normalized_order = int(order)
    except (TypeError, ValueError):
        normalized_order = 999999
    return normalized_order, str(item.get("artifact_id", item.get("id", "")))


def _rollback_refs(packet: Mapping[str, Any]) -> dict[str, str]:
    refs: dict[str, str] = {}
    rehearsals = packet.get("rehearsals", [])
    if not isinstance(rehearsals, list):
        return refs
    for rehearsal in rehearsals:
        if not isinstance(rehearsal, Mapping):
            continue
        artifact_id = str(rehearsal.get("artifact_id", rehearsal.get("id", "")))
        if not artifact_id:
            continue
        refs[artifact_id] = str(rehearsal.get("reference", rehearsal.get("rehearsal_id", "")))
    return refs


def build_inactive_release_readiness_digest(
    decision_packet: Mapping[str, Any], rollback_rehearsal_packet: Mapping[str, Any]
) -> dict[str, Any]:
    """Build a deterministic readiness digest from inactive release fixtures.

    The digest is intentionally descriptive only: it does not promote fixtures,
    mutate release state, crawl live sources, or perform official actions.
    """

    rollback_refs = _rollback_refs(rollback_rehearsal_packet)
    items = decision_packet.get("release_items", [])
    if not isinstance(items, list):
        items = []

    rows: list[ReadinessRow] = []
    for index, item in enumerate(sorted((entry for entry in items if isinstance(entry, Mapping)), key=_item_key), start=1):
        artifact_id = str(item.get("artifact_id", item.get("id", "")))
        holds = _strings(item.get("unresolved_holds", item.get("holds")))
        blockers = _strings(item.get("unresolved_blockers", item.get("blockers")))
        no_go = _strings(item.get("no_go_reasons"))
        readiness = str(item.get("readiness", "ready" if not holds and not blockers and not no_go else "not_ready"))
        rows.append(
            ReadinessRow(
                order=index,
                artifact_id=artifact_id,
                title=str(item.get("title", artifact_id)),
                readiness=readiness,
                decision=str(item.get("decision", "pending_review")),
                unresolved_holds=holds,
                unresolved_blockers=blockers,
                rollback_rehearsal_ref=rollback_refs.get(artifact_id, "pending_rollback_rehearsal_reference"),
                prerequisite_validation_commands=_strings(item.get("prerequisite_validation_commands")),
                reviewer_handoff_placeholder=str(
                    item.get("reviewer_handoff_placeholder", "reviewer_handoff_pending")
                ),
                no_go_reasons=no_go,
            )
        )

    unresolved_holds = sorted({hold for row in rows for hold in row.unresolved_holds})
    unresolved_blockers = sorted({blocker for row in rows for blocker in row.unresolved_blockers})
    no_go_reasons = sorted({reason for row in rows for reason in row.no_go_reasons})

    return {
        "schema_version": "inactive_release_promotion_readiness_digest.v1",
        "source_decision_packet": str(decision_packet.get("packet_id", "inactive_release_decision_packet.v2")),
        "source_rollback_rehearsal_packet": str(
            rollback_rehearsal_packet.get("packet_id", "release_rollback_rehearsal_packet.v1")
        ),
        "promotion_action": "none_fixture_readiness_digest_only",
        "readiness_summary_rows": [row.as_dict() for row in rows],
        "carry_forward": {
            "unresolved_holds": unresolved_holds,
            "unresolved_blockers": unresolved_blockers,
        },
        "rollback_rehearsal_references": {
            row.artifact_id: row.rollback_rehearsal_ref for row in rows
        },
        "prerequisite_validation_command_inventory": sorted(
            {command for row in rows for command in row.prerequisite_validation_commands}
        ),
        "reviewer_handoff_placeholders": {
            row.artifact_id: row.reviewer_handoff_placeholder for row in rows
        },
        "no_go_reasons": no_go_reasons,
    }
