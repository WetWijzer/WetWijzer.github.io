"""Fail-closed validation for public crawl readiness handoff packets.

This module intentionally validates plain dictionaries so deterministic fixtures and
handoff packets can be checked before any browser or network automation is allowed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from ipaddress import ip_address
from typing import Any
from urllib.parse import urlparse

MAX_ANCHOR_AGE_DAYS = 30
_ALLOWED_ROBOTS_STATUSES = {"allowed", "permitted", "public_allowed"}
_ALLOWED_POLICY_STATUSES = {"approved", "allowed", "public", "public_allowed"}
_FORBIDDEN_ARTIFACT_KEYS = {
    "body",
    "content",
    "download_path",
    "downloaded_document_path",
    "downloaded_document_paths",
    "document_path",
    "document_paths",
    "html",
    "local_document_path",
    "local_path",
    "raw_body",
    "raw_content",
    "raw_html",
    "response_body",
    "saved_path",
}
_LIVE_NETWORK_KEYS = {
    "allow_live_network",
    "allow_network",
    "execute_live",
    "live_crawl",
    "live_network",
    "network_enabled",
    "run_live",
    "use_live_network",
}
_AUTH_QUERY_MARKERS = (
    "access_token",
    "api_key",
    "auth",
    "bearer",
    "client_secret",
    "code",
    "jwt",
    "key",
    "oauth",
    "password",
    "private_key",
    "secret",
    "session",
    "sid",
    "signature",
    "signed",
    "token",
)
_AUTH_PATH_MARKERS = (
    "/account",
    "/admin",
    "/auth",
    "/dashboard",
    "/login",
    "/logout",
    "/oauth",
    "/private",
    "/session",
    "/signin",
    "/sso",
    "/user/",
)


def validate_public_crawl_readiness(
    packet: dict[str, Any],
    *,
    now: datetime | None = None,
    max_anchor_age_days: int = MAX_ANCHOR_AGE_DAYS,
) -> list[str]:
    """Return validation errors for a public crawl readiness handoff packet."""

    checked_at = now or datetime.now(timezone.utc)
    if checked_at.tzinfo is None:
        checked_at = checked_at.replace(tzinfo=timezone.utc)

    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be a dictionary"]

    _collect_forbidden_artifacts(packet, errors, "packet")
    _collect_live_network_flags(packet, errors, "packet")

    urls = _packet_urls(packet)
    if not urls:
        errors.append("packet must include at least one public source URL")
    for url in urls:
        reason = _unsafe_public_url_reason(url)
        if reason is not None:
            errors.append(f"unsafe public URL {url!r}: {reason}")

    anchors = _packet_anchors(packet)
    if not anchors:
        errors.append("packet must include at least one source anchor")
    for index, anchor in enumerate(anchors):
        location = f"source_anchors[{index}]"
        if not isinstance(anchor, dict):
            errors.append(f"{location} must be a dictionary")
            continue
        _collect_forbidden_artifacts(anchor, errors, location)
        _collect_live_network_flags(anchor, errors, location)
        anchor_url = _first_string(anchor, ("url", "href", "source_url"))
        if not anchor_url:
            errors.append(f"{location} must include a source URL")
        else:
            reason = _unsafe_public_url_reason(anchor_url)
            if reason is not None:
                errors.append(f"unsafe source anchor URL {anchor_url!r}: {reason}")
        observed_at = _first_string(anchor, ("observed_at", "retrieved_at", "fetched_at", "accessed_at", "checked_at"))
        if not observed_at:
            errors.append(f"{location} must include an observed_at/retrieved_at timestamp")
        else:
            parsed = _parse_datetime(observed_at)
            if parsed is None:
                errors.append(f"{location} timestamp must be ISO-8601")
            elif (checked_at - parsed).days > max_anchor_age_days:
                errors.append(f"{location} timestamp is stale")

    robots_status = _normalized_status(packet, ("robots_status", "robots_txt_status", "robots"))
    if robots_status not in _ALLOWED_ROBOTS_STATUSES:
        errors.append("robots status must be explicitly allowed")

    policy_status = _normalized_status(packet, ("policy_status", "crawl_policy_status", "public_policy_status"))
    if policy_status not in _ALLOWED_POLICY_STATUSES:
        errors.append("policy status must be explicitly approved for public crawling")

    if not _has_rate_limit(packet):
        errors.append("packet must include a positive crawl rate limit")

    return errors


def assert_public_crawl_ready(packet: dict[str, Any], **kwargs: Any) -> None:
    """Raise ValueError when a handoff packet is not ready for public crawling."""

    errors = validate_public_crawl_readiness(packet, **kwargs)
    if errors:
        raise ValueError("public crawl readiness validation failed: " + "; ".join(errors))


def _packet_anchors(packet: dict[str, Any]) -> list[Any]:
    for key in ("source_anchors", "anchors", "sources"):
        value = packet.get(key)
        if isinstance(value, list):
            return value
    return []


def _packet_urls(packet: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for key in ("url", "source_url", "start_url"):
        value = packet.get(key)
        if isinstance(value, str):
            urls.append(value)
    value = packet.get("urls")
    if isinstance(value, list):
        urls.extend(item for item in value if isinstance(item, str))
    return urls


def _collect_forbidden_artifacts(value: Any, errors: list[str], path: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in _FORBIDDEN_ARTIFACT_KEYS and item not in (None, "", [], {}):
                errors.append(f"{child_path} must not include raw bodies or downloaded document paths")
            _collect_forbidden_artifacts(item, errors, child_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _collect_forbidden_artifacts(item, errors, f"{path}[{index}]")


def _collect_live_network_flags(value: Any, errors: list[str], path: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in _LIVE_NETWORK_KEYS and item is True:
                errors.append(f"{child_path} must not enable live-network execution")
            _collect_live_network_flags(item, errors, child_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _collect_live_network_flags(item, errors, f"{path}[{index}]")


def _unsafe_public_url_reason(url: str) -> str | None:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        return "URL must use http or https"
    if parsed.username or parsed.password:
        return "URL must not include credentials"
    host = parsed.hostname
    if not host:
        return "URL must include a host"
    host_lower = host.lower()
    if host_lower in {"localhost", "localhost.localdomain"} or host_lower.endswith(".local"):
        return "URL host is local/private"
    try:
        address = ip_address(host_lower)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        return "URL host is private or non-public"
    path_lower = parsed.path.lower()
    if any(marker in path_lower for marker in _AUTH_PATH_MARKERS):
        return "URL path appears authenticated or private"
    query_lower = parsed.query.lower()
    if any(marker in query_lower for marker in _AUTH_QUERY_MARKERS):
        return "URL query appears to contain authentication material"
    return None


def _normalized_status(packet: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = packet.get(key)
        if isinstance(value, str):
            normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
            if normalized:
                return normalized
        if isinstance(value, dict):
            nested = _normalized_status(value, ("status", "state", "decision"))
            if nested:
                return nested
    return None


def _has_rate_limit(packet: dict[str, Any]) -> bool:
    candidates = [packet.get("rate_limit"), packet.get("rate_limits"), packet.get("crawl_rate_limit")]
    for candidate in candidates:
        if isinstance(candidate, dict):
            for key in ("requests_per_minute", "requests_per_hour", "min_delay_seconds", "crawl_delay_seconds"):
                if _positive_number(candidate.get(key)):
                    return True
        elif _positive_number(candidate):
            return True
    return False


def _positive_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        try:
            return float(value) > 0
        except ValueError:
            return False
    return False


def _first_string(packet: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = packet.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _parse_datetime(value: str) -> datetime | None:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
