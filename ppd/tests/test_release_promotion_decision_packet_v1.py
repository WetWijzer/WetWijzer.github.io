from __future__ import annotations

from pathlib import Path

from ppd.agent_readiness.release_promotion_decision_packet_v1 import (
    validate_release_promotion_decision_packet_v1,
)


def valid_packet() -> dict[str, object]:
    fixture_dir = Path(__file__).parent / "fixtures" / "release_promotion_decision_packet_v1"
    return {
        "packet_version": "release_promotion_decision_packet_v1",
        "packet_id": "release-promotion-decision-packet-v1-fixture",
        "release_scope": {
            "in_scope": ["offline release gate validation for normalized PP&D guardrail packets"],
            "out_of_scope": ["live crawl", "authenticated DevHub automation", "official permit action"],
            "boundary_statement": "Promotion only covers offline cited validation artifacts and does not mutate release state.",
        },
        "decision_rows": [
            {
                "decision": "promote offline validator fixture",
                "rationale": "The fixture is source-grounded and remains offline.",
                "citations": ["src-official-ppd-plan-boundaries"],
            }
        ],
        "manual_signoff_placeholders": [
            {"role": "release supervisor", "placeholder": "pending manual signoff after reviewing cited evidence"}
        ],
        "validation_replay_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "rollback_checkpoints": [
            {
                "checkpoint_id": "pre-promotion-offline-validator",
                "restore_command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "verification_command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "notes": f"fixture roots are derived from {fixture_dir.name}",
            }
        ],
        "active_source_mutation": False,
        "active_document_mutation": False,
        "active_requirement_mutation": False,
        "active_process_mutation": False,
        "active_guardrail_mutation": False,
        "active_prompt_mutation": False,
        "active_release_state_mutation": False,
        "active_fixture_mutation": False,
        "active_agent_state_mutation": False,
    }


def issue_codes(packet: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_release_promotion_decision_packet_v1(packet).issues}


def test_accepts_valid_offline_release_promotion_packet() -> None:
    result = validate_release_promotion_decision_packet_v1(valid_packet())

    assert result.valid is True
    assert result.issues == ()


def test_rejects_uncited_decision_rows() -> None:
    packet = valid_packet()
    packet["decision_rows"] = [{"decision": "promote", "rationale": "no cited basis"}]

    assert "uncited_decision_row" in issue_codes(packet)


def test_rejects_missing_release_scope_boundaries() -> None:
    packet = valid_packet()
    packet["release_scope"] = {"in_scope": [], "out_of_scope": [], "boundary_statement": ""}

    codes = issue_codes(packet)

    assert "missing_release_scope_in_scope" in codes
    assert "missing_release_scope_out_of_scope" in codes
    assert "missing_release_scope_boundary_statement" in codes


def test_rejects_missing_manual_signoff_validation_replay_and_rollback() -> None:
    packet = valid_packet()
    packet["manual_signoff_placeholders"] = []
    packet["validation_replay_commands"] = []
    packet["rollback_checkpoints"] = []

    codes = issue_codes(packet)

    assert "missing_manual_signoff_placeholders" in codes
    assert "missing_validation_replay_commands" in codes
    assert "missing_rollback_checkpoints" in codes


def test_rejects_private_browser_and_raw_download_artifacts() -> None:
    packet = valid_packet()
    packet["artifact_refs"] = [
        "state/auth_state.json",
        "browser/session-storage.json",
        "captures/raw_body.html",
        "downloads/application.pdf",
    ]

    codes = issue_codes(packet)

    assert "private_or_authenticated_artifact" in codes
    assert "raw_or_downloaded_artifact" in codes


def test_rejects_guarantees_and_consequential_action_language() -> None:
    packet = valid_packet()
    packet["operator_notes"] = (
        "This packet does not guarantee approval, cannot say a permit will be approved, "
        "and must not instruct an agent to submit the permit or pay fees."
    )

    codes = issue_codes(packet)

    assert "legal_or_permitting_outcome_guarantee" in codes
    assert "consequential_action_language" in codes


def test_rejects_active_mutation_flags() -> None:
    packet = valid_packet()
    packet["active_source_mutation"] = True
    packet["active_document_mutation"] = True
    packet["active_requirement_mutation"] = True
    packet["active_process_mutation"] = True
    packet["active_guardrail_mutation"] = True
    packet["active_prompt_mutation"] = True
    packet["active_release_state_mutation"] = True
    packet["active_fixture_mutation"] = True
    packet["active_agent_state_mutation"] = True

    assert issue_codes(packet) == {"active_mutation_flag"}
