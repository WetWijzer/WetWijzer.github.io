from __future__ import annotations

import json
from pathlib import Path

from ppd.surfaces.surface_registry_refresh_review_packet_v2 import (
    assert_valid_surface_registry_refresh_review_packet_v2,
    validate_surface_registry_refresh_review_packet_v2,
)


FIXTURES = Path(__file__).parent / "fixtures" / "surface_registry_refresh_review_packet_v2"


def _load_fixture(name: str) -> dict:
    with (FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def test_accepts_offline_cited_review_packet_with_required_checkpoints() -> None:
    packet = _load_fixture("valid_packet.json")

    assert validate_surface_registry_refresh_review_packet_v2(packet) == []
    assert_valid_surface_registry_refresh_review_packet_v2(packet)


def test_rejects_uncited_review_items_and_missing_required_checkpoints() -> None:
    packet = _load_fixture("invalid_uncited_missing_checkpoints.json")

    errors = validate_surface_registry_refresh_review_packet_v2(packet)

    assert "review_items[0] surface is missing citations" in errors
    assert "review_items[0] surface is missing selector_confidence" in errors
    assert "missing selector-confidence checkpoint" in errors
    assert "missing manual-handoff checkpoint" in errors


def test_rejects_private_artifacts_execution_claims_guarantees_and_mutations() -> None:
    packet = _load_fixture("invalid_prohibited_content.json")

    errors = validate_surface_registry_refresh_review_packet_v2(packet)
    joined = "\n".join(errors)

    assert "enables a consequential action" in joined
    assert "private or authenticated value field" in joined
    assert "session or authentication artifact" in joined
    assert "screenshots, traces, HAR" in joined
    assert "claims live DevHub or browser execution" in joined
    assert "legal or permitting outcome guarantee" in joined
    assert "active mutation flag" in joined
    assert "active surface-registry, guardrail, prompt, monitoring, release-state, or agent-state mutation" in joined
