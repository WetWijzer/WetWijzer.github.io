from __future__ import annotations

import json
from pathlib import Path

from ppd.validation.offline_patch_migration_approval_matrix_v2 import (
    validate_offline_patch_migration_approval_matrix_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "offline_patch_migration_approval_matrix_v2"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_matrix_is_accepted() -> None:
    result = validate_offline_patch_migration_approval_matrix_v2(_load_fixture("valid_matrix.json"))

    assert result.ok
    assert result.errors == ()


def test_invalid_matrix_rejects_required_failure_classes() -> None:
    result = validate_offline_patch_migration_approval_matrix_v2(_load_fixture("invalid_matrix.json"))

    assert not result.ok
    codes = set(result.codes())
    assert "uncited_approval_row" in codes
    assert "rationale_missing" in codes
    assert "reviewer_owner_missing" in codes
    assert "unresolved_blocker_missing_follow_up_task" in codes
    assert "rollback_verification_missing" in codes
    assert "private_or_authenticated_fact" in codes
    assert "raw_or_browser_artifact" in codes
    assert "live_execution_or_promotion_claim" in codes
    assert "legal_or_permitting_guarantee" in codes
    assert "consequential_action_language" in codes
    assert "active_mutation_flag" in codes


def test_unresolved_blocker_with_follow_up_task_is_accepted() -> None:
    matrix = {
        "version": "2",
        "approval_rows": [
            {
                "decision": "defer",
                "source_evidence_ids": ["ppd-plan-source-anchor-20260508"],
                "rationale": "Needs deterministic fixture coverage before inclusion.",
                "reviewer_owner": "ppd-validation-reviewer",
                "blockers": [
                    {
                        "status": "unresolved",
                        "description": "Fixture gap remains.",
                        "follow_up_task": "task-20260529-619",
                    }
                ],
                "rollback_verification": {"verified": True, "evidence": "fixture-only validator path"},
            }
        ],
    }

    result = validate_offline_patch_migration_approval_matrix_v2(matrix)

    assert result.ok
