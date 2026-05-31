from __future__ import annotations

from pathlib import Path
import sys

_FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "fee_deadline_trigger_matrix_packet_v2"
sys.path.insert(0, str(_FIXTURE_ROOT))

from valid_packet import valid_packet

from ppd.fee_deadline_trigger_matrix_packet_v2 import (
    is_valid_fee_deadline_trigger_matrix_packet_v2,
    validate_fee_deadline_trigger_matrix_packet_v2,
)


def _codes(packet: dict) -> set[str]:
    return {finding.code for finding in validate_fee_deadline_trigger_matrix_packet_v2(packet)}


def test_valid_fixture_is_accepted() -> None:
    assert is_valid_fee_deadline_trigger_matrix_packet_v2(valid_packet())


def test_rejects_missing_required_safety_sections() -> None:
    packet = valid_packet()
    for field in (
        "fee_trigger_rows",
        "deadline_or_expiration_cues",
        "payment_boundary_warnings",
        "source_evidence_placeholders",
        "stale_source_hold_notes",
        "blocked_financial_action_reminders",
        "reviewer_dispositions",
        "validation_commands",
    ):
        packet[field] = []

    assert _codes(packet) >= {
        "missing_fee_trigger_rows",
        "missing_deadline_or_expiration_cues",
        "missing_payment_boundary_warnings",
        "missing_source_evidence_placeholders",
        "missing_stale_source_hold_notes",
        "missing_blocked_financial_action_reminders",
        "missing_reviewer_dispositions",
        "missing_validation_commands",
    }


def test_rejects_fee_rows_without_source_evidence_or_reviewer_disposition() -> None:
    packet = valid_packet()
    packet["fee_trigger_rows"] = [{"row_id": "incomplete"}]

    assert _codes(packet) >= {
        "missing_fee_row_source_evidence_placeholder",
        "missing_fee_row_reviewer_disposition",
    }


def test_rejects_payment_details_private_artifacts_live_claims_and_guarantees() -> None:
    packet = valid_packet()
    packet["notes"] = [
        "card_number fixture value is prohibited",
        "auth_state fixture path is prohibited",
        "live crawl completed claim is prohibited",
        "permit guaranteed claim is prohibited",
    ]

    assert _codes(packet) >= {
        "payment_detail_present",
        "private_or_raw_artifact_present",
        "live_crawl_or_devhub_claim_present",
        "legal_or_permitting_guarantee_present",
    }


def test_rejects_active_mutation_flags() -> None:
    packet = valid_packet()
    packet["mutation_flags"]["active_requirement_mutation"] = True
    packet["mutation_flags"]["active_process_model_mutation"] = True
    packet["mutation_flags"]["active_guardrail_mutation"] = True
    packet["mutation_flags"]["active_prompt_mutation"] = True
    packet["mutation_flags"]["active_contract_mutation"] = True
    packet["mutation_flags"]["active_source_mutation"] = True
    packet["mutation_flags"]["active_devhub_surface_mutation"] = True
    packet["mutation_flags"]["active_release_state_mutation"] = True

    findings = validate_fee_deadline_trigger_matrix_packet_v2(packet)
    active_mutation_findings = [
        finding for finding in findings if finding.code == "active_mutation_flag"
    ]

    assert len(active_mutation_findings) == 8


def test_rejects_invalid_validation_command_shape() -> None:
    packet = valid_packet()
    packet["validation_commands"] = ["python3 ppd/daemon/ppd_daemon.py --self-test"]

    assert "invalid_validation_command" in _codes(packet)
