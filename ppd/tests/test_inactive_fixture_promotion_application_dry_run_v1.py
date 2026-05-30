from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from ppd.inactive_fixture_promotion_application_dry_run_v1 import (
    validate_inactive_fixture_promotion_application_dry_run_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "inactive_fixture_promotion_application_dry_run_v1"


def _valid_packet() -> dict:
    return json.loads((FIXTURE_DIR / "valid_dry_run.json").read_text())


def _errors(packet: dict) -> tuple[str, ...]:
    return validate_inactive_fixture_promotion_application_dry_run_v1(packet).errors


def test_valid_inactive_fixture_promotion_application_dry_run_v1_passes() -> None:
    result = validate_inactive_fixture_promotion_application_dry_run_v1(_valid_packet())

    assert result.valid is True
    assert result.errors == ()


def test_rejects_missing_patch_manifest_rows() -> None:
    packet = _valid_packet()
    packet["patch_manifest_rows"] = []

    assert any("patch_manifest_rows must include patch-manifest rows" in error for error in _errors(packet))


def test_rejects_uncited_changed_row_evidence() -> None:
    packet = _valid_packet()
    packet["patch_manifest_rows"][0]["changed_row_evidence"]["citations"] = []

    assert any("changed_row_evidence.citations" in error for error in _errors(packet))


def test_rejects_missing_unchanged_file_inventory() -> None:
    packet = _valid_packet()
    packet["unchanged_file_inventory"] = []

    assert any("unchanged_file_inventory must include" in error for error in _errors(packet))


def test_rejects_missing_validation_commands() -> None:
    packet = _valid_packet()
    packet["validation_commands"] = []

    assert any("validation_commands must include" in error for error in _errors(packet))


def test_rejects_missing_rollback_notes() -> None:
    packet = _valid_packet()
    packet["rollback_notes"] = []

    assert any("rollback_notes must include" in error for error in _errors(packet))


def test_rejects_private_authenticated_session_browser_artifacts() -> None:
    packet = _valid_packet()
    packet["artifact_refs"] = ["ppd/tests/fixtures/private-devhub-session/storage_state.json"]

    assert any("private/authenticated/session/browser artifact" in error for error in _errors(packet))


def test_rejects_raw_crawl_pdf_downloaded_data() -> None:
    packet = _valid_packet()
    packet["artifact_refs"] = ["ppd/tests/fixtures/raw-crawl-output/downloaded-data/raw_pdf.bin"]

    assert any("raw crawl/PDF/downloaded data" in error for error in _errors(packet))


def test_rejects_live_execution_claims() -> None:
    packet = _valid_packet()
    packet["notes"] = "Promotion completed after live execution completed."

    assert any("live execution claim" in error for error in _errors(packet))


def test_rejects_legal_or_permitting_outcome_guarantees() -> None:
    packet = _valid_packet()
    packet["notes"] = "This proves the permit will be approved."

    assert any("legal or permitting outcome guarantee" in error for error in _errors(packet))


def test_rejects_consequential_action_language() -> None:
    packet = _valid_packet()
    packet["next_action"] = "submit permit"

    assert any("consequential action language" in error for error in _errors(packet))


def test_rejects_blocked_live_or_consequential_validation_commands() -> None:
    packet = _valid_packet()
    packet["validation_commands"].append(["python3", "scripts/permit_submission.py"])

    assert any("blocked live or consequential behavior" in error for error in _errors(packet))


def test_rejects_mutation_flags_outside_inactive_fixture_promotion_scope() -> None:
    base = _valid_packet()
    flag_names = (
        "active_source_mutation",
        "active_document_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_fixture_mutation",
        "active_agent_state_mutation",
    )

    for flag_name in flag_names:
        packet = deepcopy(base)
        packet[flag_name] = False
        errors = _errors(packet)
        assert any("mutation flag outside inactive fixture promotion scope" in error for error in errors), flag_name
