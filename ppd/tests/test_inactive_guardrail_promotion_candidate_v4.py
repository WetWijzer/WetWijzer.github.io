from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "guardrails" / "inactive_promotion_candidate_v4.py"
spec = importlib.util.spec_from_file_location("inactive_promotion_candidate_v4", MODULE_PATH)
assert spec is not None
candidate_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(candidate_module)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guardrails" / "v4"


def test_builds_inactive_candidate_from_v4_fixtures_only() -> None:
    candidate = candidate_module.build_candidate_from_files(
        FIXTURE_DIR / "post_recompile_agent_readiness_replay_v4.json",
        FIXTURE_DIR / "prior_guardrail_placeholders_v4.json",
    )

    assert candidate["schema"] == "inactive_guardrail_promotion_candidate_v4"
    assert candidate["source_fixtures"] == {
        "readiness_replay_schema": "post_recompile_agent_readiness_replay_v4",
        "placeholder_schema": "prior_guardrail_placeholder_fixture_v4",
    }
    assert candidate["offline_validation_commands"] == candidate_module.OFFLINE_VALIDATION_COMMANDS
    assert "no DevHub access" in candidate["prohibited_actions"]

    rows = candidate["inactive_promotion_rows"]
    assert [row["guardrail_id"] for row in rows] == [
        "inactive-inspection-routing-source-check",
        "inactive-legacy-source-check",
        "inactive-permit-intake-source-check",
    ]
    assert all(row["proposed_state"] == "inactive" for row in rows)
    assert all(row["active_bundle_mutation"] is False for row in rows)

    statuses = {row["guardrail_id"]: row["status"] for row in rows}
    assert statuses["inactive-permit-intake-source-check"] == "candidate"
    assert statuses["inactive-inspection-routing-source-check"] == "hold"
    assert statuses["inactive-legacy-source-check"] == "hold"

    holds = candidate["stale_source_holds"]
    assert holds == [
        {
            "guardrail_id": "inactive-inspection-routing-source-check",
            "agent_id": "inspection-routing-agent",
            "reason": "agent readiness replay is not ready",
        },
        {
            "guardrail_id": "inactive-legacy-source-check",
            "agent_id": "legacy-agent",
            "reason": "missing post-recompile readiness replay for placeholder agent",
        },
    ]

    assert candidate["reviewer_signoff_placeholders"] == [
        {"role": "implementation reviewer", "status": "pending", "name": "TBD"},
        {"role": "guardrail owner", "status": "pending", "name": "TBD"},
    ]
    assert candidate["rollback_plan"]
    assert candidate["post_promotion_smoke_checks"]
    assert candidate["activation_prerequisites"]


def test_rejects_non_v4_readiness_fixture() -> None:
    readiness = {"schema": "older_readiness_fixture", "agents": []}
    placeholders = candidate_module.load_json(FIXTURE_DIR / "prior_guardrail_placeholders_v4.json")

    try:
        candidate_module.build_candidate(readiness, placeholders)
    except ValueError as exc:
        assert "post_recompile_agent_readiness_replay_v4" in str(exc)
    else:
        raise AssertionError("expected non-v4 readiness fixture to be rejected")
