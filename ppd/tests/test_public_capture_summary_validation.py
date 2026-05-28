from pathlib import Path

import pytest

from ppd.public_capture_summary_validation import (
    assert_public_capture_result_summary,
    validate_public_capture_result_summary,
)

FIXTURES = Path(__file__).parent / "fixtures" / "public_capture_summary"


def valid_summary() -> dict:
    digest = "a" * 64
    return {
        "source_id": "portland-ppd-public-records",
        "title": "Permit record summary",
        "public_url": "https://www.portland.gov/ppd/permits/example",
        "verified_hashes": [digest],
        "document_hash": digest,
        "citations": [{"work_item_id": "citation-001", "source_id": "portland-ppd-public-records"}],
        "extractions": [{"work_item_id": "extraction-001", "source_id": "portland-ppd-public-records"}],
        "guardrail_status": "pending_review",
        "review_status": "unreviewed",
    }


def codes(summary: dict) -> set[str]:
    return {error.code for error in validate_public_capture_result_summary(summary)}


def test_valid_public_capture_result_summary_passes() -> None:
    assert validate_public_capture_result_summary(valid_summary()) == []
    assert_public_capture_result_summary(valid_summary())


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        (lambda item: item.pop("source_id"), "missing_source_id"),
        (lambda item: item.pop("citations"), "missing_citations_work_item_links"),
        (lambda item: item.pop("extractions"), "missing_extractions_work_item_links"),
        (lambda item: item.update({"raw_body": "private crawl body"}), "raw_body_field"),
        (lambda item: item.update({"downloaded_path": "/tmp/ppd/downloads/permit.pdf"}), "downloaded_document_path"),
        (lambda item: item.update({"public_url": "https://devhub.portland.gov/permits/123?session=abc"}), "private_or_authenticated_url"),
        (lambda item: item.update({"document_hash": "b" * 64}), "invented_hash"),
        (lambda item: item.update({"guardrail_status": "ready", "review_status": "unreviewed"}), "ready_before_review"),
    ],
)
def test_rejects_public_summary_guardrail_violations(mutation, expected_code: str) -> None:
    summary = valid_summary()
    mutation(summary)
    assert expected_code in codes(summary)


def test_assertion_raises_with_deterministic_error_detail() -> None:
    summary = valid_summary()
    summary["citations"] = [{"source_id": "portland-ppd-public-records"}]

    with pytest.raises(ValueError) as exc_info:
        assert_public_capture_result_summary(summary)

    message = str(exc_info.value)
    assert "missing_citations_work_item_id" in message
    assert "citations[0]" in message
