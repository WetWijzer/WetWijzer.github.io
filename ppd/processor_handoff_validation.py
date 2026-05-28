"""Validation for PP&D processor handoff packets.

The processor handoff boundary must stay metadata-only and replayable.  This
module intentionally accepts plain dictionaries so callers can validate decoded
JSON before constructing richer contracts.
"""

from __future__ import annotations

from ipaddress import ip_address
from typing import Any
from urllib.parse import parse_qsl, urlparse


_POLICY_EVIDENCE_KEYS = (
    "policy_preflight_evidence",
    "policyPreflightEvidence",
    "preflight_evidence",
)

_CONTRACT_ID_KEYS = (
    "processor_contract_id",
    "processorContractId",
    "processor_contract_identifier",
    "processorContractIdentifier",
    "contract_id",
)

_LIVE_NETWORK_KEYS = {
    "allow_live_network",
    "allow_network",
    "live_network",
    "network_enabled",
    "use_live_network",
    "liveNetwork",
    "allowLiveNetwork",
    "networkEnabled",
    "useLiveNetwork",
}

_RAW_BODY_KEYS = {
    "archive_body",
    "body",
    "content",
    "html",
    "raw_archive",
    "raw_body",
    "raw_content",
    "raw_html",
    "response_body",
    "text",
}

_LOCAL_PATH_KEYS = {
    "downloaded_path",
    "downloadedPath",
    "file_path",
    "filePath",
    "filesystem_path",
    "filesystemPath",
    "local_path",
    "localPath",
    "path",
}

_ARTIFACT_KEYS = ("artifacts", "artifact_references", "artifactReferences")
_RATE_LIMIT_KEYS = ("rate_limit", "rateLimit", "rate_limits", "rateLimits")
_UNBOUNDED_VALUES = {"", "none", "null", "unbounded", "unlimited", "infinite", "inf", "no_limit"}
_AUTH_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "key",
    "password",
    "signature",
    "sig",
    "token",
}


def validate_processor_handoff_packet(packet: dict[str, Any]) -> list[str]:
    """Return validation errors for an unsafe processor handoff packet."""

    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["handoff packet must be an object"]

    if not _first_present(packet, _POLICY_EVIDENCE_KEYS):
        errors.append("missing policy preflight evidence")

    contract_id = _first_present(packet, _CONTRACT_ID_KEYS)
    if not isinstance(contract_id, str) or not contract_id.strip():
        errors.append("missing processor contract identifier")

    rate_limit = _first_present(packet, _RATE_LIMIT_KEYS)
    if not _has_bounded_rate_limit(rate_limit):
        errors.append("missing bounded rate limit")

    _scan_value(packet, "$", errors)
    _validate_artifacts(packet, errors)
    return errors


def assert_valid_processor_handoff_packet(packet: dict[str, Any]) -> None:
    """Raise ValueError when a handoff packet fails validation."""

    errors = validate_processor_handoff_packet(packet)
    if errors:
        raise ValueError("invalid processor handoff packet: " + "; ".join(errors))


def _first_present(packet: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in packet:
            return packet[key]
    return None


def _has_bounded_rate_limit(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in _UNBOUNDED_VALUES
    if not isinstance(value, dict):
        return False

    if str(value.get("mode", "")).strip().lower() in _UNBOUNDED_VALUES:
        return False

    request_limit = _positive_number(
        value.get("max_requests", value.get("requests", value.get("limit")))
    )
    window = _positive_number(
        value.get("per_seconds", value.get("window_seconds", value.get("seconds")))
    )
    return request_limit and window


def _positive_number(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def _scan_value(value: Any, location: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            item_location = f"{location}.{key_text}"
            if key_text in _LIVE_NETWORK_KEYS and bool(item):
                errors.append(f"live network flag is not allowed at {item_location}")
            if key_text in _RAW_BODY_KEYS and _has_payload(item):
                errors.append(f"raw archive/body field is not allowed at {item_location}")
            if key_text in _LOCAL_PATH_KEYS and _looks_like_local_path(item):
                errors.append(f"local downloaded path is not allowed at {item_location}")
            if isinstance(item, str) and _is_private_or_authenticated_url(item):
                errors.append(f"private or authenticated URL is not allowed at {item_location}")
            _scan_value(item, item_location, errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_value(item, f"{location}[{index}]", errors)
    elif isinstance(value, str) and _is_private_or_authenticated_url(value):
        errors.append(f"private or authenticated URL is not allowed at {location}")


def _has_payload(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (bytes, bytearray)):
        return len(value) > 0
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def _looks_like_local_path(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    return (
        text.startswith("/")
        or text.startswith("./")
        or text.startswith("../")
        or text.startswith("~/")
        or text.startswith("file://")
        or "\\" in text
    )


def _is_private_or_authenticated_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    if parsed.username or parsed.password:
        return True

    query_keys = {key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & _AUTH_QUERY_KEYS:
        return True

    host = parsed.hostname or ""
    if host in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return True
    try:
        address = ip_address(host)
    except ValueError:
        return False
    return address.is_private or address.is_loopback or address.is_link_local


def _validate_artifacts(packet: dict[str, Any], errors: list[str]) -> None:
    artifacts = None
    for key in _ARTIFACT_KEYS:
        if key in packet:
            artifacts = packet[key]
            break
    if artifacts is None:
        return
    if not isinstance(artifacts, list):
        errors.append("artifact references must be a list")
        return
    for index, artifact in enumerate(artifacts):
        location = f"$.artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"artifact reference must be an object at {location}")
            continue
        if artifact.get("metadata_only") is not True and artifact.get("metadataOnly") is not True:
            errors.append(f"artifact reference must be metadata-only at {location}")
        for key in _RAW_BODY_KEYS | _LOCAL_PATH_KEYS:
            if key in artifact and _has_payload(artifact[key]):
                errors.append(f"artifact reference contains non-metadata field at {location}.{key}")
