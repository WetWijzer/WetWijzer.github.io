from __future__ import annotations

import copy

import pytest

from ppd.devhub.draft_executor_dry_run_packet import assert_dry_run_packet, validate_dry_run_packet


def _valid_packet() -> dict[str, object]:
    return {
        "packet_id": "synthetic-devhub-draft-dry-run-001",
        "run_mode": "reversible_draft_executor_dry_run",
        "live_devhub_session": False,
        "required_user_facts": [
            {
                "fact_id": "site_address",
                "source_evidence_ids": ["ev-devhub-submit-guide"],
                "value_policy": "value_ref_only",
            },
            {
                "fact_id": "permit_scope",
                "provenance": {"source_evidence_ids": ["ev-apply-permits"]},
                "value_policy": "value_ref_only",
            },
        ],
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
                "selector_confidence": 0.95,
                "value_ref": "permit_scope",
            },
        ],
        "dry_run_result": "preview_only_no_devhub_state_change",
    }


def test_valid_reversible_draft_executor_dry_run_packet_is_accepted() -> None:
    packet = _valid_packet()

    assert validate_dry_run_packet(packet) == []
    assert_dry_run_packet(packet)


@pytest.mark.parametrize(
    ("name", "patch", "expected_code"),
    [
        ("private field value", {"steps": [{"action": "fill_field", "selector": "[data-testid='project-address']", "selector_confidence": "high", "value": "123 Private Street"}]}, "private_value"),
        ("missing fact provenance", {"required_user_facts": ["site_address"]}, "missing_fact_provenance"),
        ("unknown fact reference", {"steps": [{"action": "fill_field", "selector": "[data-testid='project-address']", "selector_confidence": "high", "value_ref": "unproven_fact"}]}, "missing_fact_provenance"),
        ("low confidence selector", {"steps": [{"action": "fill_field", "selector": "input", "selector_confidence": 0.42, "value_ref": "site_address"}]}, "low_confidence_selector"),
        ("browser state", {"browser_state": {"origins": []}}, "browser_artifact"),
        ("screenshot", {"screenshot_path": "/tmp/devhub.png"}, "browser_artifact"),
        ("trace", {"trace_path": "/tmp/devhub-trace.zip"}, "browser_artifact"),
        ("har", {"har_data": {"log": {}}}, "browser_artifact"),
        ("cookies", {"cookies": [{"name": "session", "value": "redacted"}]}, "browser_artifact"),
        ("credentials", {"credentials": {"username": "redacted"}}, "private_value"),
        ("save control", {"steps": [{"action": "save_draft", "selector": "button[aria-label='Save']", "selector_confidence": "high"}]}, "consequential_control"),
        ("continue control", {"steps": [{"action": "continue", "selector": "button[aria-label='Continue']", "selector_confidence": "high"}]}, "consequential_control"),
        ("submit control", {"steps": [{"action": "submit_application", "selector": "button[aria-label='Submit']", "selector_confidence": "high"}]}, "consequential_control"),
        ("certify control", {"steps": [{"action": "certify", "selector": "[data-testid='certify']", "selector_confidence": "high"}]}, "consequential_control"),
        ("upload control", {"steps": [{"action": "upload", "selector": "[data-testid='upload']", "selector_confidence": "high"}]}, "consequential_control"),
        ("payment control", {"steps": [{"action": "enter_payment_details", "selector": "[data-testid='payment']", "selector_confidence": "high"}]}, "consequential_control"),
        ("schedule control", {"steps": [{"action": "schedule_inspection", "selector": "[data-testid='schedule']", "selector_confidence": "high"}]}, "consequential_control"),
        ("official state changed flag", {"official_devhub_state_changed": True}, "official_state_changed"),
        ("official state changed outcome", {"outcome": "submitted"}, "official_state_changed"),
    ],
)
def test_reversible_draft_executor_dry_run_packet_rejects_unsafe_content(name: str, patch: dict[str, object], expected_code: str) -> None:
    packet = _valid_packet()
    packet.update(copy.deepcopy(patch))

    codes = {issue.code for issue in validate_dry_run_packet(packet)}

    assert expected_code in codes, name


def test_assert_dry_run_packet_reports_issue_codes() -> None:
    packet = _valid_packet()
    packet["cookies"] = [{"name": "session", "value": "redacted"}]

    with pytest.raises(ValueError, match="browser_artifact"):
        assert_dry_run_packet(packet)
