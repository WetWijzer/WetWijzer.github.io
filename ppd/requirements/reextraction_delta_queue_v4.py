"""Fixture-first re-extraction delta queue v4.

This module intentionally consumes already-collected public source freshness
fixture packets only. It does not crawl, download, OCR, persist raw bodies, or
invoke DevHub automation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

QUEUE_VERSION = "ppd-reextraction-delta-queue-v4"
SUPPORTED_PACKET_VERSION = "public-source-freshness-evidence-packet-v4"
STALE_STATUSES = {"changed", "stale", "missing_prior_evidence", "review_required"}
SUPPORTED_SOURCE_TYPES = {"html", "pdf", "form"}


def load_fixture_packet(path: str | Path) -> dict[str, Any]:
    """Load a public source freshness evidence packet fixture from disk."""
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError("freshness evidence packet fixture must contain a JSON object")
    return packet


def assemble_delta_queue(packet: dict[str, Any]) -> dict[str, Any]:
    """Build narrow re-extraction work items from a fixture packet."""
    packet_version = packet.get("packet_version")
    if packet_version != SUPPORTED_PACKET_VERSION:
        raise ValueError(f"unsupported freshness evidence packet version: {packet_version!r}")

    sources = packet.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("freshness evidence packet sources must be a list")

    work_items: list[dict[str, Any]] = []
    skipped_sources: list[dict[str, str]] = []

    for source in sources:
        if not isinstance(source, dict):
            skipped_sources.append({"source_id": "unknown", "reason": "source entry is not an object"})
            continue

        source_id = str(source.get("source_id") or "unknown")
        source_type = str(source.get("source_type") or "").lower()
        freshness_status = str(source.get("freshness_status") or "").lower()
        public_url = str(source.get("public_url") or "")

        if source_type not in SUPPORTED_SOURCE_TYPES:
            skipped_sources.append({"source_id": source_id, "reason": "unsupported source type"})
            continue
        if freshness_status not in STALE_STATUSES:
            skipped_sources.append({"source_id": source_id, "reason": "source is unchanged and not stale"})
            continue
        if not public_url.startswith(("https://", "http://")):
            skipped_sources.append({"source_id": source_id, "reason": "missing public source URL"})
            continue

        work_items.append(
            {
                "work_item_id": f"reextract-v4-{source_id}",
                "source_id": source_id,
                "source_type": source_type,
                "public_url": public_url,
                "freshness_status": freshness_status,
                "source_evidence_placeholders": {
                    "previous_fingerprint": source.get("previous_fingerprint"),
                    "current_fingerprint": source.get("current_fingerprint"),
                    "last_seen_at": source.get("last_seen_at"),
                    "evidence_packet_id": packet.get("packet_id"),
                },
                "expected_requirement_types": list(source.get("expected_requirement_types") or []),
                "affected_process_stages": list(source.get("affected_process_stages") or []),
                "human_review_status": "required",
                "reviewer_holds": list(source.get("reviewer_holds") or []),
                "validation_commands": [
                    ["python3", "-m", "py_compile", "ppd/requirements/reextraction_delta_queue_v4.py"],
                    ["python3", "-m", "pytest", "ppd/tests/test_reextraction_delta_queue_v4.py"],
                ],
            }
        )

    return {
        "queue_version": QUEUE_VERSION,
        "input_packet_id": packet.get("packet_id"),
        "fixture_only": True,
        "prohibited_actions": [
            "live_crawling",
            "ocr",
            "document_downloads",
            "raw_body_persistence",
            "devhub_automation",
        ],
        "work_items": work_items,
        "skipped_sources": skipped_sources,
    }
