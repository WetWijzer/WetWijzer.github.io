"""Validator for agent-facing post-activation smoke test packet v2."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

REQUIRED_SMOKE_CASES = frozenset(
    {
        "user-gap",
        "guarded-action",
        "draft-preview",
        "stale-source-hold",
        "refused-consequential-action",
    }
)

PROHIBITED_ARTIFACT_TOKENS = (
    "private",
    "session",
    "browser",
    "raw",
    "downloaded",
)

PROHIBITED_CLAIM_FIELDS = (
    "live_devhub_execution_claim",
    "official_action_completion_claim",
    "legal_or_permitting_guarantee",
)

PROHIBITED_MUTATION_FLAGS = (
    "prompt_mutated",
    "guardrail_mutated",
    "source_mutated",
    "requirement_mutated",
    "process_model_mutated",
    "contract_mutated",
    "devhub_surface_mutated",
    "release_state_mutated",
)


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def validate_packet(packet: Mapping[str, Any]) -> ValidationResult:
    errors: list[str] = []

    version = packet.get("packet_version")
    if version != 2:
        errors.append("packet_version must be 2")

    cases = packet.get("smoke_cases")
    if not isinstance(cases, Sequence) or isinstance(cases, (str, bytes)):
        errors.append("smoke_cases must be a list")
        case_names: set[str] = set()
    else:
        case_names = {
            str(case.get("name"))
            for case in cases
            if isinstance(case, Mapping) and case.get("name") is not None
        }
    missing_cases = sorted(REQUIRED_SMOKE_CASES - case_names)
    for case_name in missing_cases:
        errors.append(f"missing smoke case: {case_name}")

    expected_citations = packet.get("expected_citations")
    if not _non_empty_sequence(expected_citations):
        errors.append("missing expected citations")

    validation_commands = packet.get("validation_commands")
    if not _non_empty_sequence(validation_commands):
        errors.append("missing validation commands")

    artifacts = packet.get("artifacts", [])
    if artifacts is None:
        artifacts = []
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
        errors.append("artifacts must be a list when present")
    else:
        for artifact in artifacts:
            text = _artifact_text(artifact)
            lowered = text.lower()
            for token in PROHIBITED_ARTIFACT_TOKENS:
                if token in lowered:
                    errors.append(f"prohibited artifact reference: {token}")
                    break

    claims = packet.get("claims", {})
    if claims is None:
        claims = {}
    if not isinstance(claims, Mapping):
        errors.append("claims must be an object when present")
    else:
        for field in PROHIBITED_CLAIM_FIELDS:
            if bool(claims.get(field)):
                errors.append(f"prohibited claim: {field}")

    mutation_flags = packet.get("mutation_flags", {})
    if mutation_flags is None:
        mutation_flags = {}
    if not isinstance(mutation_flags, Mapping):
        errors.append("mutation_flags must be an object when present")
    else:
        for field in PROHIBITED_MUTATION_FLAGS:
            if bool(mutation_flags.get(field)):
                errors.append(f"prohibited mutation flag: {field}")

    return ValidationResult(ok=not errors, errors=tuple(errors))


def require_valid_packet(packet: Mapping[str, Any]) -> None:
    result = validate_packet(packet)
    if not result.ok:
        raise ValueError("; ".join(result.errors))


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) > 0


def _artifact_text(artifact: Any) -> str:
    if isinstance(artifact, Mapping):
        return " ".join(str(value) for value in artifact.values())
    return str(artifact)
