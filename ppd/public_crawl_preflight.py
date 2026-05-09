"""Public crawl preflight decisions for PP&D discovery.

This module is intentionally small and deterministic. It decides whether a URL is
eligible for a public HTML crawl before any browser or network work begins.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlparse

PUBLIC_ALLOWLIST_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
    }
)

LINKED_PUBLIC_ALLOWLIST_HOSTS = frozenset({"www.portlandmaps.com"})
SUPPORTED_SCHEMES = frozenset({"http", "https"})
SUPPORTED_CONTENT_TYPES = frozenset({"text/html", "application/xhtml+xml"})

PRIVATE_PATH_MARKERS = (
    "/login",
    "/logout",
    "/admin",
    "/user",
    "/users",
    "/account",
    "/accounts",
    "/session",
    "/sessions",
    "/oauth",
    "/saml",
    "/auth",
)

AUTH_QUERY_MARKERS = (
    "token=",
    "access_token=",
    "id_token=",
    "session=",
    "sessionid=",
    "auth=",
    "code=",
)


@dataclass(frozen=True)
class PublicCrawlPreflightDecision:
    """A deterministic crawl eligibility result."""

    allowed: bool
    reason: str
    url: str
    host: str


def public_crawl_preflight_decision(
    url: str,
    *,
    content_type: str | None = "text/html",
    linked_from_allowlisted_public_page: bool = False,
    raw_download: bool = False,
    headers: Mapping[str, str] | None = None,
) -> PublicCrawlPreflightDecision:
    """Return whether a URL may be crawled as public HTML.

    The decision is fixture-friendly: callers provide any observed content type,
    raw-download intent, and headers without performing network access here.
    """

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()

    if scheme not in SUPPORTED_SCHEMES:
        return PublicCrawlPreflightDecision(False, "unsupported-scheme", url, host)

    if host not in PUBLIC_ALLOWLIST_HOSTS:
        linked_public_host = host in LINKED_PUBLIC_ALLOWLIST_HOSTS
        if not (linked_public_host and linked_from_allowlisted_public_page):
            return PublicCrawlPreflightDecision(False, "outside-allowlist", url, host)

    if _is_private_or_authenticated(parsed.path, parsed.query):
        return PublicCrawlPreflightDecision(False, "private-authenticated", url, host)

    if raw_download or _has_attachment_disposition(headers):
        return PublicCrawlPreflightDecision(False, "raw-download-not-permitted", url, host)

    normalized_content_type = _normalize_content_type(content_type)
    if normalized_content_type not in SUPPORTED_CONTENT_TYPES:
        return PublicCrawlPreflightDecision(False, "unsupported-content-type", url, host)

    return PublicCrawlPreflightDecision(True, "public-html-allowed", url, host)


def _normalize_content_type(content_type: str | None) -> str:
    if not content_type:
        return ""
    return content_type.split(";", 1)[0].strip().lower()


def _has_attachment_disposition(headers: Mapping[str, str] | None) -> bool:
    if not headers:
        return False
    for key, value in headers.items():
        if key.lower() == "content-disposition" and "attachment" in value.lower():
            return True
    return False


def _is_private_or_authenticated(path: str, query: str) -> bool:
    normalized_path = "/" + path.strip("/").lower()
    if any(normalized_path == marker or normalized_path.startswith(marker + "/") for marker in PRIVATE_PATH_MARKERS):
        return True

    normalized_query = query.lower()
    return any(marker in normalized_query for marker in AUTH_QUERY_MARKERS)
