from copy import deepcopy
from pathlib import Path

import pytest

from ppd.agent_readiness_expectation_packet_v4 import (
    EXAMPLE_KINDS,
    REQUIRED_ATTESTATIONS,
    build_expectation_packet,
    validate_expectation_packet,
)


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "agent_readiness_packet_v4"


def test_builds_valid_fixture_first_packet_v4() -> None:
    packet = build_expectation_packet(FIXTURE_ROOT)

    validate_expectation_packet(packet)

    assert packet["packet_id"] == "agent-readiness-api-schema-expectation-packet-v4"
    assert set(packet["examples"][index]["kind"] for index in range(len(packet["examples"]))) == set(EXAMPLE_KINDS)
    assert all(packet["attestations"][name] is True for name in REQUIRED_ATTESTATIONS)


def test_examples_are_cited_and_offline_only() -> None:
    packet = build_expectation_packet(FIXTURE_ROOT)
    consumed = set(packet["consumes"].values())

    for example in packet["examples"]:
        response = example["response"]
        assert response["citations"]
        assert set(response["citations"]).issubset(consumed)
        assert set(response["process_refs"]).issubset(consumed)
        assert set(response["gap_refs"]).issubset(consumed)
        assert set(response["guardrail_refs"]).issubset(consumed)
        assert response["attestations"] == packet["attestations"]
        assert "DevHub" not in response["message"]


def test_blocks_official_mutation_actions() -> None:
    packet = build_expectation_packet(FIXTURE_ROOT)
    blocked = next(example for example in packet["examples"] if example["kind"] == "blocked_action_explanation")

    assert blocked["request"]["requested_action"] == "submit_application"
    assert blocked["response"]["ready"] is False
    assert "official action" in blocked["response"]["message"]
    assert "offer_read_only_summary" in blocked["response"]["safe_next_actions"]


@pytest.mark.parametrize(
    ("mutator", "expected_problem"),
    [
        (
            lambda packet: packet["examples"][0]["response"].__setitem__("citations", []),
            "example lacks citations",
        ),
        (
            lambda packet: packet["examples"][0]["response"].pop("process_refs"),
            "missing process_refs",
        ),
        (
            lambda packet: packet["examples"][0]["response"].pop("gap_refs"),
            "missing gap_refs",
        ),
        (
            lambda packet: packet["examples"][0]["response"].pop("guardrail_refs"),
            "missing guardrail_refs",
        ),
        (
            lambda packet: packet["examples"][0]["response"].__setitem__("safe_next_action_classes", ["submit_application"]),
            "unsupported next-action classes",
        ),
        (
            lambda packet: packet["examples"][0].__setitem__("private_user_fact", "Jane Applicant lives at 123 Private St"),
            "private user fact or value is not allowed",
        ),
        (
            lambda packet: packet["examples"][0].__setitem__("authenticated_devhub_value", "fixture must not include account-scoped values"),
            "authenticated DevHub value is not allowed",
        ),
        (
            lambda packet: packet["examples"][0].__setitem__("raw_document", "raw downloaded PDF text"),
            "raw document/session/browser artifact is not allowed",
        ),
        (
            lambda packet: packet["examples"][0]["response"].__setitem__("message", "DevHub completed the uploaded correction."),
            "live LLM or DevHub completion claim is not allowed",
        ),
        (
            lambda packet: packet["examples"][0]["response"].__setitem__("message", "This permit will be approved."),
            "legal or permitting outcome guarantee is not allowed",
        ),
        (
            lambda packet: packet["examples"][0]["response"].__setitem__("message", "I submitted the application."),
            "final submission/payment/upload/scheduling/cancellation language is not allowed",
        ),
        (
            lambda packet: packet["examples"][0].__setitem__("prompt_mutation_enabled", True),
            "active mutation flag is not allowed",
        ),
        (
            lambda packet: packet["examples"][0].__setitem__("guardrail_mutation", True),
            "active mutation flag is not allowed",
        ),
        (
            lambda packet: packet["examples"][0].__setitem__("source_mutation_enabled", True),
            "active mutation flag is not allowed",
        ),
        (
            lambda packet: packet["examples"][0].__setitem__("surface_registry_mutation", True),
            "active mutation flag is not allowed",
        ),
        (
            lambda packet: packet["examples"][0].__setitem__("release_state_mutation", True),
            "active mutation flag is not allowed",
        ),
        (
            lambda packet: packet["examples"][0].__setitem__("agent_state_mutation", True),
            "active mutation flag is not allowed",
        ),
    ],
)
def test_validation_rejects_unsafe_response_example_content(mutator, expected_problem: str) -> None:
    packet = build_expectation_packet(FIXTURE_ROOT)
    invalid_packet = deepcopy(packet)
    mutator(invalid_packet)

    with pytest.raises(ValueError, match=expected_problem):
        validate_expectation_packet(invalid_packet)
