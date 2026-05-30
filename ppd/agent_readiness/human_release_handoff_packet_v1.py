"""Fixture-first human release handoff packet v1.

This module is intentionally offline-only. It turns acceptance rehearsal and reviewer
ledger fixtures into a deterministic human-readable release recommendation packet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = "human_release_handoff_packet_v1"

NO_ACTION_STATEMENTS = (
    "No live crawl has been performed.",
    "No DevHub login has been performed.",
    "No private artifact handling has been performed.",
    "No official action has been performed.",
    "No active promotion has been performed.",
)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _citation(item: Mapping[str, Any], fallback: str) -> str:
    for key in ("citation", "cite", "source", "id", "fixture", "fixture_id"):
        value = item.get(key)
        if value:
            return str(value)
    return fallback


def _collect_fixture_families(*sections: Mapping[str, Any]) -> list[str]:
    families: set[str] = set()
    for section in sections:
        for key in ("fixture_families", "fixtureFamilies", "families", "fixtures_to_inspect"):
            for value in _as_list(section.get(key)):
                if isinstance(value, Mapping):
                    name = value.get("family") or value.get("name") or value.get("path")
                    if name:
                        families.add(str(name))
                elif value:
                    families.add(str(value))
        for item in _as_list(section.get("checks")) + _as_list(section.get("dispositions")):
            if isinstance(item, Mapping):
                family = item.get("fixture_family") or item.get("family")
                if family:
                    families.add(str(family))
    return sorted(families)


def _collect_blockers(summary: Mapping[str, Any], ledger: Mapping[str, Any]) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    for source_name, section in (("acceptance_rehearsal", summary), ("reviewer_ledger", ledger)):
        explicit = section.get("unresolved_blockers") or section.get("blockers") or []
        for index, blocker in enumerate(_as_list(explicit), start=1):
            if isinstance(blocker, Mapping):
                text = blocker.get("blocker") or blocker.get("summary") or blocker.get("description") or blocker.get("name")
                cite = _citation(blocker, f"{source_name}:blocker:{index}")
            else:
                text = blocker
                cite = f"{source_name}:blocker:{index}"
            if text:
                blockers.append({"blocker": str(text), "citation": cite})
    for index, disposition in enumerate(_as_list(ledger.get("dispositions")), start=1):
        if not isinstance(disposition, Mapping):
            continue
        state = _text(disposition.get("disposition") or disposition.get("status")).lower()
        if state in {"block", "blocked", "hold", "rejected", "needs-work", "needs_work"}:
            text = disposition.get("reason") or disposition.get("summary") or disposition.get("reviewer") or "Reviewer disposition is not apply-ready."
            blockers.append({"blocker": str(text), "citation": _citation(disposition, f"reviewer_ledger:disposition:{index}")})
    return blockers


def _collect_recommendation_citations(summary: Mapping[str, Any], ledger: Mapping[str, Any]) -> list[str]:
    citations: set[str] = set()
    for source_name, section in (("acceptance_rehearsal", summary), ("reviewer_ledger", ledger)):
        if isinstance(section.get("citation"), str):
            citations.add(section["citation"])
        for key in ("checks", "dispositions", "recommendations"):
            for index, item in enumerate(_as_list(section.get(key)), start=1):
                if isinstance(item, Mapping):
                    citations.add(_citation(item, f"{source_name}:{key}:{index}"))
    return sorted(citations)


def build_human_release_handoff_packet_v1(source_inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic handoff packet from offline fixture inputs."""
    summary = source_inputs.get("offline_acceptance_rehearsal_summary_v1") or source_inputs.get("acceptance_rehearsal_summary_v1") or {}
    ledger = source_inputs.get("reviewer_disposition_ledger_v1") or {}
    if not isinstance(summary, Mapping):
        raise TypeError("offline_acceptance_rehearsal_summary_v1 must be an object")
    if not isinstance(ledger, Mapping):
        raise TypeError("reviewer_disposition_ledger_v1 must be an object")

    blockers = _collect_blockers(summary, ledger)
    rehearsal_status = _text(summary.get("status") or summary.get("result"), "unknown").lower()
    ledger_status = _text(ledger.get("status") or ledger.get("disposition"), "unknown").lower()
    apply_ready = not blockers and rehearsal_status in {"pass", "passed", "accepted", "green"} and ledger_status in {"approved", "apply", "accepted", "green"}
    recommendation = "APPLY" if apply_ready else "HOLD"

    citations = _collect_recommendation_citations(summary, ledger)
    if not citations:
        citations = ["offline_acceptance_rehearsal_summary_v1", "reviewer_disposition_ledger_v1"]

    fixture_families = _collect_fixture_families(summary, ledger)
    if not fixture_families:
        fixture_families = ["offline_acceptance_rehearsal_summary_v1", "reviewer_disposition_ledger_v1"]

    rationale = (
        "Apply recommendation is supported by passing offline acceptance rehearsal and approved reviewer ledger fixtures."
        if apply_ready
        else "Hold recommendation is required until cited blockers or non-approved fixture evidence is resolved."
    )

    packet = {
        "schema_version": SCHEMA_VERSION,
        "recommendation": recommendation,
        "human_readable_recommendation": f"{recommendation}: {rationale}",
        "recommendation_citations": citations,
        "fixture_families_to_inspect": fixture_families,
        "unresolved_blockers": blockers,
        "rollback_note": source_inputs.get("rollback_note") or "If the release is applied and validation fails, revert the fixture-backed release change and keep promotion on hold until a new offline packet is reviewed.",
        "post_apply_validation_checklist": source_inputs.get("post_apply_validation_checklist") or [
            "Run the offline acceptance rehearsal summary fixture tests.",
            "Review the reviewer disposition ledger fixture for approval state changes.",
            "Confirm inspected fixture families match this handoff packet exactly.",
            "Verify no unresolved blockers remain before any human promotion decision.",
        ],
        "no_action_statements": list(NO_ACTION_STATEMENTS),
    }
    packet["rendered"] = render_human_release_handoff_packet_v1(packet)
    return packet


def render_human_release_handoff_packet_v1(packet_or_inputs: Mapping[str, Any]) -> str:
    """Render either a built packet or raw source inputs as a human-readable packet."""
    packet = packet_or_inputs
    if packet.get("schema_version") != SCHEMA_VERSION:
        packet = build_human_release_handoff_packet_v1(packet_or_inputs)

    lines = [
        "Human Release Handoff Packet v1",
        f"Recommendation: {packet['recommendation']}",
        f"Rationale: {packet['human_readable_recommendation']}",
        "Citations:",
    ]
    lines.extend(f"- {citation}" for citation in packet["recommendation_citations"])
    lines.append("Fixture families to inspect:")
    lines.extend(f"- {family}" for family in packet["fixture_families_to_inspect"])
    lines.append("Unresolved blockers:")
    blockers = packet["unresolved_blockers"]
    if blockers:
        lines.extend(f"- {item['blocker']} [{item['citation']}]" for item in blockers)
    else:
        lines.append("- None cited by supplied fixtures.")
    lines.append(f"Rollback note: {packet['rollback_note']}")
    lines.append("Post-apply validation checklist:")
    lines.extend(f"- {item}" for item in packet["post_apply_validation_checklist"])
    lines.append("Explicit non-action statements:")
    lines.extend(f"- {statement}" for statement in packet["no_action_statements"])
    return "\n".join(lines)


build_packet = build_human_release_handoff_packet_v1
render_packet = render_human_release_handoff_packet_v1


def load_source_inputs(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError("source inputs fixture must be a JSON object")
    return data


def main(argv: Iterable[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: human_release_handoff_packet_v1.py SOURCE_INPUTS_JSON", file=sys.stderr)
        return 2
    packet = build_human_release_handoff_packet_v1(load_source_inputs(args[0]))
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
