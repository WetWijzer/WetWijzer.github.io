import json
from pathlib import Path

import pytest

from ppd.validation.devhub_read_only_observation_runbook_v2 import (
    assert_valid_runbook,
    validation_error_codes,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_read_only_observation_runbook_v2"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_attended_read_only_observation_runbook_v2_passes() -> None:
    assert validation_error_codes(_load_fixture("valid_runbook.json")) == set()


def test_invalid_runbook_rejects_missing_required_sections_and_forbidden_claims() -> None:
    codes = validation_error_codes(_load_fixture("invalid_runbook.json"))

    assert "missing_observation_steps" in codes
    assert "missing_metadata_only_capture_fields" in codes
    assert "missing_accessible_role_placeholders" in codes
    assert "missing_validation_message_placeholders" in codes
    assert "missing_redacted_journal_examples" in codes
    assert "missing_stop_before_action_checkpoints" in codes
    assert "missing_reviewer_dispositions" in codes
    assert "missing_validation_commands" in codes
    assert "forbidden_private_or_raw_artifacts" in codes
    assert "forbidden_live_devhub_execution_claim" in codes
    assert "forbidden_official_action_completion_claim" in codes
    assert "forbidden_legal_or_permitting_guarantee" in codes
    assert "forbidden_active_mutation_flags" in codes


def test_assert_valid_runbook_raises_with_deterministic_codes() -> None:
    with pytest.raises(ValueError) as excinfo:
        assert_valid_runbook(_load_fixture("invalid_runbook.json"))

    message = str(excinfo.value)
    assert "missing_observation_steps" in message
    assert "forbidden_active_mutation_flags" in message
