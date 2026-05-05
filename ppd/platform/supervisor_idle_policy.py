"""Source-backed contract for supervisor idle and replenishment behavior."""

from __future__ import annotations


def supervisor_idle_policy() -> dict[str, object]:
    return {
        "capability": "supervisor_idle_recovery",
        "noEligibleTasksPolicy": "review_goal_before_replenishment",
        "replenishmentLimits": {
            "autonomousPlatformTranches": 1,
            "executionCapabilityTranches": 1,
        },
        "mustNotAcceptRuntimeOnlyProgress": True,
        "mustVerifyPromotionToMainWorktree": True,
        "acceptedEvidenceMode": "ledger_only",
    }
