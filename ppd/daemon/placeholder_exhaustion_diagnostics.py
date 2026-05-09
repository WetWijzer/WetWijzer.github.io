"""Diagnostics helpers for placeholder-exhaustion supervisor handoff.

This module is intentionally small and deterministic so daemon self-tests can
assert the expected no_eligible_tasks behavior without invoking live crawling or
LLM planning.
"""

from __future__ import annotations

from typing import Any, Mapping

PLANNING_GUIDANCE_ACTION = "supervisor_planning_guidance"
DETERMINISTIC_TRANCHE_ACTION = "append_generated_deterministic_tranches"


def build_no_eligible_tasks_diagnostic(event: Mapping[str, Any]) -> dict[str, Any]:
    """Return the diagnostic action for a no_eligible_tasks daemon event.

    Placeholder exhaustion is a supervisor planning problem. The daemon should
    surface guidance instead of manufacturing additional deterministic tranches,
    which can hide the fact that the explicit placeholder backlog is depleted.
    """

    reason = str(event.get("reason", ""))
    placeholders_exhausted = bool(event.get("placeholders_exhausted", False))
    eligible_task_count = int(event.get("eligible_task_count", 0))

    if reason == "no_eligible_tasks" and placeholders_exhausted and eligible_task_count == 0:
        return {
            "reason": "no_eligible_tasks",
            "action": PLANNING_GUIDANCE_ACTION,
            "append_generated_deterministic_tranches": False,
            "guidance": "Placeholder task backlog is exhausted; request supervisor planning guidance before adding new tranches.",
        }

    return {
        "reason": reason or "unknown",
        "action": "continue_daemon_diagnostics",
        "append_generated_deterministic_tranches": False,
    }


def would_append_generated_deterministic_tranches(diagnostic: Mapping[str, Any]) -> bool:
    """Expose the regression assertion in a named predicate for tests."""

    return bool(diagnostic.get("action") == DETERMINISTIC_TRANCHE_ACTION or diagnostic.get("append_generated_deterministic_tranches"))
