"""Fixture-first public source freshness recrawl queue.

This module intentionally performs no network access. It converts committed
fixtures describing official source anchors and freshness monitor observations
into deterministic dry-run recrawl candidate rows for reviewer approval.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SOURCE_FAMILY_PRIORITY = {
    "code": 10,
    "charter": 20,
    "administrative_rule": 30,
    "fee_schedule": 40,
    "policy": 50,
    "form": 60,
    "other": 90,
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _priority(source_family: str) -> int:
    return SOURCE_FAMILY_PRIORITY.get(source_family, SOURCE_FAMILY_PRIORITY["other"])


def _robots_url(source_url: str) -> str:
    parsed = urlparse(source_url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}/robots.txt"


def build_recrawl_queue(anchors: list[dict[str, Any]], freshness: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build deterministic recrawl candidates from fixture data only."""
    freshness_by_anchor_id = {item["anchor_id"]: item for item in freshness}
    rows: list[dict[str, Any]] = []

    for anchor in anchors:
        anchor_id = anchor["id"]
        source_family = anchor.get("source_family", "other")
        observed = freshness_by_anchor_id.get(anchor_id, {})
        is_stale = bool(observed.get("is_stale", False))
        changed_since_processor = bool(observed.get("changed_since_processor", False))

        if not is_stale and not changed_since_processor:
            continue

        source_url = anchor["url"]
        rows.append(
            {
                "candidate_id": f"recrawl:{anchor_id}",
                "anchor_id": anchor_id,
                "title": anchor["title"],
                "official_source_url": source_url,
                "source_family": source_family,
                "source_family_priority": _priority(source_family),
                "queue_reason": "changed" if changed_since_processor else "stale",
                "freshness": {
                    "last_checked_utc": observed.get("last_checked_utc"),
                    "last_seen_utc": observed.get("last_seen_utc"),
                    "observed_digest": observed.get("observed_digest"),
                    "processor_digest": observed.get("processor_digest"),
                    "is_stale": is_stale,
                    "changed_since_processor": changed_since_processor,
                },
                "evidence_placeholders": {
                    "stale_or_changed": observed.get("evidence", "fixture indicates stale or changed source"),
                    "raw_response_body_stored": False,
                    "downloaded_document_stored": False,
                },
                "robots_policy_preflight": {
                    "status": "not_run_fixture_only",
                    "robots_txt_url": _robots_url(source_url),
                    "policy_notes": "Reviewer must run approved preflight before any live crawl.",
                },
                "processor_handoff_dry_run": {
                    "status": "not_submitted",
                    "target_processor": anchor.get("processor", "ppd-public-source-processor"),
                    "dry_run_reference": f"dry-run://ppd/source-freshness-recrawl/{anchor_id}",
                },
                "reviewer_approval": {
                    "status": "pending",
                    "approved_by": None,
                    "approved_at_utc": None,
                },
            }
        )

    rows.sort(
        key=lambda row: (
            row["source_family_priority"],
            0 if row["freshness"]["changed_since_processor"] else 1,
            0 if row["freshness"]["is_stale"] else 1,
            row["anchor_id"],
        )
    )
    return rows


def build_recrawl_queue_from_files(anchor_path: Path, freshness_path: Path) -> list[dict[str, Any]]:
    anchors = load_json(anchor_path)
    freshness = load_json(freshness_path)
    if not isinstance(anchors, list):
        raise ValueError("anchor fixture must be a list")
    if not isinstance(freshness, list):
        raise ValueError("freshness fixture must be a list")
    return build_recrawl_queue(anchors, freshness)
