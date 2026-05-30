from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ppd.devhub.devhub_observation_dry_run import (
    FORBIDDEN_ARTIFACT_KINDS,
    MANIFEST_SCHEMA_VERSION,
    OFFLINE_VALIDATION_COMMANDS,
    build_manifest,
    load_json,
    manifest_to_json,
    validate_manifest,
    validate_preflight_packet,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "devhub"
PREFLIGHT_PACKET = FIXTURE_DIR / "attended_observation_preflight_packet_v1.json"
EXPECTED_MANIFEST = FIXTURE_DIR / "read_only_observation_dry_run_manifest_v1.json"


def test_build_manifest_matches_committed_fixture() -> None:
    packet = load_json(PREFLIGHT_PACKET)
    expected = load_json(EXPECTED_MANIFEST)

    manifest = build_manifest(packet)

    assert manifest == expected
    assert manifest_to_json(manifest) == EXPECTED_MANIFEST.read_text(encoding="utf-8")


def test_manifest_is_offline_read_only_and_artifact_free() -> None:
    manifest = build_manifest(load_json(PREFLIGHT_PACKET))
    validate_manifest(manifest)

    assert manifest["schema_version"] == MANIFEST_SCHEMA_VERSION
    assert manifest["mode"] == "offline_fixture_only"
    assert manifest["devhub_opened"] is False
    assert manifest["browser_or_session_artifacts_created"] is False
    assert manifest["prompt_changes_allowed"] is False
    assert manifest["official_actions_allowed"] is False
    assert manifest["offline_validation_commands"] == OFFLINE_VALIDATION_COMMANDS

    forbidden = set(manifest["forbidden_artifact_kinds"])
    assert forbidden == set(FORBIDDEN_ARTIFACT_KINDS)
    assert {"auth_state", "screenshots", "traces", "har", "private_page_values"}.issubset(forbidden)


def test_synthetic_steps_are_ordered_and_read_only() -> None:
    manifest = build_manifest(load_json(PREFLIGHT_PACKET))
    steps = manifest["synthetic_observation_steps"]

    assert [step["synthetic_sequence"] for step in steps] == [1, 2, 3]
    assert [step["step_id"] for step in steps] == [
        "synthetic_observation_step_01",
        "synthetic_observation_step_02",
        "synthetic_observation_step_03",
    ]

    for step in steps:
        assert step["navigation_policy"] == "manual_attended_only_no_browser_launched_by_dry_run"
        assert step["auth_scope"] == "authenticated_attended_redacted"
        assert step["manual_stop_checkpoint_refs"] == [
            "stop_before_auth_boundary",
            "stop_before_private_value_capture",
            "stop_before_reversible_draft_action",
            "stop_before_official_action",
        ]
        assert step["read_only_action_classification_refs"]
        assert all(ref.startswith("read_only:") for ref in step["read_only_action_classification_refs"])


def test_capture_fields_and_redaction_inventory_store_no_values() -> None:
    manifest = build_manifest(load_json(PREFLIGHT_PACKET))

    capture_fields = []
    for step in manifest["synthetic_observation_steps"]:
        capture_fields.extend(step["expected_accessible_role_capture_fields"])

    assert capture_fields
    for field in capture_fields:
        assert field["expected_accessible_role"]
        assert field["expected_accessible_name"]
        assert field["capture_policy"] == "record role/name/state only; never record private value"
        assert field["private_value_placeholder"] == "REDACTED_NOT_CAPTURED"
        assert field["observed_accessible_role"] is None
        assert field["observed_accessible_name"] is None
        assert field["observed_state_placeholder"] is None

    inventory = manifest["redacted_field_inventory_placeholders"]
    assert len(inventory) == len(capture_fields)
    for item in inventory:
        assert item["value_status"] == "placeholder_only_not_observed"
        assert item["stored_value"] is None


def test_reviewer_placeholders_do_not_attach_private_evidence() -> None:
    manifest = build_manifest(load_json(PREFLIGHT_PACKET))

    for step in manifest["synthetic_observation_steps"]:
        placeholder = step["reviewer_observation_placeholder"]
        assert placeholder["observed"] is False
        assert placeholder["reviewer"] is None
        assert placeholder["observed_at"] is None
        assert "Do not attach screenshots" in placeholder["evidence_policy"]
        assert "private values" in placeholder["evidence_policy"]

    assert manifest["reviewer_observation_placeholders"] == [
        {
            "surface_id": "devhub_home_attended_redacted",
            "step_id": "synthetic_observation_step_01",
            "review_status": "not_observed_fixture_placeholder",
            "reviewer_notes": None,
        },
        {
            "surface_id": "my_permits_requests_attended_redacted",
            "step_id": "synthetic_observation_step_02",
            "review_status": "not_observed_fixture_placeholder",
            "reviewer_notes": None,
        },
        {
            "surface_id": "permit_detail_attended_redacted",
            "step_id": "synthetic_observation_step_03",
            "review_status": "not_observed_fixture_placeholder",
            "reviewer_notes": None,
        },
    ]


def test_validate_preflight_rejects_live_or_stateful_packets() -> None:
    packet = load_json(PREFLIGHT_PACKET)

    packet["devhub_opened"] = True
    with pytest.raises(ValueError, match="DevHub was not opened"):
        validate_preflight_packet(packet)

    packet = load_json(PREFLIGHT_PACKET)
    packet["stores_session_or_browser_artifacts"] = True
    with pytest.raises(ValueError, match="must not store session"):
        validate_preflight_packet(packet)

    packet = load_json(PREFLIGHT_PACKET)
    packet["surfaces"][0]["read_only_action_keys"] = ["submit_permit_request"]
    with pytest.raises(ValueError, match="Unknown read-only action keys"):
        validate_preflight_packet(packet)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda manifest: manifest.pop("synthetic_observation_steps"), "synthetic_observation_steps"),
        (lambda manifest: manifest["synthetic_observation_steps"][0].pop("expected_accessible_role_capture_fields"), "expected_accessible_role_capture_fields"),
        (lambda manifest: manifest["synthetic_observation_steps"][0]["expected_accessible_role_capture_fields"][0].pop("expected_accessible_role"), "expected_accessible_role"),
        (lambda manifest: manifest.pop("redacted_field_inventory_placeholders"), "redacted_field_inventory_placeholders"),
        (lambda manifest: manifest["synthetic_observation_steps"][0].pop("read_only_action_classification_refs"), "read_only_action_classification_refs"),
        (lambda manifest: manifest.pop("manual_stop_checkpoints"), "manual_stop_checkpoints"),
        (lambda manifest: manifest.pop("reviewer_observation_placeholders"), "reviewer_observation_placeholders"),
        (lambda manifest: manifest.pop("offline_validation_commands"), "offline_validation_commands"),
    ],
)
def test_validate_manifest_rejects_missing_required_sections(mutation, expected: str) -> None:
    manifest = build_manifest(load_json(PREFLIGHT_PACKET))
    mutation(manifest)

    with pytest.raises(ValueError, match=expected):
        validate_manifest(manifest)


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("credentials", "stored password", "credentials"),
        ("auth_state_path", "playwright/.auth/session.json", "auth"),
        ("browser_profile", "/home/operator/.cache/browser", "browser"),
        ("screenshot_path", "capture.png", "screenshot"),
        ("trace_path", "trace.zip", "trace"),
        ("har_path", "network.har", "HAR"),
        ("private_page_values", {"permit_number": "24-123456-000-00-CO"}, "private"),
    ],
)
def test_validate_manifest_rejects_artifact_and_private_keys(key: str, value, expected: str) -> None:
    manifest = build_manifest(load_json(PREFLIGHT_PACKET))
    manifest[key] = value

    with pytest.raises(ValueError, match=expected):
        validate_manifest(manifest)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("The operator opened live DevHub and captured the page.", "live DevHub"),
        ("Stored screenshot path for reviewer evidence.", "screenshot"),
        ("Permit number: 24-123456-000-00-CO", "private"),
        ("Clicked submit application successfully.", "payment, submission"),
        ("Upload file action is enabled for this dry run.", "payment, submission"),
        ("Schedule inspection action completed.", "payment, submission"),
        ("Certification submission can proceed.", "payment, submission"),
        ("Payment was triggered.", "payment, submission"),
    ],
)
def test_validate_manifest_rejects_prohibited_text(text: str, expected: str) -> None:
    manifest = build_manifest(load_json(PREFLIGHT_PACKET))
    manifest["synthetic_observation_steps"][0]["unsafe_note"] = text

    with pytest.raises(ValueError, match=expected):
        validate_manifest(manifest)


def test_validate_manifest_rejects_active_mutation_flags() -> None:
    manifest = build_manifest(load_json(PREFLIGHT_PACKET))
    manifest["active_surface_registry_mutation"] = True
    manifest["active_guardrail_mutation"] = True
    manifest["active_prompt_mutation"] = True
    manifest["active_release_state_mutation"] = True
    manifest["active_devhub_mutation"] = True

    with pytest.raises(ValueError, match="active surface"):
        validate_manifest(manifest)


def test_validate_manifest_rejects_mismatched_inventory_or_review_placeholders() -> None:
    manifest = build_manifest(load_json(PREFLIGHT_PACKET))
    manifest["redacted_field_inventory_placeholders"] = manifest["redacted_field_inventory_placeholders"][:-1]
    with pytest.raises(ValueError, match="cover every expected accessible capture field"):
        validate_manifest(manifest)

    manifest = build_manifest(load_json(PREFLIGHT_PACKET))
    manifest["reviewer_observation_placeholders"] = list(reversed(manifest["reviewer_observation_placeholders"]))
    with pytest.raises(ValueError, match="match synthetic observation steps"):
        validate_manifest(manifest)


def test_committed_json_fixtures_are_valid_objects() -> None:
    for fixture_path in (PREFLIGHT_PACKET, EXPECTED_MANIFEST):
        parsed = json.loads(fixture_path.read_text(encoding="utf-8"))
        assert isinstance(parsed, dict)


def test_committed_manifest_fixture_passes_new_validator() -> None:
    manifest = deepcopy(load_json(EXPECTED_MANIFEST))
    validate_manifest(manifest)
