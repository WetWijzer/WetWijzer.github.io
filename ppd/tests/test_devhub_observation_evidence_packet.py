import json
from pathlib import Path

import pytest

from ppd.devhub.observation_evidence_packet import (
    REQUIRED_ATTESTATIONS,
    build_observation_evidence_packet,
    validate_observation_evidence_packet,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub"


def load_fixture(name: str):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_builds_expected_packet_from_attended_dry_run_runbook_v1():
    runbook = load_fixture("attended_observation_dry_run_runbook_v1.json")
    expected = load_fixture("observation_evidence_packet_v1.json")

    assert build_observation_evidence_packet(runbook) == expected


def test_packet_fixture_has_required_reviewer_safe_attestations():
    packet = load_fixture("observation_evidence_packet_v1.json")

    validate_observation_evidence_packet(packet)

    assert packet["artifact_policy"] == {
        "stores_credentials": False,
        "stores_session_state": False,
        "stores_screenshots": False,
        "stores_traces": False,
        "stores_har": False,
        "stores_raw_authenticated_values": False,
        "stores_downloads": False,
    }
    for row in packet["evidence_rows"]:
        assert row["redaction_status"] == "synthetic_fixture_only_no_private_values"
        assert row["owner_fields"]["surface_owner"]
        assert row["owner_fields"]["review_owner"]
        assert row["owner_fields"]["evidence_owner"]
        assert row["offline_validation_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
        assert all(row["attestations"][name] is True for name in REQUIRED_ATTESTATIONS)


def test_rejects_forbidden_authenticated_artifacts():
    packet = load_fixture("observation_evidence_packet_v1.json")
    packet["evidence_rows"][0]["screenshot"] = "forbidden.png"

    with pytest.raises(ValueError, match="forbidden DevHub artifact key"):
        validate_observation_evidence_packet(packet)


def test_rejects_missing_stop_before_action_gate():
    packet = load_fixture("observation_evidence_packet_v1.json")
    packet["evidence_rows"][0]["stop_before_action_gates"] = []

    with pytest.raises(ValueError, match="stop_before_action_gates"):
        validate_observation_evidence_packet(packet)


def test_rejects_any_false_required_attestation():
    packet = load_fixture("observation_evidence_packet_v1.json")
    packet["evidence_rows"][0]["attestations"]["no_payment"] = False

    with pytest.raises(ValueError, match="no_payment"):
        validate_observation_evidence_packet(packet)
