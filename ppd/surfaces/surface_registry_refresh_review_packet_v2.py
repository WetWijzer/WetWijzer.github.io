"""Validation for surface-registry refresh review packet v2.

The validator is intentionally fixture-friendly and side-effect free. It only
checks packet structure and text for release-blocking content; it never executes
DevHub, browser, crawl, prompt, guardrail, monitoring, release, or agent-state
changes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import re
from typing import Any


CONSEQUENTIAL_ACTION_TYPES = {
    "submit",
    "submission",
    "certify",
    "certification",
    "upload",
    "official_upload",
    "schedule",
    "cancel",
    "withdraw",
    "payment",
    "pay_fee",
    "purchase",
    "reactivate",
    "request_extension",
    "account_security_change",
}

PRIVATE_VALUE_KEYS = {
    "password",
    "passcode",
    "mfa_code",
    "otp",
    "token",
    "api_key",
    "secret",
    "cookie",
    "set_cookie",
    "authorization",
    "auth_header",
    "credential",
    "ssn",
    "tax_id",
    "payment_card",
    "card_number",
    "cvv",
    "bank_account",
    "routing_number",
    "private_value",
    "raw_private_value",
}

SESSION_ARTIFACT_KEYS = {
    "storage_state",
    "session_state",
    "auth_state",
    "cookies",
    "local_storage",
    "session_storage",
    "browser_context_state",
    "playwright_state",
    "devhub_session_file",
}

EVIDENCE_ARTIFACT_RE = re.compile(
    r"(?:\bscreenshot\b|\.png\b|\.jpg\b|\.jpeg\b|\.webp\b|\.trace\b|trace\.zip\b|\.har\b|\bhar\b)",
    re.IGNORECASE,
)

LIVE_EXECUTION_RE = re.compile(
    r"\b(?:opened|launched|ran|executed|clicked|filled|submitted|uploaded|scheduled|paid|certified)\b"
    r".*\b(?:devhub|browser|playwright|chromium|firefox|webkit)\b|"
    r"\b(?:devhub|browser|playwright|chromium|firefox|webkit)\b"
    r".*\b(?:opened|launched|ran|executed|clicked|filled|submitted|uploaded|scheduled|paid|certified)\b",
    re.IGNORECASE,
)

GUARANTEE_RE = re.compile(
    r"\b(?:guarantee[sd]?|assure[sd]?|will be approved|permit will issue|approval is certain|legal advice|legally sufficient|compliance is guaranteed|no risk of denial)\b",
    re.IGNORECASE,
)

MUTATION_FLAG_KEYS = {
    "mutate_surface_registry",
    "surface_registry_mutation",
    "surface_registry_write",
    "update_surface_registry",
    "apply_surface_registry_changes",
    "mutate_guardrails",
    "guardrail_mutation",
    "guardrail_write",
    "update_guardrails",
    "apply_guardrail_changes",
    "mutate_prompts",
    "prompt_mutation",
    "prompt_write",
    "update_prompts",
    "mutate_monitoring",
    "monitoring_mutation",
    "monitoring_write",
    "update_monitoring",
    "mutate_release_state",
    "release_state_mutation",
    "release_state_write",
    "update_release_state",
    "mutate_agent_state",
    "agent_state_mutation",
    "agent_state_write",
    "update_agent_state",
}

MUTATION_FLAG_TEXT_RE = re.compile(
    r"\b(?:surface-registry|surface_registry|guardrail|prompt|monitoring|release-state|release_state|agent-state|agent_state)\b"
    r".{0,48}\b(?:mutation|mutate|write|apply|enable|update|activate)\b|"
    r"\b(?:mutation|mutate|write|apply|enable|update|activate)\b"
    r".{0,48}\b(?:surface-registry|surface_registry|guardrail|prompt|monitoring|release-state|release_state|agent-state|agent_state)\b",
    re.IGNORECASE,
)


class SurfaceRegistryRefreshReviewPacketV2Error(ValueError):
    """Raised when a packet is not acceptable for review promotion."""


def validate_surface_registry_refresh_review_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for a review packet.

    An empty list means the packet is acceptable for offline review. The checks
    are intentionally conservative because this packet type must never carry
    private DevHub values, session artifacts, browser evidence, live execution
    claims, official outcome guarantees, consequential action enablement, or
    mutation flags.
    """

    errors: list[str] = []

    if not isinstance(packet, Mapping):
        return ["packet must be a mapping"]

    version = packet.get("packet_version") or packet.get("version")
    if str(version) not in {"2", "v2", "surface-registry-refresh-review-packet-v2"}:
        errors.append("packet_version must identify surface-registry refresh review packet v2")

    review_items = _list_from_any(
        packet.get("review_items")
        or packet.get("surface_review_items")
        or packet.get("action_review_items")
        or packet.get("items")
    )
    if not review_items:
        errors.append("review_items must include at least one surface or action review item")
    for index, item in enumerate(review_items):
        if not isinstance(item, Mapping):
            errors.append(f"review_items[{index}] must be a mapping")
            continue
        _validate_review_item(item, index, errors)

    checkpoints = _checkpoint_names(packet)
    if "selector-confidence" not in checkpoints:
        errors.append("missing selector-confidence checkpoint")
    if "manual-handoff" not in checkpoints:
        errors.append("missing manual-handoff checkpoint")

    _scan_mapping(packet, path="packet", errors=errors)
    return _dedupe(errors)


def assert_valid_surface_registry_refresh_review_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise a compact exception when validation fails."""

    errors = validate_surface_registry_refresh_review_packet_v2(packet)
    if errors:
        raise SurfaceRegistryRefreshReviewPacketV2Error("; ".join(errors))


def _validate_review_item(item: Mapping[str, Any], index: int, errors: list[str]) -> None:
    item_type = str(item.get("item_type") or item.get("type") or "review-item")
    citations = _list_from_any(
        item.get("citations")
        or item.get("source_citations")
        or item.get("source_evidence_ids")
        or item.get("evidence_ids")
    )
    if not citations or not all(str(citation).strip() for citation in citations):
        errors.append(f"review_items[{index}] {item_type} is missing citations")

    selector_confidence = item.get("selector_confidence")
    if selector_confidence is None:
        selector_confidence = item.get("selector-confidence")
    if selector_confidence is None:
        errors.append(f"review_items[{index}] {item_type} is missing selector_confidence")

    if _is_truthy(item.get("enabled")) or _is_truthy(item.get("enable")):
        action_type = str(item.get("action_type") or item.get("action") or item.get("name") or "").lower()
        risk = str(item.get("risk") or item.get("risk_class") or item.get("classification") or "").lower()
        if action_type in CONSEQUENTIAL_ACTION_TYPES or "consequential" in risk or "financial" in risk:
            errors.append(f"review_items[{index}] enables a consequential action")


def _checkpoint_names(packet: Mapping[str, Any]) -> set[str]:
    names: set[str] = set()
    for checkpoint in _list_from_any(packet.get("checkpoints") or packet.get("review_checkpoints")):
        if isinstance(checkpoint, Mapping):
            raw = checkpoint.get("checkpoint") or checkpoint.get("name") or checkpoint.get("id")
        else:
            raw = checkpoint
        if raw is not None:
            names.add(_normalize_checkpoint(raw))
    return names


def _normalize_checkpoint(value: Any) -> str:
    return str(value).strip().lower().replace("_", "-").replace(" ", "-")


def _scan_mapping(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = _normalize_key(raw_key)
            child_path = f"{path}.{raw_key}"
            if key in PRIVATE_VALUE_KEYS:
                errors.append(f"{child_path} contains a private or authenticated value field")
            if key in SESSION_ARTIFACT_KEYS:
                errors.append(f"{child_path} contains a session or authentication artifact")
            if key in MUTATION_FLAG_KEYS and _is_truthy(child):
                errors.append(f"{child_path} contains an active mutation flag")
            if key in {"enabled", "enable"} and _is_truthy(child):
                sibling_text = " ".join(str(v) for v in value.values() if isinstance(v, (str, int, float, bool)))
                if _mentions_consequential_action(sibling_text):
                    errors.append(f"{path} enables a consequential action")
            _scan_mapping(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_mapping(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        _scan_text(value, path, errors)


def _scan_text(text: str, path: str, errors: list[str]) -> None:
    if EVIDENCE_ARTIFACT_RE.search(text):
        errors.append(f"{path} references screenshots, traces, HAR, or browser media artifacts")
    if LIVE_EXECUTION_RE.search(text):
        errors.append(f"{path} claims live DevHub or browser execution")
    if GUARANTEE_RE.search(text):
        errors.append(f"{path} makes a legal or permitting outcome guarantee")
    if MUTATION_FLAG_TEXT_RE.search(text):
        errors.append(f"{path} references active surface-registry, guardrail, prompt, monitoring, release-state, or agent-state mutation")
    if _mentions_consequential_action(text) and re.search(r"\b(?:enabled|enable|allowed|permit|proceed)\b", text, re.IGNORECASE):
        errors.append(f"{path} enables a consequential action")


def _mentions_consequential_action(text: str) -> bool:
    normalized = text.lower().replace("-", "_")
    return any(action in normalized for action in CONSEQUENTIAL_ACTION_TYPES)


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled", "active", "apply", "write"}
    return bool(value)


def _list_from_any(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _dedupe(errors: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for error in errors:
        if error not in seen:
            seen.add(error)
            result.append(error)
    return result
