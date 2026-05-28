from __future__ import annotations

from pathlib import Path

from ppd.devhub.manual_handoff_decision_packet import (
    REQUIRED_TRIGGER_IDS,
    SAFE_ALTERNATIVE_TYPES,
    blocked_action_ids_by_trigger,
    load_manual_handoff_decision_packet,
    user_visible_handoff_text_by_trigger,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "devhub_manual_handoff_decision_packet"
    / "unsupported_manual_handoff_decision_packet.json"
)


FORBIDDEN_SAFE_ACTION_FRAGMENTS = (
    "submit",
    "payment",
    "captcha",
    "mfa",
    "password",
    "create_account",
    "upload",
    "schedule",
    "cancel",
    "certify",
)


def test_packet_covers_all_required_manual_handoff_triggers() -> None:
    packet = load_manual_handoff_decision_packet(FIXTURE_PATH)

    assert packet.fixture_only is True
    assert {trigger.trigger_id for trigger in packet.triggers} == REQUIRED_TRIGGER_IDS


def test_packet_preserves_cited_reasons_handoff_text_and_blocked_action_ids() -> None:
    packet = load_manual_handoff_decision_packet(FIXTURE_PATH)
    blocked_actions = blocked_action_ids_by_trigger(packet)
    handoff_text = user_visible_handoff_text_by_trigger(packet)

    assert blocked_actions["mfa"] == (
        "devhub:mfa_prompt_response",
        "devhub:security_challenge_response",
    )
    assert blocked_actions["captcha"] == (
        "devhub:captcha_solution",
        "devhub:bot_defense_bypass",
    )
    assert "devhub:submit_payment" in blocked_actions["final_payment_execution"]
    assert "devhub:unknown_consequence_control" in blocked_actions["unclear_consequence_control"]
    assert "devhub:create_application_for_non_devhub_path" in blocked_actions["non_devhub_permit_path"]

    for trigger in packet.triggers:
        assert trigger.cited_reason
        assert trigger.source_evidence_ids
        assert handoff_text[trigger.trigger_id]
        assert "cannot" in handoff_text[trigger.trigger_id].casefold() or "not supported" in handoff_text[
            trigger.trigger_id
        ].casefold()


def test_next_safe_alternatives_are_read_only_or_local_preview_only() -> None:
    packet = load_manual_handoff_decision_packet(FIXTURE_PATH)

    assert packet.next_safe_alternatives
    assert {alternative.action_type for alternative in packet.next_safe_alternatives}.issubset(SAFE_ALTERNATIVE_TYPES)
    assert {alternative.action_type for alternative in packet.next_safe_alternatives} == {
        "read_only_review",
        "local_preview",
    }
    for alternative in packet.next_safe_alternatives:
        assert alternative.preserves_official_state is True
        action_id = alternative.action_id.casefold()
        assert not any(fragment in action_id for fragment in FORBIDDEN_SAFE_ACTION_FRAGMENTS)


def test_packet_round_trip_preserves_agent_facing_fields() -> None:
    packet = load_manual_handoff_decision_packet(FIXTURE_PATH)
    round_trip = packet.to_dict()

    assert round_trip["packet_id"] == "fixture_ppd_unsupported_manual_handoff_decision_packet_2026_05_28"
    assert round_trip["fixture_only"] is True
    assert len(round_trip["triggers"]) == len(REQUIRED_TRIGGER_IDS)
    assert round_trip["triggers"][0]["user_visible_handoff_text"].startswith("I cannot complete MFA")
    assert round_trip["next_safe_alternatives"][0] == {
        "action_id": "safe:show_cited_guidance",
        "action_type": "read_only_review",
        "label": "Show the cited PP&D or DevHub guidance that explains why the workflow requires manual handoff.",
        "preserves_official_state": True,
    }
