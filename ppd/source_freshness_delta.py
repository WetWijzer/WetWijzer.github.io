"""Fixture-first source freshness delta review packet builder.

This module is intentionally side-effect free. It consumes already captured
metadata packets and produces reviewer-facing delta decisions without fetching
sources, running processors, updating registries, mutating requirements, or
changing guardrail outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

Decision = Dict[str, Any]
Packet = Dict[str, Any]

_ATTESTATIONS: Dict[str, bool] = {
    "no_fetch_performed": True,
    "no_processor_invoked": True,
    "no_registry_mutation": True,
    "no_requirement_mutation": True,
    "no_guardrail_mutation": True,
}

_STALE_DISPOSITIONS = {"stale", "stale_evidence", "requires_refresh", "expired"}
_CHANGED_DISPOSITIONS = {"changed", "source_changed", "content_changed"}
_UNCHANGED_DISPOSITIONS = {"unchanged", "current", "accepted_current"}


def build_source_freshness_delta_review_packet(
    refresh_metadata_intake: Mapping[str, Any],
    evidence_watchlist_disposition: Mapping[str, Any],
    schedule_update_candidate: Mapping[str, Any],
) -> Packet:
    """Build a deterministic source freshness delta review packet.

    The inputs are packet dictionaries, typically loaded from fixtures. The
    function accepts a small range of field aliases so future intake fixtures can
    evolve without requiring shared contract changes.
    """

    refresh_records = _records_by_source(
        refresh_metadata_intake,
        preferred_keys=("sources", "refresh_records", "records"),
    )
    disposition_records = _records_by_source(
        evidence_watchlist_disposition,
        preferred_keys=("dispositions", "watchlist_dispositions", "records"),
    )
    schedule_records = _records_by_source(
        schedule_update_candidate,
        preferred_keys=("schedule_candidates", "candidate_updates", "records"),
    )

    source_ids = sorted(
        set(refresh_records) | set(disposition_records) | set(schedule_records)
    )

    decisions: List[Decision] = []
    affected_source_ids: List[str] = []
    offline_queues: List[Dict[str, Any]] = []
    reviewer_owner_fields: Dict[str, Dict[str, Optional[str]]] = {}

    for source_id in source_ids:
        refresh = refresh_records.get(source_id, {})
        disposition = disposition_records.get(source_id, {})
        schedule = schedule_records.get(source_id, {})

        decision_value = _classify_decision(refresh, disposition)
        citations = _citations_for_source(refresh, disposition, schedule)
        rationale = _rationale_for_source(decision_value, refresh, disposition, schedule)
        queues = _queues_for_source(decision_value, disposition, schedule)

        if decision_value in {"changed", "stale"}:
            affected_source_ids.append(source_id)

        for queue in queues:
            offline_queues.append(
                {
                    "source_id": source_id,
                    "queue": queue,
                    "reason": decision_value,
                }
            )

        reviewer_owner_fields[source_id] = {
            "reviewer_owner": _string_or_none(
                disposition.get("reviewer_owner")
                or disposition.get("owner")
                or schedule.get("reviewer_owner")
            ),
            "reviewer_status": _string_or_none(
                disposition.get("reviewer_status") or disposition.get("status")
            ),
            "reviewed_at": _string_or_none(
                disposition.get("reviewed_at") or disposition.get("decided_at")
            ),
        }

        decisions.append(
            {
                "source_id": source_id,
                "decision": decision_value,
                "citations": citations,
                "rationale": rationale,
                "recommended_offline_follow_up_queues": queues,
                "reviewer_owner_fields": reviewer_owner_fields[source_id],
            }
        )

    return {
        "packet_type": "ppd_source_freshness_delta_review",
        "packet_version": "1.0",
        "input_packet_refs": {
            "public_source_refresh_metadata_intake_packet": _packet_ref(
                refresh_metadata_intake
            ),
            "evidence_freshness_watchlist_reviewer_disposition_packet": _packet_ref(
                evidence_watchlist_disposition
            ),
            "source_registry_schedule_update_candidate_packet": _packet_ref(
                schedule_update_candidate
            ),
        },
        "decisions": decisions,
        "affected_source_ids": sorted(affected_source_ids),
        "recommended_offline_follow_up_queues": offline_queues,
        "reviewer_owner_fields": reviewer_owner_fields,
        "attestations": dict(_ATTESTATIONS),
    }


def load_packet(path: Path) -> Packet:
    with path.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError(f"packet must be a JSON object: {path}")
    return packet


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a PP&D source freshness delta review packet from fixtures."
    )
    parser.add_argument("refresh_metadata_intake", type=Path)
    parser.add_argument("watchlist_disposition", type=Path)
    parser.add_argument("schedule_update_candidate", type=Path)
    args = parser.parse_args(argv)

    packet = build_source_freshness_delta_review_packet(
        load_packet(args.refresh_metadata_intake),
        load_packet(args.watchlist_disposition),
        load_packet(args.schedule_update_candidate),
    )
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


def _records_by_source(
    packet: Mapping[str, Any], preferred_keys: Sequence[str]
) -> Dict[str, Mapping[str, Any]]:
    records: Any = None
    for key in preferred_keys:
        if key in packet:
            records = packet[key]
            break
    if records is None:
        records = packet.get("items", [])

    if isinstance(records, Mapping):
        iterable: Iterable[Any] = records.values()
    elif isinstance(records, list):
        iterable = records
    else:
        raise ValueError("packet records must be a list or object")

    indexed: Dict[str, Mapping[str, Any]] = {}
    for record in iterable:
        if not isinstance(record, Mapping):
            raise ValueError("each packet record must be a JSON object")
        source_id = record.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("each packet record must include source_id")
        indexed[source_id] = record
    return indexed


def _classify_decision(
    refresh: Mapping[str, Any], disposition: Mapping[str, Any]
) -> str:
    disposition_value = str(
        disposition.get("disposition") or disposition.get("reviewer_disposition") or ""
    ).lower()
    freshness_status = str(refresh.get("freshness_status") or "").lower()
    http_status = refresh.get("http_status")

    if disposition_value in _STALE_DISPOSITIONS or freshness_status == "stale":
        return "stale"
    if isinstance(http_status, int) and http_status >= 400:
        return "stale"
    if disposition_value in _CHANGED_DISPOSITIONS:
        return "changed"
    if disposition_value in _UNCHANGED_DISPOSITIONS:
        return "unchanged"

    previous_hash = refresh.get("previous_content_hash") or refresh.get("prior_content_hash")
    current_hash = refresh.get("content_hash") or refresh.get("current_content_hash")
    if previous_hash and current_hash and previous_hash != current_hash:
        return "changed"
    return "unchanged"


def _citations_for_source(
    refresh: Mapping[str, Any],
    disposition: Mapping[str, Any],
    schedule: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    citations: List[Dict[str, Any]] = []
    for packet_name, record in (
        ("refresh_metadata_intake", refresh),
        ("watchlist_reviewer_disposition", disposition),
        ("schedule_update_candidate", schedule),
    ):
        for evidence_id in _as_list(
            record.get("evidence_ids") or record.get("citation_ids") or record.get("citations")
        ):
            citations.append({"packet": packet_name, "evidence_id": str(evidence_id)})
    return citations


def _rationale_for_source(
    decision: str,
    refresh: Mapping[str, Any],
    disposition: Mapping[str, Any],
    schedule: Mapping[str, Any],
) -> List[str]:
    rationale: List[str] = []
    previous_hash = refresh.get("previous_content_hash") or refresh.get("prior_content_hash")
    current_hash = refresh.get("content_hash") or refresh.get("current_content_hash")
    if previous_hash and current_hash:
        if previous_hash == current_hash:
            rationale.append("refresh content hash matches previous content hash")
        else:
            rationale.append("refresh content hash differs from previous content hash")

    for key in ("rationale", "reviewer_notes", "schedule_rationale"):
        for record in (disposition, schedule):
            value = record.get(key)
            if isinstance(value, str) and value:
                rationale.append(value)

    if not rationale:
        rationale.append(f"classified as {decision} from available packet metadata")
    return rationale


def _queues_for_source(
    decision: str,
    disposition: Mapping[str, Any],
    schedule: Mapping[str, Any],
) -> List[str]:
    queues: List[str] = []
    for value in (
        disposition.get("recommended_offline_follow_up_queue"),
        disposition.get("follow_up_queue"),
        schedule.get("recommended_offline_follow_up_queue"),
        schedule.get("offline_follow_up_queue"),
    ):
        queues.extend(str(item) for item in _as_list(value) if item)

    if decision == "stale" and not queues:
        queues.append("source-owner-offline-refresh-review")
    elif decision == "changed" and not queues:
        queues.append("source-delta-review")

    return sorted(set(queues))


def _packet_ref(packet: Mapping[str, Any]) -> Dict[str, Optional[str]]:
    return {
        "packet_id": _string_or_none(packet.get("packet_id")),
        "packet_type": _string_or_none(packet.get("packet_type")),
        "created_at": _string_or_none(packet.get("created_at")),
    }


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _string_or_none(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
