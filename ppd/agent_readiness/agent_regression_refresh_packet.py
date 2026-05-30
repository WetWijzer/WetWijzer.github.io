"""Fixture-first PP&D agent regression refresh packet builder.

The packet assembled here is intentionally offline-only.  It consumes already
captured candidate, acceptance, and smoke transcript fixtures and turns them
into reviewer-ready regression scenarios.  It must not call live LLMs, DevHub,
prompt stores, guardrail services, or mutate agent state.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

SOURCE_PACKET_KEYS = (
    "process_and_guardrail_refresh_candidate_packet",
    "agent_freshness_regression_acceptance_packet",
    "agent_consumer_post_release_smoke_transcript_packet",
)

REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub",
    "no_prompt",
    "no_guardrail",
    "no_agent_state_mutation",
)

REQUIRED_SCENARIO_FIELDS = (
    "scenario_id",
    "source_packet_ids",
    "user_scenario",
    "cited_offline_evidence",
    "expected_missing_fact_prompts",
    "refusal_explanation",
    "reversible_draft_preview_boundary",
    "blocked_consequential_action_message",
    "reviewer_owner",
)


def load_source_packets(path: str | Path) -> Dict[str, Any]:
    """Load source packets from a local fixture file."""

    with Path(path).open("r", encoding="utf-8") as fixture_file:
        data = json.load(fixture_file)
    if not isinstance(data, dict):
        raise ValueError("agent regression refresh source fixture must be a JSON object")
    return data


def build_agent_regression_refresh_packet(source_packets: Mapping[str, Any]) -> Dict[str, Any]:
    """Build a deterministic regression refresh packet from offline fixtures."""

    missing = [key for key in SOURCE_PACKET_KEYS if key not in source_packets]
    if missing:
        raise ValueError("missing source packet(s): " + ", ".join(missing))

    process_packet = _as_mapping(source_packets["process_and_guardrail_refresh_candidate_packet"])
    acceptance_packet = _as_mapping(source_packets["agent_freshness_regression_acceptance_packet"])
    smoke_packet = _as_mapping(source_packets["agent_consumer_post_release_smoke_transcript_packet"])

    packet = {
        "packet_id": "agent-regression-refresh-20260529-fixture-first",
        "packet_type": "fixture_first_agent_regression_refresh_packet",
        "source_packet_ids": [
            _packet_id(process_packet, "process-and-guardrail-refresh-candidate"),
            _packet_id(acceptance_packet, "agent-freshness-regression-acceptance"),
            _packet_id(smoke_packet, "agent-consumer-post-release-smoke-transcript"),
        ],
        "offline_user_scenarios": _build_scenarios(process_packet, acceptance_packet, smoke_packet),
        "reviewer_owner_fields": {
            "primary_owner": _text(
                acceptance_packet.get("reviewer_owner")
                or acceptance_packet.get("owner")
                or "PP&D agent readiness reviewer"
            ),
            "secondary_owner": _text(
                process_packet.get("reviewer_owner")
                or process_packet.get("owner")
                or "PP&D process and guardrail reviewer"
            ),
            "release_smoke_owner": _text(
                smoke_packet.get("reviewer_owner")
                or smoke_packet.get("owner")
                or "PP&D consumer smoke reviewer"
            ),
        },
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }
    validate_agent_regression_refresh_packet(packet)
    return packet


def validate_agent_regression_refresh_packet(packet: Mapping[str, Any]) -> None:
    """Validate the externally asserted acceptance shape."""

    scenarios = packet.get("offline_user_scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("packet must contain at least one offline user scenario")

    source_packet_ids = packet.get("source_packet_ids")
    if not isinstance(source_packet_ids, list) or len(source_packet_ids) != len(SOURCE_PACKET_KEYS):
        raise ValueError("packet must cite the three consumed source packet ids")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        raise ValueError("packet must include attestations")
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            raise ValueError(f"attestation {key} must be true")

    for scenario in scenarios:
        if not isinstance(scenario, Mapping):
            raise ValueError("offline user scenario entries must be objects")
        for field in REQUIRED_SCENARIO_FIELDS:
            value = scenario.get(field)
            if value in (None, "", []):
                raise ValueError(f"scenario {scenario.get('scenario_id', '')} missing {field}")
        citations = scenario.get("cited_offline_evidence")
        if not isinstance(citations, list) or not citations:
            raise ValueError("scenario must cite offline evidence")
        for citation in citations:
            if not isinstance(citation, Mapping):
                raise ValueError("offline evidence citations must be objects")
            if not citation.get("source_packet_id") or not citation.get("locator"):
                raise ValueError("offline evidence citations require source_packet_id and locator")


def _build_scenarios(
    process_packet: Mapping[str, Any],
    acceptance_packet: Mapping[str, Any],
    smoke_packet: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    smoke_scenarios = smoke_packet.get("offline_user_scenarios") or smoke_packet.get("scenarios")
    if not isinstance(smoke_scenarios, list) or not smoke_scenarios:
        smoke_scenarios = [
            {
                "scenario_id": "consumer-smoke-default",
                "user_scenario": "Consumer asks the released agent to summarize a Portland permitting status from fixture evidence.",
                "missing_facts": ["current permit status", "source citation date"],
            }
        ]

    scenarios: List[Dict[str, Any]] = []
    for index, raw_scenario in enumerate(smoke_scenarios, start=1):
        scenario = _as_mapping(raw_scenario)
        scenario_id = _text(scenario.get("scenario_id") or scenario.get("id") or f"offline-agent-regression-{index:02d}")
        missing_facts = _string_list(
            scenario.get("expected_missing_fact_prompts")
            or scenario.get("missing_facts")
            or acceptance_packet.get("expected_missing_fact_prompts")
            or acceptance_packet.get("missing_facts")
        )
        if not missing_facts:
            missing_facts = [
                "Ask for the missing effective date before answering.",
                "Ask for the cited ordinance or permit identifier before drafting a conclusion.",
            ]

        citations = _citations(process_packet, acceptance_packet, smoke_packet, scenario_id)
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "source_packet_ids": [citation["source_packet_id"] for citation in citations],
                "user_scenario": _text(
                    scenario.get("user_scenario")
                    or scenario.get("transcript_summary")
                    or scenario.get("prompt")
                    or "Offline consumer regression scenario built from the smoke transcript fixture."
                ),
                "cited_offline_evidence": citations,
                "expected_missing_fact_prompts": missing_facts,
                "refusal_explanation": _text(
                    scenario.get("refusal_explanation")
                    or acceptance_packet.get("refusal_explanation")
                    or "Refuse to provide a final legal, permitting, payment, filing, or enforcement conclusion when the fixture lacks the required cited facts; explain which fact is missing and offer a reversible draft preview only."
                ),
                "reversible_draft_preview_boundary": _text(
                    scenario.get("reversible_draft_preview_boundary")
                    or process_packet.get("reversible_draft_preview_boundary")
                    or "Draft previews may be edited, discarded, or re-run from the fixture; they must not file, submit, notify, purchase, schedule, or persist agent state."
                ),
                "blocked_consequential_action_message": _text(
                    scenario.get("blocked_consequential_action_message")
                    or process_packet.get("blocked_consequential_action_message")
                    or "Blocked: consequential actions require an authorized reviewer and live-system handoff outside this offline regression packet."
                ),
                "reviewer_owner": _text(
                    scenario.get("reviewer_owner")
                    or acceptance_packet.get("reviewer_owner")
                    or "PP&D agent readiness reviewer"
                ),
            }
        )
    return scenarios


def _citations(
    process_packet: Mapping[str, Any],
    acceptance_packet: Mapping[str, Any],
    smoke_packet: Mapping[str, Any],
    scenario_id: str,
) -> List[Dict[str, str]]:
    packets = (
        (process_packet, "process_and_guardrail_refresh_candidate_packet", "process and guardrail refresh candidate"),
        (acceptance_packet, "agent_freshness_regression_acceptance_packet", "agent freshness regression acceptance"),
        (smoke_packet, "agent_consumer_post_release_smoke_transcript_packet", "agent consumer post-release smoke transcript"),
    )
    citations: List[Dict[str, str]] = []
    for packet, locator_root, title in packets:
        citations.append(
            {
                "source_packet_id": _packet_id(packet, title.replace(" ", "-")),
                "title": _text(packet.get("title") or title),
                "locator": _text(packet.get("citation_locator") or f"{locator_root}::{scenario_id}"),
            }
        )
    return citations


def _packet_id(packet: Mapping[str, Any], fallback: str) -> str:
    return _text(packet.get("packet_id") or packet.get("id") or fallback)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> List[str]:
    if isinstance(value, str):
        return [_text(value)] if value.strip() else []
    if not isinstance(value, Iterable) or isinstance(value, Mapping):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""
