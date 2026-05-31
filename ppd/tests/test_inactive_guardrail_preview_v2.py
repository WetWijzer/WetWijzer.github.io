from __future__ import annotations

from pathlib import Path

from ppd.logic.inactive_guardrail_preview_v2 import (
    OFFLINE_VALIDATION_COMMANDS,
    PREVIEW_STATUS,
    build_preview_packet,
    load_fixture,
)

FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "inactive_guardrail_preview_v2"
    / "synthetic_inactive_process_model_deltas.json"
)


def test_inactive_guardrail_preview_packet_v2_maps_all_required_categories() -> None:
    fixture = load_fixture(FIXTURE_PATH)
    packet = build_preview_packet(fixture)

    assert packet["migration_preview_packet_version"] == 2
    assert packet["preview_status"] == PREVIEW_STATUS
    assert packet["source_mode"] == "committed_fixture_only"
    assert packet["promotion_allowed"] is False
    assert packet["active_prompt_changes_allowed"] is False
    assert packet["live_crawl_allowed"] is False
    assert packet["devhub_access_allowed"] is False
    assert packet["release_state_mutation_allowed"] is False

    expected_keys = {
        "proposed_deterministic_predicates",
        "proposed_deontic_rules",
        "proposed_temporal_rules",
        "proposed_reversible_action_predicates",
        "proposed_exact_confirmation_predicates",
        "proposed_refused_action_predicates",
        "proposed_stale_source_holds",
        "explanation_template_placeholders",
        "reviewer_disposition_placeholders",
        "exact_offline_validation_commands",
    }
    assert expected_keys.issubset(packet)

    delta_count = len(fixture["synthetic_inactive_process_model_deltas"])
    assert len(packet["proposed_deterministic_predicates"]) == delta_count
    assert len(packet["proposed_deontic_rules"]) == delta_count
    assert len(packet["explanation_template_placeholders"]) == delta_count
    assert len(packet["reviewer_disposition_placeholders"]) == delta_count

    assert packet["proposed_temporal_rules"]
    assert packet["proposed_reversible_action_predicates"]
    assert packet["proposed_exact_confirmation_predicates"]
    assert packet["proposed_refused_action_predicates"]
    assert packet["proposed_stale_source_holds"]


def test_consequential_actions_are_refused_without_attended_exact_confirmation() -> None:
    packet = build_preview_packet(load_fixture(FIXTURE_PATH))
    refused = packet["proposed_refused_action_predicates"]

    refused_actions = {predicate["action"] for predicate in refused}
    assert {
        "submit_permit_request",
        "submit_payment",
        "schedule_inspection",
    }.issubset(refused_actions)

    for predicate in refused:
        assert predicate["status"] == "proposed_inactive"
        assert predicate["refuse_when_unattended"] is True
        assert predicate["refuse_when_confirmation_missing"] is True


def test_stale_sources_create_preview_holds() -> None:
    packet = build_preview_packet(load_fixture(FIXTURE_PATH))
    holds = packet["proposed_stale_source_holds"]

    assert len(holds) == 1
    hold = holds[0]
    assert hold["delta_id"] == "delta.stale.file_naming_standard"
    assert hold["status"] == "proposed_inactive"
    assert hold["release_condition_placeholder"] == "{{reviewer_confirms_source_freshness}}"


def test_exact_offline_validation_commands_are_deterministic_arrays() -> None:
    packet = build_preview_packet(load_fixture(FIXTURE_PATH))

    assert packet["exact_offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS
    for command in packet["exact_offline_validation_commands"]:
        assert isinstance(command, list)
        assert command
        assert all(isinstance(part, str) and part for part in command)
