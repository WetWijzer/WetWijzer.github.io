from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
import os
import signal
import subprocess
from pathlib import Path

import ppd.daemon.ppd_supervisor as supervisor
from ppd.daemon.deterministic_fallback import deterministic_task_fallback_kind
from ppd.daemon.ppd_daemon import atomic_write_json
from ppd.daemon.task_board import parse_tasks
from ppd.daemon.ppd_supervisor import (
    AUTONOMOUS_EXECUTION_CAPABILITY_TITLES,
    CIRCUIT_BREAKER_RECOVERY_CONTINUATION_TITLES,
    CIRCUIT_BREAKER_RECOVERY_TITLES,
    SupervisorConfig,
    append_circuit_breaker_recovery_tasks,
    append_jsonl,
    builtin_autonomous_execution_goal_repair_task_board,
    builtin_autonomous_execution_replenish_task_board,
    build_supervisor_prompt,
    builtin_blocked_cascade_replenish_task_board,
    builtin_dead_worker_task_board,
    builtin_replenish_goal_tasks,
    builtin_repair_task_board,
    builtin_stalled_worker_task_board,
    diagnose,
    read_supervisor_result_rows,
    should_escalate_stale_platform_slice,
    supervisor_daemon_config,
)


class SupervisorStaleStatusReplanningTest(unittest.TestCase):
    def test_daemon_start_result_is_attached_to_supervisor_proposal(self) -> None:
        proposal = supervisor.Proposal(summary="Synthetic repair.", impact="Validated repair.")
        result = subprocess.CompletedProcess(
            args=["bash", "ppd/daemon/control.sh", "start"],
            returncode=0,
            stdout="PP&D daemon watchdog started: 123\n",
            stderr="",
        )

        supervisor.attach_daemon_start_result(proposal, SupervisorConfig(repo_root=Path(".")), result)

        self.assertIn("Daemon restart result", proposal.impact)
        self.assertEqual(("bash", "ppd/daemon/control.sh", "start"), proposal.validation_results[-1].command)
        self.assertEqual(0, proposal.validation_results[-1].returncode)

    def test_daemon_start_failure_marks_supervisor_proposal_restart_failed(self) -> None:
        proposal = supervisor.Proposal(summary="Synthetic repair.", impact="Validated repair.")
        result = subprocess.CompletedProcess(
            args=["bash", "ppd/daemon/control.sh", "start"],
            returncode=1,
            stdout="",
            stderr="daemon did not start",
        )

        supervisor.attach_daemon_start_result(proposal, SupervisorConfig(repo_root=Path(".")), result)

        self.assertEqual("restart", proposal.failure_kind)
        self.assertIn("daemon restart failed", proposal.errors[-1])
        self.assertEqual(1, proposal.validation_results[-1].returncode)

    def test_stop_daemon_if_running_skips_missing_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            (repo / "ppd" / "daemon").mkdir(parents=True)
            calls = []
            original = supervisor.run_control
            supervisor.run_control = lambda config, command: calls.append(command)  # type: ignore[assignment]
            try:
                result = supervisor.stop_daemon_if_running(SupervisorConfig(repo_root=repo))
            finally:
                supervisor.run_control = original  # type: ignore[assignment]

        self.assertIsNone(result)
        self.assertEqual([], calls)

    def test_watch_loop_uses_fast_followup_after_progress_actions(self) -> None:
        config = SupervisorConfig(repo_root=Path("."), exception_backoff_seconds=7, termination_storm_backoff_seconds=900)
        plan_decision = supervisor.SupervisorDecision(
            action="plan_next_tasks",
            reason="append source-backed continuation",
            severity="warning",
            should_invoke_codex=True,
        )
        restart_decision = supervisor.SupervisorDecision(
            action="observe",
            reason="restart requested by diagnostic",
            severity="warning",
            should_restart_daemon=True,
        )

        self.assertEqual(
            1.0,
            supervisor.supervisor_watch_sleep_seconds(plan_decision, config, interval_seconds=120),
        )
        self.assertEqual(
            1.0,
            supervisor.supervisor_watch_sleep_seconds(restart_decision, config, interval_seconds=120),
        )

    def test_watch_loop_preserves_backoff_and_short_active_observation(self) -> None:
        config = SupervisorConfig(repo_root=Path("."), exception_backoff_seconds=7, termination_storm_backoff_seconds=900)
        exception_decision = supervisor.SupervisorDecision(
            action="supervisor_exception",
            reason="contained exception",
            severity="critical",
        )
        breaker_decision = supervisor.SupervisorDecision(
            action="observe_circuit_breaker",
            reason="storm backoff remains active",
            severity="critical",
        )
        active_decision = supervisor.SupervisorDecision(
            action="observe",
            reason="daemon is actively working in applying_files; defer historical repair decisions",
            severity="info",
        )
        quiet_decision = supervisor.SupervisorDecision(
            action="observe",
            reason="nothing requires repair",
            severity="info",
        )

        self.assertEqual(
            7.0,
            supervisor.supervisor_watch_sleep_seconds(exception_decision, config, interval_seconds=120),
        )
        self.assertEqual(
            900.0,
            supervisor.supervisor_watch_sleep_seconds(breaker_decision, config, interval_seconds=120),
        )
        self.assertEqual(
            5.0,
            supervisor.supervisor_watch_sleep_seconds(active_decision, config, interval_seconds=120),
        )
        self.assertEqual(
            120.0,
            supervisor.supervisor_watch_sleep_seconds(quiet_decision, config, interval_seconds=120),
        )

    def test_supervisor_process_detects_stale_missing_watchdog(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "ppd-supervisor.pid").write_text("99999999\n", encoding="utf-8")
            (daemon_dir / "ppd-supervisor.child.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")

            self.assertTrue(supervisor.supervisor_process_is_superseded(SupervisorConfig(repo_root=repo)))

    def test_direct_supervisor_process_is_not_superseded_when_it_owns_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "ppd-supervisor.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")

            self.assertFalse(supervisor.supervisor_process_is_superseded(SupervisorConfig(repo_root=repo)))

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

    def test_stale_watchdog_pid_with_fresh_active_worker_observes_before_blocked_revisit_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "task-board.md").write_text(
                "- [!] Task checkbox-9350: Add blocked PP&D reassessment coverage.\n",
                encoding="utf-8",
            )
            (daemon_dir / "ppd-daemon.pid").write_text("99999999\n", encoding="utf-8")
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-08T22:36:55Z",
                    "active_state": "calling_llm",
                    "active_state_started_at": "2026-05-08T22:36:55Z",
                    "active_target_task": "Task checkbox-9350: Add blocked PP&D reassessment coverage.",
                    "pid": os.getpid(),
                },
            )
            atomic_write_json(daemon_dir / "progress.json", {"latest": {"failure_kind": "llm"}})

            decision = diagnose(
                SupervisorConfig(
                    repo_root=repo,
                    revisit_blocked_tasks=True,
                    reassess_blocked_llm_termination_gates=True,
                ),
                now=datetime(2026, 5, 8, 22, 37, 5, tzinfo=timezone.utc),
            )

        self.assertEqual("observe", decision.action)
        self.assertFalse(decision.should_restart_daemon)
        self.assertIn("actively working", decision.reason)

    def test_fresh_active_status_without_live_daemon_restarts_blocked_revisit(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "task-board.md").write_text(
                "- [!] Task checkbox-9350: Add blocked PP&D reassessment coverage.\n",
                encoding="utf-8",
            )
            (daemon_dir / "ppd-daemon.pid").write_text("99999999\n", encoding="utf-8")
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-08T22:36:55Z",
                    "active_state": "calling_llm",
                    "active_state_started_at": "2026-05-08T22:36:55Z",
                    "active_target_task": "Task checkbox-9350: Add blocked PP&D reassessment coverage.",
                    "pid": 99999999,
                },
            )
            atomic_write_json(daemon_dir / "progress.json", {"latest": {"failure_kind": "llm"}})

            decision = diagnose(
                SupervisorConfig(
                    repo_root=repo,
                    revisit_blocked_tasks=True,
                    reassess_blocked_llm_termination_gates=True,
                ),
                now=datetime(2026, 5, 8, 22, 37, 5, tzinfo=timezone.utc),
            )

        self.assertEqual("restart_daemon", decision.action)
        self.assertTrue(decision.should_restart_daemon)

    def test_replenishment_reopens_manual_comprehensive_goal_before_generated_continuation(self) -> None:
        board = (
            "## Manual Comprehensive PP&D Goal Handoff Tranche\n\n"
            "- [!] Task checkbox-462: Add a source-backed PP&D surface registry and taxonomy under ppd/sources that covers public Portland.gov pages, public PDFs, DevHub public entry points, authenticated read-only surfaces, reversible draft surfaces, consequential official actions, local PDF previews, and agent-facing guardrail APIs.\n"
            "- [!] Task checkbox-463: Add a PP&D source seed manifest and validation that includes the PP&D landing page, online permitting tools overview, DevHub FAQ, DevHub sign-in guide, DevHub submit-permit guide, permit applications index, Single PDF Process, file naming standards, and DevHub portal URL with crawl policy metadata.\n"
            "- [!] Task checkbox-464: Add a public crawl frontier contract that enforces Portland.gov and DevHub allowlists, robots preflight, bounded retries, content-type decisions, redirect recording, skipped reasons, and no raw body or downloaded-document persistence.\n"
            "- [!] Task checkbox-465: Add processor-suite archival integration work under ppd/crawler proving PP&D public pages and PDFs hand off to ipfs_datasets_py processor records with archive manifest IDs, content hashes, normalized document IDs, and formal-logic source evidence IDs.\n"
            "- [!] Task checkbox-466: Add a public PDF and form inventory extractor for PP&D applications, handouts, Single PDF guidance, file naming standards, checklist PDFs, and fillable form metadata without storing downloaded raw documents.\n"
            "\n## Built-In Source-Backed Execution Continuation Tranche\n\n"
            "- [x] Task checkbox-490: Add autonomous platform continuation coverage for tranche 4 proving whole-site archival, Playwright draft automation, PDF field filling, and formal-logic outputs stay connected through source evidence IDs.\n"
        )

        repaired, labels = builtin_replenish_goal_tasks(board)

        self.assertEqual(("checkbox-462", "checkbox-463", "checkbox-464", "checkbox-465"), labels)
        self.assertIn("- [ ] Task checkbox-462:", repaired)
        self.assertIn("- [!] Task checkbox-466:", repaired)
        self.assertIn("Built-In Manual Goal Reopen Notes", repaired)
        self.assertNotIn("Built-In Source-Backed Execution Continuation Tranche 2", repaired)

    def test_reopened_manual_comprehensive_goal_tasks_have_deterministic_fallbacks(self) -> None:
        board = (
            "- [ ] Task checkbox-462: Add a source-backed PP&D surface registry and taxonomy under ppd/sources that covers public Portland.gov pages, public PDFs, DevHub public entry points, authenticated read-only surfaces, reversible draft surfaces, consequential official actions, local PDF previews, and agent-facing guardrail APIs.\n"
            "- [ ] Task checkbox-463: Add a PP&D source seed manifest and validation that includes the PP&D landing page, online permitting tools overview, DevHub FAQ, DevHub sign-in guide, DevHub submit-permit guide, permit applications index, Single PDF Process, file naming standards, and DevHub portal URL with crawl policy metadata.\n"
            "- [ ] Task checkbox-464: Add a public crawl frontier contract that enforces Portland.gov and DevHub allowlists, robots preflight, bounded retries, content-type decisions, redirect recording, skipped reasons, and no raw body or downloaded-document persistence.\n"
            "- [ ] Task checkbox-465: Add processor-suite archival integration work under ppd/crawler proving PP&D public pages and PDFs hand off to ipfs_datasets_py processor records with archive manifest IDs, content hashes, normalized document IDs, and formal-logic source evidence IDs.\n"
        )

        kinds = [deterministic_task_fallback_kind(task) for task in parse_tasks(board)]

        self.assertEqual(
            [
                "surface_registry_taxonomy",
                "source_seed_manifest",
                "public_crawl_frontier",
                "processor_archival_integration",
            ],
            kinds,
        )

    def test_completed_execution_capability_board_observes_instead_of_generating_more_platform_tranches(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            board = repo / "ppd" / "daemon" / "task-board.md"
            board.parent.mkdir(parents=True)
            board.write_text(
                "## Built-In Autonomous PP&D Execution Capability Tranche\n\n"
                + "\n".join(
                    f"- [x] Task checkbox-{241 + offset}: {title}"
                    for offset, title in enumerate(AUTONOMOUS_EXECUTION_CAPABILITY_TITLES)
                )
                + "\n",
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

            board_text = board.read_text(encoding="utf-8")
            decision = diagnose(SupervisorConfig(repo_root=repo))
            repaired, labels = builtin_autonomous_execution_replenish_task_board(board_text)

        self.assertEqual("observe", decision.action)
        self.assertIn("source-backed tranche", decision.reason)
        self.assertEqual((), labels)
        self.assertEqual(board_text, repaired)

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

    def test_dead_worker_ready_status_clears_stale_active_target(self) -> None:
        previous_status = {
            "active_state": "calling_llm",
            "active_target_task": "Task checkbox-160: Add supervisor task-board de-duplication coverage.",
            "updated_at": "2026-05-03T00:00:00Z",
        }
        decision = supervisor.SupervisorDecision(
            action="reconcile_dead_worker_and_restart",
            reason="daemon process is not running but status is still calling_llm",
            severity="warning",
            should_restart_daemon=True,
        )

        ready = supervisor.build_dead_worker_ready_status(
            "2026-05-03T00:01:00Z",
            previous_status,
            decision,
            ("Add supervisor task-board de-duplication coverage.",),
        )

        self.assertEqual("ready_after_supervisor_dead_worker_repair", ready["active_state"])
        self.assertEqual("ready_after_supervisor_dead_worker_repair", ready["state"])
        self.assertEqual("", ready["active_target_task"])
        self.assertEqual("calling_llm", ready["previous_state"])
        self.assertEqual(previous_status["active_target_task"], ready["previous_target_task"])
        self.assertEqual(["Add supervisor task-board de-duplication coverage."], ready["reset_task_labels"])

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
        self.assertIn("deterministic fixture-only PP&D fallback work is available", decision.reason)

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

        self.assertEqual("restart_daemon", decision.action)
        self.assertIn("deterministic fixture-only PP&D fallback work is available", decision.reason)
        self.assertIn("- [~] Task checkbox-443", final_board)
        self.assertIn("- [ ] Task checkbox-444", final_board)
        self.assertNotIn("Built-In Generated Blocked-Cascade Quarantine Notes", final_board)
        self.assertEqual("calling_llm", paused["active_state"])

    def test_generated_blocked_cascade_quarantine_compacts_notes_without_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            accepted_dir = daemon_dir / "accepted-work"
            accepted_dir.mkdir()
            (accepted_dir / "accepted-work.jsonl").write_text("", encoding="utf-8")
            generated_lines = [
                "- [!] Task checkbox-430: Add generated blocked-cascade daemon-repair coverage for tranche 47 item 1 proving blocked PP&D work stays parked until a fresh daemon repair task validates.",
                "- [ ] Task checkbox-431: Add generated blocked-cascade daemon-repair coverage for tranche 47 item 2 proving blocked PP&D work stays parked until a fresh daemon repair task validates.",
                "- [~] Task checkbox-432: Add generated blocked-cascade daemon-repair coverage for tranche 47 item 3 proving blocked PP&D work stays parked until a fresh daemon repair task validates.",
            ]
            duplicated_notes = (
                "\n\n## Built-In Generated Blocked-Cascade Quarantine Notes\n\n"
                "- stale quarantine note one.\n"
                "\n## Built-In Generated Blocked-Cascade Quarantine Notes\n\n"
                "- stale quarantine note two.\n"
            )
            (daemon_dir / "task-board.md").write_text(
                "\n".join(generated_lines) + duplicated_notes,
                encoding="utf-8",
            )
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-04T00:00:00Z",
                    "active_state": "calling_llm",
                    "active_target_task": (
                        "Task checkbox-431: Add generated blocked-cascade daemon-repair coverage "
                        "for tranche 47 item 2 proving blocked PP&D work stays parked until a fresh daemon repair task validates."
                    ),
                },
            )
            for _ in range(4):
                append_jsonl(
                    daemon_dir / "ppd-daemon.jsonl",
                    {
                        "stage": "before_validation",
                        "diagnostic": {
                            "failure_kind": "llm",
                            "target_task": (
                                "Task checkbox-431: Add generated blocked-cascade daemon-repair coverage "
                                "for tranche 47 item 2 proving blocked PP&D work stays parked until a fresh daemon repair task validates."
                            ),
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
            sidecar_names = sorted(path.name for path in accepted_dir.iterdir())

        self.assertEqual("restart_daemon", decision.action)
        self.assertIn("deterministic fixture-only PP&D fallback work is available", decision.reason)
        self.assertIn("- [ ] Task checkbox-431", final_board)
        self.assertIn("- [~] Task checkbox-432", final_board)
        self.assertEqual(2, final_board.count("## Built-In Generated Blocked-Cascade Quarantine Notes"))
        self.assertIn("stale quarantine note one", final_board)
        self.assertIn("stale quarantine note two", final_board)
        self.assertEqual(["accepted-work.jsonl"], sidecar_names)
        self.assertNotIn(".workspace.json", "\n".join(sidecar_names))
        self.assertNotIn(".diff.txt", "\n".join(sidecar_names))

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

    def test_active_circuit_breaker_restarts_when_deterministic_no_llm_work_is_open(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            now = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
            (daemon_dir / "task-board.md").write_text(
                "- [ ] Task checkbox-455: Add processor-suite integration planning for tranche 4 proving PP&D "
                "public documents flow through archive manifests, normalized document records, PDF metadata, and "
                "requirement batches before agents use them.\n",
                encoding="utf-8",
            )
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": now.isoformat().replace("+00:00", "Z"),
                    "active_state": "paused_by_supervisor_circuit_breaker",
                    "state": "paused_by_supervisor_circuit_breaker",
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

        self.assertEqual("restart_daemon", decision.action)
        self.assertTrue(decision.should_restart_daemon)
        self.assertIn("deterministic fixture-only PP&D fallback work", decision.reason)
        self.assertIn("no-LLM progress path", decision.reason)

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

    def test_recovery_appends_continuation_when_original_recovery_titles_are_closed(self) -> None:
        board = "\n".join(
            f"- [!] Task checkbox-{446 + offset}: {title}"
            for offset, title in enumerate(CIRCUIT_BREAKER_RECOVERY_TITLES)
        ) + "\n"

        repaired, labels = append_circuit_breaker_recovery_tasks(board)

        self.assertEqual(tuple(f"checkbox-{450 + offset}" for offset in range(4)), labels)
        for title in CIRCUIT_BREAKER_RECOVERY_CONTINUATION_TITLES:
            self.assertIn(title, repaired)
        self.assertNotIn("generated blocked-cascade daemon-repair", "\n".join(CIRCUIT_BREAKER_RECOVERY_CONTINUATION_TITLES))

    def test_closed_recovery_tasks_synthesize_source_backed_continuation_before_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            board = (
                "\n".join(
                    f"- [x] Task checkbox-{446 + offset}: {title}"
                    for offset, title in enumerate(CIRCUIT_BREAKER_RECOVERY_TITLES)
                )
                + "\n"
            )
            (daemon_dir / "task-board.md").write_text(board, encoding="utf-8")
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-04T12:00:00Z",
                    "active_state": "paused_by_supervisor_circuit_breaker",
                    "state": "paused_by_supervisor_circuit_breaker",
                },
            )
            atomic_write_json(
                daemon_dir / "supervisor-circuit-breaker.json",
                {
                    "schemaVersion": 1,
                    "createdAt": "2026-05-04T12:00:00Z",
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
                            "target_task": "Task checkbox-446: Closed circuit-breaker task.",
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
                now=datetime(2026, 5, 4, 12, 30, tzinfo=timezone.utc),
            )
            repaired, labels = append_circuit_breaker_recovery_tasks(board)

        self.assertEqual("recover_termination_storm_and_restart", decision.action)
        self.assertTrue(decision.should_restart_daemon)
        self.assertEqual(tuple(f"checkbox-{450 + offset}" for offset in range(4)), labels)
        for title in CIRCUIT_BREAKER_RECOVERY_CONTINUATION_TITLES:
            self.assertIn(title, repaired)
        self.assertIn("source-backed recovery continuation coverage", repaired)
        self.assertNotIn("generated blocked-cascade daemon-repair", repaired)

    def test_parked_generated_budget_replans_to_source_backed_continuation_without_new_breaker(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            generated_repairs = "\n".join(
                "- [!] Task checkbox-{}: Add generated blocked-cascade daemon-repair coverage for tranche {} "
                "item {} proving blocked PP&D work stays parked until a fresh daemon repair task validates.".format(
                    430 + offset,
                    1 + offset // 4,
                    1 + offset % 4,
                )
                for offset in range(16)
            )
            closed_recovery = "\n".join(
                f"- [x] Task checkbox-{450 + offset}: {title}"
                for offset, title in enumerate(CIRCUIT_BREAKER_RECOVERY_CONTINUATION_TITLES)
            )
            board = (
                "## Built-In Autonomous PP&D Platform Tranche\n\n"
                "- [x] Task checkbox-219: Add a side-effect-free whole-site PP&D archival plan under ppd/crawler.\n\n"
                "## Built-In Autonomous PP&D Execution Capability Tranche\n\n"
                "- [!] Task checkbox-241: Add a supervised live whole-site public crawl runner under ppd/crawler.\n"
                "- [!] Task checkbox-242: Add processor-suite execution integration under ppd/crawler.\n\n"
                "## Built-In Blocked Cascade Recovery Tranche\n\n"
                f"{generated_repairs}\n\n"
                "## Built-In Circuit Breaker Recovery Tranche\n\n"
                f"{closed_recovery}\n"
            )
            (daemon_dir / "task-board.md").write_text(board, encoding="utf-8")
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-05T15:00:00Z",
                    "active_state": "paused_by_supervisor_circuit_breaker",
                    "state": "paused_by_supervisor_circuit_breaker",
                },
            )
            atomic_write_json(
                daemon_dir / "supervisor-circuit-breaker.json",
                {
                    "schemaVersion": 1,
                    "createdAt": "2026-05-05T15:00:00Z",
                    "repairKind": "termination_storm_circuit_breaker",
                },
            )

            decision = diagnose(
                SupervisorConfig(
                    repo_root=repo,
                    pid_file=Path("ppd/daemon/missing.pid"),
                    termination_storm_backoff_seconds=900,
                ),
                now=datetime(2026, 5, 5, 15, 5, tzinfo=timezone.utc),
            )
            repaired, labels = supervisor.builtin_replenish_goal_tasks(board, [])

        self.assertEqual("plan_next_tasks", decision.action)
        self.assertTrue(decision.should_invoke_codex)
        self.assertIn("all generated repair tasks are already parked", decision.reason)
        self.assertEqual(tuple(f"checkbox-{454 + offset}" for offset in range(4)), labels)
        self.assertIn("## Built-In Source-Backed Execution Continuation Tranche", repaired)
        self.assertIn("autonomous platform continuation coverage for tranche 1", repaired)
        self.assertIn("processor-suite integration planning for tranche 1", repaired)
        self.assertIn("Playwright/PDF handoff validation for tranche 1", repaired)
        self.assertIn("supervisor idle-recovery validation for tranche 1", repaired)

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

    def test_open_circuit_breaker_continuation_task_restarts_before_generated_budget_breaker(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            generated = "\n".join(
                "- [!] Task checkbox-"
                f"{300 + offset}: Add generated blocked-cascade daemon-repair coverage for tranche "
                f"{offset + 1} item 1 proving blocked PP&D work stays parked until a fresh daemon repair task validates."
                for offset in range(supervisor.MAX_GENERATED_BLOCKED_CASCADE_TASKS)
            )
            (daemon_dir / "task-board.md").write_text(
                generated + f"\n- [ ] Task checkbox-500: {CIRCUIT_BREAKER_RECOVERY_CONTINUATION_TITLES[0]}\n",
                encoding="utf-8",
            )

            decision = diagnose(SupervisorConfig(repo_root=repo, pid_file=Path("ppd/daemon/missing.pid")))

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
            atomic_write_json(
                daemon_dir / "status.json",
                {
                    "updated_at": "2026-05-04T12:00:00Z",
                    "active_state": "no_eligible_tasks",
                    "state": "no_eligible_tasks",
                },
            )
            atomic_write_json(
                daemon_dir / "progress.json",
                {"latest": {"failure_kind": "no_eligible_tasks"}},
            )

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

    def test_run_once_safely_does_not_swallow_system_exit(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            original_diagnose = supervisor.diagnose

            def exit_diagnose(config: SupervisorConfig) -> supervisor.SupervisorDecision:
                raise SystemExit(143)

            supervisor.diagnose = exit_diagnose  # type: ignore[assignment]
            try:
                with self.assertRaises(SystemExit) as raised:
                    supervisor.run_once_safely(SupervisorConfig(repo_root=repo))
            finally:
                supervisor.diagnose = original_diagnose  # type: ignore[assignment]

        self.assertEqual(143, raised.exception.code)

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
