"""Regression tests for daemon task-board completion source-change validation."""

from __future__ import annotations

import json
from pathlib import Path

from ppd.daemon.proposal_source_change_validation import (
    validate_daemon_timeout_diagnostic_boundaries,
    validate_task_board_completion_source_changes,
)


_FIXTURES = Path(__file__).parent / "fixtures" / "daemon_validation"


def _fixture(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def test_rejects_task_board_completion_without_visible_source_change() -> None:
    findings = validate_task_board_completion_source_changes(
        _fixture("task_board_completion_without_source_change.json")
    )

    assert [finding.code for finding in findings] == [
        "task_board_completion_without_source_change"
    ]


def test_allows_task_board_completion_with_visible_source_change() -> None:
    findings = validate_task_board_completion_source_changes(
        _fixture("task_board_completion_with_source_change.json")
    )

    assert findings == []


def test_allows_supervisor_only_plan_next_tasks_backlog_update() -> None:
    findings = validate_task_board_completion_source_changes(
        _fixture("plan_next_tasks_backlog_update.json")
    )

    assert findings == []


def test_rejects_plan_next_tasks_when_it_marks_work_complete() -> None:
    findings = validate_task_board_completion_source_changes(
        _fixture("plan_next_tasks_completion_update.json")
    )

    assert [finding.code for finding in findings] == [
        "task_board_completion_in_plan_next_tasks"
    ]


def test_allows_plan_next_tasks_with_historical_completed_tasks_and_new_unchecked_backlog() -> None:
    proposal = {
        "summary": "Supervisor plan_next_tasks after timeout diagnostics",
        "impact": "Append only the next ordered backlog item.",
        "plan_next_tasks": ["Add deterministic timeout diagnostic boundary validation"],
        "files": [
            {
                "path": "ppd/daemon/task-board.md",
                "content": "# PP&D Daemon Task Board\n\n## Completed Work\n\n- [x] Task checkbox-109: Historical completed task.\n\n## Next Ordered Tranche\n\nplan_next_tasks:\n- [ ] Task checkbox-110: Add deterministic timeout diagnostic boundary validation.\n",
            }
        ],
    }

    findings = validate_daemon_timeout_diagnostic_boundaries(proposal)

    assert findings == []


def test_timeout_diagnostic_can_update_only_supervisor_metadata() -> None:
    proposal = {
        "summary": "Record worker_llm_timeout diagnostic metadata.",
        "diagnostics": [
            {
                "kind": "worker_llm_timeout",
                "target_task": "Task checkbox-109",
                "elapsed_timeout_seconds": 300,
                "retry_count": 2,
            }
        ],
        "files": [
            {
                "path": "ppd/daemon/progress.json",
                "content": "{\"latest\": {\"failure_kind\": \"worker_llm_timeout\"}}\n",
            }
        ],
    }

    findings = validate_daemon_timeout_diagnostic_boundaries(proposal)

    assert findings == []


def test_timeout_diagnostic_rejects_domain_source_edits() -> None:
    proposal = {
        "summary": "Record daemon_llm_timeout diagnostic metadata.",
        "diagnostics": [{"kind": "daemon_llm_timeout", "target_task": "Task checkbox-109"}],
        "files": [
            {
                "path": "ppd/logic/example.py",
                "content": "TIMEOUT_DIAGNOSTIC = True\n",
            }
        ],
    }

    findings = validate_daemon_timeout_diagnostic_boundaries(proposal)

    assert [finding.code for finding in findings] == [
        "timeout_diagnostic_not_supervisor_only"
    ]
    assert findings[0].path == "ppd/logic/example.py"


def test_timeout_diagnostic_rejects_task_board_completion_without_promoted_source_change() -> None:
    proposal = {
        "summary": "Record worker_llm_timeout diagnostic metadata.",
        "diagnostics": [{"kind": "worker_llm_timeout", "target_task": "Task checkbox-109"}],
        "files": [
            {
                "path": "ppd/daemon/task-board.md",
                "content": "# PP&D Daemon Task Board\n\n- [x] Task checkbox-109: Add PP&D domain implementation.\n",
            }
        ],
    }

    findings = validate_daemon_timeout_diagnostic_boundaries(proposal)

    assert [finding.code for finding in findings] == [
        "task_board_completion_without_source_change",
        "timeout_diagnostic_marks_domain_task_complete",
        "timeout_diagnostic_not_supervisor_only",
    ]


def test_timeout_diagnostic_allows_later_ordered_plan_next_tasks_backlog_addition() -> None:
    proposal = {
        "summary": "plan_next_tasks after worker_llm_timeout diagnostic",
        "impact": "Append the next ordered daemon backlog item only.",
        "plan_next_tasks": [
            {
                "status": "needed",
                "title": "Task checkbox-111: Add timeout diagnostic compaction coverage.",
            }
        ],
        "diagnostics": [
            {
                "kind": "worker_llm_timeout",
                "target_task": "Task checkbox-109",
                "elapsed_timeout_seconds": 300,
                "retry_count": 2,
                "guidance": "Return a smaller next attempt.",
            }
        ],
        "files": [
            {
                "path": "ppd/daemon/task-board.md",
                "content": "# PP&D Daemon Task Board\n\n## Completed Work\n\n- [x] Task checkbox-108: Historical completed validation task.\n\n## Next Ordered Tranche\n\nplan_next_tasks:\n- [ ] Task checkbox-111: Add timeout diagnostic compaction coverage.\n",
            }
        ],
    }

    findings = validate_daemon_timeout_diagnostic_boundaries(proposal)

    assert findings == []
