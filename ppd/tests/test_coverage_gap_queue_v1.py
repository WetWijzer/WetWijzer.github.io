from pathlib import Path

import pytest

from ppd.coverage_gap_queue_v1 import (
    GAP_TYPES,
    CoverageGapQueueValidationError,
    assert_valid_coverage_gap_queue_v1,
    build_coverage_gap_queue_from_paths,
    is_valid_coverage_gap_queue_v1,
    validate_coverage_gap_queue_v1,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "coverage_gap_queue_v1"


def build_fixture_queue() -> dict:
    return build_coverage_gap_queue_from_paths(
        {
            "traceability_packet": FIXTURE_DIR / "source_to_requirement_traceability_packet_v1.json",
            "document_records": FIXTURE_DIR / "document_records.json",
            "requirement_nodes": FIXTURE_DIR / "requirement_nodes.json",
            "public_source_change_impact": FIXTURE_DIR / "public_source_change_impact_rehearsal_v1.json",
            "official_source_anchor_audit": FIXTURE_DIR / "official_source_anchor_audit_packet_v1.json",
        }
    )


def validation_codes(packet: dict) -> set[str]:
    return {violation.code for violation in validate_coverage_gap_queue_v1(packet)}


def test_fixture_first_queue_covers_required_gap_types() -> None:
    queue_packet = build_fixture_queue()

    queue = queue_packet["queue"]
    assert queue_packet["packet_type"] == "fixture_first_requirement_extraction_coverage_gap_queue_v1"
    assert {item["gap_type"] for item in queue} == set(GAP_TYPES)
    assert len(queue) == len(GAP_TYPES)
    assert is_valid_coverage_gap_queue_v1(queue_packet)

    for item in queue:
        assert item["affected_document_ids"]
        assert item["affected_source_ids"]
        assert item["affected_requirement_ids"]
        assert item["citation"]["source_id"] in item["affected_source_ids"]
        assert item["citation"]["url"].startswith("https://www.portland.gov/ppd/")
        assert item["citation"]["anchor"]
        assert item["human_review_status"] == "needs_review"
        assert item["reviewer_owner"] == "ppd-fixture-reviewer"
        assert "Fixture-only queue item" in item["rollback_note"]
        assert ["python3", "-m", "pytest", "ppd/tests/test_coverage_gap_queue_v1.py"] in item["offline_validation_commands"]


def test_public_source_change_impact_is_carried_into_queue_items() -> None:
    queue_packet = build_fixture_queue()

    impacted = [item for item in queue_packet["queue"] if item["public_source_change_impacted"]]
    assert {item["gap_type"] for item in impacted} == {"fee_triggers", "deadlines", "action_gates"}


def test_rejects_uncited_gaps_and_missing_affected_ids() -> None:
    queue_packet = build_fixture_queue()
    item = queue_packet["queue"][0]
    item["citation"] = {"source_id": "src-not-affected", "audit_status": "missing_source_anchor"}
    item["affected_document_ids"] = []
    item["affected_source_ids"] = []
    item["affected_requirement_ids"] = []

    codes = validation_codes(queue_packet)

    assert "uncited_gap" in codes
    assert "missing_affected_document_ids" in codes
    assert "missing_affected_source_ids" in codes
    assert "missing_affected_requirement_ids" in codes


def test_rejects_missing_human_review_owner_and_rollback_fields() -> None:
    queue_packet = build_fixture_queue()
    item = queue_packet["queue"][0]
    item.pop("human_review_status")
    item["reviewer_owner"] = ""
    item["rollback_note"] = ""

    codes = validation_codes(queue_packet)

    assert "missing_required_field" in codes
    assert "missing_human_review_status" in codes
    assert "missing_reviewer_owner" in codes
    assert "missing_rollback_note" in codes


def test_rejects_private_auth_raw_pdf_and_downloaded_artifacts() -> None:
    queue_packet = build_fixture_queue()
    item = queue_packet["queue"][0]
    item.update(
        {
            "storage_state": "private-devhub-state.json",
            "auth": {"cookie": "redacted-but-still-forbidden"},
            "raw_crawl_output": "raw body",
            "raw_pdf": "base64-pdf-data",
            "downloaded_document": "permit.pdf",
        }
    )

    codes = validation_codes(queue_packet)

    assert "private_or_authenticated_artifact" in codes
    assert "raw_artifact" in codes


def test_rejects_live_claims_guarantees_and_consequential_language() -> None:
    queue_packet = build_fixture_queue()
    item = queue_packet["queue"][0]
    item["operator_note"] = "Live extraction ran and requirements promoted to active."
    item["legal_note"] = "Approval guaranteed and the permit will be issued."
    item["next_action"] = "Submit permit and pay fee in DevHub."

    codes = validation_codes(queue_packet)

    assert "live_extraction_or_promotion_claim" in codes
    assert "legal_or_permitting_outcome_guarantee" in codes
    assert "consequential_action_language" in codes


def test_rejects_active_mutation_flags_for_ppd_state_surfaces() -> None:
    queue_packet = build_fixture_queue()
    item = queue_packet["queue"][0]
    item.update(
        {
            "active_source_mutation": True,
            "active_document_mutation": True,
            "active_requirement_mutation": True,
            "active_process_mutation": True,
            "active_guardrail_mutation": True,
            "active_release_state_mutation": True,
            "active_agent_state_mutation": True,
        }
    )

    codes = validation_codes(queue_packet)

    assert "active_mutation_flag" in codes


def test_assert_valid_raises_with_codes_for_invalid_queue() -> None:
    queue_packet = build_fixture_queue()
    queue_packet["queue"][0]["citation"] = {}

    with pytest.raises(CoverageGapQueueValidationError) as context:
        assert_valid_coverage_gap_queue_v1(queue_packet)

    assert "uncited_gap" in str(context.value)
