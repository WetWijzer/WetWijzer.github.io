"""Build inactive fixture promotion candidate packet v2 artifacts.

The builder is intentionally fixture-first and side-effect free. It consumes an
inactive rehearsal fixture and emits deterministic rows for human review without
applying fixture changes, editing active artifacts, or contacting live services.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


PACKET_VERSION = "inactive_fixture_promotion_candidate_packet_v2"
CONSUMES_REHEARSAL_VERSION = "combined_inactive_patch_preview_dependency_rehearsal_v1"

OFFLINE_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "-m", "pytest", "ppd/tests/test_inactive_fixture_promotion_candidate_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_REVIEWER_APPROVAL_PLACEHOLDER = {
    "status": "pending_review",
    "reviewer": None,
    "reviewed_at": None,
    "notes": "Fixture promotion candidate only; no active fixture changes are applied by this packet.",
}

_DEFAULT_NO_GO_REASONS = {
    "missing_owner": False,
    "failed_prerequisite_replay": False,
    "active_artifact_edit_required": False,
    "live_source_required": False,
    "devhub_access_required": False,
    "official_action_required": False,
    "undocumented_rollback_plan": False,
}


@dataclass(frozen=True)
class PromotionCandidate:
    """Normalized inactive fixture promotion candidate row."""

    candidate_id: str
    source_rehearsal_id: str
    fixture_family: str
    fixture_path: str
    preview_patch_id: str
    dependency_ids: tuple[str, ...]
    owner: str
    prerequisite_replay_ids: tuple[str, ...]
    rollback_plan_ref: str
    no_go_reasons: dict[str, bool]

    def as_row(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_rehearsal_id": self.source_rehearsal_id,
            "fixture_family": self.fixture_family,
            "fixture_path": self.fixture_path,
            "preview_patch_id": self.preview_patch_id,
            "dependency_ids": list(self.dependency_ids),
            "owner": self.owner,
            "prerequisite_replay_ids": list(self.prerequisite_replay_ids),
            "reviewer_approval": deepcopy(_REVIEWER_APPROVAL_PLACEHOLDER),
            "no_go_reasons": dict(self.no_go_reasons),
            "rollback_plan_ref": self.rollback_plan_ref,
            "promotion_action": "candidate_only_no_apply",
        }


def build_inactive_fixture_promotion_candidate_packet_v2(rehearsal: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic inactive fixture promotion candidate packet.

    The input must be a combined inactive patch preview dependency rehearsal v1
    fixture. The output is stable under input ordering differences because rows,
    ownership assignments, and replay inventory entries are sorted by explicit
    identifiers.
    """

    _validate_rehearsal(rehearsal)

    rehearsal_id = _required_str(rehearsal, "rehearsal_id")
    fixture_families = _fixture_family_owner_map(rehearsal)
    replay_inventory = _build_prerequisite_validation_replay_inventory(rehearsal)
    replay_ids_by_patch = _replay_ids_by_patch(replay_inventory)
    rollback_refs = _rollback_refs(rehearsal)

    candidates: list[PromotionCandidate] = []
    for patch in sorted(rehearsal["preview_patches"], key=lambda item: item["preview_patch_id"]):
        fixture_family = _required_str(patch, "fixture_family")
        preview_patch_id = _required_str(patch, "preview_patch_id")
        fixture_path = _required_str(patch, "fixture_path")
        owner = fixture_families[fixture_family]
        candidate_id = f"promotion-candidate-v2::{fixture_family}::{preview_patch_id}"
        no_go_reasons = _candidate_no_go_reasons(patch, owner, replay_ids_by_patch, rollback_refs)

        candidates.append(
            PromotionCandidate(
                candidate_id=candidate_id,
                source_rehearsal_id=rehearsal_id,
                fixture_family=fixture_family,
                fixture_path=fixture_path,
                preview_patch_id=preview_patch_id,
                dependency_ids=tuple(sorted(patch.get("dependency_ids", ()))),
                owner=owner,
                prerequisite_replay_ids=tuple(replay_ids_by_patch.get(preview_patch_id, ())),
                rollback_plan_ref=rollback_refs.get(preview_patch_id, "rollback-plan::missing"),
                no_go_reasons=no_go_reasons,
            )
        )

    candidate_rows = [candidate.as_row() for candidate in candidates]

    return {
        "packet_version": PACKET_VERSION,
        "consumes_rehearsal_version": CONSUMES_REHEARSAL_VERSION,
        "source_rehearsal_id": rehearsal_id,
        "mode": "fixture_first_inactive_candidate_only",
        "side_effects": {
            "applies_fixture_changes": False,
            "edits_active_artifacts": False,
            "changes_prompts": False,
            "updates_release_state": False,
            "crawls_live_sources": False,
            "accesses_devhub": False,
            "performs_official_actions": False,
        },
        "candidate_rows": candidate_rows,
        "fixture_family_ownership_assignments": _ownership_assignments(candidate_rows),
        "prerequisite_validation_replay_inventory": replay_inventory,
        "reviewer_approval_placeholders": {
            row["candidate_id"]: deepcopy(_REVIEWER_APPROVAL_PLACEHOLDER) for row in candidate_rows
        },
        "no_go_reason_fields": sorted(_DEFAULT_NO_GO_REASONS),
        "rollback_plan_references": _candidate_rollback_plan_references(candidate_rows),
        "offline_validation_commands": [list(command) for command in OFFLINE_VALIDATION_COMMANDS],
    }


def _validate_rehearsal(rehearsal: dict[str, Any]) -> None:
    if rehearsal.get("rehearsal_version") != CONSUMES_REHEARSAL_VERSION:
        raise ValueError(f"expected rehearsal_version {CONSUMES_REHEARSAL_VERSION!r}")
    for key in ("rehearsal_id", "fixture_families", "preview_patches", "prerequisite_validation_replays", "rollback_plans"):
        if key not in rehearsal:
            raise ValueError(f"missing required rehearsal field: {key}")


def _fixture_family_owner_map(rehearsal: dict[str, Any]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for family in rehearsal["fixture_families"]:
        family_id = _required_str(family, "fixture_family")
        owner = _required_str(family, "owner")
        owners[family_id] = owner
    return owners


def _build_prerequisite_validation_replay_inventory(rehearsal: dict[str, Any]) -> list[dict[str, Any]]:
    inventory = []
    for replay in sorted(rehearsal["prerequisite_validation_replays"], key=lambda item: item["replay_id"]):
        inventory.append(
            {
                "replay_id": _required_str(replay, "replay_id"),
                "preview_patch_id": _required_str(replay, "preview_patch_id"),
                "validation_name": _required_str(replay, "validation_name"),
                "status": _required_str(replay, "status"),
                "evidence_fixture_path": _required_str(replay, "evidence_fixture_path"),
                "replay_command": list(replay.get("replay_command", ())),
            }
        )
    return inventory


def _replay_ids_by_patch(replay_inventory: list[dict[str, Any]]) -> dict[str, tuple[str, ...]]:
    grouped: dict[str, list[str]] = {}
    for replay in replay_inventory:
        grouped.setdefault(replay["preview_patch_id"], []).append(replay["replay_id"])
    return {patch_id: tuple(sorted(replay_ids)) for patch_id, replay_ids in grouped.items()}


def _rollback_refs(rehearsal: dict[str, Any]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for rollback_plan in rehearsal["rollback_plans"]:
        refs[_required_str(rollback_plan, "preview_patch_id")] = _required_str(rollback_plan, "rollback_plan_ref")
    return refs


def _candidate_no_go_reasons(
    patch: dict[str, Any],
    owner: str,
    replay_ids_by_patch: dict[str, tuple[str, ...]],
    rollback_refs: dict[str, str],
) -> dict[str, bool]:
    preview_patch_id = _required_str(patch, "preview_patch_id")
    reasons = dict(_DEFAULT_NO_GO_REASONS)
    reasons["missing_owner"] = owner == ""
    reasons["failed_prerequisite_replay"] = preview_patch_id not in replay_ids_by_patch
    reasons["active_artifact_edit_required"] = bool(patch.get("touches_active_artifacts", False))
    reasons["live_source_required"] = bool(patch.get("requires_live_source", False))
    reasons["devhub_access_required"] = bool(patch.get("requires_devhub", False))
    reasons["official_action_required"] = bool(patch.get("requires_official_action", False))
    reasons["undocumented_rollback_plan"] = preview_patch_id not in rollback_refs
    return reasons


def _ownership_assignments(candidate_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen: dict[str, str] = {}
    for row in candidate_rows:
        seen[row["fixture_family"]] = row["owner"]
    return [
        {"fixture_family": fixture_family, "owner": seen[fixture_family]}
        for fixture_family in sorted(seen)
    ]


def _candidate_rollback_plan_references(candidate_rows: list[dict[str, Any]]) -> dict[str, str]:
    return {row["candidate_id"]: row["rollback_plan_ref"] for row in candidate_rows}


def _required_str(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or value == "":
        raise ValueError(f"expected non-empty string field: {key}")
    return value
