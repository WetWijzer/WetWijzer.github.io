from __future__ import annotations

import pytest

from ppd.validation.post_activation_smoke_packet_v2 import validate_packet


def valid_packet() -> dict[str, object]:
    return {
        "packet_version": 2,
        "smoke_cases": [
            {"name": "user-gap"},
            {"name": "guarded-action"},
            {"name": "draft-preview"},
            {"name": "stale-source-hold"},
            {"name": "refused-consequential-action"},
        ],
        "expected_citations": ["official PP&D public page citation"],
        "validation_commands": [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
        "artifacts": ["ppd/tests/fixtures/post_activation_smoke_packet_v2/public_fixture.json"],
        "claims": {
            "live_devhub_execution_claim": False,
            "official_action_completion_claim": False,
            "legal_or_permitting_guarantee": False,
        },
        "mutation_flags": {
            "prompt_mutated": False,
            "guardrail_mutated": False,
            "source_mutated": False,
            "requirement_mutated": False,
            "process_model_mutated": False,
            "contract_mutated": False,
            "devhub_surface_mutated": False,
            "release_state_mutated": False,
        },
    }


def test_accepts_complete_public_packet() -> None:
    result = validate_packet(valid_packet())
    assert result.ok, result.errors


@pytest.mark.parametrize(
    "case_name",
    [
        "user-gap",
        "guarded-action",
        "draft-preview",
        "stale-source-hold",
        "refused-consequential-action",
    ],
)
def test_rejects_missing_required_smoke_case(case_name: str) -> None:
    packet = valid_packet()
    packet["smoke_cases"] = [
        case for case in packet["smoke_cases"] if case["name"] != case_name  # type: ignore[index]
    ]

    result = validate_packet(packet)

    assert not result.ok
    assert f"missing smoke case: {case_name}" in result.errors


@pytest.mark.parametrize(
    "field, message",
    [
        ("expected_citations", "missing expected citations"),
        ("validation_commands", "missing validation commands"),
    ],
)
def test_rejects_missing_packet_evidence(field: str, message: str) -> None:
    packet = valid_packet()
    packet[field] = []

    result = validate_packet(packet)

    assert not result.ok
    assert message in result.errors


@pytest.mark.parametrize(
    "artifact_token",
    ["private", "session", "browser", "raw", "downloaded"],
)
def test_rejects_prohibited_artifact_references(artifact_token: str) -> None:
    packet = valid_packet()
    packet["artifacts"] = [{"path": f"ppd/tests/fixtures/{artifact_token}_artifact.json"}]

    result = validate_packet(packet)

    assert not result.ok
    assert f"prohibited artifact reference: {artifact_token}" in result.errors


@pytest.mark.parametrize(
    "claim_field",
    [
        "live_devhub_execution_claim",
        "official_action_completion_claim",
        "legal_or_permitting_guarantee",
    ],
)
def test_rejects_prohibited_claims(claim_field: str) -> None:
    packet = valid_packet()
    claims = dict(packet["claims"])  # type: ignore[arg-type]
    claims[claim_field] = True
    packet["claims"] = claims

    result = validate_packet(packet)

    assert not result.ok
    assert f"prohibited claim: {claim_field}" in result.errors


@pytest.mark.parametrize(
    "flag",
    [
        "prompt_mutated",
        "guardrail_mutated",
        "source_mutated",
        "requirement_mutated",
        "process_model_mutated",
        "contract_mutated",
        "devhub_surface_mutated",
        "release_state_mutated",
    ],
)
def test_rejects_active_mutation_flags(flag: str) -> None:
    packet = valid_packet()
    flags = dict(packet["mutation_flags"])  # type: ignore[arg-type]
    flags[flag] = True
    packet["mutation_flags"] = flags

    result = validate_packet(packet)

    assert not result.ok
    assert f"prohibited mutation flag: {flag}" in result.errors
