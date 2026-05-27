"""Fixture-first validation for PP&D agent readiness packets.

The validator is deterministic and side-effect free. It consumes synthetic packet
fixtures or assembled packet-shaped dictionaries and rejects readiness when the
packet lacks fresh cited evidence, citation spans, crawl-promotion audit closure,
DevHub surface-map readiness, or required handoff gates for consequential work.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from .packet import AgentReadinessPacketError

_CONSEQUENTIAL_CLASSES = {
    "certification",
    "consequential",
    "consequential_official",
    "financial",
    "official",
    "payment",
    "submission",
    "upload_to_official_record",
}

_STALE_STATUSES = {"expired", "needs_refresh", "stale", "unknown", "unknown_stale"}
_PROMOTABLE_AUDIT_STATUSES = {"promotable", "promotable_metadata_only", "ready", "ready_metadata_only"}
_READY_SURFACE_STATUSES = {
    "attended_only_for_official_actions",
    "fixture_validated",
    "manual_handoff_required",
    "ready_metadata_only",
}


@dataclass(frozen=True)
class AgentReadinessValidationResult:
    """Machine-readable readiness validation result."""

    ready: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ready": self.ready, "problems": list(self.problems)}


def validate_agent_readiness_packet(
    packet: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_evidence_age_days: int = 45,
) -> AgentReadinessValidationResult:
    """Return fail-closed validation for a PP&D agent readiness packet."""

    check_time = _normalize_now(now)
    problems: list[str] = []

    evidence_records = _evidence_records(packet)
    problems.extend(_source_evidence_problems(evidence_records, check_time, max_evidence_age_days))
    problems.extend(_crawl_promotion_audit_problems(packet.get("crawl_promotion_audit")))
    problems.extend(_devhub_surface_map_readiness_problems(packet.get("devhub_surface_map_readiness")))
    problems.extend(_consequential_action_problems(packet))

    return AgentReadinessValidationResult(ready=not problems, problems=tuple(problems))


def require_agent_readiness_packet_ready(
    packet: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_evidence_age_days: int = 45,
) -> None:
    """Raise the existing packet error when readiness validation fails."""

    result = validate_agent_readiness_packet(
        packet,
        now=now,
        max_evidence_age_days=max_evidence_age_days,
    )
    if not result.ready:
        raise AgentReadinessPacketError("invalid_agent_readiness_packet", result.problems)


def _evidence_records(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw = packet.get("normalized_source_evidence") or packet.get("citations") or []
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, Mapping)]


def _source_evidence_problems(
    records: list[Mapping[str, Any]],
    now: datetime,
    max_evidence_age_days: int,
) -> list[str]:
    if not records:
        return ["agent readiness packet is missing normalized source evidence"]

    problems: list[str] = []
    for index, record in enumerate(records):
        evidence_id = _record_id(record, index)
        status = str(record.get("freshness_status", "current")).lower()
        if status in _STALE_STATUSES:
            problems.append(f"source evidence {evidence_id} is stale: freshness_status={status}")

        timestamp = _parse_datetime(
            record.get("last_verified_at")
            or record.get("captured_at")
            or record.get("capture_finished_at")
            or record.get("updated_at")
        )
        if timestamp is None:
            problems.append(f"source evidence {evidence_id} is missing a freshness timestamp")
        elif (now - timestamp).days > max_evidence_age_days:
            problems.append(f"source evidence {evidence_id} is stale at {(now - timestamp).days} days old")

        spans = record.get("citation_spans")
        if not isinstance(spans, list) or not spans:
            problems.append(f"source evidence {evidence_id} is missing citation_spans")
        else:
            for span_index, span in enumerate(spans):
                if not isinstance(span, Mapping) or not _has_span_anchor(span):
                    problems.append(f"source evidence {evidence_id} citation_spans[{span_index}] lacks a page or character span anchor")
    return problems


def _crawl_promotion_audit_problems(audit: Any) -> list[str]:
    if not isinstance(audit, Mapping):
        return ["crawl_promotion_audit is required"]

    problems: list[str] = []
    status = str(audit.get("promotion_status") or audit.get("status") or "").lower()
    if status not in _PROMOTABLE_AUDIT_STATUSES:
        problems.append(f"crawl_promotion_audit has incomplete promotion_status {status or 'missing'}")
    if audit.get("promotable") is not True:
        problems.append("crawl_promotion_audit must be promotable")
    if audit.get("no_raw_body_persisted") is not True:
        problems.append("crawl_promotion_audit must confirm no_raw_body_persisted")
    if audit.get("raw_body_persisted") is True:
        problems.append("crawl_promotion_audit must not persist raw_body_persisted")
    if not audit.get("manifest_ids"):
        problems.append("crawl_promotion_audit must include manifest_ids")
    if not _collect_evidence_refs(audit):
        problems.append("crawl_promotion_audit must cite source_evidence_ids")
    return problems


def _devhub_surface_map_readiness_problems(surface: Any) -> list[str]:
    if not isinstance(surface, Mapping):
        return ["devhub_surface_map_readiness is required"]

    problems: list[str] = []
    status = str(surface.get("readiness_status") or surface.get("status") or "").lower()
    if status not in _READY_SURFACE_STATUSES:
        problems.append("devhub_surface_map_readiness must have a ready attended-only status")
    for key in ("surface_id", "auth_scope", "url_pattern", "page_heading"):
        if not surface.get(key):
            problems.append(f"devhub_surface_map_readiness is missing {key}")
    if not isinstance(surface.get("actions"), list) or not surface.get("actions"):
        problems.append("devhub_surface_map_readiness must include actions")
    if not _collect_evidence_refs(surface):
        problems.append("devhub_surface_map_readiness must cite source_evidence_ids")
    if surface.get("requires_attendance") is not True:
        problems.append("devhub_surface_map_readiness must require attendance for official actions")
    if surface.get("requires_exact_confirmation") is not True:
        problems.append("devhub_surface_map_readiness must require exact confirmation for official actions")
    return problems


def _consequential_action_problems(value: Any, path: str = "$") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        action_class = _action_classification(value)
        if action_class in _CONSEQUENTIAL_CLASSES:
            has_handoff = any(
                value.get(key) is True
                for key in ("manual_handoff_required", "requires_manual_handoff", "requires_attendance")
            )
            if not has_handoff:
                problems.append(f"consequential action lacks manual handoff or attendance requirement at {path}")
            if value.get("requires_exact_confirmation") is not True:
                problems.append(f"consequential action lacks exact-confirmation requirement at {path}")
        for key, child in value.items():
            problems.extend(_consequential_action_problems(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_consequential_action_problems(child, f"{path}[{index}]"))
    return problems


def _action_classification(value: Mapping[str, Any]) -> str | None:
    for key in ("classification", "action_class", "action_type", "decision"):
        raw = value.get(key)
        if isinstance(raw, str):
            normalized = raw.lower()
            if normalized in _CONSEQUENTIAL_CLASSES:
                return normalized
    return None


def _collect_evidence_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, Mapping):
        raw_many = value.get("source_evidence_ids")
        if isinstance(raw_many, list):
            refs.update(item for item in raw_many if isinstance(item, str) and item)
        raw_one = value.get("source_evidence_id")
        if isinstance(raw_one, str) and raw_one:
            refs.add(raw_one)
        for child in value.values():
            refs.update(_collect_evidence_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_evidence_refs(child))
    return refs


def _has_span_anchor(span: Mapping[str, Any]) -> bool:
    has_character_span = isinstance(span.get("start"), int) and isinstance(span.get("end"), int) and span["end"] > span["start"]
    has_page_anchor = span.get("page") is not None or span.get("page_number") is not None
    return has_character_span or has_page_anchor


def _normalize_now(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _record_id(record: Mapping[str, Any], index: int) -> str:
    raw = record.get("evidence_id") or record.get("source_id")
    if isinstance(raw, str) and raw:
        return raw
    return f"index-{index}"
