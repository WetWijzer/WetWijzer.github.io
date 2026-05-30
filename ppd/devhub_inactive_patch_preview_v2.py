"""Fixture-first inactive DevHub observed surface patch preview v2.

This module is intentionally offline-only. It converts fixture dictionaries for a
DevHub observed surface update plan, an attended observation handoff checklist,
and inactive surface observations into deterministic preview rows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PREVIEW_VERSION = "devhub-observed-surface-inactive-patch-preview-v2"
PREVIEW_FIELDS = (
    "label",
    "selector",
    "validation_message",
    "redaction_policy",
    "attendance_gate",
    "selector_confidence_note",
)
FORBIDDEN_FLAGS = (
    ("requires_live_devhub_access", "live DevHub access is not allowed for fixture-first preview"),
    ("requires_authenticated_artifact", "authenticated artifacts are not allowed for fixture-first preview"),
    ("requires_session_state", "private DevHub session state is not allowed for fixture-first preview"),
    ("contains_private_values", "private values are not allowed in committed preview fixtures"),
    ("performs_official_action", "official DevHub actions are not allowed for preview rows"),
    ("mutates_active_surface", "active surface mutation is not allowed for inactive preview"),
    ("mutates_process", "process mutation is not allowed for inactive preview"),
    ("mutates_guardrail", "guardrail mutation is not allowed for inactive preview"),
)


@dataclass(frozen=True)
class PreviewInput:
    plan: dict[str, Any]
    checklist: dict[str, Any]
    surfaces: dict[str, Any]


def build_preview_v2(plan: dict[str, Any], checklist: dict[str, Any], surfaces: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic read-only preview rows from offline fixtures."""

    surface_index = {surface["surface_id"]: surface for surface in surfaces.get("inactive_surfaces", [])}
    checklist_gates = checklist.get("attendance_gates", {})
    rows: list[dict[str, Any]] = []

    for update in sorted(plan.get("surface_updates", []), key=lambda item: item.get("update_id", "")):
        surface_id = update.get("surface_id", "")
        surface = surface_index.get(surface_id, {})
        proposed = update.get("proposed", {})
        base_reasons = _blocked_reasons(update, checklist_gates, surface)

        for field in PREVIEW_FIELDS:
            before = surface.get(field, "")
            after = proposed.get(field, before)
            blocked_explanations = list(base_reasons)
            status = "blocked" if blocked_explanations else "previewable"
            if before == after and not blocked_explanations:
                status = "unchanged"

            rows.append(
                {
                    "row_id": f"{surface_id}:{field}",
                    "update_id": update.get("update_id", ""),
                    "surface_id": surface_id,
                    "field": field,
                    "before": before,
                    "after": after,
                    "status": status,
                    "read_only": True,
                    "blocked_explanations": blocked_explanations,
                }
            )

    return {
        "preview_version": PREVIEW_VERSION,
        "source_fixture_versions": {
            "update_plan": plan.get("version", "unknown"),
            "handoff_checklist": checklist.get("version", "unknown"),
            "inactive_surfaces": surfaces.get("version", "unknown"),
        },
        "reviewer_owner": checklist.get("reviewer_owner", plan.get("reviewer_owner", "unassigned")),
        "rollback_checkpoints": _rollback_checkpoints(plan, checklist),
        "validation_inventory": _validation_inventory(plan, checklist, surfaces, rows),
        "rows": rows,
    }


def _blocked_reasons(update: dict[str, Any], checklist_gates: dict[str, Any], surface: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not surface:
        reasons.append("surface fixture is missing for update")
    elif surface.get("state") != "inactive":
        reasons.append("surface fixture is not inactive")

    for flag, explanation in FORBIDDEN_FLAGS:
        if update.get(flag) or surface.get(flag):
            reasons.append(explanation)

    required_gate = update.get("attendance_gate")
    if required_gate and checklist_gates.get(required_gate) != "ready":
        reasons.append(f"attendance gate {required_gate!r} is not ready")

    return reasons


def _rollback_checkpoints(plan: dict[str, Any], checklist: dict[str, Any]) -> list[str]:
    checkpoints: list[str] = []
    checkpoints.extend(str(item) for item in plan.get("rollback_checkpoints", []))
    checkpoints.extend(str(item) for item in checklist.get("rollback_checkpoints", []))
    return sorted(dict.fromkeys(checkpoints))


def _validation_inventory(
    plan: dict[str, Any], checklist: dict[str, Any], surfaces: dict[str, Any], rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return [
        {"name": "update_plan_fixture", "status": "present", "count": len(plan.get("surface_updates", []))},
        {"name": "handoff_checklist_fixture", "status": "present", "count": len(checklist.get("attendance_gates", {}))},
        {"name": "inactive_surface_fixtures", "status": "present", "count": len(surfaces.get("inactive_surfaces", []))},
        {"name": "preview_rows", "status": "derived", "count": len(rows)},
        {
            "name": "blocked_rows",
            "status": "derived",
            "count": sum(1 for row in rows if row["status"] == "blocked"),
        },
    ]
