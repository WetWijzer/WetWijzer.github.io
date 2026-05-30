"""Tests for fixture-first process model impact proposals."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from ppd.logic.process_model_impact_proposal import (
    IMPACT_CATEGORIES,
    PROPOSAL_VERSION,
    build_impact_proposal,
    build_impact_proposal_from_files,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "process_model_impact_proposal_v1"
CANDIDATE_PACKET_PATH = FIXTURE_DIR / "requirement_formalization_candidate_packet_v1.json"
PROCESS_FIXTURE_PATH = FIXTURE_DIR / "process_model_fixtures_v1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_build_impact_proposal_covers_required_categories() -> None:
    proposal = build_impact_proposal_from_files(CANDIDATE_PACKET_PATH, PROCESS_FIXTURE_PATH)

    assert proposal["proposal_version"] == PROPOSAL_VERSION
    assert proposal["mutation_policy"] == "proposal_only_no_active_model_mutation"
    assert set(proposal["impacts"]) == set(IMPACT_CATEGORIES)

    for category in IMPACT_CATEGORIES:
        category_impacts = proposal["impacts"][category]
        assert category_impacts, category
        for impact in category_impacts:
            assert impact["category"] == category
            assert impact["affected_process_ids"]
            assert impact["dependency_order"] > 0
            assert impact["reviewer_owner"] == "ppd-process-model-reviewer"
            assert "No active process models" in impact["rollback_note"]
            assert impact["source_requirement_ids"]
            assert impact["citations"]
            for citation in impact["citations"]:
                assert citation["evidence_id"]
                assert citation["canonical_url"].startswith("https://www.portland.gov/")


def test_build_impact_proposal_does_not_mutate_inputs() -> None:
    packet = _load(CANDIDATE_PACKET_PATH)
    process_fixtures = _load(PROCESS_FIXTURE_PATH)
    original_packet = deepcopy(packet)
    original_process_fixtures = deepcopy(process_fixtures)

    build_impact_proposal(packet, process_fixtures)

    assert packet == original_packet
    assert process_fixtures == original_process_fixtures


def test_affected_processes_are_derived_from_fixture_permit_types() -> None:
    proposal = build_impact_proposal_from_files(CANDIDATE_PACKET_PATH, PROCESS_FIXTURE_PATH)

    document_impacts = proposal["impacts"]["required_documents"]
    assert document_impacts[0]["affected_process_ids"] == [
        "process-building-plan-review-fixture"
    ]

    exception_impacts = proposal["impacts"]["exceptions"]
    assert exception_impacts[0]["affected_process_ids"] == [
        "process-standard-trade-fixture"
    ]

    global_fact_impacts = proposal["impacts"]["required_user_facts"]
    assert global_fact_impacts[0]["affected_process_ids"] == [
        "process-building-plan-review-fixture",
        "process-standard-trade-fixture",
    ]


def test_proposal_includes_offline_validation_commands() -> None:
    proposal = build_impact_proposal_from_files(CANDIDATE_PACKET_PATH, PROCESS_FIXTURE_PATH)

    assert ["python3", "-m", "py_compile", "ppd/logic/process_model_impact_proposal.py"] in proposal[
        "offline_validation_commands"
    ]
    assert ["python3", "ppd/tests/test_process_model_impact_proposal.py"] in proposal[
        "offline_validation_commands"
    ]


if __name__ == "__main__":
    test_build_impact_proposal_covers_required_categories()
    test_build_impact_proposal_does_not_mutate_inputs()
    test_affected_processes_are_derived_from_fixture_permit_types()
    test_proposal_includes_offline_validation_commands()
