from __future__ import annotations

import importlib.util
import json
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "live_dry_run_operator_briefing_packet_v2.json"
MODULE_PATH = Path(__file__).parents[1] / "live_dry_run_operator_briefing_packet_v2.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("live_dry_run_operator_briefing_packet_v2", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixture_packet_contains_required_operator_briefing_sections() -> None:
    packet = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert packet["packet_version"] == 2
    assert packet["go_no_go_briefing_notes"]
    assert packet["required_human_attendance_checkpoints"]
    assert packet["independent_stop_conditions"]
    assert packet["artifact_redaction_expectations"]
    assert packet["allowed_offline_validation_commands"]

    source_packets = packet["source_packets"]
    assert "public_recrawl_live_dry_run_plan_v2" in source_packets
    assert "attended_devhub_read_only_live_dry_run_plan_v2" in source_packets
    assert "live_readiness_authorization_checklist_packet_v2" in source_packets


def test_fixture_packet_attests_no_live_or_stateful_actions() -> None:
    packet = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    attestations = packet["attestations"]

    assert attestations == {
        "no_live_execution": True,
        "no_auth_state": True,
        "no_browser_artifact": True,
        "no_official_action": True,
        "no_release_state_mutation": True,
    }


def test_fixture_packet_validator_accepts_fixture() -> None:
    module = _load_module()
    packet = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    module.validate_operator_briefing_packet_v2(packet)


def test_builder_consumes_source_packets_into_cited_briefing() -> None:
    module = _load_module()
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    built = module.build_operator_briefing_packet_v2(fixture["source_packets"])

    assert built["source_packets"] == fixture["source_packets"]
    cited_text = json.dumps(built["go_no_go_briefing_notes"], sort_keys=True)
    assert "public_recrawl_live_dry_run_plan_v2.scope" in cited_text
    assert "attended_devhub_read_only_live_dry_run_plan_v2.read_only_boundary" in cited_text
    assert "live_readiness_authorization_checklist_packet_v2.authorization_gate" in cited_text
