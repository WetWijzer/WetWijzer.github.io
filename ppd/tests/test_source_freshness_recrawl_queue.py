import json
from pathlib import Path

from ppd.source_freshness_recrawl_queue import build_recrawl_queue_from_files


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source_freshness_recrawl_queue"


def test_build_recrawl_queue_from_fixtures_matches_expected_rows():
    queue = build_recrawl_queue_from_files(
        FIXTURE_DIR / "official_source_anchors.json",
        FIXTURE_DIR / "freshness_monitor_fixtures.json",
    )
    expected = json.loads((FIXTURE_DIR / "expected_queue.json").read_text(encoding="utf-8"))

    assert queue == expected


def test_queue_is_fixture_first_and_does_not_store_crawl_outputs():
    queue = build_recrawl_queue_from_files(
        FIXTURE_DIR / "official_source_anchors.json",
        FIXTURE_DIR / "freshness_monitor_fixtures.json",
    )

    assert [row["anchor_id"] for row in queue] == [
        "pcc-title-33",
        "trn-admin-rule-streets",
        "bds-fee-schedule",
    ]
    assert all(row["robots_policy_preflight"]["status"] == "not_run_fixture_only" for row in queue)
    assert all(row["processor_handoff_dry_run"]["status"] == "not_submitted" for row in queue)
    assert all(row["reviewer_approval"]["status"] == "pending" for row in queue)
    assert all(row["evidence_placeholders"]["raw_response_body_stored"] is False for row in queue)
    assert all(row["evidence_placeholders"]["downloaded_document_stored"] is False for row in queue)
