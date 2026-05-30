from __future__ import annotations

import pytest

from ppd.validation.promotion_dependency_packet_v1 import (
    assert_valid_combined_promotion_dependency_packet_v1,
    validate_combined_promotion_dependency_packet_v1,
)


def _valid_packet() -> dict[str, object]:
    return {
        "packet_version": "combined-promotion-dependency-packet-v1",
        "owner": "ppd-validation",
        "dependency_order": ["source-freeze", "fixture-check", "promotion-review"],
        "rollback_checkpoints": ["restore previous fixture manifest"],
        "validation_inventory": ["fixture schema check", "citation check"],
        "prerequisites": [
            {
                "name": "fixture-only evidence",
                "citations": ["ppd/tests/fixtures/promotion_dependency_packet_v1/README.md"],
            }
        ],
        "artifacts": ["deterministic fixture manifest"],
        "claims": ["validation packet prepared for offline review"],
        "mutation_flags": {
            "active_source_mutation": False,
            "surface_registry_mutation": False,
            "guardrail_mutation": False,
            "prompt_mutation": False,
            "release_state_mutation": False,
            "agent_state_mutation": False,
        },
    }


def test_valid_packet_passes() -> None:
    result = validate_combined_promotion_dependency_packet_v1(_valid_packet())

    assert result.valid
    assert result.errors == ()
    assert_valid_combined_promotion_dependency_packet_v1(_valid_packet())


@pytest.mark.parametrize(
    "field",
    ["owner", "dependency_order", "rollback_checkpoints", "validation_inventory"],
)
def test_required_operational_fields_are_rejected_when_missing(field: str) -> None:
    packet = _valid_packet()
    packet.pop(field)

    result = validate_combined_promotion_dependency_packet_v1(packet)

    assert not result.valid
    assert any(field in error for error in result.errors)


def test_uncited_prerequisites_are_rejected() -> None:
    packet = _valid_packet()
    packet["prerequisites"] = [{"name": "uncited dependency"}]

    result = validate_combined_promotion_dependency_packet_v1(packet)

    assert not result.valid
    assert any("prerequisites[0]" in error and "citation" in error for error in result.errors)


@pytest.mark.parametrize(
    "text",
    [
        "private artifact",
        "authenticated browser trace",
        "session cookie",
        "raw crawl output",
        "downloaded document",
        "live execution completed",
        "promotion complete",
        "permit approved guarantee",
        "legally compliant outcome",
        "submit application",
        "pay fee",
        "schedule inspection",
        "upload document",
    ],
)
def test_prohibited_packet_language_is_rejected(text: str) -> None:
    packet = _valid_packet()
    packet["claims"] = [text]

    result = validate_combined_promotion_dependency_packet_v1(packet)

    assert not result.valid
    assert result.errors


@pytest.mark.parametrize(
    "flag",
    [
        "active_source_mutation",
        "surface_registry_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "release_state_mutation",
        "agent_state_mutation",
    ],
)
def test_active_mutation_flags_are_rejected(flag: str) -> None:
    packet = _valid_packet()
    packet["mutation_flags"] = {flag: True}

    result = validate_combined_promotion_dependency_packet_v1(packet)

    assert not result.valid
    assert any("state mutation" in error for error in result.errors)


def test_assert_helper_raises_with_combined_error_message() -> None:
    packet = _valid_packet()
    packet["owner"] = ""
    packet["claims"] = ["live crawl promoted"]

    with pytest.raises(ValueError) as exc_info:
        assert_valid_combined_promotion_dependency_packet_v1(packet)

    message = str(exc_info.value)
    assert "owner" in message
    assert "live" in message or "promotion" in message
