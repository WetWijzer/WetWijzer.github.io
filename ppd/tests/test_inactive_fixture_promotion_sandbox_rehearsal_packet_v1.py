from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from ppd.inactive_fixture_promotion_sandbox_rehearsal_packet_v1 import (
    build_inactive_fixture_promotion_sandbox_rehearsal_packet_v1,
    validate_inactive_fixture_promotion_sandbox_rehearsal_packet_v1,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "inactive_fixture_promotion_sandbox_rehearsal_packet_v1"


def _source_plan() -> dict:
    return json.loads((FIXTURE_DIR / "source_patch_plan.json").read_text())


def _valid_packet() -> dict:
    return build_inactive_fixture_promotion_sandbox_rehearsal_packet_v1(_source_plan())


def _errors(packet: dict) -> tuple[str, ...]:
    return validate_inactive_fixture_promotion_sandbox_rehearsal_packet_v1(packet).errors


def test_builds_fixture_first_sandbox_rehearsal_from_application_patch_plan() -> None:
    packet = _valid_packet()

    assert validate_inactive_fixture_promotion_sandbox_rehearsal_packet_v1(packet).valid is True
    assert packet["artifact_id"] == "inactive_fixture_promotion_sandbox_rehearsal_packet_v1"
    assert packet["dry_run"] is True
    assert packet["sandbox_only"] is True
    assert packet["fixture_first"] is True
    assert packet["consumed_input_packet_refs"][0]["artifact_id"] == "inactive_fixture_promotion_application_plan_v1"


def test_sandbox_rehearsal_contains_apply_inventory_validation_rollback_and_worktree_notes() -> None:
    packet = _valid_packet()

    assert len(packet["synthetic_sandbox_apply_steps"]) == 2
    assert len(packet["expected_changed_fixture_family_inventory"]) == 4
    assert packet["pre_apply_validation_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    assert packet["post_apply_validation_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    assert packet["rollback_rehearsal_commands"] == [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
    assert packet["no_main_worktree_change_notes"][0]["asserted_unchanged"] is True


def test_sandbox_rehearsal_keeps_all_active_mutation_and_live_action_flags_false() -> None:
    packet = _valid_packet()

    for flag_name in (
        "active_fixture_mutation",
        "active_source_mutation",
        "active_document_mutation",
        "active_requirement_mutation",
        "active_process_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
        "devhub_accessed",
        "live_source_crawl_performed",
        "official_action_performed",
        "main_worktree_changed",
    ):
        assert packet[flag_name] is False


def test_rejects_missing_apply_steps_inventory_or_signoff_placeholders() -> None:
    packet = _valid_packet()
    packet["synthetic_sandbox_apply_steps"] = []
    packet["expected_changed_fixture_family_inventory"] = []
    packet["reviewer_signoff_placeholders"] = []

    errors = _errors(packet)

    assert any("synthetic_sandbox_apply_steps must include" in error for error in errors)
    assert any("expected_changed_fixture_family_inventory must include" in error for error in errors)
    assert any("reviewer_signoff_placeholders must include" in error for error in errors)


def test_rejects_missing_pre_post_or_rollback_validation_commands() -> None:
    packet = _valid_packet()
    packet["pre_apply_validation_commands"] = []
    packet["post_apply_validation_commands"] = []
    packet["rollback_rehearsal_commands"] = []

    errors = _errors(packet)

    assert any("pre_apply_validation_commands must include" in error for error in errors)
    assert any("post_apply_validation_commands must include" in error for error in errors)
    assert any("rollback_rehearsal_commands must include" in error for error in errors)


def test_rejects_filled_reviewer_signoff_placeholders() -> None:
    packet = _valid_packet()
    packet["reviewer_signoff_placeholders"][0]["reviewer_name"] = "reviewer"
    packet["reviewer_signoff_placeholders"][0]["signed_at"] = "2026-05-30T00:00:00Z"
    packet["reviewer_signoff_placeholders"][0]["disposition"] = "approved"

    errors = _errors(packet)

    assert any("reviewer_name must stay blank" in error for error in errors)
    assert any("signed_at must stay blank" in error for error in errors)
    assert any("disposition must stay blank" in error for error in errors)


def test_rejects_private_raw_live_promotion_guarantee_and_consequential_language() -> None:
    packet = _valid_packet()
    packet["artifact_refs"] = ["ppd/tests/fixtures/private-devhub-session/storage_state.json"]
    packet["raw_ref"] = "ppd/tests/fixtures/raw-crawl-output/raw_pdf.bin"
    packet["live_claim"] = "Promotion completed after live execution completed."
    packet["guarantee"] = "The permit will be approved."
    packet["next_action"] = "submit permit"

    errors = _errors(packet)

    assert any("private/authenticated/session/browser artifact" in error for error in errors)
    assert any("raw crawl/PDF/downloaded data" in error for error in errors)
    assert any("live execution or promotion-complete claim" in error for error in errors)
    assert any("legal or permitting outcome guarantee" in error for error in errors)
    assert any("consequential action language" in error for error in errors)


def test_rejects_active_flag_mutation() -> None:
    base = _valid_packet()

    for flag_name in ("active_fixture_mutation", "active_release_state_mutation", "devhub_accessed", "main_worktree_changed"):
        packet = deepcopy(base)
        packet[flag_name] = True
        assert any(f"{flag_name} must be false" in error for error in _errors(packet)), flag_name
