from pathlib import Path

from ppd.public_source_refresh_launch_rehearsal_transcript_packet import (
    build_public_source_refresh_launch_rehearsal_transcript_packet,
    load_fixture_packet,
    validate_public_source_refresh_launch_rehearsal_transcript_packet,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_refresh_launch_rehearsal_transcript"


def test_builds_fixture_first_launch_rehearsal_transcript() -> None:
    packet = build_public_source_refresh_launch_rehearsal_transcript_packet(load_fixture_packet(FIXTURE_DIR / "inputs.json"))

    assert packet["packet_type"] == "ppd.public_source_refresh_launch_rehearsal_transcript_packet.v1"
    assert packet["fixture_first"] is True
    assert {item["kind"] for item in packet["consumed_packets"]} == {
        "public_source_refresh_launch_packet",
        "public_source_refresh_execution_readiness_packet",
        "post_release_monitoring_readiness_packet",
    }
    assert [step["step_id"] for step in packet["operator_rehearsal_steps"]] == [
        "load-cited-launch-packet",
        "compare-execution-readiness-gates",
        "arm-abort-trigger-checks",
        "stage-metadata-only-placeholders",
        "confirm-monitoring-handoff",
    ]


def test_launch_rehearsal_transcript_records_gate_outcomes_and_abort_checks() -> None:
    packet = build_public_source_refresh_launch_rehearsal_transcript_packet(load_fixture_packet(FIXTURE_DIR / "inputs.json"))

    assert packet["observed_preflight_gate_outcomes"]
    assert all(gate["outcome"] == "pass" for gate in packet["observed_preflight_gate_outcomes"])
    assert {check["status"] for check in packet["abort_trigger_checks"]} == {"armed"}
    assert any(check["trigger_id"] == "live-fetch-requested" for check in packet["abort_trigger_checks"])


def test_launch_rehearsal_transcript_stays_metadata_only() -> None:
    packet = build_public_source_refresh_launch_rehearsal_transcript_packet(load_fixture_packet(FIXTURE_DIR / "inputs.json"))
    result = validate_public_source_refresh_launch_rehearsal_transcript_packet(packet)

    assert result.ready is True
    assert packet["attestations"] == {
        "no-live-fetch": True,
        "no-download": True,
        "no-processor": True,
        "no-registry-mutation": True,
        "no-schedule-mutation": True,
    }
    assert packet["execution_boundaries"] == {
        "live_fetch_allowed": False,
        "download_allowed": False,
        "processor_invocation_allowed": False,
        "registry_mutation_allowed": False,
        "schedule_mutation_allowed": False,
    }
    for placeholder in packet["expected_metadata_only_result_placeholders"]:
        assert placeholder["live_fetch_performed"] is False
        assert placeholder["document_downloaded"] is False
        assert placeholder["processor_invoked"] is False
        assert placeholder["registry_mutated"] is False
        assert placeholder["schedule_mutated"] is False
