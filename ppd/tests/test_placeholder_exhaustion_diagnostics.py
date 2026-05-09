from __future__ import annotations

from ppd.daemon.placeholder_exhaustion_diagnostics import (
    PLANNING_GUIDANCE_ACTION,
    build_no_eligible_tasks_diagnostic,
    would_append_generated_deterministic_tranches,
)


def test_no_eligible_tasks_after_placeholder_exhaustion_requests_planning_guidance() -> None:
    diagnostic = build_no_eligible_tasks_diagnostic(
        {
            "reason": "no_eligible_tasks",
            "placeholders_exhausted": True,
            "eligible_task_count": 0,
        }
    )

    assert diagnostic["action"] == PLANNING_GUIDANCE_ACTION
    assert diagnostic["reason"] == "no_eligible_tasks"
    assert diagnostic["append_generated_deterministic_tranches"] is False
    assert "supervisor planning guidance" in diagnostic["guidance"]


def test_no_eligible_tasks_after_placeholder_exhaustion_never_appends_generated_tranches() -> None:
    diagnostic = build_no_eligible_tasks_diagnostic(
        {
            "reason": "no_eligible_tasks",
            "placeholders_exhausted": True,
            "eligible_task_count": 0,
        }
    )

    assert not would_append_generated_deterministic_tranches(diagnostic)
