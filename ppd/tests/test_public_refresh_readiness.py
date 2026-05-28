from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ppd.public_refresh.readiness import build_readiness_packet, build_readiness_packet_from_files

FIXTURES = Path(__file__).parent / "fixtures" / "public_refresh_readiness"


def test_public_refresh_readiness_packet_is_ready_for_metadata_only_fixture() -> None:
    packet = build_readiness_packet_from_files(
        ingestion_outputs_path=FIXTURES / "ingestion_outputs.json",
        requirement_delta_status_path=FIXTURES / "requirement_delta_status.json",
        process_model_versions_path=FIXTURES / "process_model_versions.json",
        source_freshness_path=FIXTURES / "source_freshness.json",
        human_review_state_path=FIXTURES / "human_review_state.json",
        generated_at="2026-05-27T00:00:00Z",
    )

    assert packet["packet_type"] == "ppd_public_refresh_promotion_readiness"
    assert packet["status"] == "ready"
    assert packet["metadata_only"] is True
    assert packet["live_crawl_performed"] is False
    assert packet["raw_bodies_persisted"] is False
    assert packet["blockers"] == []
    assert {gate["gate"] for gate in packet["gates"]} == {
        "public_refresh_ingestion_metadata",
        "requirement_delta_formalization",
        "process_model_versions",
        "source_freshness",
        "human_review_state",
        "guardrail_process_version_evidence",
    }
    assert packet["inputs"]["source_ids"] == ["ppd-devhub-faq", "ppd-submit-plans-online"]


def test_public_refresh_readiness_blocks_raw_body_like_ingestion_metadata() -> None:
    packet = build_readiness_packet(
        ingestion_outputs={
            "refresh_id": "raw-body-regression",
            "outputs": [
                {
                    "source_id": "ppd-devhub-faq",
                    "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                    "content_hash": "sha256:fixture",
                    "normalized_document_id": "doc-devhub-faq",
                    "no_raw_body_persisted": True,
                    "metadata_only": True,
                    "raw_body": "this must never be promotion metadata",
                }
            ],
        },
        requirement_delta_status={
            "deltas": [
                {
                    "delta_id": "delta-001",
                    "requirement_id": "req-001",
                    "formalization_status": "formalized",
                    "human_review_status": "approved",
                    "affected_process_ids": ["building-permit-application"],
                    "affected_guardrail_ids": ["guardrail-building-permit-fixture"],
                    "source_evidence_ids": ["doc-devhub-faq"],
                }
            ]
        },
        process_model_versions={
            "process_models": [
                {
                    "process_id": "building-permit-application",
                    "version": "2026.05.27-fixture",
                    "guardrail_bundle_id": "guardrail-building-permit-fixture",
                    "validation_status": "valid",
                    "source_evidence_ids": ["doc-devhub-faq"],
                }
            ]
        },
        source_freshness={
            "sources": [
                {
                    "source_id": "ppd-devhub-faq",
                    "freshness_status": "current",
                    "last_seen_at": "2026-05-27T00:00:00Z",
                    "content_hash": "sha256:fixture",
                }
            ]
        },
        human_review_state={
            "reviews": [
                {
                    "review_id": "review-001",
                    "subject_id": "delta-001",
                    "subject_type": "requirement_delta",
                    "status": "approved",
                }
            ]
        },
    )

    assert packet["status"] == "blocked"
    assert any("raw body-like" in blocker for blocker in packet["blockers"])


def _ready_inputs() -> dict[str, dict[str, object]]:
    return {
        "ingestion_outputs": {
            "refresh_id": "fixture-refresh",
            "outputs": [
                {
                    "source_id": "ppd-devhub-faq",
                    "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                    "content_hash": "sha256:fixture",
                    "normalized_document_id": "doc-devhub-faq",
                    "no_raw_body_persisted": True,
                    "metadata_only": True,
                }
            ],
        },
        "requirement_delta_status": {
            "deltas": [
                {
                    "delta_id": "delta-001",
                    "requirement_id": "req-001",
                    "formalization_status": "formalized",
                    "human_review_status": "approved",
                    "affected_process_ids": ["process-001"],
                    "affected_guardrail_ids": ["guardrail-001"],
                    "source_evidence_ids": ["doc-devhub-faq"],
                }
            ]
        },
        "process_model_versions": {
            "process_models": [
                {
                    "process_id": "process-001",
                    "version": "2026.05.27-fixture",
                    "guardrail_bundle_id": "guardrail-001",
                    "validation_status": "valid",
                    "source_evidence_ids": ["doc-devhub-faq"],
                }
            ]
        },
        "source_freshness": {
            "sources": [
                {
                    "source_id": "ppd-devhub-faq",
                    "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                    "freshness_status": "current",
                    "last_seen_at": "2026-05-27T00:00:00Z",
                    "content_hash": "sha256:fixture",
                }
            ]
        },
        "human_review_state": {
            "reviews": [
                {
                    "review_id": "review-001",
                    "subject_id": "delta-001",
                    "subject_type": "requirement_delta",
                    "status": "approved",
                }
            ]
        },
    }


def _packet_with(inputs: dict[str, dict[str, object]]) -> dict[str, object]:
    return build_readiness_packet(
        ingestion_outputs=inputs["ingestion_outputs"],
        requirement_delta_status=inputs["requirement_delta_status"],
        process_model_versions=inputs["process_model_versions"],
        source_freshness=inputs["source_freshness"],
        human_review_state=inputs["human_review_state"],
    )


def test_public_refresh_readiness_rejects_stale_or_missing_citations() -> None:
    inputs = _ready_inputs()
    delta = inputs["requirement_delta_status"]["deltas"][0]
    delta["source_evidence_ids"] = ["doc-stale"]

    packet = _packet_with(inputs)

    assert packet["status"] == "blocked"
    assert any("cites stale or missing evidence ids" in blocker for blocker in packet["blockers"])

    inputs = _ready_inputs()
    del inputs["requirement_delta_status"]["deltas"][0]["source_evidence_ids"]

    packet = _packet_with(inputs)

    assert packet["status"] == "blocked"
    assert any("lacks citation evidence" in blocker for blocker in packet["blockers"])


def test_public_refresh_readiness_rejects_incomplete_human_review() -> None:
    inputs = _ready_inputs()
    inputs["requirement_delta_status"]["deltas"][0]["human_review_status"] = "pending_human_review"
    inputs["human_review_state"]["reviews"] = []

    packet = _packet_with(inputs)

    assert packet["status"] == "blocked"
    assert any("human_review_status is pending_human_review" in blocker for blocker in packet["blockers"])
    assert any("human review state records are missing" in blocker for blocker in packet["blockers"])


def test_public_refresh_readiness_rejects_missing_affected_process_or_guardrail_ids() -> None:
    inputs = _ready_inputs()
    delta = inputs["requirement_delta_status"]["deltas"][0]
    delta["affected_process_ids"] = []
    delta["affected_guardrail_ids"] = []

    packet = _packet_with(inputs)

    assert packet["status"] == "blocked"
    assert any("lacks affected_process_ids" in blocker for blocker in packet["blockers"])
    assert any("lacks affected_guardrail_ids" in blocker for blocker in packet["blockers"])


def test_public_refresh_readiness_rejects_ready_guardrails_without_process_version_evidence() -> None:
    inputs = _ready_inputs()
    inputs["process_model_versions"]["process_models"][0]["source_evidence_ids"] = []

    packet = _packet_with(inputs)

    assert packet["status"] == "blocked"
    assert any("lacks refreshed process-version evidence" in blocker for blocker in packet["blockers"])


def test_public_refresh_readiness_rejects_downloaded_paths_private_and_authenticated_urls() -> None:
    inputs = _ready_inputs()
    output = inputs["ingestion_outputs"]["outputs"][0]
    output["downloaded_document_path"] = "/tmp/private/download.pdf"
    output["requested_url"] = "https://user:secret@www.portland.gov/ppd/devhub-faqs"
    output["canonical_url"] = "https://devhub.portlandoregon.gov/dashboard"
    inputs["source_freshness"]["sources"][0]["canonical_url"] = "https://example.com/not-ppd"

    packet = _packet_with(inputs)
    blockers = packet["blockers"]

    assert packet["status"] == "blocked"
    assert any("downloaded document path" in blocker for blocker in blockers)
    assert any("must not include credentials" in blocker for blocker in blockers)
    assert any("appears to require authentication" in blocker for blocker in blockers)
    assert any("outside the PP&D public allowlist" in blocker for blocker in blockers)


def test_ready_inputs_fixture_remains_isolated_between_mutations() -> None:
    first = _ready_inputs()
    second = deepcopy(first)

    first["requirement_delta_status"]["deltas"][0]["source_evidence_ids"] = []

    assert second["requirement_delta_status"]["deltas"][0]["source_evidence_ids"] == ["doc-devhub-faq"]
    assert FIXTURES == Path(__file__).parent / "fixtures" / "public_refresh_readiness"
