from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ppd.inactive_devhub_surface_fixture_migration_packet_v2 import (
    PACKET_TYPE,
    REQUIRED_ATTESTATIONS,
    build_inactive_devhub_surface_fixture_migration_packet_v2_from_fixture,
    validate_inactive_devhub_surface_fixture_migration_packet_v2,
)

FIXTURE = Path(__file__).parent / "fixtures" / "inactive_devhub_surface_fixture_migration_packet_v2" / "source_packets.json"


def valid_packet() -> dict[str, object]:
    return build_inactive_devhub_surface_fixture_migration_packet_v2_from_fixture(FIXTURE)


def test_builds_fixture_first_inactive_devhub_surface_fixture_migration_packet_v2() -> None:
    packet = valid_packet()

    assert packet["packet_type"] == PACKET_TYPE
    assert packet["packet_version"] == 2
    assert packet["mode"] == "fixture_first_inactive_devhub_surface_action_patch_rows_only"
    assert packet["attestations"] == REQUIRED_ATTESTATIONS
    assert packet["attestations"]["no_live_devhub"] is True
    assert packet["attestations"]["no_auth_state"] is True
    assert packet["attestations"]["no_screenshot"] is True
    assert packet["attestations"]["no_trace"] is True
    assert packet["attestations"]["no_har"] is True
    assert packet["attestations"]["no_active_surface_registry_mutation"] is True
    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]

    surface_rows = packet["cited_fixture_only_surface_patch_rows"]
    action_rows = packet["cited_fixture_only_action_patch_rows"]

    assert surface_rows
    assert action_rows
    assert packet["selector_confidence_before_after_checks"]
    assert packet["manual_handoff_dispositions"]
    assert packet["redaction_dispositions"]
    assert packet["rollback_checkpoints"]
    assert packet["reviewer_owner_fields"]

    first = surface_rows[0]
    assert first["fixture_only"] is True
    assert first["inactive"] is True
    assert first["active_surface_registry_mutation"] is False
    assert first["citations"]
    assert len(first["before_fixture_checksum"]) == 64
    assert len(first["after_fixture_checksum"]) == 64
    validate_inactive_devhub_surface_fixture_migration_packet_v2(packet)


def test_packet_carries_action_rows_selector_handoff_redaction_rollback_and_reviewers() -> None:
    packet = valid_packet()

    action = packet["cited_fixture_only_action_patch_rows"][0]
    assert action["surface_patch_row_id"] == packet["cited_fixture_only_surface_patch_rows"][0]["surface_patch_row_id"]
    assert action["phase"] in {"before", "after"}
    assert action["synthetic_action"]
    assert action["citations"]

    selector = packet["selector_confidence_before_after_checks"][0]
    assert selector["before_confidence"] == "current_fixture_selector_confidence_retained"
    assert selector["after_confidence"] == "medium"
    assert selector["citations"]

    handoff = packet["manual_handoff_dispositions"][0]
    assert handoff["required"] is True
    assert handoff["reason"]
    assert handoff["citations"]

    redaction = packet["redaction_dispositions"][0]
    assert redaction["disposition"] == "synthetic-only"
    assert redaction["reason"]
    assert redaction["citations"]

    rollback = packet["rollback_checkpoints"][0]
    assert rollback["active_surface_registry_unchanged"] is True
    assert rollback["reviewer_owner"]
    assert rollback["citations"]

    owner = packet["reviewer_owner_fields"][0]
    assert owner["reviewer_owner"]
    assert owner["linked_row_ids"]
    assert owner["citations"]


def test_validation_rejects_missing_required_sections() -> None:
    base = valid_packet()

    cases = [
        ("cited_fixture_only_surface_patch_rows", "surface patch rows"),
        ("cited_fixture_only_action_patch_rows", "action patch rows"),
        ("selector_confidence_before_after_checks", "selector-confidence"),
        ("manual_handoff_dispositions", "manual-handoff"),
        ("redaction_dispositions", "redaction dispositions"),
        ("rollback_checkpoints", "rollback checkpoints"),
        ("reviewer_owner_fields", "reviewer-owner"),
    ]

    for key, message in cases:
        broken = deepcopy(base)
        broken[key] = []
        with pytest.raises(ValueError, match=message):
            validate_inactive_devhub_surface_fixture_migration_packet_v2(broken)


def test_validation_rejects_uncited_rows_and_bad_action_references() -> None:
    packet = valid_packet()

    for section in (
        "cited_fixture_only_surface_patch_rows",
        "cited_fixture_only_action_patch_rows",
        "selector_confidence_before_after_checks",
        "manual_handoff_dispositions",
        "redaction_dispositions",
        "rollback_checkpoints",
    ):
        uncited = deepcopy(packet)
        uncited[section][0]["citations"] = []
        with pytest.raises(ValueError, match="citations must be non-empty"):
            validate_inactive_devhub_surface_fixture_migration_packet_v2(uncited)

    broken_ref = deepcopy(packet)
    broken_ref["cited_fixture_only_action_patch_rows"][0]["surface_patch_row_id"] = "missing-surface-row"
    with pytest.raises(ValueError, match="must reference a surface patch row"):
        validate_inactive_devhub_surface_fixture_migration_packet_v2(broken_ref)


def test_validation_rejects_missing_selector_handoff_redaction_and_rollback_fields() -> None:
    packet = valid_packet()

    for field in ("before_confidence", "after_confidence", "delta_disposition"):
        broken = deepcopy(packet)
        broken["selector_confidence_before_after_checks"][0][field] = ""
        with pytest.raises(ValueError, match=f"{field} must be present"):
            validate_inactive_devhub_surface_fixture_migration_packet_v2(broken)

    missing_handoff_required = deepcopy(packet)
    del missing_handoff_required["manual_handoff_dispositions"][0]["required"]
    with pytest.raises(ValueError, match="required must be present"):
        validate_inactive_devhub_surface_fixture_migration_packet_v2(missing_handoff_required)

    missing_redaction = deepcopy(packet)
    missing_redaction["redaction_dispositions"][0]["disposition"] = ""
    with pytest.raises(ValueError, match="disposition must be present"):
        validate_inactive_devhub_surface_fixture_migration_packet_v2(missing_redaction)

    bad_rollback = deepcopy(packet)
    bad_rollback["rollback_checkpoints"][0]["active_surface_registry_unchanged"] = False
    with pytest.raises(ValueError, match="active_surface_registry_unchanged must be true"):
        validate_inactive_devhub_surface_fixture_migration_packet_v2(bad_rollback)


def test_validation_rejects_missing_no_live_artifact_and_mutation_attestations() -> None:
    packet = valid_packet()
    broken = deepcopy(packet)
    broken["attestations"]["no_har"] = False

    with pytest.raises(ValueError, match="no-live-DevHub/no-auth-state/no-screenshot/no-trace/no-HAR"):
        validate_inactive_devhub_surface_fixture_migration_packet_v2(broken)


def test_validation_rejects_active_surface_registry_mutation_flags() -> None:
    for field in (
        "active_surface_registry_mutation",
        "surface_registry_mutation_enabled",
        "update_surface_registry",
        "mutates_surface_registry",
    ):
        packet = valid_packet()
        packet["cited_fixture_only_surface_patch_rows"][0][field] = True
        with pytest.raises(ValueError, match="active mutation flag|active_surface_registry_mutation false"):
            validate_inactive_devhub_surface_fixture_migration_packet_v2(packet)


def test_validation_rejects_private_session_browser_artifacts_live_claims_and_consequential_language() -> None:
    cases = [
        {"auth_state": "storage-state.json"},
        {"credentials": {"username": "private-user"}},
        {"private_value": "private DevHub value"},
        {"screenshot_path": "devhub.png"},
        {"trace_path": "trace.zip"},
        {"har_path": "devhub.har"},
        {"note": "browser automation completed"},
        {"note": "DevHub live run completed"},
        {"note": "guaranteed approval"},
        {"note": "permit will be approved"},
        {"note": "submit application"},
        {"note": "upload correction"},
        {"note": "schedule inspection"},
        {"note": "submit payment"},
    ]

    for injected in cases:
        packet = valid_packet()
        packet["unsafe_test_field"] = injected
        with pytest.raises(ValueError, match="prohibited|active mutation"):
            validate_inactive_devhub_surface_fixture_migration_packet_v2(packet)
