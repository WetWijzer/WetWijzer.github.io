from __future__ import annotations

from copy import deepcopy

from ppd.release_decision_packet_v2 import validate_post_recompile_release_decision_packet_v2


def _valid_packet() -> dict[str, object]:
    return {
        "packet_version": "post-recompile-release-decision-v2",
        "release_decision_rows": [
            {
                "decision": "hold",
                "status": "not_released",
                "reason": "deterministic validation requires reviewer completion outside the packet",
            }
        ],
        "stale_source_hold_outcomes": [
            {
                "source_id": "ppd-public-guidance-index",
                "hold_outcome": "held_until_source_freshness_review",
            }
        ],
        "reviewer_signoff_placeholders": [
            {
                "reviewer_role": "ppd_release_reviewer",
                "signed": False,
                "placeholder": "pending human review",
            }
        ],
        "rollback_references": ["ppd rollback plan fixture reference"],
        "inactive_to_active_eligibility_notes": ["activation requires a separate reviewed release action"],
        "blocked_consequential_action_reminders": [
            "Do not submit, upload, certify, schedule, cancel, or pay without attended confirmation."
        ],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "active_mutation_flags": [],
    }


def _codes(packet: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_post_recompile_release_decision_packet_v2(packet)}


def test_accepts_complete_conservative_packet() -> None:
    assert validate_post_recompile_release_decision_packet_v2(_valid_packet()) == []


def test_rejects_missing_required_release_controls() -> None:
    for field in (
        "release_decision_rows",
        "stale_source_hold_outcomes",
        "reviewer_signoff_placeholders",
        "rollback_references",
        "inactive_to_active_eligibility_notes",
        "blocked_consequential_action_reminders",
        "validation_commands",
    ):
        packet = _valid_packet()
        packet.pop(field)
        assert f"packet.{field}.missing" in _codes(packet)


def test_rejects_malformed_rows_outcomes_signoffs_and_commands() -> None:
    packet = _valid_packet()
    packet["release_decision_rows"] = [{"decision": "hold"}]
    packet["stale_source_hold_outcomes"] = [{"source_id": "source-a"}]
    packet["reviewer_signoff_placeholders"] = [{"signed": True}]
    packet["validation_commands"] = ["python3 ppd/daemon/ppd_daemon.py --self-test"]

    codes = _codes(packet)

    assert "packet.release_decision_rows.reason" in codes
    assert "packet.release_decision_rows.status" in codes
    assert "packet.stale_source_hold_outcomes.hold_outcome" in codes
    assert "packet.reviewer_signoff_placeholders.role" in codes
    assert "packet.reviewer_signoff_placeholders.signed" in codes
    assert "packet.validation_commands.item" in codes


def test_rejects_private_session_browser_raw_and_downloaded_artifacts() -> None:
    forbidden_terms = (
        "session file",
        "browser_context",
        "raw crawl",
        "downloaded",
        "trace.zip",
        "storage_state",
    )

    for term in forbidden_terms:
        packet = _valid_packet()
        packet["rollback_references"] = [f"contains {term}"]
        assert "packet.forbidden_artifact" in _codes(packet)


def test_rejects_live_crawl_devhub_official_action_and_guarantee_claims() -> None:
    forbidden_claims = (
        "live crawl completed",
        "DevHub was accessed",
        "official action completed",
        "submitted to DevHub",
        "legal guarantee",
        "permit guaranteed",
    )

    for claim in forbidden_claims:
        packet = _valid_packet()
        packet["release_decision_rows"] = [
            {"decision": "release", "status": "ready", "reason": claim}
        ]
        assert "packet.forbidden_claim" in _codes(packet)


def test_rejects_active_mutation_flags() -> None:
    for field in (
        "active_prompt_mutation",
        "active_guardrail_mutation",
        "active_source_mutation",
        "active_requirement_mutation",
        "active_process_model_mutation",
        "active_contract_mutation",
        "active_devhub_surface_mutation",
        "active_release_state_mutation",
    ):
        packet = _valid_packet()
        packet[field] = True
        assert "packet.mutation_flag" in _codes(packet)

    packet = deepcopy(_valid_packet())
    packet["active_mutation_flags"] = ["source"]
    assert "packet.active_mutation_flags" in _codes(packet)
