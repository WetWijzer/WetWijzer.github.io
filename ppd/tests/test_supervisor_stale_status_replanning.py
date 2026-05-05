from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
import os
import signal
from pathlib import Path

import ppd.daemon.ppd_supervisor as supervisor
from ppd.daemon.ppd_daemon import atomic_write_json
from ppd.daemon.ppd_supervisor import (
    AUTONOMOUS_EXECUTION_CAPABILITY_TITLES,
    CIRCUIT_BREAKER_RECOVERY_TITLES,
    SupervisorConfig,
    append_circuit_breaker_recovery_tasks,
    append_jsonl,
    builtin_autonomous_execution_goal_repair_task_board,
    builtin_autonomous_execution_replenish_task_board,
    build_supervisor_prompt,
    builtin_blocked_cascade_replenish_task_board,
    builtin_dead_worker_task_board,
    builtin_repair_task_board,
    builtin_stalled_worker_task_board,
    diagnose,
    read_supervisor_result_rows,
    should_escalate_stale_platform_slice,
    supervisor_daemon_config,
)


class SupervisorStaleStatusReplanningTest(unittest.TestCase):
    def test_completed_board_with_no_eligible_status_plans_next_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            board = repo / "ppd" / "daemon" / "task-board.md"
            board.parent.mkdir(parents=True)
            board.write_text("- [x] Task checkbox-1: Done.\n", encoding="utf-8")
            atomic_write_json(
                repo / "ppd" / "daemon" / "status.json",
                {
                    "updated_at": "2026-05-02T00:00:00Z",
                    "active_state": "no_eligible_tasks",
                    "state": "no_eligible_tasks",
                },
            )
            atomic_write_json(
                repo / "ppd" / "daemon" / "progress.json",
                {"latest": {"failure_kind": "no_eligible_tasks"}},
            )

            decision = diagnose(SupervisorConfig(repo_root=repo))

        self.assertEqual("plan_next_tasks", decision.action)
        self.assertTrue(decision.should_invoke_codex)

    def test_blocked_only_board_with_no_eligible_status_plans_fresh_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            board = repo / "ppd" / "daemon" / "task-board.md"
            board.parent.mkdir(parents=True)
            board.write_text(
                "- [!] Task checkbox-241: Add a supervised live whole-site public crawl runner.\n",
                encoding="utf-8",
            )
            atomic_write_json(
                repo / "ppd" / "daemon" / "status.json",
                {
                    "updated_at": "2026-05-02T00:00:00Z",
                    "active_state": "no_eligible_tasks",
                    "state": "no_eligible_tasks",
                },
            )
            atomic_write_json(
                repo / "ppd" / "daemon" / "progress.json",
                {"latest": {"failure_kind": "no_eligible_tasks"}},
            )

            decision = diagnose(SupervisorConfig(repo_root=repo))

        self.assertEqual("plan_next_tasks", decision.action)
        self.assertIn("no eligible unblocked tasks", decision.reason)

    def test_blocked_only_no_eligible_status_respects_termination_storm_breaker(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = "Task checkbox-241: Add a supervised live whole-site public crawl runner."
            (daemon_dir / "task-board.md").write_text(f"- [!] {target}\n", encoding="utf-8")
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-02T00:00:00Z",
                    "active_state": "no_eligible_tasks",
                    "state": "no_eligible_tasks",
                },
            )
            atomic_write_json(
                daemon_dir / "progress.json",
                {"latest": {"failure_kind": "no_eligible_tasks"}},
            )
            for _ in range(8):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "proposal": {
                            "failure_kind": "llm",
                            "target_task": target,
                            "errors": ["llm_router child exited with code -15:"],
                        }
                    },
                )

            decision = diagnose(SupervisorConfig(repo_root=repo, termination_storm_threshold=8))

        self.assertEqual("enter_termination_storm_circuit_breaker", decision.action)

    def test_completed_board_with_stale_calling_llm_status_plans_next_tasks_first(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            board = repo / "ppd" / "daemon" / "task-board.md"
            board.parent.mkdir(parents=True)
            board.write_text("- [x] Task checkbox-1: Done.\n", encoding="utf-8")
            atomic_write_json(
                repo / "ppd" / "daemon" / "status.json",
                {
                    "updated_at": "2026-05-02T00:00:00Z",
                    "active_state": "calling_llm",
                    "active_state_started_at": "2026-05-02T00:00:00Z",
                    "active_target_task": "Task checkbox-1: Done.",
                },
            )

            decision = diagnose(SupervisorConfig(repo_root=repo))

        self.assertEqual("plan_next_tasks", decision.action)
        self.assertIn("all PP&D daemon tasks are complete", decision.reason)

    def test_dead_worker_calling_llm_status_resets_in_progress_task_before_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            board = repo / "ppd" / "daemon" / "task-board.md"
            board.parent.mkdir(parents=True)
            board.write_text(
                "- [~] Task checkbox-160: Add supervisor task-board de-duplication coverage.\n"
                "- [ ] Task checkbox-161: Add daemon stale-worker recovery coverage.\n",
                encoding="utf-8",
            )
            atomic_write_json(
                repo / "ppd" / "daemon" / "status.json",
                {
                    "updated_at": "2026-05-03T00:00:00Z",
                    "active_state": "calling_llm",
                    "active_state_started_at": "2026-05-03T00:00:00Z",
                    "active_target_task": "Task checkbox-160: Add supervisor task-board de-duplication coverage.",
                    "pid": 99999999,
                },
            )

            decision = diagnose(SupervisorConfig(repo_root=repo, pid_file=Path("ppd/daemon/missing.pid")))
            repaired, reset = builtin_dead_worker_task_board(
                board.read_text(encoding="utf-8"),
                "Task checkbox-160: Add supervisor task-board de-duplication coverage.",
            )

        self.assertEqual("reconcile_dead_worker_and_restart", decision.action)
        self.assertTrue(decision.should_restart_daemon)
        self.assertEqual(("Add supervisor task-board de-duplication coverage.",), reset)
        self.assertIn("- [ ] Task checkbox-160: Add supervisor task-board de-duplication coverage.", repaired)
        self.assertNotIn("- [~] Task checkbox-160", repaired)

    def test_dead_worker_with_already_parked_active_target_restarts_on_next_task(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            board = repo / "ppd" / "daemon" / "task-board.md"
            board.parent.mkdir(parents=True)
            active_target = "Task checkbox-225: Add autonomous platform continuation coverage for tranche 2 proving whole-site archival, Playwright draft automation, PDF field filling, and formal-logic outputs stay connected through source evidence IDs."
            next_target = "Task checkbox-241: Add a supervised live whole-site public crawl runner under ppd/crawler."
            board.write_text(
                "- [!] " + active_target + "\n"
                "- [ ] " + next_target + "\n",
                encoding="utf-8",
            )
            atomic_write_json(
                repo / "ppd" / "daemon" / "status.json",
                {
                    "updated_at": "2026-05-03T00:00:00Z",
                    "active_state": "calling_llm",
                    "active_state_started_at": "2026-05-03T00:00:00Z",
                    "active_target_task": active_target,
                },
            )

            decision = diagnose(SupervisorConfig(repo_root=repo, pid_file=Path("ppd/daemon/missing.pid")))

        self.assertEqual("restart_daemon", decision.action)
        self.assertTrue(decision.should_restart_daemon)
        self.assertIn(next_target, decision.reason)

    def test_repeated_durable_parse_diagnostics_trigger_deterministic_parking_before_restart_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "task-board.md").write_text(
                "- [~] Task checkbox-160: Add supervisor task-board de-duplication coverage.\n",
                encoding="utf-8",
            )
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-03T00:00:00Z",
                    "active_state": "calling_llm",
                    "active_target_task": "Task checkbox-160: Add supervisor task-board de-duplication coverage.",
                },
            )
            for _ in range(3):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "parse",
                            "target_task": "Task checkbox-160: Add supervisor task-board de-duplication coverage.",
                            "errors": ["LLM response did not contain a JSON object."],
                        },
                    },
                )

            rows = read_supervisor_result_rows(daemon_dir / "ppd-daemon.jsonl")
            decision = diagnose(SupervisorConfig(repo_root=repo, pid_file=Path("ppd/daemon/missing.pid")))

        self.assertEqual(3, len(rows))
        self.assertEqual("reconcile_repeated_llm_loop_and_restart", decision.action)
        self.assertFalse(decision.should_invoke_codex)
        self.assertTrue(decision.should_restart_daemon)
        self.assertIn("durable LLM parse/runtime diagnostics", decision.reason)

    def test_repeated_parse_diagnostics_for_blocked_task_do_not_interrupt_current_work(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            current = (
                "Task checkbox-242: Add processor-suite execution integration under ppd/crawler "
                "proving public PP&D pages and PDFs flow through archive manifests."
            )
            blocked = (
                "Task checkbox-241: Add a supervised live whole-site public crawl runner "
                "under ppd/crawler."
            )
            (daemon_dir / "task-board.md").write_text(
                f"- [!] {blocked}\n"
                f"- [~] {current}\n"
                "- [ ] Task checkbox-243: Add attended Playwright runner.\n",
                encoding="utf-8",
            )
            (daemon_dir / "ppd-daemon.pid").write_text(str(os.getpid()), encoding="utf-8")
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": now,
                    "active_state": "calling_llm",
                    "active_state_started_at": now,
                    "active_target_task": current,
                },
            )
            for _ in range(3):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": blocked,
                            "errors": ["llm_router child timed out after 90 seconds"],
                        },
                    },
                )

            decision = diagnose(SupervisorConfig(repo_root=repo))

        self.assertEqual("observe", decision.action)
        self.assertNotIn("durable LLM parse/runtime diagnostics", decision.reason)

    def test_repeated_llm_diagnostics_do_not_stop_fresh_active_worker(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            current = "Task checkbox-225: Add autonomous platform continuation coverage."
            (daemon_dir / "task-board.md").write_text(
                "- [~] Task checkbox-225: Add autonomous platform continuation coverage.\n"
                "- [ ] Task checkbox-226: Add follow-up platform coverage.\n",
                encoding="utf-8",
            )
            (daemon_dir / "ppd-daemon.pid").write_text(str(os.getpid()), encoding="utf-8")
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": now,
                    "active_state": "calling_llm",
                    "active_state_started_at": now,
                    "active_target_task": current,
                },
            )
            for _ in range(4):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": current,
                            "errors": ["llm_router child exited with code -15:"],
                        },
                    },
                )

            decision = diagnose(SupervisorConfig(repo_root=repo))

        self.assertEqual("observe", decision.action)
        self.assertFalse(decision.should_restart_daemon)
        self.assertIn("actively working", decision.reason)

    def test_termination_storm_trips_circuit_breaker_before_blocked_cascade_growth(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "task-board.md").write_text(
                "- [!] Task checkbox-430: Blocked repair task one.\n"
                "- [!] Task checkbox-431: Blocked repair task two.\n",
                encoding="utf-8",
            )
            targets = [
                "Task checkbox-430: Blocked repair task one.",
                "Task checkbox-431: Blocked repair task two.",
                "Task checkbox-430: Blocked repair task one.",
                "Task checkbox-431: Blocked repair task two.",
            ]
            for target in targets:
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": target,
                            "errors": ["llm_router child exited with code -15:"],
                        },
                    },
                )

            decision = diagnose(
                SupervisorConfig(
                    repo_root=repo,
                    pid_file=Path("ppd/daemon/missing.pid"),
                    termination_storm_threshold=4,
                )
            )

        self.assertEqual("enter_termination_storm_circuit_breaker", decision.action)
        self.assertFalse(decision.should_restart_daemon)
        self.assertIn("termination storm", decision.reason)

    def test_run_once_writes_circuit_breaker_without_validation_restart_or_board_growth(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            board = "- [!] Task checkbox-430: Blocked repair task one.\n"
            (daemon_dir / "task-board.md").write_text(board, encoding="utf-8")
            for _ in range(4):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": "Task checkbox-430: Blocked repair task one.",
                            "errors": ["143"],
                        },
                    },
                )
            config = SupervisorConfig(
                repo_root=repo,
                pid_file=Path("ppd/daemon/missing.pid"),
                apply=True,
                restart_daemon=False,
                termination_storm_threshold=4,
            )

            decision = supervisor.run_once(config)
            breaker = json.loads((daemon_dir / "supervisor-circuit-breaker.json").read_text(encoding="utf-8"))
            status = json.loads((daemon_dir / "supervisor-status.json").read_text(encoding="utf-8"))
            final_board = (daemon_dir / "task-board.md").read_text(encoding="utf-8")

        self.assertEqual("enter_termination_storm_circuit_breaker", decision.action)
        self.assertEqual("termination_storm_circuit_breaker", breaker["repairKind"])
        self.assertEqual(board, final_board)
        self.assertEqual("termination_storm", status["proposal"]["failure_kind"])
        self.assertEqual([], status["proposal"]["validation_results"])

    def test_termination_storm_quarantines_open_generated_tasks_and_pauses_status(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            open_one = (
                "Add generated blocked-cascade daemon-repair coverage for tranche 50 item 2 proving "
                "blocked PP&D work stays parked until a fresh daemon repair task validates."
            )
            open_two = (
                "Add generated blocked-cascade daemon-repair coverage for tranche 50 item 3 proving "
                "blocked PP&D work stays parked until a fresh daemon repair task validates."
            )
            parked = (
                "Add generated blocked-cascade daemon-repair coverage for tranche 50 item 4 proving "
                "blocked PP&D work stays parked until a fresh daemon repair task validates."
            )
            (daemon_dir / "task-board.md").write_text(
                f"- [~] Task checkbox-443: {open_one}\n"
                f"- [ ] Task checkbox-444: {open_two}\n"
                f"- [!] Task checkbox-445: {parked}\n",
                encoding="utf-8",
            )
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-04T00:00:00Z",
                    "active_state": "calling_llm",
                    "active_target_task": f"Task checkbox-443: {open_one}",
                },
            )
            for _ in range(4):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": f"Task checkbox-443: {open_one}",
                            "errors": ["llm_router child exited with code -15:"],
                        },
                    },
                )

            decision = supervisor.run_once(
                SupervisorConfig(
                    repo_root=repo,
                    pid_file=Path("ppd/daemon/missing.pid"),
                    apply=True,
                    termination_storm_threshold=4,
                )
            )
            final_board = (daemon_dir / "task-board.md").read_text(encoding="utf-8")
            paused = json.loads((daemon_dir / "status.json").read_text(encoding="utf-8"))
            breaker = json.loads((daemon_dir / "supervisor-circuit-breaker.json").read_text(encoding="utf-8"))

        self.assertEqual("enter_termination_storm_circuit_breaker", decision.action)
        self.assertIn("- [!] Task checkbox-443", final_board)
        self.assertIn("- [!] Task checkbox-444", final_board)
        self.assertIn("Built-In Generated Blocked-Cascade Quarantine Notes", final_board)
        self.assertEqual("paused_by_supervisor_circuit_breaker", paused["active_state"])
        self.assertEqual(["checkbox-443", "checkbox-444"], breaker["quarantinedGeneratedTaskLabels"])

    def test_active_circuit_breaker_observes_without_rewriting(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            now = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
            (daemon_dir / "task-board.md").write_text("- [!] Task checkbox-430: Parked.\n", encoding="utf-8")
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": now.isoformat().replace("+00:00", "Z"),
                    "active_state": "paused_by_supervisor_circuit_breaker",
                },
            )
            atomic_write_json(
                daemon_dir / "supervisor-circuit-breaker.json",
                {
                    "schemaVersion": 1,
                    "createdAt": now.isoformat().replace("+00:00", "Z"),
                    "repairKind": "termination_storm_circuit_breaker",
                },
            )

            decision = diagnose(
                SupervisorConfig(
                    repo_root=repo,
                    pid_file=Path("ppd/daemon/missing.pid"),
                    termination_storm_backoff_seconds=900,
                ),
                now=now,
            )

        self.assertEqual("observe_circuit_breaker", decision.action)
        self.assertFalse(decision.should_restart_daemon)

    def test_expired_circuit_breaker_recovers_with_vetted_non_generated_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            now = datetime(2026, 5, 4, 12, 20, tzinfo=timezone.utc)
            created = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
            (daemon_dir / "task-board.md").write_text(
                "- [!] Task checkbox-430: Blocked repair task one.\n"
                "- [!] Task checkbox-431: Blocked repair task two.\n",
                encoding="utf-8",
            )
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": created.isoformat().replace("+00:00", "Z"),
                    "active_state": "paused_by_supervisor_circuit_breaker",
                },
            )
            atomic_write_json(
                daemon_dir / "supervisor-circuit-breaker.json",
                {
                    "schemaVersion": 1,
                    "createdAt": created.isoformat().replace("+00:00", "Z"),
                    "repairKind": "termination_storm_circuit_breaker",
                },
            )
            for _ in range(4):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": "Task checkbox-430: Blocked repair task one.",
                            "errors": ["llm_router child exited with code -15:"],
                        },
                    },
                )

            decision = diagnose(
                SupervisorConfig(
                    repo_root=repo,
                    pid_file=Path("ppd/daemon/missing.pid"),
                    termination_storm_threshold=4,
                    termination_storm_backoff_seconds=900,
                ),
                now=now,
            )
            repaired, labels = append_circuit_breaker_recovery_tasks(
                (daemon_dir / "task-board.md").read_text(encoding="utf-8")
            )

        self.assertEqual("recover_termination_storm_and_restart", decision.action)
        self.assertTrue(decision.should_restart_daemon)
        self.assertEqual(tuple(f"checkbox-{432 + offset}" for offset in range(4)), labels)
        for title in CIRCUIT_BREAKER_RECOVERY_TITLES:
            self.assertIn(title, repaired)
        self.assertNotIn("generated blocked-cascade daemon-repair", "\n".join(CIRCUIT_BREAKER_RECOVERY_TITLES))

    def test_open_circuit_breaker_recovery_task_restarts_daemon_despite_old_storm(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "task-board.md").write_text(
                f"- [ ] Task checkbox-500: {CIRCUIT_BREAKER_RECOVERY_TITLES[0]}\n"
                "- [!] Task checkbox-501: Blocked old generated task.\n",
                encoding="utf-8",
            )
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-04T12:00:00Z",
                    "active_state": "ready_after_supervisor_circuit_breaker_recovery",
                },
            )
            for _ in range(4):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": "Task checkbox-501: Blocked old generated task.",
                            "errors": ["143"],
                        },
                    },
                )

            decision = diagnose(
                SupervisorConfig(
                    repo_root=repo,
                    pid_file=Path("ppd/daemon/missing.pid"),
                    termination_storm_threshold=4,
                )
            )

        self.assertEqual("restart_daemon", decision.action)
        self.assertTrue(decision.should_restart_daemon)
        self.assertIn("vetted circuit-breaker recovery tasks", decision.reason)

    def test_supervisor_honors_term_when_service_manager_owns_restart_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            config = SupervisorConfig(repo_root=repo, honor_supervisor_term=True)
            original_config = supervisor._WATCH_CONFIG
            supervisor._WATCH_CONFIG = config
            try:
                with self.assertRaises(SystemExit) as raised:
                    supervisor.handle_supervisor_signal(signal.SIGTERM, None)
            finally:
                supervisor._WATCH_CONFIG = original_config

            rows = [
                json.loads(line)
                for line in (repo / "ppd" / "daemon" / "supervisor-actions.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]

        self.assertEqual(143, raised.exception.code)
        self.assertEqual("supervisor_signal_honored", rows[0]["event"])

    def test_supervisor_ignores_incidental_term_without_service_manager_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            config = SupervisorConfig(repo_root=repo, honor_supervisor_term=False)
            original_config = supervisor._WATCH_CONFIG
            supervisor._WATCH_CONFIG = config
            try:
                supervisor.handle_supervisor_signal(signal.SIGTERM, None)
            finally:
                supervisor._WATCH_CONFIG = original_config

            rows = [
                json.loads(line)
                for line in (repo / "ppd" / "daemon" / "supervisor-actions.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]

        self.assertEqual("supervisor_signal_ignored", rows[0]["event"])

    def test_generated_blocked_cascade_budget_exhaustion_trips_breaker_without_more_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            lines = []
            for offset in range(supervisor.MAX_GENERATED_BLOCKED_CASCADE_TASKS):
                lines.append(
                    "- [!] Task checkbox-"
                    f"{300 + offset}: Add generated blocked-cascade daemon-repair coverage for tranche "
                    f"{offset + 1} item 1 proving blocked PP&D work stays parked until a fresh daemon repair task validates."
                )
            board = "\n".join(lines) + "\n"
            (daemon_dir / "task-board.md").write_text(board, encoding="utf-8")

            decision = diagnose(SupervisorConfig(repo_root=repo, pid_file=Path("ppd/daemon/missing.pid")))
            repaired, labels = builtin_blocked_cascade_replenish_task_board(board)

        self.assertEqual("enter_termination_storm_circuit_breaker", decision.action)
        self.assertIn("fallback budget", decision.reason)
        self.assertEqual(board, repaired)
        self.assertEqual((), labels)

    def test_run_once_safely_records_supervisor_exception_without_raising(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            original_diagnose = supervisor.diagnose

            def crash_diagnose(config: SupervisorConfig) -> supervisor.SupervisorDecision:
                raise RuntimeError("synthetic supervisor crash")

            supervisor.diagnose = crash_diagnose  # type: ignore[assignment]
            try:
                decision = supervisor.run_once_safely(SupervisorConfig(repo_root=repo))
            finally:
                supervisor.diagnose = original_diagnose  # type: ignore[assignment]

            status = json.loads((daemon_dir / "supervisor-status.json").read_text(encoding="utf-8"))
            rows = [
                json.loads(line)
                for line in (daemon_dir / "supervisor-actions.jsonl").read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual("supervisor_exception", decision.action)
        self.assertEqual("supervisor_exception", status["decision"]["action"])
        self.assertEqual("supervisor_exception", rows[0]["decision"]["action"])
        self.assertEqual("supervisor_exception", status["proposal"]["failure_kind"])
        self.assertIn("synthetic supervisor crash", status["proposal"]["errors"][0])

    def test_supervisor_validation_does_not_invoke_nested_repair_pass(self) -> None:
        config = supervisor_daemon_config(SupervisorConfig(repo_root=Path("."), self_heal=True))

        self.assertFalse(config.repair_validation_failures)

    def test_archived_task_failures_do_not_trigger_current_board_self_heal(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            current = "Task checkbox-242: Add processor-suite execution integration under ppd/crawler."
            archived = "Task checkbox-215: Add generated blocked-cascade daemon-repair coverage."
            completed = "Task checkbox-172: Add supervisor validation-failure classification coverage."
            (daemon_dir / "task-board.md").write_text(
                f"- [x] {completed}\n"
                f"- [~] {current}\n"
                "- [ ] Task checkbox-243: Add attended Playwright runner.\n",
                encoding="utf-8",
            )
            (daemon_dir / "ppd-daemon.pid").write_text(str(os.getpid()), encoding="utf-8")
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": now,
                    "active_state": "calling_llm",
                    "active_state_started_at": now,
                    "active_target_task": current,
                },
            )
            for _ in range(4):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": archived,
                            "errors": ["llm_router child exited with code -15:"],
                        },
                    },
                )
            for _ in range(3):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": f"Task checkbox-999: {completed}",
                            "errors": ["llm_router child exited with code -15:"],
                        },
                    },
                )

            decision = diagnose(SupervisorConfig(repo_root=repo))

        self.assertEqual("observe", decision.action)
        self.assertFalse(decision.should_invoke_codex)

    def test_repeated_parse_diagnostics_park_stuck_task_in_builtin_repair(self) -> None:
        board = (
            "- [~] Task checkbox-160: Add supervisor task-board de-duplication coverage.\n"
            "- [ ] Task checkbox-161: Add daemon stale-worker recovery coverage.\n"
        )
        rows = [
            {
                "failure_kind": "parse",
                "target_task": "Task checkbox-160: Add supervisor task-board de-duplication coverage.",
                "errors": ["LLM response did not contain a JSON object."],
            }
            for _ in range(3)
        ]

        repaired, parked = builtin_repair_task_board(board, rows)

        self.assertEqual(("Add supervisor task-board de-duplication coverage.",), parked)
        self.assertIn("- [!] Task checkbox-160: Add supervisor task-board de-duplication coverage.", repaired)
        self.assertIn("- [ ] Task checkbox-161: Add daemon stale-worker recovery coverage.", repaired)

    def test_execution_capability_tranche_is_comprehensive_and_unique(self) -> None:
        board = "- [x] Task checkbox-240: Completed attended worker resume validation.\n"

        repaired, labels = builtin_autonomous_execution_replenish_task_board(board)
        repeated, repeated_labels = builtin_autonomous_execution_replenish_task_board(repaired)

        self.assertEqual(tuple(f"checkbox-{number}" for number in range(241, 247)), labels)
        self.assertIn("## Built-In Autonomous PP&D Execution Capability Tranche", repaired)
        for title in AUTONOMOUS_EXECUTION_CAPABILITY_TITLES:
            self.assertIn(title, repaired)
        self.assertIn("supervised live whole-site public crawl runner", repaired)
        self.assertIn("attended Playwright DevHub worker runner", repaired)
        self.assertIn("local PDF draft-fill work queue", repaired)
        self.assertIn("formal-logic guardrail extraction pipeline", repaired)
        self.assertEqual(repaired, repeated)
        self.assertEqual((), repeated_labels)

    def test_stale_platform_slice_detection_requires_new_live_worker_capabilities(self) -> None:
        board = (
            "## Built-In Autonomous PP&D Platform Tranche 2\n\n"
            "- [ ] Task checkbox-225: Add autonomous platform continuation coverage for tranche 2 proving whole-site archival, Playwright draft automation, PDF field filling, and formal-logic outputs stay connected through source evidence IDs.\n"
            "\n## Manual Attended Worker Resume Tranche\n\n"
            "- [x] Task checkbox-240: Add tests proving journal replay rejects later worker events after a step is complete.\n"
        )
        stale_target = "Task checkbox-225: Add autonomous platform continuation coverage for tranche 2 proving whole-site archival, Playwright draft automation, PDF field filling, and formal-logic outputs stay connected through source evidence IDs."
        unrelated_target = "Task checkbox-226: Add processor-suite integration planning for tranche 2."

        self.assertTrue(should_escalate_stale_platform_slice(board, stale_target))
        self.assertFalse(should_escalate_stale_platform_slice(board, unrelated_target))
        self.assertFalse(should_escalate_stale_platform_slice("- [ ] Task checkbox-225: old task.\n", stale_target))

    def test_platform_stall_repair_parks_stale_small_slice_and_appends_execution_work(self) -> None:
        board = (
            "## Built-In Autonomous PP&D Platform Tranche 2\n\n"
            "- [~] Task checkbox-225: Add autonomous platform continuation coverage for tranche 2 proving whole-site archival, Playwright draft automation, PDF field filling, and formal-logic outputs stay connected through source evidence IDs.\n"
            "- [ ] Task checkbox-226: Add processor-suite integration planning for tranche 2 proving PP&D public documents flow through archive manifests, normalized document records, PDF metadata, and requirement batches before agents use them.\n"
            "- [ ] Task checkbox-227: Add Playwright/PDF handoff validation for tranche 2 proving redacted user facts can fill draft fields and PDF previews while official DevHub transitions stay behind exact confirmation checkpoints.\n"
            "- [ ] Task checkbox-228: Add supervisor idle-recovery validation for tranche 2 proving completed boards synthesize new goal-aligned platform tasks without sleeping, duplicate tranche reuse, or blocked-task retry churn.\n"
            "\n## Manual Live Execution Boundary Tranche\n\n"
            "- [x] Task checkbox-229: Add bounded live public scrape execution.\n"
            "\n## Manual Attended Worker Resume Tranche\n\n"
            "- [x] Task checkbox-240: Add tests proving journal replay rejects later worker events after a step is complete.\n"
        )
        target = "Task checkbox-225: Add autonomous platform continuation coverage for tranche 2 proving whole-site archival, Playwright draft automation, PDF field filling, and formal-logic outputs stay connected through source evidence IDs."

        repaired, parked, replenished = builtin_autonomous_execution_goal_repair_task_board(board, target)

        self.assertIn("- [!] Task checkbox-225:", repaired)
        self.assertIn("- [!] Task checkbox-226:", repaired)
        self.assertIn("- [!] Task checkbox-227:", repaired)
        self.assertIn("- [!] Task checkbox-228:", repaired)
        self.assertIn("## Built-In Autonomous PP&D Execution Capability Tranche", repaired)
        self.assertIn("Built-In Autonomous Execution Supersession Notes", repaired)
        self.assertEqual(("checkbox-226", "checkbox-227", "checkbox-228"), parked)
        self.assertEqual(tuple(f"checkbox-{number}" for number in range(241, 247)), replenished)

    def test_compact_supervisor_repair_prompt_omits_failed_manifest_dump(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            failed_dir = daemon_dir / "failed-patches"
            failed_dir.mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / "docs" / "PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md").write_text(
                "Plan\n" + ("long plan\n" * 1000),
                encoding="utf-8",
            )
            (daemon_dir / "task-board.md").write_text(
                "- [~] Task checkbox-168: Add prompt-budget enforcement.\n",
                encoding="utf-8",
            )
            (daemon_dir / "ppd_daemon.py").write_text("# daemon excerpt\n" + ("x = 1\n" * 1000), encoding="utf-8")
            (daemon_dir / "ppd_supervisor.py").write_text("# supervisor excerpt\n" + ("y = 1\n" * 1000), encoding="utf-8")
            (failed_dir / "huge.json").write_text("FAILED_MANIFEST_SHOULD_NOT_APPEAR\n" * 1000, encoding="utf-8")
            decision = diagnose(SupervisorConfig(repo_root=repo, pid_file=Path("ppd/daemon/missing.pid")))
            decision = type(decision)(
                action="repair_daemon_programming",
                reason="3 recent durable LLM parse/runtime diagnostics were recorded for the same task before the daemon exited",
                severity="warning",
                should_invoke_codex=True,
                should_restart_daemon=True,
            )

            prompt = build_supervisor_prompt(SupervisorConfig(repo_root=repo, max_repair_prompt_chars=7000), decision)

        self.assertLessEqual(len(prompt), 7015)
        self.assertIn("compact repair prompt", prompt)
        self.assertIn("Recent daemon results", prompt)
        self.assertIn("task-board-summary", prompt)
        self.assertNotIn("FAILED_MANIFEST_SHOULD_NOT_APPEAR", prompt)

    def test_running_worker_stalled_in_calling_llm_gets_deterministic_restart_decision(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            board = repo / "ppd" / "daemon" / "task-board.md"
            board.parent.mkdir(parents=True)
            board.write_text(
                "- [~] Task checkbox-200: Add stalled worker coverage.\n",
                encoding="utf-8",
            )
            atomic_write_json(
                repo / "ppd" / "daemon" / "status.json",
                {
                    "updated_at": "2026-05-03T00:10:00Z",
                    "active_state": "calling_llm",
                    "active_state_started_at": "2026-05-03T00:00:00Z",
                    "active_target_task": "Task checkbox-200: Add stalled worker coverage.",
                },
            )
            pid_file = repo / "ppd" / "daemon" / "ppd-daemon.pid"
            pid_file.write_text(str(os.getpid()), encoding="utf-8")

            decision = diagnose(
                SupervisorConfig(
                    repo_root=repo,
                    active_state_timeout_seconds=60,
                ),
                now=datetime(2026, 5, 3, 0, 2, 1, tzinfo=timezone.utc),
            )

        self.assertEqual("reconcile_stalled_worker_and_restart", decision.action)
        self.assertFalse(decision.should_invoke_codex)
        self.assertTrue(decision.should_restart_daemon)

    def test_stalled_worker_repair_parks_in_progress_task_instead_of_resetting(self) -> None:
        board = (
            "- [~] Task checkbox-200: Add stalled worker coverage.\n"
            "- [ ] Task checkbox-201: Add next independent task.\n"
        )

        repaired, parked = builtin_stalled_worker_task_board(
            board,
            "Task checkbox-200: Add stalled worker coverage.",
        )

        self.assertEqual(("Add stalled worker coverage.",), parked)
        self.assertIn("- [!] Task checkbox-200: Add stalled worker coverage.", repaired)
        self.assertIn("- [ ] Task checkbox-201: Add next independent task.", repaired)
        self.assertIn("Parked stalled worker task", repaired)

    def test_dead_worker_with_recent_failure_parks_instead_of_resets(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = "Task checkbox-300: Add dead worker recent failure coverage."
            (daemon_dir / "task-board.md").write_text(
                "- [~] Task checkbox-300: Add dead worker recent failure coverage.\n"
                "- [ ] Task checkbox-301: Add next independent task.\n",
                encoding="utf-8",
            )
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-03T00:00:00Z",
                    "active_state": "calling_llm",
                    "active_target_task": target,
                },
            )
            append_jsonl(
                daemon_dir / "ppd-daemon.jsonl",
                {
                    "stage": "before_validation",
                    "diagnostic": {
                        "failure_kind": "llm",
                        "target_task": target,
                        "errors": ["llm_router child exited with code -15:"],
                    },
                },
            )

            decision = diagnose(SupervisorConfig(repo_root=repo, pid_file=Path("ppd/daemon/missing.pid")))

        self.assertEqual("reconcile_dead_worker_with_recent_failures_and_restart", decision.action)
        self.assertFalse(decision.should_invoke_codex)
        self.assertTrue(decision.should_restart_daemon)

    def test_blocked_cascade_appends_deterministic_repair_tasks_without_llm(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            board_path = repo / "ppd" / "daemon" / "task-board.md"
            board_path.parent.mkdir(parents=True)
            board = (
                "- [!] Task checkbox-178: Blocked domain task.\n"
                "- [!] Task checkbox-182: Blocked daemon diagnostics task.\n"
            )
            board_path.write_text(board, encoding="utf-8")

            decision = diagnose(SupervisorConfig(repo_root=repo, pid_file=Path("ppd/daemon/missing.pid")))
            repaired, labels = builtin_blocked_cascade_replenish_task_board(board)

        self.assertEqual("reconcile_blocked_cascade_and_restart", decision.action)
        self.assertFalse(decision.should_invoke_codex)
        self.assertTrue(decision.should_restart_daemon)
        self.assertEqual(("checkbox-183", "checkbox-184", "checkbox-185", "checkbox-186"), labels)
        self.assertIn("Built-In Blocked Cascade Recovery Tranche", repaired)
        self.assertIn("blocked-cascade recovery coverage", repaired)
        self.assertIn("- [!] Task checkbox-178: Blocked domain task.", repaired)


if __name__ == "__main__":
    unittest.main()
