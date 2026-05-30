from __future__ import annotations

from pathlib import Path
import json

from ppd.devhub.review_readiness_checklist_v3 import (
    assert_checklist_v3_ready,
    load_checklist,
    validate_checklist_v3,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "review_readiness_checklist_v3"


def test_valid_fixture_is_ready() -> None:
    checklist = load_checklist(FIXTURE_DIR / "valid_checklist.json")

    result = validate_checklist_v3(checklist)

    assert result.ok, result.to_dict()
    assert result.errors == ()
    assert_checklist_v3_ready(checklist)


def test_invalid_fixture_rejects_required_failure_classes() -> None:
    checklist = load_checklist(FIXTURE_DIR / "invalid_checklist.json")

    result = validate_checklist_v3(checklist)

    assert not result.ok
    codes = {error.code for error in result.errors}
    assert "uncited_row" in codes
    assert "missing_acceptance_criteria" in codes
    assert "missing_unresolved_deferral_disposition" in codes
    assert "missing_rollback_verification" in codes
    assert "missing_reviewer_owner" in codes
    assert "private_or_authenticated_fact" in codes
    assert "raw_artifact" in codes
    assert "live_execution_claim" in codes
    assert "outcome_guarantee" in codes
    assert "consequential_action_language" in codes
    assert "active_mutation_flag" in codes


def test_assertion_reports_rejection() -> None:
    checklist = load_checklist(FIXTURE_DIR / "invalid_checklist.json")

    try:
        assert_checklist_v3_ready(checklist)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("invalid checklist should be rejected")

    assert "attended review readiness checklist v3 rejected" in message
    assert "uncited_row" in message


def test_each_disallowed_phrase_family_is_scanned_recursively() -> None:
    base = json.loads((FIXTURE_DIR / "valid_checklist.json").read_text(encoding="utf-8"))
    base["rows"][0]["notes"] = {
        "private_fact": "authenticated account fact: permit number: 24-000000",
        "artifact": "raw PDF artifact /tmp/devhub.pdf",
        "live": "clicked in live DevHub",
        "guarantee": "will be approved",
        "final_action": "final payment",
    }
    base["rows"][0]["prompt_mutation"] = "enabled"

    result = validate_checklist_v3(base)

    codes = {error.code for error in result.errors}
    assert {
        "private_or_authenticated_fact",
        "raw_artifact",
        "live_execution_claim",
        "outcome_guarantee",
        "consequential_action_language",
        "active_mutation_flag",
    }.issubset(codes)
