from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.crawler.public_frontier_expansion_plan_v1 import (
    assert_valid_frontier_expansion_plan_v1,
    validate_frontier_expansion_plan_v1,
)


FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    with (FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def test_public_frontier_expansion_plan_v1_accepts_metadata_only_plan() -> None:
    plan = _load_fixture("public_frontier_expansion_plan_v1_valid.json")

    assert validate_frontier_expansion_plan_v1(plan) == []
    assert_valid_frontier_expansion_plan_v1(plan)


def test_public_frontier_expansion_plan_v1_rejects_required_forbidden_cases() -> None:
    plan = _load_fixture("public_frontier_expansion_plan_v1_invalid.json")

    findings = validate_frontier_expansion_plan_v1(plan)
    codes = {finding.code for finding in findings}

    assert "uncited_candidate" in codes
    assert "non_https_url" in codes
    assert "non_allowlisted_url" in codes
    assert "authenticated_or_private_url" in codes
    assert "missing_source_page_provenance" in codes
    assert "missing_skip_reason" in codes
    assert "raw_body_or_downloaded_artifact_reference" in codes
    assert "processor_completion_claim" in codes
    assert "private_session_or_browser_artifact" in codes
    assert "legal_or_permitting_outcome_guarantee" in codes
    assert "active_state_mutation_flag" in codes

    with pytest.raises(ValueError):
        assert_valid_frontier_expansion_plan_v1(plan)


def test_public_frontier_expansion_plan_v1_rejects_active_state_mutation_domains() -> None:
    mutation_keys = [
        "mutate_source_registry",
        "mutate_crawl_frontier",
        "mutate_archive",
        "mutate_requirements",
        "mutate_guardrails",
        "mutate_release_state",
        "mutate_agent_state",
    ]

    for key in mutation_keys:
        plan = _load_fixture("public_frontier_expansion_plan_v1_valid.json")
        plan[key] = True
        findings = validate_frontier_expansion_plan_v1(plan)
        assert "active_state_mutation_flag" in {finding.code for finding in findings}


def test_public_frontier_expansion_plan_v1_rejects_processor_completion_status_claims() -> None:
    plan = _load_fixture("public_frontier_expansion_plan_v1_valid.json")
    plan["processor_status"] = "succeeded"

    findings = validate_frontier_expansion_plan_v1(plan)

    assert "processor_completion_claim" in {finding.code for finding in findings}
