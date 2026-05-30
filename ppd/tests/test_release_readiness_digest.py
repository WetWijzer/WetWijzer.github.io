from __future__ import annotations

import json
from pathlib import Path

from ppd.release_readiness_digest import build_inactive_release_readiness_digest


FIXTURES = Path(__file__).parent / "fixtures" / "inactive_release_readiness_digest_v1"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_digest_builds_ordered_rows_and_carry_forward_fields() -> None:
    digest = build_inactive_release_readiness_digest(
        _load_fixture("inactive_release_decision_packet_v2.json"),
        _load_fixture("release_rollback_rehearsal_packet_v1.json"),
    )

    rows = digest["readiness_summary_rows"]
    assert digest["schema_version"] == "inactive_release_promotion_readiness_digest.v1"
    assert digest["promotion_action"] == "none_fixture_readiness_digest_only"
    assert [row["artifact_id"] for row in rows] == ["inactive-alpha", "inactive-beta"]
    assert rows[0]["rollback_rehearsal_ref"] == "rollback-rehearsal-alpha-001"
    assert rows[1]["unresolved_blockers"] == ["missing reviewer handoff owner"]
    assert digest["carry_forward"] == {
        "unresolved_holds": ["awaiting legal review"],
        "unresolved_blockers": ["missing reviewer handoff owner"],
    }
    assert digest["no_go_reasons"] == ["rollback rehearsal owner not assigned"]


def test_digest_preserves_validation_inventory_and_handoff_placeholders() -> None:
    digest = build_inactive_release_readiness_digest(
        _load_fixture("inactive_release_decision_packet_v2.json"),
        _load_fixture("release_rollback_rehearsal_packet_v1.json"),
    )

    assert digest["prerequisite_validation_command_inventory"] == [
        "python3 ppd/daemon/ppd_daemon.py --self-test",
        "python3 -m pytest ppd/tests/test_release_readiness_digest.py",
    ]
    assert digest["reviewer_handoff_placeholders"] == {
        "inactive-alpha": "reviewer_handoff_pending: inactive-alpha",
        "inactive-beta": "reviewer_handoff_pending: inactive-beta",
    }
