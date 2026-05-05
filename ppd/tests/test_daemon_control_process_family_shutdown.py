from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROL_SCRIPT = REPO_ROOT / "ppd" / "daemon" / "control.sh"
WATCHDOG_SCRIPT = REPO_ROOT / "ppd" / "daemon" / "watchdog.sh"


class DaemonControlProcessFamilyShutdownTest(unittest.TestCase):
    def test_control_script_is_syntax_valid(self) -> None:
        for script in (CONTROL_SCRIPT, WATCHDOG_SCRIPT):
            result = subprocess.run(
                ["bash", "-n", str(script)],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)

    def test_stop_paths_terminate_captured_descendant_process_groups(self) -> None:
        source = CONTROL_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("collect_descendant_pids", source)
        self.assertIn("process_group_for_pid", source)
        self.assertIn("terminate_process_family", source)
        self.assertIn("wait_for_pid_file_process", source)
        self.assertIn("wait_for_systemd_inactive", source)
        self.assertIn("wait_for_systemd_main_pid", source)
        self.assertIn("systemd_unit_main_pid", source)
        self.assertIn("is_systemd_unit_process", source)
        self.assertIn("run_systemd_watchdog_unit", source)
        self.assertIn("write_supervisor_user_unit", source)
        self.assertIn("start_persistent_supervisor_unit", source)
        self.assertIn("is_descendant_of", source)
        self.assertIn("is_current_managed_child", source)
        self.assertIn("sweep_orphaned_ppd_llm_children", source)
        self.assertIn("sweep_unwatched_ppd_daemon_children", source)
        self.assertIn("sweep_unwatched_ppd_supervisor_children", source)
        self.assertIn('kill -TERM -- "-$pgid"', source)
        self.assertIn('kill -KILL -- "-$pgid"', source)
        self.assertIn('! is_descendant_of "$pid" "$daemon_child_pid"', source)
        self.assertIn("/PPD_LLM_PROMPT_FILE/", source)
        self.assertIn("ppd_daemon.py --apply --watch", source)
        self.assertIn("ppd_supervisor.py --watch", source)
        self.assertIn("watchdog.sh", source)
        self.assertIn("systemd-run --user", source)
        self.assertIn('--property=Restart="$restart_policy"', source)
        self.assertIn("--property=KillMode=process", source)
        self.assertIn("PPD_SUPERVISOR_DISABLE_SYSTEMD", source)
        self.assertIn("PPD_SUPERVISOR_HONOR_TERM=1", source)
        self.assertIn("--honor-term", source)
        self.assertIn("Restart=always", source)
        self.assertIn("StartLimitIntervalSec=0", source)
        self.assertIn("ppd-daemon.service", source)
        self.assertIn("ppd-supervisor.service", source)
        self.assertIn("ppd-daemon.child.pid", source)
        self.assertIn("ppd-supervisor.child.pid", source)
        self.assertIn("ppd-daemon-lifecycle.jsonl", source)
        self.assertIn("ppd-supervisor-lifecycle.jsonl", source)
        self.assertIn('touch "$PID_FILE.stop"', source)
        self.assertIn('touch "$SUPERVISOR_PID_FILE.stop"', source)
        self.assertIn("--repair-validation-failures", source)
        self.assertIn("--llm-max-new-tokens 1536", source)
        self.assertIn("--max-prompt-chars 20000", source)
        self.assertIn("--max-compact-prompt-chars 3600", source)
        self.assertIn("--crash-backoff 5", source)
        self.assertNotIn("--revisit-blocked", source)
        self.assertIn("--exception-backoff 5", source)
        self.assertIn("--termination-storm-threshold 8", source)
        self.assertIn("--termination-storm-backoff 900", source)
        self.assertIn('wait_for_pid_file_process "$PID_FILE" 10', source)
        self.assertIn('wait_for_systemd_main_pid "$SUPERVISOR_UNIT" 10', source)
        self.assertIn('wait_for_pid_file_process "$SUPERVISOR_PID_FILE" 10', source)
        self.assertIn('terminate_process_family "$pid" "PP&D daemon"', source)
        self.assertIn('terminate_process_family "$pid" "PP&D supervisor"', source)

        watchdog = WATCHDOG_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("setsid \"$@\" &", watchdog)
        self.assertIn("cleanup_stale_child_on_start", watchdog)
        self.assertIn("stale_child_cleanup", watchdog)
        self.assertIn("terminate_process_family", watchdog)
        self.assertIn("payload+=", watchdog)
        self.assertIn("printf '%s\\n' \"$payload\"", watchdog)

    def test_watchdog_records_child_exit_and_cleans_pid_files_in_oneshot_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp = Path(tempdir)
            pid_file = temp / "watchdog.pid"
            child_pid_file = temp / "child.pid"
            lifecycle_log = temp / "lifecycle.jsonl"
            env = os.environ.copy()
            env["PPD_WATCHDOG_ONESHOT"] = "1"

            result = subprocess.run(
                [
                    "bash",
                    str(WATCHDOG_SCRIPT),
                    "test-role",
                    str(pid_file),
                    str(child_pid_file),
                    str(lifecycle_log),
                    "0",
                    "bash",
                    "-lc",
                    "exit 7",
                ],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                check=False,
            )

            rows = [json.loads(line) for line in lifecycle_log.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(7, result.returncode)
        self.assertFalse(pid_file.exists())
        self.assertFalse(child_pid_file.exists())
        self.assertEqual("watchdog_start", rows[0]["event"])
        self.assertEqual("child_start", rows[1]["event"])
        self.assertEqual("child_exit", rows[2]["event"])
        self.assertEqual(7, rows[2]["exit_code"])
        self.assertEqual("test-role", rows[2]["role"])

    def test_watchdog_cleans_stale_child_pid_before_launching_new_child(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp = Path(tempdir)
            pid_file = temp / "watchdog.pid"
            child_pid_file = temp / "child.pid"
            lifecycle_log = temp / "lifecycle.jsonl"
            stale = subprocess.Popen(
                ["bash", "-lc", "sleep 30"],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            child_pid_file.write_text(str(stale.pid), encoding="utf-8")
            env = os.environ.copy()
            env["PPD_WATCHDOG_ONESHOT"] = "1"
            try:
                result = subprocess.run(
                    [
                        "bash",
                        str(WATCHDOG_SCRIPT),
                        "test-role",
                        str(pid_file),
                        str(child_pid_file),
                        str(lifecycle_log),
                        "0",
                        "bash",
                        "-lc",
                        "exit 0",
                    ],
                    cwd=REPO_ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    check=False,
                    timeout=10,
                )
                rows = [json.loads(line) for line in lifecycle_log.read_text(encoding="utf-8").splitlines()]
            finally:
                if stale.poll() is None:
                    stale.kill()
                    stale.wait(timeout=5)

        self.assertEqual(0, result.returncode)
        self.assertIsNotNone(stale.poll())
        self.assertEqual("stale_child_cleanup", rows[0]["event"])
        self.assertEqual(stale.pid, rows[0]["pid"])

    def test_watchdog_ignores_term_without_stop_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp = Path(tempdir)
            pid_file = temp / "watchdog.pid"
            child_pid_file = temp / "child.pid"
            lifecycle_log = temp / "lifecycle.jsonl"
            process = subprocess.Popen(
                [
                    "bash",
                    str(WATCHDOG_SCRIPT),
                    "test-role",
                    str(pid_file),
                    str(child_pid_file),
                    str(lifecycle_log),
                    "0.1",
                    "bash",
                    "-lc",
                    "sleep 30",
                ],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                for _ in range(50):
                    if pid_file.exists() and child_pid_file.exists():
                        break
                    time.sleep(0.02)
                self.assertTrue(pid_file.exists())
                os.kill(process.pid, signal.SIGTERM)
                time.sleep(0.2)
                self.assertIsNone(process.poll())

                (temp / "watchdog.pid.stop").write_text("stop\n", encoding="utf-8")
                os.kill(process.pid, signal.SIGTERM)
                process.wait(timeout=5)
                rows = [json.loads(line) for line in lifecycle_log.read_text(encoding="utf-8").splitlines()]
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)

        events = [row["event"] for row in rows]
        self.assertIn("watchdog_signal_ignored", events)
        self.assertIn("watchdog_stop", events)
        self.assertFalse(pid_file.exists())
        self.assertFalse(child_pid_file.exists())


if __name__ == "__main__":
    unittest.main()
