from __future__ import annotations

import json
from pathlib import Path

from ppd.offline_patch_approval_matrix_v2 import REQUIRED_ATTESTATIONS, build_approval_matrix_v2

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "offline_patch_approval_matrix_v2"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_builds_expected_fixture_first_matrix_v2() -> None:
    packet = _load_fixture("combined_packets_v2.json")
    expected = _load_fixture("expected_matrix_v2.json")

    assert build_approval_matrix_v2(packet) == expected


def test_matrix_contains_required_review_and_safety_fields() -> None:
    matrix = build_approval_matrix_v2(_load_fixture("combined_packets_v2.json"))

    assert {row["decision"] for row in matrix["rows"]} == {"approve", "defer", "reject"}
    assert {row["row_kind"] for row in matrix["rows"]} == {
        "source",
        "devhub_surface",
        "guardrail_preview",
    }
    assert matrix["required_attestations"] == list(REQUIRED_ATTESTATIONS)

    for row in matrix["rows"]:
        assert row["citation_ids"]
        assert row["reviewer_owner"]
        assert isinstance(row["dependency_order"], int)
        assert row["rollback_verification_notes"]
        assert row["required_offline_validation_commands"]
        assert row["attestations"] == {
            "no_live_access": True,
            "no_auth_access": True,
            "no_official_action": True,
            "no_active_registry_mutation": True,
            "no_active_guardrail_mutation": True,
        }


def test_missing_citation_rejects_without_live_lookup() -> None:
    packet = _load_fixture("combined_packets_v2.json")
    packet["offline_patch_rehearsal_packet_v2"]["sources"][0]["citation_ids"] = []

    matrix = build_approval_matrix_v2(packet)
    rejected = next(
        row
        for row in matrix["rows"]
        if row["item_id"] == "ppd-online-tools-overview"
    )

    assert rejected["decision"] == "reject"
    assert rejected["attestations"]["no_live_access"] is True
