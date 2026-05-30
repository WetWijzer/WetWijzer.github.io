from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ppd.source_observation_patch_application_preview_v2 import (
    ATTESTATIONS,
    build_source_observation_patch_application_preview_v2_from_fixture,
    require_source_observation_patch_application_preview_v2,
    validate_source_observation_patch_application_preview_v2,
)

FIXTURE = Path(__file__).parent / "fixtures" / "source_observation_patch_application_preview_v2" / "source_packets.json"


def valid_preview() -> dict[str, object]:
    return build_source_observation_patch_application_preview_v2_from_fixture(FIXTURE)


def error_text(packet: dict[str, object]) -> str:
    return "\n".join(validate_source_observation_patch_application_preview_v2(packet).errors)


def test_builds_inactive_cited_source_registry_fixture_patch_previews() -> None:
    packet = valid_preview()

    assert packet["preview_type"] == "ppd.source_observation_patch_application_preview.v2"
    assert packet["fixture_first"] is True
    assert packet["attestations"] == ATTESTATIONS
    assert packet["affected_source_ids"]
    assert packet["reviewer_owner_fields"]
    assert packet["rollback_checkpoints"]

    previews = packet["source_registry_fixture_patch_previews"]
    assert isinstance(previews, list)
    assert previews
    first = previews[0]
    assert isinstance(first, dict)
    assert first["inactive"] is True
    assert first["source_registry_fixture_patch"] is True
    assert first["affected_source_ids"]
    assert first["before_metadata_rows"]
    assert first["after_metadata_rows"]
    assert first["citations"]
    require_source_observation_patch_application_preview_v2(packet)


def test_validation_rejects_missing_before_after_metadata_rows() -> None:
    packet = valid_preview()
    broken = deepcopy(packet)
    previews = broken["source_registry_fixture_patch_previews"]
    assert isinstance(previews, list)
    first = previews[0]
    assert isinstance(first, dict)
    first["before_metadata_rows"] = []
    first["after_metadata_rows"] = []

    text = error_text(broken)
    assert "before_metadata_rows must be non-empty" in text
    assert "after_metadata_rows must be non-empty" in text


def test_validation_rejects_source_registry_mutation_flags() -> None:
    packet = valid_preview()
    broken = deepcopy(packet)
    broken["source_registry_mutation_enabled"] = True

    assert "must not enable source registry mutation" in error_text(broken)


def test_validation_rejects_raw_body_and_live_claims() -> None:
    packet = valid_preview()
    broken = deepcopy(packet)
    broken["raw_body"] = "not allowed"
    broken["note"] = "live crawl completed"

    text = error_text(broken)
    assert "raw_body is prohibited" in text
    assert "prohibited live" in text
