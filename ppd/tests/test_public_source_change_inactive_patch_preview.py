from copy import deepcopy
from pathlib import Path

import pytest

from ppd.extraction.public_source_change_inactive_patch_preview import (
    PREVIEW_VERSION,
    PublicSourceChangeInactivePatchPreviewError,
    assert_valid_public_source_change_inactive_patch_preview_v1,
    build_public_source_change_inactive_patch_preview_v1,
    load_reviewer_disposition_queue,
    validate_public_source_change_inactive_patch_preview_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_change_inactive_patch_preview"


def _valid_preview() -> dict:
    queue = load_reviewer_disposition_queue(FIXTURE_DIR / "reviewer_queue_v1.json")
    return build_public_source_change_inactive_patch_preview_v1(queue)


def test_builds_inactive_file_scoped_before_after_preview_from_queue_fixture() -> None:
    queue = load_reviewer_disposition_queue(FIXTURE_DIR / "reviewer_queue_v1.json")

    preview = build_public_source_change_inactive_patch_preview_v1(queue)

    assert preview["preview_version"] == PREVIEW_VERSION
    assert preview["fixture_scope"] == "inactive_public_source_fixtures_only"
    assert preview["applies_fixture_changes"] is False
    assert preview["active_public_source_artifact_mutation"] is False
    assert preview["live_source_crawl"] is False
    assert preview["downloaded_documents"] is False
    assert preview["prompt_changes"] is False
    assert preview["release_state_updates"] is False
    assert [row["source_id"] for row in preview["file_scoped_previews"]] == [
        "ppd-devhub-faq",
        "ppd-submit-plans-online",
        "ppd-file-naming-standards",
    ]
    assert all("/inactive/" in row["inactive_fixture_path"] for row in preview["file_scoped_previews"])
    assert all(row["before"]["fixture_state"] == "inactive" for row in preview["file_scoped_previews"])
    assert all(row["after"]["fixture_state"] == "inactive" for row in preview["file_scoped_previews"])
    assert all(row["after"]["preview_only"] is True for row in preview["file_scoped_previews"])
    assert all(check["status"] == "pass" for check in preview["citation_preservation_checks"])
    assert preview["unchanged_row_inventory"] == [
        {
            "row_id": "inactive-preview:ppd-submit-plans-online",
            "source_id": "ppd-submit-plans-online",
            "reason": "Reviewer disposition is unchanged; preview records no fixture content change.",
        }
    ]
    assert preview["blocked_row_explanations"] == [
        {
            "row_id": "inactive-preview:ppd-file-naming-standards",
            "source_id": "ppd-file-naming-standards",
            "explanation": "Human review is required before promotion because the changed guidance may affect file-rule extraction.",
        }
    ]
    assert preview["reviewer_signoff_placeholders"][0]["decision"] == "pending_manual_review"
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in preview["validation_replay_commands"]
    assert_valid_public_source_change_inactive_patch_preview_v1(preview)


def test_blocks_uncited_preview_rows() -> None:
    queue = load_reviewer_disposition_queue(FIXTURE_DIR / "reviewer_queue_v1.json")
    queue["reviewer_decision_rows"][0]["impact_references"] = []

    with pytest.raises(PublicSourceChangeInactivePatchPreviewError, match="preserve citations"):
        build_public_source_change_inactive_patch_preview_v1(queue)


def test_validator_rejects_missing_before_or_after_inactive_fixture_previews() -> None:
    preview = _valid_preview()
    del preview["file_scoped_previews"][0]["before"]
    preview["file_scoped_previews"][1]["after"]["fixture_state"] = "active"
    preview["file_scoped_previews"][2]["after"]["preview_only"] = False

    errors = validate_public_source_change_inactive_patch_preview_v1(preview)

    assert any("must include before and after objects" in error for error in errors)
    assert "file_scoped_previews[1].after.fixture_state must be inactive" in errors
    assert "file_scoped_previews[2].after.preview_only must be true" in errors


def test_validator_rejects_missing_citation_checks_and_uncited_changed_rows() -> None:
    preview = _valid_preview()
    preview["citation_preservation_checks"] = []
    changed_row = preview["file_scoped_previews"][0]
    changed_row["impact_references"] = []
    changed_row["citation_preserved"] = False

    errors = validate_public_source_change_inactive_patch_preview_v1(preview)

    assert "citation_preservation_checks must include one check per preview row" in errors
    assert "file_scoped_previews[0] changed rows must preserve citations" in errors
    assert "file_scoped_previews[0] must preserve citations" in errors


def test_validator_rejects_missing_unchanged_inventory_and_blocked_explanations() -> None:
    preview = _valid_preview()
    preview["unchanged_row_inventory"] = []
    preview["blocked_row_explanations"] = []

    errors = validate_public_source_change_inactive_patch_preview_v1(preview)

    assert "unchanged_row_inventory missing unchanged row inactive-preview:ppd-submit-plans-online" in errors
    assert "blocked_row_explanations missing blocked row inactive-preview:ppd-file-naming-standards" in errors


def test_validator_rejects_missing_signoffs_rollback_notes_and_validation_commands() -> None:
    preview = _valid_preview()
    preview["reviewer_signoff_placeholders"] = []
    preview["rollback_notes"] = []
    preview["validation_replay_commands"] = []

    errors = validate_public_source_change_inactive_patch_preview_v1(preview)

    assert "reviewer_signoff_placeholders missing row inactive-preview:ppd-devhub-faq" in errors
    assert "rollback_notes must contain rollback notes" in errors
    assert "validation_replay_commands must contain command arrays" in errors


def test_validator_rejects_active_mutation_flags_and_live_claims() -> None:
    preview = _valid_preview()
    preview["mutation_flags"]["active_fixture_mutation"] = True
    preview["rollback_notes"].append("live crawl refresh complete")

    errors = validate_public_source_change_inactive_patch_preview_v1(preview)

    assert "mutation_flags.active_fixture_mutation must be false" in errors
    assert any("forbidden claim" in error for error in errors)


def test_validator_rejects_private_raw_downloaded_and_browser_artifacts() -> None:
    preview = _valid_preview()
    preview["auth_state"] = {"token": "redacted"}
    preview["file_scoped_previews"][0]["raw_pdf"] = "bytes"
    preview["file_scoped_previews"][1]["downloaded_document"] = "document.pdf"
    preview["file_scoped_previews"][2]["browser_artifact"] = "trace.zip"

    errors = validate_public_source_change_inactive_patch_preview_v1(preview)

    assert any("$.auth_state must not include private" in error for error in errors)
    assert any("raw_pdf must not include private" in error for error in errors)
    assert any("downloaded_document must not include private" in error for error in errors)
    assert any("browser_artifact must not include private" in error for error in errors)


def test_validator_rejects_outcome_guarantees_consequential_language_and_applied_promotion_claims() -> None:
    preview = _valid_preview()
    preview["file_scoped_previews"][0]["blocked_explanation"] = "Permit will be approved after applied promotion."
    preview["reviewer_signoff_placeholders"][0]["decision"] = "submit application"

    errors = validate_public_source_change_inactive_patch_preview_v1(preview)

    assert any("permit will be approved" in error for error in errors)
    assert any("applied promotion" in error for error in errors)
    assert any("submit application" in error for error in errors)


def test_validator_rejects_mutation_flags_outside_inactive_public_source_fixture_scope() -> None:
    preview = _valid_preview()
    preview["mutation_flags"]["active_surface_mutation"] = True
    preview["file_scoped_previews"][0]["active_guardrail_mutation"] = True
    preview["file_scoped_previews"][1]["update_active_registry"] = "enabled"

    errors = validate_public_source_change_inactive_patch_preview_v1(preview)

    assert "mutation_flags.active_surface_mutation is outside inactive public-source fixture preview scope" in errors
    assert any("active_guardrail_mutation must not enable mutation" in error for error in errors)
    assert any("update_active_registry must not enable mutation" in error for error in errors)


def test_rejects_wrong_queue_version() -> None:
    with pytest.raises(ValueError, match="queue version"):
        build_public_source_change_inactive_patch_preview_v1(
            {
                "version": "public_source_change_reviewer_disposition_queue_v0",
                "reviewer_decision_rows": [],
            }
        )


def test_valid_preview_copy_remains_accepted() -> None:
    preview = deepcopy(_valid_preview())

    assert validate_public_source_change_inactive_patch_preview_v1(preview) == []
