"""Deterministic PP&D freshness-refresh recrawl planning.

The helpers in this module operate only on committed source-index style
metadata. They do not fetch URLs, inspect live robots.txt, persist raw bodies, or
invoke processors. The output is a metadata-only intention that a later live
runner must still preflight before any crawl.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse
import json


RAW_BODY_FIELDS = frozenset({"body", "html", "raw_body", "rawBody", "raw_content", "response_body", "text"})
REFRESH_STATUSES = frozenset({"stale", "stale_guidance", "content_hash_changed", "hash_changed", "priority_recrawl"})
ALLOW_VALUES = frozenset({"allow", "allowed", "listed", "public_allowlist"})
DENY_VALUES = frozenset({"deny", "denied", "disallow", "disallowed", "blocked", "outside_allowlist"})
PUBLIC_SOURCE_TYPES = frozenset({"public_html", "public_pdf", "public_form", "devhub_public", "external_reference"})
RATE_LIMIT_SECONDS = {"daily": 5, "every_few_days": 7, "weekly": 10, "monthly": 15}


@dataclass(frozen=True)
class FreshnessRefreshIntention:
    source_id: str
    canonical_url: str
    source_type: str
    refresh_reason: str
    recrawl_mode: str
    network_requests_made: bool
    allowlist_policy: dict[str, Any]
    robots_preflight_policy: dict[str, Any]
    rate_limit_policy: dict[str, Any]
    processor_policy: dict[str, Any]
    no_raw_body_policy: dict[str, Any]
    blocked_actions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["blocked_actions"] = list(self.blocked_actions)
        return payload


def load_freshness_refresh_intentions(path: str | Path) -> list[dict[str, Any]]:
    """Load a fixture and return stable metadata-only refresh intentions."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    sources = payload.get("sources", payload) if isinstance(payload, dict) else payload
    if not isinstance(sources, list):
        raise ValueError("freshness refresh fixture must contain a list or a {'sources': [...]} object")
    return [intention.to_dict() for intention in plan_freshness_refresh_intentions(sources)]


def plan_freshness_refresh_intentions(sources: Iterable[Mapping[str, Any]]) -> list[FreshnessRefreshIntention]:
    """Convert stale or hash-changed public source-index entries into intentions.

    Non-public, fresh, allowlist-blocked, robots-blocked, and raw-body-bearing
    records are fail-closed: blocked records are omitted; raw body fields raise a
    fixture validation error because they are not commit-safe.
    """

    intentions: list[FreshnessRefreshIntention] = []
    for source in sources:
        _assert_no_raw_body_fields(source)
        if not _is_public_source(source):
            continue
        reason = _refresh_reason(source)
        if reason is None:
            continue
        if not _policy_allows(source.get("allowlist_policy")):
            continue
        if not _policy_allows(source.get("robots_policy")):
            continue
        if _processor_requests_raw_body(source.get("processor_policy")):
            continue
        intentions.append(_build_intention(source, reason))
    return sorted(intentions, key=lambda item: item.source_id)


def _build_intention(source: Mapping[str, Any], reason: str) -> FreshnessRefreshIntention:
    source_id = _required_string(source, "source_id")
    canonical_url = _required_string(source, "canonical_url")
    host = urlparse(canonical_url).netloc
    frequency = str(source.get("crawl_frequency", "weekly")).strip().lower()
    return FreshnessRefreshIntention(
        source_id=source_id,
        canonical_url=canonical_url,
        source_type=_required_string(source, "source_type"),
        refresh_reason=reason,
        recrawl_mode="metadata_only",
        network_requests_made=False,
        allowlist_policy={
            "required": True,
            "decision": "allow",
            "allowed_host": host,
            "source_field": "allowlist_policy",
        },
        robots_preflight_policy={
            "required_before_live_crawl": True,
            "fixture_decision": "allow",
            "live_robots_fetch_performed": False,
            "source_field": "robots_policy",
        },
        rate_limit_policy={
            "bucket": host,
            "crawl_frequency": frequency,
            "minimum_delay_seconds": RATE_LIMIT_SECONDS.get(frequency, 10),
            "enforced_before_live_crawl": True,
        },
        processor_policy={
            "processor": "ipfs_datasets_py.web_archive",
            "handoff_mode": "metadata_only_recrawl_intention",
            "persist_raw_body": False,
            "normalize_text_after_live_preflight_only": True,
        },
        no_raw_body_policy={
            "no_raw_body_persisted": True,
            "forbidden_fixture_fields_absent": sorted(RAW_BODY_FIELDS),
            "commit_safe": True,
        },
        blocked_actions=(
            "network_request",
            "raw_body_persistence",
            "authenticated_access",
            "captcha_or_mfa_automation",
            "official_submission_or_payment",
        ),
    )


def _refresh_reason(source: Mapping[str, Any]) -> str | None:
    status = str(source.get("freshness_status", "")).strip().lower()
    if status in REFRESH_STATUSES:
        return f"freshness_status:{status}"
    previous_hash = _optional_string(source.get("previous_content_hash") or source.get("stored_content_hash"))
    observed_hash = _optional_string(source.get("current_content_hash") or source.get("observed_content_hash"))
    if previous_hash is not None and observed_hash is not None and previous_hash != observed_hash:
        return "content_hash_changed"
    return None


def _is_public_source(source: Mapping[str, Any]) -> bool:
    return str(source.get("source_type", "")).strip().lower() in PUBLIC_SOURCE_TYPES


def _policy_allows(value: Any) -> bool:
    normalized = str(value or "").strip().lower()
    if normalized in DENY_VALUES:
        return False
    return normalized in ALLOW_VALUES


def _processor_requests_raw_body(value: Any) -> bool:
    return str(value or "metadata_only").strip().lower() in {"raw_body", "persist_raw_body", "raw_download"}


def _assert_no_raw_body_fields(source: Mapping[str, Any]) -> None:
    present = sorted(str(key) for key in source if str(key) in RAW_BODY_FIELDS)
    if present:
        source_id = source.get("source_id", "")
        raise ValueError(f"source {source_id!r} contains raw body field(s): {', '.join(present)}")
    if source.get("no_raw_body_persisted") is False:
        source_id = source.get("source_id", "")
        raise ValueError(f"source {source_id!r} does not preserve no_raw_body_persisted")


def _required_string(source: Mapping[str, Any], field: str) -> str:
    value = source.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"source is missing required string field: {field}")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
