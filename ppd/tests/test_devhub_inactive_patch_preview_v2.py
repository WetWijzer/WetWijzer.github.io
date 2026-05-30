from __future__ import annotations

import json
from pathlib import Path

from ppd.devhub_inactive_patch_preview_v2 import build_preview_v2

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub_inactive_patch_preview_v2"


def _load(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_build_preview_v2_matches_expected_fixture() -> None:
    actual = build_preview_v2(
        _load("observed_surface_update_plan_v2.json"),
        _load("attended_observation_handoff_checklist_v1.json"),
        _load("inactive_devhub_surface_fixtures.json"),
    )

    assert actual == _load("expected_preview_v2.json")


def test_preview_rows_are_read_only_and_deterministic() -> None:
    preview = build_preview_v2(
        _load("observed_surface_update_plan_v2.json"),
        _load("attended_observation_handoff_checklist_v1.json"),
        _load("inactive_devhub_surface_fixtures.json"),
    )

    row_ids = [row["row_id"] for row in preview["rows"]]
    assert row_ids == sorted(row_ids)
    assert all(row["read_only"] is True for row in preview["rows"])
    assert any(row["status"] == "blocked" for row in preview["rows"])
