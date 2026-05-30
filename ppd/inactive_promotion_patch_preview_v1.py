"""Fixture-first inactive promotion patch preview v1.

This module is intentionally side-effect free. It reads a promotion candidate
patch plan and inactive fixture family inventory, then returns deterministic
review artifacts that can be committed as fixtures or inspected by tests.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


PREVIEW_VERSION = "inactive_promotion_patch_preview_v1"


@dataclass(frozen=True)
class PreviewInput:
    plan_path: Path
    inactive_families_path: Path


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object at {path}")
    return value


def build_preview_from_files(plan_path: Path, inactive_families_path: Path) -> dict[str, Any]:
    return build_preview(load_json(plan_path), load_json(inactive_families_path))


def build_preview(plan: dict[str, Any], inactive_families: dict[str, Any]) -> dict[str, Any]:
    candidates = _as_list(plan.get("promotion_candidates"))
    fixtures_by_id = _index_inactive_fixtures(inactive_families)
    rows = [_build_row(candidate, fixtures_by_id) for candidate in candidates]
    rows = sorted(rows, key=lambda row: (row["candidate_id"], row["inactive_fixture_id"]))

    validation_inventory = _build_validation_inventory(rows, inactive_families)
    blocked_rows = [row for row in rows if row["preview_status"] == "blocked"]

    return {
        "preview_version": PREVIEW_VERSION,
        "source_plan_id": str(plan.get("plan_id", "unknown_plan")),
        "source_fixture_inventory_id": str(inactive_families.get("inventory_id", "unknown_inventory")),
        "preview_rows": rows,
        "validation_inventory": validation_inventory,
        "blocked_row_explanations": [
            {
                "candidate_id": row["candidate_id"],
                "inactive_fixture_id": row["inactive_fixture_id"],
                "reasons": row["blocked_reasons"],
            }
            for row in blocked_rows
        ],
        "reviewer_signoff_placeholders": _build_signoff_placeholders(rows),
        "rollback_checkpoints": _build_rollback_checkpoints(plan, rows),
        "side_effects": {
            "active_fixtures_edited": False,
            "prompts_edited": False,
            "process_models_edited": False,
            "guardrails_edited": False,
            "release_state_edited": False,
            "agent_state_edited": False,
        },
    }


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("expected list")
    return value


def _index_inactive_fixtures(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fixtures_by_id: dict[str, dict[str, Any]] = {}
    for family in _as_list(inventory.get("inactive_fixture_families")):
        if not isinstance(family, dict):
            continue
        family_id = str(family.get("family_id", "unknown_family"))
        for fixture in _as_list(family.get("fixtures")):
            if not isinstance(fixture, dict):
                continue
            fixture_id = str(fixture.get("fixture_id", ""))
            if not fixture_id:
                continue
            enriched = dict(fixture)
            enriched["family_id"] = family_id
            fixtures_by_id[fixture_id] = enriched
    return fixtures_by_id


def _build_row(candidate: Any, fixtures_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        candidate = {}
    candidate_id = str(candidate.get("candidate_id", "unknown_candidate"))
    fixture_id = str(candidate.get("inactive_fixture_id", ""))
    fixture = fixtures_by_id.get(fixture_id)

    blocked_reasons: list[str] = []
    if not fixture_id:
        blocked_reasons.append("candidate_missing_inactive_fixture_id")
    if fixture_id and fixture is None:
        blocked_reasons.append("inactive_fixture_not_found")
    if fixture and fixture.get("active") is True:
        blocked_reasons.append("fixture_is_active")
    for error in _as_list(candidate.get("validation_errors")):
        blocked_reasons.append(f"candidate_validation_error:{error}")
    if not candidate.get("rollback_checkpoint_id"):
        blocked_reasons.append("candidate_missing_rollback_checkpoint")

    before_state = _state_snapshot(fixture, "before")
    after_state = _build_after_state(candidate, fixture)

    return {
        "candidate_id": candidate_id,
        "inactive_fixture_id": fixture_id,
        "inactive_fixture_family_id": str(fixture.get("family_id", "")) if fixture else "",
        "promotion_target": str(candidate.get("promotion_target", "")),
        "preview_status": "blocked" if blocked_reasons else "ready_for_review",
        "blocked_reasons": sorted(blocked_reasons),
        "before": before_state,
        "after": after_state,
        "validation_refs": sorted(str(item) for item in _as_list(candidate.get("validation_refs"))),
        "rollback_checkpoint_id": str(candidate.get("rollback_checkpoint_id", "")),
        "reviewer_signoff_required": True,
    }


def _state_snapshot(fixture: dict[str, Any] | None, state_name: str) -> dict[str, Any]:
    if fixture is None:
        return {"state": state_name, "exists": False}
    return {
        "state": state_name,
        "exists": True,
        "fixture_id": str(fixture.get("fixture_id", "")),
        "family_id": str(fixture.get("family_id", "")),
        "active": bool(fixture.get("active", False)),
        "content_hash": str(fixture.get("content_hash", "")),
        "schema_version": str(fixture.get("schema_version", "")),
    }


def _build_after_state(candidate: dict[str, Any], fixture: dict[str, Any] | None) -> dict[str, Any]:
    if fixture is None:
        return {"state": "after", "exists": False, "would_promote": False}
    patch = candidate.get("patch", {})
    if not isinstance(patch, dict):
        patch = {}
    return {
        "state": "after",
        "exists": True,
        "fixture_id": str(fixture.get("fixture_id", "")),
        "family_id": str(fixture.get("family_id", "")),
        "would_promote": True,
        "active": True,
        "content_hash": str(patch.get("content_hash", fixture.get("content_hash", ""))),
        "schema_version": str(patch.get("schema_version", fixture.get("schema_version", ""))),
        "patch_summary": str(candidate.get("patch_summary", "")),
    }


def _build_validation_inventory(rows: list[dict[str, Any]], inventory: dict[str, Any]) -> dict[str, Any]:
    family_ids = sorted(
        str(family.get("family_id", "unknown_family"))
        for family in _as_list(inventory.get("inactive_fixture_families"))
        if isinstance(family, dict)
    )
    refs = sorted({ref for row in rows for ref in row["validation_refs"]})
    return {
        "candidate_count": len(rows),
        "ready_for_review_count": sum(1 for row in rows if row["preview_status"] == "ready_for_review"),
        "blocked_count": sum(1 for row in rows if row["preview_status"] == "blocked"),
        "inactive_fixture_family_ids": family_ids,
        "validation_refs": refs,
        "deterministic_order": "candidate_id,inactive_fixture_id",
    }


def _build_signoff_placeholders(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": row["candidate_id"],
            "reviewer": "",
            "reviewed_at": "",
            "decision": "pending",
            "notes": "",
        }
        for row in rows
    ]


def _build_rollback_checkpoints(plan: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan_checkpoints = {
        str(item.get("checkpoint_id", "")): item
        for item in _as_list(plan.get("rollback_checkpoints"))
        if isinstance(item, dict)
    }
    checkpoints: list[dict[str, Any]] = []
    for row in rows:
        checkpoint_id = row["rollback_checkpoint_id"]
        source = plan_checkpoints.get(checkpoint_id, {})
        checkpoints.append(
            {
                "candidate_id": row["candidate_id"],
                "checkpoint_id": checkpoint_id,
                "restore_fixture_id": str(source.get("restore_fixture_id", row["inactive_fixture_id"])),
                "restore_content_hash": row["before"].get("content_hash", ""),
                "rollback_status": "placeholder",
            }
        )
    return checkpoints
