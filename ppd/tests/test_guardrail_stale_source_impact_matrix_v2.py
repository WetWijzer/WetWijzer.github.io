import json
from pathlib import Path

from ppd.guardrail_stale_source_impact_matrix_v2 import (
    assert_guardrail_stale_source_impact_matrix_v2,
    validate_guardrail_stale_source_impact_matrix_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "guardrail_stale_source_impact_matrix_v2"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_matrix_passes_without_findings() -> None:
    matrix = _load_fixture("valid_matrix.json")

    findings = validate_guardrail_stale_source_impact_matrix_v2(matrix)

    assert findings == []
    assert_guardrail_stale_source_impact_matrix_v2(matrix)


def test_invalid_matrix_rejects_required_stale_source_omissions_and_forbidden_claims() -> None:
    matrix = _load_fixture("invalid_matrix.json")

    findings = validate_guardrail_stale_source_impact_matrix_v2(matrix)
    codes = {finding.code for finding in findings}

    assert "missing_impact_row" in codes
    assert "missing_stale_source_hold_reason" in codes
    assert "missing_re_extraction_placeholders" in codes
    assert "missing_user_facing_caution_templates" in codes
    assert "missing_blocked_action_reminders" in codes
    assert "missing_reviewer_dispositions" in codes
    assert "missing_validation_commands" in codes
    assert "forbidden_private_or_raw_artifact" in codes
    assert "forbidden_live_crawl_or_devhub_claim" in codes
    assert "forbidden_legal_or_permitting_guarantee" in codes
    assert "active_mutation_flag_enabled" in codes


def test_assertion_reports_invalid_matrix_locations() -> None:
    matrix = _load_fixture("invalid_matrix.json")

    try:
        assert_guardrail_stale_source_impact_matrix_v2(matrix)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("invalid matrix unexpectedly passed")

    assert "invalid guardrail stale-source impact matrix v2" in message
    assert "active_mutation_flags.requirements" in message
