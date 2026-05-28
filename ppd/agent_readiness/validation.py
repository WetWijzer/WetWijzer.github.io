"""Fixture-first validation for PP&D agent readiness packets.

The validator is deterministic and side-effect free. It consumes synthetic packet
fixtures or assembled packet-shaped dictionaries and rejects readiness when the
packet lacks fresh cited evidence, required case facts, non-conflicting gap
analysis, validated DevHub selectors, metadata-only preview records, complete
journal checkpoints, or required handoff gates for consequential work.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

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
_HIGH_SELECTOR_CONFIDENCE_LABELS = {"fixture", "fixture_validated", "high", "strong", "validated"}
_MIN_SELECTOR_CONFIDENCE = 0.8
_COMPLETE_CHECKPOINT_STATUSES = {"complete", "completed", "fixture_validated", "validated"}
_GATE_CHECKPOINT_STATUSES = _COMPLETE_CHECKPOINT_STATUSES | {
    "blocked_until_user_attended",
    "manual_handoff_required",
    "required",
}
_REQUIRED_COMPLETE_CHECKPOINTS = {
    "source_evidence_freshness",
    "case_gap_analysis",
    "surface_map_validation",
    "preview_metadata_generated",
}
_REQUIRED_GATE_CHECKPOINTS = {
    "manual_handoff_gate",
    "exact_confirmation_gate",
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
    problems.extend(_case_gap_readiness_problems(packet))
    problems.extend(_crawl_promotion_audit_problems(packet.get("crawl_promotion_audit")))
    problems.extend(_devhub_surface_map_readiness_problems(packet.get("devhub_surface_map_readiness")))
    problems.extend(_preview_metadata_problems(packet.get("preview_metadata") or packet.get("local_draft_preview")))
    problems.extend(_journal_checkpoint_problems(packet.get("action_journal_expectations")))
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
                    problems.append(
                        f"source evidence {evidence_id} citation_spans[{span_index}] lacks a page or character span anchor"
                    )
    return problems


def _case_gap_readiness_problems(packet: Mapping[str, Any]) -> list[str]:
    case_gap = packet.get("case_gap_report")
    process_bundle = packet.get("process_bundle")
    if not isinstance(case_gap, Mapping):
        return ["case_gap_report is required"]

    problems: list[str] = []
    if _non_empty_list(case_gap.get("stale_evidence")):
        problems.append("case_gap_report contains stale_evidence")
    if _non_empty_list(case_gap.get("conflicting_evidence")):
        problems.append("case_gap_report contains conflicting_evidence")
    if _non_empty_list(case_gap.get("conflicting_facts")):
        problems.append("case_gap_report contains conflicting_facts")
    if _non_empty_list(case_gap.get("missing_facts")):
        problems.append("case_gap_report contains missing_facts")
    if _non_empty_list(case_gap.get("missing_documents")):
        problems.append("case_gap_report contains missing_documents")

    if isinstance(process_bundle, Mapping):
        required_fact_ids = _string_set(process_bundle.get("required_user_fact_ids"))
        present_fact_ids = {
            str(item.get("fact_id"))
            for item in _mapping_items(case_gap.get("known_facts"))
            if item.get("presence") == "present" and isinstance(item.get("fact_id"), str)
        }
        for fact_id in sorted(required_fact_ids - present_fact_ids):
            problems.append(f"required fact is not present: {fact_id}")

        required_document_ids = _string_set(process_bundle.get("required_document_ids"))
        matched_document_ids = _string_set(case_gap.get("matched_document_ids"))
        for document_id in sorted(required_document_ids - matched_document_ids):
            problems.append(f"required document is not matched: {document_id}")
    else:
        problems.append("process_bundle is required for required fact validation")

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
    actions = surface.get("actions")
    if not isinstance(actions, list) or not actions:
        problems.append("devhub_surface_map_readiness must include actions")
    if not _collect_evidence_refs(surface):
        problems.append("devhub_surface_map_readiness must cite source_evidence_ids")
    if surface.get("requires_attendance") is not True:
        problems.append("devhub_surface_map_readiness must require attendance for official actions")
    if surface.get("requires_exact_confirmation") is not True:
        problems.append("devhub_surface_map_readiness must require exact confirmation for official actions")
    problems.extend(_selector_confidence_problems(surface, "devhub_surface_map_readiness"))
    return problems


def _selector_confidence_problems(value: Any, path: str) -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        if "selector_confidence" in value:
            if not _selector_confidence_is_high(value.get("selector_confidence")):
                problems.append(f"selector confidence is low at {path}")
        elif path == "devhub_surface_map_readiness":
            problems.append("devhub_surface_map_readiness is missing selector_confidence")
        for key, child in value.items():
            problems.extend(_selector_confidence_problems(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_selector_confidence_problems(child, f"{path}[{index}]"))
    return problems


def _selector_confidence_is_high(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return float(value) >= _MIN_SELECTOR_CONFIDENCE
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _HIGH_SELECTOR_CONFIDENCE_LABELS:
            return True
        try:
            return float(normalized) >= _MIN_SELECTOR_CONFIDENCE
        except ValueError:
            return False
    return False


def _preview_metadata_problems(preview: Any) -> list[str]:
    if not isinstance(preview, Mapping):
        return ["preview_metadata is required"]

    problems: list[str] = []
    for key in ("preview_id", "preview_type", "generated_at"):
        if not preview.get(key):
            problems.append(f"preview_metadata is missing {key}")
    if preview.get("metadata_only") is not True:
        problems.append("preview_metadata must be metadata_only")
    if preview.get("no_private_values") is not True:
        problems.append("preview_metadata must confirm no_private_values")
    if preview.get("no_official_submission") is not True:
        problems.append("preview_metadata must confirm no_official_submission")
    if not _collect_evidence_refs(preview):
        problems.append("preview_metadata must cite source_evidence_ids")
    return problems


def _journal_checkpoint_problems(journal: Any) -> list[str]:
    if not isinstance(journal, Mapping):
        return ["action_journal_expectations is required"]

    problems: list[str] = []
    checkpoints = journal.get("checkpoints")
    if not isinstance(checkpoints, list) or not checkpoints:
        return ["action_journal_expectations.checkpoints must be non-empty"]

    checkpoint_by_id: dict[str, Mapping[str, Any]] = {}
    for index, checkpoint in enumerate(checkpoints):
        if not isinstance(checkpoint, Mapping):
            problems.append(f"action_journal_expectations.checkpoints[{index}] must be an object")
            continue
        checkpoint_id = checkpoint.get("checkpoint_id")
        if not isinstance(checkpoint_id, str) or not checkpoint_id:
            problems.append(f"action_journal_expectations.checkpoints[{index}] is missing checkpoint_id")
            continue
        checkpoint_by_id[checkpoint_id] = checkpoint
        if not _collect_evidence_refs(checkpoint):
            problems.append(f"journal checkpoint {checkpoint_id} must cite source_evidence_ids")

    for checkpoint_id in sorted(_REQUIRED_COMPLETE_CHECKPOINTS):
        checkpoint = checkpoint_by_id.get(checkpoint_id)
        if checkpoint is None:
            problems.append(f"required journal checkpoint is missing: {checkpoint_id}")
            continue
        status = str(checkpoint.get("status") or "").lower()
        if status not in _COMPLETE_CHECKPOINT_STATUSES:
            problems.append(f"journal checkpoint {checkpoint_id} is incomplete: status={status or 'missing'}")

    for checkpoint_id in sorted(_REQUIRED_GATE_CHECKPOINTS):
        checkpoint = checkpoint_by_id.get(checkpoint_id)
        if checkpoint is None:
            problems.append(f"required journal checkpoint is missing: {checkpoint_id}")
            continue
        status = str(checkpoint.get("status") or "").lower()
        if status not in _GATE_CHECKPOINT_STATUSES:
            problems.append(f"journal checkpoint {checkpoint_id} is incomplete: status={status or 'missing'}")

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


def _mapping_items(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str) and item}


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0
