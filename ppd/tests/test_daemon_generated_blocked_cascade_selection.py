from __future__ import annotations

import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from ppd.daemon.task_board import parse_tasks, select_task_for_config


@dataclass(frozen=True)
class SelectionConfig:
    repo_root: Path
    result_log: Path
    revisit_blocked: bool = True
    revisit_blocked_ignore_failure_gates: bool = True
    revisit_blocked_reassess_llm_termination_gates: bool = True

    def resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else self.repo_root / path


class GeneratedBlockedCascadeSelectionTest(unittest.TestCase):
    def test_reassessment_prefers_source_backed_blocked_work_over_generated_cascade(self) -> None:
        board = """
# PP&D Daemon Task Board

## Built-In Autonomous PP&D Execution Capability Tranche
- [!] Task checkbox-241: Add a supervised live whole-site public crawl runner under ppd/crawler that resumes an allowlisted PP&D frontier.

## Built-In Blocked Cascade Recovery Tranche 3
- [!] Task checkbox-254: Add generated blocked-cascade daemon-repair coverage for tranche 3 item 1 proving blocked PP&D work stays parked until a fresh daemon repair task validates.
- [!] Task checkbox-255: Add generated blocked-cascade daemon-repair coverage for tranche 3 item 2 proving blocked PP&D work stays parked until a fresh daemon repair task validates.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result_log = root / "ppd-daemon.jsonl"
            result_log.write_text("", encoding="utf-8")
            selected = select_task_for_config(
                parse_tasks(board),
                SelectionConfig(repo_root=root, result_log=result_log),
            )

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected.checkbox_id, 241)

    def test_reassessment_can_fall_back_to_generated_cascade_when_it_is_all_that_remains(self) -> None:
        board = """
# PP&D Daemon Task Board

## Built-In Blocked Cascade Recovery Tranche 3
- [!] Task checkbox-254: Add generated blocked-cascade daemon-repair coverage for tranche 3 item 1 proving blocked PP&D work stays parked until a fresh daemon repair task validates.
- [!] Task checkbox-255: Add generated blocked-cascade daemon-repair coverage for tranche 3 item 2 proving blocked PP&D work stays parked until a fresh daemon repair task validates.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result_log = root / "ppd-daemon.jsonl"
            result_log.write_text("", encoding="utf-8")
            selected = select_task_for_config(
                parse_tasks(board),
                SelectionConfig(repo_root=root, result_log=result_log),
            )

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected.checkbox_id, 254)


if __name__ == "__main__":
    unittest.main()
