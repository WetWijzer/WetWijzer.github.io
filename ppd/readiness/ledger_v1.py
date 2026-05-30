"""Fixture-first PP&D readiness ledger v1.

The ledger deliberately reads committed fixtures only. It does not crawl public
sources, open DevHub, persist browser state, or perform official actions.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

REQUIRED_TOPICS = {
    "public_source_freshness",
    "requirement_traceability",
    "guardrail_explanations",
    "reversible_draft_preview",
    "devhub_read_only_observation",
    "action_journal_safety",
    "agent_response_safety",
}

ATTESTATION_KEYS = {
    "no_live_crawl",
    "no_devhub_session",
    "no_private_artifact",
    "no_official_action",
}


@dataclass(frozen=True)
class ReadinessRow:
    """A cited readiness row assembled from fixture packets and validators."""

    row_id: str
    topic: str
    status: str
    owner: str
    evidence_ids: tuple[str, ...]
    citation_urls: tuple[str, ...]
    fixture_packet_ids: tuple[str, ...]
    validator_ids: tuple[str, ...]
    manual_review_blockers: tuple[str, ...]
    offline_validation_commands: tuple[tuple[str, ...], ...]
    attestations: dict[str, bool]


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _load_bundle(fixture_dir: Path) -> dict[str, Any]:
    bundle_path = fixture_dir / "readiness_ledger_v1.json"
    if not bundle_path.exists():
        raise FileNotFoundError(f"missing readiness fixture bundle: {bundle_path}")
    return _read_json(bundle_path)


def _latest_packets(source_packets: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for packet in source_packets:
        source_id = str(packet.get("source_id", ""))
        if not source_id:
            raise ValueError("source packet missing source_id")
        previous = latest.get(source_id)
        if previous is None or str(packet.get("capture_verified_at", "")) > str(previous.get("capture_verified_at", "")):
            latest[source_id] = packet
    return latest


def build_readiness_rows(fixture_dir: Path) -> list[ReadinessRow]:
    """Build readiness rows from committed fixture packets.

    Args:
        fixture_dir: Directory containing readiness_ledger_v1.json.

    Returns:
        Validated readiness rows sorted by row_id.
    """

    bundle = _load_bundle(fixture_dir)
    latest_by_source = _latest_packets(bundle.get("source_packets", []))
    packets_by_evidence = {
        str(packet["evidence_id"]): packet for packet in latest_by_source.values()
    }
    validators_by_id = {
        str(validator["validator_id"]): validator for validator in bundle.get("validators", [])
    }

    rows: list[ReadinessRow] = []
    for raw_row in bundle.get("readiness_rows", []):
        evidence_ids = tuple(str(item) for item in raw_row.get("evidence_ids", []))
        validator_ids = tuple(str(item) for item in raw_row.get("validator_ids", []))
        missing_evidence = [item for item in evidence_ids if item not in packets_by_evidence]
        missing_validators = [item for item in validator_ids if item not in validators_by_id]
        if missing_evidence:
            raise ValueError(f"{raw_row.get('row_id')} references unknown evidence ids: {missing_evidence}")
        if missing_validators:
            raise ValueError(f"{raw_row.get('row_id')} references unknown validator ids: {missing_validators}")

        citation_urls = tuple(str(packets_by_evidence[item]["canonical_url"]) for item in evidence_ids)
        fixture_packet_ids = tuple(str(packets_by_evidence[item]["fixture_packet_id"]) for item in evidence_ids)
        commands = tuple(
            tuple(str(part) for part in validators_by_id[item]["offline_command"])
            for item in validator_ids
        )
        rows.append(
            ReadinessRow(
                row_id=str(raw_row["row_id"]),
                topic=str(raw_row["topic"]),
                status=str(raw_row["status"]),
                owner=str(raw_row["owner"]),
                evidence_ids=evidence_ids,
                citation_urls=citation_urls,
                fixture_packet_ids=fixture_packet_ids,
                validator_ids=validator_ids,
                manual_review_blockers=tuple(str(item) for item in raw_row.get("manual_review_blockers", [])),
                offline_validation_commands=commands,
                attestations={str(key): bool(value) for key, value in raw_row.get("attestations", {}).items()},
            )
        )

    rows.sort(key=lambda row: row.row_id)
    validate_readiness_rows(rows)
    return rows


def validate_readiness_rows(rows: Iterable[ReadinessRow]) -> None:
    """Validate ledger completeness and safety attestations."""

    materialized = list(rows)
    topics = {row.topic for row in materialized}
    missing_topics = REQUIRED_TOPICS - topics
    if missing_topics:
        raise ValueError(f"readiness ledger missing topics: {sorted(missing_topics)}")

    row_ids: set[str] = set()
    for row in materialized:
        if row.row_id in row_ids:
            raise ValueError(f"duplicate readiness row id: {row.row_id}")
        row_ids.add(row.row_id)
        if row.topic not in REQUIRED_TOPICS:
            raise ValueError(f"unexpected readiness topic for {row.row_id}: {row.topic}")
        if row.status not in {"ready_with_blockers", "blocked_manual_review"}:
            raise ValueError(f"unexpected readiness status for {row.row_id}: {row.status}")
        if not row.owner:
            raise ValueError(f"{row.row_id} missing owner")
        if not row.evidence_ids or not row.citation_urls or not row.fixture_packet_ids:
            raise ValueError(f"{row.row_id} must cite fixture evidence")
        if not row.validator_ids or not row.offline_validation_commands:
            raise ValueError(f"{row.row_id} must cite offline validators")
        if not row.manual_review_blockers:
            raise ValueError(f"{row.row_id} must list remaining manual-review blockers")
        if set(row.attestations) != ATTESTATION_KEYS:
            raise ValueError(f"{row.row_id} has incomplete attestations")
        failed_attestations = [key for key, value in row.attestations.items() if not value]
        if failed_attestations:
            raise ValueError(f"{row.row_id} failed attestations: {failed_attestations}")
