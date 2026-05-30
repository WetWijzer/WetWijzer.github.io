from __future__ import annotations

import json
from pathlib import Path

from ppd.acceptance.surface_registry_refresh_acceptance_packet_v2 import (
    OFFLINE_VALIDATION_COMMANDS,
    REQUIRED_ATTESTATIONS,
    build_from_fixture_paths,
    validate_surface_registry_refresh_acceptance_packet_v2,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "surface_registry_refresh_acceptance_packet_v2"


def _load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_packet() -> dict:
    return build_from_fixture_paths(
        FIXTURE_DIR / "surface_registry_refresh_review_packet_v2.json",
        FIXTURE_DIR / "devhub_attended_readonly_observation_packet_v2.json",
        FIXTURE_DIR / "guardrail_bundle_refresh_candidate_v2.json",
    )


def test_builds_expected_surface_registry_refresh_acceptance_packet_v2() -> None:
    assert _build_packet() == _load_fixture("expected_surface_registry_refresh_acceptance_packet_v2.json")


def test_acceptance_packet_groups_cited_updates_by_decision() -> None:
    packet = _build_packet()
    validate_surface_registry_refresh_acceptance_packet_v2(packet)

    updates = packet["surface_action_updates"]
    assert [entry["update_id"] for entry in updates["accepted"]] == ["update:devhub-home-readonly-status-card"]
    assert [entry["update_id"] for entry in updates["deferred"]] == ["update:my-permits-filter-selector"]
    assert [entry["update_id"] for entry in updates["rejected"]] == ["update:correction-upload-submit-control"]
    assert all(entry["citations"] for group in updates.values() for entry in group)


def test_acceptance_packet_preserves_selector_manual_handoff_and_redaction_decisions() -> None:
    packet = _build_packet()

    selector_dispositions = {entry["selector_id"]: entry["disposition"] for entry in packet["selector_confidence_dispositions"]}
    assert selector_dispositions == {
        "selector:devhub-home-status-card-heading": "accept-high-confidence-readonly-selector",
        "selector:my-permits-filter-input": "defer-until-attended-live-confirmation",
        "selector:correction-upload-submit-button": "reject-consequential-control-selector",
    }
    assert all(entry["requires_attendance"] is True for entry in packet["manual_handoff_decisions"])
    assert all(entry["private_values_allowed"] is False for entry in packet["redaction_gate_decisions"])
    assert all(entry["browser_artifacts_allowed"] is False for entry in packet["redaction_gate_decisions"])


def test_acceptance_packet_contains_required_attestations_and_offline_commands() -> None:
    packet = _build_packet()

    assert packet["attestations"] == {name: True for name in REQUIRED_ATTESTATIONS}
    assert packet["offline_validation_commands"] == [list(command) for command in OFFLINE_VALIDATION_COMMANDS]
