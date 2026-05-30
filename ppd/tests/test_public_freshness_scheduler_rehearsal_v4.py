from __future__ import annotations

import json
from pathlib import Path

from ppd.public_freshness_scheduler_rehearsal_v4 import ATTESTATIONS, build_rehearsal, load_json

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_freshness_scheduler_rehearsal_v4"


def test_build_rehearsal_from_public_fixtures() -> None:
    result = build_rehearsal(
        load_json(FIXTURE_DIR / "public_source_freshness_watch_plan_v3.json"),
        load_json(FIXTURE_DIR / "public_source_registry_promotion_preview_v3.json"),
        load_json(FIXTURE_DIR / "source_registry_fixtures.json"),
    )

    assert result["schema"] == "ppd.public_freshness_scheduler_rehearsal.v4"
    assert result["attestations"] == ATTESTATIONS

    candidates = result["cited_metadata_only_recrawl_schedule_candidates"]
    assert [candidate["source_id"] for candidate in candidates] == ["portland-zoning-code"]
    assert candidates[0]["cadence"] == "P7D"
    assert candidates[0]["metadata_fields"]["public_url"] == "https://www.portland.gov/code/33"
    assert candidates[0]["citations"]
    assert candidates[0]["attestations"]["no_live_crawl"] is True
    assert candidates[0]["attestations"]["no_raw_body"] is True

    skips = result["skip_defer_reasons"]
    assert [skip["source_id"] for skip in skips] == ["portland-archived-fee-schedule", "portland-building-code"]
    reasons = {skip["source_id"]: skip["reason"] for skip in skips}
    assert reasons["portland-building-code"] == "awaiting reviewer confirmation of registry promotion preview"
    assert reasons["portland-archived-fee-schedule"] == "missing promotion preview"

    assert [item["source_id"] for item in result["dependency_order"]] == [
        "portland-zoning-code",
        "portland-archived-fee-schedule",
        "portland-building-code",
    ]
    assert all(owner["review_required"] is True for owner in result["reviewer_owner_fields"])
    assert all(checkpoint["mutation_allowed"] is False for checkpoint in result["rollback_checkpoints"])


def test_result_is_json_serializable() -> None:
    result = build_rehearsal(
        load_json(FIXTURE_DIR / "public_source_freshness_watch_plan_v3.json"),
        load_json(FIXTURE_DIR / "public_source_registry_promotion_preview_v3.json"),
        load_json(FIXTURE_DIR / "source_registry_fixtures.json"),
    )
    encoded = json.dumps(result, sort_keys=True)
    assert "raw_body" not in encoded
    assert "downloaded_document" not in encoded
