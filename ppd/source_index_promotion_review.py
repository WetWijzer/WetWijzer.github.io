"""Fixture-first source-index promotion review packets for PP&D.

This module converts public capture result summaries into reviewed promotion
candidates for the PP&D source registry, archive manifest, and normalized
document record layers. It is intentionally metadata-only: callers provide
already-loaded fixture data, and the builder rejects raw bodies, local paths,
private/authenticated URLs, invented hashes, unreviewed ready statuses, and
processor outputs that do not point to metadata-only artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import ipaddress
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping
from urllib.parse import parse_qsl, urlparse

RAW_BODY_KEYS = frozenset(
    {
        "body",
        "content",
        "downloaded_pdf",
        "downloaded_pdf_bytes",
        "html",
        "markdown",
        "ocr_text",
        "page_body",
        "pdf_bytes",
        "raw",
        "raw_body",
        "raw_html",
        "response_body",
        "screenshot",
        "text",
    }
)
PRIVATE_PATH_KEYS = frozenset(
    {
        "archive_path",
        "auth_state_path",
        "downloaded_document_path",
        "downloaded_pdf_path",
        "har_path",
        "local_path",
        "path",
        "private_devhub_artifact_path",
        "source_path",
        "trace_path",
    }
)
URL_KEYS = frozenset(
    {
        "canonical_url",
        "requested_url",
        "source_url",
        "url",
        "location",
        "href",
        "archive_url",
        "document_url",
    }
)
SENSITIVE_QUERY_KEYS = frozenset(
    {
        "access_token",
        "api_key",
        "auth",
        "code",
        "cookie",
        "jwt",
        "key",
        "mfa",
        "password",
        "session",
        "sessionid",
        "sid",
        "signature",
        "token",
    }
)
AUTHENTICATED_PATH_MARKERS = (
    "/account",
    "/admin",
    "/dashboard",
    "/login",
    "/logout",
    "/oauth",
    "/profile",
    "/secure",
    "/signin",
    "/sign-in",
    "/user/",
)
READY_STATUSES = frozenset({"approved", "promote", "ready", "ready_for_promotion"})
REVIEWED_VALUES = frozenset({"reviewed", "human_reviewed", "approved_for_metadata_only_promotion"})
METADATA_ARTIFACT_PREFIXES = ("metadata-only:", "metadata://", "ipfs://metadata-only/")


class SourceIndexPromotionReviewError(ValueError):
    """Raised when a capture summary cannot be safely promoted for review."""


@dataclass(frozen=True)
class PromotionCandidate:
    source_id: str
    source_registry: dict[str, Any]
    archive_manifest: dict[str, Any]
    document_record: dict[str, Any]
    hash_evidence: dict[str, Any]
    citation_links: tuple[dict[str, Any], ...]
    review_status: str
    review_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "review_status": self.review_status,
            "review_notes": list(self.review_notes),
            "citation_links": [dict(link) for link in self.citation_links],
            "hash_evidence": dict(self.hash_evidence),
            "source_registry_candidate": dict(self.source_registry),
            "archive_manifest_candidate": dict(self.archive_manifest),
            "document_record_candidate": dict(self.document_record),
        }


def build_source_index_promotion_review_packet(
    capture_summary: Mapping[str, Any],
    *,
    reviewed_by: str = "fixture-supervisor",
    generated_at: str = "2026-05-28T00:00:00Z",
) -> dict[str, Any]:
    """Build a deterministic promotion review packet from summary fixtures."""

    _reject_raw_or_private_artifacts(capture_summary)
    _reject_private_or_authenticated_urls(capture_summary)
    _reject_unreviewed_ready_statuses(capture_summary)
    if capture_summary.get("live_network_access") is True or capture_summary.get("live_crawl_performed") is True:
        raise SourceIndexPromotionReviewError("promotion review packets must not use live network access")
    if not generated_at.endswith("Z"):
        raise SourceIndexPromotionReviewError("generated_at must be an ISO UTC timestamp ending in Z")
    if not reviewed_by.strip():
        raise SourceIndexPromotionReviewError("reviewed_by is required")

    source_candidates = _list_of_mappings(capture_summary, "source_index_update_candidates")
    extraction_items = _index_by_source_id(_list_of_mappings(capture_summary, "extraction_work_items"), "extraction_work_items")
    freshness_changes = _index_by_source_id(_list_of_mappings(capture_summary, "freshness_changes"), "freshness_changes")
    processor_outputs = _index_processor_outputs(_list_of_mappings(capture_summary, "processor_outputs", required=False))
    review_prompts = _list_of_mappings(capture_summary, "human_review_prompts", required=False)

    prompt_reasons_by_source: dict[str, list[str]] = {}
    for prompt in review_prompts:
        source_id = str(prompt.get("source_id", ""))
        if source_id:
            prompt_reasons_by_source.setdefault(source_id, []).append(str(prompt.get("reason", "review_required")))

    candidates: list[PromotionCandidate] = []
    blockers: list[str] = []
    for source in sorted(source_candidates, key=lambda item: (str(item.get("source_id", "")), str(item.get("canonical_url", "")))):
        source_id = _required_text(source, "source_id")
        try:
            extraction = extraction_items[source_id]
            freshness = freshness_changes[source_id]
        except KeyError as exc:
            blockers.append(f"{source_id}: missing paired {exc.args[0]} summary")
            continue
        try:
            _validate_processor_output_for_source(source_id, processor_outputs)
            candidates.append(
                _candidate_from_summary(
                    source=source,
                    extraction=extraction,
                    freshness=freshness,
                    prompt_reasons=tuple(sorted(prompt_reasons_by_source.get(source_id, []))),
                    reviewed_by=reviewed_by,
                    reviewed_at=generated_at,
                )
            )
        except SourceIndexPromotionReviewError as exc:
            blockers.append(f"{source_id}: {exc}")

    status = "reviewed" if candidates and not blockers else "blocked"
    return {
        "packet_type": "ppd_source_index_promotion_review_packet",
        "schema_version": 1,
        "generated_at": generated_at,
        "reviewed_by": reviewed_by,
        "status": status,
        "metadata_only": True,
        "live_network_access": False,
        "no_raw_body_persisted": True,
        "candidate_count": len(candidates),
        "blockers": blockers,
        "promotion_candidates": [candidate.to_dict() for candidate in candidates],
    }


def build_source_index_promotion_review_packet_from_file(path: Path | str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, Mapping):
        raise SourceIndexPromotionReviewError("capture summary fixture must be an object")
    return build_source_index_promotion_review_packet(payload)


def _candidate_from_summary(
    *,
    source: Mapping[str, Any],
    extraction: Mapping[str, Any],
    freshness: Mapping[str, Any],
    prompt_reasons: tuple[str, ...],
    reviewed_by: str,
    reviewed_at: str,
) -> PromotionCandidate:
    source_id = _required_text(source, "source_id")
    canonical_url = _required_text(source, "canonical_url")
    requested_url = _required_text(source, "requested_url")
    manifest_id = _required_text(source, "manifest_id")
    archive_artifact_ref = _required_metadata_artifact_ref(source, "archive_artifact_ref")
    content_hash = _required_sha256(source, "content_hash")
    _validate_https_url(canonical_url, "canonical_url")
    _validate_http_url(requested_url, "requested_url")
    if source.get("no_raw_body_persisted") is not True:
        raise SourceIndexPromotionReviewError("source candidate must preserve no_raw_body_persisted true")

    extraction_source_id = _required_text(extraction, "source_id")
    freshness_source_id = _required_text(freshness, "source_id")
    if extraction_source_id != source_id or freshness_source_id != source_id:
        raise SourceIndexPromotionReviewError("paired summary source_id values must match")

    normalized_document_id = _required_text(extraction, "normalized_document_id")
    extraction_hash = _required_sha256(extraction, "content_hash")
    current_hash = _required_sha256(freshness, "current_content_hash")
    previous_hash = _nullable_text(freshness.get("previous_content_hash"))
    if previous_hash is not None and not previous_hash.startswith("sha256:"):
        raise SourceIndexPromotionReviewError("previous_content_hash must use sha256: format")
    if len({content_hash, extraction_hash, current_hash}) != 1:
        raise SourceIndexPromotionReviewError("invented hashes are not allowed; source, extraction, and freshness hashes must match")

    title = _optional_text(source, "title") or source_id
    source_type = _source_type(_optional_text(source, "page_type"), _required_text(source, "content_type"))
    freshness_status = _required_text(freshness, "status")
    skipped_reason = _nullable_text(source.get("skipped_reason")) or _nullable_text(extraction.get("skipped_reason"))
    citation_links = tuple(_citation_links(source, extraction, freshness))
    if not citation_links:
        raise SourceIndexPromotionReviewError("document records must include at least one citation link")
    hash_evidence = {
        "source_id": source_id,
        "content_hash": content_hash,
        "previous_content_hash": previous_hash,
        "current_content_hash": current_hash,
        "freshness_status": freshness_status,
        "observed_at": _optional_text(source, "observed_at") or _optional_text(freshness, "observed_at") or reviewed_at,
    }

    registry = {
        "source_id": source_id,
        "canonical_url": canonical_url,
        "source_type": source_type,
        "owning_surface": _owning_surface(canonical_url, source_type),
        "allowlist_policy": "official_ppd_public_allowlist",
        "robots_policy": "preflight_required_before_live_fetch",
        "crawl_frequency": _crawl_frequency(source_type),
        "processor_policy": "metadata_only_fixture_review_before_processor_handoff",
        "privacy_classification": "public_metadata_only",
        "last_seen_at": hash_evidence["observed_at"],
        "freshness_status": freshness_status,
        "citation_links": [dict(link) for link in citation_links],
        "no_raw_body_persisted": True,
        "reviewed_by": reviewed_by,
        "reviewed_at": reviewed_at,
    }
    archive = {
        "manifest_id": manifest_id,
        "source_id": source_id,
        "canonical_url": canonical_url,
        "requested_url": requested_url,
        "redirect_chain": list(source.get("redirect_chain", [])) if isinstance(source.get("redirect_chain", []), list) else [],
        "http_status": _integer(source.get("http_status"), "http_status"),
        "content_type": _required_text(source, "content_type"),
        "content_hash": content_hash,
        "capture_started_at": _optional_text(source, "capture_started_at") or hash_evidence["observed_at"],
        "capture_finished_at": _optional_text(source, "capture_finished_at") or hash_evidence["observed_at"],
        "processor_name": _optional_text(source, "processor_name") or "ppd.fake_public_capture",
        "processor_version": _optional_text(source, "processor_version") or "fixture",
        "archive_artifact_ref": archive_artifact_ref,
        "normalized_document_id": normalized_document_id,
        "skipped_reason": skipped_reason,
        "no_raw_body_persisted": True,
    }
    document = {
        "document_id": normalized_document_id,
        "source_id": source_id,
        "title": title,
        "document_type": _document_type(source_type, _optional_text(extraction, "extraction_kind")),
        "language": "en",
        "sections": [],
        "tables": [],
        "links": [dict(link) for link in citation_links],
        "pdf_pages": [],
        "form_fields": [],
        "citation_spans": [
            {
                "citation_id": _stable_id("citation", source_id, canonical_url, content_hash),
                "source_id": source_id,
                "canonical_url": canonical_url,
                "content_hash": content_hash,
                "freshness_status": freshness_status,
                "span_kind": "metadata_only_document_reference",
            }
        ],
        "content_hash": content_hash,
        "extraction_confidence": "metadata_only_pending_review",
        "no_raw_body_persisted": True,
    }
    _validate_document_is_cited(document)
    return PromotionCandidate(
        source_id=source_id,
        source_registry=registry,
        archive_manifest=archive,
        document_record=document,
        hash_evidence=hash_evidence,
        citation_links=citation_links,
        review_status="reviewed",
        review_notes=prompt_reasons or ("metadata_only_fixture_review",),
    )


def _citation_links(source: Mapping[str, Any], extraction: Mapping[str, Any], freshness: Mapping[str, Any]) -> list[dict[str, Any]]:
    explicit = source.get("citation_links") or extraction.get("citation_links")
    if isinstance(explicit, list) and explicit:
        links: list[dict[str, Any]] = []
        expected_hash = _required_sha256(source, "content_hash")
        for index, item in enumerate(explicit):
            if not isinstance(item, Mapping):
                raise SourceIndexPromotionReviewError(f"citation_links[{index}] must be an object")
            url = _required_text(item, "url")
            _validate_https_url(url, "citation_links.url")
            content_hash = _optional_text(item, "content_hash") or expected_hash
            if content_hash != expected_hash:
                raise SourceIndexPromotionReviewError("invented hashes are not allowed in citation links")
            links.append(
                {
                    "label": _optional_text(item, "label") or _optional_text(source, "title") or _required_text(source, "source_id"),
                    "url": url,
                    "source_id": _optional_text(item, "source_id") or _required_text(source, "source_id"),
                    "content_hash": content_hash,
                    "freshness_status": _optional_text(item, "freshness_status") or _required_text(freshness, "status"),
                }
            )
        return links
    return [
        {
            "label": _optional_text(source, "title") or _required_text(source, "source_id"),
            "url": _required_text(source, "canonical_url"),
            "source_id": _required_text(source, "source_id"),
            "content_hash": _required_sha256(source, "content_hash"),
            "freshness_status": _required_text(freshness, "status"),
        }
    ]


def _source_type(page_type: str, content_type: str) -> str:
    lowered_type = page_type.lower()
    lowered_content = content_type.lower()
    if lowered_type in {"devhub_public", "public_html", "public_pdf", "public_form", "external_reference"}:
        return lowered_type
    if "pdf" in lowered_content:
        return "public_pdf"
    if "html" in lowered_content:
        return "public_html"
    return "external_reference"


def _document_type(source_type: str, extraction_kind: str) -> str:
    if source_type == "public_pdf" or "pdf" in extraction_kind:
        return "pdf"
    if source_type == "public_form":
        return "form"
    return "html"


def _owning_surface(canonical_url: str, source_type: str) -> str:
    host = urlparse(canonical_url).hostname or ""
    if "devhub" in host or source_type == "devhub_public":
        return "devhub_public"
    if "portlandmaps" in host:
        return "portlandmaps_public_reference"
    return "portland_ppd_public"


def _crawl_frequency(source_type: str) -> str:
    if source_type == "devhub_public":
        return "daily_or_every_few_days"
    if source_type in {"public_pdf", "public_form"}:
        return "weekly_or_monthly_by_parent_page_change"
    return "weekly"


def _list_of_mappings(payload: Mapping[str, Any], key: str, *, required: bool = True) -> list[Mapping[str, Any]]:
    value = payload.get(key)
    if value is None and not required:
        return []
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise SourceIndexPromotionReviewError(f"{key} must be a list of objects")
    return value


def _index_by_source_id(items: list[Mapping[str, Any]], label: str) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for item in items:
        source_id = _required_text(item, "source_id")
        if source_id in indexed:
            raise SourceIndexPromotionReviewError(f"{label} has duplicate source_id {source_id}")
        indexed[source_id] = item
    return indexed


def _index_processor_outputs(items: list[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    indexed: dict[str, list[Mapping[str, Any]]] = {}
    for item in items:
        source_id = _required_text(item, "source_id")
        indexed.setdefault(source_id, []).append(item)
    return indexed


def _validate_processor_output_for_source(source_id: str, outputs_by_source: Mapping[str, list[Mapping[str, Any]]]) -> None:
    outputs = outputs_by_source.get(source_id, [])
    if not outputs:
        return
    for output in outputs:
        if output.get("metadata_only") is not True:
            raise SourceIndexPromotionReviewError("processor outputs must be metadata_only true")
        if output.get("no_raw_body_persisted") is not True:
            raise SourceIndexPromotionReviewError("processor outputs must preserve no_raw_body_persisted true")
        _required_metadata_artifact_ref(output, "artifact_ref")


def _required_metadata_artifact_ref(values: Mapping[str, Any], key: str) -> str:
    value = _required_text(values, key)
    if not value.startswith(METADATA_ARTIFACT_PREFIXES):
        raise SourceIndexPromotionReviewError(f"{key} must be a metadata-only artifact reference")
    return value


def _validate_document_is_cited(document: Mapping[str, Any]) -> None:
    links = document.get("links")
    spans = document.get("citation_spans")
    if not isinstance(links, list) or not links:
        raise SourceIndexPromotionReviewError("document records must include citation links")
    if not isinstance(spans, list) or not spans:
        raise SourceIndexPromotionReviewError("document records must include citation spans")


def _reject_raw_or_private_artifacts(value: Any, path: str = "$", key: str = "") -> None:
    if isinstance(value, Mapping):
        for nested_key, nested_value in value.items():
            lowered_key = str(nested_key).lower()
            if lowered_key in RAW_BODY_KEYS:
                raise SourceIndexPromotionReviewError(f"raw body-like field is not allowed at {path}.{nested_key}")
            if lowered_key in PRIVATE_PATH_KEYS and isinstance(nested_value, str):
                _reject_private_path(nested_value, f"{path}.{nested_key}")
            _reject_raw_or_private_artifacts(nested_value, f"{path}.{nested_key}", lowered_key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_raw_or_private_artifacts(item, f"{path}[{index}]", key)
    elif isinstance(value, str) and key in PRIVATE_PATH_KEYS:
        _reject_private_path(value, path)


def _reject_private_path(value: str, label: str) -> None:
    if not value:
        return
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if value.startswith("~") or posix.is_absolute() or windows.is_absolute() or ".." in posix.parts or ".." in windows.parts:
        raise SourceIndexPromotionReviewError(f"local private path is not allowed at {label}")


def _reject_private_or_authenticated_urls(value: Any, path: str = "$", key: str = "") -> None:
    if isinstance(value, Mapping):
        for nested_key, nested_value in value.items():
            _reject_private_or_authenticated_urls(nested_value, f"{path}.{nested_key}", str(nested_key).lower())
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_private_or_authenticated_urls(item, f"{path}[{index}]", key)
    elif isinstance(value, str) and (key in URL_KEYS or _looks_like_http_url(value)):
        _reject_private_or_authenticated_url(value, path)


def _reject_private_or_authenticated_url(value: str, label: str) -> None:
    if not _looks_like_http_url(value):
        return
    parsed = urlparse(value)
    if parsed.username or parsed.password:
        raise SourceIndexPromotionReviewError(f"private/authenticated URL is not allowed at {label}")
    host = parsed.hostname or ""
    if host.lower() in {"localhost", "127.0.0.1", "0.0.0.0"}:
        raise SourceIndexPromotionReviewError(f"private/authenticated URL is not allowed at {label}")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None and (ip.is_private or ip.is_loopback or ip.is_link_local):
        raise SourceIndexPromotionReviewError(f"private/authenticated URL is not allowed at {label}")
    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys.intersection(SENSITIVE_QUERY_KEYS):
        raise SourceIndexPromotionReviewError(f"private/authenticated URL is not allowed at {label}")
    normalized_path = parsed.path.lower().replace("_", "-")
    if any(marker in normalized_path for marker in AUTHENTICATED_PATH_MARKERS):
        raise SourceIndexPromotionReviewError(f"private/authenticated URL is not allowed at {label}")


def _reject_unreviewed_ready_statuses(value: Any, path: str = "$", parent: Mapping[str, Any] | None = None, key: str = "") -> None:
    if isinstance(value, Mapping):
        for nested_key, nested_value in value.items():
            _reject_unreviewed_ready_statuses(nested_value, f"{path}.{nested_key}", value, str(nested_key).lower())
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_unreviewed_ready_statuses(item, f"{path}[{index}]", parent, key)
    elif isinstance(value, str) and key in {"status", "review_status", "promotion_status", "readiness_status"}:
        if value.lower() in READY_STATUSES and not _parent_is_reviewed(parent):
            raise SourceIndexPromotionReviewError(f"unreviewed ready status is not allowed at {path}")


def _parent_is_reviewed(parent: Mapping[str, Any] | None) -> bool:
    if parent is None:
        return False
    review_status = parent.get("human_review_status", parent.get("review_status"))
    if isinstance(review_status, str) and review_status.lower() in REVIEWED_VALUES:
        return True
    return parent.get("human_reviewed") is True


def _looks_like_http_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _validate_https_url(value: str, field: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise SourceIndexPromotionReviewError(f"{field} must be an HTTPS URL")


def _validate_http_url(value: str, field: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SourceIndexPromotionReviewError(f"{field} must be an HTTP(S) URL")


def _required_text(values: Mapping[str, Any], key: str) -> str:
    value = values.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SourceIndexPromotionReviewError(f"missing required text field: {key}")
    return value


def _optional_text(values: Mapping[str, Any], key: str) -> str:
    value = values.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise SourceIndexPromotionReviewError(f"optional text field must be a string: {key}")
    return value


def _nullable_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise SourceIndexPromotionReviewError("nullable text fields must be strings or null")
    return value or None


def _required_sha256(values: Mapping[str, Any], key: str) -> str:
    value = _required_text(values, key)
    if not value.startswith("sha256:"):
        raise SourceIndexPromotionReviewError(f"{key} must use sha256: format")
    return value


def _integer(value: Any, key: str) -> int:
    if isinstance(value, bool):
        raise SourceIndexPromotionReviewError(f"integer field must not be boolean: {key}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise SourceIndexPromotionReviewError(f"invalid integer field: {key}") from exc


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\u001f".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


__all__ = [
    "PromotionCandidate",
    "SourceIndexPromotionReviewError",
    "build_source_index_promotion_review_packet",
    "build_source_index_promotion_review_packet_from_file",
]
