"""Validation for PP&D agent API smoke rehearsal packet v1.

The smoke rehearsal packet is a committed, deterministic fixture used to prove
that an agent-facing API can explain safe behavior before any live crawl,
authenticated DevHub session, mutation, or consequential official action.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PRIVATE_ARTIFACT_TOKENS = (
    "auth_state",
    "browser_state",
    "cookie",
    "cookies",
    "credential",
    "download",
    "downloaded",
    "har",
    "local_private_path",
    "raw_body",
    "raw_crawl",
    "screenshot",
    "session",
    "storage_state",
    "trace",
)

PRIVATE_PATH_TOKENS = (
    "/downloads/",
    "/private/",
    "/sessions/",
    "/tmp/",
    "\\downloads\\",
    "\\private\\",
    "\\sessions\\",
    "\\tmp\\",
)

OFFICIAL_COMPLETION_CLAIMS = (
    "application submitted",
    "certification completed",
    "fee paid",
    "inspection scheduled",
    "official action completed",
    "permit approved",
    "permit issued",
    "submitted to devhub",
    "upload completed",
)

LIVE_OR_DEVHUB_CLAIMS = (
    "authenticated devhub",
    "devhub login completed",
    "devhub session",
    "live crawl completed",
    "live crawl ran",
    "live devhub",
    "production crawl",
)

LEGAL_OR_PERMITTING_GUARANTEES = (
    "approval is guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "legal advice",
    "permit will be approved",
    "will be issued",
)

ACTIVE_MUTATION_KEYS = (
    "active_mutation",
    "allow_mutation",
    "mutation_enabled",
    "perform_mutation",
    "write_enabled",
)


@dataclass(frozen=True)
class PacketValidationResult:
    """Result returned by the packet validator."""

    valid: bool
    errors: tuple[str, ...]


def validate_agent_api_smoke_rehearsal_packet_v1(packet: dict[str, Any]) -> PacketValidationResult:
    """Validate a PP&D agent API smoke rehearsal packet v1 fixture.

    The validator is intentionally schema-light and policy-heavy. It accepts
    ordinary JSON dictionaries while enforcing the safety coverage required by
    the PP&D plan.
    """

    errors: list[str] = []

    if packet.get("packet_version") != "agent_api_smoke_rehearsal_packet_v1":
        errors.append("packet_version must be agent_api_smoke_rehearsal_packet_v1")

    scenario_ids = _scenario_ids(packet.get("scenarios"))
    if not scenario_ids:
        errors.append("packet must include scenario coverage")

    expected_rows = _rows(packet, "expected_response_rows")
    if not expected_rows:
        errors.append("packet must include expected response rows")

    citation_refs = packet.get("citation_references")
    if not isinstance(citation_refs, dict) or not citation_refs:
        errors.append("packet must include citation references")
    else:
        _validate_citations(expected_rows, citation_refs, errors)

    if not _rows(packet, "stale_source_holds"):
        errors.append("packet must include stale-source holds")

    if not _rows(packet, "exact_confirmation_gates"):
        errors.append("packet must include exact-confirmation gates")

    if not _rows(packet, "refusal_rows"):
        errors.append("packet must include refusal rows")

    if not _valid_validation_commands(packet.get("validation_commands")):
        errors.append("packet must include validation commands as non-empty string argv rows")

    for path, value in _walk(packet):
        lowered_path = ".".join(path).lower()
        if any(token in lowered_path for token in PRIVATE_ARTIFACT_TOKENS):
            errors.append(f"private/session/browser/raw/downloaded artifact field is not allowed: {'.'.join(path)}")

        if isinstance(value, str):
            lowered_value = value.lower()
            if any(token in lowered_value for token in PRIVATE_PATH_TOKENS):
                errors.append(f"private/session/browser/raw/downloaded artifact path is not allowed: {'.'.join(path)}")
            if any(claim in lowered_value for claim in OFFICIAL_COMPLETION_CLAIMS):
                errors.append(f"official-action completion claim is not allowed: {'.'.join(path)}")
            if any(claim in lowered_value for claim in LIVE_OR_DEVHUB_CLAIMS):
                errors.append(f"live crawl or DevHub claim is not allowed: {'.'.join(path)}")
            if any(claim in lowered_value for claim in LEGAL_OR_PERMITTING_GUARANTEES):
                errors.append(f"legal or permitting guarantee is not allowed: {'.'.join(path)}")

        if path and path[-1].lower() in ACTIVE_MUTATION_KEYS and value is True:
            errors.append(f"active mutation flag must not be true: {'.'.join(path)}")

    return PacketValidationResult(valid=not errors, errors=tuple(dict.fromkeys(errors)))


def assert_agent_api_smoke_rehearsal_packet_v1(packet: dict[str, Any]) -> None:
    """Raise ValueError if a packet fails validation."""

    result = validate_agent_api_smoke_rehearsal_packet_v1(packet)
    if not result.valid:
        raise ValueError("; ".join(result.errors))


def _rows(packet: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = packet.get(key)
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict) and row]


def _scenario_ids(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    ids: set[str] = set()
    for row in value:
        if isinstance(row, dict) and isinstance(row.get("scenario_id"), str) and row["scenario_id"].strip():
            ids.add(row["scenario_id"])
    return ids


def _validate_citations(
    expected_rows: list[dict[str, Any]],
    citation_refs: dict[str, Any],
    errors: list[str],
) -> None:
    for index, row in enumerate(expected_rows):
        citations = row.get("citations")
        if not isinstance(citations, list) or not citations:
            errors.append(f"expected response row {index} must cite at least one reference")
            continue
        for citation in citations:
            if not isinstance(citation, str) or citation not in citation_refs:
                errors.append(f"expected response row {index} cites an unknown reference: {citation!r}")

    for ref_id, ref in citation_refs.items():
        if not isinstance(ref_id, str) or not ref_id.strip():
            errors.append("citation reference ids must be non-empty strings")
            continue
        if not isinstance(ref, dict):
            errors.append(f"citation reference {ref_id} must be an object")
            continue
        url = ref.get("url")
        if not isinstance(url, str) or not url.startswith("https://www.portland.gov/ppd"):
            errors.append(f"citation reference {ref_id} must use an official PP&D https URL")


def _valid_validation_commands(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for command in value:
        if not isinstance(command, list) or not command:
            return False
        if not all(isinstance(part, str) and part for part in command):
            return False
    return True


def _walk(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    rows: list[tuple[tuple[str, ...], Any]] = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            rows.extend(_walk(child, path + (str(key),)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_walk(child, path + (str(index),)))
    return rows
