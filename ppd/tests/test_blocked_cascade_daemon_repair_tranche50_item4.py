import json
from datetime import datetime, timezone
from pathlib import Path


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "blocked_cascade_tranche50_item4"
    / "blocked_cascade_repair_tasks.json"
)


def _parse_utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _has_fresh_validating_repair(blocked_work, repair_tasks):
    blocked_at = _parse_utc(blocked_work["blocked_at"])
    target_task_id = blocked_work["repair_gate"]["validates_task_id"]

    for repair_task in repair_tasks:
        if repair_task.get("kind") != "daemon_repair":
            continue
        if _parse_utc(repair_task["generated_at"]) <= blocked_at:
            continue

        validation = repair_task.get("validation", {})
        if validation.get("status") != "passed":
            continue
        if target_task_id in validation.get("validates_task_ids", []):
            return True

    return False


def test_blocked_cascade_stays_parked_without_fresh_validating_daemon_repair():
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    blocked_work = fixture["blocked_work"]
    repair_tasks = fixture["repair_tasks"]

    assert blocked_work["status"] == "parked"
    assert not _has_fresh_validating_repair(blocked_work, [])
    assert not _has_fresh_validating_repair(blocked_work, repair_tasks[:1])
    assert not _has_fresh_validating_repair(blocked_work, repair_tasks[:2])


def test_blocked_cascade_unparks_only_after_fresh_daemon_repair_validates_target():
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    blocked_work = fixture["blocked_work"]

    assert _has_fresh_validating_repair(blocked_work, fixture["repair_tasks"])
