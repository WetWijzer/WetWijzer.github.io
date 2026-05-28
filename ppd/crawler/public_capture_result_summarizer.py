"""Fixture-first public capture result summarizer for PP&D.

The summarizer accepts only approved fake public-capture metadata. It emits
metadata-only source-index update candidates, extraction work items, freshness
changes, and human-review prompts without storing page bodies or downloaded PDFs.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import ipaddress
import json
from pathlib import PurePosixPath, PureWindowsPath
import re
from typing import Any, Mapping
from urllib.parse import urlparse

RAW_BODY_KEYS = frozenset(
    {
        "body",
        "content",
        "downloaded_pdf",
        "downloaded_pdf_bytes",
        "downloaded_pdf_path",
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
PRIVATE_PATH_KEYS = frozenset({"archive_path", "downloaded_pdf_path", "local_path", "path", "source_path", "trace_path"})
AUTHENTICATED_PATH_MARKERS = ("/login", "/session", "/account", "/oauth", "/admin")
_WINDOWS_DRIVE_RE = re.compile(r"^[a-zA-Z]:[\\/]")


class PublicCaptureSummaryError(ValueError):
    """Raised when fake capture metadata cannot be safely summarized."""


@dataclass(frozen=True)
class PublicCaptureSummary:
    source_index_update_candidates: tuple[dict[str, Any], ...]
    extraction_work_items: tuple[dict[str, Any], ...]
    freshness_changes: tuple[dict[str, Any], ...]
    human_review_prompts: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "ppd-public-capture-summary-v1",
            "source_index_update_candidates": list(self.source_index_update_candidates),
            "extraction_work_items": list(self.extraction_work_items),
            "freshness_changes": list(self.freshness_changes),
            "human_review_prompts": list(self.human_review_prompts),
        }


def summarize_public_capture_results(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Summarize approved fake capture metadata into downstream work queues."""

    _reject_raw_or_private_artifacts(payload)
    captures = _capture_list(payload)
    as_of = _optional_text(payload, "as_of") or _optional_text(payload, "captured_as_of") or "2026-05-27T00:00:00Z"

    source_candidates: list[dict[str, Any]] = []
    extraction_items: list[dict[str, Any]] = []
    freshness_changes: list[dict[str, Any]] = []
    review_prompts: list[dict[str, Any]] = []

    for capture in sorted(captures, key=lambda item: (_required_text(item, "source_id"), _required_text(item, "canonical_url"))):
        _require_approved_fake_capture(capture)
        source_id = _required_text(capture, "source_id")
        canonical_url = _required_text(capture, "canonical_url")
        requested_url = _required_text(capture, "requested_url")
        content_type = _required_text(capture, "content_type")
        content_hash = _required_text(capture, "content_hash")
        http_status = _integer(capture.get("http_status"), "http_status")
        _validate_public_url(canonical_url, "canonical_url")
        _validate_public_url(requested_url, "requested_url")
        if not content_hash.startswith("sha256:"):
            raise PublicCaptureSummaryError("content_hash must use sha256: prefix")

        observed_at = _optional_text(capture, "capture_finished_at") or as_of
        title = _optional_text(capture, "title") or _optional_text(capture, "source_title") or source_id
        page_type = _page_type(capture, content_type)
        normalized_document_id = _optional_text(capture, "normalized_document_id") or _stable_id("document", source_id, canonical_url, content_hash)
        previous_hash = _optional_text(capture, "previous_content_hash")
        freshness_status = _freshness_status(http_status, previous_hash, content_hash)

        source_candidates.append(
            {
                "candidate_id": _stable_id("source-index-candidate", source_id, canonical_url, content_hash),
                "source_id": source_id,
                "canonical_url": canonical_url,
                "requested_url": requested_url,
                "title": title,
                "page_type": page_type,
                "content_type": content_type,
                "http_status": http_status,
                "content_hash": content_hash,
                "observed_at": observed_at,
                "no_raw_body_persisted": True,
                "update_action": "upsert_metadata_only_record",
            }
        )
        extraction_items.append(
            {
                "work_item_id": _stable_id("extraction-work", source_id, normalized_document_id, content_hash),
                "source_id": source_id,
                "normalized_document_id": normalized_document_id,
                "canonical_url": canonical_url,
                "content_hash": content_hash,
                "extraction_kind": _extraction_kind(content_type),
                "allowed_inputs": ["capture_metadata", "normalized_document_reference"],
                "prohibited_inputs": ["raw_public_page_body", "downloaded_pdf_path", "pdf_bytes"],
                "human_review_required": page_type in {"public_pdf", "public_form"},
            }
        )
        freshness_changes.append(
            {
                "freshness_change_id": _stable_id("freshness-change", source_id, canonical_url, freshness_status),
                "source_id": source_id,
                "canonical_url": canonical_url,
                "previous_content_hash": previous_hash or None,
                "current_content_hash": content_hash,
                "status": freshness_status,
                "observed_at": observed_at,
                "recrawl_priority": _recrawl_priority(page_type, freshness_status),
            }
        )
        review_prompts.extend(_review_prompts(capture, page_type, freshness_status, title))

    summary = PublicCaptureSummary(
        source_index_update_candidates=tuple(source_candidates),
        extraction_work_items=tuple(extraction_items),
        freshness_changes=tuple(freshness_changes),
        human_review_prompts=tuple(sorted(review_prompts, key=lambda item: item["prompt_id"])),
    )
    return summary.to_dict()


def load_capture_summary_fixture(path: Any) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, Mapping):
        raise PublicCaptureSummaryError("fixture payload must be an object")
    return summarize_public_capture_results(payload)


def _capture_list(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    captures = payload.get("captures", payload.get("capture_results"))
    if not isinstance(captures, list) or not all(isinstance(item, Mapping) for item in captures):
        raise PublicCaptureSummaryError("payload must include a captures list of objects")
    return captures


def _require_approved_fake_capture(capture: Mapping[str, Any]) -> None:
    if capture.get("no_raw_body_persisted") is not True:
        raise PublicCaptureSummaryError("capture must declare no_raw_body_persisted true")
    metadata = capture.get("processor_metadata")
    if not isinstance(metadata, Mapping) or metadata.get("transport") != "fake_public_capture":
        raise PublicCaptureSummaryError("capture must come from fake_public_capture transport")
    if metadata.get("network_requests_made") not in {0, "0"}:
        raise PublicCaptureSummaryError("fake capture summary requires zero network requests")
    if metadata.get("raw_body_persisted") is not False:
        raise PublicCaptureSummaryError("fake capture summary rejects persisted raw bodies")
    approval = capture.get("approval")
    approved = capture.get("approved") is True
    if isinstance(approval, Mapping):
        approved = approved or approval.get("status") == "approved"
    if not approved:
        raise PublicCaptureSummaryError("capture must be approved before summarization")


def _page_type(capture: Mapping[str, Any], content_type: str) -> str:
    explicit = _optional_text(capture, "page_type")
    if explicit:
        return explicit
    lowered = content_type.lower()
    if "pdf" in lowered:
        return "public_pdf"
    if "html" in lowered:
        return "public_html"
    return "public_metadata"


def _extraction_kind(content_type: str) -> str:
    lowered = content_type.lower()
    if "pdf" in lowered:
        return "pdf_metadata_and_requirement_extraction"
    if "html" in lowered:
        return "html_metadata_and_requirement_extraction"
    return "metadata_review"


def _freshness_status(http_status: int, previous_hash: str, content_hash: str) -> str:
    if http_status in {404, 410}:
        return "page_removed"
    if previous_hash and previous_hash != content_hash:
        return "content_hash_changed"
    if not previous_hash:
        return "new_source"
    return "metadata_refreshed"


def _recrawl_priority(page_type: str, freshness_status: str) -> str:
    if freshness_status in {"content_hash_changed", "page_removed"}:
        return "high"
    if page_type in {"devhub_public", "public_form", "public_pdf"}:
        return "normal"
    return "low"


def _review_prompts(capture: Mapping[str, Any], page_type: str, freshness_status: str, title: str) -> list[dict[str, Any]]:
    source_id = _required_text(capture, "source_id")
    canonical_url = _required_text(capture, "canonical_url")
    prompts: list[dict[str, Any]] = []
    if freshness_status in {"new_source", "content_hash_changed", "page_removed"}:
        prompts.append(
            {
                "prompt_id": _stable_id("review", source_id, canonical_url, freshness_status),
                "source_id": source_id,
                "canonical_url": canonical_url,
                "reason": freshness_status,
                "prompt": "Review metadata-only capture before promoting source-index or requirement changes.",
            }
        )
    if page_type in {"public_pdf", "public_form"}:
        prompts.append(
            {
                "prompt_id": _stable_id("review", source_id, canonical_url, "document-extraction"),
                "source_id": source_id,
                "canonical_url": canonical_url,
                "reason": "document_extraction_review",
                "prompt": "Confirm extracted PDF/form requirements from normalized document references only.",
            }
        )
    if title == source_id:
        prompts.append(
            {
                "prompt_id": _stable_id("review", source_id, canonical_url, "missing-title"),
                "source_id": source_id,
                "canonical_url": canonical_url,
                "reason": "missing_title_metadata",
                "prompt": "Add or verify a public title before publishing the source-index update.",
            }
        )
    return prompts


def _reject_raw_or_private_artifacts(value: Any, path: str = "$", key: str = "") -> None:
    if isinstance(value, Mapping):
        for nested_key, nested_value in value.items():
            lowered_key = str(nested_key).lower()
            if lowered_key in RAW_BODY_KEYS:
                raise PublicCaptureSummaryError("raw public body or downloaded PDF field is not allowed at %s.%s" % (path, nested_key))
            if lowered_key in PRIVATE_PATH_KEYS and isinstance(nested_value, str):
                _reject_private_path(nested_value, "%s.%s" % (path, nested_key))
            _reject_raw_or_private_artifacts(nested_value, "%s.%s" % (path, nested_key), lowered_key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_raw_or_private_artifacts(item, "%s[%d]" % (path, index), key)
    elif isinstance(value, str):
        if key in PRIVATE_PATH_KEYS:
            _reject_private_path(value, path)


def _reject_private_path(path: str, label: str) -> None:
    if not path:
        return
    if path.startswith("~") or _WINDOWS_DRIVE_RE.match(path):
        raise PublicCaptureSummaryError("local private path is not allowed at %s" % label)
    if PurePosixPath(path).is_absolute() or PureWindowsPath(path).is_absolute():
        raise PublicCaptureSummaryError("local private path is not allowed at %s" % label)
    if ".." in PurePosixPath(path).parts or ".." in PureWindowsPath(path).parts:
        raise PublicCaptureSummaryError("path traversal is not allowed at %s" % label)


def _validate_public_url(url: str, label: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise PublicCaptureSummaryError("%s must be an http or https URL" % label)
    lowered_path = parsed.path.lower()
    if any(marker in lowered_path for marker in AUTHENTICATED_PATH_MARKERS):
        raise PublicCaptureSummaryError("%s points at an authenticated URL path" % label)
    host = parsed.hostname or ""
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        lowered_host = host.lower()
        if lowered_host in {"localhost", "0.0.0.0"} or lowered_host.endswith(".local"):
            raise PublicCaptureSummaryError("%s uses a private host" % label)
        return
    if address.is_private or address.is_loopback or address.is_link_local:
        raise PublicCaptureSummaryError("%s uses a private host" % label)


def _required_text(values: Mapping[str, Any], key: str) -> str:
    value = values.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PublicCaptureSummaryError("missing required text field: %s" % key)
    return value


def _optional_text(values: Mapping[str, Any], key: str) -> str:
    value = values.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise PublicCaptureSummaryError("optional text field must be a string: %s" % key)
    return value


def _integer(value: Any, key: str) -> int:
    if isinstance(value, bool):
        raise PublicCaptureSummaryError("integer field must not be boolean: %s" % key)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise PublicCaptureSummaryError("invalid integer field: %s" % key) from exc


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\u001f".join(parts).encode("utf-8")).hexdigest()[:24]
    return "%s:%s" % (prefix, digest)


__all__ = [
    "PublicCaptureSummary",
    "PublicCaptureSummaryError",
    "load_capture_summary_fixture",
    "summarize_public_capture_results",
]
