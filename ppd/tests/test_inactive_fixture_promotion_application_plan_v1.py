from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from ppd.daemon.inactive_fixture_promotion_application_plan_v1 import (
    validate_inactive_fixture_promotion_application_plan_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "inactive_fixture_promotion_application_plan_v1"


def _valid_plan() -> dict:
    return json.loads((FIXTURE_DIR / "valid_plan.json").read_text())


def _errors(plan: dict) -> tuple[str, ...]:
    return validate_inactive_fixture_promotion_application_plan_v1(plan).errors


def test_valid_application_plan_passes() -> None:
    result = validate_inactive_fixture_promotion_application_plan_v1(_valid_plan())

    assert result.valid is True
    assert result.errors == ()


def test_rejects_uncited_application_steps() -> None:
    plan = _valid_plan()
    plan["ordered_application_steps"][0]["citations"] = []

    assert any("ordered_application_steps[0].citations" in error for error in _errors(plan))


def test_rejects_missing_affected_fixture_family_rows() -> None:
    plan = _valid_plan()
    plan["affected_fixture_family_rows"] = plan["affected_fixture_family_rows"][1:]

    assert any("missing row for public_source_refresh" in error for error in _errors(plan))


def test_rejects_missing_dependency_gates() -> None:
    plan = _valid_plan()
    plan["dependency_gates"] = []

    assert any("dependency_gates must include" in error for error in _errors(plan))


def test_rejects_missing_reviewer_owner_or_rollback_checkpoint() -> None:
    plan = _valid_plan()
    plan["ordered_application_steps"][0]["reviewer_owner"] = ""
    plan["ordered_application_steps"][0]["rollback_checkpoint"] = ""

    errors = _errors(plan)

    assert any("ordered_application_steps[0].reviewer_owner" in error for error in errors)
    assert any("ordered_application_steps[0].rollback_checkpoint" in error for error in errors)


def test_rejects_missing_validation_commands() -> None:
    plan = _valid_plan()
    plan["exact_offline_validation_commands"] = []

    assert any("exact_offline_validation_commands must include" in error for error in _errors(plan))


def test_rejects_private_authenticated_session_browser_artifacts() -> None:
    plan = _valid_plan()
    plan["artifact_refs"] = ["ppd/tests/fixtures/private-devhub-session/storage_state.json"]

    assert any("private/authenticated/session/browser artifact" in error for error in _errors(plan))


def test_rejects_raw_crawl_pdf_downloaded_data() -> None:
    plan = _valid_plan()
    plan["artifact_refs"] = ["ppd/tests/fixtures/raw-crawl-output/downloaded-data/raw-pdf.bin"]

    assert any("raw crawl/PDF/downloaded data" in error for error in _errors(plan))


def test_rejects_live_execution_or_promotion_complete_claims() -> None:
    plan = _valid_plan()
    plan["notes"] = "Promotion completed after live execution."

    assert any("live execution or promotion-complete claim" in error for error in _errors(plan))


def test_rejects_legal_or_permitting_outcome_guarantees() -> None:
    plan = _valid_plan()
    plan["notes"] = "This plan means the permit will be approved."

    assert any("legal or permitting outcome guarantee" in error for error in _errors(plan))


def test_rejects_consequential_action_language() -> None:
    plan = _valid_plan()
    plan["next_action"] = "submit permit"

    assert any("consequential action language" in error for error in _errors(plan))


def test_rejects_blocked_live_or_consequential_validation_commands() -> None:
    plan = _valid_plan()
    plan["exact_offline_validation_commands"].append(["python3", "scripts/permit_submission.py"])

    assert any("blocked live or consequential behavior" in error for error in _errors(plan))


def test_rejects_active_source_document_requirement_process_guardrail_prompt_release_fixture_or_agent_state_mutation_flags() -> None:
    base = _valid_plan()
    flag_names = (
        "active_source_mutation",
        "active_document_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_fixture_mutation",
        "active_agent_state_mutation",
    )

    for flag_name in flag_names:
        plan = deepcopy(base)
        plan[flag_name] = False
        assert any("active mutation flag" in error for error in _errors(plan)), flag_name
