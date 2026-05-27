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
    assert payment_review["affected_process_ids"] == ["process-devhub-fee-payment-review"]
    assert payment_review["blocked_guardrail_bundle_ids"] == ["guardrail-bundle-devhub-payment-action-gate"]


def test_public_refresh_ingestion_rejects_live_crawl_raw_body_and_private_fields() -> None:
    fixture = _fixture()
    fixture["live_crawl_performed"] = True
    with pytest.raises(PublicRefreshIngestionError, match="live_crawl"):
        build_public_refresh_ingestion_plan(fixture)

    fixture = _fixture()
    fixture["refreshed_captures"][0]["raw_body"] = "not committed"
    with pytest.raises(PublicRefreshIngestionError, match="raw or private field"):
        build_public_refresh_ingestion_plan(fixture)

    fixture = _fixture()
    fixture["refreshed_captures"][0]["canonical_url"] = "https://example.com/not-ppd"
    with pytest.raises(PublicRefreshIngestionError, match="outside the PP&D public allowlist"):
        build_public_refresh_ingestion_plan(fixture)


def test_fixture_path_is_scoped_under_ppd_tests_fixtures() -> None:
    assert FIXTURE_PATH.parent == Path(__file__).parent / "fixtures" / "public_refresh_ingestion"
