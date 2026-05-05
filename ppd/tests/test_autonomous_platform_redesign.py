from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ppd.crawler.whole_site_archival import (
    ArchiveSeed,
    build_default_whole_site_archive_plan,
    validate_whole_site_archive_plan,
)
from ppd.daemon.ppd_daemon import parse_tasks, select_task, should_sleep_between_watch_cycles
from ppd.daemon.ppd_supervisor import (
    AUTONOMOUS_EXECUTION_CAPABILITY_TITLES,
    AUTONOMOUS_PLATFORM_REPLENISHMENT_TITLES,
    SupervisorConfig,
    builtin_replenish_goal_tasks,
    compact_repeated_autonomous_platform_tranches,
    diagnose,
)
from ppd.devhub.playwright_pdf_automation import (
    AutomationActionKind,
    AutomationDisposition,
    REFUSED_ACTIONS,
    build_default_interaction_plan,
    validate_interaction_plan,
)


class AutonomousPlatformRedesignTest(unittest.TestCase):
    def test_whole_site_archive_plan_uses_processor_suite_without_live_artifacts(self) -> None:
        plan = build_default_whole_site_archive_plan()
        payload = plan.to_dict()

        self.assertEqual([], validate_whole_site_archive_plan(plan))
        self.assertEqual("ppd-whole-site-archive-v2", payload["planId"])
        self.assertGreaterEqual(len(payload["seeds"]), 5)
        self.assertIn("https://www.portland.gov/ppd", {seed["url"] for seed in payload["seeds"]})
        self.assertIn("https://devhub.portlandoregon.gov/", {seed["url"] for seed in payload["seeds"]})
        self.assertTrue(payload["policy"]["robotsPreflightRequired"])
        self.assertTrue(payload["policy"]["manifestOnly"])
        self.assertFalse(payload["policy"]["storesRawOutputs"])
        self.assertFalse(payload["policy"]["storesPrivateRuntimeArtifacts"])
        self.assertFalse(payload["policy"]["launchesBrowser"])
        self.assertFalse(payload["policy"]["liveNetworkEnabledByDefault"])

        modules = {item["module"] for item in payload["processorCapabilities"]}
        self.assertTrue(any(module.startswith("ipfs_datasets_py.processors.web_archiving") for module in modules))
        self.assertTrue(any(module.startswith("ipfs_datasets_py.processors.legal_scrapers") for module in modules))
        self.assertTrue(any("pdf" in module for module in modules))
        self.assertIn("formal_logic_guardrail_bundle", payload["downstreamOutputs"])
        self.assertIn("playwright_draft_planning_hints", payload["downstreamOutputs"])

    def test_whole_site_archive_plan_rejects_private_devhub_seed(self) -> None:
        plan = build_default_whole_site_archive_plan()
        broken = type(plan)(
            plan_id=plan.plan_id,
            source_authority=plan.source_authority,
            seeds=plan.seeds
            + (
                ArchiveSeed(
                    id="private-devhub-permits",
                    url="https://devhub.portlandoregon.gov/permits",
                    purpose="Invalid private permit area.",
                ),
            ),
            policy=plan.policy,
            processor_capabilities=plan.processor_capabilities,
            work_queue=plan.work_queue,
            downstream_outputs=plan.downstream_outputs,
            citation_urls=plan.citation_urls,
        )

        errors = validate_whole_site_archive_plan(broken)

        self.assertTrue(any("private DevHub paths" in error for error in errors))

    def test_playwright_pdf_plan_allows_draft_fills_and_refuses_official_actions(self) -> None:
        plan = build_default_interaction_plan()
        payload = plan.to_dict()

        self.assertEqual([], validate_interaction_plan(plan))
        self.assertTrue(payload["userAuthorizationRequired"])
        self.assertFalse(payload["liveBrowserEnabledByDefault"])
        self.assertFalse(payload["privateRuntimeArtifactsAllowed"])
        self.assertTrue(any(action["actionKind"] == "fill_field" for action in payload["playwrightActions"]))
        self.assertTrue(any(action["actionKind"] == "save_draft_preview" for action in payload["playwrightActions"]))

        pdf_plan = payload["pdfFillPlans"][0]
        self.assertEqual("draft_preview_pdf_fields", pdf_plan["outputMode"])
        self.assertFalse(pdf_plan["officialUploadAllowed"])
        self.assertGreaterEqual(len(pdf_plan["fields"]), 3)

        gates = {AutomationActionKind(gate["actionKind"]): gate for gate in payload["gates"]}
        for action_kind in REFUSED_ACTIONS:
            self.assertEqual(AutomationDisposition.REFUSE.value, gates[action_kind]["disposition"])
            self.assertTrue(gates[action_kind]["exactConfirmationRequired"])
            self.assertFalse(gates[action_kind]["reversible"])
        self.assertEqual(AutomationDisposition.ALLOW_DRAFT.value, gates[AutomationActionKind.FILL_FIELD]["disposition"])
        self.assertEqual(AutomationDisposition.ALLOW_DRAFT.value, gates[AutomationActionKind.FILL_PDF_FIELD]["disposition"])

    def test_supervisor_appends_platform_tranche_when_completed_recovery_board_has_no_work(self) -> None:
        board = "\n".join(
            (
                "# PP&D Daemon Task Board",
                "",
                "## Manual Recovery Tranche 20",
                "",
                "- [x] Task checkbox-217: Completed generated daemon repair.",
                "- [x] Task checkbox-218: Completed generated daemon repair.",
                "",
                "## Built-In Blocked Cascade Recovery Tranche",
                "",
                "- [x] Task checkbox-215: Completed generated blocked-cascade daemon-repair coverage.",
            )
        )

        repaired, labels = builtin_replenish_goal_tasks(board, rows=[])
        selected = select_task(parse_tasks(repaired), revisit_blocked=True)

        self.assertEqual(tuple(f"checkbox-{number}" for number in range(219, 225)), labels)
        self.assertIn("## Built-In Autonomous PP&D Platform Tranche", repaired)
        for title in AUTONOMOUS_PLATFORM_REPLENISHMENT_TITLES:
            self.assertIn(title, repaired)
        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(219, selected.checkbox_id)
        self.assertIn("whole-site PP&D archival plan", selected.title)

    def test_supervisor_escalates_once_to_execution_capability_after_platform_tranche_completes(self) -> None:
        first_board = "\n".join(
            (
                "# PP&D Daemon Task Board",
                "",
                "## Manual Recovery Tranche 20",
                "",
                "- [x] Task checkbox-218: Completed generated daemon repair.",
                "",
                "## Built-In Autonomous PP&D Platform Tranche",
                "",
                *(
                    f"- [x] Task checkbox-{219 + offset}: {title}"
                    for offset, title in enumerate(AUTONOMOUS_PLATFORM_REPLENISHMENT_TITLES)
                ),
            )
        )

        repaired, labels = builtin_replenish_goal_tasks(first_board, rows=[])
        selected = select_task(parse_tasks(repaired), revisit_blocked=True)

        self.assertEqual(tuple(f"checkbox-{number}" for number in range(225, 231)), labels)
        self.assertIn("## Built-In Autonomous PP&D Execution Capability Tranche", repaired)
        self.assertNotIn("## Built-In Autonomous PP&D Platform Tranche 2", repaired)
        for title in AUTONOMOUS_EXECUTION_CAPABILITY_TITLES:
            self.assertIn(title, repaired)
        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(225, selected.checkbox_id)
        self.assertIn("supervised live whole-site public crawl runner", selected.title)

    def test_supervisor_compacts_repeated_generated_platform_tranches(self) -> None:
        board = "\n".join(
            (
                "# PP&D Daemon Task Board",
                "",
                "## Built-In Autonomous PP&D Platform Tranche",
                "",
                "- [x] Task checkbox-219: Add a side-effect-free whole-site PP&D archival plan.",
                "",
                "## Built-In Supervisor Planning Notes",
                "",
                "- First planning note.",
                "",
                "## Built-In Autonomous PP&D Platform Tranche 2",
                "",
                "- [x] Task checkbox-225: Add autonomous platform continuation coverage for tranche 2.",
                "",
                "## Built-In Supervisor Planning Notes",
                "",
                "- Duplicate planning note.",
                "",
                "## Built-In Autonomous PP&D Platform Tranche 3",
                "",
                "- [x] Task checkbox-229: Add autonomous platform continuation coverage for tranche 3.",
                "",
                "## Manual Followup",
                "",
                "- [ ] Task checkbox-233: Keep independent work.",
            )
        )

        compacted, removed = compact_repeated_autonomous_platform_tranches(board)

        self.assertEqual(2, removed)
        self.assertIn("## Built-In Autonomous PP&D Platform Tranche", compacted)
        self.assertNotIn("## Built-In Autonomous PP&D Platform Tranche 2", compacted)
        self.assertNotIn("tranche 3", compacted)
        self.assertIn("## Manual Followup", compacted)
        self.assertIn("- [ ] Task checkbox-233: Keep independent work.", compacted)
        self.assertIn("Built-In Autonomous Platform Compaction Notes", compacted)

    def test_supervisor_diagnoses_completed_board_as_platform_replanning(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            board_path = repo / "ppd" / "daemon" / "task-board.md"
            board_path.parent.mkdir(parents=True)
            board_path.write_text("- [x] Task checkbox-218: Completed generated daemon repair.\n", encoding="utf-8")

            decision = diagnose(SupervisorConfig(repo_root=repo, pid_file=Path("ppd/daemon/missing.pid")))

        self.assertEqual("plan_next_tasks", decision.action)
        self.assertTrue(decision.should_invoke_codex)

    def test_daemon_watch_mode_does_not_sleep_when_another_task_is_selectable(self) -> None:
        board_with_work = "- [x] Task checkbox-219: Done.\n- [ ] Task checkbox-220: Next.\n"
        complete_board = "- [x] Task checkbox-219: Done.\n- [x] Task checkbox-220: Done too.\n"

        self.assertFalse(should_sleep_between_watch_cycles(board_with_work))
        self.assertTrue(should_sleep_between_watch_cycles(complete_board))

    def test_platform_plans_do_not_serialize_private_runtime_artifacts(self) -> None:
        combined = json.dumps(
            {
                "archive": build_default_whole_site_archive_plan().to_dict(),
                "interaction": build_default_interaction_plan().to_dict(),
            },
            sort_keys=True,
        ).lower()

        for marker in (
            "storage-state",
            "auth-state",
            "trace.zip",
            ".har",
            "ppd/data/private",
            "ppd/data/raw",
            "password",
            "payment_material",
        ):
            self.assertNotIn(marker, combined)


if __name__ == "__main__":
    unittest.main()
