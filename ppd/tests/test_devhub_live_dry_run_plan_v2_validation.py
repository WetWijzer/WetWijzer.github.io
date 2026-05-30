from pathlib import Path

import pytest

from ppd.devhub_live_dry_run_plan_v2_validation import (
    assert_valid_attended_devhub_live_dry_run_plan_v2,
    validate_attended_devhub_live_dry_run_plan_v2,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_live_dry_run_plan_v2"


def _fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_accepts_cited_attended_read_only_plan() -> None:
    issues = validate_attended_devhub_live_dry_run_plan_v2(_fixture("valid_plan.md"))
    assert issues == []


def test_assert_helper_raises_with_codes() -> None:
    with pytest.raises(ValueError) as exc_info:
        assert_valid_attended_devhub_live_dry_run_plan_v2(_fixture("invalid_plan.md"))
    message = str(exc_info.value)
    assert "uncited_verification_step" in message
    assert "browser_automation" in message


@pytest.mark.parametrize(
    ("text", "expected_code"),
    [
        ("Verify the permit record matches the address.", "uncited_verification_step"),
        ("Login to DevHub and continue through MFA.", "missing_manual_login_mfa_captcha_boundary"),
        ("Use the applicant password and bearer token.", "private_or_authenticated_value"),
        ("Persist storage_state and cookies.json for reuse.", "session_or_auth_artifact"),
        ("Attach screenshot, trace, and HAR references.", "screenshot_trace_har_reference"),
        ("Run Playwright to auto-click the live DevHub form.", "browser_automation"),
        ("The live DevHub submission was completed.", "live_devhub_completion_claim"),
        ("This guarantees permit approval and legal compliance.", "legal_or_permitting_guarantee"),
        ("Submit the permit application and pay the fee.", "consequential_action_enablement"),
        ("Set surface-registry mutation enabled true.", "active_mutation_flag"),
    ],
)

def test_rejects_specific_forbidden_plan_content(text: str, expected_code: str) -> None:
    codes = {issue.code for issue in validate_attended_devhub_live_dry_run_plan_v2(text)}
    assert expected_code in codes


def test_login_mfa_captcha_allowed_only_with_manual_boundary() -> None:
    text = "Attended read-only DevHub review. Manual handoff boundary: stop before login, MFA, or CAPTCHA."
    codes = {issue.code for issue in validate_attended_devhub_live_dry_run_plan_v2(text)}
    assert "missing_manual_login_mfa_captcha_boundary" not in codes
