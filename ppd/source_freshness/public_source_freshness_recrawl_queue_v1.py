"""Fixture-first public source freshness recrawl queue v1 validation.

The queue is a reviewer planning artifact only. It must not contain private
DevHub artifacts, raw crawl output, downloaded documents, live crawl execution
claims, legal/permitting guarantees, consequential DevHub action language, or
active mutation flags for sources, processes, guardrails, prompts, or release
state.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Mapping
from urllib.parse import urlparse

PACKET_TYPE = "ppd.public_source_freshness_recrawl_queue.v1"
MODE = "fixture_first_public_source_freshness_recrawl_queue"

_REQUIRED_FALSE_POLICY_KEYS = (
    "network_allowed",
    "network_invoked",
    "live_crawl_allowed",
    "live_crawl_executed",
    "document_download_allowed",
    "raw_data_persistence_allowed",
    "processor_invocation_allowed",
    "devhub_action_allowed",
    "active_source_mutation_allowed",
    "active_process_mutation_allowed",
    "active_guardrail_mutation_allowed",
    "active_prompt_mutation_allowed",
    "active_release_state_mutation_allowed",
)
_REQUIRED_ROW_LISTS = (
    "stale_or_changed_evidence_placeholders",
    "robots_policy_preflight_placeholders",
    "processor_handoff_dry_run_refs",
    "reviewer_approval_placeholders",
)
_PRIVATE_KEY_RE = re.compile(
    r"(auth|authenticated|browser|cookie|credential|password|secret|session|storage_state|token|trace|har|screenshot)",
    re.IGNORECASE,
)
_RAW_KEY_RE = re.compile(
    r"(raw_(body|content|crawl|data|download|html|pdf)|downloaded_(data|document|file|pdf)|pdf_(bytes|content|download)|crawl_output|warc)",
    re.IGNORECASE,
)
_MUTATION_KEY_RE = re.compile(
    r"(active_)?(source|process|guardrail|prompt|release[-_]?state).*?(mutat|update|write|apply|promot|enable)",
    re.IGNORECASE,
)
_PRIVATE_TEXT_RE = re.compile(
    r"\b(authenticated|browser trace|cookie|credential|password|secret|session|storage state|token|\.har|screenshot)\b",
    re.IGNORECASE,
)
_RAW_TEXT_RE = re.compile(
    r"\b(raw crawl|raw body|raw html|raw pdf|downloaded document|downloaded pdf|downloaded data|pdf bytes|crawl output|warc)\b",
    re.IGNORECASE,
)
_LIVE_CLAIM_RE = re.compile(
    r"\b(live crawl|live recrawl|live refresh|recrawl|refresh)\b.{0,80}\b(executed|ran|complete|completed|succeeded|finished|done)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(guarantee|guaranteed|legal advice|legally sufficient|permit will issue|will be approved|approval guaranteed|compliant outcome)\b",
    re.IGNORECASE,
)
_CONSEQUENTIAL_DEVHUB_RE = re.compile(
    r"\b(devhub)\b.{0,80}\b(submit|submitted|submission|certify|certified|upload|uploaded|pay|paid|payment|purchase|schedule|scheduled|cancel|cancelled|withdraw|reactivate)\b|\b(submit|submitted|submission|certify|certified|upload|uploaded|pay|paid|payment|purchase|schedule|scheduled|cancel|cancelled|withdraw|reactivate)\b.{0,80}\b(devhub)\b",
    re.IGNORECASE,
)
_MUTATION_TEXT_RE = re.compile(
    r"\b(apply|enable|mutate|promote|publish|replace|update|write)\b.{0,80}\b(source|process|guardrail|prompt|release state|release-state)\b",
    re.IGNORECASE,
)
_NEGATED_RE = re.compile(r"\b(do not|don't|must not|without|no|not allowed|blocked|refuse|refused|prohibit|prohibited|disabled)\b", re.IGNORECASE)
_PRIVATE_PATH_MARKERS = ("/account", "/admin", "/auth", "/dashboard", "/login", "/payment", "/session", "/upload")
_PRIVATE_QUERY_MARKERS = ("access_token=", "auth=", "password=", "session=", "token=")


@dataclass(frozen=True)
class PublicSourceFreshnessRecrawlQueueValidationResult:
    valid: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("JSON payload must be an object")
    return payload


def build_public_source_freshness_recrawl_queue_v1(rows: list[Mapping[str, Any]], *, generated_at: str) -> dict[str, Any]:
    queue = {
        "packet_type": PACKET_TYPE,
        "mode": MODE,
        "generated_at": generated_at,
        "fixture_first": True,
        "metadata_only": True,
        "execution_policy": {key: False for key in _REQUIRED_FALSE_POLICY_KEYS},
        "recrawl_candidate_rows": [deepcopy(dict(row)) for row in rows],
    }
    result = validate_public_source_freshness_recrawl_queue_v1(queue)
    if not result.valid:
        raise ValueError("invalid public source freshness recrawl queue v1: " + "; ".join(result.errors))
    return queue


def validate_public_source_freshness_recrawl_queue_v1(packet: Mapping[str, Any]) -> PublicSourceFreshnessRecrawlQueueValidationResult:
    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be " + PACKET_TYPE)
    if packet.get("mode") != MODE:
        errors.append("mode must be " + MODE)
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        errors.append("metadata_only must be true")

    policy = packet.get("execution_policy")
    if not isinstance(policy, Mapping):
        errors.append("execution_policy must be an object")
    else:
        for key in _REQUIRED_FALSE_POLICY_KEYS:
            if policy.get(key) is not False:
                errors.append(f"execution_policy.{key} must be false")

    rows = packet.get("recrawl_candidate_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("recrawl_candidate_rows must be a non-empty list")
    else:
        seen_row_ids: set[str] = set()
        for index, row in enumerate(rows):
            _validate_row(row, index, seen_row_ids, errors)

    _scan_unsafe_content(packet, errors)
    return PublicSourceFreshnessRecrawlQueueValidationResult(valid=not errors, errors=tuple(_dedupe(errors)))


def _validate_row(row: Any, index: int, seen_row_ids: set[str], errors: list[str]) -> None:
    prefix = f"recrawl_candidate_rows[{index}]"
    if not isinstance(row, Mapping):
        errors.append(prefix + " must be an object")
        return

    row_id = _text(row.get("row_id"))
    if not row_id:
        errors.append(prefix + ".row_id is required")
    elif row_id in seen_row_ids:
        errors.append(prefix + ".row_id must be unique")
    else:
        seen_row_ids.add(row_id)

    for key in ("source_id", "candidate_reason", "review_state"):
        if not _text(row.get(key)):
            errors.append(prefix + f".{key} is required")
    if row.get("review_state") != "pending_reviewer_approval":
        errors.append(prefix + ".review_state must be pending_reviewer_approval")

    priority = row.get("source_family_priority")
    if not isinstance(priority, Mapping):
        errors.append(prefix + ".source_family_priority is required")
    else:
        if not _text(priority.get("source_family")):
            errors.append(prefix + ".source_family_priority.source_family is required")
        if not _text(priority.get("priority_band")):
            errors.append(prefix + ".source_family_priority.priority_band is required")
        if not isinstance(priority.get("priority_order"), int):
            errors.append(prefix + ".source_family_priority.priority_order must be an integer")

    anchor = row.get("official_source_anchor_ref")
    if not isinstance(anchor, Mapping):
        errors.append(prefix + ".official_source_anchor_ref is required")
    else:
        for key in ("anchor_id", "label", "url", "verified_on"):
            if not _text(anchor.get(key)):
                errors.append(prefix + f".official_source_anchor_ref.{key} is required")
        url = _text(anchor.get("url"))
        if url and not _is_public_url(url):
            errors.append(prefix + ".official_source_anchor_ref.url must be a public http(s) URL")

    for key in _REQUIRED_ROW_LISTS:
        items = row.get(key)
        if not isinstance(items, list) or not items:
            errors.append(prefix + f".{key} must be a non-empty list")
            continue
        for item_index, item in enumerate(items):
            if not isinstance(item, Mapping):
                errors.append(prefix + f".{key}[{item_index}] must be an object")
            elif not any(_text(item.get(id_key)) for id_key in ("id", "placeholder_id", "ref_id")):
                errors.append(prefix + f".{key}[{item_index}] must include an id, placeholder_id, or ref_id")

    constraints = row.get("row_constraints")
    if not isinstance(constraints, Mapping):
        errors.append(prefix + ".row_constraints must be an object")
    else:
        for key in _REQUIRED_FALSE_POLICY_KEYS:
            if constraints.get(key) is not False:
                errors.append(prefix + f".row_constraints.{key} must be false")


def _scan_unsafe_content(value: Any, errors: list[str], path: str = "$", *, key_context: str = "") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized = key_text.replace("-", "_")
            if _PRIVATE_KEY_RE.search(normalized) and child:
                errors.append(f"private/authenticated/session/browser artifact rejected at {child_path}")
            if _RAW_KEY_RE.search(normalized) and child:
                errors.append(f"raw crawl/PDF/downloaded data rejected at {child_path}")
            if _MUTATION_KEY_RE.search(normalized) and child is not False:
                errors.append(f"active source/process/guardrail/prompt/release-state mutation flag rejected at {child_path}")
            _scan_unsafe_content(child, errors, child_path, key_context=key_text)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_unsafe_content(child, errors, f"{path}[{index}]", key_context=key_context)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return
        if _PRIVATE_TEXT_RE.search(text) and not _is_negated(text):
            errors.append(f"private/authenticated/session/browser artifact rejected at {path}")
        if _RAW_TEXT_RE.search(text) and not _is_negated(text):
            errors.append(f"raw crawl/PDF/downloaded data rejected at {path}")
        if _LIVE_CLAIM_RE.search(text) and not _is_negated(text):
            errors.append(f"live crawl execution claim rejected at {path}")
        if _GUARANTEE_RE.search(text) and not _is_negated(text):
            errors.append(f"legal or permitting outcome guarantee rejected at {path}")
        if _CONSEQUENTIAL_DEVHUB_RE.search(text) and not _is_negated(text):
            errors.append(f"consequential DevHub action language rejected at {path}")
        if _MUTATION_TEXT_RE.search(text) and not _is_negated(text):
            errors.append(f"active source/process/guardrail/prompt/release-state mutation language rejected at {path}")


def _is_public_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    path = parsed.path.lower()
    query = parsed.query.lower()
    return not any(marker in path for marker in _PRIVATE_PATH_MARKERS) and not any(marker in query for marker in _PRIVATE_QUERY_MARKERS)


def _is_negated(text: str) -> bool:
    return bool(_NEGATED_RE.search(text[:120]))


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _dedupe(errors: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for error in errors:
        if error not in seen:
            seen.add(error)
            result.append(error)
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 ppd/source_freshness/public_source_freshness_recrawl_queue_v1.py QUEUE.json")
    result = validate_public_source_freshness_recrawl_queue_v1(load_json(sys.argv[1]))
    if not result.valid:
        raise SystemExit("\n".join(result.errors))
    print("ok")
