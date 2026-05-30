from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.crawler.public_source_recrawl_dry_run_manifest_v1 import (
    OFFLINE_VALIDATION_COMMANDS,
    ManifestValidationError,
    build_public_source_recrawl_dry_run_manifest_v1,
    build_public_source_recrawl_dry_run_manifest_v1_from_file,
    load_json,
    validate_public_source_recrawl_dry_run_manifest_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "public_source_recrawl_dry_run_manifest_v1"


def build_fixture_manifest() -> dict[str, object]:
    return build_public_source_recrawl_dry_run_manifest_v1_from_file(FIXTURE_DIR / "preflight_packet.json")


def test_builds_expected_fixture_first_public_source_recrawl_dry_run_manifest_v1() -> None:
    actual = build_fixture_manifest()
    expected = load_json(FIXTURE_DIR / "expected_manifest.json")

    assert actual == expected


def test_synthetic_request_rows_are_ordered_with_allow_and_skip_reasons() -> None:
    manifest = build_fixture_manifest()
    rows = manifest["synthetic_request_rows"]
    assert isinstance(rows, list)

    assert [row["request_order"] for row in rows] == [1, 2, 3]
    assert [row["source_id"] for row in rows] == [
        "ppd-online-permitting-tools",
        "ppd-fee-payment-guide",
        "ppd-devhub-public-portal",
    ]
    assert [row["allow_reason"] for row in rows] == [
        "official_anchor_policy_preflight_ready",
        "official_anchor_policy_preflight_ready",
        None,
    ]
    assert [row["skipped_reason"] for row in rows] == [
        None,
        None,
        "portal_access_deferred_no_devhub_access",
    ]


def test_rows_include_metadata_only_capture_fields_and_processor_suite_adapter_refs() -> None:
    manifest = build_fixture_manifest()
    rows = manifest["synthetic_request_rows"]
    assert isinstance(rows, list)

    for row in rows:
        capture = row["expected_metadata_only_capture"]
        assert capture["redirect_chain_placeholder"] == []
        assert capture["http_status_placeholder"] is None
        assert capture["content_hash_placeholder"] is None
        assert capture["capture_started_at_placeholder"] is None
        assert capture["capture_finished_at_placeholder"] is None
        assert capture["no_raw_body_persisted"] is True

        adapter_ref = row["processor_suite_adapter_ref"]
        assert adapter_ref["adapter_module"] == "ppd.crawler.processor_suite"
        assert adapter_ref["adapter_id"].startswith("processor-suite-adapter:")
        assert adapter_ref["processor_name"]
        assert adapter_ref["processor_version"]


def test_manifest_contains_freshness_and_reviewer_placeholders_without_active_updates() -> None:
    manifest = build_fixture_manifest()

    freshness_rows = manifest["freshness_monitor_update_placeholders"]
    reviewer_rows = manifest["reviewer_disposition_placeholders"]
    assert isinstance(freshness_rows, list)
    assert isinstance(reviewer_rows, list)

    assert len(freshness_rows) == 3
    assert len(reviewer_rows) == 3

    for row in freshness_rows:
        assert row["current_freshness_status_placeholder"] == "pending_metadata_capture_review"
        assert row["freshness_monitor_mutation_allowed"] is False
        assert row["reviewer_required_before_update"] is True

    for row in reviewer_rows:
        assert row["hold_reason_placeholder"] == "pending_reviewer_disposition"
        assert row["approve_reason_placeholder"] == "pending_reviewer_disposition"
        assert row["approved_for_live_recrawl"] is False


def test_manifest_records_exact_offline_validation_commands_and_side_effect_boundary() -> None:
    manifest = build_fixture_manifest()

    assert manifest["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS
    assert manifest["side_effect_boundary"] == {
        "network_requests_allowed": False,
        "document_downloads_allowed": False,
        "raw_response_body_storage_allowed": False,
        "devhub_access_allowed": False,
        "processor_invocation_allowed": False,
        "active_source_mutation_allowed": False,
        "active_process_mutation_allowed": False,
        "active_guardrail_mutation_allowed": False,
        "active_prompt_mutation_allowed": False,
    }
    assert manifest["network_request_performed"] is False
    assert manifest["document_download_performed"] is False
    assert manifest["raw_response_body_stored"] is False
    assert manifest["devhub_access_performed"] is False
    assert manifest["processor_invoked"] is False


def test_rejects_preflight_packet_that_fails_preflight_packet_validator() -> None:
    packet = load_json(FIXTURE_DIR / "preflight_packet.json")
    packet["candidate_preflight_rows"][0]["canonical_url"] = "https://example.com/not-allowed"

    with pytest.raises(ValueError, match="official public PP&D anchor"):
        build_public_source_recrawl_dry_run_manifest_v1(packet)


@pytest.mark.parametrize(
    "flag",
    [
        "network_request_performed",
        "document_download_performed",
        "raw_response_body_stored",
        "devhub_access_performed",
        "processor_invoked",
        "active_source_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "freshness_monitor_mutation",
    ],
)
def test_validator_rejects_live_execution_or_mutation_claims(flag: str) -> None:
    manifest = build_fixture_manifest()
    manifest[flag] = True

    with pytest.raises(ManifestValidationError, match="must be false"):
        validate_public_source_recrawl_dry_run_manifest_v1(manifest)


def test_validator_rejects_raw_or_downloaded_artifact_data_references() -> None:
    manifest = build_fixture_manifest()
    rows = manifest["synthetic_request_rows"]
    assert isinstance(rows, list)
    rows[0]["raw_body"] = "not allowed"
    rows[1]["download_path"] = "not allowed"

    with pytest.raises(ManifestValidationError, match="raw, private, or downloaded artifact data"):
        validate_public_source_recrawl_dry_run_manifest_v1(manifest)


def test_validator_rejects_out_of_order_synthetic_rows() -> None:
    manifest = build_fixture_manifest()
    rows = manifest["synthetic_request_rows"]
    assert isinstance(rows, list)
    rows[0]["request_order"] = 2

    with pytest.raises(ManifestValidationError, match="contiguous request_order"):
        validate_public_source_recrawl_dry_run_manifest_v1(manifest)


def test_validator_rejects_pre_approved_reviewer_disposition() -> None:
    manifest = build_fixture_manifest()
    reviewer_rows = manifest["reviewer_disposition_placeholders"]
    assert isinstance(reviewer_rows, list)
    reviewer_rows[0]["approved_for_live_recrawl"] = True

    with pytest.raises(ManifestValidationError, match="must not pre-approve live recrawl"):
        validate_public_source_recrawl_dry_run_manifest_v1(manifest)


def test_validator_accepts_clean_deepcopy_of_fixture_manifest() -> None:
    manifest = deepcopy(build_fixture_manifest())

    validate_public_source_recrawl_dry_run_manifest_v1(manifest)
