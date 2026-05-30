from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from ppd.daemon.inactive_fixture_promotion_diff_ledger_v1 import (
    validate_inactive_fixture_promotion_diff_ledger_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "inactive_fixture_promotion_diff_ledger_v1"


def _valid_ledger() -> dict:
    return json.loads((FIXTURE_DIR / "valid_review_only_ledger.json").read_text())


def _errors(ledger: dict) -> tuple[str, ...]:
    result = validate_inactive_fixture_promotion_diff_ledger_v1(ledger)
    return result.errors


def test_valid_review_only_ledger_passes() -> None:
    result = validate_inactive_fixture_promotion_diff_ledger_v1(_valid_ledger())

    assert result.valid is True
    assert result.errors == ()


def test_rejects_missing_file_level_diff_summary() -> None:
    ledger = _valid_ledger()
    ledger["file_diffs"][0].pop("file_level_diff_summary")

    assert any("file_level_diff_summary" in error for error in _errors(ledger))


def test_rejects_missing_fixture_family_readiness_row() -> None:
    ledger = _valid_ledger()
    ledger["fixture_family_readiness"] = []

    errors = _errors(ledger)

    assert any("fixture_family_readiness" in error for error in errors)
    assert any("missing row" in error for error in errors)


def test_rejects_uncited_readiness_evidence() -> None:
    ledger = _valid_ledger()
    ledger["fixture_family_readiness"][0]["readiness_evidence"][0]["citations"] = []

    assert any("citations is required" in error for error in _errors(ledger))


def test_rejects_missing_blocked_promotion_explanation() -> None:
    ledger = _valid_ledger()
    ledger["blocked_promotions"][0]["explanation"] = ""

    assert any("blocked_promotions[0].explanation" in error for error in _errors(ledger))


def test_rejects_missing_reviewer_owner_or_rollback_note() -> None:
    ledger = _valid_ledger()
    ledger["review"]["reviewer_owner"] = ""
    ledger["review"]["rollback_note"] = ""

    errors = _errors(ledger)

    assert any("review.reviewer_owner" in error for error in errors)
    assert any("review.rollback_note" in error for error in errors)


def test_rejects_private_authenticated_session_browser_artifacts() -> None:
    ledger = _valid_ledger()
    ledger["artifact_refs"] = ["ppd/tests/fixtures/private-devhub-session/storage_state.json"]

    assert any("private/authenticated/session/browser artifact" in error for error in _errors(ledger))


def test_rejects_raw_crawl_pdf_downloaded_data() -> None:
    ledger = _valid_ledger()
    ledger["artifact_refs"] = ["ppd/tests/fixtures/raw-crawl-output/downloaded-data/raw-pdf.bin"]

    assert any("raw crawl/PDF/downloaded data artifact" in error for error in _errors(ledger))


def test_rejects_live_execution_or_promotion_claims() -> None:
    ledger = _valid_ledger()
    ledger["notes"] = "Promotion completed after live execution."

    assert any("live execution or promotion claim" in error for error in _errors(ledger))


def test_rejects_legal_or_permitting_outcome_guarantees() -> None:
    ledger = _valid_ledger()
    ledger["notes"] = "This fixture means the permit will be approved."

    assert any("legal or permitting outcome guarantee" in error for error in _errors(ledger))


def test_rejects_consequential_action_language() -> None:
    ledger = _valid_ledger()
    ledger["next_action"] = "submit permit"

    assert any("consequential action language" in error for error in _errors(ledger))


def test_rejects_active_mutation_flags() -> None:
    ledger = _valid_ledger()
    ledger["mutation_flags"]["fixture_mutation_enabled"] = True
    ledger["active_prompt_mutation"] = False

    errors = _errors(ledger)

    assert any("mutation_flags.fixture_mutation_enabled" in error for error in errors)
    assert any("active mutation flag" in error for error in errors)


def test_rejects_any_active_fixture_prompt_process_guardrail_release_or_agent_flag_name() -> None:
    base = _valid_ledger()
    flag_names = (
        "active_fixture_mutation",
        "active_prompt_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    )

    for flag_name in flag_names:
        ledger = deepcopy(base)
        ledger[flag_name] = False
        assert any("active mutation flag" in error for error in _errors(ledger)), flag_name
