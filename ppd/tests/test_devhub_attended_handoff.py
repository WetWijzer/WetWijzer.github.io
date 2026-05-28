from __future__ import annotations

from pathlib import Path

import pytest

from ppd.devhub.attended_handoff import (
    AttendedHandoffChecklist,
    HandoffValidationError,
    ScopeKind,
    load_default_attended_handoff_checklist,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "devhub" / "attended_handoff_checklist.json"


def _payload_from_fixture() -> dict[str, object]:
    checklist = AttendedHandoffChecklist.from_json_file(FIXTURE_PATH)
    return {
        "checklist_id": checklist.checklist_id,
        "manual_login_prerequisites": list(checklist.manual_login_prerequisites),
        "permitted_read_only_scopes": list(checklist.permitted_read_only_scopes),
        "permitted_reversible_draft_scopes": list(checklist.permitted_reversible_draft_scopes),
        "redaction_requirements": list(checklist.redaction_requirements),
        "exact_confirmation_boundaries": list(checklist.exact_confirmation_boundaries),
        "abort_conditions": list(checklist.abort_conditions),
        "forbidden_storage": list(checklist.forbidden_storage),
        "stores_browser_state": checklist.stores_browser_state,
        "stores_private_values": checklist.stores_private_values,
    }


def test_fixture_loads_without_private_state() -> None:
    checklist = AttendedHandoffChecklist.from_json_file(FIXTURE_PATH)

    assert checklist.checklist_id == "devhub-attended-handoff-v1"
    assert checklist.stores_browser_state is False
    assert checklist.stores_private_values is False
    assert "devhub_home_review" in checklist.permitted_scopes(ScopeKind.READ_ONLY)
    assert "form_field_draft_before_final_action" in checklist.permitted_scopes(ScopeKind.REVERSIBLE_DRAFT)


def test_default_loader_uses_committed_fixture() -> None:
    checklist = load_default_attended_handoff_checklist()

    assert "user_completes_portlandoregon_login" in checklist.manual_login_prerequisites
    assert "submit_permit_request" in checklist.exact_confirmation_boundaries
    assert "credentials" in checklist.redaction_requirements


def test_rejects_browser_state_storage() -> None:
    payload = _payload_from_fixture()
    payload["stores_browser_state"] = True

    with pytest.raises(HandoffValidationError, match="browser state"):
        AttendedHandoffChecklist.from_mapping(payload)


def test_rejects_missing_exact_confirmation_boundary() -> None:
    payload = _payload_from_fixture()
    payload["exact_confirmation_boundaries"] = [
        boundary
        for boundary in payload["exact_confirmation_boundaries"]
        if boundary != "enter_or_submit_payment_details"
    ]

    with pytest.raises(HandoffValidationError, match="enter_or_submit_payment_details"):
        AttendedHandoffChecklist.from_mapping(payload)


@pytest.mark.parametrize(
    ("scope", "expected"),
    [
        ("automate_captcha_challenge", "CAPTCHA"),
        ("automate_mfa_prompt", "MFA"),
        ("account_creation_flow", "account creation"),
        ("password_recovery_flow", "password recovery"),
        ("payment_entry", "payment"),
        ("submission_step", "submission"),
        ("certification_prompt", "certification"),
        ("upload_document", "upload"),
        ("schedule_inspection", "scheduling"),
        ("cancel_request", "cancellation"),
        ("auth_state_capture", "auth state"),
        ("cookie_capture", "cookies"),
        ("screenshot_capture", "screenshots"),
        ("trace_capture", "traces"),
        ("har_capture", "HAR data"),
    ],
)
def test_rejects_prohibited_read_only_scopes(scope: str, expected: str) -> None:
    payload = _payload_from_fixture()
    payload["permitted_read_only_scopes"] = [scope]

    with pytest.raises(HandoffValidationError, match=expected):
        AttendedHandoffChecklist.from_mapping(payload)


@pytest.mark.parametrize(
    ("scope", "expected"),
    [
        ("automate_captcha_challenge", "CAPTCHA"),
        ("automate_mfa_prompt", "MFA"),
        ("account_creation_flow", "account creation"),
        ("password_recovery_flow", "password recovery"),
        ("payment_entry", "payment"),
        ("submit_application", "submission"),
        ("certify_acknowledgement", "certification"),
        ("upload_staging", "upload"),
        ("scheduling_draft", "scheduling"),
        ("cancellation_draft", "cancellation"),
        ("auth_state_capture", "auth state"),
        ("cookies_capture", "cookies"),
        ("screenshot_capture", "screenshots"),
        ("trace_capture", "traces"),
        ("har_capture", "HAR data"),
    ],
)
def test_rejects_prohibited_reversible_draft_scopes(scope: str, expected: str) -> None:
    payload = _payload_from_fixture()
    payload["permitted_reversible_draft_scopes"] = [scope]

    with pytest.raises(HandoffValidationError, match=expected):
        AttendedHandoffChecklist.from_mapping(payload)


def test_rejects_local_private_paths_anywhere_in_checklist() -> None:
    payload = _payload_from_fixture()
    payload["permitted_read_only_scopes"] = ["review_/home/example/private-devhub-state.json"]

    with pytest.raises(HandoffValidationError, match="local private path"):
        AttendedHandoffChecklist.from_mapping(payload)
