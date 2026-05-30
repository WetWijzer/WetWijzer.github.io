from pathlib import Path

import pytest

from ppd.document_extraction_task_packet_v1 import (
    DOCUMENT_FAMILY,
    TARGET_TYPES,
    DocumentExtractionTaskPacketError,
    assert_valid_document_extraction_task_packet_v1,
    build_document_extraction_task_packet_from_paths,
    is_valid_document_extraction_task_packet_v1,
    validate_document_extraction_task_packet_v1,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "document_extraction_task_packet_v1"


def build_fixture_packet() -> dict:
    return build_document_extraction_task_packet_from_paths(
        {
            "coverage_gap_prioritization_packet": FIXTURE_DIR / "coverage_gap_prioritization_packet_v1.json",
            "document_records": FIXTURE_DIR / "document_records.json",
        }
    )


def validation_codes(packet: dict) -> set[str]:
    return {violation.code for violation in validate_document_extraction_task_packet_v1(packet)}


def test_builds_fixture_first_document_extraction_work_items_for_one_family() -> None:
    packet = build_fixture_packet()

    assert packet["packet_type"] == "fixture_first_document_extraction_task_packet_v1"
    assert packet["document_family"] == DOCUMENT_FAMILY
    assert packet["target_types"] == list(TARGET_TYPES)
    assert is_valid_document_extraction_task_packet_v1(packet)

    work_items = packet["work_items"]
    assert {item["target_type"] for item in work_items} == set(TARGET_TYPES)
    assert len(work_items) == len(TARGET_TYPES)

    for item in work_items:
        assert item["document_family"] == DOCUMENT_FAMILY
        assert item["priority_row_id"] == "priority-v1:pdfs:single-pdf-process-guidance:001"
        assert item["affected_document_id"] == "doc-single-pdf-process-guidance"
        assert item["affected_source_id"] == "src-submit-plans-online"
        assert item["fixture_input_ref"].startswith("document_records:")
        assert item["expected_fixture_output_ref"].startswith("ppd/tests/fixtures/document_extraction_task_packet_v1/")
        assert item["citation"]["source_id"] == item["affected_source_id"]
        assert item["citation"]["document_id"] == item["affected_document_id"]
        assert item["citation"]["url"].startswith("https://www.portland.gov/ppd/")
        assert item["citation"]["anchor"]
        assert item["human_review_status"] == "needs_review"
        assert item["reviewer_owner"] == "ppd-document-extraction-reviewer"
        assert "Fixture-only extraction task" in item["rollback_note"]
        assert ["python3", "-m", "pytest", "ppd/tests/test_document_extraction_task_packet_v1.py"] in item["offline_validation_commands"]


def test_safety_attestations_block_live_document_handling_outcomes_actions_and_mutation() -> None:
    packet = build_fixture_packet()

    assert packet["safety_attestations"] == {
        "fixture_first_only": True,
        "no_private_files_read": True,
        "no_authenticated_artifacts": True,
        "no_document_downloads": True,
        "no_ocr_execution": True,
        "no_raw_pdf_persistence": True,
        "no_live_extraction_or_processor_execution": True,
        "no_legal_or_permitting_outcome_guarantees": True,
        "no_consequential_actions": True,
        "no_active_state_mutation": True,
    }


def test_rejects_uncited_work_items_missing_ids_targets_review_owner_and_rollback() -> None:
    packet = build_fixture_packet()
    item = packet["work_items"][0]
    item["citation"] = {"source_id": "", "document_id": "", "url": "", "anchor": ""}
    item["affected_document_id"] = ""
    item["affected_source_id"] = ""
    item["target_type"] = ""
    item["fixture_input_ref"] = ""
    item["expected_fixture_output_ref"] = ""
    item["human_review_status"] = ""
    item["reviewer_owner"] = ""
    item["rollback_note"] = ""

    codes = validation_codes(packet)

    assert "uncited_work_item" in codes
    assert "missing_document_id" in codes
    assert "missing_source_id" in codes
    assert "missing_extraction_target_field" in codes
    assert "missing_human_review_status" in codes
    assert "missing_reviewer_owner" in codes
    assert "missing_rollback_note" in codes


def test_rejects_citation_source_and_document_mismatch() -> None:
    packet = build_fixture_packet()
    item = packet["work_items"][0]
    item["citation"]["source_id"] = "src-other"
    item["citation"]["document_id"] = "doc-other"

    codes = validation_codes(packet)

    assert "citation_source_mismatch" in codes
    assert "citation_document_mismatch" in codes


def test_rejects_private_authenticated_downloaded_raw_ocr_and_processor_artifacts() -> None:
    packet = build_fixture_packet()
    item = packet["work_items"][0]
    item.update(
        {
            "auth_state": "state.json",
            "private_file_path": "/Users/example/private/permit.pdf",
            "downloaded_pdf": "permit.pdf",
            "raw_pdf": "base64-data",
            "ocr_output": "text from OCR",
            "processor_output": {"claim": "complete"},
            "live_extraction": True,
        }
    )
    item["operator_note"] = "Processor executed live extraction after auth state review. OCR ran and raw PDF saved."

    codes = validation_codes(packet)

    assert "forbidden_private_authenticated_or_raw_artifact" in codes
    assert "forbidden_live_extraction_or_processor_claim" in codes


def test_rejects_legal_or_permitting_guarantees_and_consequential_action_language() -> None:
    packet = build_fixture_packet()
    item = packet["work_items"][0]
    item.update(
        {
            "approval_guarantee": True,
            "submit_permit": True,
            "review_note": "Permit will be approved after you submit permit materials and pay the fee.",
        }
    )

    codes = validation_codes(packet)

    assert "forbidden_legal_or_permitting_outcome_guarantee" in codes
    assert "forbidden_consequential_action_language" in codes


def test_rejects_active_source_document_requirement_process_guardrail_release_and_agent_mutations() -> None:
    packet = build_fixture_packet()
    packet.update(
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

    codes = validation_codes(packet)

    assert "active_ppd_state_mutation" in codes


def test_rejects_unsafe_validation_commands() -> None:
    packet = build_fixture_packet()
    packet["offline_validation_commands"] = [["curl", "https://www.portland.gov/ppd/get-permit/submit-plans-online"]]

    codes = validation_codes(packet)

    assert "unsafe_validation_command" in codes


def test_assert_valid_raises_with_codes() -> None:
    packet = build_fixture_packet()
    packet["target_types"] = ["sections"]

    with pytest.raises(DocumentExtractionTaskPacketError) as context:
        assert_valid_document_extraction_task_packet_v1(packet)

    assert "missing_target_coverage" in str(context.value)
