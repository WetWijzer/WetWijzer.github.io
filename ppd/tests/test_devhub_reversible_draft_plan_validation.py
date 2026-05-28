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
                "action": "select_option",
                "selector": "[data-testid='permit-type']",
                "selector_confidence": "high",
                "value_ref": "permit_scope",
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


def test_sensitive_packet_artifacts_are_rejected() -> None:
    base_plan = {
        "plan_id": "devhub-draft-demo-valid",
        "attendance": "required",
        "required_user_facts": ["site_address"],
        "source_evidence_ids": ["ppd-devhub-guide-submit-permit-application"],
        "preview": {"redacted": True, "fields": [{"label": "Address", "user_fact_id": "site_address"}]},
        "steps": [
            {
                "action": "fill_field",
                "selector": "[data-testid='project-address']",
                "selector_confidence": "high",
                "value_ref": "site_address",
            }
        ],
    }
    cases = [
        ("low-confidence selector", {"steps": [{"action": "fill_field", "selector": "input", "selector_confidence": "low", "value_ref": "site_address"}]}, "ambiguous_selector"),
        ("save side effect", {"steps": [{"action": "save_draft", "selector": "button[aria-label='Save draft']", "selector_confidence": "high"}]}, "draft_persistence"),
        ("continue side effect", {"steps": [{"action": "continue", "selector": "button[aria-label='Continue']", "selector_confidence": "high"}]}, "draft_persistence"),
        ("browser state", {"browser_state": {"origins": []}}, "browser_state"),
        ("cookies", {"cookies": [{"name": "session", "value": "redacted"}]}, "cookies"),
        ("screenshot", {"screenshot_path": "/tmp/devhub.png"}, "screenshot"),
        ("trace", {"trace_path": "/tmp/trace.zip"}, "trace"),
        ("har", {"har_path": "/tmp/devhub.har"}, "har_data"),
        ("authenticated live url", {"handoff": {"url": "https://devhub.portlandoregon.gov/account", "requires_auth": True}}, "authenticated_live_url"),
    ]

    for name, patch, expected_code in cases:
        plan = dict(base_plan)
        plan.update(patch)
        issues = validate_reversible_draft_plan(plan)
        codes = {issue.code for issue in issues}
        assert expected_code in codes, name


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
