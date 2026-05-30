from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from ppd.source_refresh_patch_plan import (
    build_public_source_refresh_patch_plan,
    validate_public_source_refresh_patch_plan_v1,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_refresh_patch_plan_v1"


def _load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _valid_plan() -> dict:
    return build_public_source_refresh_patch_plan(
        _load_fixture("approved_reviewer_disposition_ledger.json"),
        _load_fixture("public_source_refresh_reviewer_queue_v1.json"),
    )


def _codes(plan: dict) -> set[str]:
    return {issue.code for issue in validate_public_source_refresh_patch_plan_v1(plan)}


def test_builds_non_executing_patch_rows_from_approved_dispositions_only() -> None:
    disposition_ledger = _load_fixture("approved_reviewer_disposition_ledger.json")
    reviewer_queue = _load_fixture("public_source_refresh_reviewer_queue_v1.json")

    plan = build_public_source_refresh_patch_plan(disposition_ledger, reviewer_queue)

    assert validate_public_source_refresh_patch_plan_v1(plan) == []
    assert plan["plan_version"] == "public-source-refresh-patch-plan-v1"
    assert plan["execution_policy"] == {
        "recrawl": False,
        "download": False,
        "processor_execution": False,
        "raw_body_storage": False,
        "registry_mutation": False,
    }

    rows = plan["proposed_patch_rows"]
    assert [row["patch_row_id"] for row in rows] == [
        "psrpp-v1:queue-apply-permits-001:disp-001"
    ]

    row = rows[0]
    assert row["execution_mode"] == "proposal_only"
    assert row["citations"] == [
        {
            "source_id": "src-ppd-apply-permits",
            "url": "https://www.portland.gov/ppd/get-permit/apply-permits",
            "queue_item_id": "queue-apply-permits-001",
            "disposition_id": "disp-001",
        }
    ]
    assert row["source_freshness_metadata"]["source_id"] == "src-ppd-apply-permits"
    assert row["source_freshness_metadata"]["canonical_url"] == (
        "https://www.portland.gov/ppd/get-permit/apply-permits"
    )
    assert row["visible_page_review_notes"]["title"] == "Apply for permits"
    assert row["visible_page_review_notes"]["visible_date_text"] == "Last updated May 2026"
    assert row["affected_source_ids"] == ["src-ppd-apply-permits"]
    assert row["affected_requirement_ids"] == [
        "req-devhub-application-path",
        "req-unsupported-email-path-check",
    ]
    expected_rollback = {
        "checkpoint_id": "rollback:src-ppd-apply-permits:sha256:previous-apply-permits-fixture",
        "restore_source_id": "src-ppd-apply-permits",
        "restore_content_hash": "sha256:previous-apply-permits-fixture",
        "restore_freshness_status": "unchanged_before_proposed_refresh_patch",
        "registry_mutation_required": False,
    }
    assert row["rollback_checkpoint"] == expected_rollback
    assert row["rollback_checkpoints"] == [expected_rollback]
    assert row["validation_inventory"]["blocked_operations"] == plan["execution_policy"]
    assert row["validation_inventory"]["requires_human_review_before_apply"] is True


def test_requirement_impact_links_cover_affected_requirements() -> None:
    plan = _valid_plan()

    row = plan["proposed_patch_rows"][0]
    assert row["requirement_impact_links"] == [
        {
            "source_id": "src-ppd-apply-permits",
            "requirement_id": "req-devhub-application-path",
            "impact": "source_refresh_review_required",
        },
        {
            "source_id": "src-ppd-apply-permits",
            "requirement_id": "req-unsupported-email-path-check",
            "impact": "source_refresh_review_required",
        },
    ]


def test_validation_rejects_uncited_patch_rows() -> None:
    plan = _valid_plan()
    plan["proposed_patch_rows"][0]["citations"] = []

    assert "missing_citation" in _codes(plan)


def test_validation_rejects_non_allowlisted_and_authenticated_urls() -> None:
    plan = _valid_plan()
    row = plan["proposed_patch_rows"][0]
    row["source_freshness_metadata"]["canonical_url"] = "https://example.com/ppd"
    row["citations"][0]["url"] = "https://www.portland.gov/account?token=secret"

    codes = _codes(plan)
    assert "url_not_allowlisted" in codes
    assert "authenticated_url" in codes


def test_validation_rejects_raw_page_bodies_and_downloaded_documents() -> None:
    plan = _valid_plan()
    row = plan["proposed_patch_rows"][0]
    row["raw_body"] = "raw public page body must not be committed"
    row["downloaded_document"] = "apply-permits.pdf"

    codes = _codes(plan)
    assert "raw_page_body_present" in codes
    assert "downloaded_document_present" in codes


def test_validation_rejects_processor_or_archive_completion_claims() -> None:
    plan = _valid_plan()
    row = plan["proposed_patch_rows"][0]
    row["processor_complete"] = True
    row["validation_inventory"]["note"] = "Processor execution completed for this source."

    assert "processor_or_archive_completion_claim" in _codes(plan)


def test_validation_rejects_missing_affected_ids_and_rollback_checkpoints() -> None:
    plan = _valid_plan()
    row = plan["proposed_patch_rows"][0]
    row["affected_source_ids"] = []
    row["affected_requirement_ids"] = []
    row.pop("rollback_checkpoint")
    row.pop("rollback_checkpoints")

    codes = _codes(plan)
    assert "missing_affected_source_ids" in codes
    assert "missing_affected_requirement_ids" in codes
    assert "missing_rollback_checkpoints" in codes


def test_validation_rejects_legal_or_permitting_outcome_guarantees() -> None:
    plan = _valid_plan()
    plan["proposed_patch_rows"][0]["visible_page_review_notes"]["reviewer_disposition_note"] = (
        "This guarantees approval and the permit will be issued."
    )

    assert "outcome_guarantee" in _codes(plan)


def test_validation_rejects_active_mutation_flags() -> None:
    mutation_keys = [
        "active_source_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_monitoring_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    ]

    for mutation_key in mutation_keys:
        plan = _valid_plan()
        plan["proposed_patch_rows"][0][mutation_key] = True

        assert "active_mutation_flag" in _codes(plan)


def test_validation_rejects_unsafe_execution_policy_or_apply_mode() -> None:
    plan = _valid_plan()
    plan["execution_policy"]["download"] = True
    plan["proposed_patch_rows"][0]["execution_mode"] = "apply"

    codes = _codes(plan)
    assert "unsafe_execution_policy" in codes
    assert "invalid_execution_mode" in codes


def test_mutating_a_copy_does_not_affect_fixture_backed_valid_plan() -> None:
    plan = _valid_plan()
    broken = deepcopy(plan)
    broken["proposed_patch_rows"][0]["source_mutation"] = "enabled"

    assert "active_mutation_flag" in _codes(broken)
    assert validate_public_source_refresh_patch_plan_v1(plan) == []
