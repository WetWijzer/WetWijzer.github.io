from pathlib import Path

from ppd.extraction.public_source_freshness_watch_plan_v3 import (
    REQUIRED_ATTESTATIONS,
    build_watch_plan_from_paths,
    validate_watch_plan,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_freshness_watch_plan_v3"


def test_build_watch_plan_v3_from_committed_fixtures():
    plan = build_watch_plan_from_paths(
        FIXTURE_DIR / "public_source_observation_refresh_candidate_v2.json",
        FIXTURE_DIR / "inactive_source_fixture_migration_packet_v2.json",
        FIXTURE_DIR / "guardrail_regression_replay_matrix_v3.json",
    )

    validate_watch_plan(plan)
    assert plan["plan_version"] == "public_source_freshness_watch_plan_v3"
    assert len(plan["watch_rows"]) == 3
    assert plan["attestations"] == REQUIRED_ATTESTATIONS


def test_high_priority_row_carries_citations_requirements_guardrails_and_offline_commands():
    plan = build_watch_plan_from_paths(
        FIXTURE_DIR / "public_source_observation_refresh_candidate_v2.json",
        FIXTURE_DIR / "inactive_source_fixture_migration_packet_v2.json",
        FIXTURE_DIR / "guardrail_regression_replay_matrix_v3.json",
    )
    row = next(item for item in plan["watch_rows"] if item["source_id"] == "ppd-devhub-submit-guide")

    assert row["recrawl_priority"] == "high"
    assert row["citation_ids"] == ["cite-devhub-submit-application-guide"]
    assert row["affected_requirement_ids"] == ["REQ-DEVHUB-APPLICATION-DRAFT", "REQ-DEVHUB-UPLOAD-STAGING"]
    assert row["affected_guardrail_ids"] == ["GR-ACTION-SUBMISSION-GATE", "GR-UPLOAD-ATTENDED-CONFIRMATION"]
    assert row["reviewer_owner"] == ["devhub-guardrail-reviewer", "public-source-reviewer"]
    assert ["python3", "-m", "py_compile", "ppd/extraction/public_source_freshness_watch_plan_v3.py"] in row["offline_validation_commands"]
    assert row["attestations"] == REQUIRED_ATTESTATIONS


def test_inactive_source_row_is_deferred_and_never_authorizes_live_activity():
    plan = build_watch_plan_from_paths(
        FIXTURE_DIR / "public_source_observation_refresh_candidate_v2.json",
        FIXTURE_DIR / "inactive_source_fixture_migration_packet_v2.json",
        FIXTURE_DIR / "guardrail_regression_replay_matrix_v3.json",
    )
    row = next(item for item in plan["watch_rows"] if item["source_id"] == "ppd-legacy-fee-handout")

    assert row["recrawl_priority"] == "defer"
    assert row["skip_defer_reason"] == "inactive legacy handout replaced by current fee payment guide"
    assert "do not recrawl inactive source" in row["metadata_only_watch_expectations"]
    assert row["affected_requirement_ids"] == ["REQ-FEE-PAYMENT-GATE"]
    assert row["affected_guardrail_ids"] == ["GR-PAYMENT-EXACT-CONFIRMATION"]
    assert row["attestations"] == REQUIRED_ATTESTATIONS
