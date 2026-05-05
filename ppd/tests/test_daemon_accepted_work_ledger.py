import json
import tempfile
import unittest
from pathlib import Path

from ppd.daemon.ppd_daemon import CommandResult, Config, Proposal, persist_accepted_work


class AcceptedWorkLedgerTests(unittest.TestCase):
    def test_persist_accepted_work_appends_jsonl_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            config = Config(repo_root=Path(temp), accepted_dir=Path("accepted-work"))
            proposal = Proposal(
                summary="Accepted fixture round",
                impact="Ledger test",
                target_task="Task checkbox-99: Fixture",
                changed_files=["ppd/example.py"],
                validation_results=[CommandResult(("python3", "--version"), 0, "Python", "")],
                applied=True,
                dry_run=False,
                promotion_verified=True,
            )

            persist_accepted_work(proposal, config, diff_text="--- diff\n")

            ledger_path = Path(temp) / "accepted-work" / "accepted-work.jsonl"
            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["target_task"], "Task checkbox-99: Fixture")
            self.assertEqual(entries[0]["changed_files"], ["ppd/example.py"])
            self.assertEqual("ledger_only", entries[0]["artifacts"]["mode"])
            self.assertEqual("accepted-work/accepted-work.jsonl", entries[0]["artifacts"]["ledger"])
            self.assertEqual(1, entries[0]["diff"]["line_count"])
            self.assertTrue(entries[0]["promotion"]["verified"])
            self.assertTrue(entries[0]["validation_passed"])
            self.assertEqual(["accepted-work.jsonl"], sorted(path.name for path in (Path(temp) / "accepted-work").iterdir()))

    def test_ledger_only_default_ignores_existing_legacy_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            accepted_dir = Path(temp) / "accepted-work"
            accepted_dir.mkdir()
            for name in (
                "legacy-round.json",
                "legacy-round.workspace.json",
                "legacy-round.diff.txt",
                "legacy-round.stat.txt",
            ):
                (accepted_dir / name).write_text("legacy sidecar\n", encoding="utf-8")
            config = Config(repo_root=Path(temp), accepted_dir=Path("accepted-work"))
            proposal = Proposal(
                summary="Accepted ledger-only migration round",
                impact="Keeps legacy sidecars ignored by default.",
                target_task="Task checkbox-452: Ledger-only migration",
                changed_files=["ppd/generated/new.py"],
                validation_results=[CommandResult(("python3", "--version"), 0, "Python", "")],
                applied=True,
                dry_run=False,
                promotion_verified=True,
            )

            persist_accepted_work(proposal, config, diff_text="--- diff\n+++ diff\n")

            entries = [
                json.loads(line)
                for line in (accepted_dir / "accepted-work.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            names = sorted(path.name for path in accepted_dir.iterdir())
            self.assertEqual(1, len(entries))
            self.assertEqual("ledger_only", entries[0]["artifacts"]["mode"])
            self.assertEqual("accepted-work/accepted-work.jsonl", entries[0]["artifacts"]["ledger"])
            self.assertEqual(["ppd/generated/new.py"], entries[0]["changed_files"])
            self.assertEqual(2, entries[0]["diff"]["line_count"])
            self.assertIn("legacy-round.workspace.json", names)
            self.assertNotIn("accepted-ledger-only-migration-round.workspace.json", names)
            self.assertFalse(any(name.endswith(".diff.txt") and "migration" in name for name in names))


if __name__ == "__main__":
    unittest.main()
