"""Fixture-first inactive guardrail promotion candidate v4.

This module is intentionally offline-only. It reads committed fixtures and produces
an inactive promotion candidate; it never mutates active guardrail bundles or opens
external systems.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

READY_REPLAY_SCHEMA = "post_recompile_agent_readiness_replay_v4"
PLACEHOLDER_SCHEMA = "prior_guardrail_placeholder_fixture_v4"
CANDIDATE_SCHEMA = "inactive_guardrail_promotion_candidate_v4"

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/guardrails/inactive_promotion_candidate_v4.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_inactive_guardrail_promotion_candidate_v4.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return data


def _require_schema(data: dict[str, Any], expected: str, label: str) -> None:
    actual = data.get("schema")
    if actual != expected:
        raise ValueError(f"{label} fixture schema must be {expected!r}, got {actual!r}")


def build_candidate(readiness_replay: dict[str, Any], placeholders: dict[str, Any]) -> dict[str, Any]:
    """Build an inactive promotion candidate from offline fixtures only."""

    _require_schema(readiness_replay, READY_REPLAY_SCHEMA, "readiness replay")
    _require_schema(placeholders, PLACEHOLDER_SCHEMA, "placeholder")

    agents = readiness_replay.get("agents", [])
    guardrails = placeholders.get("guardrails", [])
    if not isinstance(agents, list):
        raise ValueError("readiness replay agents must be a list")
    if not isinstance(guardrails, list):
        raise ValueError("placeholder guardrails must be a list")

    readiness_by_id: dict[str, dict[str, Any]] = {}
    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError("each readiness replay agent must be an object")
        agent_id = str(agent.get("agent_id", "")).strip()
        if not agent_id:
            raise ValueError("each readiness replay agent must include agent_id")
        readiness_by_id[agent_id] = agent

    inactive_rows: list[dict[str, Any]] = []
    stale_source_holds: list[dict[str, str]] = []

    for guardrail in sorted(guardrails, key=lambda item: str(item.get("guardrail_id", ""))):
        if not isinstance(guardrail, dict):
            raise ValueError("each placeholder guardrail must be an object")
        guardrail_id = str(guardrail.get("guardrail_id", "")).strip()
        agent_id = str(guardrail.get("agent_id", "")).strip()
        if not guardrail_id or not agent_id:
            raise ValueError("each placeholder guardrail must include guardrail_id and agent_id")

        readiness = readiness_by_id.get(agent_id)
        if readiness is None:
            stale_source_holds.append(
                {
                    "guardrail_id": guardrail_id,
                    "agent_id": agent_id,
                    "reason": "missing post-recompile readiness replay for placeholder agent",
                }
            )
            status = "hold"
        elif readiness.get("ready") is not True:
            stale_source_holds.append(
                {
                    "guardrail_id": guardrail_id,
                    "agent_id": agent_id,
                    "reason": "agent readiness replay is not ready",
                }
            )
            status = "hold"
        else:
            status = "candidate"

        inactive_rows.append(
            {
                "guardrail_id": guardrail_id,
                "agent_id": agent_id,
                "source_placeholder_id": str(guardrail.get("placeholder_id", guardrail_id)),
                "proposed_state": "inactive",
                "active_bundle_mutation": False,
                "status": status,
                "notes": str(guardrail.get("notes", "offline fixture candidate only")),
            }
        )

    return {
        "schema": CANDIDATE_SCHEMA,
        "source_fixtures": {
            "readiness_replay_schema": READY_REPLAY_SCHEMA,
            "placeholder_schema": PLACEHOLDER_SCHEMA,
        },
        "inactive_promotion_rows": inactive_rows,
        "activation_prerequisites": [
            "reviewer confirms readiness replay fixture was generated after recompile",
            "reviewer confirms placeholders still match intended inactive guardrail rows",
            "reviewer confirms no active guardrail bundle mutation is included in this proposal",
            "run all offline validation commands successfully before any later activation proposal",
        ],
        "stale_source_holds": stale_source_holds,
        "reviewer_signoff_placeholders": [
            {"role": "implementation reviewer", "status": "pending", "name": "TBD"},
            {"role": "guardrail owner", "status": "pending", "name": "TBD"},
        ],
        "rollback_plan": [
            "discard this inactive candidate fixture output",
            "leave active guardrail bundles unchanged",
            "rerun readiness replay and rebuild candidate from fresh fixtures if needed",
        ],
        "post_promotion_smoke_checks": [
            "confirm promoted rows remain inactive until a separate activation review",
            "confirm stale-source holds were not promoted",
            "confirm daemon self-test passes offline",
        ],
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "prohibited_actions": [
            "no DevHub access",
            "no private document reads",
            "no uploads or submissions",
            "no certification, payment, or scheduling",
            "no legal or permitting guarantees",
        ],
    }


def build_candidate_from_files(readiness_path: Path, placeholders_path: Path) -> dict[str, Any]:
    return build_candidate(load_json(readiness_path), load_json(placeholders_path))
