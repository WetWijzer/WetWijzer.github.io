import json
from pathlib import Path

from ppd.source_freshness_delta import build_source_freshness_delta_review_packet


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source_freshness_delta"


def _load(name: str):
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_build_source_freshness_delta_review_packet_from_fixtures():
    packet = build_source_freshness_delta_review_packet(
        _load("public_source_refresh_metadata_intake.json"),
        _load("evidence_freshness_watchlist_reviewer_disposition.json"),
        _load("source_registry_schedule_update_candidate.json"),
    )

    assert packet == _load("expected_source_freshness_delta_review_packet.json")


def test_attestations_prohibit_live_or_mutating_work():
    packet = build_source_freshness_delta_review_packet(
        _load("public_source_refresh_metadata_intake.json"),
        _load("evidence_freshness_watchlist_reviewer_disposition.json"),
        _load("source_registry_schedule_update_candidate.json"),
    )

    assert packet["attestations"] == {
        "no_fetch_performed": True,
        "no_processor_invoked": True,
        "no_registry_mutation": True,
        "no_requirement_mutation": True,
        "no_guardrail_mutation": True,
    }
    assert packet["affected_source_ids"] == [
        "ppd-devhub-faq",
        "ppd-submit-plans-online",
    ]
