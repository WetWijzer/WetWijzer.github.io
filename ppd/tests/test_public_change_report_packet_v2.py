from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

import pytest

from ppd.public_change_report_packet_v2 import (
    PublicChangeReportPacketV2Error,
    build_public_change_report_packet_v2,
    build_public_change_report_packet_v2_from_file,
    load_public_change_report_fixture_v2,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_change_report_packet_v2" / "synthetic_changed_source_hashes_fixture.json"


def _fixture() -> dict[str, Any]:
    return deepcopy(load_public_change_report_fixture_v2(FIXTURE_PATH))


def test_public_change_report_packet_v2_is_fixture_first_and_side_effect_free() -> None:
    packet = build_public_change_report_packet_v2_from_file(FIXTURE_PATH)
    assert packet["packet_type"] == "public_change_report_packet_v2"
    assert packet["generated_from"] == "synthetic_changed_source_hashes_fixture"
    assert packet["side_effect_policy"] == {"fixture_only": True, "live_content_reextracted": False, "active_requirements_mutated": False, "active_process_models_mutated": False, "active_guardrail_bundles_mutated": False, "active_source_registries_mutated": False}


def test_public_change_report_packet_v2_emits_added_removed_and_changed_rows() -> None:
    packet = build_public_change_report_packet_v2_from_file(FIXTURE_PATH)
    assert [row["change_type"] for row in packet["requirement_rows"]] == ["added", "removed", "changed"]
    assert packet["summary_counts"] == {"source_hashes": 2, "added_requirement_rows": 1, "removed_requirement_rows": 1, "changed_requirement_rows": 1, "affected_process_models": 3, "affected_guardrail_bundles": 3}


def test_public_change_report_packet_v2_lists_affected_models_guardrails_and_placeholders() -> None:
    packet = build_public_change_report_packet_v2_from_file(FIXTURE_PATH)
    assert packet["affected_process_model_ids"] == ["process-building-permit-plan-review", "process-devhub-corrections-review", "process-single-pdf-submit-plans"]
    assert packet["affected_guardrail_bundle_ids"] == ["guardrail-bundle-devhub-corrections", "guardrail-bundle-document-preparation", "guardrail-bundle-upload-staging-review"]
    assert all("pending" in placeholder for placeholder in packet["reviewer_disposition_placeholders"])
    assert all(row["active_requirement_mutated"] is False for row in packet["requirement_rows"])


def test_public_change_report_packet_v2_preserves_stale_source_carry_forward_notes() -> None:
    packet = build_public_change_report_packet_v2_from_file(FIXTURE_PATH)
    assert len(packet["stale_source_carry_forward_notes"]) == 3
    assert all(note for note in packet["stale_source_carry_forward_notes"])
    assert all(source["source_registry_mutated"] is False for source in packet["synthetic_changed_source_hashes"])


def test_public_change_report_packet_v2_includes_exact_offline_validation_commands() -> None:
    packet = build_public_change_report_packet_v2_from_file(FIXTURE_PATH)
    assert packet["exact_offline_validation_commands"] == [["python3", "-m", "py_compile", "ppd/public_change_report_packet_v2.py"], ["python3", "-m", "py_compile", "ppd/tests/test_public_change_report_packet_v2.py"], ["python3", "-m", "pytest", "ppd/tests/test_public_change_report_packet_v2.py"], ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]


@pytest.mark.parametrize("field", ["previous_hash", "current_hash"])
def test_public_change_report_packet_v2_rejects_missing_changed_source_hashes(field: str) -> None:
    fixture = _fixture()
    del fixture["synthetic_changed_source_hashes"][0][field]
    with pytest.raises(PublicChangeReportPacketV2Error, match=field):
        build_public_change_report_packet_v2(fixture)


@pytest.mark.parametrize("change_type", ["added", "removed", "changed"])
def test_public_change_report_packet_v2_rejects_missing_requirement_change_bucket(change_type: str) -> None:
    fixture = _fixture()
    fixture["requirement_deltas"] = [row for row in fixture["requirement_deltas"] if row["change_type"] != change_type]
    with pytest.raises(PublicChangeReportPacketV2Error, match="added, removed, and changed"):
        build_public_change_report_packet_v2(fixture)


@pytest.mark.parametrize("field", ["affected_process_model_ids", "affected_guardrail_bundle_ids"])
def test_public_change_report_packet_v2_rejects_missing_affected_ids(field: str) -> None:
    fixture = _fixture()
    fixture["requirement_deltas"][0][field] = []
    with pytest.raises(PublicChangeReportPacketV2Error, match=field):
        build_public_change_report_packet_v2(fixture)


@pytest.mark.parametrize("field", ["reviewer_disposition_placeholder", "stale_source_carry_forward_note"])
def test_public_change_report_packet_v2_rejects_missing_review_and_stale_notes(field: str) -> None:
    fixture = _fixture()
    fixture["requirement_deltas"][0][field] = ""
    with pytest.raises(PublicChangeReportPacketV2Error, match=field):
        build_public_change_report_packet_v2(fixture)


def test_public_change_report_packet_v2_rejects_missing_validation_commands() -> None:
    fixture = _fixture()
    fixture["exact_offline_validation_commands"] = []
    with pytest.raises(PublicChangeReportPacketV2Error, match="exact_offline_validation_commands"):
        build_public_change_report_packet_v2(fixture)


def test_public_change_report_packet_v2_rejects_unknown_source_references() -> None:
    fixture = _fixture()
    fixture["requirement_deltas"][0]["source_id"] = "missing-source"
    with pytest.raises(PublicChangeReportPacketV2Error, match="unknown source_id"):
        build_public_change_report_packet_v2(fixture)


@pytest.mark.parametrize("key", ["private_artifact", "session_artifact", "browser_trace", "raw_body", "downloaded_document_path"])
def test_public_change_report_packet_v2_rejects_private_browser_raw_or_downloaded_artifacts(key: str) -> None:
    fixture = _fixture()
    fixture[key] = "not allowed"
    with pytest.raises(PublicChangeReportPacketV2Error, match="raw or private field"):
        build_public_change_report_packet_v2(fixture)


def test_public_change_report_packet_v2_rejects_private_query_urls() -> None:
    fixture = _fixture()
    fixture["synthetic_changed_source_hashes"][0]["canonical_url"] = "https://www.portland.gov/ppd/get-permit/submit-plans-online?token=abc"
    with pytest.raises(PublicChangeReportPacketV2Error, match="private query"):
        build_public_change_report_packet_v2(fixture)


@pytest.mark.parametrize("claim", ["live crawl completed", "This is legal advice.", "Permit approval guaranteed."])
def test_public_change_report_packet_v2_rejects_live_crawl_or_legal_permitting_guarantees(claim: str) -> None:
    fixture = _fixture()
    fixture["requirement_deltas"][0]["requirement_summary"] = claim
    with pytest.raises(PublicChangeReportPacketV2Error, match="forbidden live crawl, legal, or permitting guarantee"):
        build_public_change_report_packet_v2(fixture)


@pytest.mark.parametrize("flag", ["live_content_reextracted", "active_requirements_mutated", "active_process_models_mutated", "active_guardrail_bundles_mutated", "active_source_registries_mutated"])
def test_public_change_report_packet_v2_rejects_live_reextract_or_mutation_flags(flag: str) -> None:
    fixture = _fixture()
    fixture["side_effect_policy"][flag] = True
    with pytest.raises(PublicChangeReportPacketV2Error):
        build_public_change_report_packet_v2(fixture)


@pytest.mark.parametrize("flag", ["active_source_mutation", "active_requirement_mutation", "active_process_model_mutation", "active_guardrail_mutation", "active_prompt_mutation", "active_contract_mutation", "active_devhub_surface_mutation", "active_release_state_mutation"])
def test_public_change_report_packet_v2_rejects_active_domain_mutation_flags(flag: str) -> None:
    fixture = _fixture()
    fixture["mutation_flags"] = {flag: True}
    with pytest.raises(PublicChangeReportPacketV2Error, match="active source, requirement, process-model"):
        build_public_change_report_packet_v2(fixture)
