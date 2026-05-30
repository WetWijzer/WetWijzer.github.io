"""Validation for public source refresh launch rehearsal transcript packets.

The validator is intentionally local and deterministic. It rejects packets that look
like they could launch or mutate a real public-source refresh instead of recording
a cited, metadata-only rehearsal transcript.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlparse

_ALLOWED_URL_HOSTS = {
    "portland.gov",
    "www.portland.gov",
    "efiles.portlandoregon.gov",
}

_AUTH_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "bearer",
    "client_secret",
    "code",
    "jwt",
    "key",
    "oauth_token",
    "password",
    "refresh_token",
    "secret",
    "session",
    "sid",
    "signature",
    "signed",
    "token",
}

_LIVE_COMMAND_RE = re.compile(
    r"\b(curl|wget|aria2c|httpie|python\s+-m\s+requests|requests\.|httpx\.|urllib\.|fetch\s*\(|playwright|selenium|scrapy|crawl|scrape|download|fetch)\b",
    re.IGNORECASE,
)

_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(will\s+(be\s+)?(approved|accepted|issued|granted|permitted)|guarantee[sd]?|ensures?|shall\s+(be\s+)?(approved|accepted|issued|granted|permitted)|permit\s+will\s+issue|approval\s+is\s+guaranteed)\b",
    re.IGNORECASE,
)

_RAW_ARTIFACT_RE = re.compile(
    r"(^|/)(raw|crawl|downloads?|artifacts?)/|\.(html?|pdf|docx?|xlsx?|zip|tar|gz|png|jpe?g|webp)$",
    re.IGNORECASE,
)

_MUTATION_FLAGS = (
    "registry_mutation",
    "schedule_mutation",
    "source_mutation",
    "requirement_mutation",
    "guardrail_mutation",
    "monitoring_mutation",
    "release_state_mutation",
    "mutates_registry",
    "mutates_schedule",
    "mutates_sources",
    "mutates_requirements",
    "mutates_guardrails",
    "mutates_monitoring",
    "mutates_release_state",
    "active_registry_mutation",
    "active_schedule_mutation",
    "active_source_mutation",
    "active_requirement_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
)


def validate_public_source_refresh_launch_rehearsal_packet(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a rehearsal transcript packet."""

    errors: list[str] = []

    consumed = packet.get("consumed_packets")
    if not _non_empty_sequence(consumed):
        errors.append("missing consumed-packet references")

    preflight = packet.get("preflight_gate_outcome")
    if not isinstance(preflight, Mapping) or not preflight.get("outcome"):
        errors.append("missing preflight gate outcome")

    abort_checks = packet.get("abort_trigger_checks")
    if not _non_empty_sequence(abort_checks):
        errors.append("missing abort-trigger checks")

    reviewer_owner = packet.get("reviewer_owner") or packet.get("reviewer")
    if not isinstance(reviewer_owner, str) or not reviewer_owner.strip():
        errors.append("missing reviewer owner")

    result_placeholders = packet.get("result_placeholders")
    if not _non_empty_sequence(result_placeholders):
        errors.append("missing metadata-only result placeholders")
    else:
        for index, placeholder in enumerate(result_placeholders):
            if not isinstance(placeholder, Mapping) or placeholder.get("metadata_only") is not True:
                errors.append(f"result placeholder {index} is not metadata-only")

    steps = packet.get("rehearsal_steps") or packet.get("steps")
    if not _non_empty_sequence(steps):
        errors.append("missing cited rehearsal steps")
    else:
        for index, step in enumerate(steps):
            if not isinstance(step, Mapping):
                errors.append(f"rehearsal step {index} is not an object")
                continue
            citations = step.get("citations") or step.get("source_citations")
            if not _non_empty_sequence(citations):
                errors.append(f"rehearsal step {index} has no citations")

    for location, value in _walk(packet):
        if isinstance(value, str):
            stripped = value.strip()
            if _looks_like_url(stripped):
                url_error = _validate_public_url(stripped)
                if url_error:
                    errors.append(f"{location}: {url_error}")
            if _LIVE_COMMAND_RE.search(stripped):
                errors.append(f"{location}: command or text fetches/downloads/processes live sources")
            if _RAW_ARTIFACT_RE.search(stripped):
                errors.append(f"{location}: raw artifact reference is not allowed")
            if _OUTCOME_GUARANTEE_RE.search(stripped):
                errors.append(f"{location}: legal or permitting outcome guarantee is not allowed")
        elif isinstance(value, bool):
            key = location.rsplit(".", 1)[-1].replace("[]", "")
            if value and key in _MUTATION_FLAGS:
                errors.append(f"{location}: active mutation flag is not allowed")

    return sorted(set(errors))


def assert_valid_public_source_refresh_launch_rehearsal_packet(packet: Mapping[str, Any]) -> None:
    errors = validate_public_source_refresh_launch_rehearsal_packet(packet)
    if errors:
        joined = "; ".join(errors)
        raise ValueError(f"invalid public source refresh launch rehearsal packet: {joined}")


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0


def _looks_like_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _validate_public_url(value: str) -> str | None:
    parsed = urlparse(value)
    if parsed.scheme != "https":
        return "URL must use https"
    if parsed.username or parsed.password:
        return "authenticated URL is not allowed"
    hostname = parsed.hostname or ""
    if hostname not in _ALLOWED_URL_HOSTS:
        return "URL host is not allowlisted"
    query_keys = {part.split("=", 1)[0].lower() for part in parsed.query.split("&") if part}
    if query_keys & _AUTH_QUERY_KEYS:
        return "authenticated URL query parameter is not allowed"
    return None


def _walk(value: Any, path: str = "packet") -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            found.extend(_walk(child, f"{path}.{key}"))
    elif _non_empty_sequence(value):
        for child in value:
            found.extend(_walk(child, f"{path}[]"))
    return found
