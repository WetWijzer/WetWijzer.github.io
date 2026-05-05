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

from ppd.daemon.failure_policy import pre_llm_block_decision


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
    for task in task_list:
        if task.status != "blocked":
            continue
        if task.checkbox_id in PROTECTED_BLOCKED_REVISIT_CHECKBOX_IDS:
            continue
        try:
            block_decision = pre_llm_block_decision(config, task.label)
        except Exception:
            continue
        if block_decision is not None:
            continue
        return task
    return None


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
