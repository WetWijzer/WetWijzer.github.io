from __future__ import annotations

from pathlib import Path

import pytest

from ppd.extraction.source_change_report_validation import (
    SourceChangeReportValidationError,
    source_change_report_violations,
    validate_source_change_report,
)


FIXTURES = Path(__file__).parent / "fixtures" / "source_change_reports"


def valid_report() -> dict[str, object]:
    return {
        "report_id": "fixture-report-001",
        "human_review_status": "review_required",
        "guardrail_validation_status": "draft",
        "source_evidence": [
            {
                "evidence_id": "ev-prev",
                "source_id": "src-devhub-faq",
                "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                "source_type": "public_html",
                "privacy_classification": "public",
                "content_hash": "sha256:previous",
            },
            {
                "evidence_id": "ev-current",
                "source_id": "src-devhub-faq",
                "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                "source_type": "public_html",
                "privacy_classification": "public",
                "content_hash": "sha256:current",
            },
        ],
        "changes": [
            {
                "change_id": "chg-001",
                "previous_source_evidence_id": "ev-prev",
                "current_source_evidence_id": "ev-current",
                "previous_hash": "sha256:previous",
                "current_hash": "sha256:current",
                "changed_source_hash": "sha256:current",
                "affected_requirement_ids": ["req-upload-corrections"],
                "affected_guardrail_bundle_ids": ["guardrail-devhub-upload"],
                "affected_id_citations": {
                    "req-upload-corrections": ["ev-current"],
                    "guardrail-devhub-upload": ["ev-current"],
                },
                "human_review_status": "review_required",
                "guardrail_validation_status": "draft",
            }
        ],
    }


def violation_codes(report: dict[str, object]) -> set[str]:
    return {violation.code for violation in source_change_report_violations(report)}


def test_valid_source_change_report_is_accepted() -> None:
    validate_source_change_report(valid_report())


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (
            lambda report: report["changes"][0].update(  # type: ignore[index, union-attr]
                {"changed_source_hash": "sha256:invented"}
            ),
            "invented_changed_hash",
        ),
        (
            lambda report: report["changes"][0].pop("previous_source_evidence_id"),  # type: ignore[index, union-attr]
            "missing_previous_source_evidence",
        ),
        (
            lambda report: report["changes"][0].pop("current_source_evidence_id"),  # type: ignore[index, union-attr]
            "missing_current_source_evidence",
        ),
        (
            lambda report: report["source_evidence"][1].update(  # type: ignore[index, union-attr]
                {"canonical_url": "https://devhub.portlandoregon.gov/my-permits?token=secret"}
            ),
            "private_or_authenticated_url",
        ),
        (
            lambda report: report["source_evidence"][1].update(  # type: ignore[index, union-attr]
                {"raw_body": "raw page body"}
            ),
            "raw_page_body_present",
        ),
        (
            lambda report: report["source_evidence"][1].update(  # type: ignore[index, union-attr]
                {"downloaded_path": "/home/user/Downloads/devhub.pdf"}
            ),
            "downloaded_path_present",
        ),
        (
            lambda report: report["changes"][0].pop("affected_id_citations"),  # type: ignore[index, union-attr]
            "affected_ids_without_citations",
        ),
        (
            lambda report: report["changes"][0].update(  # type: ignore[index, union-attr]
                {"guardrail_validation_status": "validated", "auto_promote_guardrails": True}
            ),
            "guardrail_auto_promotion_review_required",
        ),
    ],
)
def test_rejects_unsafe_source_change_report_patterns(mutator, expected_code: str) -> None:
    report = valid_report()
    mutator(report)

    assert expected_code in violation_codes(report)


def test_raises_with_all_violations_for_callers_that_need_fail_fast() -> None:
    report = valid_report()
    report["changes"][0]["previous_hash"] = "sha256:made-up"  # type: ignore[index]
    report["changes"][0]["affected_id_citations"] = {  # type: ignore[index]
        "req-upload-corrections": ["ev-missing"],
        "guardrail-devhub-upload": ["ev-current"],
    }

    with pytest.raises(SourceChangeReportValidationError) as excinfo:
        validate_source_change_report(report)

    assert {violation.code for violation in excinfo.value.violations} == {
        "invented_changed_hash",
        "unknown_citation_evidence",
    }
