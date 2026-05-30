from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.monitoring.readiness import (
    ReadinessValidationError,
    assert_post_release_monitoring_readiness_packet,
    validate_post_release_monitoring_readiness_packet,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "post_release_monitoring_readiness_valid.json"
)


def _valid_packet() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _codes(packet: dict) -> set[str]:
    result = validate_post_release_monitoring_readiness_packet(packet)
    return {finding.code for finding in result.findings}


def test_valid_fixture_is_ready() -> None:
    packet = _valid_packet()

    result = validate_post_release_monitoring_readiness_packet(packet)

    assert result.ok
    assert result.findings == ()
    assert_post_release_monitoring_readiness_packet(packet)


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (
            lambda packet: packet["monitoring_checks"][0].pop("source_evidence_ids"),
            "uncited_monitoring_check",
        ),
        (
            lambda packet: packet["monitoring_checks"][0].pop("escalation_threshold"),
            "missing_escalation_threshold",
        ),
        (
            lambda packet: packet.pop("escalation_thresholds"),
            "missing_escalation_thresholds",
        ),
        (
            lambda packet: packet["rollback"].pop("owner"),
            "missing_rollback_owner",
        ),
        (
            lambda packet: packet.pop("offline_validation_commands"),
            "missing_offline_validation_commands",
        ),
        (
            lambda packet: packet.update(
                {"raw_body_ref": "raw public response body was stored"}
            ),
            "raw_body_download_or_archive_reference",
        ),
        (
            lambda packet: packet.update(
                {"download_url": "https://www.portland.gov/example/download"}
            ),
            "raw_body_download_or_archive_reference",
        ),
        (
            lambda packet: packet.update({"archive_artifact_ref": "warc://example"}),
            "raw_body_download_or_archive_reference",
        ),
        (
            lambda packet: packet.update({"storage_state": "playwright/.auth/user.json"}),
            "private_or_session_artifact",
        ),
        (
            lambda packet: packet.update({"devhub_session": "session.json"}),
            "private_or_session_artifact",
        ),
        (
            lambda packet: packet.update({"live_crawler_executed": True}),
            "live_execution_claim",
        ),
        (
            lambda packet: packet.update({"processor_executed": "true"}),
            "live_execution_claim",
        ),
        (
            lambda packet: packet.update({"notes": "DevHub automation executed."}),
            "live_execution_claim",
        ),
        (
            lambda packet: packet.update({"notes": "Permit approval guaranteed."}),
            "legal_or_permitting_outcome_guarantee",
        ),
        (
            lambda packet: packet.update({"active_source_registry_mutation": True}),
            "active_mutation_flag",
        ),
        (
            lambda packet: packet.update({"requirement_update_enabled": True}),
            "active_mutation_flag",
        ),
        (
            lambda packet: packet.update({"process_write_enabled": True}),
            "active_mutation_flag",
        ),
        (
            lambda packet: packet.update({"guardrail_publish_active": True}),
            "active_mutation_flag",
        ),
        (
            lambda packet: packet.update({"prompt_mutation_enabled": True}),
            "active_mutation_flag",
        ),
        (
            lambda packet: packet.update({"surface_registry_commit": True}),
            "active_mutation_flag",
        ),
        (
            lambda packet: packet.update({"release_state_update_active": True}),
            "active_mutation_flag",
        ),
    ],
)
def test_rejects_post_release_monitoring_readiness_violations(
    mutator: object,
    expected_code: str,
) -> None:
    packet = copy.deepcopy(_valid_packet())

    mutator(packet)

    assert expected_code in _codes(packet)


def test_rejects_live_or_network_offline_validation_commands() -> None:
    packet = _valid_packet()
    packet["offline_validation_commands"].append(
        ["python3", "ppd/crawler/live_monitor.py"]
    )

    assert "non_offline_validation_command" in _codes(packet)


def test_assertion_raises_with_findings() -> None:
    packet = _valid_packet()
    packet["monitoring_checks"][0].pop("source_evidence_ids")

    with pytest.raises(ReadinessValidationError) as exc_info:
        assert_post_release_monitoring_readiness_packet(packet)

    assert exc_info.value.findings
    assert "uncited_monitoring_check" in str(exc_info.value)
