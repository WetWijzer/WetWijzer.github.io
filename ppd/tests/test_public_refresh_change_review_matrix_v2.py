from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.public_refresh_change_review_matrix_v2 import (
    PublicRefreshChangeReviewMatrixV2Error,
    build_public_refresh_change_review_matrix_v2,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "public_refresh_change_review_matrix_v2"
    / "public_refresh_observation_plan_v2.json"
)


def _fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_builds_ordered_change_review_rows_from_observation_plan_v2() -> None:
    matrix = build_public_refresh_change_review_matrix_v2(_fixture())
    matrix_dict = matrix.to_dict()

    assert matrix_dict["source_plan_id"] == "fixture-public-refresh-observation-plan-v2-001"
    assert matrix_dict["live_source_fetch_performed"] is False
    assert matrix_dict["raw_body_persisted"] is False
    assert matrix_dict["pdf_downloaded"] is False
    assert matrix_dict["active_source_registry_changed"] is False
    assert matrix_dict["formal_guardrails_updated"] is False

    rows = matrix_dict["rows"]
    assert [row["disposition_bucket"] for row in rows] == [
        "changed",
        "unchanged",
        "skipped",
        "stale_source",
    ]
    assert [row["row_order"] for row in rows] == [1, 2, 3, 4]


def test_rows_include_placeholder_links_and_reviewer_dispositions() -> None:
    matrix = build_public_refresh_change_review_matrix_v2(_fixture()).to_dict()
    changed_row = matrix["rows"][0]
    stale_row = matrix["rows"][3]

    assert changed_row["reviewer_disposition_placeholder"] == "reviewer_disposition_pending_changed_document_rule_review"
    assert changed_row["recrawl_deferral_reason"] == "not_deferred_change_requires_human_review_before_promotion"
    assert changed_row["affected_requirement_links"] == [
        {
            "link_id": "placeholder-requirement-obs-changed-submit-plans-online-placeholder-req-single-pdf-process",
            "target_id": "placeholder-req-single-pdf-process",
            "placeholder_href": "ppd://placeholder/requirement/placeholder-req-single-pdf-process",
            "review_status": "placeholder_pending_human_review",
        },
        {
            "link_id": "placeholder-requirement-obs-changed-submit-plans-online-placeholder-req-supporting-documents-separate-pdfs",
            "target_id": "placeholder-req-supporting-documents-separate-pdfs",
            "placeholder_href": "ppd://placeholder/requirement/placeholder-req-supporting-documents-separate-pdfs",
            "review_status": "placeholder_pending_human_review",
        },
    ]
    assert changed_row["affected_guardrail_links"][0]["placeholder_href"] == "ppd://placeholder/guardrail/placeholder-guardrail-document-preparation"
    assert stale_row["recrawl_deferral_reason"] == "deferred_until_offline_fee_payment_source_refresh_is_scheduled"


def test_exact_offline_validation_commands_are_preserved_on_matrix_and_rows() -> None:
    matrix = build_public_refresh_change_review_matrix_v2(_fixture()).to_dict()
    expected_commands = [
        ["python3", "-m", "py_compile", "ppd/public_refresh_change_review_matrix_v2.py"],
        ["python3", "-m", "py_compile", "ppd/tests/test_public_refresh_change_review_matrix_v2.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_public_refresh_change_review_matrix_v2.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]

    assert matrix["exact_offline_validation_commands"] == expected_commands
    assert all(row["exact_offline_validation_commands"] == expected_commands for row in matrix["rows"])


def test_rejects_missing_required_review_bucket_rows() -> None:
    fixture = _fixture()
    fixture["observations"] = [row for row in fixture["observations"] if row["status"] != "stale_source"]

    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="review rows must cover"):
        build_public_refresh_change_review_matrix_v2(fixture)


def test_rejects_missing_reviewer_disposition_and_recrawl_deferral_reason() -> None:
    fixture = _fixture()
    del fixture["observations"][0]["reviewer_disposition_placeholder"]
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="reviewer_disposition_placeholder must be a non-empty string"):
        build_public_refresh_change_review_matrix_v2(fixture)

    fixture = _fixture()
    del fixture["observations"][0]["recrawl_deferral_reason"]
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="recrawl_deferral_reason must be a non-empty string"):
        build_public_refresh_change_review_matrix_v2(fixture)


def test_rejects_missing_validation_commands() -> None:
    fixture = _fixture()
    del fixture["exact_offline_validation_commands"]

    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="exact_offline_validation_commands must be provided"):
        build_public_refresh_change_review_matrix_v2(fixture)


def test_rejects_live_fetch_or_raw_body_fields() -> None:
    fixture = _fixture()
    fixture["live_source_fetch_performed"] = True
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="live_source_fetch_performed must be false"):
        build_public_refresh_change_review_matrix_v2(fixture)

    fixture = _fixture()
    fixture["observations"][0]["raw_body"] = "not allowed"
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="raw or private field"):
        build_public_refresh_change_review_matrix_v2(fixture)

    fixture = _fixture()
    fixture["observations"][0]["downloaded_pdf"] = "ppd/tests/fixtures/private.pdf"
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="raw or private field"):
        build_public_refresh_change_review_matrix_v2(fixture)


def test_rejects_non_public_urls_and_missing_placeholders() -> None:
    fixture = _fixture()
    fixture["observations"][0]["public_url"] = "https://example.com/not-allowed"
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="outside the PP&D public allowlist"):
        build_public_refresh_change_review_matrix_v2(fixture)

    fixture = _fixture()
    fixture["observations"][0]["affected_guardrail_ids"] = []
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="must include affected_guardrail_ids"):
        build_public_refresh_change_review_matrix_v2(fixture)

    fixture = _fixture()
    fixture["observations"][0]["affected_requirement_ids"] = ["req-single-pdf-process"]
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="must contain placeholder ids"):
        build_public_refresh_change_review_matrix_v2(fixture)


def test_rejects_live_claims_consequential_language_and_guarantees() -> None:
    fixture = _fixture()
    fixture["observations"][0]["change_summary"] = "Live crawl completed for this source."
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="live crawl claim"):
        build_public_refresh_change_review_matrix_v2(fixture)

    fixture = _fixture()
    fixture["observations"][0]["change_summary"] = "Reviewer says the submitted permit is complete."
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="consequential official action language"):
        build_public_refresh_change_review_matrix_v2(fixture)

    fixture = _fixture()
    fixture["observations"][0]["change_summary"] = "This creates a guarantee that the permit will be approved."
    with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="legal or permitting guarantee"):
        build_public_refresh_change_review_matrix_v2(fixture)


def test_rejects_active_source_process_requirement_guardrail_prompt_or_release_mutation_flags() -> None:
    for key in (
        "active_source_registry_changed",
        "active_process_model_changed",
        "active_requirement_registry_changed",
        "active_guardrail_bundle_changed",
        "active_prompt_changed",
        "active_release_state_changed",
    ):
        fixture = _fixture()
        fixture[key] = True
        with pytest.raises(PublicRefreshChangeReviewMatrixV2Error, match="active mutation flag must be false"):
            build_public_refresh_change_review_matrix_v2(fixture)
