from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.crawler.processor_handoff_manifest_plan_v1 import (
    build_dry_run_manifest_plan,
    build_dry_run_manifest_plan_from_files,
    load_json,
    validate_dry_run_manifest_plan,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "processor_handoff_manifest_plan_v1"


def build_fixture_plan() -> dict[str, object]:
    return build_dry_run_manifest_plan_from_files(
        FIXTURE_DIR / "public_crawl_frontier_expansion_plan_v1.fixture.json",
        FIXTURE_DIR / "processor_suite_policy.fixture.json",
    )


def assert_invalid_plan(plan: dict[str, object], expected_message: str) -> None:
    with pytest.raises(ValueError, match=expected_message):
        validate_dry_run_manifest_plan(plan)


def test_fixture_first_processor_handoff_manifest_plan_matches_expected_rows() -> None:
    actual = build_fixture_plan()
    expected = load_json(FIXTURE_DIR / "expected_archive_manifest_plan_v1.json")

    assert actual == expected


def test_allowed_public_html_and_pdf_rows_are_processor_ready_without_raw_body_persistence() -> None:
    actual = build_fixture_plan()

    allowed_rows = [row for row in actual["archive_manifest_rows"] if row["skipped_reason"] is None]
    assert [row["content_type"] for row in allowed_rows] == ["text/html", "application/pdf"]

    for row in allowed_rows:
        assert row["source_evidence_ids"]
        assert row["requested_url"].startswith("https://www.portland.gov/ppd/")
        assert row["canonical_url"].startswith("https://www.portland.gov/ppd/")
        assert row["processor_name"].startswith("ipfs-datasets-")
        assert row["processor_version"] == "placeholder-version"
        assert row["archive_artifact_ref"] is None
        assert row["normalized_document_id"].startswith("normalized-document:placeholder:v1:")
        assert row["no_raw_body_persisted"] is True


def test_skipped_rows_record_reasons_and_do_not_claim_normalized_documents() -> None:
    actual = build_fixture_plan()

    skipped_reasons = {
        row["source_id"]: row["skipped_reason"]
        for row in actual["archive_manifest_rows"]
        if row["skipped_reason"] is not None
    }

    assert skipped_reasons == {
        "ppd-skipped-private-devhub": "private_authenticated",
        "ppd-skipped-outside-allowlist": "outside_allowlist",
        "ppd-skipped-unsupported-content-type": "unsupported_content_type",
    }

    for row in actual["archive_manifest_rows"]:
        if row["skipped_reason"] is not None:
            assert row["source_evidence_ids"]
            assert row["processor_name"] == "no-processor-dry-run-skip"
            assert row["processor_version"] == "not-applicable"
            assert row["archive_artifact_ref"] is None
            assert row["normalized_document_id"] is None
            assert row["no_raw_body_persisted"] is True


def test_plan_attests_offline_dry_run_boundaries_and_validation_commands() -> None:
    actual = build_fixture_plan()

    assert actual["attestations"] == {
        "fixture_first": True,
        "network_fetch_performed": False,
        "ipfs_datasets_py_invoked": False,
        "archive_artifacts_written": False,
        "no_raw_body_persisted": True,
    }
    assert actual["rollback_note"]
    assert actual["offline_validation_commands"] == [
        ["python3", "-m", "py_compile", "ppd/crawler/processor_handoff_manifest_plan_v1.py"],
        ["python3", "-m", "pytest", "ppd/tests/test_processor_handoff_manifest_plan_v1.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def test_build_rejects_uncited_manifest_candidates() -> None:
    frontier = load_json(FIXTURE_DIR / "public_crawl_frontier_expansion_plan_v1.fixture.json")
    policy = load_json(FIXTURE_DIR / "processor_suite_policy.fixture.json")
    frontier["candidates"][0].pop("source_evidence_ids")

    with pytest.raises(ValueError, match="source_evidence_ids"):
        build_dry_run_manifest_plan(frontier, policy)


def test_build_rejects_missing_requested_or_canonical_url_pairs() -> None:
    frontier = load_json(FIXTURE_DIR / "public_crawl_frontier_expansion_plan_v1.fixture.json")
    policy = load_json(FIXTURE_DIR / "processor_suite_policy.fixture.json")
    frontier["candidates"][0].pop("canonical_url")

    with pytest.raises(ValueError, match="canonical_url"):
        build_dry_run_manifest_plan(frontier, policy)


def test_build_rejects_missing_processor_policy_fields() -> None:
    frontier = load_json(FIXTURE_DIR / "public_crawl_frontier_expansion_plan_v1.fixture.json")
    policy = load_json(FIXTURE_DIR / "processor_suite_policy.fixture.json")
    policy["content_type_processors"]["text/html"].pop("processor_version")

    with pytest.raises(ValueError, match="processor_version"):
        build_dry_run_manifest_plan(frontier, policy)


def test_build_rejects_missing_skipped_reason_for_skipped_manifest_rows() -> None:
    plan = build_fixture_plan()
    plan["archive_manifest_rows"][2]["skipped_reason"] = None
    plan["archive_manifest_rows"][2]["normalized_document_id"] = None

    assert_invalid_plan(plan, "processor-ready row missing normalized_document_id")


def test_validation_rejects_raw_archive_body_and_pdf_artifacts() -> None:
    plan = build_fixture_plan()
    plan["archive_manifest_rows"][0]["archive_artifact_ref"] = "warc://raw-output"
    plan["archive_manifest_rows"][0]["raw_body_path"] = "raw/page.html"
    plan["archive_manifest_rows"][1]["pdf_artifact_ref"] = "raw/form.pdf"

    assert_invalid_plan(plan, "raw, private, session, browser, or PDF artifact data")


def test_validation_rejects_live_processor_execution_or_promotion_claims() -> None:
    plan = build_fixture_plan()
    plan["attestations"]["ipfs_datasets_py_invoked"] = True
    plan["processor_executed"] = True
    plan["promotion_ready"] = True

    assert_invalid_plan(plan, "live processor execution or promotion")


def test_validation_rejects_private_authenticated_session_or_browser_artifacts() -> None:
    plan = build_fixture_plan()
    plan["archive_manifest_rows"][0]["session_state"] = "state.json"
    plan["archive_manifest_rows"][0]["screenshot_path"] = "trace.png"
    plan["archive_manifest_rows"][0]["auth_state"] = {"token": "redacted"}

    assert_invalid_plan(plan, "raw, private, session, browser, or PDF artifact data")


def test_validation_rejects_legal_or_permitting_outcome_guarantees() -> None:
    plan = build_fixture_plan()
    plan["archive_manifest_rows"][0]["operator_note"] = "Permit will be issued after this dry-run."

    assert_invalid_plan(plan, "legal or permitting outcome guarantee")


def test_validation_rejects_active_archive_source_document_requirement_guardrail_release_or_agent_mutation_flags() -> None:
    for flag in (
        "active_archive_mutation",
        "active_source_mutation",
        "active_document_mutation",
        "active_requirement_mutation",
        "active_guardrail_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    ):
        plan = build_fixture_plan()
        plan[flag] = True
        assert_invalid_plan(plan, "active mutation")


def test_validation_accepts_clean_fixture_plan_after_deepcopy() -> None:
    plan = deepcopy(build_fixture_plan())

    validate_dry_run_manifest_plan(plan)
