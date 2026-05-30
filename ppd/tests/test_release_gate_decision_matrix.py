from copy import deepcopy
from pathlib import Path

import pytest

from ppd.release_gate_decision_matrix import (
    DEPENDENCY_ORDER,
    REQUIRED_ATTESTATIONS,
    ReleaseGateDecisionMatrixError,
    build_release_gate_decision_matrix,
    matrix_from_fixture,
    validate_release_gate_decision_matrix,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "release_gate_decision_matrix_v1" / "evidence_bundle.json"


def _matrix() -> dict:
    return matrix_from_fixture(FIXTURE_PATH)


def _first_problem_for(mutator) -> str:
    matrix = _matrix()
    mutator(matrix)
    problems = validate_release_gate_decision_matrix(matrix)
    assert problems
    return "; ".join(problems)


def test_matrix_from_fixture_returns_cited_pass_defer_block_rows() -> None:
    matrix = matrix_from_fixture(FIXTURE_PATH)
    rows = {row["candidate_id"]: row for row in matrix["rows"]}

    assert matrix["schema_version"] == "ppd.release_gate_decision_matrix.v1"
    assert matrix["overall_decision"] == "block"
    assert rows["rc-pass-001"]["decision"] == "pass"
    assert rows["rc-defer-001"]["decision"] == "defer"
    assert rows["rc-block-001"]["decision"] == "block"
    assert "public:pass:current" in rows["rc-pass-001"]["citations"]
    assert "gap:defer:open" in rows["rc-defer-001"]["citations"]
    assert "journal:block:blocker" in rows["rc-block-001"]["citations"]


def test_matrix_includes_reviewer_signoff_dependency_rollback_and_offline_validation() -> None:
    matrix = matrix_from_fixture(FIXTURE_PATH)
    row = matrix["rows"][0]

    assert matrix["reviewer_signoff_fields"] == {
        "reviewer_name": None,
        "reviewer_role": None,
        "reviewed_at": None,
        "decision_acknowledged": False,
        "notes": None,
    }
    assert row["reviewer_signoff"] == matrix["reviewer_signoff_fields"]
    assert tuple(matrix["dependency_order"]) == DEPENDENCY_ORDER
    assert "reviewer_signoff" in matrix["dependency_order"]
    assert "restore_last_passing_fixture_bundle" in matrix["rollback_checkpoints"]
    assert ["python3", "-m", "py_compile", "ppd/release_gate_decision_matrix.py"] in matrix["offline_validation_commands"]


def test_required_safety_attestations_are_explicit_and_true_for_fixture() -> None:
    matrix = matrix_from_fixture(FIXTURE_PATH)

    assert set(matrix["attestations"]) == set(REQUIRED_ATTESTATIONS)
    assert matrix["attestations"] == {
        "no_live_crawl": True,
        "no_devhub": True,
        "no_private_artifact": True,
        "no_official_action": True,
        "no_active_promotion": True,
    }


def test_failed_attestation_blocks_candidate() -> None:
    evidence = {
        "attestations_v1": {
            "no_live_crawl": False,
            "no_devhub": True,
            "no_private_artifact": True,
            "no_official_action": True,
            "no_active_promotion": True,
        },
        "release_candidate_evidence_bundle_v1": {
            "candidates": [
                {
                    "candidate_id": "rc-attestation-block",
                    "title": "Blocked by failed attestation",
                    "evidence_ids": ["rc:attestation:block"],
                }
            ]
        },
        "readiness_gap_report_v1": {"gaps": []},
        "public_source_refresh_evidence_intake_packet_v1": {"refresh_evidence": []},
        "devhub_observation_evidence_intake_packet_v1": {"observations": []},
        "action_journal_replay_findings_v1": {"findings": []},
    }

    matrix = build_release_gate_decision_matrix(evidence)

    assert matrix["overall_decision"] == "block"
    assert matrix["rows"][0]["decision"] == "block"
    assert "required safety attestations failed: no_live_crawl" in matrix["rows"][0]["reasons"]


def test_missing_required_input_section_raises_clear_error() -> None:
    with pytest.raises(ReleaseGateDecisionMatrixError, match="missing required evidence sections"):
        build_release_gate_decision_matrix({})


def test_validator_rejects_uncited_decision_rows() -> None:
    problem = _first_problem_for(lambda matrix: matrix["rows"][0].__setitem__("citations", []))
    assert "rows[0].citations must be non-empty" in problem


def test_validator_rejects_missing_reviewer_signoff_fields() -> None:
    def mutate(matrix: dict) -> None:
        matrix["rows"][0]["reviewer_signoff"] = {"decision_acknowledged": False}

    problem = _first_problem_for(mutate)
    assert "rows[0].reviewer_signoff missing required fields" in problem


def test_validator_rejects_missing_unresolved_blocker_handling() -> None:
    def mutate(matrix: dict) -> None:
        del matrix["rows"][1]["unresolved_blocker_handling"]

    problem = _first_problem_for(mutate)
    assert "rows[1].unresolved_blocker_handling must be present" in problem


def test_validator_rejects_missing_dependency_order() -> None:
    problem = _first_problem_for(lambda matrix: matrix.__setitem__("dependency_order", []))
    assert "dependency_order must include the required release gate order" in problem


def test_validator_rejects_missing_rollback_checkpoints() -> None:
    problem = _first_problem_for(lambda matrix: matrix.__setitem__("rollback_checkpoints", []))
    assert "rollback_checkpoints must include the required rollback checkpoints" in problem


def test_validator_rejects_private_authenticated_raw_pdf_session_and_browser_artifacts() -> None:
    examples = [
        {"private_artifact_ref": "private-artifact:devhub-session"},
        {"authenticated_artifact": "https://example.test/authenticated/download"},
        {"raw_pdf_data": "raw_pdf fixture body"},
        {"session_state": "session-state.json"},
        {"browser_state": "browser-state.json"},
    ]
    for unsafe in examples:
        matrix = _matrix()
        matrix["rows"][0]["unsafe_fixture"] = unsafe
        problems = validate_release_gate_decision_matrix(matrix)
        assert any("private, authenticated, raw, session, or browser artifact" in problem for problem in problems)


def test_validator_rejects_live_execution_and_promotion_claims() -> None:
    problem = _first_problem_for(lambda matrix: matrix["rows"][0].__setitem__("summary", "live promotion complete"))
    assert "live execution or promotion claim" in problem


def test_validator_rejects_legal_or_permitting_outcome_guarantees() -> None:
    problem = _first_problem_for(lambda matrix: matrix["rows"][0].__setitem__("summary", "permit will be approved"))
    assert "legal or permitting outcome guarantee" in problem


def test_validator_rejects_consequential_action_language() -> None:
    problem = _first_problem_for(lambda matrix: matrix["rows"][0].__setitem__("next_step", "submit the permit application"))
    assert "consequential action language" in problem


def test_validator_rejects_active_mutation_flags_for_release_surfaces() -> None:
    for flag in (
        "active_source_mutation",
        "active_surface_registry_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    ):
        matrix = _matrix()
        matrix["rows"][0][flag] = True
        problems = validate_release_gate_decision_matrix(matrix)
        assert any("active mutation flag is not allowed" in problem for problem in problems)


def test_builder_rejects_uncited_release_candidates() -> None:
    import json

    evidence = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    evidence = deepcopy(evidence)
    evidence["release_candidate_evidence_bundle_v1"]["candidates"][0]["evidence_ids"] = []

    with pytest.raises(ReleaseGateDecisionMatrixError, match="each release candidate requires evidence_ids"):
        build_release_gate_decision_matrix(evidence)
