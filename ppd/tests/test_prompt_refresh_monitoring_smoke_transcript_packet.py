import json
from pathlib import Path


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "prompt_refresh_monitoring_smoke_transcript_packet.json"
)


REQUIRED_INPUT_PACKETS = {
    "prompt-refresh-monitoring-readiness-packet",
    "prompt-consumer-dry-run-transcript-packet",
    "source-freshness-watchlist-packet",
}

REQUIRED_ATTESTATIONS = {
    "no_live_monitoring",
    "no_crawler",
    "no_devhub",
    "no_llm",
    "no_prompt_mutation",
    "no_guardrail_mutation",
    "no_release_state_mutation",
    "no_private_devhub_session_files",
    "no_auth_state",
    "no_traces",
    "no_raw_crawl_output",
    "no_downloaded_documents",
}


def load_packet():
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def test_smoke_transcript_consumes_required_packets():
    packet = load_packet()

    consumed_packet_ids = {entry["packet_id"] for entry in packet["consumes"]}
    transcript_packet_ids = {event["input_packet"] for event in packet["fixture_transcript"]}

    assert packet["mode"] == "offline_fixture_only"
    assert REQUIRED_INPUT_PACKETS <= consumed_packet_ids
    assert REQUIRED_INPUT_PACKETS <= transcript_packet_ids
    assert all(entry["required"] is True for entry in packet["consumes"])


def test_expected_observations_are_cited_and_referenced_by_transcript():
    packet = load_packet()

    citation_ids = {citation["citation_id"] for citation in packet["citation_catalog"]}
    observation_ids = {
        observation["observation_id"]
        for observation in packet["expected_offline_monitor_observations"]
    }
    referenced_observation_ids = {
        observation_id
        for event in packet["fixture_transcript"]
        for observation_id in event["expected_monitor_observation_ids"]
    }

    assert referenced_observation_ids <= observation_ids
    assert referenced_observation_ids == observation_ids

    for observation in packet["expected_offline_monitor_observations"]:
        assert observation["expected"]
        assert observation["citation_ids"]
        assert set(observation["citation_ids"]) <= citation_ids


def test_escalation_and_non_escalation_decisions_are_explicit():
    packet = load_packet()

    observation_ids = {
        observation["observation_id"]
        for observation in packet["expected_offline_monitor_observations"]
    }
    citation_ids = {citation["citation_id"] for citation in packet["citation_catalog"]}
    decisions = packet["escalation_decisions"]

    assert any(decision["escalate"] is True for decision in decisions)
    assert any(decision["escalate"] is False for decision in decisions)

    for decision in decisions:
        assert set(decision["observation_ids"]) <= observation_ids
        assert set(decision["citation_ids"]) <= citation_ids
        assert decision["reason"]


def test_rollback_checks_cover_block_and_pass_paths():
    packet = load_packet()

    citation_ids = {citation["citation_id"] for citation in packet["citation_catalog"]}
    checks = packet["rollback_trigger_checks"]

    assert any(check["triggered"] is True for check in checks)
    assert any(check["triggered"] is False for check in checks)

    for check in checks:
        assert check["reason"]
        assert check["required_action"]
        assert set(check["citation_ids"]) <= citation_ids


def test_validation_commands_and_attestations_are_side_effect_bounded():
    packet = load_packet()

    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet[
        "allowed_validation_commands"
    ]
    assert [
        "python3",
        "-m",
        "pytest",
        "ppd/tests/test_prompt_refresh_monitoring_smoke_transcript_packet.py",
    ] in packet["allowed_validation_commands"]

    attestations = packet["attestations"]
    assert REQUIRED_ATTESTATIONS <= set(attestations)
    assert all(attestations[name] is True for name in REQUIRED_ATTESTATIONS)
