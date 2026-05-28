from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable

import pytest

from ppd.source_index_promotion_review import (
    SourceIndexPromotionReviewError,
    build_source_index_promotion_review_packet,
    build_source_index_promotion_review_packet_from_file,
)

FIXTURE = Path(__file__).parent / "fixtures" / "source_index_promotion_review" / "capture_result_summary.json"


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_builds_reviewed_source_archive_and_document_candidates_from_fixture_summary() -> None:
    packet = build_source_index_promotion_review_packet_from_file(FIXTURE)

    assert packet["packet_type"] == "ppd_source_index_promotion_review_packet"
    assert packet["status"] == "reviewed"
    assert packet["metadata_only"] is True
    assert packet["live_network_access"] is False
    assert packet["no_raw_body_persisted"] is True
    assert packet["candidate_count"] == 2
    assert packet["blockers"] == []

    candidates = {candidate["source_id"]: candidate for candidate in packet["promotion_candidates"]}
    devhub = candidates["ppd-devhub-faqs"]
    registry = devhub["source_registry_candidate"]
    archive = devhub["archive_manifest_candidate"]
    document = devhub["document_record_candidate"]

    assert registry["source_type"] == "devhub_public"
    assert registry["owning_surface"] == "devhub_public"
    assert registry["freshness_status"] == "content_hash_changed"
    assert registry["citation_links"][0]["url"] == "https://www.portland.gov/ppd/devhub-faqs"
    assert archive["manifest_id"] == "archive-manifest:fake:devhub-faqs"
    assert archive["archive_artifact_ref"].startswith("metadata-only:")
    assert archive["redirect_chain"][0]["status"] == 301
    assert archive["no_raw_body_persisted"] is True
    assert document["document_id"] == "document-fixture-ppd-devhub-faqs"
    assert document["links"][0]["content_hash"].startswith("sha256:")
    assert document["citation_spans"][0]["freshness_status"] == "content_hash_changed"
    assert document["no_raw_body_persisted"] is True
    assert devhub["hash_evidence"]["previous_content_hash"].startswith("sha256:")


def test_preserves_skipped_reason_and_pdf_review_note() -> None:
    packet = build_source_index_promotion_review_packet_from_file(FIXTURE)
    candidates = {candidate["source_id"]: candidate for candidate in packet["promotion_candidates"]}
    pdf_candidate = candidates["ppd-spp-file-naming-standards"]

    assert pdf_candidate["archive_manifest_candidate"]["skipped_reason"] == "not_modified_fixture_summary"
    assert pdf_candidate["source_registry_candidate"]["freshness_status"] == "metadata_refreshed"
    assert pdf_candidate["document_record_candidate"]["document_type"] == "pdf"
    assert "document_extraction_review" in pdf_candidate["review_notes"]


def test_rejects_raw_body_private_path_and_live_network_markers() -> None:
    fixture = _fixture()

    raw_fixture = deepcopy(fixture)
    raw_fixture["source_index_update_candidates"][0]["raw_body"] = "not allowed"
    with pytest.raises(SourceIndexPromotionReviewError, match="raw body-like"):
        build_source_index_promotion_review_packet(raw_fixture)

    path_fixture = deepcopy(fixture)
    path_fixture["source_index_update_candidates"][0]["downloaded_pdf_path"] = "/tmp/public.pdf"
    with pytest.raises(SourceIndexPromotionReviewError, match="local private path"):
        build_source_index_promotion_review_packet(path_fixture)

    live_fixture = deepcopy(fixture)
    live_fixture["live_network_access"] = True
    with pytest.raises(SourceIndexPromotionReviewError, match="live network"):
        build_source_index_promotion_review_packet(live_fixture)


def test_blocks_incomplete_paired_summary_without_partial_apply() -> None:
    fixture = _fixture()
    fixture["freshness_changes"] = fixture["freshness_changes"][:1]

    packet = build_source_index_promotion_review_packet(fixture)

    assert packet["status"] == "blocked"
    assert packet["candidate_count"] == 1
    assert any("ppd-spp-file-naming-standards" in blocker for blocker in packet["blockers"])


def test_rejects_unreviewed_ready_statuses() -> None:
    fixture = _fixture()
    fixture["source_index_update_candidates"][0]["promotion_status"] = "ready"
    fixture["source_index_update_candidates"][0].pop("human_review_status", None)

    with pytest.raises(SourceIndexPromotionReviewError, match="unreviewed ready status"):
        build_source_index_promotion_review_packet(fixture)


def test_rejects_missing_source_or_archive_identifiers() -> None:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None], str]] = [
        (
            "source_id",
            lambda fixture: fixture["source_index_update_candidates"][0].pop("source_id"),
            "missing required text field: source_id",
        ),
        (
            "manifest_id",
            lambda fixture: fixture["source_index_update_candidates"][0].pop("manifest_id"),
            "missing required text field: manifest_id",
        ),
        (
            "archive_artifact_ref",
            lambda fixture: fixture["source_index_update_candidates"][0].pop("archive_artifact_ref"),
            "missing required text field: archive_artifact_ref",
        ),
    ]

    for _name, mutate, expected in mutations:
        fixture = _fixture()
        mutate(fixture)
        with pytest.raises(SourceIndexPromotionReviewError, match=expected):
            build_source_index_promotion_review_packet(fixture)


def test_rejects_uncited_document_records() -> None:
    fixture = _fixture()
    fixture["source_index_update_candidates"][0]["citation_links"] = []
    fixture["extraction_work_items"][0]["citation_links"] = []
    fixture["source_index_update_candidates"][0]["canonical_url"] = ""

    with pytest.raises(SourceIndexPromotionReviewError, match="missing required text field: canonical_url"):
        build_source_index_promotion_review_packet(fixture)


def test_rejects_invented_hashes() -> None:
    fixture = _fixture()
    fixture["extraction_work_items"][0]["content_hash"] = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    packet = build_source_index_promotion_review_packet(fixture)

    assert packet["status"] == "blocked"
    assert any("invented hashes" in blocker for blocker in packet["blockers"])


def test_rejects_private_and_authenticated_urls() -> None:
    mutations: list[tuple[Callable[[dict[str, Any]], None], str]] = [
        (
            lambda fixture: fixture["source_index_update_candidates"][0].__setitem__(
                "canonical_url",
                "https://user:secret@www.portland.gov/ppd/devhub-faqs",
            ),
            "private/authenticated URL",
        ),
        (
            lambda fixture: fixture["source_index_update_candidates"][0].__setitem__(
                "canonical_url",
                "https://www.portland.gov/ppd/devhub-faqs?token=secret",
            ),
            "private/authenticated URL",
        ),
        (
            lambda fixture: fixture["source_index_update_candidates"][0].__setitem__(
                "canonical_url",
                "https://devhub.portlandoregon.gov/account/permits",
            ),
            "private/authenticated URL",
        ),
    ]

    for mutate, expected in mutations:
        fixture = _fixture()
        mutate(fixture)
        with pytest.raises(SourceIndexPromotionReviewError, match=expected):
            build_source_index_promotion_review_packet(fixture)


def test_rejects_processor_outputs_without_metadata_only_artifact_refs() -> None:
    fixture = _fixture()
    fixture["processor_outputs"][0]["artifact_ref"] = "ipfs://raw-output"

    packet = build_source_index_promotion_review_packet(fixture)

    assert packet["status"] == "blocked"
    assert any("artifact_ref must be a metadata-only artifact reference" in blocker for blocker in packet["blockers"])

    metadata_flag_fixture = _fixture()
    metadata_flag_fixture["processor_outputs"][0]["metadata_only"] = False
    blocked = build_source_index_promotion_review_packet(metadata_flag_fixture)
    assert blocked["status"] == "blocked"
    assert any("processor outputs must be metadata_only true" in blocker for blocker in blocked["blockers"])
