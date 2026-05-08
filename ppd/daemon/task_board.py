"""PP&D task-board parsing, selection, and generated-status helpers."""

from __future__ import annotations

import re
from typing import Any, Iterable, Optional

from ipfs_datasets_py.optimizers.todo_daemon.engine import (
    Task,
    parse_markdown_tasks,
    select_task as select_todo_task,
)
from ipfs_datasets_py.optimizers.todo_daemon.task_board import (
    count_unmanaged_generated_status_sections as count_todo_unmanaged_generated_status_sections,
    replace_task_mark as replace_todo_task_mark,
    should_sleep_between_task_cycles as should_sleep_between_todo_task_cycles,
    strip_unmanaged_generated_status_sections as strip_todo_unmanaged_generated_status_sections,
    update_generated_status_block as update_todo_generated_status_block,
)

from ppd.daemon.failure_policy import (
    has_llm_termination_block_for_failures,
    llm_termination_failure_count_from_failures,
    pre_llm_block_decision_for_failures,
    read_result_and_diagnostic_log,
    recent_task_failures_from_records,
)


CHECKBOX_RE = re.compile(r"^(?P<prefix>\s*-\s+\[)(?P<mark>[ xX~!])(?P<suffix>\]\s+)(?P<title>.+)$")
TASK_BOARD_STATUS_START = "<!-- ppd-daemon-task-board:start -->"
TASK_BOARD_STATUS_END = "<!-- ppd-daemon-task-board:end -->"

PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS = frozenset(
    {
        178,
        182,
        186,
        187,
        191,
        193,
        194,
        195,
        197,
        198,
        203,
        208,
        209,
        210,
    }
)

GENERATED_BLOCKED_CASCADE_TITLE_RE = re.compile(
    r"^Add generated blocked-cascade daemon-repair coverage for tranche \d+ item \d+ "
    r"proving blocked PP&D work stays parked until a fresh daemon repair task validates\.?$"
)


def parse_tasks(markdown: str) -> list[Task]:
    return parse_markdown_tasks(markdown, checkbox_re=CHECKBOX_RE)


def select_task(tasks: Iterable[Task], *, revisit_blocked: bool = False) -> Optional[Task]:
    return select_todo_task(
        tasks,
        revisit_blocked=revisit_blocked,
        protected_blocked_checkbox_ids=PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS,
    )


def select_task_for_config(tasks: Iterable[Task], config: Any) -> Optional[Task]:
    """Select work while suppressing blocked tasks that already hit retry stop gates."""

    task_list = list(tasks)
    selected = select_task(task_list, revisit_blocked=False)
    if selected is not None:
        return selected
    if not config.revisit_blocked:
        return None
    records = read_result_and_diagnostic_log(config.resolve(config.result_log))
    blocked_revisit_tasks = [
        task
        for task in task_list
        if task.status == "blocked" and task.checkbox_id not in PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS
    ]
    source_backed_blocked_tasks = [
        task for task in blocked_revisit_tasks if not is_generated_blocked_cascade_task(task)
    ]
    # Generated blocked-cascade repair tasks are fallback scaffolding. Once the
    # user asks to work the blocked backlog, prefer the human/source-backed PP&D
    # tasks so the daemon does not churn through hundreds of generated slices.
    candidate_pool = source_backed_blocked_tasks or blocked_revisit_tasks
    if getattr(config, "revisit_blocked_reassess_llm_termination_gates", False):
        reassessment_candidates = []
        for task in candidate_pool:
            failures = recent_task_failures_from_records(records, task.label, limit=100)
            llm_termination_count = llm_termination_failure_count_from_failures(failures)
            reassessment_candidates.append((llm_termination_count, task.checkbox_id, task))
        if reassessment_candidates:
            return min(reassessment_candidates, key=lambda item: (item[0], item[1]))[2]
    for task in candidate_pool:
        try:
            failures = recent_task_failures_from_records(records, task.label, limit=100)
            if (
                getattr(config, "revisit_blocked_ignore_failure_gates", False)
                and not getattr(config, "revisit_blocked_reassess_llm_termination_gates", False)
                and has_llm_termination_block_for_failures(config, failures)
            ):
                continue
            block_decision = pre_llm_block_decision_for_failures(config, failures)
        except Exception:
            if getattr(config, "revisit_blocked_ignore_failure_gates", False):
                return task
            continue
        if block_decision is not None:
            if getattr(config, "revisit_blocked_reassess_llm_termination_gates", False):
                return task
            if getattr(config, "revisit_blocked_ignore_failure_gates", False) and (
                block_decision.failure_kind != "llm_termination"
            ):
                return task
            continue
        return task
    return None


def is_generated_blocked_cascade_task(task: Task) -> bool:
    return bool(GENERATED_BLOCKED_CASCADE_TITLE_RE.match(task.title.strip()))


def replace_task_mark(markdown: str, selected: Task, mark: str) -> str:
    return replace_todo_task_mark(markdown, selected, mark, checkbox_re=CHECKBOX_RE)


def count_unmanaged_generated_status_sections(markdown: str) -> int:
    """Count generated-status headings outside the daemon-managed marker block."""

    return count_todo_unmanaged_generated_status_sections(
        markdown,
        start_marker=TASK_BOARD_STATUS_START,
        end_marker=TASK_BOARD_STATUS_END,
    )


def strip_unmanaged_generated_status_sections(markdown: str) -> str:
    """Remove stale generated-status sections outside the managed marker block."""

    return strip_todo_unmanaged_generated_status_sections(
        markdown,
        start_marker=TASK_BOARD_STATUS_START,
        end_marker=TASK_BOARD_STATUS_END,
    )


def update_generated_status(markdown: str, *, latest: dict[str, Any], tasks: list[Task]) -> str:
    return update_todo_generated_status_block(
        markdown,
        latest=latest,
        tasks=tasks,
        start_marker=TASK_BOARD_STATUS_START,
        end_marker=TASK_BOARD_STATUS_END,
    )


def should_sleep_between_watch_cycles(markdown: str, *, revisit_blocked: bool = False) -> bool:
    """Sleep only when there is no immediately selectable work on the board."""

    return should_sleep_between_todo_task_cycles(
        markdown,
        parse_tasks_fn=parse_tasks,
        revisit_blocked=revisit_blocked,
        protected_blocked_checkbox_ids=PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS,
    )
