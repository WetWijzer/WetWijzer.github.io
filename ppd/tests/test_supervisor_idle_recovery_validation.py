from __future__ import annotations

from pathlib import Path

from ppd.supervisor_idle_recovery import load_idle_recovery_board, validate_tranche_2_idle_recovery


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "supervisor_idle_recovery"


def test_tranche_2_idle_recovery_accepts_fresh_goal_aligned_platform_tasks() -> None:
    board = load_idle_recovery_board(FIXTURE_DIR / "tranche2_completed_board.json")

    report = validate_tranche_2_idle_recovery(board)

    assert report.ok is True
    assert report.findings == ()


def test_tranche_2_idle_recovery_rejects_sleep_and_completed_tranche_reuse() -> None:
    board = load_idle_recovery_board(FIXTURE_DIR / "tranche2_completed_board.json")
    board["synthesized_tasks"] = [
        {
            "id": "task-sleep-on-idle",
            "title": "Sleep until the next supervisor cycle",
            "goal_id": "goal-platform-supervision",
            "area": "platform",
            "tranche": 2,
            "source_tranche": 2,
        }
    ]

    report = validate_tranche_2_idle_recovery(board)

    assert report.ok is False
    assert {finding.code for finding in report.findings} == {"sleep_task", "duplicate_tranche_reuse"}


def test_tranche_2_idle_recovery_rejects_blocked_retry_churn_and_goal_drift() -> None:
    board = load_idle_recovery_board(FIXTURE_DIR / "tranche2_completed_board.json")
    board["synthesized_tasks"] = [
        {
            "id": "task-retry-authenticated-upload",
            "title": "Retry authenticated upload",
            "goal_id": "goal-unrelated",
            "area": "scraping",
            "tranche": 3,
            "retry_of": "task-retry-authenticated-upload",
        }
    ]

    report = validate_tranche_2_idle_recovery(board)

    assert report.ok is False
    assert {finding.code for finding in report.findings} == {"goal_misaligned", "not_platform_task", "blocked_retry_churn"}
