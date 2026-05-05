from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from ppd.daemon.ppd_daemon import (
    Config,
    Proposal,
    apply_files_with_validation,
    cleanup_stale_validation_worktrees,
    temporary_validation_worktree,
)


def make_minimal_repo(root: Path) -> None:
    (root / "ppd" / "daemon").mkdir(parents=True)
    (root / "ppd" / "README.md").write_text("PP&D test repo\n", encoding="utf-8")
    (root / "ppd" / ".gitignore").write_text(
        "/daemon/failed-patches/\n/daemon/worktrees/\n/data/private/\n/data/raw/\n",
        encoding="utf-8",
    )
    (root / "ppd" / "daemon" / "task-board.md").write_text(
        "- [ ] Task checkbox-1: Synthetic task.\n",
        encoding="utf-8",
    )
    (root / "docs").mkdir()
    (root / "docs" / "PORTLAND_PPD_SCRAPING_AUTOMATION_LOGIC_PLAN.md").write_text(
        "Synthetic plan\n",
        encoding="utf-8",
    )


class DaemonTemporaryWorktreeTransportTest(unittest.TestCase):
    def test_validation_failure_never_touches_main_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            make_minimal_repo(repo)
            target = repo / "ppd" / "generated" / "candidate.py"
            proposal = Proposal(
                summary="Add candidate that fails tests",
                files=[
                    {
                        "path": "ppd/generated/candidate.py",
                        "content": "VALUE = 1\n",
                    }
                ],
            )
            config = Config(
                repo_root=repo,
                validation_commands=(("python3", "-c", "raise SystemExit(7)"),),
            )

            result = apply_files_with_validation(proposal, config)

            self.assertFalse(result.applied)
            self.assertEqual("validation", result.failure_kind)
            self.assertFalse(target.exists())
            worktree_root = repo / "ppd" / "daemon" / "worktrees"
            self.assertEqual([], list(worktree_root.iterdir()) if worktree_root.exists() else [])
            manifests = [
                path
                for path in (repo / "ppd" / "daemon" / "failed-patches").glob("*validation*.json")
                if not path.name.endswith(".workspace.json")
            ]
            self.assertEqual(1, len(manifests))
            manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
            self.assertEqual("ephemeral_worktree", manifest["transport"])
            self.assertEqual("failed_ephemeral_workspace", manifest["artifact_kind"])
            self.assertTrue(manifests[0].with_suffix(".workspace.json").exists())
            self.assertTrue(manifests[0].with_suffix(".diff.txt").exists())
            self.assertFalse(manifests[0].with_suffix(".patch").exists())

    def test_validation_repair_pass_promotes_repaired_candidate_only_after_tests_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            make_minimal_repo(repo)
            target = repo / "ppd" / "generated" / "candidate.py"

            def repair_callback(prompt: str, config: Config) -> str:
                self.assertIn("Failing validation results", prompt)
                return json.dumps(
                    {
                        "summary": "Repair candidate value",
                        "impact": "Makes the isolated validation command pass.",
                        "files": [
                            {
                                "path": "ppd/generated/candidate.py",
                                "content": "VALUE = 2\n",
                            }
                        ],
                    }
                )

            validation = (
                "from pathlib import Path\n"
                "text = Path('ppd/generated/candidate.py').read_text(encoding='utf-8')\n"
                "raise SystemExit(0 if 'VALUE = 2' in text else 3)\n"
            )
            proposal = Proposal(
                summary="Add candidate requiring repair",
                files=[
                    {
                        "path": "ppd/generated/candidate.py",
                        "content": "VALUE = 1\n",
                    }
                ],
            )
            config = Config(
                repo_root=repo,
                validation_commands=(("python3", "-c", validation),),
                repair_validation_failures=True,
                validation_repair_callback=repair_callback,
            )

            result = apply_files_with_validation(proposal, config)

            self.assertTrue(result.applied)
            self.assertEqual("Repair candidate value", result.summary)
            self.assertEqual("VALUE = 2\n", target.read_text(encoding="utf-8"))
            self.assertEqual(["ppd/generated/candidate.py"], result.changed_files)
            accepted_dir = repo / "ppd" / "daemon" / "accepted-work"
            self.assertEqual(["accepted-work.jsonl"], sorted(path.name for path in accepted_dir.iterdir()))
            rows = [
                json.loads(line)
                for line in (accepted_dir / "accepted-work.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(1, len(rows))
            self.assertEqual("ephemeral_worktree", rows[0]["transport"])
            self.assertEqual("ledger_only", rows[0]["artifacts"]["mode"])
            self.assertEqual(["ppd/generated/candidate.py"], rows[0]["changed_files"])
            self.assertTrue(rows[0]["promotion"]["verified"])

    def test_stale_worktree_cleanup_removes_interrupted_validation_trees(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            make_minimal_repo(repo)
            stale = repo / "ppd" / "daemon" / "worktrees" / "cycle-stale"
            stale.mkdir(parents=True)
            (stale / "ppd-worktree.json").write_text('{"state":"ready"}\n', encoding="utf-8")
            os.utime(stale, (1, 1))

            removed = cleanup_stale_validation_worktrees(Config(repo_root=repo), max_age_seconds=0)

            self.assertEqual(["cycle-stale"], removed)
            self.assertFalse(stale.exists())

    def test_validation_worktree_exposes_processor_suite_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            make_minimal_repo(repo)
            processor_metadata = repo / "ipfs_datasets_py" / "ipfs_datasets_py" / "processors"
            processor_metadata.mkdir(parents=True)
            (processor_metadata / "web_archiving").write_text("metadata placeholder\n", encoding="utf-8")

            with temporary_validation_worktree(Config(repo_root=repo)) as worktree:
                copied = worktree / "ipfs_datasets_py" / "ipfs_datasets_py" / "processors" / "web_archiving"
                self.assertTrue(copied.exists())
                self.assertEqual("metadata placeholder\n", copied.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
