from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.public_refresh.observation_plan_v2 import (
    EXACT_OFFLINE_VALIDATION_COMMANDS,
    OFFICIAL_PPD_ANCHORS,
    build_public_refresh_observation_plan_v2,
    require_public_refresh_observation_plan_v2,
    validate_public_refresh_observation_plan_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_refresh"


def _load_json(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _valid_plan() -> dict:
    return build_public_refresh_observation_plan_v2(_load_json("expected_public_refresh_readiness_packet_v2.json"))


def _problem_text(packet: dict) -> str:
    result = validate_public_refresh_observation_plan_v2(packet)
    assert not result.valid
    return "; ".join(result.errors)


def test_build_public_refresh_observation_plan_v2_matches_fixture() -> None:
    readiness = _load_json("expected_public_refresh_readiness_packet_v2.json")
    expected = _load_json("expected_public_refresh_observation_plan_v2.json")

    assert build_public_refresh_observation_plan_v2(readiness) == expected


def test_public_refresh_observation_plan_v2_has_one_ordered_row_per_official_anchor() -> None:
    plan = _valid_plan()
    rows = plan["ordered_public_refresh_observation_rows"]

    assert [row["order"] for row in rows] == list(range(1, len(OFFICIAL_PPD_ANCHORS) + 1))
    assert [row["official_anchor_url"] for row in rows] == [anchor["url"] for anchor in OFFICIAL_PPD_ANCHORS]
    assert all(row["canonical_url_placeholder"].startswith("placeholder_") for row in rows)
    assert all("placeholder" in row["allowlist_decision_placeholder"] for row in rows)
    assert all("placeholder" in row["robots_decision_placeholder"] for row in rows)
    require_public_refresh_observation_plan_v2(plan)


def test_public_refresh_observation_plan_v2_is_offline_non_persistent_and_non_mutating() -> None:
    plan = _valid_plan()

    assert plan["network_access"] == "not_requested"
    assert plan["document_downloads"] == "not_allowed"
    assert plan["devhub_scope"] == "not_touched"
    assert plan["crawl_output_storage"] == "not_allowed"
    assert plan["raw_body_persistence"] == "not_allowed"
    assert plan["active_source_registry_changes"] == "not_allowed"
    assert plan["exact_offline_validation_commands"] == EXACT_OFFLINE_VALIDATION_COMMANDS
    assert all(row["network_request_performed"] is False for row in plan["ordered_public_refresh_observation_rows"])
    assert all(row["document_download_performed"] is False for row in plan["ordered_public_refresh_observation_rows"])
    assert all(row["raw_body_persisted"] is False for row in plan["ordered_public_refresh_observation_rows"])
    assert all(row["crawl_output_stored"] is False for row in plan["ordered_public_refresh_observation_rows"])
    assert all(row["active_registry_mutated"] is False for row in plan["ordered_public_refresh_observation_rows"])


def test_public_refresh_observation_plan_v2_rejects_modified_validation_commands() -> None:
    plan = _valid_plan()
    plan["exact_offline_validation_commands"].append(["python3", "ppd/crawler/live_public_scrape.py"])

    assert "exact_offline_validation_commands must match" in _problem_text(plan)


def test_public_refresh_observation_plan_v2_rejects_missing_anchor_row() -> None:
    plan = _valid_plan()
    plan["ordered_public_refresh_observation_rows"] = plan["ordered_public_refresh_observation_rows"][:-1]

    assert "must cover every official PP&D anchor" in _problem_text(plan)


def test_public_refresh_observation_plan_v2_rejects_reordered_anchor_rows() -> None:
    plan = _valid_plan()
    rows = plan["ordered_public_refresh_observation_rows"]
    rows[0], rows[1] = rows[1], rows[0]

    problems = _problem_text(plan)

    assert "must be contiguous and ordered" in problems
    assert "must preserve the official PP&D anchor order" in problems


def test_public_refresh_observation_plan_v2_rejects_missing_freshness_signal_fields() -> None:
    plan = _valid_plan()
    plan["ordered_public_refresh_observation_rows"][0]["expected_freshness_signal_placeholders"]["expected_signal_fields"] = ["content_hash"]

    problems = _problem_text(plan)

    assert "expected_signal_fields missing" in problems
    assert "affected_guardrail_bundle_ids" in problems


def test_public_refresh_observation_plan_v2_rejects_missing_no_raw_body_attestation_ref() -> None:
    plan = _valid_plan()
    plan["ordered_public_refresh_observation_rows"][0]["no_raw_body_persistence_attestation_ids"] = ["no_raw_public_body_commits"]

    assert "metadata_only_fixture_scope" in _problem_text(plan)


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("session_state", "storage-state.json", "private, browser, raw, download, session, or crawl-output artifacts"),
        ("browser_trace", "trace.zip", "private, browser, raw, download, session, or crawl-output artifacts"),
        ("raw_response_body", "raw response body", "private, browser, raw, download, session, or crawl-output artifacts"),
        ("downloaded_document_path", "/downloads/permit.pdf", "private, browser, raw, download, session, or crawl-output artifacts"),
        ("live_claim", "live crawl captured the page", "live crawl or network execution"),
        ("official_action_claim", "submit permit application", "consequential official action language"),
        ("guarantee_claim", "permit will issue", "legal or permitting outcomes"),
        ("network_request_performed", True, "must be false"),
        ("document_download_performed", True, "must be false"),
        ("raw_body_persisted", True, "must be false"),
        ("crawl_output_stored", True, "must be false"),
        ("active_registry_mutated", True, "must be false"),
    ],
)
def test_public_refresh_observation_plan_v2_rejects_unsafe_values(field: str, value: object, expected: str) -> None:
    plan = _valid_plan()
    plan["ordered_public_refresh_observation_rows"][0][field] = value

    assert expected in _problem_text(plan)


def test_public_refresh_observation_plan_v2_validation_does_not_mutate_input() -> None:
    plan = _valid_plan()
    before = copy.deepcopy(plan)

    assert validate_public_refresh_observation_plan_v2(plan).valid
    assert plan == before
