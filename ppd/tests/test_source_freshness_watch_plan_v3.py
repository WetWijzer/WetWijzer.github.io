from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.source_freshness_watch_plan import (
    WatchPlanValidationError,
    validate_public_source_freshness_watch_plan_v3,
    validate_public_source_freshness_watch_plan_v3_dict,
)


FIXTURE = Path(__file__).parent / "fixtures" / "source_freshness_watch_plan_v3.json"


def load_fixture(name: str) -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))[name]


def error_codes(plan: dict[str, object]) -> set[str]:
    with pytest.raises(WatchPlanValidationError) as raised:
        validate_public_source_freshness_watch_plan_v3(plan)
    return {error.code for error in raised.value.errors}


def test_accepts_minimal_cited_public_watch_plan_v3() -> None:
    plan = load_fixture("valid")

    validate_public_source_freshness_watch_plan_v3(plan)

    assert validate_public_source_freshness_watch_plan_v3_dict(plan) == {"ok": True, "errors": []}


def test_rejects_uncited_watch_rows() -> None:
    plan = load_fixture("valid")
    row = copy.deepcopy(plan["watch_rows"][0])
    row["watch_id"] = "missing-citations"
    row["citations"] = []
    plan["watch_rows"] = [row]

    assert "missing_citations" in error_codes(plan)


def test_rejects_non_allowlisted_and_authenticated_urls() -> None:
    plan = load_fixture("valid")
    outside = copy.deepcopy(plan["watch_rows"][0])
    outside["watch_id"] = "outside-host"
    outside["canonical_url"] = "https://example.com/ppd"
    auth = copy.deepcopy(plan["watch_rows"][0])
    auth["watch_id"] = "authenticated-devhub"
    auth["canonical_url"] = "https://devhub.portlandoregon.gov/account/my-permits"
    auth["requires_auth"] = True
    plan["watch_rows"] = [outside, auth]

    codes = error_codes(plan)

    assert "non_allowlisted_url" in codes
    assert "authenticated_url" in codes


def test_rejects_missing_priority_or_skip_defer_rationale() -> None:
    plan = load_fixture("valid")
    missing_priority = copy.deepcopy(plan["watch_rows"][0])
    missing_priority["watch_id"] = "missing-priority"
    missing_priority.pop("priority")
    skipped = copy.deepcopy(plan["watch_rows"][0])
    skipped["watch_id"] = "skip-without-rationale"
    skipped["decision"] = "skip"
    deferred = copy.deepcopy(plan["watch_rows"][0])
    deferred["watch_id"] = "defer-without-rationale"
    deferred["decision"] = "defer"
    plan["watch_rows"] = [missing_priority, skipped, deferred]

    codes = error_codes(plan)

    assert "missing_priority" in codes
    assert "missing_skip_rationale" in codes
    assert "missing_defer_rationale" in codes


def test_rejects_missing_affected_requirement_or_guardrail_refs() -> None:
    plan = load_fixture("valid")
    row = copy.deepcopy(plan["watch_rows"][0])
    row["watch_id"] = "missing-affected-refs"
    row["affected_requirements"] = []
    row["affected_guardrails"] = []
    plan["watch_rows"] = [row]

    codes = error_codes(plan)

    assert "missing_affected_requirement" in codes
    assert "missing_affected_guardrail" in codes


def test_rejects_raw_body_download_archive_and_browser_artifacts() -> None:
    plan = load_fixture("valid")
    row = copy.deepcopy(plan["watch_rows"][0])
    row["watch_id"] = "artifact-row"
    row["raw_body"] = "raw public body must not be committed"
    row["artifact_refs"] = {"download_path": "ppd/tmp/file.pdf", "browser_trace": "trace.zip"}
    plan["watch_rows"] = [row]

    codes = error_codes(plan)

    assert "raw_or_browser_artifact" in codes


def test_rejects_live_crawler_or_processor_completion_claims() -> None:
    plan = load_fixture("valid")
    row = copy.deepcopy(plan["watch_rows"][0])
    row["watch_id"] = "completion-claim"
    row["claims"] = ["crawler_completed", "processor_completed"]
    plan["watch_rows"] = [row]

    assert "live_completion_claim" in error_codes(plan)


def test_rejects_legal_or_permitting_outcome_guarantees() -> None:
    plan = load_fixture("valid")
    row = copy.deepcopy(plan["watch_rows"][0])
    row["watch_id"] = "guarantee-row"
    row["claims"] = ["permit_guaranteed"]
    plan["watch_rows"] = [row]

    assert "outcome_guarantee" in error_codes(plan)


def test_rejects_active_state_and_model_mutation_flags() -> None:
    plan = load_fixture("valid")
    row = copy.deepcopy(plan["watch_rows"][0])
    row["watch_id"] = "mutation-row"
    row["mutation_flags"] = {
        "active_source_mutation": True,
        "active_schedule_mutation": True,
        "active_requirement_mutation": True,
        "active_process_mutation": True,
        "active_guardrail_mutation": True,
        "active_prompt_mutation": True,
        "active_monitoring_mutation": True,
        "active_release_state_mutation": True,
        "active_agent_state_mutation": True,
    }
    plan["watch_rows"] = [row]

    assert "active_mutation_flag" in error_codes(plan)
