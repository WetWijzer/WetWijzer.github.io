import unittest

from ppd.daemon.blocked_cascade_recovery import classify_blocked_cascade_stall


class BlockedCascadeRecoveryTest(unittest.TestCase):
    def test_repeated_termination_replans_and_keeps_target_parked(self):
        decision = classify_blocked_cascade_stall(
            active_target_task=(
                "Task checkbox-443: Add generated blocked-cascade daemon-repair "
                "coverage proving blocked PP&D work stays parked until a fresh "
                "daemon repair task validates."
            ),
            consecutive_exceptions=2,
            recent_results=[
                {
                    "errors": ["SystemExit: 143 during apply_file_replacement_proposal"],
                    "target_task": "blocked PP&D work stays parked",
                    "summary": "Daemon cycle crashed before completion.",
                }
            ],
        )

        self.assertTrue(decision.should_replan)
        self.assertTrue(decision.keep_target_parked)
        self.assertEqual(3, len(decision.next_tasks))
        self.assertIn("py_compile", decision.next_tasks[2])

    def test_single_exception_does_not_force_replan(self):
        decision = classify_blocked_cascade_stall(
            active_target_task="Task checkbox-443: blocked-cascade daemon-repair coverage",
            consecutive_exceptions=1,
            recent_results=[{"errors": ["SystemExit: 143"]}],
        )

        self.assertFalse(decision.should_replan)
        self.assertFalse(decision.keep_target_parked)
        self.assertEqual((), decision.next_tasks)


if __name__ == "__main__":
    unittest.main()
