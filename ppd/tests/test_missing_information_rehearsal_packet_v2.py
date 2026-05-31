from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ppd.agent_readiness.missing_information_rehearsal_packet_v2 import (
    MissingInformationRehearsalPacketV2Error,
    assert_valid_missing_information_rehearsal_packet_v2,
    load_missing_information_rehearsal_packet_v2,
    validate_missing_information_rehearsal_packet_v2,
)

FIXTURES = Path(__file__).parent / "fixtures"
PACKET = FIXTURES / "missing_information_rehearsal_packet_v2" / "packet.json"


def test_fixture_packet_covers_required_workflows_and_gap_categories() -> None:
    packet = load_missing_information_rehearsal_packet_v2(PACKET)

    assert validate_missing_information_rehearsal_packet_v2(packet) == []
    assert {case["workflow"] for case in packet["synthetic_user_cases"]} == {
        "building",
        "trade",
        "solar",
        "demolition",
        "sign",
        "urban_forestry",
        "corrections",
    }
    for case in packet["synthetic_user_cases"]:
        assert case["missing_facts"]
        assert case["missing_documents"]
        assert case["required_confirmations"]
        assert case["blocked_actions"]
        assert case["next_safe_actions"]
        assert case["citation_references"]
        assert case["reviewer_disposition_placeholder"]["status"] == "pending_human_review"


def test_fixture_packet_is_offline_and_non_mutating() -> None:
    packet = load_missing_information_rehearsal_packet_v2(PACKET)

    assert all(packet["boundaries"].values())
    assert packet["validation_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    for case in packet["synthetic_user_cases"]:
        assert case["offline_validation_commands"] == packet["validation_commands"]
        for action in case["blocked_actions"]:
            assert action["blocked"] is True
            assert action["requires_confirmation_before_unblock"] is True
        for action in case["next_safe_actions"]:
            assert action["requires_devhub"] is False
            assert action["fills_form"] is False
            assert action["uploads"] is False
            assert action["submits"] is False
            assert action["pays_fee"] is False
            assert action["schedules_inspection"] is False


def test_validator_rejects_private_fact_markers_and_unsafe_actions() -> None:
    packet = load_missing_information_rehearsal_packet_v2(PACKET)
    unsafe = copy.deepcopy(packet)
    unsafe["synthetic_user_cases"][0]["site_address"] = "synthetic private address value"
    unsafe["synthetic_user_cases"][0]["next_safe_actions"][0]["requires_devhub"] = True
    unsafe["synthetic_user_cases"][0]["blocked_actions"][0]["blocked"] = False

    errors = validate_missing_information_rehearsal_packet_v2(unsafe)

    assert any("private-data key" in error for error in errors)
    assert any("requires_devhub must be false" in error for error in errors)
    assert any("must stay blocked" in error for error in errors)
    with pytest.raises(MissingInformationRehearsalPacketV2Error):
        assert_valid_missing_information_rehearsal_packet_v2(unsafe)
