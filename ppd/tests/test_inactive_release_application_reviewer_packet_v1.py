from __future__ import annotations

from ppd.release.inactive_reviewer_packet_v1 import (
    validate_inactive_release_application_reviewer_packet_v1,
)


def _valid_packet() -> dict[str, object]:
    return {
        "packet_version": "inactive-release-application-reviewer-packet-v1",
        "release_activity": "inactive",
        "reviewer_comparison_rows": [
            {
                "reviewer": "fixture-reviewer",
                "baseline": "inactive packet fixture",
                "candidate": "current packet fixture",
                "finding": "no active release claim",
            }
        ],
        "prerequisite_gate_acknowledgements": [
            {"gate": "fixtures-only", "acknowledged": True},
        ],
        "fixture_family_risk_notes": [
            {"fixture_family": "release-application", "risk_note": "deterministic fixture only"},
        ],
        "rollback_checkpoint_confirmations": [
            {"checkpoint": "no state mutation", "confirmed": True},
        ],
        "unresolved_hold_carry_forward": [
            {
                "hold_id": "hold-001",
                "source": "supervisor",
                "carry_forward_reason": "requires later human review",
                "next_review_action": "compare deterministic reviewer rows",
            }
        ],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "notes": "Inactive reviewer packet based on deterministic committed fixtures.",
    }


def _codes(packet: dict[str, object]) -> set[str]:
    result = validate_inactive_release_application_reviewer_packet_v1(packet)
    return {error.code for error in result.errors}


def test_valid_inactive_reviewer_packet_passes() -> None:
    result = validate_inactive_release_application_reviewer_packet_v1(_valid_packet())
    assert result.ok
    assert result.errors == ()


def test_rejects_missing_required_reviewer_evidence() -> None:
    packet = _valid_packet()
    for field in (
        "reviewer_comparison_rows",
        "prerequisite_gate_acknowledgements",
        "fixture_family_risk_notes",
        "rollback_checkpoint_confirmations",
        "unresolved_hold_carry_forward",
        "validation_commands",
    ):
        packet[field] = []

    codes = _codes(packet)

    assert "reviewer_comparison_rows.missing" in codes
    assert "prerequisite_gate_acknowledgements.missing" in codes
    assert "fixture_family_risk_notes.missing" in codes
    assert "rollback_checkpoint_confirmations.missing" in codes
    assert "unresolved_hold_carry_forward.missing" in codes
    assert "validation_commands.missing" in codes


def test_rejects_unacknowledged_gates_and_unconfirmed_rollback_checkpoints() -> None:
    packet = _valid_packet()
    packet["prerequisite_gate_acknowledgements"] = [{"gate": "fixtures-only", "acknowledged": False}]
    packet["rollback_checkpoint_confirmations"] = [{"checkpoint": "no state mutation", "confirmed": False}]

    codes = _codes(packet)

    assert "prerequisite_gate_acknowledgements.item.unconfirmed" in codes
    assert "rollback_checkpoint_confirmations.item.unconfirmed" in codes


def test_rejects_missing_hold_carry_forward_fields() -> None:
    packet = _valid_packet()
    packet["unresolved_hold_carry_forward"] = [{"hold_id": "hold-001"}]

    codes = _codes(packet)

    assert "unresolved_hold_carry_forward.source.missing" in codes
    assert "unresolved_hold_carry_forward.carry_forward_reason.missing" in codes
    assert "unresolved_hold_carry_forward.next_review_action.missing" in codes


def test_rejects_private_browser_and_raw_data_artifacts() -> None:
    packet = _valid_packet()
    packet["browser_session"] = {"storage_state": "tmp/auth.json"}
    packet["artifacts"] = ["test-results/run/trace.zip", "fixtures/raw_crawl/output.json", "downloads/raw.pdf.har"]

    codes = _codes(packet)

    assert "private_artifact.key" in codes
    assert "private_artifact.value" in codes
    assert "raw_data_artifact.value" in codes


def test_rejects_live_release_claims_outcome_guarantees_and_consequential_actions() -> None:
    packet = _valid_packet()
    packet["claims"] = [
        "Release complete after live execution.",
        "Permit will be approved by the city.",
        "Submit the permit and pay the fee.",
    ]

    codes = _codes(packet)

    assert "live_release_claim.value" in codes
    assert "outcome_guarantee.value" in codes
    assert "consequential_action.value" in codes


def test_rejects_active_mutation_flags() -> None:
    packet = _valid_packet()
    packet["mutate_release_state"] = True
    packet["notes"] = "Mutate active prompt during packet review."

    codes = _codes(packet)

    assert "active_mutation.value" in codes
    assert "active_mutation.flag" in codes
