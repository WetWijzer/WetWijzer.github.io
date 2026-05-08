"""Deterministic replenishment selection policy for PP&D daemon supervision."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional


@dataclass(frozen=True)
class ReplenishmentCandidate:
    """A candidate work tranche the supervisor can enqueue."""

    task_id: str
    source: str
    selectable: bool = True


@dataclass(frozen=True)
class ReplenishmentDecision:
    """The supervisor's replenishment decision."""

    selected_task_id: Optional[str]
    reason: str


HUMAN_AUTHORED_AUTONOMY = "human-authored-autonomy-tranche"
GENERATED_CONTINUATION = "generated-continuation-slice"


def candidate_from_mapping(value: Mapping[str, object]) -> ReplenishmentCandidate:
    """Build a candidate from fixture or daemon ledger data."""

    return ReplenishmentCandidate(
        task_id=str(value["task_id"]),
        source=str(value["source"]),
        selectable=bool(value.get("selectable", True)),
    )


def select_replenishment_candidate(
    *,
    selectable_ppd_work_remaining: bool,
    original_goal_complete: bool,
    candidates: Iterable[ReplenishmentCandidate],
) -> ReplenishmentDecision:
    """Select the next replenishment candidate for the PP&D supervisor.

    When no selectable PP&D work remains and the original comprehensive goal is
    still incomplete, a human-authored autonomy tranche must be preferred over
    generated continuation slices.
    """

    if selectable_ppd_work_remaining:
        return ReplenishmentDecision(None, "selectable-ppd-work-remains")

    if original_goal_complete:
        return ReplenishmentDecision(None, "original-goal-complete")

    selectable_candidates = [candidate for candidate in candidates if candidate.selectable]

    for candidate in selectable_candidates:
        if candidate.source == HUMAN_AUTHORED_AUTONOMY:
            return ReplenishmentDecision(candidate.task_id, "preferred-human-authored-autonomy-tranche")

    for candidate in selectable_candidates:
        if candidate.source == GENERATED_CONTINUATION:
            return ReplenishmentDecision(candidate.task_id, "fallback-generated-continuation-slice")

    return ReplenishmentDecision(None, "no-selectable-replenishment-candidates")
