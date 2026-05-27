from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ppd.daemon.ppd_supervisor import SupervisorConfig, diagnose
from ppd.daemon.task_board import (
    count_unmanaged_generated_status_sections,
    parse_tasks,
    select_task,
    update_generated_status,
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class DaemonPlanNextTasksSupervisorBacklogTest(unittest.TestCase):
    def test_no_eligible_state_accepts_supervisor_only_backlog_and_refreshes_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            completed_board = (
                "- [x] Task checkbox-79: Preserve completed source registry coverage.\n"
                "- [x] Task checkbox-80: Preserve completed guardrail bundle coverage.\n"
                "\n"
                "\n"
                "## Generated Status\n"
                "\n"
                "Last updated: stale\n"
                "\n"
                "- Latest target: `Task checkbox-80: Preserve completed guardrail bundle coverage.`\n"
                "- Latest result: `accepted`\n"
                "- Latest summary: stale completed-board status before supervisor replanning.\n"
                "- Counts: `{\"blocked\": 0, \"complete\": 2, \"in_progress\": 0, \"needed\": 0}`\n"
                "\n"
                "\n"
            )
            (daemon_dir / "task-board.md").write_text(completed_board, encoding="utf-8")
            _write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-27T00:00:00Z",
                    "active_state": "no_eligible_tasks",
                    "state": "no_eligible_tasks",
                },
            )
            _write_json(daemon_dir / "progress.json", {"latest": {"failure_kind": "no_eligible_tasks"}})

            decision = diagnose(SupervisorConfig(repo_root=repo))

        self.assertEqual("plan_next_tasks", decision.action)
        self.assertTrue(decision.should_invoke_codex)

        supervisor_backlog_board = (
            completed_board.rstrip()
            + "\n\n## Supervisor-Only Backlog\n\n"
            + "- [ ] Task checkbox-81: Task supervisor-20260527-082: Add narrow daemon regression coverage for supervisor-only plan_next_tasks backlog additions.\n"
            + "- [ ] Task checkbox-82: Task supervisor-20260527-083: Add focused daemon validation for generated task-board status counts after supervisor replanning.\n"
        )
        tasks = parse_tasks(supervisor_backlog_board)
        selected = select_task(tasks)
        self.assertIsNotNone(selected)
        self.assertEqual(
            "Task checkbox-81: Task supervisor-20260527-082: Add narrow daemon regression coverage for supervisor-only plan_next_tasks backlog additions.",
            selected.label,
        )

        completed_labels = {task.label for task in tasks if task.status == "complete"}
        self.assertEqual(
            {
                "Task checkbox-79: Preserve completed source registry coverage.",
                "Task checkbox-80: Preserve completed guardrail bundle coverage.",
            },
            completed_labels,
        )

        refreshed = update_generated_status(
            supervisor_backlog_board,
            latest={
                "target_task": "Supervisor plan_next_tasks",
                "result": "accepted",
                "summary": "supervisor-only backlog accepted after no eligible daemon work",
            },
            tasks=tasks,
        )
        expected_counts = {"blocked": 0, "complete": 2, "in_progress": 0, "needed": 2}

        self.assertEqual(0, count_unmanaged_generated_status_sections(refreshed))
        self.assertEqual(1, refreshed.count("## Generated Status"))
        self.assertIn(f"- Counts: `{json.dumps(expected_counts, sort_keys=True)}`", refreshed)
        self.assertIn("- [x] Task checkbox-79: Preserve completed source registry coverage.", refreshed)
        self.assertIn("- [x] Task checkbox-80: Preserve completed guardrail bundle coverage.", refreshed)
        self.assertIn("- [ ] Task checkbox-81: Task supervisor-20260527-082", refreshed)
        self.assertIn("- [ ] Task checkbox-82: Task supervisor-20260527-083", refreshed)


if __name__ == "__main__":
    unittest.main()
