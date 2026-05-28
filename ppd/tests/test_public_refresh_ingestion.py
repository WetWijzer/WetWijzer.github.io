from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.public_refresh_ingestion import PublicRefreshIngestionError, build_public_refresh_ingestion_plan


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_refresh_ingestion" / "metadata_only_refreshed_captures.json"


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_build_public_refresh_ingestion_plan_is_fixture_first_and_deterministic() -> None:
    fixture = _fixture()

    first = build_public_refresh_ingestion_plan(fixture).to_dict()
    second = build_public_refresh_ingestion_plan(copy.deepcopy(fixture)).to_dict()

    assert first == second
    assert first["plan_id"].startswith("public-refresh-ingestion-")
    assert first["no_live_crawl"] is True
    assert first["no_raw_body_storage"] is True
    assert len(first["source_index_hash_deltas"]) == 2
    assert {delta["changed"] for delta in first["source_index_hash_deltas"]} == {True}
    assert {item["delta_kind"] for item in first["requirement_delta_review_items"]} == {"added", "changed"}
    assert {item["human_review_status"] for item in first["requirement_delta_review_items"]} == {"pending_human_review"}


def test_plan_rolls_requirement_deltas_up_to_processes_and_blocked_guardrails() -> None:
    plan = build_public_refresh_ingestion_plan(_fixture()).to_dict()

    assert plan["affected_process_ids"] == [
        "process-devhub-fee-payment-review",
        "process-residential-building-permit",
        "process-single-pdf-plan-review",
        "process-trade-permit-with-plan-review",
    ]
    assert plan["blocked_guardrail_bundle_ids"] == [
        "guardrail-bundle-devhub-payment-action-gate",
        "guardrail-bundle-residential-building-permit",
        "guardrail-bundle-single-pdf-plan-review",
        "guardrail-bundle-trade-permit-with-plan-review",
    ]

    payment_review = next(
        item
        for item in plan["requirement_delta_review_items"]
        if item["requirement_id"] == "req-devhub-payment-exact-confirmation"
    )
    assert payment_review["requirement_type"] == "action_gate"
    assert payment_review["citation_spans"] == ["devhub-faqs#payment-actions"]
    assert payment_review["affected_process_ids"] == ["process-devhub-fee-payment-review"]
    assert payment_review["blocked_guardrail_bundle_ids"] == ["guardrail-bundle-devhub-payment-action-gate"]


def test_public_refresh_ingestion_rejects_live_crawl_raw_body_and_downloaded_paths() -> None:
    fixture = _fixture()
    fixture["live_crawl_performed"] = True
    with pytest.raises(PublicRefreshIngestionError, match="live_crawl"):
        build_public_refresh_ingestion_plan(fixture)

    fixture = _fixture()
    fixture["refreshed_captures"][0]["raw_body"] = "not committed"
    with pytest.raises(PublicRefreshIngestionError, match="raw or private field"):
        build_public_refresh_ingestion_plan(fixture)

    fixture = _fixture()
    fixture["refreshed_captures"][0]["downloaded_document_path"] = "/tmp/private/download.pdf"
    with pytest.raises(PublicRefreshIngestionError, match="raw or private field"):
        build_public_refresh_ingestion_plan(fixture)


def test_public_refresh_ingestion_rejects_private_or_authenticated_urls() -> None:
    fixture = _fixture()
    fixture["refreshed_captures"][0]["canonical_url"] = "https://example.com/not-ppd"
    with pytest.raises(PublicRefreshIngestionError, match="outside the PP&D public allowlist"):
        build_public_refresh_ingestion_plan(fixture)

    fixture = _fixture()
    fixture["refreshed_captures"][0]["canonical_url"] = "https://devhub.portlandoregon.gov/dashboard"
    with pytest.raises(PublicRefreshIngestionError, match="requires authentication"):
        build_public_refresh_ingestion_plan(fixture)

    fixture = _fixture()
    fixture["refreshed_captures"][0]["source_url"] = "https://user:secret@www.portland.gov/ppd"
    with pytest.raises(PublicRefreshIngestionError, match="must not include credentials"):
        build_public_refresh_ingestion_plan(fixture)


def test_public_refresh_ingestion_rejects_requirement_metadata_gaps() -> None:
    fixture = _fixture()
    del fixture["refreshed_captures"][0]["requirement_deltas"][0]["citation_spans"]
    with pytest.raises(PublicRefreshIngestionError, match="citation_spans"):
        build_public_refresh_ingestion_plan(fixture)

    fixture = _fixture()
    fixture["refreshed_captures"][0]["requirement_deltas"][0]["requirement_type"] = "informational_note"
    with pytest.raises(PublicRefreshIngestionError, match="unsupported requirement_type"):
        build_public_refresh_ingestion_plan(fixture)

    fixture = _fixture()
    fixture["refreshed_captures"][0]["affected_process_ids"] = []
    fixture["refreshed_captures"][0]["requirement_deltas"][0]["affected_process_ids"] = []
    with pytest.raises(PublicRefreshIngestionError, match="missing affected_process_ids"):
        build_public_refresh_ingestion_plan(fixture)

    fixture = _fixture()
    fixture["refreshed_captures"][0]["guardrail_bundle_ids"] = []
    fixture["refreshed_captures"][0]["requirement_deltas"][0]["blocked_guardrail_bundle_ids"] = []
    with pytest.raises(PublicRefreshIngestionError, match="missing blocked_guardrail_bundle_ids"):
        build_public_refresh_ingestion_plan(fixture)


def test_public_refresh_ingestion_rejects_ready_guardrails_before_human_review() -> None:
    fixture = _fixture()
    delta = fixture["refreshed_captures"][0]["requirement_deltas"][0]
    delta["human_review_status"] = "pending_human_review"
    delta["refreshed_guardrail_status"] = "ready"

    with pytest.raises(PublicRefreshIngestionError, match="before human review is complete"):
        build_public_refresh_ingestion_plan(fixture)


def test_fixture_path_is_scoped_under_ppd_tests_fixtures() -> None:
    assert FIXTURE_PATH.parent == Path(__file__).parent / "fixtures" / "public_refresh_ingestion"
