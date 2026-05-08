from __future__ import annotations

from datetime import datetime, timezone

from ppd.daemon.supervisor_execution_recovery import RECOVERY_BACKEND, build_recovery_plan


def test_stale_calling_llm_and_applying_files_slices_are_parked() -> None:
    now = datetime(2026, 5, 8, 22, 0, tzinfo=timezone.utc)
    plan = build_recovery_plan(
        [
            {"id": "old-call", "status": "calling_llm", "platform": "old"},
            {"id": "old-apply", "status": "applying_files", "platform": "old"},
            {"id": "fresh", "status": "pending", "platform": "old"},
        ],
        now=now,
    )

    assert [item["id"] for item in plan.parked_tranches] == ["old-call", "old-apply"]
    assert {item["previous_status"] for item in plan.parked_tranches} == {"calling_llm", "applying_files"}
    assert {item["status"] for item in plan.parked_tranches} == {"parked_stale_execution_capability"}
    assert all(item["parked_at"] == "2026-05-08T22:00:00+00:00" for item in plan.parked_tranches)


def test_recovery_appends_comprehensive_execution_tranche_and_router_restart() -> None:
    now = datetime(2026, 5, 8, 22, 5, tzinfo=timezone.utc)
    plan = build_recovery_plan(
        [
            {"id": "slice-a", "status": "calling_llm"},
            {"id": "slice-b", "status": "applying_files"},
        ],
        now=now,
    )

    assert plan.appended_tranche["kind"] == "supervisor_execution_capability_recovery"
    assert plan.appended_tranche["scope"] == "comprehensive_execution_capability"
    assert plan.appended_tranche["parked_tranche_ids"] == ["slice-a", "slice-b"]
    assert plan.appended_tranche["requires_daemon_validation"] is True
    assert plan.daemon_validation_command == ("python3", "ppd/daemon/ppd_daemon.py", "--self-test")
    assert plan.restart_environment == {"PPD_LLM_BACKEND": RECOVERY_BACKEND}
    assert plan.appended_tranche["restart_environment"] == {"PPD_LLM_BACKEND": "llm_router"}
