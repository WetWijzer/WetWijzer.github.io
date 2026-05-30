"""Fixture-first source freshness drift triage v2 packet builder.

This module intentionally consumes committed metadata fixtures only. It does not crawl,
call processors, read registries, or mutate requirement/guardrail records.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

DRIFT_TRIAGE_PACKET_VERSION = "source_freshness_drift_triage_v2"
REQUIRED_ATTESTATIONS = {
    "no_live_crawl": True,
    "no_processor_invocation": True,
    "no_registry_mutation": True,
    "no_requirement_mutation": True,
    "no_guardrail_mutation": True,
}
DEFAULT_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/extraction/source_freshness_drift_triage_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_source_freshness_drift_triage_v2.py"],
]


@dataclass(frozen=True)
class SourceClassification:
    source_id: str
    canonical_url: str
    classification: str
    reason: str
    citations: list[dict[str, Any]]
    affected_requirement_ids: list[str]
    affected_process_ids: list[str]
    affected_guardrail_ids: list[str]
    escalation_owner: str
    offline_validation_commands: list[list[str]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "canonical_url": self.canonical_url,
            "classification": self.classification,
            "reason": self.reason,
            "citations": self.citations,
            "affected_requirement_ids": self.affected_requirement_ids,
            "affected_process_ids": self.affected_process_ids,
            "affected_guardrail_ids": self.affected_guardrail_ids,
            "escalation_owner": self.escalation_owner,
            "offline_validation_commands": self.offline_validation_commands,
        }


def build_source_freshness_drift_triage_v2(intake: dict[str, Any]) -> dict[str, Any]:
    """Build a cited changed/unchanged/stale triage packet from fixture data."""
    recrawl_sources = _index_by_source_id(
        intake.get("public_recrawl_post_run_metadata_intake_v2", {}).get("sources", [])
    )
    badge_packets = _index_by_source_id(intake.get("source_freshness_badge_packets", []))
    watchlist_packets = _watchlist_by_source_id(
        intake.get("evidence_freshness_watchlist_packets", [])
    )

    source_ids = sorted(set(recrawl_sources) | set(badge_packets) | set(watchlist_packets))
    classifications = [
        _classify_source(
            source_id,
            recrawl_sources.get(source_id, {}),
            badge_packets.get(source_id, {}),
            watchlist_packets.get(source_id, []),
        ).as_dict()
        for source_id in source_ids
    ]

    return {
        "packet_type": DRIFT_TRIAGE_PACKET_VERSION,
        "packet_id": intake.get("packet_id", "source-freshness-drift-triage-v2-fixture"),
        "generated_from": {
            "public_recrawl_post_run_metadata_intake_v2": intake.get(
                "public_recrawl_post_run_metadata_intake_v2", {}
            ).get("run_id"),
            "source_freshness_badge_packet_ids": sorted(
                packet.get("packet_id", "")
                for packet in intake.get("source_freshness_badge_packets", [])
                if packet.get("packet_id")
            ),
            "evidence_freshness_watchlist_packet_ids": sorted(
                packet.get("packet_id", "")
                for packet in intake.get("evidence_freshness_watchlist_packets", [])
                if packet.get("packet_id")
            ),
        },
        "classifications": classifications,
        "totals": _totals(classifications),
        "attestations": deepcopy(REQUIRED_ATTESTATIONS),
        "offline_validation_commands": deepcopy(DEFAULT_VALIDATION_COMMANDS),
    }


def _classify_source(
    source_id: str,
    recrawl: dict[str, Any],
    badge: dict[str, Any],
    watchlist_entries: list[dict[str, Any]],
) -> SourceClassification:
    canonical_url = _first_text(
        recrawl.get("canonical_url"),
        badge.get("canonical_url"),
        *(entry.get("canonical_url") for entry in watchlist_entries),
    )
    citations = _citations(recrawl, badge, watchlist_entries)
    affected_requirement_ids = _sorted_unique(
        recrawl.get("affected_requirement_ids", []),
        badge.get("affected_requirement_ids", []),
        *(entry.get("affected_requirement_ids", []) for entry in watchlist_entries),
    )
    affected_process_ids = _sorted_unique(
        recrawl.get("affected_process_ids", []),
        badge.get("affected_process_ids", []),
        *(entry.get("affected_process_ids", []) for entry in watchlist_entries),
    )
    affected_guardrail_ids = _sorted_unique(
        recrawl.get("affected_guardrail_ids", []),
        badge.get("affected_guardrail_ids", []),
        *(entry.get("affected_guardrail_ids", []) for entry in watchlist_entries),
    )
    escalation_owner = _escalation_owner(badge, watchlist_entries)
    classification, reason = _classification_and_reason(recrawl, badge, watchlist_entries)

    return SourceClassification(
        source_id=source_id,
        canonical_url=canonical_url,
        classification=classification,
        reason=reason,
        citations=citations,
        affected_requirement_ids=affected_requirement_ids,
        affected_process_ids=affected_process_ids,
        affected_guardrail_ids=affected_guardrail_ids,
        escalation_owner=escalation_owner,
        offline_validation_commands=deepcopy(DEFAULT_VALIDATION_COMMANDS),
    )


def _classification_and_reason(
    recrawl: dict[str, Any],
    badge: dict[str, Any],
    watchlist_entries: list[dict[str, Any]],
) -> tuple[str, str]:
    badge_status = str(badge.get("freshness_status", "")).lower()
    watchlist_statuses = {str(entry.get("watch_status", "")).lower() for entry in watchlist_entries}
    skipped_reason = str(recrawl.get("skipped_reason", "")).strip()
    before_hash = recrawl.get("content_hash_before")
    after_hash = recrawl.get("content_hash_after")
    http_status = recrawl.get("http_status")

    if badge_status == "stale" or "stale" in watchlist_statuses:
        return "stale", "Badge or evidence watchlist marked the source stale."
    if skipped_reason:
        return "stale", f"Recrawl metadata skipped the source: {skipped_reason}."
    if isinstance(http_status, int) and http_status >= 400:
        return "stale", f"Recrawl metadata returned HTTP {http_status}."
    if before_hash and after_hash and before_hash != after_hash:
        return "changed", "Recrawl metadata content hash changed."
    if badge_status in {"fresh", "current"} and before_hash == after_hash:
        return "unchanged", "Freshness badge is current and recrawl hash is unchanged."
    if before_hash == after_hash and before_hash:
        return "unchanged", "Recrawl hash is unchanged."
    return "stale", "Insufficient fixture metadata to prove the source is current."


def _index_by_source_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        source_id = item.get("source_id")
        if source_id:
            indexed[str(source_id)] = item
    return indexed


def _watchlist_by_source_id(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    indexed: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        source_id = item.get("source_id")
        if source_id:
            indexed[str(source_id)].append(item)
    return dict(indexed)


def _citations(
    recrawl: dict[str, Any],
    badge: dict[str, Any],
    watchlist_entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for source, item in (
        ("public_recrawl_post_run_metadata_intake_v2", recrawl),
        ("source_freshness_badge_packet", badge),
    ):
        citation = item.get("citation")
        if citation:
            cited = dict(citation)
            cited.setdefault("packet_source", source)
            citations.append(cited)
    for entry in watchlist_entries:
        citation = entry.get("citation")
        if citation:
            cited = dict(citation)
            cited.setdefault("packet_source", "evidence_freshness_watchlist_packet")
            citations.append(cited)
    return citations


def _escalation_owner(
    badge: dict[str, Any], watchlist_entries: list[dict[str, Any]]
) -> str:
    owner = badge.get("escalation_owner") or badge.get("owner")
    if owner:
        return str(owner)
    for entry in watchlist_entries:
        owner = entry.get("escalation_owner") or entry.get("owner")
        if owner:
            return str(owner)
    return "ppd-source-freshness-maintainer"


def _sorted_unique(*groups: list[Any]) -> list[str]:
    values: set[str] = set()
    for group in groups:
        for value in group or []:
            if value:
                values.add(str(value))
    return sorted(values)


def _first_text(*values: Any) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def _totals(classifications: list[dict[str, Any]]) -> dict[str, int]:
    totals = {"changed": 0, "unchanged": 0, "stale": 0}
    for item in classifications:
        classification = item.get("classification")
        if classification in totals:
            totals[classification] += 1
    totals["total_sources"] = len(classifications)
    return totals
