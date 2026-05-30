"""Fixture-first release candidate evidence bundle v1.

The builder intentionally consumes committed, redacted evidence packets and does not
crawl public sources, open DevHub, read private artifacts, or promote anything.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

REQUIRED_INPUT_KEYS = (
    "readiness_gap_report_v1",
    "public_source_refresh_evidence_intake_packet_v1",
    "devhub_observation_evidence_intake_packet_v1",
    "action_journal_replay_findings",
    "guarded_agent_response_acceptance_examples",
)

ATTESTATIONS = {
    "no_live_crawl": True,
    "no_devhub_session": True,
    "no_private_artifact": True,
    "no_official_action": True,
    "no_active_promotion": True,
}


def build_release_candidate_evidence_bundle_v1(inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic release-candidate evidence bundle from fixtures."""
    missing = [key for key in REQUIRED_INPUT_KEYS if key not in inputs]
    if missing:
        raise ValueError(f"missing release candidate input packet(s): {', '.join(missing)}")

    readiness = deepcopy(inputs["readiness_gap_report_v1"])
    public_refresh = deepcopy(inputs["public_source_refresh_evidence_intake_packet_v1"])
    devhub = deepcopy(inputs["devhub_observation_evidence_intake_packet_v1"])
    replay = deepcopy(inputs["action_journal_replay_findings"])
    examples = deepcopy(inputs["guarded_agent_response_acceptance_examples"])

    source_packets = [
        _packet_summary("readiness_gap_report_v1", readiness),
        _packet_summary("public_source_refresh_evidence_intake_packet_v1", public_refresh),
        _packet_summary("devhub_observation_evidence_intake_packet_v1", devhub),
        _packet_summary("action_journal_replay_findings", replay),
        _packet_summary("guarded_agent_response_acceptance_examples", examples),
    ]

    evidence_rows = []
    evidence_rows.extend(_readiness_rows(readiness))
    evidence_rows.extend(_public_refresh_rows(public_refresh))
    evidence_rows.extend(_devhub_rows(devhub))
    evidence_rows.extend(_replay_rows(replay))
    evidence_rows.extend(_acceptance_rows(examples))
    evidence_rows = sorted(evidence_rows, key=lambda row: row["row_id"])

    unresolved_blockers = _unresolved_blockers(readiness, evidence_rows)
    rollback_checkpoints = _rollback_checkpoints(replay, unresolved_blockers)
    validation_command_inventory = _validation_command_inventory(inputs)
    reviewer_owner_fields = _reviewer_owner_fields(inputs)

    return {
        "bundle_id": "ppd-release-candidate-evidence-bundle-v1",
        "bundle_version": "1.0",
        "generation_mode": "fixture_first",
        "source_packets": source_packets,
        "release_candidate_evidence_rows": evidence_rows,
        "unresolved_blocker_summaries": unresolved_blockers,
        "rollback_checkpoints": rollback_checkpoints,
        "validation_command_inventory": validation_command_inventory,
        "reviewer_owner_fields": reviewer_owner_fields,
        "attestations": deepcopy(ATTESTATIONS),
    }


def validate_release_candidate_evidence_bundle_v1(bundle: Mapping[str, Any]) -> None:
    required = {
        "bundle_id",
        "bundle_version",
        "generation_mode",
        "source_packets",
        "release_candidate_evidence_rows",
        "unresolved_blocker_summaries",
        "rollback_checkpoints",
        "validation_command_inventory",
        "reviewer_owner_fields",
        "attestations",
    }
    missing = sorted(required.difference(bundle))
    if missing:
        raise ValueError(f"missing bundle field(s): {', '.join(missing)}")

    attestations = bundle["attestations"]
    for key, expected in ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            raise ValueError(f"attestation {key} must be {expected!r}")

    rows = bundle["release_candidate_evidence_rows"]
    if not rows:
        raise ValueError("release candidate evidence rows must not be empty")
    for row in rows:
        if not row.get("citations"):
            raise ValueError(f"evidence row {row.get('row_id', '')} has no citations")
        if not row.get("reviewer_owner"):
            raise ValueError(f"evidence row {row.get('row_id', '')} has no reviewer owner")


def _packet_summary(packet_name: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "packet_name": packet_name,
        "packet_id": packet.get("packet_id", packet_name),
        "fixture_only": packet.get("fixture_only", True),
        "citations": list(packet.get("citations", [])),
    }


def _readiness_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for gap in packet.get("gaps", []):
        rows.append(
            _row(
                "readiness",
                gap["gap_id"],
                "readiness_gap",
                gap["summary"],
                gap.get("status", "unknown"),
                gap.get("severity", "medium"),
                gap.get("citations", packet.get("citations", [])),
                gap.get("reviewer_owner", packet.get("default_reviewer_owner", "ppd-release-reviewer")),
                gap.get("rollback_checkpoint", "hold release candidate until gap is resolved"),
            )
        )
    return rows


def _public_refresh_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for source in packet.get("sources", []):
        rows.append(
            _row(
                "public-source-refresh",
                source["source_id"],
                "public_source_refresh",
                source["summary"],
                source.get("freshness_status", "unknown"),
                source.get("severity", "medium"),
                source.get("citations", packet.get("citations", [])),
                source.get("reviewer_owner", packet.get("default_reviewer_owner", "ppd-source-reviewer")),
                source.get("rollback_checkpoint", "discard candidate if source freshness cannot be reproduced from fixture evidence"),
            )
        )
    return rows


def _devhub_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for observation in packet.get("observations", []):
        rows.append(
            _row(
                "devhub-observation",
                observation["observation_id"],
                "devhub_observation",
                observation["summary"],
                observation.get("status", "observed_fixture_only"),
                observation.get("severity", "medium"),
                observation.get("citations", packet.get("citations", [])),
                observation.get("reviewer_owner", packet.get("default_reviewer_owner", "ppd-devhub-reviewer")),
                observation.get("rollback_checkpoint", "remove DevHub-derived row if redaction or attendance boundary is disputed"),
            )
        )
    return rows


def _replay_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for finding in packet.get("findings", []):
        rows.append(
            _row(
                "action-journal-replay",
                finding["finding_id"],
                "action_journal_replay",
                finding["summary"],
                finding.get("status", "unknown"),
                finding.get("severity", "medium"),
                finding.get("citations", packet.get("citations", [])),
                finding.get("reviewer_owner", packet.get("default_reviewer_owner", "ppd-journal-reviewer")),
                finding.get("rollback_checkpoint", "replay from last accepted fixture event before any candidate promotion"),
            )
        )
    return rows


def _acceptance_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for example in packet.get("examples", []):
        rows.append(
            _row(
                "guarded-agent-response",
                example["example_id"],
                "guarded_agent_response_acceptance",
                example["summary"],
                example.get("status", "unknown"),
                example.get("severity", "medium"),
                example.get("citations", packet.get("citations", [])),
                example.get("reviewer_owner", packet.get("default_reviewer_owner", "ppd-agent-reviewer")),
                example.get("rollback_checkpoint", "reject candidate if guarded response acceptance cannot be reproduced"),
            )
        )
    return rows


def _row(
    prefix: str,
    item_id: str,
    evidence_type: str,
    summary: str,
    status: str,
    severity: str,
    citations: list[str],
    reviewer_owner: str,
    rollback_checkpoint: str,
) -> dict[str, Any]:
    return {
        "row_id": f"rc-v1:{prefix}:{item_id}",
        "evidence_type": evidence_type,
        "summary": summary,
        "status": status,
        "severity": severity,
        "citations": list(citations),
        "reviewer_owner": reviewer_owner,
        "rollback_checkpoint": rollback_checkpoint,
    }


def _unresolved_blockers(readiness: Mapping[str, Any], rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    blockers = []
    blocking_statuses = {"open", "blocked", "unresolved", "needs_review"}
    for row in rows:
        if row["status"] in blocking_statuses or row["severity"] == "blocker":
            blockers.append(
                {
                    "blocker_id": row["row_id"].replace("rc-v1:", "blocker:"),
                    "summary": row["summary"],
                    "severity": row["severity"],
                    "source_row_id": row["row_id"],
                    "reviewer_owner": row["reviewer_owner"],
                    "citations": list(row["citations"]),
                }
            )
    for blocker in readiness.get("unresolved_blockers", []):
        blockers.append(
            {
                "blocker_id": blocker["blocker_id"],
                "summary": blocker["summary"],
                "severity": blocker.get("severity", "blocker"),
                "source_row_id": blocker.get("source_row_id"),
                "reviewer_owner": blocker.get("reviewer_owner", readiness.get("default_reviewer_owner", "ppd-release-reviewer")),
                "citations": list(blocker.get("citations", readiness.get("citations", []))),
            }
        )
    return sorted(blockers, key=lambda item: item["blocker_id"])


def _rollback_checkpoints(replay: Mapping[str, Any], blockers: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    checkpoints = list(replay.get("rollback_checkpoints", []))
    checkpoints.append(
        {
            "checkpoint_id": "rc-v1-hold-on-unresolved-blockers",
            "trigger": "unresolved_blocker_count > 0",
            "action": "do not promote release candidate; keep fixture bundle as evidence only",
            "citations": [blocker["blocker_id"] for blocker in blockers],
        }
    )
    return sorted(checkpoints, key=lambda item: item["checkpoint_id"])


def _validation_command_inventory(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    inventory = [
        {
            "command_id": "ppd-daemon-self-test",
            "argv": ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
            "purpose": "Run PP&D daemon self-test without live crawl or authenticated DevHub automation.",
        },
        {
            "command_id": "ppd-release-candidate-evidence-tests",
            "argv": ["python3", "-m", "unittest", "ppd.tests.test_release_candidate_evidence_v1"],
            "purpose": "Validate deterministic fixture-to-bundle release candidate evidence behavior.",
        },
    ]
    for command in inputs.get("validation_commands", []):
        inventory.append(command)
    return sorted(inventory, key=lambda item: item["command_id"])


def _reviewer_owner_fields(inputs: Mapping[str, Any]) -> dict[str, Any]:
    owners = {}
    for packet_name in REQUIRED_INPUT_KEYS:
        packet = inputs[packet_name]
        owners[packet_name] = packet.get("default_reviewer_owner", "ppd-release-reviewer")
    return {
        "primary_reviewer_owner": inputs.get("primary_reviewer_owner", "ppd-release-reviewer"),
        "packet_reviewer_owners": owners,
        "requires_human_review_before_promotion": True,
    }
