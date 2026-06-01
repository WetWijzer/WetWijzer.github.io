"""Fixture-first post-activation monitoring rehearsal v4.

This module intentionally consumes only inactive activation checklist v4 fixtures and
returns synthetic monitoring rows. It does not activate guardrails, open DevHub,
read private documents, crawl live sites, upload, submit, certify, pay, schedule,
or make legal/permitting guarantees.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REHEARSAL_VERSION = "post_activation_monitoring_rehearsal_v4"
REQUIRED_CHECKLIST_VERSION = "activation_checklist_v4"

REQUIRED_ROW_IDS = (
    "guardrail_lookup_health",
    "stale_source_stop_gate",
    "exact_confirmation_gate_behavior",
    "refused_consequential_action",
    "refused_financial_action",
    "rollback_trigger_thresholds",
    "reviewer_escalation_routing",
    "exact_offline_validation_commands",
)

PROHIBITED_ACTIONS = (
    "activate_guardrails",
    "open_devhub",
    "read_private_documents",
    "crawl_live_sites",
    "upload",
    "submit",
    "certify",
    "pay",
    "schedule",
    "legal_or_permitting_guarantee",
)

OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/post_activation_monitoring_rehearsal_v4.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_post_activation_monitoring_rehearsal_v4.py"),
)


def load_inactive_checklist_fixture(path: str | Path) -> dict[str, Any]:
    """Load and validate an inactive activation checklist v4 fixture."""
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        checklist = json.load(handle)
    validate_inactive_checklist(checklist)
    return checklist


def validate_inactive_checklist(checklist: dict[str, Any]) -> None:
    if checklist.get("checklist_version") != REQUIRED_CHECKLIST_VERSION:
        raise ValueError("expected activation_checklist_v4 fixture")
    if checklist.get("activation_state") != "inactive":
        raise ValueError("rehearsal requires an inactive activation checklist fixture")
    if checklist.get("fixture_only") is not True:
        raise ValueError("rehearsal requires fixture_only=true")
    prohibited = checklist.get("prohibited_actions", [])
    missing = [action for action in PROHIBITED_ACTIONS if action not in prohibited]
    if missing:
        raise ValueError(f"inactive checklist fixture missing prohibited actions: {missing}")


def build_rehearsal_rows(checklist: dict[str, Any]) -> list[dict[str, Any]]:
    """Return deterministic synthetic monitoring rows from an inactive fixture."""
    validate_inactive_checklist(checklist)
    source_id = str(checklist["fixture_id"])
    commands = [list(command) for command in OFFLINE_VALIDATION_COMMANDS]
    rows = [
        _row(source_id, "guardrail_lookup_health", "lookup_ok", "synthetic guardrail lookup returns fixture-backed healthy status only"),
        _row(source_id, "stale_source_stop_gate", "stopped", "synthetic stale-source age exceeds fixture threshold and blocks downstream action"),
        _row(source_id, "exact_confirmation_gate_behavior", "confirmation_required", "synthetic action is blocked unless fixture text exactly matches the confirmation phrase"),
        _row(source_id, "refused_consequential_action", "refused", "synthetic consequential permitting action is refused before external effect"),
        _row(source_id, "refused_financial_action", "refused", "synthetic payment or fee action is refused before external effect"),
        _row(source_id, "rollback_trigger_thresholds", "rollback_rehearsed", "synthetic error budget breach crosses fixture rollback threshold"),
        _row(source_id, "reviewer_escalation_routing", "escalated", "synthetic blocked action routes to the fixture reviewer queue"),
        _row(source_id, "exact_offline_validation_commands", "offline_only", "only exact offline validation commands are exposed", validation_commands=commands),
    ]
    return rows


def build_rehearsal_document(checklist: dict[str, Any]) -> dict[str, Any]:
    rows = build_rehearsal_rows(checklist)
    return {
        "rehearsal_version": REHEARSAL_VERSION,
        "source_checklist_version": REQUIRED_CHECKLIST_VERSION,
        "source_fixture_id": checklist["fixture_id"],
        "activation_state": "inactive",
        "fixture_only": True,
        "external_effects_allowed": False,
        "prohibited_actions": list(PROHIBITED_ACTIONS),
        "rows": rows,
    }


def _row(
    source_id: str,
    row_id: str,
    expected_state: str,
    synthetic_observation: str,
    validation_commands: list[list[str]] | None = None,
) -> dict[str, Any]:
    row = {
        "row_id": row_id,
        "source_fixture_id": source_id,
        "synthetic": True,
        "expected_state": expected_state,
        "synthetic_observation": synthetic_observation,
        "external_effects_allowed": False,
        "requires_live_site": False,
        "requires_devhub": False,
        "requires_private_documents": False,
    }
    if validation_commands is not None:
        row["validation_commands"] = validation_commands
    return row
