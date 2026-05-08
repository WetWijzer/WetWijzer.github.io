"""Deterministic recovery planning for stale PP&D execution-capability tranches."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

STALE_EXECUTION_STATUSES = frozenset({"calling_llm", "applying_files"})
RECOVERY_TRANCHE_KIND = "supervisor_execution_capability_recovery"
RECOVERY_BACKEND = "llm_router"


@dataclass(frozen=True)
class RecoveryPlan:
    """A serializable plan for recovering stale execution-capability work."""

    parked_tranches: tuple[dict[str, Any], ...]
    appended_tranche: dict[str, Any]
    daemon_validation_command: tuple[str, ...]
    restart_environment: dict[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "parked_tranches": list(self.parked_tranches),
            "appended_tranche": dict(self.appended_tranche),
            "daemon_validation_command": list(self.daemon_validation_command),
            "restart_environment": dict(self.restart_environment),
        }


def build_recovery_plan(
    platform_slices: list[Mapping[str, Any]],
    *,
    now: datetime | None = None,
) -> RecoveryPlan:
    """Build a deterministic recovery plan for old slices stuck in execution statuses."""

    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    stale_slices = [dict(item) for item in platform_slices if item.get("status") in STALE_EXECUTION_STATUSES]
    parked = tuple(_park_stale_slice(item, timestamp) for item in stale_slices)
    appended = {
        "kind": RECOVERY_TRANCHE_KIND,
        "status": "pending",
        "created_at": timestamp,
        "backend": RECOVERY_BACKEND,
        "scope": "comprehensive_execution_capability",
        "recovers_statuses": sorted(STALE_EXECUTION_STATUSES),
        "parked_tranche_ids": [str(item.get("id", "")) for item in stale_slices],
        "requires_daemon_validation": True,
        "restart_environment": {"PPD_LLM_BACKEND": RECOVERY_BACKEND},
    }
    return RecoveryPlan(
        parked_tranches=parked,
        appended_tranche=appended,
        daemon_validation_command=("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
        restart_environment={"PPD_LLM_BACKEND": RECOVERY_BACKEND},
    )


def _park_stale_slice(platform_slice: Mapping[str, Any], timestamp: str) -> dict[str, Any]:
    parked = dict(platform_slice)
    parked["previous_status"] = platform_slice.get("status")
    parked["status"] = "parked_stale_execution_capability"
    parked["parked_at"] = timestamp
    parked["parked_reason"] = "stale execution-capability tranche superseded by supervisor recovery"
    return parked
