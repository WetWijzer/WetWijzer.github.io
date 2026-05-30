from __future__ import annotations

import json
from pathlib import Path

from ppd.logic.process_model_impact_proposal_v1 import (
    assert_valid_process_model_impact_proposal_v1,
    finding_codes,
    validate_process_model_impact_proposal_v1,
)


_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "process_model_impact_proposal_v1"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((_FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_process_model_impact_proposal_v1_passes() -> None:
    proposal = _load_fixture("valid_proposal.json")

    result = validate_process_model_impact_proposal_v1(proposal)

    assert result.ok
    assert result.findings == ()
    assert_valid_process_model_impact_proposal_v1(proposal)


def test_process_model_impact_proposal_v1_rejects_required_gaps_and_hazards() -> None:
    proposal = _load_fixture("invalid_proposal.json")

    result = validate_process_model_impact_proposal_v1(proposal)

    assert not result.ok
    codes = set(finding_codes(result))
    assert "uncited_impact_row" in codes
    assert "missing_affected_process_ids" in codes
    assert "missing_affected_requirement_ids" in codes
    assert "missing_dependency_order" in codes
    assert "missing_reviewer_owner" in codes
    assert "missing_rollback_note" in codes
    assert "private_artifact" in codes
    assert "authenticated_artifact" in codes
    assert "session_artifact" in codes
    assert "browser_artifact" in codes
    assert "raw_crawl_artifact" in codes
    assert "outcome_guarantee" in codes
    assert "consequential_action_execution_language" in codes
    assert "active_mutation_flag" in codes


def test_process_model_impact_proposal_v1_allows_inactive_mutation_flags() -> None:
    proposal = _load_fixture("valid_proposal.json")
    proposal["mutation_flags"] = {
        "source": False,
        "document_mutation": "false",
        "active_requirement": "no",
        "process": None,
    }

    result = validate_process_model_impact_proposal_v1(proposal)

    assert result.ok
