"""Fixture-first public source recrawl preflight packet v1.

This module intentionally performs no network access, browser automation, DevHub access,
document downloads, or raw response body storage. It converts an offline recrawl queue
fixture into deterministic reviewer preflight rows.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PACKET_VERSION = "public_source_recrawl_preflight_packet_v1"
FORBIDDEN_RAW_OR_DOWNLOAD_KEYS = frozenset(
    {
        "raw_body",
        "raw_response_body",
        "response_body",
        "body",
        "html",
        "content",
        "bytes",
        "file_bytes",
        "download",
        "download_path",
        "download_url",
        "document_path",
        "pdf_path",
    }
)
OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/public_source_recrawl_preflight.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_public_source_recrawl_preflight.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


def _load_queue(queue_path: Path) -> dict[str, Any]:
    data = json.loads(queue_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("recrawl queue fixture must be a JSON object")
    if data.get("queue_version") != "public_source_freshness_recrawl_queue_v1":
        raise ValueError("unsupported or missing public source freshness recrawl queue version")
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("recrawl queue fixture must contain a candidates list")
    return data


def _scan_for_forbidden_keys(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_RAW_OR_DOWNLOAD_KEYS:
                findings.append(child_path)
            findings.extend(_scan_for_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_scan_for_forbidden_keys(child, f"{path}[{index}]"))
    return findings


def _candidate_sort_key(candidate: dict[str, Any]) -> tuple[int, str, str]:
    priority = candidate.get("priority", 999)
    if not isinstance(priority, int):
        priority = 999
    source_id = str(candidate.get("source_id", ""))
    url = str(candidate.get("url", ""))
    return priority, source_id, url


def _build_row(index: int, candidate: dict[str, Any]) -> dict[str, Any]:
    anchors = candidate.get("official_anchors", [])
    if not isinstance(anchors, list):
        anchors = []
    anchor_citations = []
    for anchor_index, anchor in enumerate(anchors, start=1):
        if not isinstance(anchor, dict):
            continue
        anchor_citations.append(
            {
                "citation_id": f"A{index}.{anchor_index}",
                "label": str(anchor.get("label", "official source anchor")),
                "url": str(anchor.get("url", "")),
                "publisher": str(anchor.get("publisher", "City of Portland")),
            }
        )

    return {
        "row_id": f"preflight-{index:03d}",
        "source_id": str(candidate.get("source_id", "")),
        "title": str(candidate.get("title", "")),
        "url": str(candidate.get("url", "")),
        "recrawl_reason": str(candidate.get("recrawl_reason", "")),
        "freshness_signal": str(candidate.get("freshness_signal", "")),
        "official_anchor_citations": anchor_citations,
        "robots_policy_decision": {
            "status": "review_required_before_live_crawl",
            "robots_txt_checked": False,
            "terms_policy_checked": False,
            "decision": "placeholder_pending_reviewer_review",
            "notes": "Offline fixture preflight only; no live source was accessed.",
        },
        "processor_handoff_dry_run_prerequisites": [
            "Confirm official anchor citation URLs remain public and authoritative.",
            "Confirm robots.txt and applicable policy allow the intended fetch pattern.",
            "Confirm candidate metadata is sufficient for a dry-run processor handoff without raw bodies.",
            "Confirm no document download or raw response body capture is required for preflight approval.",
        ],
        "raw_body_download_exclusion_check": {
            "raw_response_body_stored": False,
            "downloaded_document_stored": False,
            "forbidden_fixture_keys_present": [],
            "status": "passed",
        },
        "reviewer_approval": {
            "approved": False,
            "reviewer": "",
            "reviewed_at": "",
            "notes": "",
        },
    }


def build_preflight_packet(queue_path: Path | str) -> dict[str, Any]:
    """Build a deterministic offline preflight review packet from a queue fixture."""

    resolved_queue_path = Path(queue_path)
    queue = _load_queue(resolved_queue_path)
    forbidden_key_paths = _scan_for_forbidden_keys(queue)
    candidates = [candidate for candidate in queue["candidates"] if isinstance(candidate, dict)]
    ordered_candidates = sorted(candidates, key=_candidate_sort_key)
    rows = [_build_row(index, candidate) for index, candidate in enumerate(ordered_candidates, start=1)]

    for row in rows:
        row["raw_body_download_exclusion_check"]["forbidden_fixture_keys_present"] = forbidden_key_paths
        if forbidden_key_paths:
            row["raw_body_download_exclusion_check"]["status"] = "failed_fixture_contains_raw_or_download_fields"

    return {
        "packet_version": PACKET_VERSION,
        "source_queue_version": queue["queue_version"],
        "source_queue_fixture": str(resolved_queue_path),
        "offline_only": True,
        "live_crawl_performed": False,
        "devhub_accessed": False,
        "documents_downloaded": False,
        "raw_response_bodies_stored": False,
        "ordered_candidate_preflight_rows": rows,
        "packet_level_exclusion_check": {
            "forbidden_fixture_keys_present": forbidden_key_paths,
            "status": "passed" if not forbidden_key_paths else "failed_fixture_contains_raw_or_download_fields",
        },
        "exact_offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }
