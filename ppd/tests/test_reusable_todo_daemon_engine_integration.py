from __future__ import annotations

import unittest

from ppd.daemon import ppd_daemon

from ipfs_datasets_py.optimizers.todo_daemon.engine import (
    CommandResult as EngineCommandResult,
    Proposal as EngineProposal,
    Task as EngineTask,
)
from ipfs_datasets_py.optimizers.todo_daemon.runner import TodoDaemonRunner


class ReusableTodoDaemonEngineIntegrationTests(unittest.TestCase):
    def test_ppd_daemon_uses_shared_engine_dataclasses(self) -> None:
        self.assertIs(ppd_daemon.Task, EngineTask)
        self.assertIs(ppd_daemon.Proposal, EngineProposal)
        self.assertIs(ppd_daemon.CommandResult, EngineCommandResult)
        self.assertTrue(issubclass(ppd_daemon.Daemon, TodoDaemonRunner))

        task = ppd_daemon.parse_tasks("- [ ] Task checkbox-450: Reusable engine wiring.\n")[0]

        self.assertIsInstance(task, EngineTask)
        self.assertEqual("Task checkbox-450: Reusable engine wiring.", task.label)

    def test_ppd_path_policy_keeps_portland_specific_guardrails(self) -> None:
        self.assertEqual([], ppd_daemon.validate_write_path("ppd/platform/reusable_contract.py"))
        self.assertTrue(
            any(
                "outside PP&D daemon allowlist" in error
                for error in ppd_daemon.validate_write_path("docs/not-the-plan.md")
            )
        )
        self.assertTrue(
            any(
                "private/session artifacts" in error
                for error in ppd_daemon.validate_write_path("ppd/devhub/auth-state.json")
            )
        )

    def test_visible_source_change_policy_ignores_runtime_only_progress(self) -> None:
        self.assertTrue(ppd_daemon.has_visible_source_change(["ppd/platform/reusable_contract.py"]))
        self.assertFalse(
            ppd_daemon.has_visible_source_change(
                [
                    "ppd/daemon/task-board.md",
                    "ppd/daemon/builtin-repair-status.json",
                    "ppd/daemon/accepted-work/accepted-work.jsonl",
                ]
            )
        )


if __name__ == "__main__":
    unittest.main()
