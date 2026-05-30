from __future__ import annotations

import copy

from ppd.offline_release_candidate_validation_checklist import (
    PACKET_TYPE,
    validate_offline_release_candidate_validation_checklist,
)


def _valid_packet() -> dict[str, object]:
    return {
        "packet_type": PACKET_TYPE,
        "packet_id": "offline-release-candidate-checklist-fixture",
        "fixture_only": True,
        "metadata_only": True,
        "consumed_packets": [
            {
                "packet_id": "readiness-packet-1",
                "packet_role": "offline_release_readiness_packet",
                "source_evidence_ids": ["ev-readiness"],
            }
        ],
        "reviewer_owners": [
            {"owner_id": "release-reviewer", "role": "ppd_release_reviewer"}
        ],
        "go_no_go_gates": [
            {
                "gate_id": "gate-primary",
                "decision": "no_go",
                "summary": "No-go until residual blockers remain dispositioned in the offline packet.",
                "source_evidence_ids": ["ev-gate"],
                "consumed_packet_ids": ["readiness-packet-1"],
                "reviewer_owner": "release-reviewer",
            }
        ],
        "residual_blockers": [
            {
                "blocker_id": "blocker-open-review",
                "summary": "Operator review remains required.",
                "source_evidence_ids": ["ev-blocker"],
            }
        ],
        "residual_blocker_dispositions": [
            {
                "blocker_id": "blocker-open-review",
                "disposition": "no_go_blocker",
                "source_evidence_ids": ["ev-disposition"],
                "consumed_packet_ids": ["readiness-packet-1"],
                "reviewer_owner": "release-reviewer",
            }
        ],
        "rollback_drill_references": [
            {
                "rollback_drill_id": "rollback-discard-offline-candidate",
                "source_evidence_ids": ["ev-rollback"],
                "consumed_packet_ids": ["readiness-packet-1"],
                "reviewer_owner": "release-reviewer",
            }
        ],
        "offline_validation_commands": [
            {
                "command_id": "self-test",
                "command": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
                "source_evidence_ids": ["ev-command"],
                "consumed_packet_ids": ["readiness-packet-1"],
                "reviewer_owner": "release-reviewer",
            }
        ],
    }


def _problems(packet: dict[str, object]) -> str:
    result = validate_offline_release_candidate_validation_checklist(packet)
    return "; ".join(result.problems)


def test_accepts_cited_fixture_only_checklist_packet() -> None:
    result = validate_offline_release_candidate_validation_checklist(_valid_packet())

    assert result.valid, result.problems


def test_rejects_uncited_gate_and_missing_consumed_packet_reference() -> None:
    packet = _valid_packet()
    gate = copy.deepcopy(packet["go_no_go_gates"])[0]
    gate.pop("source_evidence_ids")
    gate.pop("consumed_packet_ids")
    packet["go_no_go_gates"] = [gate]

    problems = _problems(packet)

    assert "go_no_go_gates[0] lacks source_evidence_ids" in problems
    assert "go_no_go_gates[0] lacks consumed_packet_ids" in problems


def test_rejects_missing_blocker_disposition_rollback_owner_and_command() -> None:
    packet = _valid_packet()
    packet["residual_blocker_dispositions"] = []
    packet["rollback_drill_references"] = []
    packet["reviewer_owners"] = []
    packet["offline_validation_commands"] = []

    problems = _problems(packet)

    assert "residual_blocker_dispositions must cover residual_blockers" in problems
    assert "rollback_drill_references must include at least one rollback drill reference" in problems
    assert "reviewer_owners must include at least one reviewer owner" in problems
    assert "offline_validation_commands must include at least one offline validation command" in problems


def test_rejects_raw_private_live_guarantee_and_mutation_content() -> None:
    packet = _valid_packet()
    packet["raw_body_ref"] = "raw-download/body.html"
    packet["session_state"] = "auth-state.json"
    packet["live_processor_execution"] = True
    packet["active_requirement_mutation"] = True
    packet["notes"] = "Live DevHub execution completed and permit will be approved."

    problems = _problems(packet)

    assert "raw_body_ref uses a forbidden raw" in problems
    assert "session_state uses a forbidden raw" in problems
    assert "live_processor_execution claims live crawler" in problems
    assert "active_requirement_mutation enables active source" in problems
    assert "claims live crawler, processor, DevHub, or LLM execution" in problems
    assert "makes a legal or permitting outcome guarantee" in problems


def test_rejects_live_validation_commands() -> None:
    packet = _valid_packet()
    command = copy.deepcopy(packet["offline_validation_commands"])[0]
    command["command"] = ["python3", "ppd/crawler/live_public_scrape.py"]
    packet["offline_validation_commands"] = [command]

    problems = _problems(packet)

    assert "offline_validation_commands[0].command must be offline" in problems
