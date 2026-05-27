from __future__ import annotations

import json
from pathlib import Path

from ppd.devhub.surface_map_candidate_validation import (
    validate_surface_map_candidate,
    validate_surface_map_candidates,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "surface_map_candidate_validation.json"


def _fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _candidate(candidate_id: str) -> dict[str, object]:
    fixture = _fixture()
    candidates = fixture["candidates"]
    assert isinstance(candidates, list)
    for candidate in candidates:
        assert isinstance(candidate, dict)
        if candidate.get("candidate_id") == candidate_id:
            return candidate
    raise AssertionError(f"missing fixture candidate {candidate_id}")


def _codes(candidate_id: str) -> set[str]:
    result = validate_surface_map_candidate(_candidate(candidate_id))
    return {violation.code for violation in result.violations}


def test_clear_candidate_allows_reversible_draft_actions() -> None:
    result = validate_surface_map_candidate(_candidate("valid_residential_draft_surface"))

    assert result.reversible_draft_allowed is True
    assert result.violations == ()


def test_low_confidence_or_missing_route_and_heading_blocks_reversible_drafts() -> None:
    assert _codes("low_confidence_missing_context") == {
        "low_selector_confidence",
        "missing_route_evidence",
        "missing_heading_evidence",
    }


def test_ambiguous_required_labels_block_reversible_drafts() -> None:
    result = validate_surface_map_candidate(_candidate("ambiguous_required_labels"))

    assert result.reversible_draft_allowed is False
    messages = [violation.message for violation in result.violations]
    assert "required field 'owner_name' must have exactly one non-empty label" in messages
    assert "required label 'project contact' is shared by fields: applicant_name, contractor_name" in messages


def test_consequential_controls_cannot_be_classified_reversible() -> None:
    result = validate_surface_map_candidate(_candidate("consequential_controls_mislabeled_reversible"))

    assert result.reversible_draft_allowed is False
    assert {violation.code for violation in result.violations} == {"consequential_control_marked_reversible"}
    messages = [violation.message for violation in result.violations]
    assert "actions item 'submit_application' must not be classified as reversible" in messages
    assert "actions item 'pay_fee' must not be classified as reversible" in messages
    assert "upload_controls item 'upload_plans' must not be classified as reversible" in messages


def test_batch_validation_fails_closed_when_any_candidate_is_unsafe() -> None:
    fixture = _fixture()
    candidates = fixture["candidates"]
    assert isinstance(candidates, list)

    result = validate_surface_map_candidates(candidates)

    assert result.reversible_draft_allowed is False
    assert len(result.results) == 4
    assert result.results[0].reversible_draft_allowed is True
    assert all(item.candidate_id for item in result.results)
