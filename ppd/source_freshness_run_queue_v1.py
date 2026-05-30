from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.source_freshness_monitor_backlog import validate_packet


RUN_QUEUE_VERSION = "public-source-freshness-run-queue-v1"
NO_NETWORK_MODE = "fixture_first_no_network"

_MUTATION_KEY_RE = re.compile(
    r"(^|_)(active_)?(source|document|requirement|process|guardrail|release_state|release-state|prompt|agent_state|agent-state)_.*(mutation|mutate|write|update|promote|enable|apply)",
    re.IGNORECASE,
)
_MUTATION_VALUE_RE = re.compile(
    r"\b(active|apply|enable|mutate|promote|publish|replace|update|write)\b.{0,80}\b(source|document|requirement|process|guardrail|release[-_ ]?state|prompt|agent[-_ ]?state)\b",
    re.IGNORECASE,
)
_PRIVATE_ARTIFACT_RE = re.compile(
    r"\b(cookie|credential|password|secret|token|session|auth[-_ ]?state|storage[-_ ]?state|har|trace|screenshot|browser[-_ ]?profile|playwright[-_ ]?state)\b|\.(har|zip|png|jpg|jpeg|webp)$",
    re.IGNORECASE,
)
_RAW_DATA_RE = re.compile(
    r"\b(raw[-_ ]?(crawl|body|html|pdf|download|downloaded)|downloaded[-_ ]?(pdf|document|file)|pdf[-_ ]?(body|download|binary|bytes)|crawl[-_ ]?output|warc)\b",
    re.IGNORECASE,
)
_LIVE_CLAIM_RE = re.compile(
    r"\b(live[-_ ]?crawl|live[-_ ]?refresh|recrawl|refresh)\b.{0,80}\b(complete|completed|succeeded|finished|executed|ran|done)\b|\b(mark|marked)\b.{0,40}\b(refresh|source[-_ ]?refresh)\b.{0,40}\bcomplete\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(guarantee|guaranteed|ensure|ensures|will be approved|approval guaranteed|permit will issue|legally sufficient|legal advice|compliant outcome)\b",
    re.IGNORECASE,
)
_CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(submit|submitted|submission|certify|certified|upload|uploaded|pay|paid|payment|purchase|schedule|scheduled|cancel|cancelled|withdraw|reactivate|official action)\b",
    re.IGNORECASE,
)
_NEGATED_PREFIX_RE = re.compile(r"\b(do not|don't|must not|without|no|not allowed|blocked|refuse|refused|prohibit|prohibited)\b", re.IGNORECASE)
_REQUIRED_HANDOFF_FIELDS = ("queue_owner", "review_state", "reviewer_decision_required", "allowed_decisions", "handoff_notes")
_REQUIRED_CONSTRAINTS = (
    "network_allowed",
    "live_crawl_allowed",
    "document_download_allowed",
    "raw_body_persistence_allowed",
    "active_artifact_updates_allowed",
    "refresh_completion_claim_allowed",
)


def load_json(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("JSON payload must be an object")
    return data


def build_public_source_freshness_run_queue_v1(backlog_packet: Mapping[str, Any]) -> dict[str, Any]:
    """Build an ordered offline run queue from a freshness monitor backlog packet.

    The queue is a reviewer planning artifact only. It preserves official source
    anchors, expected cadences, synthetic probes, and exact offline validation
    commands while avoiding live crawl status, raw bodies, and active artifact
    updates.
    """
    backlog_errors = validate_packet(dict(backlog_packet))
    if backlog_errors:
        raise ValueError("invalid public source freshness monitor backlog packet v1: " + "; ".join(backlog_errors))

    anchors_by_id = _index_by_id(backlog_packet.get("source_anchors", []))
    schedules_by_id = _index_by_id(backlog_packet.get("freshness_schedules", []))
    probes_by_id = _index_by_id(backlog_packet.get("synthetic_change_categories", []))
    commands_by_id = _index_by_id(backlog_packet.get("offline_validation_commands", []))

    rows = []
    for work_item in sorted(_as_list(backlog_packet.get("work_items")), key=lambda item: item["order"]):
        anchor_ids = list(work_item["anchor_ids"])
        schedule_ids = list(work_item["schedule_ids"])
        probe_ids = list(work_item["synthetic_change_category_ids"])
        command_ids = list(work_item["offline_validation_command_ids"])
        cadences = [_cadence_for_schedule(schedules_by_id[schedule_id]) for schedule_id in schedule_ids]

        rows.append(
            {
                "order": work_item["order"],
                "check_id": f"run-{work_item['id']}",
                "backlog_work_item_id": work_item["id"],
                "title": work_item["title"],
                "source_anchor_ids": anchor_ids,
                "source_anchors": [_source_anchor_summary(anchors_by_id[anchor_id]) for anchor_id in anchor_ids],
                "expected_freshness_cadence": _ordered_unique(cadences),
                "schedule_ids": schedule_ids,
                "synthetic_change_probes": [_probe_summary(probes_by_id[probe_id]) for probe_id in probe_ids],
                "reviewer_handoff": {
                    "queue_owner": "ppd-public-source-freshness-reviewer",
                    "review_state": "pending_offline_fixture_review",
                    "reviewer_decision_required": True,
                    "allowed_decisions": [
                        "accept_no_change_fixture_result",
                        "request_public_metadata_recrawl_preflight",
                        "escalate_for_human_source_review",
                    ],
                    "handoff_notes": [
                        "Use fixture probes only for this queue row.",
                        "Do not fetch live pages or downloaded documents from this run queue.",
                        "Do not mark any source refresh complete from this run queue alone.",
                    ],
                },
                "offline_validation_commands": [_command_summary(commands_by_id[command_id]) for command_id in command_ids],
                "run_constraints": {
                    "network_allowed": False,
                    "live_crawl_allowed": False,
                    "document_download_allowed": False,
                    "raw_body_persistence_allowed": False,
                    "active_artifact_updates_allowed": False,
                    "refresh_completion_claim_allowed": False,
                },
            }
        )

    queue = {
        "version": RUN_QUEUE_VERSION,
        "packet_id": "ppd-public-source-freshness-run-queue-v1",
        "mode": NO_NETWORK_MODE,
        "input_packet": {
            "packet_id": _text(backlog_packet.get("packet_id")),
            "version": backlog_packet.get("version"),
            "scope": _text(backlog_packet.get("scope")),
        },
        "run_queue_rows": rows,
        "queue_constraints": {
            "network_allowed": False,
            "live_crawl_allowed": False,
            "document_download_allowed": False,
            "raw_body_persistence_allowed": False,
            "active_artifact_updates_allowed": False,
            "refresh_completion_claim_allowed": False,
        },
        "validation_commands": _dedupe_commands(rows),
    }
    errors = validate_public_source_freshness_run_queue_v1(queue)
    if errors:
        raise ValueError("invalid public source freshness run queue v1: " + "; ".join(errors))
    return queue


def validate_public_source_freshness_run_queue_v1(queue: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if queue.get("version") != RUN_QUEUE_VERSION:
        errors.append(f"version must be {RUN_QUEUE_VERSION}")
    if queue.get("mode") != NO_NETWORK_MODE:
        errors.append(f"mode must be {NO_NETWORK_MODE}")

    rows = queue.get("run_queue_rows")
    if not isinstance(rows, list) or not rows:
        errors.append("run_queue_rows must be a non-empty list")
        _scan_unsafe_content(queue, errors)
        return errors

    orders = []
    seen_check_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append("run_queue_rows entries must be objects")
            continue
        order = row.get("order")
        if not isinstance(order, int):
            errors.append(f"row {row.get('check_id')} order must be an integer")
        else:
            orders.append(order)
        check_id = row.get("check_id")
        if not isinstance(check_id, str) or not check_id:
            errors.append("row check_id must be a non-empty string")
        elif check_id in seen_check_ids:
            errors.append(f"duplicate check_id {check_id}")
        else:
            seen_check_ids.add(check_id)

        _require_non_empty_string_list(row, "source_anchor_ids", errors)
        _require_non_empty_string_list(row, "expected_freshness_cadence", errors)
        _require_non_empty_list(row, "synthetic_change_probes", errors)
        _require_non_empty_list(row, "offline_validation_commands", errors)
        _validate_source_anchor_summaries(row, errors)
        _validate_synthetic_probes(row, errors)
        _validate_offline_commands(row, errors)
        _validate_reviewer_handoff(row, errors)
        _validate_run_constraints(row, errors)

    if orders and sorted(orders) != list(range(1, len(orders) + 1)):
        errors.append("run_queue_rows order must be contiguous starting at 1")

    queue_constraints = queue.get("queue_constraints")
    if not isinstance(queue_constraints, dict):
        errors.append("queue_constraints must be an object")
    else:
        for key in _REQUIRED_CONSTRAINTS:
            if queue_constraints.get(key) is not False:
                errors.append(f"queue constraint {key} must be false")
        for key, value in queue_constraints.items():
            if value is not False:
                errors.append(f"queue constraint {key} must be false")

    _validate_top_level_commands(queue, errors)
    _scan_unsafe_content(queue, errors)
    return errors


def _validate_source_anchor_summaries(row: Mapping[str, Any], errors: list[str]) -> None:
    check_id = row.get("check_id")
    anchor_ids = row.get("source_anchor_ids")
    summaries = row.get("source_anchors")
    if not isinstance(anchor_ids, list) or not isinstance(summaries, list) or len(summaries) != len(anchor_ids):
        errors.append(f"row {check_id} source_anchors must match source_anchor_ids")
        return
    summary_ids = []
    for anchor in summaries:
        if not isinstance(anchor, Mapping):
            errors.append(f"row {check_id} source_anchors entries must be objects")
            continue
        anchor_id = anchor.get("id")
        if not isinstance(anchor_id, str) or not anchor_id:
            errors.append(f"row {check_id} source anchor summary id must be present")
        else:
            summary_ids.append(anchor_id)
        for key in ("label", "official_url", "crawl_policy"):
            if not isinstance(anchor.get(key), str) or not anchor.get(key):
                errors.append(f"row {check_id} source anchor {anchor_id or ''} missing {key}")
        citation = anchor.get("citation")
        if not isinstance(citation, Mapping) or not all(isinstance(citation.get(key), str) and citation.get(key) for key in ("label", "url", "verified_on")):
            errors.append(f"row {check_id} source anchor {anchor_id or ''} missing citation fields")
    if summary_ids != anchor_ids:
        errors.append(f"row {check_id} source anchor summary ids must match source_anchor_ids order")


def _validate_synthetic_probes(row: Mapping[str, Any], errors: list[str]) -> None:
    check_id = row.get("check_id")
    for probe in _as_list(row.get("synthetic_change_probes")):
        if not isinstance(probe, Mapping):
            errors.append(f"row {check_id} synthetic_change_probes entries must be objects")
            continue
        for key in ("id", "probe_type", "description"):
            if not isinstance(probe.get(key), str) or not probe.get(key):
                errors.append(f"row {check_id} synthetic probe missing {key}")
        if probe.get("execution_mode") != "synthetic_fixture_only":
            errors.append(f"row {check_id} synthetic probe execution_mode must be synthetic_fixture_only")


def _validate_reviewer_handoff(row: Mapping[str, Any], errors: list[str]) -> None:
    check_id = row.get("check_id")
    handoff = row.get("reviewer_handoff")
    if not isinstance(handoff, dict):
        errors.append(f"row {check_id} reviewer_handoff must be an object")
        return
    for key in _REQUIRED_HANDOFF_FIELDS:
        if key not in handoff:
            errors.append(f"row {check_id} reviewer_handoff missing {key}")
    if not isinstance(handoff.get("queue_owner"), str) or not handoff.get("queue_owner"):
        errors.append(f"row {check_id} reviewer_handoff queue_owner must be present")
    if handoff.get("review_state") != "pending_offline_fixture_review":
        errors.append(f"row {check_id} must remain pending offline fixture review")
    if handoff.get("reviewer_decision_required") is not True:
        errors.append(f"row {check_id} must require reviewer decision")
    if not isinstance(handoff.get("allowed_decisions"), list) or not handoff.get("allowed_decisions"):
        errors.append(f"row {check_id} reviewer_handoff allowed_decisions must be a non-empty list")
    if not isinstance(handoff.get("handoff_notes"), list) or not handoff.get("handoff_notes"):
        errors.append(f"row {check_id} reviewer_handoff handoff_notes must be a non-empty list")


def _validate_run_constraints(row: Mapping[str, Any], errors: list[str]) -> None:
    check_id = row.get("check_id")
    constraints = row.get("run_constraints")
    if not isinstance(constraints, dict):
        errors.append(f"row {check_id} run_constraints must be an object")
        return
    for key in _REQUIRED_CONSTRAINTS:
        if constraints.get(key) is not False:
            errors.append(f"row {check_id} {key} must be false")


def _validate_offline_commands(row: Mapping[str, Any], errors: list[str]) -> None:
    check_id = row.get("check_id")
    for command in _as_list(row.get("offline_validation_commands")):
        if not isinstance(command, dict):
            errors.append(f"row {check_id} offline commands must be objects")
            continue
        argv = command.get("argv")
        if not isinstance(command.get("id"), str) or not command.get("id"):
            errors.append(f"row {check_id} offline command id must be present")
        if not isinstance(argv, list) or not argv or not all(isinstance(part, str) and part for part in argv):
            errors.append(f"row {check_id} offline command argv must be a non-empty string list")
        if command.get("network") is not False:
            errors.append(f"row {check_id} offline command network must be false")


def _validate_top_level_commands(queue: Mapping[str, Any], errors: list[str]) -> None:
    commands = queue.get("validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("validation_commands must be a non-empty list")
        return
    for command in commands:
        if not isinstance(command, Mapping):
            errors.append("validation_commands entries must be objects")
            continue
        argv = command.get("argv")
        if not isinstance(command.get("id"), str) or not command.get("id"):
            errors.append("validation command id must be present")
        if not isinstance(argv, list) or not argv or not all(isinstance(part, str) and part for part in argv):
            errors.append("validation command argv must be a non-empty string list")
        if command.get("network") is not False:
            errors.append("validation command network must be false")


def _scan_unsafe_content(value: Any, errors: list[str], path: str = "$", *, key_context: str = "") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if _is_mutation_key(key_text) and child is not False:
                errors.append(f"active mutation flag must be false at {child_path}")
            if _is_private_artifact_key(key_text) and child:
                errors.append(f"private/authenticated/session/browser artifact rejected at {child_path}")
            if _is_raw_data_key(key_text) and child:
                errors.append(f"raw crawl/PDF/downloaded data rejected at {child_path}")
            _scan_unsafe_content(child, errors, child_path, key_context=key_text)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_unsafe_content(child, errors, f"{path}[{index}]", key_context=key_context)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return
        if _PRIVATE_ARTIFACT_RE.search(text) and not _is_negated(text):
            errors.append(f"private/authenticated/session/browser artifact rejected at {path}")
        if _RAW_DATA_RE.search(text) and not _is_negated(text):
            errors.append(f"raw crawl/PDF/downloaded data rejected at {path}")
        if _LIVE_CLAIM_RE.search(text) and not _is_negated(text):
            errors.append(f"live crawl or refresh-complete claim rejected at {path}")
        if _GUARANTEE_RE.search(text) and not _is_negated(text):
            errors.append(f"legal or permitting outcome guarantee rejected at {path}")
        if _CONSEQUENTIAL_ACTION_RE.search(text) and not _is_allowed_consequential_context(text, key_context):
            errors.append(f"consequential action language rejected at {path}")
        if _MUTATION_VALUE_RE.search(text) and not _is_negated(text):
            errors.append(f"active mutation language rejected at {path}")


def _is_mutation_key(key: str) -> bool:
    normalized = key.replace("-", "_")
    return bool(_MUTATION_KEY_RE.search(normalized))


def _is_private_artifact_key(key: str) -> bool:
    return bool(re.search(r"(cookie|credential|password|secret|token|session|auth_state|storage_state|har|trace|screenshot|browser_profile)", key.replace("-", "_"), re.IGNORECASE))


def _is_raw_data_key(key: str) -> bool:
    normalized = key.replace("-", "_")
    if normalized in {"document_download_allowed", "raw_body_persistence_allowed"}:
        return False
    return bool(re.search(r"(raw_body|raw_crawl|raw_pdf|downloaded_data|downloaded_pdf|downloaded_document|crawl_output|pdf_bytes|warc)", normalized, re.IGNORECASE))


def _is_allowed_consequential_context(text: str, key_context: str) -> bool:
    if _is_negated(text):
        return True
    normalized_key = key_context.replace("-", "_").lower()
    return normalized_key in {"allowed_decisions", "handoff_notes"} and "request_public_metadata_recrawl_preflight" in text


def _is_negated(text: str) -> bool:
    prefix = text[:120]
    return bool(_NEGATED_PREFIX_RE.search(prefix))


def _index_by_id(items: Any) -> dict[str, Mapping[str, Any]]:
    return {str(item["id"]): item for item in _as_list(items) if isinstance(item, Mapping) and isinstance(item.get("id"), str)}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _source_anchor_summary(anchor: Mapping[str, Any]) -> dict[str, Any]:
    citation = anchor.get("citation") if isinstance(anchor.get("citation"), Mapping) else {}
    return {
        "id": _text(anchor.get("id")),
        "label": _text(anchor.get("label")),
        "official_url": _text(anchor.get("official_url")),
        "crawl_policy": _text(anchor.get("crawl_policy")),
        "citation": {
            "label": _text(citation.get("label")),
            "url": _text(citation.get("url")),
            "verified_on": _text(citation.get("verified_on")),
        },
    }


def _cadence_for_schedule(schedule: Mapping[str, Any]) -> str:
    return _text(schedule.get("cadence"))


def _probe_summary(probe: Mapping[str, Any]) -> dict[str, str]:
    return {
        "id": _text(probe.get("id")),
        "probe_type": _text(probe.get("id")),
        "description": _text(probe.get("description")),
        "execution_mode": "synthetic_fixture_only",
    }


def _command_summary(command: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": _text(command.get("id")),
        "argv": list(command.get("argv", [])),
        "network": False,
    }


def _dedupe_commands(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        for command in _as_list(row.get("offline_validation_commands")):
            command_id = _text(command.get("id"))
            if command_id and command_id not in seen:
                seen.add(command_id)
                commands.append(dict(command))
    return commands


def _ordered_unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _require_non_empty_string_list(row: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = row.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        errors.append(f"row {row.get('check_id')} {key} must be a non-empty string list")


def _require_non_empty_list(row: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = row.get(key)
    if not isinstance(value, list) or not value:
        errors.append(f"row {row.get('check_id')} {key} must be a non-empty list")


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 ppd/source_freshness_run_queue_v1.py BACKLOG_PACKET.json")
    print(json.dumps(build_public_source_freshness_run_queue_v1(load_json(sys.argv[1])), indent=2, sort_keys=True))
