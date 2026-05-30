from pathlib import Path

from ppd.release.offline_release_candidate_validation import (
    REQUIRED_ATTESTATIONS,
    build_offline_release_candidate_checklist,
    load_json_packet,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "offline_release_candidate_validation"


def _load_fixture(name: str) -> dict:
    return load_json_packet(FIXTURE_DIR / name)


def test_offline_release_candidate_checklist_builds_ordered_go_gates() -> None:
    checklist = build_offline_release_candidate_checklist(
        _load_fixture("offline_release_candidate_assembly_packet.json"),
        _load_fixture("release_acceptance_review_packet.json"),
        _load_fixture("release_rollback_drill_outcome_review_packet.json"),
    )

    packet = checklist.to_dict()

    assert packet["checklist_id"] == "offline-rc-validation-rc-20260529-offline-001"
    assert packet["release_candidate_id"] == "rc-20260529-offline-001"
    assert packet["final_decision"] == "go"
    assert [gate["order"] for gate in packet["gates"]] == [1, 2, 3, 4, 5, 6, 7]
    assert [gate["decision"] for gate in packet["gates"]] == ["go"] * 7
    assert [gate["gate_id"] for gate in packet["gates"]] == [
        "gate-01-fixture-source-integrity",
        "gate-02-offline-assembly-packet",
        "gate-03-release-acceptance-review",
        "gate-04-rollback-drill-outcome",
        "gate-05-residual-blocker-disposition",
        "gate-06-reviewer-owner-fields",
        "gate-07-offline-boundary-attestations",
    ]


def test_checklist_preserves_blockers_rollback_refs_and_reviewers() -> None:
    checklist = build_offline_release_candidate_checklist(
        _load_fixture("offline_release_candidate_assembly_packet.json"),
        _load_fixture("release_acceptance_review_packet.json"),
        _load_fixture("release_rollback_drill_outcome_review_packet.json"),
    )
    packet = checklist.to_dict()

    assert packet["source_packet_ids"] == [
        "assembly-packet-20260529-rc-001",
        "acceptance-review-20260529-rc-001",
        "rollback-drill-review-20260529-rc-001",
    ]
    assert packet["reviewer_owner_fields"] == {
        "release_owner": "ppd-release-owner",
        "assembly_reviewer": "ppd-assembly-reviewer",
        "acceptance_reviewer": "ppd-acceptance-reviewer",
        "rollback_owner": "ppd-rollback-owner",
        "rollback_reviewer": "ppd-rollback-reviewer",
        "validation_reviewer": "ppd-validation-reviewer",
    }
    assert packet["rollback_drill_refs"] == [
        "rollback-drill:restore-prior-offline-fixture-packet",
        "rollback-drill:verify-no-release-state-mutation",
        "rollback-drill:review-owner-signoff-recorded",
    ]
    assert [item["disposition"] for item in packet["residual_blocker_dispositions"]] == [
        "not-applicable",
        "not-applicable",
        "resolved",
    ]


def test_required_offline_attestations_are_enforced() -> None:
    checklist = build_offline_release_candidate_checklist(
        _load_fixture("offline_release_candidate_assembly_packet.json"),
        _load_fixture("release_acceptance_review_packet.json"),
        _load_fixture("release_rollback_drill_outcome_review_packet.json"),
    )
    packet = checklist.to_dict()

    assert set(packet["attestations"]) == set(REQUIRED_ATTESTATIONS)
    assert packet["attestations"] == {
        "no_live_crawl": True,
        "no_devhub": True,
        "no_prompt": True,
        "no_guardrail_mutation": True,
        "no_release_mutation": True,
    }
    boundary_gate = packet["gates"][-1]
    assert boundary_gate["gate_id"] == "gate-07-offline-boundary-attestations"
    assert boundary_gate["attestations"] == packet["attestations"]
