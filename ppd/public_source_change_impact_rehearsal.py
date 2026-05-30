"""Fixture-first public source change impact rehearsal v1.

This module intentionally works from committed fixtures only. It does not crawl,
download, persist raw response bodies, or mutate any active registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

REQUIRED_ATTESTATIONS = {
    "no_live_crawl": True,
    "no_download": True,
    "no_raw_body": True,
    "no_active_registry_mutation": True,
}


@dataclass(frozen=True)
class ChangeImpactRow:
    """A cited hypothetical public-source change impact row."""

    change_id: str
    affected_source_ids: tuple[str, ...]
    document_sections: tuple[str, ...]
    requirement_ids: tuple[str, ...]
    process_stages: tuple[str, ...]
    guardrail_bundle_ids: tuple[str, ...]
    reviewer_owner: str
    reviewer_backup_owner: str
    rollback_notes: str
    offline_validation_commands: tuple[tuple[str, ...], ...]
    citations: tuple[str, ...]
    attestations: Mapping[str, bool]

    def as_dict(self) -> dict[str, Any]:
        return {
            "change_id": self.change_id,
            "affected_source_ids": list(self.affected_source_ids),
            "document_sections": list(self.document_sections),
            "requirement_ids": list(self.requirement_ids),
            "process_stages": list(self.process_stages),
            "guardrail_bundle_ids": list(self.guardrail_bundle_ids),
            "reviewer_owner": self.reviewer_owner,
            "reviewer_backup_owner": self.reviewer_backup_owner,
            "rollback_notes": self.rollback_notes,
            "offline_validation_commands": [list(command) for command in self.offline_validation_commands],
            "citations": list(self.citations),
            "attestations": dict(self.attestations),
        }


def build_change_impact_rows(
    traceability_packet: Mapping[str, Any],
    freshness_handoff: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Build deterministic cited hypothetical impact rows from fixture packets."""

    trace_sources = traceability_packet.get("sources", [])
    reviewer_by_source = {
        item["source_id"]: item for item in freshness_handoff.get("reviewer_handoff", [])
    }

    rows: list[ChangeImpactRow] = []
    for index, source in enumerate(trace_sources, start=1):
        source_id = source["source_id"]
        reviewer = reviewer_by_source.get(source_id, {})
        row = ChangeImpactRow(
            change_id=f"hypothetical-public-source-change-{index:03d}",
            affected_source_ids=(source_id,),
            document_sections=tuple(source.get("document_sections", [])),
            requirement_ids=tuple(source.get("requirement_ids", [])),
            process_stages=tuple(source.get("process_stages", [])),
            guardrail_bundle_ids=tuple(source.get("guardrail_bundle_ids", [])),
            reviewer_owner=str(reviewer.get("reviewer_owner", "unassigned")),
            reviewer_backup_owner=str(reviewer.get("reviewer_backup_owner", "unassigned")),
            rollback_notes=str(reviewer.get("rollback_notes", "Discard fixture-only rehearsal output and keep current registry unchanged.")),
            offline_validation_commands=(
                ("python3", "-m", "py_compile", "ppd/public_source_change_impact_rehearsal.py"),
                ("python3", "-m", "pytest", "ppd/tests/test_public_source_change_impact_rehearsal.py"),
            ),
            citations=tuple(source.get("citations", [])) + tuple(reviewer.get("citations", [])),
            attestations=REQUIRED_ATTESTATIONS,
        )
        rows.append(row)

    return [row.as_dict() for row in rows]


def validate_change_impact_rows(rows: list[Mapping[str, Any]]) -> None:
    """Validate the narrow v1 row contract used by tests and daemon proposals."""

    required_fields = {
        "change_id",
        "affected_source_ids",
        "document_sections",
        "requirement_ids",
        "process_stages",
        "guardrail_bundle_ids",
        "reviewer_owner",
        "reviewer_backup_owner",
        "rollback_notes",
        "offline_validation_commands",
        "citations",
        "attestations",
    }
    for row in rows:
        missing = sorted(required_fields.difference(row))
        if missing:
            raise ValueError(f"change impact row is missing required fields: {missing}")
        if row["attestations"] != REQUIRED_ATTESTATIONS:
            raise ValueError("change impact row must include all required no-live/no-download attestations")
        for field in ("affected_source_ids", "document_sections", "requirement_ids", "process_stages", "guardrail_bundle_ids", "citations"):
            if not row[field]:
                raise ValueError(f"change impact row field must not be empty: {field}")
