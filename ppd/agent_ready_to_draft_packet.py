"""Fixture-first ready-to-draft packet validation for PP&D agents.

The packet is intentionally metadata-only: it describes readiness, gaps,
DevHub surfaces, reversible draft steps, and action-journal expectations
without storing private session state, downloaded documents, or raw crawl
output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

REQUIRED_TOP_LEVEL_KEYS = {
    "packet_id",
    "workflow_id",
    "workflow_name",
    "metadata_only",
    "synthetic_workflow",
    "process_model_version_readiness",
    "missing_information_prioritization",
    "devhub_surface_map_readiness",
    "reversible_draft_planning",
    "action_journal_expectations",
    "citations",
}

FORBIDDEN_RAW_KEYS = {
    "auth_state",
    "captcha_solution",
    "downloaded_document",
    "downloaded_documents",
    "html",
    "mfa_secret",
    "password",
    "private_session",
    "raw_crawl_output",
    "session_cookie",
    "trace",
    "traces",
    "upload_payload",
}

REQUIRED_CITATION_SECTIONS = {
    "process_model_version_readiness",
    "missing_information_prioritization",
    "devhub_surface_map_readiness",
    "reversible_draft_planning",
    "action_journal_expectations",
}


class ReadyToDraftPacketError(ValueError):
    """Raised when a ready-to-draft packet fixture is invalid."""


def load_packet(path: Path | str) -> dict[str, Any]:
    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as packet_file:
        data = json.load(packet_file)
    if not isinstance(data, dict):
        raise ReadyToDraftPacketError("packet must be a JSON object")
    validate_packet(data)
    return data


def validate_packet(packet: Mapping[str, Any]) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL_KEYS.difference(packet.keys()))
    if missing:
        raise ReadyToDraftPacketError(f"missing top-level keys: {', '.join(missing)}")

    if packet.get("metadata_only") is not True:
        raise ReadyToDraftPacketError("metadata_only must be true")
    if packet.get("synthetic_workflow") is not True:
        raise ReadyToDraftPacketError("synthetic_workflow must be true")

    forbidden_path = _find_forbidden_key(packet)
    if forbidden_path is not None:
        raise ReadyToDraftPacketError(f"forbidden raw/private field present: {forbidden_path}")

    citations = packet.get("citations")
    if not isinstance(citations, list) or not citations:
        raise ReadyToDraftPacketError("citations must be a non-empty list")

    citation_ids = set()
    for index, citation in enumerate(citations):
        if not isinstance(citation, dict):
            raise ReadyToDraftPacketError(f"citation {index} must be an object")
        source_id = citation.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ReadyToDraftPacketError(f"citation {index} requires source_id")
        citation_ids.add(source_id)
        if citation.get("classification") != "metadata":
            raise ReadyToDraftPacketError(f"citation {source_id} must be classified as metadata")

    for section in REQUIRED_CITATION_SECTIONS:
        value = packet.get(section)
        if not isinstance(value, dict):
            raise ReadyToDraftPacketError(f"{section} must be an object")
        _require_known_citations(section, value.get("citation_ids"), citation_ids)

    missing_info = packet.get("missing_information_prioritization")
    if isinstance(missing_info, dict):
        priorities = missing_info.get("priorities")
        if not isinstance(priorities, list) or not priorities:
            raise ReadyToDraftPacketError("missing_information_prioritization.priorities must be non-empty")
        for item in priorities:
            if not isinstance(item, dict):
                raise ReadyToDraftPacketError("each missing-information priority must be an object")
            if item.get("rank") is None or not item.get("question"):
                raise ReadyToDraftPacketError("each missing-information priority requires rank and question")

    draft_plan = packet.get("reversible_draft_planning")
    if isinstance(draft_plan, dict):
        steps = draft_plan.get("draft_steps")
        if not isinstance(steps, list) or not steps:
            raise ReadyToDraftPacketError("reversible_draft_planning.draft_steps must be non-empty")
        for step in steps:
            if not isinstance(step, dict):
                raise ReadyToDraftPacketError("each draft step must be an object")
            if step.get("reversible") is not True:
                raise ReadyToDraftPacketError("each draft step must be explicitly reversible")
            if step.get("requires_submission") is not False:
                raise ReadyToDraftPacketError("draft steps must not require submission")


def _require_known_citations(section: str, citation_ids: object, known_ids: set[str]) -> None:
    if not isinstance(citation_ids, list) or not citation_ids:
        raise ReadyToDraftPacketError(f"{section}.citation_ids must be non-empty")
    unknown = [source_id for source_id in citation_ids if source_id not in known_ids]
    if unknown:
        raise ReadyToDraftPacketError(f"{section} references unknown citations: {', '.join(unknown)}")


def _find_forbidden_key(value: object, prefix: str = "") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in FORBIDDEN_RAW_KEYS:
                return path
            nested = _find_forbidden_key(child, path)
            if nested is not None:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nested = _find_forbidden_key(child, f"{prefix}[{index}]")
            if nested is not None:
                return nested
    return None
