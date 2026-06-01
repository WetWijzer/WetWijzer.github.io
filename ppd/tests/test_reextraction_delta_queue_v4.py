from __future__ import annotations

from pathlib import Path

from ppd.requirements.reextraction_delta_queue_v4 import assemble_delta_queue, load_fixture_packet


def test_assemble_delta_queue_from_public_freshness_fixture_v4() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "public_source_freshness_packet_v4.json"
    packet = load_fixture_packet(fixture_path)

    queue = assemble_delta_queue(packet)

    assert queue["queue_version"] == "ppd-reextraction-delta-queue-v4"
    assert queue["fixture_only"] is True
    assert queue["prohibited_actions"] == [
        "live_crawling",
        "ocr",
        "document_downloads",
        "raw_body_persistence",
        "devhub_automation",
    ]

    work_items = queue["work_items"]
    assert [item["source_id"] for item in work_items] == [
        "bds-permit-application-html",
        "commercial-permit-application-pdf",
        "intake-form-public-form",
    ]

    html_item = work_items[0]
    assert html_item["source_evidence_placeholders"]["evidence_packet_id"] == "freshness-packet-v4-fixture-001"
    assert html_item["expected_requirement_types"] == ["submittal", "fee", "inspection"]
    assert html_item["affected_process_stages"] == ["application", "plan_review", "inspection"]
    assert html_item["human_review_status"] == "required"
    assert html_item["reviewer_holds"] == ["confirm changed fee language before extraction"]

    assert queue["skipped_sources"] == [
        {"source_id": "unchanged-public-checklist", "reason": "source is unchanged and not stale"},
        {"source_id": "gis-layer", "reason": "unsupported source type"},
    ]


def test_rejects_non_v4_packet() -> None:
    packet = {"packet_version": "public-source-freshness-evidence-packet-v3", "sources": []}

    try:
        assemble_delta_queue(packet)
    except ValueError as exc:
        assert "unsupported freshness evidence packet version" in str(exc)
    else:
        raise AssertionError("expected ValueError")
