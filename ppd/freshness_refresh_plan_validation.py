"""Validation for freshness-refresh public crawl plans.

This module is intentionally narrow and deterministic. It validates plan-shaped
dictionaries before any live crawl is considered.
"""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlparse


@dataclass(frozen=True)
class PlanValidationIssue:
    code: str
    message: str


_PRIVATE_HOSTS = {"localhost", "ip6-localhost", "ip6-loopback", "0.0.0.0"}
_AUTH_QUERY_NAMES = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "bearer",
    "client_secret",
    "key",
    "password",
    "session",
    "sessionid",
    "sid",
    "signature",
    "token",
}
_AUTH_PATH_PARTS = {"admin", "auth", "login", "private", "session", "signin", "sso"}
_PUBLIC_SUFFIX_LIKE_HOSTS = {
    "biz",
    "com",
    "edu",
    "gov",
    "info",
    "io",
    "net",
    "org",
    "or.us",
    "us",
}
_FREQUENCY_KEYS = {"crawl_frequency", "frequency", "refresh_frequency"}
_RATE_LIMIT_KEYS = {"crawl_rate_limit", "politeness", "rate_limit", "rate_limit_policy"}
_RAW_BODY_PATH_KEYS = {
    "body_output_path",
    "raw_body_output_path",
    "raw_body_path",
    "raw_output_path",
    "response_body_path",
}
_DOWNLOADED_DOCUMENT_PATH_KEYS = {
    "document_output_path",
    "download_dir",
    "downloaded_document_path",
    "downloaded_document_paths",
    "downloaded_documents_path",
}
_URL_KEY_PARTS = ("url", "uri", "href")
_HOST_EXPANSION_KEYS = {
    "allowed_domains",
    "allowed_hosts",
    "crawl_domains",
    "crawl_hosts",
    "domains",
    "host_expansion",
    "include_hosts",
}


def validate_freshness_refresh_plan(plan: dict[str, Any]) -> list[PlanValidationIssue]:
    """Return validation issues that prevent a live public crawl.

    The validator accepts ordinary dictionaries so fixtures and daemon callers do
    not need a shared contract change.
    """

    issues: list[PlanValidationIssue] = []
    urls = list(_collect_url_values(plan))

    if not _has_present_key(plan, _FREQUENCY_KEYS):
        issues.append(
            PlanValidationIssue(
                "missing_crawl_frequency",
                "freshness-refresh crawl plans must declare crawl frequency",
            )
        )

    if not _has_present_key(plan, _RATE_LIMIT_KEYS):
        issues.append(
            PlanValidationIssue(
                "missing_rate_limit_policy",
                "freshness-refresh crawl plans must declare a rate-limit policy",
            )
        )

    for url in urls:
        issue = _validate_public_url(url)
        if issue is not None:
            issues.append(issue)

    for host in _collect_host_expansion_values(plan):
        issue = _validate_host_expansion(host)
        if issue is not None:
            issues.append(issue)

    for key, value in _walk_items(plan):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _RAW_BODY_PATH_KEYS and _has_value(value):
            issues.append(
                PlanValidationIssue(
                    "raw_body_output_path_refused",
                    f"raw body output path is not allowed for live crawl plans: {key}",
                )
            )
        if normalized_key in _DOWNLOADED_DOCUMENT_PATH_KEYS and _has_value(value):
            issues.append(
                PlanValidationIssue(
                    "downloaded_document_path_refused",
                    f"downloaded document path is not allowed for live crawl plans: {key}",
                )
            )

    return _dedupe_issues(issues)


def assert_freshness_refresh_plan_is_live_crawl_safe(plan: dict[str, Any]) -> None:
    issues = validate_freshness_refresh_plan(plan)
    if issues:
        details = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        raise ValueError(f"freshness-refresh plan refused: {details}")


def _collect_url_values(value: Any) -> Iterable[str]:
    for key, item in _walk_items(value):
        normalized_key = key.lower().replace("-", "_")
        if any(part in normalized_key for part in _URL_KEY_PARTS):
            if isinstance(item, str):
                yield item
            elif isinstance(item, list):
                for nested in item:
                    if isinstance(nested, str):
                        yield nested


def _collect_host_expansion_values(value: Any) -> Iterable[str]:
    for key, item in _walk_items(value):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _HOST_EXPANSION_KEYS:
            if isinstance(item, str):
                yield item
            elif isinstance(item, list):
                for nested in item:
                    if isinstance(nested, str):
                        yield nested


def _walk_items(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            yield key_text, item
            yield from _walk_items(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_items(item)


def _has_present_key(value: Any, names: set[str]) -> bool:
    for key, item in _walk_items(value):
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in names and _has_value(item):
            return True
    return False


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _validate_public_url(url: str) -> PlanValidationIssue | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return PlanValidationIssue("private_or_authenticated_url", f"URL is not a public HTTP(S) URL: {url}")
    if parsed.username or parsed.password:
        return PlanValidationIssue("private_or_authenticated_url", f"URL embeds credentials: {url}")

    hostname = (parsed.hostname or "").lower().rstrip(".")
    if not hostname:
        return PlanValidationIssue("private_or_authenticated_url", f"URL is missing a host: {url}")
    if hostname in _PRIVATE_HOSTS or hostname.endswith(".local") or hostname.endswith(".internal"):
        return PlanValidationIssue("private_or_authenticated_url", f"URL host is private: {url}")

    try:
        address = ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        return PlanValidationIssue("private_or_authenticated_url", f"URL host is not globally routable: {url}")

    query_names = {name.lower() for name, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_names & _AUTH_QUERY_NAMES:
        return PlanValidationIssue("private_or_authenticated_url", f"URL contains authentication query material: {url}")

    path_parts = {part.lower() for part in parsed.path.split("/") if part}
    if path_parts & _AUTH_PATH_PARTS:
        return PlanValidationIssue("private_or_authenticated_url", f"URL path appears authenticated or private: {url}")

    return None


def _validate_host_expansion(host: str) -> PlanValidationIssue | None:
    normalized = host.strip().lower().rstrip(".")
    if not normalized:
        return PlanValidationIssue("over_broad_host_expansion", "host expansion contains an empty host")
    if normalized in {"*", ".*"} or normalized.startswith("*.") or normalized.startswith("."):
        return PlanValidationIssue("over_broad_host_expansion", f"host expansion is over-broad: {host}")
    if "://" in normalized or "/" in normalized:
        return PlanValidationIssue("over_broad_host_expansion", f"host expansion must be a host, not a URL or path: {host}")
    if normalized in _PUBLIC_SUFFIX_LIKE_HOSTS or normalized.count(".") == 0:
        return PlanValidationIssue("over_broad_host_expansion", f"host expansion is too broad: {host}")
    return None


def _dedupe_issues(issues: list[PlanValidationIssue]) -> list[PlanValidationIssue]:
    seen: set[tuple[str, str]] = set()
    deduped: list[PlanValidationIssue] = []
    for issue in issues:
        key = (issue.code, issue.message)
        if key not in seen:
            seen.add(key)
            deduped.append(issue)
    return deduped
