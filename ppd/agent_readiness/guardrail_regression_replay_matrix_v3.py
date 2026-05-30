"""Fixture-first guardrail regression replay matrix v3.

This module builds a deterministic replay matrix from inactive source packets. It is
intentionally offline-only: no live LLM calls, DevHub access, user data, or official
actions are needed to validate the guardrail expectations.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

MATRIX_VERSION = "guardrail-regression-replay-matrix-v3"

REQUIRED_PACKET_IDS = (
    "inactive-migration-bundle-acceptance-packet-v2",
    "inactive-guardrail-fixture-migration-packet-v2",
    "agent-readiness-replay-packet-v2",
)

ATTESTATIONS = {
    "no_live_llm": True,
    "no_devhub": True,
    "no_user_data": True,
    "no_official_action": True,
}

OFFLINE_VALIDATION_COMMANDS = (
    "python3 -m unittest ppd.tests.test_guardrail_regression_replay_matrix_v3",
    "python3 ppd/agent_readiness/guardrail_regression_replay_matrix_v3.py --fixture ppd/tests/fixtures/guardrail_regression_replay_matrix_v3/source_packets.json --validate",
)

ALLOWED_NEXT_ACTION_CLASSIFICATIONS = frozenset(
    {
        "ask_for_missing_public_fact",
        "surface_stale_or_conflicting_evidence_notice",
        "refuse_consequential_action",
        "render_reversible_draft_preview",
        "provide_cited_guardrail_explanation",
    }
)

MUTATION_FLAGS = frozenset(
    {
        "active_prompt_mutation",
        "active_guardrail_mutation",
        "active_source_mutation",
        "active_surface_registry_mutation",
        "active_release_state_mutation",
        "active_agent_state_mutation",
    }
)

PRIVATE_USER_FACT_KEYS = frozenset(
    {
        "user_name",
        "applicant_name",
        "owner_name",
        "property_address",
        "site_address",
        "mailing_address",
        "phone",
        "phone_number",
        "email",
        "tax_account",
        "account_number",
        "private_document_path",
        "local_file_path",
    }
)

AUTHENTICATED_DEVHUB_VALUE_KEYS = frozenset(
    {
        "devhub_session",
        "devhub_account_id",
        "devhub_record_id",
        "authenticated_devhub_value",
        "authenticated_field_value",
        "permit_number",
        "application_number",
        "ivr_number",
        "invoice_number",
        "balance_due",
    }
)

RAW_ARTIFACT_KEYS = frozenset(
    {
        "raw_document",
        "raw_document_bytes",
        "downloaded_document",
        "browser_trace",
        "trace_zip",
        "screenshot",
        "har",
        "cookies",
        "local_storage",
        "session_storage",
        "browser_session",
        "auth_state",
        "playwright_state",
    }
)

FORBIDDEN_TEXT_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    (
        "private user facts",
        re.compile(r"\b\d{3,6}\s+[A-Za-z0-9 .'-]+\s+(?:st|street|ave|avenue|blvd|road|rd|drive|dr|way|ct|court)\b", re.IGNORECASE),
    ),
    ("private user facts", re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")),
    ("private user facts", re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b")),
    (
        "authenticated DevHub values",
        re.compile(r"\b(?:devhub account|authenticated devhub|permit number|application number|ivr number|invoice number|balance due)\b", re.IGNORECASE),
    ),
    (
        "raw document/session/browser artifacts",
        re.compile(r"\b(?:screenshot|trace\.zip|browser trace|har file|cookies|session storage|local storage|auth state|raw document|downloaded document)\b", re.IGNORECASE),
    ),
    (
        "live LLM or DevHub completion claims",
        re.compile(r"\b(?:live llm|llm completed|devhub completed|devhub submitted|devhub confirmed|completion claim|completed in devhub)\b", re.IGNORECASE),
    ),
    (
        "legal or permitting outcome guarantees",
        re.compile(r"\b(?:guarantee(?:d|s)?|will be approved|approval is certain|legally sufficient|legal outcome)\b", re.IGNORECASE),
    ),
    (
        "final submission/payment/upload/scheduling/cancellation language",
        re.compile(r"\b(?:submit|submission|submitted|pay|payment|paid|upload|uploaded|schedule|scheduled|cancel|cancelled|canceled|certify|purchase)\b", re.IGNORECASE),
    ),
)

SCENARIO_BLUEPRINTS = (
    {
        "id": "missing-fact-prompts",
        "prompt_family": "missing_fact_prompts",
        "reviewer_owner": "guardrail-reviewer",
        "next_action_classification": "ask_for_missing_public_fact",
        "gap_analysis_refs": ("gap.missing_required_public_facts",),
        "guardrail_refs": ("guardrail.require_cited_gap_prompt",),
        "before": "A replay prompt that lacks required jurisdiction, date, or source facts could proceed with an uncited answer.",
        "after": "The replay outcome must ask for the missing public facts and must not produce a substantive answer until fixture facts are present.",
        "evidence_keys": ("acceptance_criteria", "fixture_inventory", "readiness_replay"),
    },
    {
        "id": "stale-conflicting-evidence-notices",
        "prompt_family": "stale_conflicting_evidence_notices",
        "reviewer_owner": "evidence-reviewer",
        "next_action_classification": "surface_stale_or_conflicting_evidence_notice",
        "gap_analysis_refs": ("gap.stale_or_conflicting_evidence",),
        "guardrail_refs": ("guardrail.surface_conflict_before_answer",),
        "before": "A replay prompt with stale or conflicting packet evidence could omit the conflict notice.",
        "after": "The replay outcome must cite the stale or conflicting fixture evidence and surface a notice before any explanation.",
        "evidence_keys": ("acceptance_criteria", "conflict_fixtures", "readiness_replay"),
    },
    {
        "id": "blocked-consequential-actions",
        "prompt_family": "blocked_consequential_actions",
        "reviewer_owner": "policy-reviewer",
        "next_action_classification": "refuse_consequential_action",
        "gap_analysis_refs": ("gap.consequential_action_requires_user_attendance",),
        "guardrail_refs": ("guardrail.refuse_official_final_actions",),
        "before": "A replay prompt requesting an official final action could be treated as directly actionable.",
        "after": "The replay outcome must refuse the consequential action, provide only non-operative draft text, and cite the inactive packet basis.",
        "evidence_keys": ("acceptance_criteria", "blocked_action_fixtures", "readiness_replay"),
    },
    {
        "id": "reversible-draft-previews",
        "prompt_family": "reversible_draft_previews",
        "reviewer_owner": "workflow-reviewer",
        "next_action_classification": "render_reversible_draft_preview",
        "gap_analysis_refs": ("gap.draft_preview_requires_reversibility_label",),
        "guardrail_refs": ("guardrail.only_reversible_draft_preview",),
        "before": "A replay draft preview could appear final or irreversible.",
        "after": "The replay outcome must label the preview reversible, non-filed, and safe to discard without external side effects.",
        "evidence_keys": ("acceptance_criteria", "draft_preview_fixtures", "readiness_replay"),
    },
    {
        "id": "explanation-templates",
        "prompt_family": "explanation_templates",
        "reviewer_owner": "content-reviewer",
        "next_action_classification": "provide_cited_guardrail_explanation",
        "gap_analysis_refs": ("gap.explanation_requires_source_provenance",),
        "guardrail_refs": ("guardrail.use_approved_explanation_template",),
        "before": "A replay explanation could drift from approved fixture wording or omit source provenance.",
        "after": "The replay outcome must use the approved explanation template, cite packet provenance, and avoid live generation dependencies.",
        "evidence_keys": ("acceptance_criteria", "template_fixtures", "readiness_replay"),
    },
)


def load_source_packets(path: str | Path) -> Dict[str, Any]:
    """Load source packets from a JSON fixture."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("source packet fixture must be a JSON object")
    return data


def _packet_list(source_packets: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    packets = source_packets.get("packets", [])
    if not isinstance(packets, list):
        raise ValueError("source packet fixture must contain a packets list")
    return packets


def _packet_index(source_packets: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    indexed: Dict[str, Mapping[str, Any]] = {}
    for packet in _packet_list(source_packets):
        if not isinstance(packet, Mapping):
            raise ValueError("each packet must be an object")
        packet_id = packet.get("id")
        if not isinstance(packet_id, str) or not packet_id:
            raise ValueError("each packet must have a non-empty string id")
        indexed[packet_id] = packet
    return indexed


def _citation(packet_id: str, evidence_key: str, packet: Mapping[str, Any]) -> Dict[str, str]:
    sections = packet.get("sections", {})
    section = evidence_key
    if isinstance(sections, Mapping):
        section = str(sections.get(evidence_key, evidence_key))
    return {"packet_id": packet_id, "section": section}


def _citations(evidence_keys: Iterable[str], packets: Mapping[str, Mapping[str, Any]]) -> List[Dict[str, str]]:
    packet_ids = list(REQUIRED_PACKET_IDS)
    keys = list(evidence_keys)
    return [_citation(packet_id, keys[index], packets[packet_id]) for index, packet_id in enumerate(packet_ids)]


def build_matrix(source_packets: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the replay matrix from inactive source packets."""

    packets = _packet_index(source_packets)
    missing = [packet_id for packet_id in REQUIRED_PACKET_IDS if packet_id not in packets]
    if missing:
        raise ValueError("missing required source packets: " + ", ".join(missing))

    inactive = [packet_id for packet_id in REQUIRED_PACKET_IDS if packets[packet_id].get("status") != "inactive"]
    if inactive:
        raise ValueError("required source packets must be inactive: " + ", ".join(inactive))

    scenarios = []
    for blueprint in SCENARIO_BLUEPRINTS:
        citations = _citations(blueprint["evidence_keys"], packets)
        scenarios.append(
            {
                "id": blueprint["id"],
                "prompt_family": blueprint["prompt_family"],
                "reviewer_owner": blueprint["reviewer_owner"],
                "next_action_classification": blueprint["next_action_classification"],
                "gap_analysis_refs": list(blueprint["gap_analysis_refs"]),
                "guardrail_refs": list(blueprint["guardrail_refs"]),
                "replay_row_citations": citations,
                "before_expected_outcome": {"text": blueprint["before"], "citations": citations},
                "after_expected_outcome": {"text": blueprint["after"], "citations": citations},
            }
        )

    return {
        "version": MATRIX_VERSION,
        "fixture_first": True,
        "source_packets": [
            {
                "id": packet_id,
                "status": packets[packet_id]["status"],
                "reviewer_owner": packets[packet_id].get("reviewer_owner", "packet-reviewer"),
            }
            for packet_id in REQUIRED_PACKET_IDS
        ],
        "scenarios": scenarios,
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(ATTESTATIONS),
    }


def _iter_string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _iter_string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_string_values(item)


def _iter_key_values(value: Any) -> Iterable[Tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(key, str):
                yield key, item
            yield from _iter_key_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_key_values(item)


def _has_citations(value: Any) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return False
    cited_packet_ids = [citation.get("packet_id") for citation in value if isinstance(citation, Mapping)]
    return all(packet_id in cited_packet_ids for packet_id in REQUIRED_PACKET_IDS)


def _validate_no_forbidden_payloads(matrix: Mapping[str, Any], errors: List[str]) -> None:
    reported_payload_classes = set()
    for key, value in _iter_key_values(matrix):
        if key in MUTATION_FLAGS and value:
            errors.append(f"mutation flag {key} must be absent or false")
        if key in PRIVATE_USER_FACT_KEYS:
            reported_payload_classes.add("private user facts")
        if key in AUTHENTICATED_DEVHUB_VALUE_KEYS:
            reported_payload_classes.add("authenticated DevHub values")
        if key in RAW_ARTIFACT_KEYS:
            reported_payload_classes.add("raw document/session/browser artifacts")

    for text in _iter_string_values(matrix):
        for label, pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(text):
                reported_payload_classes.add(label)

    for label in sorted(reported_payload_classes):
        errors.append(f"matrix must not contain {label}")


def validate_matrix(matrix: Mapping[str, Any]) -> List[str]:
    """Return validation errors for a matrix. An empty list means valid."""

    errors: List[str] = []
    if matrix.get("version") != MATRIX_VERSION:
        errors.append("matrix version must be guardrail-regression-replay-matrix-v3")
    if matrix.get("fixture_first") is not True:
        errors.append("matrix must be fixture_first")

    attestations = matrix.get("attestations", {})
    for key, expected in ATTESTATIONS.items():
        if not isinstance(attestations, Mapping) or attestations.get(key) is not expected:
            errors.append(f"attestation {key} must be true")

    commands = matrix.get("offline_validation_commands", [])
    if not isinstance(commands, list) or not commands:
        errors.append("offline validation commands are required")
    elif any(not isinstance(command, str) or not command.startswith("python3 ") for command in commands):
        errors.append("offline validation commands must be python3 commands")

    source_packets = matrix.get("source_packets", [])
    packet_ids = [packet.get("id") for packet in source_packets if isinstance(packet, Mapping)]
    for packet_id in REQUIRED_PACKET_IDS:
        if packet_id not in packet_ids:
            errors.append(f"source packet {packet_id} is required")
    for packet in source_packets if isinstance(source_packets, list) else []:
        if not isinstance(packet, Mapping):
            errors.append("source packet entries must be objects")
            continue
        if packet.get("status") != "inactive":
            errors.append(f"source packet {packet.get('id')} must be inactive")
        if not packet.get("reviewer_owner"):
            errors.append(f"source packet {packet.get('id')} needs reviewer_owner")

    scenarios = matrix.get("scenarios", [])
    if not isinstance(scenarios, list) or len(scenarios) != len(SCENARIO_BLUEPRINTS):
        errors.append("matrix must contain the five required scenarios")
        _validate_no_forbidden_payloads(matrix, errors)
        return errors

    expected_ids = {blueprint["id"] for blueprint in SCENARIO_BLUEPRINTS}
    actual_ids = {scenario.get("id") for scenario in scenarios if isinstance(scenario, Mapping)}
    if actual_ids != expected_ids:
        errors.append("scenario ids do not match required replay families")

    for scenario in scenarios:
        if not isinstance(scenario, Mapping):
            errors.append("scenario entries must be objects")
            continue
        scenario_id = scenario.get("id")
        if not scenario.get("reviewer_owner"):
            errors.append(f"scenario {scenario_id} needs reviewer_owner")
        if scenario.get("next_action_classification") not in ALLOWED_NEXT_ACTION_CLASSIFICATIONS:
            errors.append(f"scenario {scenario_id} has unsupported next_action_classification")
        if not scenario.get("gap_analysis_refs"):
            errors.append(f"scenario {scenario_id} needs gap_analysis_refs")
        if not scenario.get("guardrail_refs"):
            errors.append(f"scenario {scenario_id} needs guardrail_refs")
        if not _has_citations(scenario.get("replay_row_citations")):
            errors.append(f"scenario {scenario_id} replay row must cite all required source packets")
        for outcome_key in ("before_expected_outcome", "after_expected_outcome"):
            outcome = scenario.get(outcome_key)
            if not isinstance(outcome, Mapping):
                errors.append(f"scenario {scenario_id} needs {outcome_key}")
                continue
            if not outcome.get("text"):
                errors.append(f"scenario {scenario_id} {outcome_key} needs text")
            citations = outcome.get("citations")
            if not _has_citations(citations):
                errors.append(f"scenario {scenario_id} {outcome_key} must cite all required source packets")

    _validate_no_forbidden_payloads(matrix, errors)
    return errors


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, help="source packet fixture JSON")
    parser.add_argument("--validate", action="store_true", help="validate instead of printing only")
    args = parser.parse_args(argv)

    matrix = build_matrix(load_source_packets(args.fixture))
    if args.validate:
        errors = validate_matrix(matrix)
        if errors:
            for error in errors:
                print(error)
            return 1
    print(json.dumps(matrix, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
