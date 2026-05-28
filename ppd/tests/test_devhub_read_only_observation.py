from __future__ import annotations

import pytest

from ppd.devhub.read_only_observation import (
    ObservationPacketRejected,
    is_read_only_observation_packet_safe,
    validate_read_only_observation_packet,
)


def test_accepts_attended_read_only_structural_observation() -> None:
    packet = {
        "packet_type": "devhub_attended_read_only_observation",
        "attendance": {
            "login_completed_by": "human_user",
            "mfa_completed_by": "human_user_if_presented",
            "captcha_completed_by": "human_user_if_presented",
        },
        "surface": {
            "name": "My Permits & Requests",
            "url_host": "devhub.portlandoregon.gov",
            "heading": "My Permits & Requests",
        },
        "visible_structure": {
            "landmarks": ["main", "navigation"],
            "read_only_sections": ["permit list", "status summary", "fee notice summary"],
            "fields": [
                {"label": "Permit number", "presence": "visible", "value_redacted": True},
                {"label": "Status", "presence": "visible", "value_redacted": True},
            ],
        },
        "notes": "Observed after attended sign in. No credentials, browser state, screenshots, traces, or private values recorded.",
    }

    assert validate_read_only_observation_packet(packet) is packet
    assert is_read_only_observation_packet_safe(packet) is True


@pytest.mark.parametrize(
    "packet, expected_reason",
    [
        ({"browser_state": {"localStorage": {}}}, "browser state"),
        ({"storage_state": "state.json"}, "browser state"),
        ({"cookies": [{"name": "session"}]}, "cookies"),
        ({"credentials": {"username": "person@example.test"}}, "credentials"),
        ({"password": "not-allowed"}, "credentials"),
        ({"screenshot_path": "devhub.png"}, "screenshots"),
        ({"trace_path": "trace.zip"}, "traces"),
        ({"har_data": {"log": {}}}, "HAR"),
        ({"fields": [{"label": "Owner", "raw_value": "Private Name"}]}, "private field values"),
        ({"controls": [{"role": "button", "label": "Upload corrections"}]}, "controls"),
        ({"actions": [{"accessible_name": "Submit permit request"}]}, "controls"),
        ({"buttons": [{"text": "Schedule inspection"}]}, "controls"),
        ({"links": [{"text": "Cancel request"}]}, "controls"),
        ({"control": {"role": "button", "text": "Pay fees"}}, "controls"),
        ({"note": "The script automated login and then observed the page."}, "login"),
        ({"note": "CAPTCHA was solved automatically before observation."}, "CAPTCHA"),
        ({"mfa_automated": True}, "MFA"),
    ],
)
def test_rejects_prohibited_observation_packet_content(packet: dict[str, object], expected_reason: str) -> None:
    with pytest.raises(ObservationPacketRejected) as exc_info:
        validate_read_only_observation_packet(packet)

    assert expected_reason.lower() in str(exc_info.value).lower()
    assert is_read_only_observation_packet_safe(packet) is False


def test_rejection_reports_all_detected_policy_violations() -> None:
    packet = {
        "cookies": [{"name": "session"}],
        "controls": [{"label": "Submit payment"}],
        "note": "MFA was automated by the script.",
    }

    with pytest.raises(ObservationPacketRejected) as exc_info:
        validate_read_only_observation_packet(packet)

    reasons = [error.reason for error in exc_info.value.errors]
    assert any("cookies" in reason for reason in reasons)
    assert any("controls" in reason for reason in reasons)
    assert any("MFA" in reason for reason in reasons)
