from pathlib import Path

from ppd.source_freshness_scheduler_v2 import (
    DEFAULT_VALIDATION_COMMANDS,
    SCHEDULE_VERSION,
    build_scheduler_packet,
    load_anchor_fixture,
)


def _fixture_path() -> Path:
    return Path(__file__).parent / "fixtures" / "ppd_source_freshness" / "anchor_set_v2.json"


def test_scheduler_packet_is_fixture_first_and_offline() -> None:
    fixture = load_anchor_fixture(_fixture_path())
    packet = build_scheduler_packet(fixture)

    assert packet["version"] == SCHEDULE_VERSION
    assert packet["mode"] == "fixture-first-offline"
    assert packet["live_crawl_performed"] is False
    assert packet["raw_bodies_stored"] is False
    assert packet["downloaded_files"] is False
    assert packet["source_registry_changed"] is False
    assert packet["offline_validation_commands"] == DEFAULT_VALIDATION_COMMANDS


def test_scheduler_packet_builds_daily_weekly_and_monthly_windows() -> None:
    fixture = load_anchor_fixture(_fixture_path())
    packet = build_scheduler_packet(fixture)
    by_id = {window["anchor_id"]: window for window in packet["recrawl_windows"]}

    assert by_id["ppd-permits-search"]["cadence"] == "daily"
    assert by_id["ppd-permits-search"]["window_start"] == "2026-05-31"
    assert by_id["ppd-permits-search"]["window_end"] == "2026-06-01"

    assert by_id["ppd-building-code-appeals"]["cadence"] == "weekly"
    assert by_id["ppd-building-code-appeals"]["window_end"] == "2026-06-07"

    assert by_id["ppd-fee-schedules"]["cadence"] == "monthly"
    assert by_id["ppd-fee-schedules"]["window_end"] == "2026-06-30"


def test_scheduler_packet_records_surfaces_holds_and_auth_skips() -> None:
    fixture = load_anchor_fixture(_fixture_path())
    packet = build_scheduler_packet(fixture)

    trigger_ids = {trigger["id"] for trigger in packet["stale_source_hold_triggers"]}
    assert "synthetic_window_elapsed_without_fixture_refresh" in trigger_ids
    assert "authenticated_or_session_bound_url" in trigger_ids

    assert "permits" in packet["affected_surface_categories"]
    assert "land-use" in packet["affected_surface_categories"]
    assert "fees" in packet["affected_surface_categories"]

    skipped = packet["skipped_authenticated_url_notes"]
    assert len(skipped) == 1
    assert skipped[0]["anchor_id"] == "devhub-private-dashboard"
    assert skipped[0]["reason"] == "authenticated_or_session_bound_url_not_crawled_offline"

    crawled_ids = {window["anchor_id"] for window in packet["recrawl_windows"]}
    assert "devhub-private-dashboard" not in crawled_ids
