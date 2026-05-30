from __future__ import annotations

import json
from pathlib import Path

from ppd.post_promotion_guarded_agent_replay_result_ledger_v1 import build_result_ledger

FIXTURE_DIR = Path(__file__).parent / "fixtures"
PLAN_PATH = FIXTURE_DIR / "post_promotion_guarded_agent_replay_plan_v1.json"
EXPECTED_PATH = FIXTURE_DIR / "post_promotion_guarded_agent_replay_result_ledger_v1.expected.json"


def test_build_result_ledger_from_fixture_plan() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))

    assert build_result_ledger(plan) == expected


def test_result_rows_are_ordered_and_fixture_only() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    ledger = build_result_ledger(plan)

    assert ledger["live_agents_run"] is False
    assert ledger["official_actions_performed"] is False
    assert ledger["active_artifacts_mutated"] is False
    assert [row["row_index"] for row in ledger["ordered_result_rows"]] == [1, 2]
    assert [row["expected_outcome_placeholder"] for row in ledger["ordered_result_rows"]] == [
        "EXPECTED_PASS_PLACEHOLDER",
        "EXPECTED_BLOCK_PLACEHOLDER",
    ]
    assert all(row["synthetic_replay_result"] == "NOT_RUN_FIXTURE_ONLY" for row in ledger["ordered_result_rows"])
