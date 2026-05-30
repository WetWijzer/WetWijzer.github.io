from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from ppd.agent_readiness.post_release_monitoring_readiness_packet import (
    build_post_release_monitoring_readiness_packet,
    require_post_release_monitoring_readiness_packet,
    validate_post_release_monitoring_readiness_packet,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "post_release_monitoring_readiness" / "source_packets.json"


def _load_fixture() -> dict[str, object]:
    loaded = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_builds_fixture_first_monitoring_readiness_packet() -> None:
    packet = build_post_release_monitoring_readiness_packet(_load_fixture())

    assert packet["packet_type"] == "ppd.post_release_monitoring_readiness_packet.v1"
    assert packet["fixture_first"] is True
    assert [check["check_id"] for check in packet["monitoring_checks"]] == [
        "freshness:online-tools-guide",
        "freshness:submit-plans-online",
    ]
    assert packet["monitoring_checks"][0]["source_evidence_ids"] == ["ppd-online-tools-guide"]
    assert packet["monitoring_checks"][0]["escalation_threshold"] == {
        "max_age_days": 3,
        "change_count_greater_than": 0,
    }
    assert {contact["role"] for contact in packet["rollback_owner_contacts"]} >= {
        "release_owner",
        "rollback_owner",
        "rollback_reviewer",
    }
    assert packet["reviewer_owner_fields"]["release_owner"] == "ppd-release-owner"
    assert packet["reviewer_owner_fields"]["release_consumer_reviewer_1"] == "owner-release-review"
    assert packet["attestations"] == {
        "no-live-crawl": True,
        "no-DevHub": True,
        "no-prompt": True,
        "no-guardrail-mutation": True,
        "no-release-mutation": True,
    }
    assert packet["execution_boundaries"] == {
        "live_crawl": False,
        "devhub": False,
        "prompt": False,
        "guardrail_mutation": False,
        "release_mutation": False,
    }
    assert packet["offline_validation_commands"] == [
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ["python3", "-m", "unittest", "ppd.tests.test_post_release_monitoring_readiness_packet"],
    ]
    require_post_release_monitoring_readiness_packet(packet)


def test_rejects_source_packet_missing_offline_attestation() -> None:
    fixture = _load_fixture()
    checklist = deepcopy(fixture["offline_release_candidate_validation_checklist"])
    checklist["attestations"]["no_devhub"] = False
    fixture["offline_release_candidate_validation_checklist"] = checklist

    with pytest.raises(ValueError, match="no-DevHub"):
        build_post_release_monitoring_readiness_packet(fixture)


def test_validation_rejects_compiled_packet_without_threshold_or_boundary() -> None:
    packet = build_post_release_monitoring_readiness_packet(_load_fixture())
    packet["monitoring_checks"][0]["escalation_threshold"] = {}
    packet["execution_boundaries"]["release_mutation"] = True

    result = validate_post_release_monitoring_readiness_packet(packet)

    assert result.ready is False
    assert any("escalation_threshold" in problem for problem in result.problems)
    assert any("release_mutation" in problem for problem in result.problems)
