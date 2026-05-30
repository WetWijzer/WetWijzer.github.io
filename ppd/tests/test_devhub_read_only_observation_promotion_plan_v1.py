from __future__ import annotations

import json
from pathlib import Path

from ppd.validation.devhub_read_only_observation_promotion_plan_v1 import (
    validate_devhub_read_only_observation_promotion_plan_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_read_only_observation_promotion_plan_v1"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text())


def test_valid_devhub_read_only_observation_promotion_plan_v1_passes() -> None:
    result = validate_devhub_read_only_observation_promotion_plan_v1(_load_fixture("valid_plan.json"))

    assert result.ok
    assert result.findings == ()


def test_devhub_read_only_observation_promotion_plan_v1_rejects_forbidden_content() -> None:
    result = validate_devhub_read_only_observation_promotion_plan_v1(
        _load_fixture("invalid_private_artifacts_and_mutations.json")
    )

    codes = {finding.code for finding in result.findings}
    assert not result.ok
    assert "private_account_value" in codes
    assert "browser_artifact" in codes
    assert "write_capable_action_evidence" in codes
    assert "automated_login_or_account_handling" in codes
    assert "consequential_action_language" in codes
    assert "missing_or_invalid_redaction_attendance_field" in codes
    assert "active_mutation_flag" in codes


def test_devhub_read_only_observation_promotion_plan_v1_rejects_missing_redaction_or_attendance() -> None:
    plan = {
        "plan_version": "devhub_read_only_observation_promotion_plan_v1",
        "scope": "devhub",
        "mode": "read_only_observation",
        "evidence": [],
    }

    result = validate_devhub_read_only_observation_promotion_plan_v1(plan)

    assert not result.ok
    assert {finding.code for finding in result.findings} == {
        "missing_or_invalid_redaction_attendance_field"
    }


def test_devhub_read_only_observation_promotion_plan_v1_rejects_active_mutation_flags() -> None:
    plan = _load_fixture("valid_plan.json")
    plan["mutation_flags"] = {
        "devhub": True,
        "surface_registry": True,
        "guardrail": True,
        "prompt": True,
        "release_state": True,
        "agent_state": True,
    }

    result = validate_devhub_read_only_observation_promotion_plan_v1(plan)

    assert not result.ok
    mutation_findings = [finding for finding in result.findings if finding.code == "active_mutation_flag"]
    assert len(mutation_findings) == 6
