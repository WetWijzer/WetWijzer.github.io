from __future__ import annotations

from pathlib import Path

from ppd.guarded_agent_readiness_delta_packet_v2 import (
    DELTA_PACKET_VERSION,
    REQUIRED_SCENARIO_KINDS,
    build_delta_packet_from_files,
)


def test_fixture_first_delta_packet_v2_orders_and_covers_required_scenarios() -> None:
    fixture_dir = Path(__file__).parent / "fixtures" / "guarded_agent_readiness_delta_v2"
    packet = build_delta_packet_from_files(
        fixture_dir / "inactive_fixture_promotion_candidate_packet_v2.json",
        [fixture_dir / "guarded_agent_readiness_packet_v2.json"],
    )

    scenarios = packet["ordered_agent_facing_delta_scenarios"]
    assert packet["packet_version"] == DELTA_PACKET_VERSION
    assert packet["mode"] == "fixture_first_offline_only"
    assert [scenario["order"] for scenario in scenarios] == list(range(1, len(scenarios) + 1))
    assert [scenario["kind"] for scenario in scenarios] == list(REQUIRED_SCENARIO_KINDS)
    assert packet["coverage"]["missing_required_scenario_kinds"] == []


def test_delta_packet_v2_preserves_guarded_offline_boundaries() -> None:
    fixture_dir = Path(__file__).parent / "fixtures" / "guarded_agent_readiness_delta_v2"
    packet = build_delta_packet_from_files(
        fixture_dir / "inactive_fixture_promotion_candidate_packet_v2.json",
        [fixture_dir / "guarded_agent_readiness_packet_v2.json"],
    )

    guards = packet["guards"]
    assert guards["active_artifact_mutation"] == "forbidden"
    assert guards["devhub_access"] == "forbidden"
    assert guards["live_source_crawl"] == "forbidden"
    assert guards["official_actions"] == "forbidden"
    assert guards["prompt_changes"] == "forbidden"

    by_kind = {scenario["kind"]: scenario for scenario in packet["ordered_agent_facing_delta_scenarios"]}
    assert by_kind["refusal_behavior"]["refusal_required"] is True
    assert "official_submission" in by_kind["refusal_behavior"]["blocked_actions"]
    assert by_kind["reversible_draft_boundary"]["reversible_draft_only"] is True
    assert by_kind["journal_event_safety"]["journal_event_safe"] is True
    assert by_kind["rollback_readiness"]["rollback_ready"] is True
    assert by_kind["offline_validation_command"]["offline_validation_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
