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
    build_deterministic_task_fallback_proposal,
    compact_deterministic_progress_source_payload,
    deterministic_task_fallback_kind,
    failure_block_threshold,
    has_deterministic_task_fallback,
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
        self.assertEqual(1, failure_block_threshold(Proposal(failure_kind="no_visible_source_change"), config))
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

    def test_revisit_blocked_ignore_stale_gates_still_skips_fresh_llm_terminations(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            terminated = "Task checkbox-241: Add a supervised live whole-site public crawl runner."
            syntax_stale = "Task checkbox-242: Add processor-suite execution integration."
            for target, kind, messages in (
                (terminated, "llm", ("llm_router child exited with code -15:", "143")),
                (syntax_stale, "syntax_preflight", ("Syntax preflight failed.", "Syntax preflight failed.")),
            ):
                for message in messages:
                    with (daemon_dir / "ppd-daemon.jsonl").open("a", encoding="utf-8") as handle:
                        handle.write(
                            json.dumps(
                                {
                                    "proposal": {
                                        "failure_kind": kind,
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
                "- [!] Task checkbox-243: Add attended Playwright runner.\n"
            )

            selected = select_task_for_config(
                parse_tasks(board),
                Config(
                    repo_root=repo,
                    revisit_blocked=True,
                    revisit_blocked_ignore_failure_gates=True,
                ),
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

    def test_reassess_blocked_llm_terminations_selects_gated_task(self) -> None:
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
            board = "- [!] Task checkbox-241: Add a supervised live whole-site public crawl runner.\n"

            selected = select_task_for_config(
                parse_tasks(board),
                Config(
                    repo_root=repo,
                    revisit_blocked=True,
                    revisit_blocked_ignore_failure_gates=True,
                    revisit_blocked_reassess_llm_termination_gates=True,
                ),
            )

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(241, selected.checkbox_id)

    def test_reassess_blocked_llm_terminations_spreads_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            noisy_target = "Task checkbox-241: Add a supervised live whole-site public crawl runner."
            quieter_target = "Task checkbox-242: Add processor-suite execution integration."
            for target, messages in (
                (noisy_target, ("llm_router child exited with code -15:", "143", "143")),
                (quieter_target, ("143",)),
            ):
                for message in messages:
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
                Config(
                    repo_root=repo,
                    revisit_blocked=True,
                    revisit_blocked_ignore_failure_gates=True,
                    revisit_blocked_reassess_llm_termination_gates=True,
                ),
            )

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(242, selected.checkbox_id)

    def test_deterministic_platform_task_fallback_builds_progress_manifest_without_llm(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            (repo / "ppd" / "daemon").mkdir(parents=True)
            config = Config(repo_root=repo)
            task = parse_tasks(
                "- [ ] Task checkbox-455: Add processor-suite integration planning for tranche 4 proving PP&D public "
                "documents flow through archive manifests, normalized document records, PDF metadata, and requirement "
                "batches before agents use them.\n"
            )[0]

            proposal = build_deterministic_task_fallback_proposal(config, task)
            assert proposal is not None
            files = {item["path"]: item["content"] for item in proposal.files}
            payload = json.loads(files["ppd/daemon/deterministic-progress.json"])
            source_payload = compact_deterministic_progress_source_payload(payload)
            record = payload["records"][0]

        self.assertTrue(has_deterministic_task_fallback(task))
        self.assertTrue(proposal.trusted_validation_commands)
        self.assertTrue(proposal.requires_visible_source_change)
        self.assertEqual(
            [
                "ppd/platform/__init__.py",
                "ppd/platform/processor_suite_contract.py",
                "ppd/platform/deterministic_fallback_progress.py",
                "ppd/daemon/deterministic-progress.json",
            ],
            [item["path"] for item in proposal.files],
        )
        self.assertIn(
            "processor_suite_planning",
            files["ppd/platform/deterministic_fallback_progress.py"],
        )
        self.assertEqual(1, source_payload["recordCount"])
        self.assertEqual("processor_suite_planning", source_payload["recentRecords"][0]["fallbackKind"])
        self.assertIn(["python3", "ppd/tests/validate_ppd.py"], proposal.validation_commands)
        self.assertEqual(455, record["checkboxId"])
        self.assertEqual("processor_suite_planning", record["fallbackKind"])
        self.assertIn("official_upload", record["blockedActions"])
        self.assertIn("fee_payment", record["blockedActions"])
        self.assertIn("evidence:devhub-faq:2026-05-01", record["sourceEvidenceIds"])
        self.assertFalse(record["runtimePolicy"]["liveCrawlAllowedByDefault"])
        self.assertTrue(record["runtimePolicy"]["requiresHumanAttendanceBeforeBrowserUse"])

    def test_current_source_backed_blocked_tasks_have_deterministic_fallbacks(self) -> None:
        tasks = parse_tasks(
            "- [!] Task checkbox-241: Add a supervised live whole-site public crawl runner under ppd/crawler that resumes an allowlisted PP&D frontier, delegates archival capture to the ipfs_datasets_py processor suite, records robots and content-type decisions, and persists metadata manifests instead of raw bodies or downloaded documents.\n"
            "- [!] Task checkbox-9354: Add a user document-store reconciliation contract that compares known user facts and files to PP&D guardrail bundles, identifies stale or conflicting evidence, and emits the smallest review packet needed before draft automation proceeds.\n"
            "- [!] Task checkbox-9365: Add RequirementNode and ProcessModel schema coverage with citation spans, confidence, human-review status, and representative residential, commercial, trade, correction, inspection, and fee workflow stages.\n"
            "- [!] Task checkbox-262: Add generated blocked-cascade daemon-repair coverage for tranche 5 item 1 proving blocked PP&D work stays parked until a fresh daemon repair task validates.\n"
        )

        self.assertEqual(
            [
                "bounded_live_crawl_dry_run",
                "user_document_gap_analysis",
                "process_requirement_schemas",
                "blocked_cascade_daemon_repair",
            ],
            [deterministic_task_fallback_kind(task) for task in tasks],
        )
        self.assertTrue(all(has_deterministic_task_fallback(task) for task in tasks))

    def test_daemon_completes_deterministic_task_without_calling_llm(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = (
                "Task checkbox-455: Add processor-suite integration planning for tranche 4 proving PP&D public "
                "documents flow through archive manifests, normalized document records, PDF metadata, and requirement "
                "batches before agents use them."
            )
            (daemon_dir / "task-board.md").write_text(f"- [ ] {target}\n", encoding="utf-8")
            daemon = Daemon(
                Config(
                    repo_root=repo,
                    apply=True,
                    validation_commands=(("true",),),
                )
            )

            proposal = daemon.run_cycle()
            board = (daemon_dir / "task-board.md").read_text(encoding="utf-8")
            manifest = json.loads((daemon_dir / "deterministic-progress.json").read_text(encoding="utf-8"))
            source_contract_exists = (repo / "ppd" / "platform" / "processor_suite_contract.py").exists()

        self.assertTrue(proposal.valid)
        self.assertEqual(
            [
                "ppd/platform/__init__.py",
                "ppd/platform/processor_suite_contract.py",
                "ppd/platform/deterministic_fallback_progress.py",
                "ppd/daemon/deterministic-progress.json",
            ],
            proposal.changed_files,
        )
        self.assertTrue(source_contract_exists)
        self.assertTrue(proposal.promotion_verified)
        self.assertIn(f"- [x] {target}", board)
        self.assertEqual(455, manifest["records"][0]["checkboxId"])
        self.assertEqual("processor_suite_planning", manifest["records"][0]["fallbackKind"])

    def test_daemon_completes_reassessed_blocked_deterministic_task_without_llm(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = (
                "Task checkbox-241: Add a supervised live whole-site public crawl runner under ppd/crawler that "
                "resumes an allowlisted PP&D frontier, delegates archival capture to the ipfs_datasets_py processor "
                "suite, records robots and content-type decisions, and persists metadata manifests instead of raw "
                "bodies or downloaded documents."
            )
            (daemon_dir / "task-board.md").write_text(f"- [!] {target}\n", encoding="utf-8")
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
            daemon = Daemon(
                Config(
                    repo_root=repo,
                    apply=True,
                    revisit_blocked=True,
                    revisit_blocked_ignore_failure_gates=True,
                    revisit_blocked_reassess_llm_termination_gates=True,
                    validation_commands=(("true",),),
                )
            )

            proposal = daemon.run_cycle()
            board = (daemon_dir / "task-board.md").read_text(encoding="utf-8")
            manifest = json.loads((daemon_dir / "deterministic-progress.json").read_text(encoding="utf-8"))
            source_contract_exists = (repo / "ppd" / "platform" / "bounded_live_crawl_dry_run.py").exists()

        self.assertTrue(proposal.valid)
        self.assertTrue(source_contract_exists)
        self.assertTrue(proposal.promotion_verified)
        self.assertIn(f"- [x] {target}", board)
        self.assertEqual(241, manifest["records"][0]["checkboxId"])
        self.assertEqual("bounded_live_crawl_dry_run", manifest["records"][0]["fallbackKind"])

    def test_daemon_completes_generated_blocked_cascade_task_without_llm(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            target = (
                "Task checkbox-262: Add generated blocked-cascade daemon-repair coverage for tranche 5 item 1 "
                "proving blocked PP&D work stays parked until a fresh daemon repair task validates."
            )
            (daemon_dir / "task-board.md").write_text(f"- [!] {target}\n", encoding="utf-8")
            daemon = Daemon(
                Config(
                    repo_root=repo,
                    apply=True,
                    revisit_blocked=True,
                    revisit_blocked_ignore_failure_gates=True,
                    revisit_blocked_reassess_llm_termination_gates=True,
                    validation_commands=(("true",),),
                )
            )

            proposal = daemon.run_cycle()
            board = (daemon_dir / "task-board.md").read_text(encoding="utf-8")
            manifest = json.loads((daemon_dir / "deterministic-progress.json").read_text(encoding="utf-8"))
            source_contract_exists = (repo / "ppd" / "platform" / "blocked_cascade_daemon_repair.py").exists()

        self.assertTrue(proposal.valid)
        self.assertTrue(source_contract_exists)
        self.assertTrue(proposal.promotion_verified)
        self.assertIn(f"- [x] {target}", board)
        self.assertEqual(262, manifest["records"][0]["checkboxId"])
        self.assertEqual("blocked_cascade_daemon_repair", manifest["records"][0]["fallbackKind"])

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

    def test_daemon_cli_exits_zero_when_watch_reaches_no_eligible_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            daemon_dir = repo / "ppd" / "daemon"
            daemon_dir.mkdir(parents=True)
            (daemon_dir / "task-board.md").write_text(
                "- [!] Task checkbox-1: Parked task.\n",
                encoding="utf-8",
            )
            project_root = Path(__file__).resolve().parents[2]

            completed = subprocess.run(
                [
                    "python3",
                    "ppd/daemon/ppd_daemon.py",
                    "--repo-root",
                    str(repo),
                    "--apply",
                    "--watch",
                    "--iterations",
                    "0",
                ],
                cwd=project_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            status = json.loads((daemon_dir / "status.json").read_text(encoding="utf-8"))

        self.assertEqual(0, completed.returncode)
        self.assertIn("no_eligible_tasks", completed.stdout)
        self.assertEqual("", status["active_target_task"])


if __name__ == "__main__":
    unittest.main()
