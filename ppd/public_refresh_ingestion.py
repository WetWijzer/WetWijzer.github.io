"""Fixture-first public refresh ingestion planning for PP&D.

The planner accepts metadata-only refreshed capture fixtures. It performs no
network access and rejects raw body, browser, credential, and downloaded artifact
fields so public refresh work can be reviewed before any live crawl promotion.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


_HASH_RE = re.compile(r"^(sha256:)?[0-9a-f]{64}$")
_RAW_OR_PRIVATE_KEYS = {
    "auth_state",
    "body",
    "content",
    "cookies",
    "credential",
    "credentials",
    "downloaded_document",
    "har",
    "html",
    "local_path",
    "markdown",
    "normalized_text",
    "ocr_text",
    "password",
    "pdf_pages",
    "raw",
    "raw_body",
    "raw_html",
    "screenshot",
    "session_state",
    "text",
    "trace",
}


class PublicRefreshIngestionError(ValueError):
    """Raised when public refresh metadata is unsafe or incomplete."""


@dataclass(frozen=True)
class SourceIndexHashDelta:
    source_index_id: str
    capture_id: str
    canonical_url: str
    previous_content_hash: str
    refreshed_content_hash: str
    changed: bool


@dataclass(frozen=True)
class RequirementDeltaReviewItem:
    review_item_id: str
    requirement_id: str
    delta_kind: str
    source_index_id: str
    capture_id: str
    canonical_url: str
    review_reason: str
    affected_process_ids: tuple[str, ...]
    blocked_guardrail_bundle_ids: tuple[str, ...]


@dataclass(frozen=True)
class PublicRefreshIngestionPlan:
    plan_id: str
    generated_at: str
    source_index_hash_deltas: tuple[SourceIndexHashDelta, ...]
    requirement_delta_review_items: tuple[RequirementDeltaReviewItem, ...]
    affected_process_ids: tuple[str, ...]
    blocked_guardrail_bundle_ids: tuple[str, ...]
    no_live_crawl: bool = True
    no_raw_body_storage: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "generated_at": self.generated_at,
            "no_live_crawl": self.no_live_crawl,
            "no_raw_body_storage": self.no_raw_body_storage,
            "source_index_hash_deltas": [delta.__dict__ for delta in self.source_index_hash_deltas],
            "requirement_delta_review_items": [item.__dict__ for item in self.requirement_delta_review_items],
            "affected_process_ids": list(self.affected_process_ids),
            "blocked_guardrail_bundle_ids": list(self.blocked_guardrail_bundle_ids),
        }


def build_public_refresh_ingestion_plan(fixture: Mapping[str, Any]) -> PublicRefreshIngestionPlan:
    """Build a deterministic review plan from metadata-only refresh captures."""

    _reject_raw_or_private_fields(fixture)
    generated_at = _required_str(fixture, "generated_at")
    if not generated_at.endswith("Z"):
        raise PublicRefreshIngestionError("generated_at must be UTC and end in Z")
    if fixture.get("capture_mode") != "fixture_metadata_only":
        raise PublicRefreshIngestionError("capture_mode must be fixture_metadata_only")
    if fixture.get("live_crawl_performed") is not False:
        raise PublicRefreshIngestionError("live_crawl_performed must be false")
    if fixture.get("raw_body_persisted") is not False:
        raise PublicRefreshIngestionError("raw_body_persisted must be false")

    captures = _list_of_mappings(fixture, "refreshed_captures")
    source_deltas: list[SourceIndexHashDelta] = []
    review_items: list[RequirementDeltaReviewItem] = []
    affected_process_ids: set[str] = set()
    blocked_guardrail_bundle_ids: set[str] = set()

    for capture in captures:
        capture_id = _required_str(capture, "capture_id")
        source_index_id = _required_str(capture, "source_index_id")
        canonical_url = _official_url(_required_str(capture, "canonical_url"), capture_id)
        previous_hash = _required_hash(capture, "previous_content_hash")
        refreshed_hash = _required_hash(capture, "refreshed_content_hash")
        changed = previous_hash != refreshed_hash

        source_deltas.append(
            SourceIndexHashDelta(
                source_index_id=source_index_id,
                capture_id=capture_id,
                canonical_url=canonical_url,
                previous_content_hash=previous_hash,
                refreshed_content_hash=refreshed_hash,
                changed=changed,
            )
        )

        capture_process_ids = tuple(sorted(_string_list(capture, "affected_process_ids")))
        capture_guardrail_ids = tuple(sorted(_string_list(capture, "guardrail_bundle_ids")))
        affected_process_ids.update(capture_process_ids)

        for requirement_delta in _list_of_mappings(capture, "requirement_deltas"):
            requirement_id = _required_str(requirement_delta, "requirement_id")
            delta_kind = _required_str(requirement_delta, "delta_kind")
            if delta_kind not in {"added", "changed", "removed"}:
                raise PublicRefreshIngestionError(f"unsupported delta_kind for {requirement_id}")
            requirement_process_ids = tuple(
                sorted(set(capture_process_ids) | set(_string_list(requirement_delta, "affected_process_ids")))
            )
            requirement_guardrail_ids = tuple(
                sorted(set(capture_guardrail_ids) | set(_string_list(requirement_delta, "blocked_guardrail_bundle_ids")))
            )
            affected_process_ids.update(requirement_process_ids)
            blocked_guardrail_bundle_ids.update(requirement_guardrail_ids)
            review_items.append(
                RequirementDeltaReviewItem(
                    review_item_id=f"review-{source_index_id}-{requirement_id}-{delta_kind}",
                    requirement_id=requirement_id,
                    delta_kind=delta_kind,
                    source_index_id=source_index_id,
                    capture_id=capture_id,
                    canonical_url=canonical_url,
                    review_reason=_required_str(requirement_delta, "review_reason"),
                    affected_process_ids=requirement_process_ids,
                    blocked_guardrail_bundle_ids=requirement_guardrail_ids,
                )
            )

    source_deltas.sort(key=lambda item: (item.source_index_id, item.capture_id))
    review_items.sort(key=lambda item: item.review_item_id)
    plan_body = {
        "generated_at": generated_at,
        "source_index_hash_deltas": [delta.__dict__ for delta in source_deltas],
        "requirement_delta_review_items": [item.__dict__ for item in review_items],
        "affected_process_ids": sorted(affected_process_ids),
        "blocked_guardrail_bundle_ids": sorted(blocked_guardrail_bundle_ids),
    }
    plan_id = "public-refresh-ingestion-" + hashlib.sha256(
        json.dumps(plan_body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]

    return PublicRefreshIngestionPlan(
        plan_id=plan_id,
        generated_at=generated_at,
        source_index_hash_deltas=tuple(source_deltas),
        requirement_delta_review_items=tuple(review_items),
        affected_process_ids=tuple(sorted(affected_process_ids)),
        blocked_guardrail_bundle_ids=tuple(sorted(blocked_guardrail_bundle_ids)),
    )


def _reject_raw_or_private_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized_key = str(key).lower()
            if normalized_key in _RAW_OR_PRIVATE_KEYS:
                raise PublicRefreshIngestionError(f"raw or private field is not allowed at {path}.{key}")
            _reject_raw_or_private_fields(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_raw_or_private_fields(nested, f"{path}[{index}]")


def _required_str(value: Mapping[str, Any], key: str) -> str:
    nested = value.get(key)
    if not isinstance(nested, str) or not nested.strip():
        raise PublicRefreshIngestionError(f"{key} must be a non-empty string")
    return nested


def _required_hash(value: Mapping[str, Any], key: str) -> str:
    digest = _required_str(value, key)
    if not _HASH_RE.match(digest):
        raise PublicRefreshIngestionError(f"{key} must be a sha256 hash")
    return digest


def _list_of_mappings(value: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    nested = value.get(key)
    if not isinstance(nested, list) or not all(isinstance(item, Mapping) for item in nested):
        raise PublicRefreshIngestionError(f"{key} must be a list of objects")
    return nested


def _string_list(value: Mapping[str, Any], key: str) -> tuple[str, ...]:
    nested = value.get(key, [])
    if not isinstance(nested, list) or not all(isinstance(item, str) and item.strip() for item in nested):
        raise PublicRefreshIngestionError(f"{key} must be a list of non-empty strings")
    return tuple(nested)


def _official_url(url: str, capture_id: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise PublicRefreshIngestionError(f"{capture_id} canonical_url must be HTTPS")
    if parsed.hostname not in {"www.portland.gov", "devhub.portlandoregon.gov", "www.portlandoregon.gov", "www.portlandmaps.com"}:
        raise PublicRefreshIngestionError(f"{capture_id} canonical_url is outside the PP&D public allowlist")
    return url
