from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.agent_readiness.prompt_refresh_monitoring_readiness_packet import (
    PromptRefreshMonitoringReadinessPacketError,
    assert_valid_prompt_refresh_monitoring_readiness_packet,
    build_prompt_refresh_monitoring_readiness_packet,
    validate_prompt_refresh_monitoring_readiness_packet,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "prompt_refresh_monitoring_readiness_packet" / "input_packets.json"


def _load_inputs() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _build_packet() -> dict:
    return build_prompt_refresh_monitoring_readiness_packet(_load_inputs())


def test_builds_fixture_first_prompt_refresh_monitoring_readiness_packet() -> None:
    packet = _build_packet()

    assert packet["packet_type"] == "ppd.prompt_refresh_monitoring_readiness_packet.v1"
    assert packet["fixture_first"] is True
    assert packet["offline_only"] is True
    assert validate_prompt_refresh_monitoring_readiness_packet(packet).valid is True
    assert_valid_prompt_refresh_monitoring_readiness_packet(packet)


def test_consumes_required_packets_into_cited_monitoring_checks_and_drift_signals() -> None:
    packet = _build_packet()

    assert set(packet["consumed_packets"]) == {
        "prompt_consumer_dry_run_transcript_packet",
        "post_release_monitoring_plan_packet",
        "source_freshness_watchlist_packet",
    }
    assert {row["check_id"] for row in packet["offline_monitoring_checks"]} == {
        "freshness:online-tools-guide",
        "freshness:submit-plans-online",
    }
    for check in packet["offline_monitoring_checks"]:
        assert check["source_evidence_ids"]
        assert check["reviewer_owner"] == "ppd-release-operator"
        assert check["escalation_note"]
        assert check["escalation_threshold"]
        assert check["monitoring_mode"] == "offline_fixture_comparison_only"

    assert {signal["source_id"] for signal in packet["drift_signals"]} == {
        "ppd-online-tools-guide",
        "ppd-submit-plans-online",
    }
    for signal in packet["drift_signals"]:
        assert signal["source_evidence_ids"]
        assert signal["affected_requirement_ids"]
        assert signal["affected_guardrail_ids"]
        assert "refuses-official-action-with-cited-boundary" in signal["prompt_consumer_scenario_ids"]


def test_exposes_escalation_owners_rollback_triggers_commands_and_attestations() -> None:
    packet = _build_packet()

    assert packet["escalation_owner_fields"] == {
        "prompt_refresh_owner": "ppd-agent-prompt-reviewer",
        "monitoring_owner": "ppd-release-operator",
        "source_freshness_owner": "ppd-evidence-freshness-watchlist-owner",
        "guardrail_owner": "ppd-traceability-reviewer",
        "rollback_owner": "ppd-evidence-freshness-reviewer",
    }
    assert packet["rollback_triggers"]
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["allowed_validation_commands"]
    for key in (
        "no-live-monitoring",
        "no-crawler",
        "no-DevHub",
        "no-prompt",
        "no-guardrail-mutation",
        "no-release-state-mutation",
    ):
        assert packet["attestations"][key] is True
    assert all(value is False for value in packet["execution_boundaries"].values())


def test_validator_rejects_uncited_live_or_mutating_packet() -> None:
    packet = _build_packet()
    broken = copy.deepcopy(packet)
    broken["offline_monitoring_checks"][0]["source_evidence_ids"] = []
    broken["drift_signals"][0]["affected_guardrail_ids"] = []
    broken["rollback_triggers"][0]["source_evidence_ids"] = []
    broken["allowed_validation_commands"] = [["python3", "-m", "crawl"]]
    broken["attestations"]["no-live-monitoring"] = False
    broken["execution_boundaries"]["live_monitoring"] = True

    result = validate_prompt_refresh_monitoring_readiness_packet(broken)

    assert result.valid is False
    codes = set(result.codes())
    assert "uncited_offline_monitoring_check" in codes
    assert "missing_drift_guardrail_links" in codes
    assert "uncited_rollback_trigger" in codes
    assert "live_validation_command" in codes
    assert "missing_required_attestation" in codes
    assert "enabled_execution_boundary" in codes


def test_assert_valid_raises_with_findings() -> None:
    packet = _build_packet()
    packet["escalation_owner_fields"]["rollback_owner"] = "tbd"

    with pytest.raises(PromptRefreshMonitoringReadinessPacketError) as exc_info:
        assert_valid_prompt_refresh_monitoring_readiness_packet(packet)

    assert exc_info.value.findings
