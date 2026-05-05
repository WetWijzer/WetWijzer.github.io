from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from ppd.daemon.ppd_daemon import (
    CommandResult,
    Config,
    Daemon,
    Proposal,
    failure_block_threshold,
    parse_tasks,
    select_task_for_config,
    should_block_task_before_llm,
    should_skip_validation_for_no_file_failure,
    terminate_process_group,
)


class DaemonLlmResultDurabilityTest(unittest.TestCase):
    def test_parse_failure_diagnostic_is_written_before_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            (repo / "ppd" / "daemon").mkdir(parents=True)
            (repo / "ppd" / "daemon" / "task-board.md").write_text(
                "- [~] Task checkbox-1: Synthetic task.\n",
                encoding="utf-8",
            )
            daemon = Daemon(Config(repo_root=repo, apply=True))
            proposal = Proposal(
                errors=["LLM response did not contain a JSON object."],
                failure_kind="parse",
                target_task="Task checkbox-1: Synthetic task.",
            )
            proposal.dry_run = False

            daemon.write_progress([proposal])
            daemon.write_cycle_diagnostic(proposal, stage="before_validation")

            progress = json.loads((repo / "ppd" / "daemon" / "progress.json").read_text(encoding="utf-8"))
            rows = [
                json.loads(line)
                for line in (repo / "ppd" / "daemon" / "ppd-daemon.jsonl").read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual("parse", progress["latest"]["failure_kind"])
        self.assertEqual("before_validation", rows[0]["stage"])
        self.assertEqual("parse", rows[0]["diagnostic"]["failure_kind"])

    def test_timeout_interrupted_and_vanished_child_diagnostics_are_durable(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            (repo / "ppd" / "daemon").mkdir(parents=True)
            (repo / "ppd" / "daemon" / "task-board.md").write_text(
                "- [~] Task checkbox-1: Synthetic task.\n",
                encoding="utf-8",
            )
            daemon = Daemon(Config(repo_root=repo, apply=True))
            for message in (
                "llm_router child timed out after 330 seconds",
                "llm_router child exited with code -9",
                "validation command interrupted before final result",
            ):
                proposal = Proposal(
                    summary="LLM proposal failed.",
                    errors=[message],
                    failure_kind="llm",
                    target_task="Task checkbox-1: Synthetic task.",
                )
                daemon.write_cycle_diagnostic(proposal, stage="before_validation")

            rows = [
                json.loads(line)
                for line in (repo / "ppd" / "daemon" / "ppd-daemon.jsonl").read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual(3, len(rows))
        self.assertTrue(all(row["diagnostic"]["failure_kind"] == "llm" for row in rows))
        self.assertIn("timed out", rows[0]["diagnostic"]["errors"][0])
        self.assertIn("code -9", rows[1]["diagnostic"]["errors"][0])
        self.assertIn("interrupted", rows[2]["diagnostic"]["errors"][0])

    def test_no_file_llm_failures_skip_full_validation_after_durable_diagnostic(self) -> None:
        self.assertTrue(
            should_skip_validation_for_no_file_failure(
                Proposal(summary="LLM proposal failed.", failure_kind="llm")
            )
        )
        self.assertTrue(
            should_skip_validation_for_no_file_failure(
                Proposal(errors=["LLM response did not contain a JSON object."], failure_kind="parse")
            )
        )
        self.assertFalse(
            should_skip_validation_for_no_file_failure(
                Proposal(
                    summary="Has files",
                    failure_kind="llm",
                    files=[{"path": "ppd/example.py", "content": "print('ok')\n"}],
                )
            )
        )
        self.assertFalse(should_skip_validation_for_no_file_failure(Proposal(summary="Needs validation")))

    def test_syntax_preflight_failures_block_after_tighter_threshold(self) -> None:
        config = Config(repo_root=Path("."), max_task_failures_before_block=3)

        self.assertEqual(2, failure_block_threshold(Proposal(failure_kind="syntax_preflight"), config))
        self.assertEqual(3, failure_block_threshold(Proposal(failure_kind="validation"), config))
        self.assertEqual(
            1,
            failure_block_threshold(
                Proposal(failure_kind="syntax_preflight"),
                Config(repo_root=Path("."), max_task_failures_before_block=1),
            ),
        )

    def test_repeated_syntax_preflight_failures_block_before_next_llm(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = "Task checkbox-242: Add processor-suite execution integration."
            for kind in ("syntax_preflight", "syntax_preflight"):
                with (daemon_dir / "ppd-daemon.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(
                        json.dumps(
                            {
                                "proposal": {
                                    "failure_kind": kind,
                                    "target_task": target,
                                    "errors": ["Syntax preflight failed."],
                                }
                            }
                        )
                        + "\n"
                    )

            self.assertTrue(
                should_block_task_before_llm(
                    Config(repo_root=repo, max_task_failures_before_block=3),
                    target,
                )
            )
            self.assertFalse(
                should_block_task_before_llm(
                    Config(repo_root=repo, max_task_failures_before_block=3),
                    "Task checkbox-243: Add attended Playwright runner.",
                )
            )

    def test_repeated_llm_terminations_block_before_next_llm(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = "Task checkbox-446: Add supervisor circuit-breaker recovery coverage."
            for message in ("llm_router child exited with code -15:", "143"):
                with (daemon_dir / "ppd-daemon.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(
                        json.dumps(
                            {
                                "proposal": {
                                    "failure_kind": "llm",
                                    "target_task": target,
                                    "errors": [message],
                                }
                            }
                        )
                        + "\n"
                    )

            self.assertTrue(
                should_block_task_before_llm(
                    Config(repo_root=repo, max_task_failures_before_block=3),
                    target,
                )
            )
            self.assertFalse(
                should_block_task_before_llm(
                    Config(repo_root=repo, max_task_failures_before_block=3),
                    "Task checkbox-447: Add daemon circuit-breaker resume coverage.",
                )
            )

    def test_daemon_parks_repeated_llm_termination_task_without_calling_llm(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = "Task checkbox-446: Add supervisor circuit-breaker recovery coverage."
            (daemon_dir / "task-board.md").write_text(
                f"- [ ] {target}\n"
                "- [ ] Task checkbox-447: Add daemon circuit-breaker resume coverage.\n",
                encoding="utf-8",
            )
            for message in ("llm_router child exited with code -15:", "143"):
                with (daemon_dir / "ppd-daemon.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(
                        json.dumps(
                            {
                                "proposal": {
                                    "failure_kind": "llm",
                                    "target_task": target,
                                    "errors": [message],
                                }
                            }
                        )
                        + "\n"
                    )
            daemon = Daemon(Config(repo_root=repo, apply=True))

            proposal = daemon.run_cycle()
            board = (daemon_dir / "task-board.md").read_text(encoding="utf-8")
            progress = json.loads((daemon_dir / "progress.json").read_text(encoding="utf-8"))

        self.assertEqual("llm_termination", proposal.failure_kind)
        self.assertIn(f"- [!] {target}", board)
        self.assertIn("- [ ] Task checkbox-447: Add daemon circuit-breaker resume coverage.", board)
        self.assertEqual("llm_termination", progress["latest"]["failure_kind"])

    def test_revisit_blocked_skips_task_with_repeated_llm_terminations(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = "Task checkbox-241: Add a supervised live whole-site public crawl runner."
            for message in ("llm_router child exited with code -15:", "143"):
                with (daemon_dir / "ppd-daemon.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(
                        json.dumps(
                            {
                                "proposal": {
                                    "failure_kind": "llm",
                                    "target_task": target,
                                    "errors": [message],
                                }
                            }
                        )
                        + "\n"
                    )
            board = (
                "- [!] Task checkbox-241: Add a supervised live whole-site public crawl runner.\n"
                "- [!] Task checkbox-242: Add processor-suite execution integration.\n"
            )

            selected = select_task_for_config(
                parse_tasks(board),
                Config(repo_root=repo, revisit_blocked=True),
            )

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(242, selected.checkbox_id)

    def test_revisit_blocked_returns_no_eligible_when_all_blocked_tasks_are_suppressed(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = "Task checkbox-241: Add a supervised live whole-site public crawl runner."
            (daemon_dir / "task-board.md").write_text(
                "- [!] Task checkbox-241: Add a supervised live whole-site public crawl runner.\n",
                encoding="utf-8",
            )
            for message in ("llm_router child exited with code -15:", "143"):
                with (daemon_dir / "ppd-daemon.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(
                        json.dumps(
                            {
                                "proposal": {
                                    "failure_kind": "llm",
                                    "target_task": target,
                                    "errors": [message],
                                }
                            }
                        )
                        + "\n"
                    )
            daemon = Daemon(Config(repo_root=repo, apply=True, revisit_blocked=True))

            proposal = daemon.run_cycle()

        self.assertEqual("no_eligible_tasks", proposal.failure_kind)

    def test_llm_timeout_cleanup_terminates_descendant_processes(self) -> None:
        process = subprocess.Popen(
            ["bash", "-lc", "setsid sleep 30 & echo $!; wait"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        assert process.stdout is not None
        child_pid = int(process.stdout.readline().strip())

        terminate_process_group(process, grace_seconds=0.2)
        time.sleep(0.1)

        self.assertIsNotNone(process.poll())
        with self.assertRaises(ProcessLookupError):
            os.kill(child_pid, 0)

    def test_daemon_run_records_cycle_exception_without_raising(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "task-board.md").write_text(
                "- [ ] Task checkbox-1: Synthetic task.\n",
                encoding="utf-8",
            )
            daemon = Daemon(
                Config(
                    repo_root=repo,
                    apply=True,
                    watch=True,
                    iterations=1,
                    crash_backoff_seconds=0,
                )
            )

            def crash_once() -> Proposal:
                raise RuntimeError("synthetic daemon cycle crash")

            daemon.run_cycle = crash_once  # type: ignore[method-assign]
            proposals = daemon.run()

            status = json.loads((daemon_dir / "status.json").read_text(encoding="utf-8"))
            rows = [json.loads(line) for line in (daemon_dir / "ppd-daemon.jsonl").read_text(encoding="utf-8").splitlines()]

        self.assertEqual(1, len(proposals))
        self.assertEqual("daemon_exception", proposals[0].failure_kind)
        self.assertEqual("cycle_exception", status["state"])
        self.assertEqual("cycle_exception", rows[0]["stage"])
        self.assertIn("synthetic daemon cycle crash", rows[0]["diagnostic"]["errors"][0])

    def test_daemon_watch_continues_after_contained_cycle_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "task-board.md").write_text(
                "- [ ] Task checkbox-1: Synthetic task.\n",
                encoding="utf-8",
            )
            daemon = Daemon(
                Config(
                    repo_root=repo,
                    apply=True,
                    watch=True,
                    iterations=2,
                    crash_backoff_seconds=0,
                )
            )
            calls = 0

            def flaky_cycle() -> Proposal:
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise RuntimeError("synthetic first cycle crash")
                return Proposal(
                    summary="Recovered cycle.",
                    applied=True,
                    dry_run=False,
                    validation_results=[CommandResult(("true",), 0, "", "")],
                )

            daemon.run_cycle = flaky_cycle  # type: ignore[method-assign]
            proposals = daemon.run()

        self.assertEqual(2, len(proposals))
        self.assertEqual("daemon_exception", proposals[0].failure_kind)
        self.assertTrue(proposals[1].valid)


if __name__ == "__main__":
    unittest.main()
