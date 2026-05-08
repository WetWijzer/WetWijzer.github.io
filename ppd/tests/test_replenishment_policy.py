from __future__ import annotations

import json
from pathlib import Path

from ppd.daemon.replenishment_policy import (
    GENERATED_CONTINUATION,
    HUMAN_AUTHORED_AUTONOMY,
    ReplenishmentCandidate,
    candidate_from_mapping,
    select_replenishment_candidate,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "replenishment" / "no_selectable_ppd_work_goal_incomplete.json"


def load_fixture_candidates() -> list[ReplenishmentCandidate]:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [candidate_from_mapping(value) for value in fixture["candidates"]]


def test_human_authored_autonomy_tranche_beats_generated_continuation_when_goal_incomplete() -> None:
    decision = select_replenishment_candidate(
        selectable_ppd_work_remaining=False,
        original_goal_complete=False,
        candidates=load_fixture_candidates(),
    )

    assert decision.selected_task_id == "checkbox-9356-human-authored-autonomy"
    assert decision.reason == "preferred-human-authored-autonomy-tranche"


def test_generated_continuation_is_only_fallback_when_no_human_tranche_exists() -> None:
    decision = select_replenishment_candidate(
        selectable_ppd_work_remaining=False,
        original_goal_complete=False,
        candidates=[
            ReplenishmentCandidate(
                task_id="generated-continuation-001",
                source=GENERATED_CONTINUATION,
            )
        ],
    )

    assert decision.selected_task_id == "generated-continuation-001"
    assert decision.reason == "fallback-generated-continuation-slice"


def test_replenishment_does_not_run_while_selectable_ppd_work_remains() -> None:
    decision = select_replenishment_candidate(
        selectable_ppd_work_remaining=True,
        original_goal_complete=False,
        candidates=[
            ReplenishmentCandidate(
                task_id="checkbox-9356-human-authored-autonomy",
                source=HUMAN_AUTHORED_AUTONOMY,
            )
        ],
    )

    assert decision.selected_task_id is None
    assert decision.reason == "selectable-ppd-work-remains"


def test_replenishment_does_not_run_after_original_goal_is_complete() -> None:
    decision = select_replenishment_candidate(
        selectable_ppd_work_remaining=False,
        original_goal_complete=True,
        candidates=load_fixture_candidates(),
    )

    assert decision.selected_task_id is None
    assert decision.reason == "original-goal-complete"
