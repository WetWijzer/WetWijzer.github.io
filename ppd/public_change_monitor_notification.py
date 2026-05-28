"""Fixture-first public PP&D change-monitor notification packets.

The packet is intentionally metadata-only: it carries changed hashes, changed
requirement identifiers, affected version identifiers, readiness blocks, and
human-review prompts without preserving raw public page bodies, downloaded
files, authenticated URLs, or agent recommendations that bypass review.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlparse

PROHIBITED_PUBLIC_BODY_KEYS = frozenset(
    {
        "body",
        "html",
        "raw_body",
        "raw_html",
        "page_body",
        "public_page_body",
        "normalized_text",
        "document_text",
        "downloaded_document",
        "raw_public_page_body",
    }
)

PROHIBITED_DOWNLOADED_PATH_KEYS = frozenset(
    {
        "download_path",
        "downloaded_document_path",
        "downloaded_pdf_path",
        "document_path",
        "local_document_path",
        "local_pdf_path",
        "pdf_path",
    }
)

SUPPORTED_CHANGE_KINDS = frozenset({"added", "removed", "changed"})

SUPPORTED_CHANGE_CATEGORIES = frozenset(
    {
        "deadline_or_expiration",
        "devhub_action_guidance",
        "document_requirement",
        "fee_payment_instruction",
        "file_rule",
        "permit_type",
        "source_hash",
    }
)

ACCEPTABLE_SOURCE_FRESHNESS_STATUSES = frozenset({"fresh", "verified_current"})

REQUIRED_PACKET_FIELDS = (
    "packet_id",
    "packet_kind",
    "generated_at",
    "source_change_basis",
    "source_hash_changes",
    "requirement_changes",
    "affected_versions",
    "blocked_readiness_reasons",
    "next_human_review_prompts",
)

_AUTHENTICATED_QUERY_KEYS = frozenset(
    {
        "access_token",
        "auth",
        "authorization",
        "code",
        "id_token",
        "password",
        "session",
        "sessionid",
        "state",
        "token",
    }
)

_PRIVATE_PATH_MARKERS = frozenset(
    {
        "account",
        "admin",
        "application",
        "applications",
        "auth",
        "checkout",
        "dashboard",
        "login",
        "my-permits",
        "payment",
        "payments",
        "permit",
        "permits",
        "profile",
        "signin",
        "sign-in",
        "submit",
        "upload",
    }
)


def build_public_change_monitor_notification(fixture: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe notification packet from a deterministic fixture."""
    _reject_unsafe_public_fields(fixture)
    _require_text(fixture, "packet_id")
    _require_text(fixture, "generated_at")
    source_changes = _source_hash_changes(fixture)
    requirement_changes = _requirement_changes(fixture)
    affected_versions = _affected_versions(fixture)
    blocked_reasons = _required_text_list(fixture, "blocked_readiness_reasons")
    review_prompts = _required_text_list(fixture, "next_human_review_prompts")

    packet: dict[str, Any] = {
        "packet_id": str(fixture["packet_id"]),
        "packet_kind": "public_change_monitor_notification",
        "generated_at": str(fixture["generated_at"]),
        "source_change_basis": str(fixture.get("source_change_basis", "fixture_only_public_metadata")),
        "source_hash_changes": source_changes,
        "requirement_change_summary": _requirement_change_summary(requirement_changes),
        "requirement_changes": requirement_changes,
        "affected_versions": affected_versions,
        "blocked_readiness_reasons": blocked_reasons,
        "next_human_review_prompts": review_prompts,
        "raw_public_page_bodies_included": False,
    }
    if "recommendations" in fixture:
        packet["recommendations"] = _recommendations(fixture)
    validate_public_change_monitor_notification_packet(packet)
    return packet


def validate_public_change_monitor_notification_packet(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a notification packet is incomplete or unsafe."""
    _reject_unsafe_public_fields(packet)
    for field in REQUIRED_PACKET_FIELDS:
        if field not in packet:
            raise ValueError(f"packet is missing {field}")
    if packet.get("packet_kind") != "public_change_monitor_notification":
        raise ValueError("packet_kind must be public_change_monitor_notification")
    if packet.get("raw_public_page_bodies_included") is not False:
        raise ValueError("raw_public_page_bodies_included must be false")
    if not str(packet.get("generated_at", "")).endswith("Z"):
        raise ValueError("generated_at must be an RFC3339 UTC timestamp ending in Z")

    source_changes = _required_sequence(packet, "source_hash_changes")
    source_ids: set[str] = set()
    for change in source_changes:
        if not isinstance(change, Mapping):
            raise ValueError("each source_hash_changes item must be an object")
        source_ids.add(_validate_hash_change(change))

    requirement_changes = _required_sequence(packet, "requirement_changes")
    seen_requirement_changes: set[str] = set()
    affected_process_ids: set[str] = set()
    affected_guardrail_ids: set[str] = set()
    for change in requirement_changes:
        if not isinstance(change, Mapping):
            raise ValueError("each requirement_changes item must be an object")
        change_id = _require_text(change, "change_id")
        if change_id in seen_requirement_changes:
            raise ValueError(f"duplicate requirement change id: {change_id}")
        seen_requirement_changes.add(change_id)
        kind = _require_text(change, "change_kind")
        if kind not in SUPPORTED_CHANGE_KINDS:
            raise ValueError(f"unsupported requirement change kind: {kind}")
        category = _require_text(change, "change_category")
        if category not in SUPPORTED_CHANGE_CATEGORIES:
            raise ValueError(f"unsupported requirement change category: {category}")
        _require_text(change, "requirement_id")
        source_id = _require_text(change, "source_id")
        if source_id not in source_ids:
            raise ValueError(f"requirement change references unknown source_id: {source_id}")
        process_ids = _required_text_list(change, "affected_process_ids")
        guardrail_ids = _required_text_list(change, "affected_guardrail_bundle_ids")
        affected_process_ids.update(process_ids)
        affected_guardrail_ids.update(guardrail_ids)
        if _require_text(change, "human_review_status") not in {"needs_human_review", "human_review_pending"}:
            raise ValueError("requirement changes must remain blocked for human review")

    affected_versions = packet.get("affected_versions")
    if not isinstance(affected_versions, Mapping):
        raise ValueError("affected_versions must be an object")
    process_versions = set(_required_text_list(affected_versions, "process_versions"))
    guardrail_versions = set(_required_text_list(affected_versions, "guardrail_bundle_versions"))
    if not affected_process_ids.issubset(process_versions):
        missing = sorted(affected_process_ids - process_versions)
        raise ValueError(f"affected_versions missing process ids: {missing}")
    if not affected_guardrail_ids.issubset(guardrail_versions):
        missing = sorted(affected_guardrail_ids - guardrail_versions)
        raise ValueError(f"affected_versions missing guardrail bundle ids: {missing}")
    _required_text_list(packet, "blocked_readiness_reasons")
    _required_text_list(packet, "next_human_review_prompts")
    if "recommendations" in packet:
        _validate_recommendations(_required_sequence(packet, "recommendations"))


def _source_hash_changes(fixture: Mapping[str, Any]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for item in _required_sequence(fixture, "source_hash_changes"):
        if not isinstance(item, Mapping):
            raise ValueError("each source_hash_changes item must be an object")
        _validate_hash_change(item)
        changes.append(
            {
                "source_id": str(item["source_id"]),
                "canonical_url": str(item["canonical_url"]),
                "previous_source_hash": str(item["previous_source_hash"]),
                "current_source_hash": str(item["current_source_hash"]),
                "change_reason": str(item["change_reason"]),
                "source_freshness_status": str(item["source_freshness_status"]),
                "source_last_verified_at": str(item["source_last_verified_at"]),
            }
        )
    return changes


def _requirement_changes(fixture: Mapping[str, Any]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for item in _required_sequence(fixture, "requirement_changes"):
        if not isinstance(item, Mapping):
            raise ValueError("each requirement_changes item must be an object")
        changes.append(
            {
                "change_id": _require_text(item, "change_id"),
                "change_kind": _require_text(item, "change_kind"),
                "change_category": _require_text(item, "change_category"),
                "requirement_id": _require_text(item, "requirement_id"),
                "requirement_type": _require_text(item, "requirement_type"),
                "source_id": _require_text(item, "source_id"),
                "affected_process_ids": _required_text_list(item, "affected_process_ids"),
                "affected_guardrail_bundle_ids": _required_text_list(item, "affected_guardrail_bundle_ids"),
                "human_review_status": _require_text(item, "human_review_status"),
            }
        )
    return changes


def _recommendations(fixture: Mapping[str, Any]) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    for item in _required_sequence(fixture, "recommendations"):
        if not isinstance(item, Mapping):
            raise ValueError("each recommendations item must be an object")
        recommendations.append(
            {
                "recommendation_id": _require_text(item, "recommendation_id"),
                "summary": _require_text(item, "summary"),
                "action_status": _require_text(item, "action_status"),
                "human_review_required": bool(item.get("human_review_required")),
            }
        )
    return recommendations


def _requirement_change_summary(changes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    added = sorted(str(change["requirement_id"]) for change in changes if change.get("change_kind") == "added")
    removed = sorted(str(change["requirement_id"]) for change in changes if change.get("change_kind") == "removed")
    changed = sorted(str(change["requirement_id"]) for change in changes if change.get("change_kind") == "changed")
    return {
        "added_requirement_ids": added,
        "removed_requirement_ids": removed,
        "changed_requirement_ids": changed,
        "added_count": len(added),
        "removed_count": len(removed),
        "changed_count": len(changed),
    }


def _affected_versions(fixture: Mapping[str, Any]) -> dict[str, list[str]]:
    value = fixture.get("affected_versions")
    if not isinstance(value, Mapping):
        raise ValueError("affected_versions must be an object")
    return {
        "process_versions": _required_text_list(value, "process_versions"),
        "guardrail_bundle_versions": _required_text_list(value, "guardrail_bundle_versions"),
    }


def _validate_hash_change(change: Mapping[str, Any]) -> str:
    source_id = _require_text(change, "source_id")
    canonical_url = _require_text(change, "canonical_url")
    _validate_public_ppd_url(canonical_url)
    previous_hash = _require_text(change, "previous_source_hash")
    current_hash = _require_text(change, "current_source_hash")
    if previous_hash == current_hash:
        raise ValueError(f"source hash must change for {source_id}")
    if not previous_hash.startswith("sha256:") or not current_hash.startswith("sha256:"):
        raise ValueError(f"source hashes must use sha256 for {source_id}")
    _require_text(change, "change_reason")
    freshness = _require_text(change, "source_freshness_status")
    if freshness not in ACCEPTABLE_SOURCE_FRESHNESS_STATUSES:
        raise ValueError(f"stale source freshness rejected for {source_id}: {freshness}")
    if not _require_text(change, "source_last_verified_at").endswith("Z"):
        raise ValueError(f"source_last_verified_at must end in Z for {source_id}")
    return source_id


def _validate_recommendations(recommendations: Sequence[Any]) -> None:
    seen: set[str] = set()
    for item in recommendations:
        if not isinstance(item, Mapping):
            raise ValueError("each recommendations item must be an object")
        recommendation_id = _require_text(item, "recommendation_id")
        if recommendation_id in seen:
            raise ValueError(f"duplicate recommendation id: {recommendation_id}")
        seen.add(recommendation_id)
        _require_text(item, "summary")
        if item.get("human_review_required") is not True:
            raise ValueError("recommendations must require human review")
        if _require_text(item, "action_status") != "blocked_until_human_review":
            raise ValueError("recommendations must be blocked_until_human_review")


def _reject_unsafe_public_fields(value: Any, path: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            normalized_key = _normalize_key(key_text)
            if normalized_key in {_normalize_key(item_key) for item_key in PROHIBITED_PUBLIC_BODY_KEYS}:
                raise ValueError(f"raw public page body field is not allowed: {path}.{key_text}")
            if normalized_key in {_normalize_key(item_key) for item_key in PROHIBITED_DOWNLOADED_PATH_KEYS}:
                raise ValueError(f"downloaded document path field is not allowed: {path}.{key_text}")
            _reject_unsafe_public_fields(item, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_unsafe_public_fields(item, f"{path}[{index}]")
    elif isinstance(value, str):
        _reject_unsafe_string(value, path)


def _reject_unsafe_string(value: str, path: str) -> None:
    stripped = value.strip()
    if not stripped:
        return
    if _looks_like_downloaded_document_path(stripped):
        raise ValueError(f"downloaded document path is not allowed: {path}")
    if stripped.startswith("http://") or stripped.startswith("https://"):
        if _is_private_or_authenticated_url(stripped):
            raise ValueError(f"private or authenticated URL is not allowed: {path}")


def _validate_public_ppd_url(url: str) -> None:
    if _is_private_or_authenticated_url(url):
        raise ValueError(f"private or authenticated URL is not allowed: {url}")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "www.portland.gov" or not parsed.path.startswith("/ppd/"):
        raise ValueError(f"canonical_url must be a public PP&D URL: {url}")


def _is_private_or_authenticated_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return True
    query_keys = {_normalize_key(part.split("=", 1)[0]) for part in parsed.query.split("&") if part}
    if query_keys.intersection(_AUTHENTICATED_QUERY_KEYS):
        return True
    path_parts = {_normalize_key(part) for part in parsed.path.split("/") if part}
    if parsed.netloc == "devhub.portlandoregon.gov" and path_parts.intersection(_PRIVATE_PATH_MARKERS):
        return True
    if parsed.netloc in {"www.portland.gov", "www.portlandoregon.gov"} and path_parts.intersection({"login", "signin", "sign-in", "account"}):
        return True
    return False


def _looks_like_downloaded_document_path(value: str) -> bool:
    lowered = value.lower()
    if lowered.startswith(("/tmp/", "/var/folders/", "/users/", "c:\\", "file://")):
        return True
    return ("/downloads/" in lowered or "\\downloads\\" in lowered) and lowered.endswith((".pdf", ".doc", ".docx"))


def _normalize_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def _required_sequence(entry: Mapping[str, Any], key: str) -> Sequence[Any]:
    value = entry.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    return value


def _required_text_list(entry: Mapping[str, Any], key: str) -> list[str]:
    value = _required_sequence(entry, key)
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key} must contain only non-empty strings")
        result.append(item)
    return result


def _require_text(entry: Mapping[str, Any], key: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value
