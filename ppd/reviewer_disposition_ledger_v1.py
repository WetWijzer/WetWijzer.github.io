"""Fixture-first reviewer disposition ledger v1.

This module is intentionally offline-only. It consumes committed reviewer queue
fixtures and emits deterministic disposition records for PP&D review planning.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_ATTESTATIONS = {
    "no_live": True,
    "no_auth": True,
    "no_private_artifact": True,
    "no_official_action": True,
    "no_active_mutation": True,
}

QUEUE_ORDER = [
    "public_source_refresh_reviewer_queue_v1",
    "devhub_manual_observation_reviewer_queue_v1",
    "supervised_offline_release_rehearsal_v1",
]


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _record_from_item(queue_name: str, item: dict[str, Any], index: int) -> dict[str, Any]:
    missing = [key for key in REQUIRED_ATTESTATIONS if item.get("attestations", {}).get(key) is not True]
    if missing:
        raise ValueError(f"{queue_name}:{item.get('id', index)} missing attestations: {', '.join(missing)}")

    disposition = item["recommended_disposition"]
    if disposition not in {"approve", "defer", "block"}:
        raise ValueError(f"{queue_name}:{item.get('id', index)} has invalid disposition {disposition!r}")

    citations = item.get("citations", [])
    if not citations:
        raise ValueError(f"{queue_name}:{item.get('id', index)} must include at least one citation")

    return {
        "id": f"reviewer-disposition-v1-{queue_name}-{index:03d}",
        "source_queue": queue_name,
        "source_item_id": item["id"],
        "disposition": disposition,
        "reviewer_owner": item["reviewer_owner"],
        "decision_rationale": item["decision_rationale"],
        "dependency_order": item["dependency_order"],
        "rollback_note": item["rollback_note"],
        "expected_follow_up_artifact": item["expected_follow_up_artifact"],
        "offline_validation_command": item["offline_validation_command"],
        "citations": citations,
        "attestations": dict(REQUIRED_ATTESTATIONS),
    }


def build_reviewer_disposition_ledger(fixture_dir: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for queue_name in QUEUE_ORDER:
        queue_path = fixture_dir / f"{queue_name}.json"
        queue = _load_json(queue_path)
        for index, item in enumerate(queue["items"], start=1):
            records.append(_record_from_item(queue_name, item, index))

    return {
        "schema": "ppd.reviewer_disposition_ledger.v1",
        "source_queues": QUEUE_ORDER,
        "fixture_first": True,
        "records": records,
    }


def main() -> None:
    fixture_dir = Path(__file__).parent / "tests" / "fixtures" / "reviewer_disposition_ledger_v1"
    print(json.dumps(build_reviewer_disposition_ledger(fixture_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
