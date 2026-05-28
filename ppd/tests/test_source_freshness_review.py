from copy import deepcopy
from pathlib import Path

import pytest

from ppd.extraction.source_freshness_review import (
    build_source_freshness_review_packet,
    load_fixture,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source_freshness"


def _fixture():
    return load_fixture(FIXTURE_DIR / "source_freshness_packet_fixture.json")


def test_source_freshness_packet_maps_cadence_hashes_requirements_and_prompts():
    fixture = _fixture()

    packet = build_source_freshness_review_packet(
        fixture, generated_at="2026-05-27T00:00:00+00:00"
    )

    assert packet["review_mode"] == "fixture-first-offline"
    assert packet["raw_body_persisted"] is False
    assert packet["packet_id"].startswith("source-freshness-")

    by_source = {item["source_id"]: item for item in packet["items"]}
    devhub_faq = by_source["ppd-devhub-faq"]
    assert devhub_faq["recrawl_cadence"] == "daily"
    assert devhub_faq["previous_hash"] == "sha256:" + "0" * 64
    assert devhub_faq["latest_hash"] == "sha256:" + "1" * 64
    assert devhub_faq["hash_changed"] is True
    assert devhub_faq["freshness_status"] == "changed_needs_review"
    assert devhub_faq["affected_requirement_ids"] == [
        "REQ-DEVHUB-READONLY-001",
        "REQ-DEVHUB-UPLOAD-GATE-002",
    ]
    assert any("source hash changed" in prompt for prompt in devhub_faq["human_review_prompts"])
    assert any("REQ-DEVHUB-UPLOAD-GATE-002" in prompt for prompt in devhub_faq["human_review_prompts"])
    assert any("Escalate for human review" in prompt for prompt in devhub_faq["human_review_prompts"])

    file_standards = by_source["ppd-file-naming-standards"]
    assert file_standards["recrawl_cadence"] == "weekly"
    assert file_standards["hash_changed"] is False
    assert file_standards["freshness_status"] == "previously_current"
    assert file_standards["affected_requirement_ids"] == ["REQ-FILE-NAMING-001"]
    assert file_standards["no_raw_body_persisted"] is True

    fee_guide = by_source["ppd-fee-payment-guide"]
    assert fee_guide["source_type"] == "public_pdf"
    assert fee_guide["recrawl_cadence"] == "daily"
    assert fee_guide["hash_changed"] is True
    assert fee_guide["affected_requirement_ids"] == [
        "REQ-FEE-PAYMENT-GATE-001",
        "REQ-FEE-RECEIPT-002",
    ]
    assert any("fee payment instruction" in prompt for prompt in fee_guide["human_review_prompts"])


def test_source_freshness_packet_rejects_raw_body_fields():
    fixture = _fixture()
    fixture["public_capture_summaries"][0]["raw_html"] = "raw captured body"

    with pytest.raises(ValueError, match="raw body persistence is not allowed"):
        build_source_freshness_review_packet(fixture, generated_at="2026-05-27T00:00:00+00:00")


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (
            lambda fixture: fixture["source_registry"][0].update(
                {"canonical_url": "https://devhub.portlandoregon.gov/my-permits/12345"}
            ),
            "private/authenticated URL",
        ),
        (
            lambda fixture: fixture["public_capture_summaries"][0].update(
                {"downloaded_document_path": "/tmp/devhub-private.pdf"}
            ),
            "downloaded document paths are not allowed",
        ),
        (
            lambda fixture: fixture["source_registry"][0].update({"content_hash": "sha256:old-devhub-faq"}),
            "invented or invalid sha256 hash",
        ),
        (
            lambda fixture: fixture["public_capture_summaries"][0].pop("source_id"),
            "source_id must be a non-empty string",
        ),
        (
            lambda fixture: fixture["requirement_index"].update({"ppd-devhub-faq": []}),
            "missing affected requirement links",
        ),
        (
            lambda fixture: fixture["public_capture_summaries"][0].update(
                {
                    "human_review_required": True,
                    "guardrail_readiness_status": "ready",
                }
            ),
            "guardrail status cannot be ready while human review is still required",
        ),
    ],
)
def test_source_freshness_packet_rejects_unsafe_review_packet_fields(mutator, message):
    fixture = deepcopy(_fixture())
    mutator(fixture)

    with pytest.raises(ValueError, match=message):
        build_source_freshness_review_packet(fixture, generated_at="2026-05-27T00:00:00+00:00")
