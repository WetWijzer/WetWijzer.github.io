from ppd.daemon.task_board import parse_tasks, select_task
from ppd.daemon.worker_llm_timeout_diagnostics import (
    SMALLER_WORKER_TIMEOUT_NEXT_ATTEMPT_GUIDANCE,
    WorkerLlmTimeoutEvent,
    repeated_worker_llm_timeout_diagnostics,
)


def test_repeated_worker_llm_timeout_records_required_context_for_same_task():
    events = [
        WorkerLlmTimeoutEvent(
            target_task="Task checkbox-108: Add worker LLM timeout regression.",
            elapsed_timeout_seconds=300,
            summary="worker exceeded llm timeout before returning JSON",
        ),
        WorkerLlmTimeoutEvent(
            target_task="Task checkbox-109: unrelated task",
            elapsed_timeout_seconds=300,
            summary="single timeout is not repeated",
        ),
        WorkerLlmTimeoutEvent(
            target_task="Task checkbox-108: Add worker LLM timeout regression.",
            elapsed_timeout_seconds=300,
            summary="worker exceeded llm timeout again",
        ),
    ]

    diagnostics = repeated_worker_llm_timeout_diagnostics(events)

    assert diagnostics == [
        {
            "kind": "worker_llm_timeout",
            "target_task": "Task checkbox-108: Add worker LLM timeout regression.",
            "elapsed_timeout_seconds": 300,
            "retry_count": 2,
            "latest_summary": "worker exceeded llm timeout again",
            "guidance": SMALLER_WORKER_TIMEOUT_NEXT_ATTEMPT_GUIDANCE,
        }
    ]
    assert "smaller next attempt" in diagnostics[0]["guidance"]


def test_single_worker_llm_timeout_is_not_reported_as_repeated():
    events = [
        WorkerLlmTimeoutEvent(
            target_task="Task checkbox-108: Add worker LLM timeout regression.",
            elapsed_timeout_seconds=300,
        )
    ]

    assert repeated_worker_llm_timeout_diagnostics(events) == []


def test_worker_llm_timeout_diagnostics_do_not_add_selection_fields_or_change_selection():
    board_text = """
# PP&D Daemon Task Board

- [x] Task checkbox-107: Completed predecessor.
- [ ] Task checkbox-108: Add worker LLM timeout regression.
- [ ] Task checkbox-109: Later ordinary work.
"""
    selected_before = select_task(parse_tasks(board_text))

    diagnostics = repeated_worker_llm_timeout_diagnostics(
        [
            WorkerLlmTimeoutEvent(
                target_task="Task checkbox-108: Add worker LLM timeout regression.",
                elapsed_timeout_seconds=300,
            ),
            WorkerLlmTimeoutEvent(
                target_task="Task checkbox-108: Add worker LLM timeout regression.",
                elapsed_timeout_seconds=300,
            ),
        ]
    )

    selected_after = select_task(parse_tasks(board_text))
    assert selected_before is not None
    assert selected_after is not None
    assert selected_before.checkbox_id == selected_after.checkbox_id == 108

    diagnostic = diagnostics[0]
    assert "selected_task" not in diagnostic
    assert "next_task" not in diagnostic
    assert "priority" not in diagnostic
    assert "score" not in diagnostic
    assert "status" not in diagnostic
