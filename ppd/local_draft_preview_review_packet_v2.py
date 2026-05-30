"""Build a fixture-first local draft preview review packet v2.

This module is intentionally offline-only. It consumes committed JSON fixtures and
returns reviewer-visible rows with citations, confirmation checkpoints, blocker
summaries, rollback notes, owner fields, validation commands, and guardrail
attestations. It does not read PDFs, write PDFs, upload files, call DevHub, or
mutate agent state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ATTESTATIONS = {
    "no_private_documents": True,
    "no_pdf_write": True,
    "no_upload": True,
    "no_devhub": True,
    "no_agent_state_mutation": True,
}

VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/local_draft_preview_review_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_local_draft_preview_review_packet_v2.py"],
]


def load_fixture(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must be a JSON object: {path}")
    return data


def _citation(source: dict[str, Any], fallback_id: str) -> str:
    label = str(source.get("label") or fallback_id)
    locator = str(source.get("locator") or "fixture")
    return f"{label} ({locator})"


def _indexed_sources(*fixtures: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for fixture in fixtures:
        for source in fixture.get("sources", []):
            if isinstance(source, dict) and source.get("id"):
                sources[str(source["id"])] = source
    return sources


def build_review_packet(
    preview_plan: dict[str, Any],
    readiness_packet: dict[str, Any],
    gap_analysis: dict[str, Any],
) -> dict[str, Any]:
    sources = _indexed_sources(preview_plan, readiness_packet, gap_analysis)
    rows: list[dict[str, Any]] = []

    for item in preview_plan.get("preview_rows", []):
        if not isinstance(item, dict):
            continue
        source_id = str(item.get("source_id") or "preview-plan")
        source = sources.get(source_id, {"label": source_id, "locator": "fixture"})
        rows.append(
            {
                "row_id": str(item.get("row_id") or source_id),
                "reviewer_visible_value": str(item.get("value") or ""),
                "value_explanation": str(item.get("explanation") or "Fixture-backed draft preview value."),
                "citation": _citation(source, source_id),
                "reviewer_owner": str(item.get("reviewer_owner") or "PP&D reviewer"),
                "confirmation_checkpoint": str(item.get("confirmation_checkpoint") or "Confirm fixture value before any live or authenticated workflow."),
                "rollback_note": str(item.get("rollback_note") or "Remove this fixture row if the cited local source changes."),
            }
        )

    blockers = []
    for blocker in readiness_packet.get("unresolved_blockers", []):
        if isinstance(blocker, dict):
            blockers.append(
                {
                    "blocker_id": str(blocker.get("id") or "blocker"),
                    "summary": str(blocker.get("summary") or "Unresolved readiness blocker."),
                    "owner": str(blocker.get("owner") or "PP&D reviewer"),
                    "citation": _citation(sources.get(str(blocker.get("source_id") or "readiness"), {}), str(blocker.get("source_id") or "readiness")),
                }
            )

    gaps = []
    for gap in gap_analysis.get("gaps", []):
        if isinstance(gap, dict):
            gaps.append(
                {
                    "gap_id": str(gap.get("id") or "gap"),
                    "summary": str(gap.get("summary") or "Fixture gap requires reviewer attention."),
                    "exact_confirmation": str(gap.get("exact_confirmation") or "Confirm the missing local evidence before escalation."),
                    "owner": str(gap.get("owner") or "PP&D reviewer"),
                }
            )

    return {
        "packet_version": "local-draft-preview-review-packet-v2",
        "mode": "fixture-first-offline",
        "reviewer_visible_preview_rows": rows,
        "unresolved_blocker_summaries": blockers,
        "gap_analysis_checkpoints": gaps,
        "offline_validation_commands": VALIDATION_COMMANDS,
        "attestations": dict(ATTESTATIONS),
    }


def build_from_paths(preview_plan_path: Path, readiness_packet_path: Path, gap_analysis_path: Path) -> dict[str, Any]:
    return build_review_packet(
        load_fixture(preview_plan_path),
        load_fixture(readiness_packet_path),
        load_fixture(gap_analysis_path),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build local draft preview review packet v2 from fixtures.")
    parser.add_argument("preview_plan", type=Path)
    parser.add_argument("readiness_packet", type=Path)
    parser.add_argument("gap_analysis", type=Path)
    args = parser.parse_args()
    packet = build_from_paths(args.preview_plan, args.readiness_packet, args.gap_analysis)
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
