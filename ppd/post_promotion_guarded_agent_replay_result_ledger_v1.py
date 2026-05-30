"""Fixture-first post-promotion guarded agent replay result ledger v1.

This module intentionally performs no live agent execution, source crawling,
DevHub access, prompt mutation, or official action. It transforms a synthetic
post-promotion guarded replay plan fixture into deterministic reviewer ledger
rows that can be validated offline.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/post_promotion_guarded_agent_replay_result_ledger_v1.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_post_promotion_guarded_agent_replay_result_ledger_v1.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

PLACEHOLDER_REVIEWER_OBSERVATION = "PENDING_OFFLINE_REVIEWER_OBSERVATION"
PLACEHOLDER_EXPECTED_PASS = "EXPECTED_PASS_PLACEHOLDER"
PLACEHOLDER_EXPECTED_BLOCK = "EXPECTED_BLOCK_PLACEHOLDER"


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _scenario_sort_key(scenario: dict[str, Any]) -> tuple[int, str]:
    order = scenario.get("order")
    if not isinstance(order, int):
        order = 999_999
    scenario_id = str(scenario.get("scenario_id", ""))
    return order, scenario_id


def _expected_placeholder(scenario: dict[str, Any]) -> str:
    outcome = str(scenario.get("expected_guarded_outcome", "")).lower()
    if outcome == "block":
        return PLACEHOLDER_EXPECTED_BLOCK
    return PLACEHOLDER_EXPECTED_PASS


def build_result_ledger(plan: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic synthetic replay result ledger rows from a plan."""

    scenarios = plan.get("scenarios", [])
    if not isinstance(scenarios, list):
        raise ValueError("plan.scenarios must be a list")

    rows: list[dict[str, Any]] = []
    for index, scenario in enumerate(sorted(scenarios, key=_scenario_sort_key), start=1):
        if not isinstance(scenario, dict):
            raise ValueError("each scenario must be an object")

        scenario_id = str(scenario.get("scenario_id", f"scenario-{index:03d}"))
        cited_refs = [str(item) for item in _as_list(scenario.get("cited_scenario_references"))]
        rollback_ref = str(
            scenario.get(
                "rollback_checkpoint_reference",
                plan.get("rollback_checkpoint_reference", "rollback-checkpoint-not-specified"),
            )
        )

        rows.append(
            {
                "row_index": index,
                "scenario_id": scenario_id,
                "scenario_ref": f"scenario:{scenario_id}",
                "cited_scenario_references": cited_refs,
                "expected_guarded_outcome": scenario.get("expected_guarded_outcome", "pass"),
                "expected_outcome_placeholder": _expected_placeholder(scenario),
                "synthetic_replay_result": "NOT_RUN_FIXTURE_ONLY",
                "reviewer_observation_placeholder": PLACEHOLDER_REVIEWER_OBSERVATION,
                "mismatch_carry_forward": {
                    "prior_mismatch_id": scenario.get("prior_mismatch_id"),
                    "prior_mismatch_summary": scenario.get("prior_mismatch_summary"),
                    "carry_forward_required": bool(scenario.get("carry_forward_required", False)),
                    "carry_forward_notes_placeholder": "PENDING_REVIEWER_MISMATCH_NOTES",
                },
                "rollback_checkpoint_reference": rollback_ref,
            }
        )

    return {
        "ledger_version": "post_promotion_guarded_agent_replay_result_ledger_v1",
        "source_plan_version": plan.get("plan_version", "post_promotion_guarded_agent_replay_plan_v1"),
        "source_plan_id": plan.get("plan_id", "synthetic-post-promotion-guarded-agent-replay-plan-v1"),
        "execution_mode": "fixture_first_offline_no_live_agents",
        "official_actions_performed": False,
        "live_agents_run": False,
        "active_artifacts_mutated": False,
        "ordered_result_rows": rows,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }


def load_plan(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_ledger(plan_path: Path, output_path: Path) -> None:
    ledger = build_result_ledger(load_plan(plan_path))
    output_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")


__all__ = ["OFFLINE_VALIDATION_COMMANDS", "build_result_ledger", "load_plan", "write_ledger"]
