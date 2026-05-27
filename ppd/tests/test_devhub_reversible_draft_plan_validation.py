import json
from pathlib import Path

from ppd.devhub.reversible_draft_plan_validation import (
    assert_reversible_draft_plan,
    validate_reversible_draft_plan,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub_reversible_draft_plans" / "invalid_cases.json"


def test_valid_reversible_draft_plan_is_accepted() -> None:
    plan = {
        "plan_id": "devhub-draft-demo-valid",
        "attendance": "required",
        "required_user_facts": ["site_address", "permit_scope"],
        "source_evidence_ids": ["ppd-devhub-guide-submit-permit-application", "ppd-submit-plans-online"],
        "preview": {
            "redacted": True,
            "fields": [
                {"label": "Project address", "user_fact_id": "site_address"},
                {"label": "Scope summary", "user_fact_id": "permit_scope"},
            ],
        },
        "steps": [
            {
                "action": "fill_field",
                "selector": "[data-testid='project-address']",
                "selector_confidence": "high",
                "value_ref": "site_address",
            },
            {
                "action": "save_draft",
                "selector": "button[aria-label='Save draft']",
                "selector_confidence": "high",
            },
        ],
    }

    assert validate_reversible_draft_plan(plan) == []
    assert_reversible_draft_plan(plan)


def test_invalid_reversible_draft_plan_cases_are_rejected() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    for case in fixture["cases"]:
        issues = validate_reversible_draft_plan(case["plan"])
        codes = {issue.code for issue in issues}
        assert case["expected_code"] in codes, case["name"]


def test_assert_reversible_draft_plan_raises_with_issue_codes() -> None:
    plan = {
        "plan_id": "devhub-draft-demo-private-value",
        "required_user_facts": ["site_address"],
        "source_evidence_ids": ["ppd-devhub-guide-submit-permit-application"],
        "preview": {"redacted": True, "fields": [{"label": "Address", "user_fact_id": "site_address"}]},
        "steps": [
            {
                "action": "fill_field",
                "selector": "[data-testid='project-address']",
                "selector_confidence": "high",
                "value": "123 Private Address",
            }
        ],
    }

    try:
        assert_reversible_draft_plan(plan)
    except ValueError as exc:
        assert "private_value" in str(exc)
    else:
        raise AssertionError("Expected private value rejection")
