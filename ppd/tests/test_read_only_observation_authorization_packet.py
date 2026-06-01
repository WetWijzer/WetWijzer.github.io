import json
from pathlib import Path

import pytest

from ppd.devhub.read_only_observation_authorization import (
    AuthorizationPacketError,
    validate_read_only_observation_authorization_packet,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub"
    / "read_only_observation_authorization_packet_v1.json"
)


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_first_read_only_observation_authorization_packet_is_valid():
    packet = load_fixture()

    authorization = validate_read_only_observation_authorization_packet(packet)

    assert authorization.packet_id == "devhub-read-only-observation-renewal-authorization-v1-fixture"


def test_packet_authorizes_no_live_devhub_or_stateful_artifacts():
    packet = load_fixture()

    assert packet["live_devhub_opening_authorized"] is False
    assert packet["auth_state_storage_authorized"] is False
    assert packet["active_devhub_mutation_authorized"] is False
    assert "open_devhub" in packet["prohibited_actions"]
    assert "store_auth_state" in packet["prohibited_actions"]
    assert "create_screenshots_traces_or_har" in packet["prohibited_actions"]


def test_packet_records_attendance_redaction_stop_and_handoff_requirements():
    packet = load_fixture()

    assert packet["synthetic_user_attendance_prerequisites"]
    assert packet["allowed_read_only_surfaces"]
    assert packet["redaction_requirements"]
    assert packet["stop_conditions"]
    assert packet["manual_handoff_points"]
    assert packet["observation_evidence_placeholders"]


def test_packet_contains_only_exact_offline_validation_commands():
    packet = load_fixture()

    assert packet["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/devhub/read_only_observation_authorization.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_read_only_observation_authorization_packet.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def test_validator_rejects_missing_required_prohibition():
    packet = load_fixture()
    packet["prohibited_actions"] = [
        action for action in packet["prohibited_actions"] if action != "submit_requests"
    ]

    with pytest.raises(AuthorizationPacketError):
        validate_read_only_observation_authorization_packet(packet)
