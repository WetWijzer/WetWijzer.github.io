from __future__ import annotations

import json
from pathlib import Path

from ppd.public_recrawl_live_dry_run_plan_v2 import build_plan, build_plan_from_fixture_paths, validate_plan


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_recrawl_live_dry_run_plan_v2"


def _load(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_build_plan_from_committed_fixtures_selects_cited_seed_batches() -> None:
    plan = build_plan_from_fixture_paths(
        FIXTURE_DIR / "live_readiness_authorization_checklist_packet_v2.json",
        FIXTURE_DIR / "public_recrawl_operator_packet_v2.json",
        FIXTURE_DIR / "source_allowlist_robots_fixtures_v2.json",
    )

    validate_plan(plan)
    assert plan["plan_id"] == "public-recrawl-live-dry-run-plan-v2"
    assert plan["attestations"] == {
        "no_live_crawl": True,
        "no_processor": True,
        "no_raw_body": True,
        "no_download": True,
        "no_source_registry_mutation": True,
    }
    assert [batch["source_id"] for batch in plan["seed_batches"]] == [
        "portland-council-agendas",
        "portland-auditor-public-notices",
    ]
    assert plan["seed_batches"][0]["rate_limit_decision"]["delay_seconds"] == 60
    assert plan["seed_batches"][1]["rate_limit_decision"]["delay_seconds"] == 45
    assert all(batch["citations"] for batch in plan["seed_batches"])
    assert all(batch["expected_capture"]["metadata_only"] is True for batch in plan["seed_batches"])
    assert "raw_body" in plan["seed_batches"][0]["expected_capture"]["excluded_fields"]
    assert {item["source_id"] for item in plan["rejected_sources"]} == {"example-disallowed-robots"}


def test_build_plan_rejects_missing_readiness_authorization() -> None:
    readiness = _load("live_readiness_authorization_checklist_packet_v2.json")
    readiness["approved_for_fixture_dry_run"] = False

    try:
        build_plan(
            readiness,
            _load("public_recrawl_operator_packet_v2.json"),
            _load("source_allowlist_robots_fixtures_v2.json"),
        )
    except ValueError as exc:
        assert "readiness" in str(exc)
    else:
        raise AssertionError("expected readiness authorization failure")


def test_validate_plan_rejects_weakened_attestations() -> None:
    plan = build_plan_from_fixture_paths(
        FIXTURE_DIR / "live_readiness_authorization_checklist_packet_v2.json",
        FIXTURE_DIR / "public_recrawl_operator_packet_v2.json",
        FIXTURE_DIR / "source_allowlist_robots_fixtures_v2.json",
    )
    plan["attestations"]["no_live_crawl"] = False

    try:
        validate_plan(plan)
    except ValueError as exc:
        assert "attestations" in str(exc)
    else:
        raise AssertionError("expected attestation validation failure")
