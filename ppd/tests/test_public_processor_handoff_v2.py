from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ppd.validation.public_processor_handoff_v2 import (
    PublicProcessorHandoffV2ValidationError,
    assert_valid_public_processor_handoff_packet_v2,
    validate_public_processor_handoff_packet_v2,
)


_FIXTURE = Path(__file__).parent / "fixtures" / "public_processor_handoff_v2" / "valid_packet.json"


def _packet() -> dict[str, Any]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def test_valid_public_processor_handoff_packet_v2_fixture_passes() -> None:
    assert validate_public_processor_handoff_packet_v2(_packet()) == []


@pytest.mark.parametrize(
    "field",
    [
        "allowlist_decisions",
        "robots_preflight_evidence",
        "policy_preflight_evidence",
        "archive_manifest_placeholders",
        "normalized_document_placeholders",
        "validation_commands",
    ],
)
def test_public_processor_handoff_packet_v2_rejects_missing_required_evidence(field: str) -> None:
    packet = _packet()
    packet.pop(field)

    errors = validate_public_processor_handoff_packet_v2(packet)

    assert any(field in error for error in errors)


def test_public_processor_handoff_packet_v2_rejects_missing_no_raw_body_flag() -> None:
    packet = _packet()
    packet.pop("no_raw_body")

    assert "no_raw_body must be true" in validate_public_processor_handoff_packet_v2(packet)


def test_public_processor_handoff_packet_v2_rejects_skipped_items_without_reasons() -> None:
    packet = _packet()
    packet["skipped_items"] = [{"item": "blocked-document"}]

    errors = validate_public_processor_handoff_packet_v2(packet)

    assert "skipped_items[0] must include a non-empty reason" in errors


@pytest.mark.parametrize(
    "artifact",
    [
        {"path": "private/devhub-session.json"},
        {"path": "browser/trace.zip"},
        {"path": "raw/downloaded-body.html"},
    ],
)
def test_public_processor_handoff_packet_v2_rejects_private_or_raw_artifacts(artifact: dict[str, str]) -> None:
    packet = _packet()
    packet["artifacts"] = [artifact]

    errors = validate_public_processor_handoff_packet_v2(packet)

    assert any("artifacts[0] references disallowed" in error for error in errors)


def test_public_processor_handoff_packet_v2_rejects_live_crawl_claims() -> None:
    packet = _packet()
    packet["live_crawl_claim"] = True

    assert "live crawl claims are not allowed" in validate_public_processor_handoff_packet_v2(packet)


@pytest.mark.parametrize(
    "field",
    [
        "active_crawler_mutation",
        "active_source_mutation",
        "active_archive_mutation",
        "active_document_mutation",
        "active_requirement_mutation",
        "active_guardrail_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
    ],
)
def test_public_processor_handoff_packet_v2_rejects_active_mutation_flags(field: str) -> None:
    packet = _packet()
    packet[field] = True

    errors = validate_public_processor_handoff_packet_v2(packet)

    assert f"{field} must not be true" in errors


@pytest.mark.parametrize(
    "claim",
    [
        "This is legal advice.",
        "Permit approval is guaranteed.",
        "The application will be approved.",
    ],
)
def test_public_processor_handoff_packet_v2_rejects_legal_or_permitting_guarantees(claim: str) -> None:
    packet = _packet()
    packet["notes"] = claim

    errors = validate_public_processor_handoff_packet_v2(packet)

    assert any("legal or permitting guarantee is not allowed" in error for error in errors)


def test_public_processor_handoff_packet_v2_assertion_raises_with_errors() -> None:
    packet = _packet()
    packet["allowlist_decisions"] = []

    with pytest.raises(PublicProcessorHandoffV2ValidationError):
        assert_valid_public_processor_handoff_packet_v2(packet)
