from pathlib import Path

import pytest

from ppd.extraction.public_source_change_reviewer import (
    QUEUE_VERSION,
    build_reviewer_disposition_queue,
    load_triage_packet,
    offline_validation_commands,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_change_reviewer"


def test_builds_ordered_reviewer_disposition_queue_from_fixture() -> None:
    packet = load_triage_packet(FIXTURE_DIR / "triage_packet_v1.json")

    queue = build_reviewer_disposition_queue(packet)

    assert queue["queue_version"] == QUEUE_VERSION
    assert queue["source"] == "fixture_only"
    assert queue["no_live_crawling"] is True
    assert queue["no_raw_body_persistence"] is True
    assert queue["official_action_claim"] is False
    assert [row["change_id"] for row in queue["decision_rows"]] == [
        "chg-devhub-faq-upload-corrections",
        "chg-file-standards-needs-review",
        "chg-forms-index-no-change",
    ]
    assert queue["buckets"] == {
        "changed": ["chg-devhub-faq-upload-corrections"],
        "unchanged": ["chg-forms-index-no-change"],
        "needs_review": ["chg-file-standards-needs-review"],
    }
    assert queue["blocked_promotion_reasons"] == []
    assert queue["rollback_checkpoints"][0] == {
        "checkpoint_id": "rollback:fixture-public-change-triage-001:queue",
        "restore_target": "discard generated reviewer queue artifact",
        "release_state_change": False,
    }
    assert offline_validation_commands() == queue["validation_commands"]


def test_blocks_raw_content_and_uncited_changed_rows() -> None:
    packet = load_triage_packet(FIXTURE_DIR / "triage_packet_v1.json")
    packet["changes"] = [
        {
            "change_id": "chg-bad",
            "source_id": "src-bad",
            "canonical_url": "https://www.portland.gov/ppd/example",
            "triage_status": "changed",
            "review_priority": 1,
            "summary": "Bad fixture intentionally includes raw body content.",
            "raw_body": "raw public page text must not be carried into this queue",
            "impact_references": [],
        }
    ]

    queue = build_reviewer_disposition_queue(packet)
    row = queue["decision_rows"][0]

    assert row["reviewer_decision"] == "blocked_needs_human_review"
    assert "raw_or_downloaded_content_present:raw_body" in row["blocked_promotion_reasons"]
    assert "changed_source_without_cited_impact_reference" in row["blocked_promotion_reasons"]
    assert "packet_contains_raw_or_downloaded_content" in queue["blocked_promotion_reasons"]


def test_rejects_wrong_packet_version() -> None:
    with pytest.raises(ValueError, match="packet_version"):
        build_reviewer_disposition_queue(
            {
                "packet_version": "public_source_change_triage_packet_v0",
                "packet_id": "bad-version",
                "changes": [],
            }
        )
