from __future__ import annotations

import pytest

from ppd.extraction.public_source_recrawl_inactive_patch_preview import (
    PublicSourceRecrawlInactivePatchPreviewError,
    iter_public_source_recrawl_inactive_patch_preview_v1_issues,
    validate_public_source_recrawl_inactive_patch_preview_v1,
)


def valid_preview() -> dict[str, object]:
    return {
        "preview_version": "public_source_recrawl_inactive_patch_preview_v1",
        "inactive_patch_preview_rows": [
            {
                "source_id": "ppd-devhub-faq",
                "canonical_url": "https://www.portland.gov/ppd/devhub-faqs",
                "disposition": "inactive_patch_preview",
                "reason": "deterministic fixture preview only",
            }
        ],
        "delta_placeholders": {
            "source_registry_delta": {"placeholder": True, "rows": []},
            "archive_manifest_delta": {"placeholder": True, "rows": []},
            "normalized_document_reference_delta": {"placeholder": True, "rows": []},
        },
        "freshness_monitor_replay_notes": [
            "Replay would compare prior fixture hashes only; no network access is performed."
        ],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "mutates_active_artifacts": False,
        "mutates_prompts": False,
    }


def issue_codes(payload: dict[str, object]) -> set[str]:
    return {
        issue.code
        for issue in iter_public_source_recrawl_inactive_patch_preview_v1_issues(payload)
    }


def test_valid_preview_is_accepted() -> None:
    validate_public_source_recrawl_inactive_patch_preview_v1(valid_preview())


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (
            lambda payload: payload.update(
                {
                    "inactive_patch_preview_rows": [
                        {"source_id": "x", "disposition": "apply_now"}
                    ]
                }
            ),
            "unapproved_disposition",
        ),
        (
            lambda payload: payload.pop("inactive_patch_preview_rows"),
            "missing_inactive_patch_preview_rows",
        ),
        (
            lambda payload: payload["delta_placeholders"].pop("source_registry_delta"),
            "missing_source_registry_delta",
        ),
        (
            lambda payload: payload["delta_placeholders"].pop("archive_manifest_delta"),
            "missing_archive_manifest_delta",
        ),
        (
            lambda payload: payload["delta_placeholders"].pop(
                "normalized_document_reference_delta"
            ),
            "missing_normalized_document_reference_delta",
        ),
        (
            lambda payload: payload.pop("freshness_monitor_replay_notes"),
            "missing_freshness_monitor_replay_notes",
        ),
        (
            lambda payload: payload.pop("validation_commands"),
            "missing_validation_commands",
        ),
        (
            lambda payload: payload.update({"notes": "stores raw crawl artifact"}),
            "raw_crawl_artifact",
        ),
        (
            lambda payload: payload.update({"notes": "keeps downloaded PDF output"}),
            "downloaded_artifact",
        ),
        (
            lambda payload: payload.update({"notes": "contains private DevHub values"}),
            "private_artifact",
        ),
        (
            lambda payload: payload.update({"notes": "the worker performed a live crawl"}),
            "live_crawl_claim",
        ),
        (
            lambda payload: payload.update({"notes": "this will guarantee approval"}),
            "legal_or_permitting_guarantee",
        ),
        (
            lambda payload: payload.update({"notes": "click submit permit in DevHub"}),
            "consequential_DevHub_language",
        ),
        (
            lambda payload: payload.update({"mutates_active_artifacts": True}),
            "active_artifact_or_prompt_mutation_flag",
        ),
        (
            lambda payload: payload.update({"prompt_mutation_enabled": True}),
            "active_artifact_or_prompt_mutation_flag",
        ),
    ],
)
def test_preview_rejects_required_unsafe_or_incomplete_shapes(
    mutator: object, expected_code: str
) -> None:
    payload = valid_preview()
    mutator(payload)

    assert expected_code in issue_codes(payload)
    with pytest.raises(PublicSourceRecrawlInactivePatchPreviewError):
        validate_public_source_recrawl_inactive_patch_preview_v1(payload)
