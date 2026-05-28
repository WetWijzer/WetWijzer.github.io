"""Fixture-first source freshness review packets for PP&D public sources.

The packet builder is intentionally offline-only: it accepts committed metadata
fixtures or in-memory dictionaries and refuses raw page bodies. It is meant to
help reviewers decide what to recrawl and which requirements need attention
before any live crawl is scheduled.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping
from urllib.parse import parse_qsl, urlparse

RAW_BODY_KEYS = frozenset(
    {
        "body",
        "raw_body",
        "raw_html",
        "html",
        "text",
        "content",
        "document_text",
        "page_source",
        "screenshot",
        "trace",
        "har",
    }
)

DOWNLOADED_DOCUMENT_PATH_KEYS = frozenset(
    {
        "downloaded_document_path",
        "downloaded_path",
        "local_document_path",
        "local_download_path",
        "document_path",
        "filesystem_path",
        "file_path",
        "path",
    }
)

HASH_KEYS = frozenset({"content_hash", "last_content_hash", "source_hash"})
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

URL_KEYS = frozenset(
    {
        "canonical_url",
        "requested_url",
        "url",
        "source_url",
        "final_url",
    }
)

PRIVATE_PATH_MARKERS = (
    "/login",
    "/signin",
    "/sign-in",
    "/register",
    "/auth",
    "/oauth",
    "/account",
    "/dashboard",
    "/my-permits",
    "/myrequests",
    "/my-requests",
    "/permit/",
    "/permits/",
    "/applications/",
    "/inspections/",
)

PRIVATE_QUERY_MARKERS = (
    "access_token",
    "auth",
    "code",
    "cookie",
    "jwt",
    "password",
    "permit_number",
    "session",
    "state",
    "token",
)

READY_GUARDRAIL_STATUSES = frozenset({"ready", "approved", "complete", "completed", "validated"})
PENDING_HUMAN_REVIEW_STATUSES = frozenset(
    {
        "human_review_required",
        "needs_human_review",
        "needs_review",
        "pending",
        "pending_human_review",
        "required",
        "unreviewed",
    }
)

DEFAULT_CADENCE_BY_SOURCE_TYPE = {
    "devhub_public": "daily",
    "public_html": "weekly",
    "public_form": "weekly",
    "public_pdf": "monthly",
    "external_reference": "monthly",
}

HIGH_ATTENTION_HINTS = (
    "fee",
    "payment",
    "deadline",
    "expiration",
    "upload",
    "file naming",
    "required document",
    "permit type",
    "devhub action",
    "certification",
)


@dataclass(frozen=True)
class SourceFreshnessReviewItem:
    source_id: str
    canonical_url: str
    source_type: str
    recrawl_cadence: str
    previous_hash: str | None
    latest_hash: str | None
    hash_changed: bool
    freshness_status: str
    affected_requirement_ids: tuple[str, ...]
    human_review_prompts: tuple[str, ...]
    no_raw_body_persisted: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "canonical_url": self.canonical_url,
            "source_type": self.source_type,
            "recrawl_cadence": self.recrawl_cadence,
            "previous_hash": self.previous_hash,
            "latest_hash": self.latest_hash,
            "hash_changed": self.hash_changed,
            "freshness_status": self.freshness_status,
            "affected_requirement_ids": list(self.affected_requirement_ids),
            "human_review_prompts": list(self.human_review_prompts),
            "no_raw_body_persisted": self.no_raw_body_persisted,
        }


@dataclass(frozen=True)
class SourceFreshnessReviewPacket:
    packet_id: str
    generated_at: str
    review_mode: str
    items: tuple[SourceFreshnessReviewItem, ...]
    raw_body_persisted: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "generated_at": self.generated_at,
            "review_mode": self.review_mode,
            "raw_body_persisted": self.raw_body_persisted,
            "items": [item.as_dict() for item in self.items],
        }


def load_fixture(path: str | Path) -> dict[str, Any]:
    """Load a JSON fixture and fail if it contains unsafe review-packet data."""

    fixture_path = Path(path)
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    validate_source_freshness_review_fixture(data)
    return data


def build_source_freshness_review_packet(
    fixture: Mapping[str, Any], *, generated_at: str | None = None
) -> dict[str, Any]:
    """Build an offline freshness packet from registry and capture-summary data."""

    validate_source_freshness_review_fixture(fixture)
    registry_entries = _require_list(fixture, "source_registry")
    capture_summaries = _require_list(fixture, "public_capture_summaries")
    requirement_index = fixture.get("requirement_index", {})
    if not isinstance(requirement_index, Mapping):
        raise ValueError("requirement_index must be an object mapping source IDs to requirement IDs")

    captures_by_source_id = {
        _required_string(capture, "source_id"): capture for capture in capture_summaries
    }

    items: list[SourceFreshnessReviewItem] = []
    for entry in registry_entries:
        source_id = _required_string(entry, "source_id")
        source_type = _required_string(entry, "source_type")
        canonical_url = _required_string(entry, "canonical_url")
        capture = captures_by_source_id.get(source_id, {})

        previous_hash = _first_string(entry, "content_hash", "last_content_hash", "source_hash")
        latest_hash = _first_string(capture, "content_hash", "source_hash")
        hash_changed = bool(previous_hash and latest_hash and previous_hash != latest_hash)
        if hash_changed and (_has_ready_guardrail_status(entry) or _has_ready_guardrail_status(capture)):
            raise ValueError(f"{source_id} cannot mark guardrails ready while source freshness requires human review")

        freshness_status = _freshness_status(entry, capture, hash_changed)
        affected_requirement_ids = tuple(sorted(_requirement_ids(requirement_index, source_id)))

        item = SourceFreshnessReviewItem(
            source_id=source_id,
            canonical_url=canonical_url,
            source_type=source_type,
            recrawl_cadence=_recrawl_cadence(entry),
            previous_hash=previous_hash,
            latest_hash=latest_hash,
            hash_changed=hash_changed,
            freshness_status=freshness_status,
            affected_requirement_ids=affected_requirement_ids,
            human_review_prompts=tuple(
                _human_review_prompts(
                    entry=entry,
                    capture=capture,
                    hash_changed=hash_changed,
                    affected_requirement_ids=affected_requirement_ids,
                )
            ),
        )
        items.append(item)

    generated = generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    packet_id = _stable_packet_id(generated, items)
    packet = SourceFreshnessReviewPacket(
        packet_id=packet_id,
        generated_at=generated,
        review_mode="fixture-first-offline",
        items=tuple(items),
    )
    return packet.as_dict()


def validate_source_freshness_review_fixture(fixture: Mapping[str, Any]) -> None:
    """Reject unsafe or under-linked source freshness review packet inputs."""

    assert_no_raw_body(fixture)
    assert_no_downloaded_document_paths(fixture)
    _assert_no_private_urls(fixture)
    _assert_no_premature_ready_guardrails(fixture)
    _assert_valid_hashes(fixture)

    registry_entries = _require_list(fixture, "source_registry")
    capture_summaries = _require_list(fixture, "public_capture_summaries")
    requirement_index = fixture.get("requirement_index", {})
    if not isinstance(requirement_index, Mapping):
        raise ValueError("requirement_index must be an object mapping source IDs to requirement IDs")

    source_ids: set[str] = set()
    for index, entry in enumerate(registry_entries):
        source_id = _required_string(entry, "source_id")
        if source_id in source_ids:
            raise ValueError(f"duplicate source_id in source_registry: {source_id}")
        source_ids.add(source_id)
        _assert_public_source_entry(entry, f"source_registry[{index}]")
        if not tuple(_requirement_ids(requirement_index, source_id)):
            raise ValueError(f"missing affected requirement links for {source_id}")

    for index, capture in enumerate(capture_summaries):
        source_id = _required_string(capture, "source_id")
        if source_id not in source_ids:
            raise ValueError(f"public_capture_summaries[{index}] references unknown source_id: {source_id}")
        if capture.get("no_raw_body_persisted") is False:
            raise ValueError(f"public_capture_summaries[{index}] persisted a raw body")

    for source_id in requirement_index:
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("requirement_index contains an invalid source ID")
        if source_id not in source_ids:
            raise ValueError(f"requirement_index references unknown source_id: {source_id}")


def assert_no_raw_body(value: Any, path: str = "$") -> None:
    """Reject fixtures that accidentally persist raw public or private bodies."""

    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            if key_text.lower() in RAW_BODY_KEYS:
                raise ValueError(f"raw body persistence is not allowed at {path}.{key_text}")
            assert_no_raw_body(nested, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            assert_no_raw_body(nested, f"{path}[{index}]")


def assert_no_downloaded_document_paths(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            if key_text.lower() in DOWNLOADED_DOCUMENT_PATH_KEYS and isinstance(nested, str) and nested.strip():
                raise ValueError(f"downloaded document paths are not allowed at {path}.{key_text}")
            if isinstance(nested, str) and nested.startswith("file://"):
                raise ValueError(f"downloaded document paths are not allowed at {path}.{key_text}")
            assert_no_downloaded_document_paths(nested, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            assert_no_downloaded_document_paths(nested, f"{path}[{index}]")


def _assert_public_source_entry(entry: Mapping[str, Any], path: str) -> None:
    source_type = _required_string(entry, "source_type")
    if source_type == "devhub_authenticated":
        raise ValueError(f"{path} uses authenticated source_type")
    privacy = str(entry.get("privacy_classification", "public")).lower()
    if privacy not in {"public", "public_metadata"}:
        raise ValueError(f"{path} is not public source metadata")
    _assert_public_url(_required_string(entry, "canonical_url"), f"{path}.canonical_url")


def _assert_no_private_urls(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            nested_path = f"{path}.{key_text}"
            if key_text.lower() in URL_KEYS and isinstance(nested, str):
                _assert_public_url(nested, nested_path)
            elif key_text == "redirect_chain" and isinstance(nested, list):
                for index, url in enumerate(nested):
                    if isinstance(url, str):
                        _assert_public_url(url, f"{nested_path}[{index}]")
            _assert_no_private_urls(nested, nested_path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_private_urls(nested, f"{path}[{index}]")


def _assert_public_url(url: str, path: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"private or unsupported URL at {path}: {url}")
    if parsed.username or parsed.password:
        raise ValueError(f"private/authenticated URL at {path}: {url}")
    lowered_path = parsed.path.lower()
    if any(marker in lowered_path for marker in PRIVATE_PATH_MARKERS):
        raise ValueError(f"private/authenticated URL at {path}: {url}")
    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    if any(marker in query_keys for marker in PRIVATE_QUERY_MARKERS):
        raise ValueError(f"private/authenticated URL at {path}: {url}")


def _assert_valid_hashes(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            nested_path = f"{path}.{key_text}"
            if key_text in HASH_KEYS and nested is not None:
                if not isinstance(nested, str) or not SHA256_RE.fullmatch(nested):
                    raise ValueError(f"invented or invalid sha256 hash at {nested_path}")
            _assert_valid_hashes(nested, nested_path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_valid_hashes(nested, f"{path}[{index}]")


def _assert_no_premature_ready_guardrails(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        if _has_ready_guardrail_status(value) and _human_review_still_required(value):
            raise ValueError(f"guardrail status cannot be ready while human review is still required at {path}")
        for key, nested in value.items():
            _assert_no_premature_ready_guardrails(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_premature_ready_guardrails(nested, f"{path}[{index}]")


def _has_ready_guardrail_status(value: Mapping[str, Any]) -> bool:
    for key, nested in value.items():
        key_text = str(key).lower()
        if "guardrail" in key_text and "status" in key_text:
            if isinstance(nested, str) and nested.strip().lower() in READY_GUARDRAIL_STATUSES:
                return True
    return False


def _human_review_still_required(value: Mapping[str, Any]) -> bool:
    if value.get("human_review_required") is True:
        return True
    for key in ("human_review_status", "review_status"):
        status = value.get(key)
        if isinstance(status, str) and status.strip().lower() in PENDING_HUMAN_REVIEW_STATUSES:
            return True
    return False


def _require_list(fixture: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = fixture.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{key}[{index}] must be an object")
    return value


def _required_string(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _first_string(mapping: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _recrawl_cadence(entry: Mapping[str, Any]) -> str:
    crawl_frequency = entry.get("crawl_frequency")
    if isinstance(crawl_frequency, str) and crawl_frequency:
        return crawl_frequency
    source_type = _required_string(entry, "source_type")
    return DEFAULT_CADENCE_BY_SOURCE_TYPE.get(source_type, "monthly")


def _freshness_status(entry: Mapping[str, Any], capture: Mapping[str, Any], hash_changed: bool) -> str:
    if hash_changed:
        return "changed_needs_review"
    capture_status = capture.get("capture_status")
    if capture_status == "skipped":
        return "capture_skipped_needs_review"
    entry_status = entry.get("freshness_status")
    if isinstance(entry_status, str) and entry_status:
        return entry_status
    if capture:
        return "unchanged"
    return "missing_capture_summary"


def _requirement_ids(requirement_index: Mapping[str, Any], source_id: str) -> Iterable[str]:
    ids = requirement_index.get(source_id, [])
    if not isinstance(ids, list):
        raise ValueError(f"requirement_index.{source_id} must be a list")
    for requirement_id in ids:
        if not isinstance(requirement_id, str) or not requirement_id:
            raise ValueError(f"requirement_index.{source_id} contains an invalid requirement ID")
        yield requirement_id


def _human_review_prompts(
    *,
    entry: Mapping[str, Any],
    capture: Mapping[str, Any],
    hash_changed: bool,
    affected_requirement_ids: tuple[str, ...],
) -> list[str]:
    source_id = _required_string(entry, "source_id")
    prompts: list[str] = []

    if not capture:
        prompts.append(
            f"Review {source_id}: no public capture summary fixture is available; schedule metadata-only recrawl preflight."
        )
        return prompts

    changed_topics = _changed_topics(capture)
    if hash_changed:
        prompts.append(
            f"Review {source_id}: source hash changed; compare normalized extraction before updating guardrails."
        )
    if affected_requirement_ids:
        prompts.append(
            "Confirm whether affected requirements still match source guidance: "
            + ", ".join(affected_requirement_ids)
            + "."
        )
    if changed_topics:
        prompts.append(
            "Check public summary change topics for requirement impact: "
            + ", ".join(changed_topics)
            + "."
        )
    if any(_topic_needs_priority_review(topic) for topic in changed_topics):
        prompts.append(
            "Escalate for human review before changing fee, deadline, upload, file rule, permit type, or DevHub action gates."
        )
    if capture.get("capture_status") == "skipped":
        reason = capture.get("skipped_reason", "unspecified")
        prompts.append(f"Review skipped capture reason for {source_id}: {reason}.")
    if not prompts:
        prompts.append(f"No hash change detected for {source_id}; keep cadence and monitor next fixture refresh.")
    return prompts


def _changed_topics(capture: Mapping[str, Any]) -> list[str]:
    topics = capture.get("changed_topics", [])
    if topics is None:
        return []
    if not isinstance(topics, list):
        raise ValueError("changed_topics must be a list when present")
    result: list[str] = []
    for topic in topics:
        if not isinstance(topic, str):
            raise ValueError("changed_topics entries must be strings")
        result.append(topic)
    return result


def _topic_needs_priority_review(topic: str) -> bool:
    normalized = topic.strip().lower()
    return any(hint in normalized for hint in HIGH_ATTENTION_HINTS)


def _stable_packet_id(generated_at: str, items: Iterable[SourceFreshnessReviewItem]) -> str:
    digest_input = {
        "generated_at": generated_at,
        "sources": [
            {
                "source_id": item.source_id,
                "previous_hash": item.previous_hash,
                "latest_hash": item.latest_hash,
                "affected_requirement_ids": list(item.affected_requirement_ids),
            }
            for item in items
        ],
    }
    encoded = json.dumps(digest_input, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "source-freshness-" + hashlib.sha256(encoded).hexdigest()[:16]


def today_iso() -> str:
    return date.today().isoformat()
