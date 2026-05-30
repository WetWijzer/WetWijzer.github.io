"""Fixture-first public source refresh evidence intake packet v1.

This module intentionally converts committed reviewer/rehearsal fixtures into
metadata-only intake rows. It does not crawl, download, invoke processors, read
raw page bodies, or mutate any registry.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_VERSION = "fixture_first_public_source_refresh_evidence_intake_v1"
FRESHNESS_VERSION = "public_freshness_reviewer_handoff_v1"
IMPACT_VERSION = "public_source_change_impact_rehearsal_v1"

ATTESTATIONS = {
    "fixture_first": True,
    "metadata_only": True,
    "no_recrawl": True,
    "no_download": True,
    "no_processor": True,
    "no_raw_body": True,
    "no_registry_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/extraction/public_source_refresh_evidence_intake.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


@dataclass(frozen=True)
class FixtureIntakeInputs:
    """Input paths for the fixture-only conversion."""

    freshness_handoff_path: Path
    change_impact_rehearsal_path: Path


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must be a JSON object: {path}")
    return data


def _require_version(payload: dict[str, Any], expected: str, path: Path) -> None:
    actual = payload.get("packet_version")
    if actual != expected:
        raise ValueError(f"{path} has packet_version {actual!r}; expected {expected!r}")


def _as_string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
    return value


def _unique_sorted(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def _metadata_citations(source: dict[str, Any]) -> list[dict[str, str]]:
    citations = source.get("citations", [])
    if not isinstance(citations, list):
        raise ValueError("citations must be a list")

    metadata_only: list[dict[str, str]] = []
    for citation in citations:
        if not isinstance(citation, dict):
            raise ValueError("each citation must be an object")
        label = citation.get("label")
        url = citation.get("url")
        observed_field = citation.get("observed_field")
        if not all(isinstance(item, str) and item for item in (label, url, observed_field)):
            raise ValueError("citation label, url, and observed_field are required strings")
        metadata_only.append({"label": label, "url": url, "observed_field": observed_field})
    return metadata_only


def build_public_source_refresh_evidence_intake_packet(
    freshness_handoff: dict[str, Any], change_impact_rehearsal: dict[str, Any]
) -> dict[str, Any]:
    """Build a deterministic metadata-only reviewer intake packet."""

    sources = freshness_handoff.get("sources")
    impacts = change_impact_rehearsal.get("impacts")
    if not isinstance(sources, list):
        raise ValueError("freshness handoff sources must be a list")
    if not isinstance(impacts, list):
        raise ValueError("change impact rehearsal impacts must be a list")

    impacts_by_source: dict[str, dict[str, Any]] = {}
    for impact in impacts:
        if not isinstance(impact, dict):
            raise ValueError("each impact must be an object")
        source_id = impact.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("impact source_id is required")
        impacts_by_source[source_id] = impact

    rows: list[dict[str, Any]] = []
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            raise ValueError("each source must be an object")
        source_id = source.get("source_id")
        title = source.get("observed_public_page_title")
        visible_updated_date = source.get("visible_updated_date")
        public_page_url = source.get("public_page_url")
        if not all(isinstance(item, str) and item for item in (source_id, title, public_page_url)):
            raise ValueError("source_id, observed_public_page_title, and public_page_url are required")
        if visible_updated_date is not None and not isinstance(visible_updated_date, str):
            raise ValueError("visible_updated_date must be a string or null")

        impact = impacts_by_source.get(source_id, {})
        affected_source_ids = _unique_sorted(
            [source_id]
            + _as_string_list(source.get("affected_source_ids"), "source affected_source_ids")
            + _as_string_list(impact.get("affected_source_ids"), "impact affected_source_ids")
        )
        affected_requirement_ids = _unique_sorted(
            _as_string_list(source.get("affected_requirement_ids"), "source affected_requirement_ids")
            + _as_string_list(impact.get("affected_requirement_ids"), "impact affected_requirement_ids")
        )

        defer_reason = impact.get("defer_reason") or source.get("defer_reason") or "fixture_review_required"
        rollback_note = impact.get("rollback_note") or source.get("rollback_note") or "Drop this intake row; no registry mutation has occurred."
        if not isinstance(defer_reason, str) or not isinstance(rollback_note, str):
            raise ValueError("defer_reason and rollback_note must be strings")

        rows.append(
            {
                "intake_row_id": f"public-refresh-intake-v1-{index:03d}",
                "source_id": source_id,
                "public_page_url": public_page_url,
                "observed_public_page_title": title,
                "visible_updated_date": visible_updated_date,
                "affected_source_ids": affected_source_ids,
                "affected_requirement_ids": affected_requirement_ids,
                "citations": _metadata_citations(source),
                "defer_reason": defer_reason,
                "rollback_note": rollback_note,
                "attestations": dict(ATTESTATIONS),
                "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
            }
        )

    return {
        "packet_version": PACKET_VERSION,
        "input_packet_versions": [FRESHNESS_VERSION, IMPACT_VERSION],
        "generated_from": "committed_ppd_test_fixtures_only",
        "attestations": dict(ATTESTATIONS),
        "rows": rows,
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
    }


def build_packet_from_fixture_paths(inputs: FixtureIntakeInputs) -> dict[str, Any]:
    freshness_handoff = load_json(inputs.freshness_handoff_path)
    change_impact_rehearsal = load_json(inputs.change_impact_rehearsal_path)
    _require_version(freshness_handoff, FRESHNESS_VERSION, inputs.freshness_handoff_path)
    _require_version(change_impact_rehearsal, IMPACT_VERSION, inputs.change_impact_rehearsal_path)
    return build_public_source_refresh_evidence_intake_packet(freshness_handoff, change_impact_rehearsal)
