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


if __name__ == "__main__":
    unittest.main()
