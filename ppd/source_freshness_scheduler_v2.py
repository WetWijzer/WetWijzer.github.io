"""Fixture-first PP&D source freshness scheduler packet v2.

This module intentionally performs no network access. It converts a committed
anchor fixture into deterministic synthetic recrawl windows for offline planning
and validation.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

SCHEDULE_VERSION = "ppd-source-freshness-scheduler-packet-v2"
DEFAULT_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/source_freshness_scheduler_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_source_freshness_scheduler_v2.py"],
]

CADENCE_DAYS = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
}

STALE_HOLD_TRIGGERS = [
    {
        "id": "fixture_anchor_missing_url",
        "severity": "hold",
        "description": "Hold publication when an enabled public anchor lacks a URL in the fixture.",
    },
    {
        "id": "fixture_anchor_unknown_cadence",
        "severity": "hold",
        "description": "Hold publication when an anchor requests a cadence outside daily, weekly, or monthly.",
    },
    {
        "id": "synthetic_window_elapsed_without_fixture_refresh",
        "severity": "hold",
        "description": "Hold publication when the synthetic recrawl window has elapsed but no refreshed fixture evidence exists.",
    },
    {
        "id": "authenticated_or_session_bound_url",
        "severity": "skip",
        "description": "Skip authenticated, session-bound, payment, upload, submission, CAPTCHA, MFA, or account-only URLs.",
    },
]


def load_anchor_fixture(path: Path) -> Dict[str, Any]:
    """Load an anchor-set fixture from disk without fetching remote content."""
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("anchor fixture must be a JSON object")
    anchors = payload.get("anchors")
    if not isinstance(anchors, list):
        raise ValueError("anchor fixture must include an anchors list")
    return payload


def build_scheduler_packet(anchor_fixture: Mapping[str, Any]) -> Dict[str, Any]:
    generated_on = _parse_date(str(anchor_fixture.get("generated_on", "2026-05-31")))
    packet: Dict[str, Any] = {
        "version": SCHEDULE_VERSION,
        "generated_on": generated_on.isoformat(),
        "mode": "fixture-first-offline",
        "source_registry_changed": False,
        "live_crawl_performed": False,
        "raw_bodies_stored": False,
        "downloaded_files": False,
        "official_anchor_set_id": anchor_fixture.get("official_anchor_set_id", "unknown"),
        "recrawl_windows": [],
        "stale_source_hold_triggers": list(STALE_HOLD_TRIGGERS),
        "affected_surface_categories": _sorted_unique(_iter_surface_categories(anchor_fixture.get("anchors", []))),
        "skipped_authenticated_url_notes": [],
        "offline_validation_commands": list(DEFAULT_VALIDATION_COMMANDS),
    }

    for anchor in anchor_fixture.get("anchors", []):
        if not isinstance(anchor, Mapping):
            continue
        normalized = _normalize_anchor(anchor, generated_on)
        if normalized.get("skip_reason"):
            packet["skipped_authenticated_url_notes"].append(
                {
                    "anchor_id": normalized["anchor_id"],
                    "url": normalized.get("url", ""),
                    "reason": normalized["skip_reason"],
                    "surfaces": normalized["surfaces"],
                }
            )
            continue
        packet["recrawl_windows"].append(normalized)

    packet["recrawl_windows"] = sorted(
        packet["recrawl_windows"], key=lambda item: (item["cadence"], item["anchor_id"])
    )
    packet["skipped_authenticated_url_notes"] = sorted(
        packet["skipped_authenticated_url_notes"], key=lambda item: item["anchor_id"]
    )
    return packet


def _normalize_anchor(anchor: Mapping[str, Any], generated_on: date) -> Dict[str, Any]:
    anchor_id = str(anchor.get("id", "")).strip()
    cadence = str(anchor.get("cadence", "weekly")).strip().lower()
    surfaces = _sorted_unique(anchor.get("surface_categories", []))
    url = str(anchor.get("url", "")).strip()
    requires_auth = bool(anchor.get("requires_auth", False)) or _looks_authenticated(url)

    if requires_auth:
        return {
            "anchor_id": anchor_id,
            "label": str(anchor.get("label", anchor_id)),
            "url": url,
            "surfaces": surfaces,
            "skip_reason": "authenticated_or_session_bound_url_not_crawled_offline",
        }

    cadence_days = CADENCE_DAYS.get(cadence)
    if cadence_days is None:
        cadence = "weekly"
        cadence_days = CADENCE_DAYS[cadence]

    window_start = generated_on
    window_end = generated_on + timedelta(days=cadence_days)
    return {
        "anchor_id": anchor_id,
        "label": str(anchor.get("label", anchor_id)),
        "url": url,
        "cadence": cadence,
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "stale_after": window_end.isoformat(),
        "surfaces": surfaces,
        "hold_trigger_ids": [
            "fixture_anchor_missing_url" if not url else "synthetic_window_elapsed_without_fixture_refresh"
        ],
        "evidence_policy": "fixture_metadata_only_no_raw_body_storage",
    }


def _iter_surface_categories(anchors: Any) -> Iterable[str]:
    if not isinstance(anchors, list):
        return []
    values: List[str] = []
    for anchor in anchors:
        if isinstance(anchor, Mapping):
            values.extend(str(item) for item in anchor.get("surface_categories", []) if str(item).strip())
    return values


def _sorted_unique(values: Iterable[Any]) -> List[str]:
    return sorted({str(value).strip() for value in values if str(value).strip()})


def _looks_authenticated(url: str) -> bool:
    lowered = url.lower()
    markers = ("login", "signin", "session", "account", "checkout", "payment", "upload", "submit")
    return any(marker in lowered for marker in markers)


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


__all__ = [
    "SCHEDULE_VERSION",
    "DEFAULT_VALIDATION_COMMANDS",
    "load_anchor_fixture",
    "build_scheduler_packet",
]
