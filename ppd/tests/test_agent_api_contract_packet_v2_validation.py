from __future__ import annotations

import pytest

from ppd.contracts.agent_api_contract_packet_v2_validation import (
    assert_valid_agent_api_contract_packet_v2,
    validate_agent_api_contract_packet_v2,
)


def _valid_packet() -> dict[str, object]:
    return {
        "version": 2,
        "synthetic_request_examples": ["synthetic request only; no live DevHub access"],
        "response_examples": ["response cites supplied fixture evidence only"],
        "citation_requirements": ["cite fixture path and excerpt id for every claim"],
        "stale_or_conflicting_evidence_response": "refuse certainty and request refreshed official evidence",
        "refused_consequential_action_response": "refuse submissions, payments, certifications, uploads, and scheduling",
        "reversible_draft_preview_references": ["draft preview must be reversible and labeled non-official"],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "active_prompt_mutation": False,
        "active_guardrail_mutation": False,
        "active_source_mutation": False,
        "active_requirement_mutation": False,
        "active_process_model_mutation": False,
        "active_contract_mutation": False,
        "active_devhub_surface_mutation": False,
        "active_release_state_mutation": False,
    }


def test_valid_packet_has_no_errors() -> None:
    assert validate_agent_api_contract_packet_v2(_valid_packet()) == []
    assert_valid_agent_api_contract_packet_v2(_valid_packet())


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("synthetic_request_examples", "missing synthetic request examples"),
        ("response_examples", "missing response examples"),
        ("citation_requirements", "missing citation requirements"),
        ("reversible_draft_preview_references", "missing reversible draft preview references"),
        ("validation_commands", "missing validation commands"),
        ("stale_or_conflicting_evidence_response", "missing stale or conflicting evidence responses"),
        ("refused_consequential_action_response", "missing refused consequential-action responses"),
    ],
)
def test_rejects_missing_required_contract_sections(field: str, message: str) -> None:
    packet = _valid_packet()
    packet.pop(field)

    assert message in validate_agent_api_contract_packet_v2(packet)


@pytest.mark.parametrize(
    "text",
    [
        "includes private/session browser artifacts",
        "contains auth_state for DevHub",
        "stores raw crawl output",
        "references a downloaded document",
        "queried DevHub live for this answer",
        "permit submitted successfully",
        "this guarantees approval",
    ],
)
def test_rejects_forbidden_artifacts_and_claims(text: str) -> None:
    packet = _valid_packet()
    packet["response_examples"] = [text]

    assert validate_agent_api_contract_packet_v2(packet)


@pytest.mark.parametrize(
    "field",
    [
        "active_prompt_mutation",
        "active_guardrail_mutation",
        "active_source_mutation",
        "active_requirement_mutation",
        "active_process_model_mutation",
        "active_contract_mutation",
        "active_devhub_surface_mutation",
        "active_release_state_mutation",
    ],
)
def test_rejects_active_mutation_flags(field: str) -> None:
    packet = _valid_packet()
    packet[field] = True

    assert f"{field} must not be active" in validate_agent_api_contract_packet_v2(packet)


def test_rejects_malformed_validation_commands() -> None:
    packet = _valid_packet()
    packet["validation_commands"] = ["python3 ppd/daemon/ppd_daemon.py --self-test"]

    assert "validation command 0 must be a non-empty list of strings" in validate_agent_api_contract_packet_v2(packet)


def test_assert_helper_raises_on_invalid_packet() -> None:
    packet = _valid_packet()
    packet["version"] = 1

    with pytest.raises(ValueError, match="packet version must be 2"):
        assert_valid_agent_api_contract_packet_v2(packet)
