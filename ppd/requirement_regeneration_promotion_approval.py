"""Build fixture-first requirement regeneration promotion approval packets.

The packet is intentionally offline and deterministic: it consumes already-captured
candidate, blocker-closure, and freshness-acceptance packets and emits cited
approve/defer decisions without mutating active requirements or release artifacts.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Sequence


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _ids(items: Iterable[Mapping[str, Any]]) -> List[str]:
    result: List[str] = []
    for item in items:
        item_id = item.get("id") or item.get("artifact_id") or item.get("delta_id")
        if item_id is not None:
            result.append(str(item_id))
    return sorted(set(result))


def _citations(*packets: Mapping[str, Any]) -> List[str]:
    citations: List[str] = []
    for packet in packets:
        for citation in _as_list(packet.get("citations")):
            citations.append(str(citation))
        packet_id = packet.get("packet_id")
        if packet_id:
            citations.append(str(packet_id))
    return sorted(set(citations))


def build_approval_packet(
    candidate_packet: Mapping[str, Any],
    release_blocker_packet: Mapping[str, Any],
    freshness_packet: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return a cited approval packet for requirement regeneration deltas."""

    candidate_deltas = _as_list(candidate_packet.get("candidate_deltas"))
    closed_blockers = _as_list(release_blocker_packet.get("closed_blockers"))
    open_blockers = _as_list(release_blocker_packet.get("open_blockers"))
    accepted_freshness_ids = set(str(item) for item in _as_list(freshness_packet.get("accepted_delta_ids")))
    blocked_delta_ids = set(str(item) for item in _as_list(release_blocker_packet.get("blocked_delta_ids")))

    blocker_clear = bool(release_blocker_packet.get("release_blockers_closed")) and not open_blockers
    freshness_clear = bool(freshness_packet.get("freshness_regression_accepted"))
    base_citations = _citations(candidate_packet, release_blocker_packet, freshness_packet)

    decisions: List[Dict[str, Any]] = []
    for delta in candidate_deltas:
        delta_id = str(delta.get("id"))
        delta_citations = sorted(set(base_citations + [str(item) for item in _as_list(delta.get("citations"))]))
        approve = blocker_clear and freshness_clear and delta_id in accepted_freshness_ids and delta_id not in blocked_delta_ids
        if approve:
            rationale = "Candidate delta is covered by release blocker closure and accepted freshness regression evidence."
            decision = "approve"
        else:
            rationale = "Candidate delta is deferred until blocker closure, freshness acceptance, and blocked-delta checks all pass."
            decision = "defer"
        decisions.append(
            {
                "delta_id": delta_id,
                "decision": decision,
                "rationale": rationale,
                "citations": delta_citations,
                "impacted_artifact_ids": sorted(set(str(item) for item in _as_list(delta.get("impacted_artifact_ids")))),
                "rollback": {
                    "required": approve,
                    "plan": str(delta.get("rollback_plan") or "Restore the prior fixture packet and rerun offline validation before any promotion retry."),
                },
                "reviewer_signoff": {
                    "required": True,
                    "reviewer": None,
                    "signed_at": None,
                    "status": "pending",
                },
            }
        )

    impacted_artifact_ids = sorted(
        set(
            _ids(candidate_deltas)
            + _ids(closed_blockers)
            + [str(item) for item in _as_list(candidate_packet.get("impacted_artifact_ids"))]
            + [str(item) for item in _as_list(freshness_packet.get("impacted_artifact_ids"))]
            + [str(item) for item in _as_list(release_blocker_packet.get("impacted_artifact_ids"))]
        )
    )

    return {
        "packet_id": "requirement-regeneration-promotion-approval-packet",
        "packet_type": "fixture-first-requirement-regeneration-promotion-approval",
        "source_packet_ids": [
            str(candidate_packet.get("packet_id")),
            str(release_blocker_packet.get("packet_id")),
            str(freshness_packet.get("packet_id")),
        ],
        "decisions": decisions,
        "expected_offline_validation_commands": deepcopy(
            candidate_packet.get(
                "expected_offline_validation_commands",
                [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]],
            )
        ),
        "impacted_artifact_ids": impacted_artifact_ids,
        "attestations": {
            "no_active_requirement_mutation": True,
            "no_active_process_mutation": True,
            "no_active_guardrail_mutation": True,
            "no_active_prompt_mutation": True,
            "no_active_release_mutation": True,
        },
        "citations": base_citations,
    }
