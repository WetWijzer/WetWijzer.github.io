from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.agent_readiness.offline_release_readiness_packet import compile_offline_release_readiness_packet
from ppd.agent_readiness.prompt_refresh_release_handoff_packet import build_prompt_refresh_release_handoff_packet
from ppd.agent_readiness.release_rollback_readiness_packet import (
    REQUIRED_ATTESTATIONS,
    ReleaseRollbackReadinessPacketError,
    build_release_rollback_readiness_packet,
    validate_release_rollback_readiness_packet,
)

FIXTURES = Path(__file__).parent / "fixtures"
PROMPT_HANDOFF_INPUT = FIXTURES / "agent_readiness" / "prompt_refresh_release_handoff_packet.json"
MONITORING_SMOKE_TRANSCRIPT = FIXTURES / "prompt_refresh_monitoring_smoke_transcript_packet.json"
ROLLBACK_OUTCOME_REVIEW = FIXTURES / "release" / "rollback_drill_outcome_review_packet.json"
OFFLINE_READINESS_INPUT = FIXTURES / "offline_release_readiness" / "source_candidate_packet.json"


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_packets() -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    prompt_inputs = _load_json(PROMPT_HANDOFF_INPUT)
    prompt_handoff = build_prompt_refresh_release_handoff_packet(
        prompt_inputs["acceptance_packet"],  # type: ignore[arg-type]
        prompt_inputs["consumer_handoff_packet"],  # type: ignore[arg-type]
    )
    monitoring_smoke = _load_json(MONITORING_SMOKE_TRANSCRIPT)
    rollback_outcome = _load_json(ROLLBACK_OUTCOME_REVIEW)
    offline_readiness = compile_offline_release_readiness_packet(_load_json(OFFLINE_READINESS_INPUT))
    return prompt_handoff, monitoring_smoke, rollback_outcome, offline_readiness


def _packet() -> dict[str, object]:
    return build_release_rollback_readiness_packet(*_source_packets())


def _problem_text(packet: dict[str, object]) -> str:
    return "\n".join(validate_release_rollback_readiness_packet(packet).problems)


def test_builds_fixture_first_release_rollback_readiness_packet() -> None:
    packet = _packet()

    assert packet["packet_type"] == "ppd.release_rollback_readiness_packet.v1"
    assert packet["fixture_first"] is True
    assert packet["offline_only"] is True

    consumed_roles = {entry["packet_role"] for entry in packet["consumed_packets"]}  # type: ignore[index]
    assert consumed_roles == {
        "prompt_refresh_release_handoff_packet",
        "prompt_refresh_monitoring_smoke_transcript_packet",
        "release_rollback_drill_outcome_review_packet",
        "offline_release_readiness_packet",
    }

    prerequisites = packet["rollback_prerequisites"]
    assert prerequisites
    assert all(item["source_evidence_ids"] for item in prerequisites)  # type: ignore[index]
    assert {item["source_packet_role"] for item in prerequisites} >= {  # type: ignore[index]
        "prompt_refresh_release_handoff_packet",
        "prompt_refresh_monitoring_smoke_transcript_packet",
        "release_rollback_drill_outcome_review_packet",
        "offline_release_readiness_packet",
    }

    acknowledgements = packet["owner_acknowledgements"]
    assert acknowledgements
    assert all(item["owner"] for item in acknowledgements)  # type: ignore[index]
    assert all(item["acknowledgement_status"] == "required_before_live_release_or_rollback" for item in acknowledgements)  # type: ignore[index]

    boundaries = packet["blocked_live_action_boundaries"]
    assert {item["boundary_id"] for item in boundaries} == set(REQUIRED_ATTESTATIONS)  # type: ignore[index]
    assert all(item["blocked"] is True for item in boundaries)  # type: ignore[index]
    assert all(item["enabled"] is False for item in boundaries)  # type: ignore[index]

    assert ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"] in packet["offline_validation_commands"]  # type: ignore[operator]
    assert set(packet["attestations"]) == set(REQUIRED_ATTESTATIONS)  # type: ignore[arg-type]
    assert all(packet["attestations"][key] is True for key in REQUIRED_ATTESTATIONS)  # type: ignore[index]
    assert all(value is False for value in packet["execution_boundaries"].values())  # type: ignore[union-attr]

    result = validate_release_rollback_readiness_packet(packet)
    assert result.valid is True
    assert result.problems == ()


def test_release_rollback_readiness_rejects_missing_attestation_and_live_boundaries() -> None:
    packet = copy.deepcopy(_packet())
    packet["attestations"]["no-DevHub"] = False  # type: ignore[index]
    packet["execution_boundaries"]["devhub"] = True  # type: ignore[index]
    packet["blocked_live_action_boundaries"][0]["enabled"] = True  # type: ignore[index]
    packet["offline_validation_commands"] = [["python3", "ppd/crawler/live_public_scrape.py"]]

    joined = _problem_text(packet)

    assert "attestations.no-DevHub must be true" in joined
    assert "execution_boundaries.devhub must be false" in joined
    assert "blocked_live_action_boundaries[0].enabled must be false" in joined
    assert "live-action command token" in joined


def test_release_rollback_readiness_rejects_uncited_prerequisites_missing_owner_acknowledgements_and_missing_boundaries() -> None:
    packet = copy.deepcopy(_packet())
    packet["rollback_prerequisites"][0]["source_evidence_ids"] = []  # type: ignore[index]
    packet["owner_acknowledgements"][0]["owner"] = ""  # type: ignore[index]
    packet["owner_acknowledgements"][0]["acknowledgement_status"] = "acknowledged"  # type: ignore[index]
    packet["blocked_live_action_boundaries"] = [  # type: ignore[assignment]
        item for item in packet["blocked_live_action_boundaries"] if item["boundary_id"] != "no-live-monitoring"  # type: ignore[index]
    ]
    packet["offline_validation_commands"] = []

    joined = _problem_text(packet)

    assert "rollback_prerequisites[0] must include source_evidence_ids" in joined
    assert "owner_acknowledgements[0].owner is required" in joined
    assert "owner_acknowledgements[0].acknowledgement_status must be required_before_live_release_or_rollback" in joined
    assert "blocked_live_action_boundaries must include no-live-monitoring" in joined
    assert "offline_validation_commands must be a non-empty list of command arrays" in joined


def test_release_rollback_readiness_rejects_private_authenticated_runtime_and_execution_claims() -> None:
    packet = copy.deepcopy(_packet())
    packet["notes"] = [
        "Authenticated facts from the user's account were used.",
        "https://user:pass@www.portland.gov/ppd/private",
        "https://www.portland.gov/ppd?token=secret",
        "/tmp/private/session/crawl.json",
        "The live release executed and monitoring ran after publication.",
        "DevHub was invoked and the LLM called a processor.",
        "The live crawler completed.",
    ]

    joined = _problem_text(packet)

    assert "private, authenticated, runtime, raw, or downloaded artifact reference" in joined
    assert "authenticated URL credentials" in joined
    assert "authenticated URL query parameters" in joined
    assert "live release, monitoring, DevHub, LLM, crawler, or processor execution claim" in joined


def test_release_rollback_readiness_rejects_legal_guarantees_and_active_mutation_flags() -> None:
    packet = copy.deepcopy(_packet())
    packet["legal_summary"] = "Permit approval is guaranteed and the permit will be issued."
    for field in (
        "active_prompt_mutation",
        "guardrail_mutation_enabled",
        "monitoring_mutation_allowed",
        "active_release_state_mutation",
        "active_source_mutation",
        "schedule_mutation_enabled",
        "active_agent_state_mutation",
    ):
        packet[field] = True

    joined = _problem_text(packet)

    assert "legal or permitting outcome guarantee" in joined
    assert joined.count("active mutation flag is not allowed") >= 7


def test_release_rollback_readiness_rejects_invalid_source_packet() -> None:
    prompt_handoff, monitoring_smoke, rollback_outcome, offline_readiness = _source_packets()
    monitoring_smoke = copy.deepcopy(monitoring_smoke)
    monitoring_smoke["mode"] = "online"

    with pytest.raises(ReleaseRollbackReadinessPacketError, match="monitoring smoke transcript"):
        build_release_rollback_readiness_packet(
            prompt_handoff,
            monitoring_smoke,
            rollback_outcome,
            offline_readiness,
        )
