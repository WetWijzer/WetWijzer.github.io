import json
from pathlib import Path

import pytest

from ppd.inactive_fixture_promotion_diff_ledger import (
    build_inactive_fixture_promotion_diff_ledger,
    ledger_to_json,
    load_json,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "inactive_fixture_promotion_diff_ledger"


def test_builds_expected_inactive_fixture_promotion_diff_ledger_v1() -> None:
    decision_packet = load_json(FIXTURE_DIR / "release_promotion_decision_packet_v1.json")
    patch_preview = load_json(FIXTURE_DIR / "inactive_promotion_patch_preview_v1.json")
    expected = load_json(FIXTURE_DIR / "expected_inactive_fixture_promotion_diff_ledger_v1.json")

    actual = build_inactive_fixture_promotion_diff_ledger(decision_packet, patch_preview)

    assert actual == expected
    assert json.loads(ledger_to_json(actual)) == expected


def test_rejects_unknown_decision_packet_version() -> None:
    decision_packet = load_json(FIXTURE_DIR / "release_promotion_decision_packet_v1.json")
    patch_preview = load_json(FIXTURE_DIR / "inactive_promotion_patch_preview_v1.json")
    decision_packet["packet_version"] = "release_promotion_decision_packet_v0"

    with pytest.raises(ValueError, match="unsupported decision packet version"):
        build_inactive_fixture_promotion_diff_ledger(decision_packet, patch_preview)


def test_readiness_blocks_missing_validations_without_active_fixture_state() -> None:
    decision_packet = load_json(FIXTURE_DIR / "release_promotion_decision_packet_v1.json")
    patch_preview = load_json(FIXTURE_DIR / "inactive_promotion_patch_preview_v1.json")
    decision_packet["fixture_families"][0]["passed_validations"] = []

    ledger = build_inactive_fixture_promotion_diff_ledger(decision_packet, patch_preview)
    readiness = {
        row["fixture_family"]: row for row in ledger["fixture_family_readiness_rows"]
    }

    assert readiness["devhub-standard-trade-permit"]["readiness"] == "blocked"
    assert "json_schema" in readiness["devhub-standard-trade-permit"]["missing_validations"]
    assert ledger["safety_notes"] == [
        "Ledger is derived from inactive fixture decision and preview packets only.",
        "No active fixtures, release state, authenticated artifacts, or raw crawl outputs are modified.",
    ]
