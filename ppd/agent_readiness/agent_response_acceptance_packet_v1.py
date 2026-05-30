"""Fixture-first guarded agent response acceptance packet v1.

This module assembles committed PP&D fixture outputs into deterministic,
cited final-response examples for agent consumers. It consumes guardrail-to-agent
explanation packet v1 output, offline agent readiness adapter v4 examples,
draft-preview bridge v1 user gap analysis, and action-journal replay evidence.
It never calls a live LLM, opens DevHub, reads private user data, mutates shared
state, or performs an official PP&D action.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping


PACKET_TYPE = "ppd.guarded_agent_response_acceptance_packet.v1"
REQUIRED_EXAMPLE_KINDS = (
    "missing_facts",
    "stale_conflicting_evidence",
    "reversible_draft_limits",
    "blocked_official_actions",
    "next_safe_read_only_steps",
)
REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub",
    "no_private_data",
    "no_official_action",
)
SUPPORTED_PROCESS_IDS = ("ppd-single-pdf-plan-review-v1",)
SUPPORTED_GUARDRAIL_BUNDLE_IDS = ("guardrail-explanation-single-pdf-v1",)
OFFLINE_VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]

_PRIVATE_KEYS = {
    "access_token",
    "account_number",
    "applicant_email",
    "applicant_name",
    "auth_state",
    "authenticated_fact",
    "authenticated_facts",
    "bank_account",
    "card_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "cvv",
    "devhub_session",
    "email",
    "entered_value",
    "field_value",
    "file_path",
    "local_path",
    "password",
    "payment_details",
    "phone",
    "private_document",
    "private_documents",
    "private_fact",
    "private_facts",
    "private_value",
    "private_values",
    "raw_value",
    "refresh_token",
    "secret",
    "session_state",
    "ssn",
    "token",
    "user_input",
    "user_supplied_value",
    "value",
}
_RAW_ARTIFACT_KEYS = {
    "browser_snapshot",
    "browser_storage",
    "browser_trace",
    "document_body",
    "downloaded_document",
    "downloaded_documents",
    "dom_snapshot",
    "har",
    "html",
    "page_content",
    "raw_browser_artifact",
    "raw_crawl_output",
    "raw_document",
    "raw_document_text",
    "raw_dom",
    "raw_html",
    "raw_session",
    "raw_text",
    "screenshot",
    "session_artifact",
    "trace",
}
_MUTATION_FLAG_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "source_mutation",
    "surface_registry_mutation",
}
_LOCAL_PATH_RE = re.compile(r"(file://|/home/|/users/|/var/folders/|/tmp/|\\users\\|[a-z]:\\)", re.IGNORECASE)
_PRIVATE_TEXT_RE = re.compile(
    r"\b(authenticated fact|authenticated value|credential|cookie|session token|payment detail|card number|"
    r"applicant email|private document|private fact|private value|unredacted)\b",
    re.IGNORECASE,
)
_UNCITED_TEXT_RE = re.compile(r"\b(uncited|citation needed|no citation|without citation)\b", re.IGNORECASE)
_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will be approved|permit will issue|approval is certain|legally sufficient|no legal risk)\b",
    re.IGNORECASE,
)
_FINAL_ACTION_RE = re.compile(
    r"\b(final submit|final submission|submit payment|make payment|paid (the )?fee|pay (the )?fee|"
    r"submitted (the )?(application|permit|request)|I (will|can|should) (submit|upload|schedule|cancel|certify|pay)|"
    r"click(ed)? (submit|pay|upload|schedule|cancel|certify)|select(ed)? (submit|pay|upload|schedule|cancel|certify)|"
    r"uploaded (the )?(file|document|correction|plans)|upload (the )?(file|document|correction|plans)|"
    r"scheduled (the )?inspection|schedule (the )?inspection|cancelled (the )?(inspection|permit|request)|"
    r"canceled (the )?(inspection|permit|request)|cancel (the )?(inspection|permit|request)|"
    r"certify (the )?(application|acknowledgement|acknowledgment)|certified (the )?(application|acknowledgement|acknowledgment))\b",
    re.IGNORECASE,
)


class AgentResponseAcceptancePacketV1Error(ValueError):
    """Raised when fixtures cannot produce a safe acceptance packet."""

    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid guarded agent response acceptance packet v1: " + "; ".join(self.problems))


def load_agent_response_acceptance_fixture(path: str | Path) -> dict[str, Any]:
    """Load committed fixture inputs and build the v1 acceptance packet."""

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AgentResponseAcceptancePacketV1Error(["fixture must be a JSON object"])
    return build_agent_response_acceptance_packet_v1(
        guardrail_to_agent_explanation_packet=_required_mapping(raw, "guardrail_to_agent_explanation_packet"),
        offline_agent_readiness_adapter_outputs=_required_sequence(raw, "offline_agent_readiness_adapter_outputs"),
        user_gap_analysis_to_draft_preview_bridge_v1=_required_mapping(raw, "user_gap_analysis_to_draft_preview_bridge_v1"),
        action_journal_replay_fixture=_required_mapping(raw, "action_journal_replay_fixture"),
    )


def build_agent_response_acceptance_packet_v1(
    *,
    guardrail_to_agent_explanation_packet: Mapping[str, Any],
    offline_agent_readiness_adapter_outputs: Iterable[Mapping[str, Any]],
    user_gap_analysis_to_draft_preview_bridge_v1: Mapping[str, Any],
    action_journal_replay_fixture: Mapping[str, Any],
) -> dict[str, Any]:
    """Build cited final-response examples from offline fixture outputs."""

    explanation_packet = deepcopy(dict(guardrail_to_agent_explanation_packet))
    adapter_outputs = [deepcopy(dict(item)) for item in offline_agent_readiness_adapter_outputs]
    bridge = deepcopy(dict(user_gap_analysis_to_draft_preview_bridge_v1))
    journal = deepcopy(dict(action_journal_replay_fixture))

    input_errors = _input_errors(explanation_packet, adapter_outputs, bridge, journal)
    if input_errors:
        raise AgentResponseAcceptancePacketV1Error(input_errors)

    citation_ids = _citation_ids(explanation_packet, bridge, adapter_outputs, journal)
    packet = {
        "packet_type": PACKET_TYPE,
        "fixture_first": True,
        "metadata_only": True,
        "acceptance_version": "v1",
        "case_id": _text(explanation_packet.get("case_id") or bridge.get("case_id")),
        "process_id": _text(explanation_packet.get("process_id") or bridge.get("process_id")),
        "guardrail_bundle_id": _text(explanation_packet.get("guardrail_bundle_id")),
        "input_refs": {
            "guardrail_to_agent_explanation_packet": _text(explanation_packet.get("packet_type")),
            "guardrail_bundle_id": _text(explanation_packet.get("guardrail_bundle_id")),
            "offline_agent_readiness_adapter_output_kinds": sorted(_text(item.get("example_kind")) for item in adapter_outputs),
            "draft_preview_bridge_analysis_id": _text(bridge.get("analysis_id")),
            "action_journal_replay_packet": _text(journal.get("packet_version")),
        },
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
        "final_response_examples": [
            _missing_facts_example(explanation_packet, adapter_outputs, bridge, journal, citation_ids),
            _stale_conflicting_example(explanation_packet, adapter_outputs, bridge, journal, citation_ids),
            _reversible_draft_limits_example(explanation_packet, adapter_outputs, bridge, journal, citation_ids),
            _blocked_official_actions_example(explanation_packet, adapter_outputs, bridge, journal, citation_ids),
            _next_safe_read_only_steps_example(explanation_packet, adapter_outputs, bridge, journal, citation_ids),
        ],
    }

    errors = validate_agent_response_acceptance_packet_v1(packet)
    if errors:
        raise AgentResponseAcceptancePacketV1Error(errors)
    return packet


def validate_agent_response_acceptance_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a built acceptance packet."""

    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be ppd.guarded_agent_response_acceptance_packet.v1")
    for key in ("fixture_first", "metadata_only"):
        if packet.get(key) is not True:
            errors.append(f"{key} must be true")
    if packet.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        errors.append("offline_validation_commands must include only the PP&D daemon self-test")
    errors.extend(_unsupported_id_errors(packet, "packet"))

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
    else:
        for name in REQUIRED_ATTESTATIONS:
            if attestations.get(name) is not True:
                errors.append(f"attestations.{name} must be true")

    examples = packet.get("final_response_examples")
    if not isinstance(examples, list):
        errors.append("final_response_examples must be a list")
        examples = []
    kinds = [_text(example.get("example_kind")) for example in examples if isinstance(example, Mapping)]
    if set(kinds) != set(REQUIRED_EXAMPLE_KINDS):
        errors.append("final_response_examples must cover every required example kind exactly once")
    if len(kinds) != len(set(kinds)):
        errors.append("final_response_examples must not duplicate example kinds")

    for index, example in enumerate(examples):
        path = f"final_response_examples[{index}]"
        if not isinstance(example, Mapping):
            errors.append(f"{path} must be an object")
            continue
        citations = _strings(example.get("citations"))
        if not citations:
            errors.append(f"{path}.citations must be non-empty")
        if any(_UNCITED_TEXT_RE.search(citation) for citation in citations):
            errors.append(f"{path}.citations must not contain uncited placeholders")
        if not _text(example.get("final_response")):
            errors.append(f"{path}.final_response must be non-empty")
        safety = example.get("safety")
        if not isinstance(safety, Mapping):
            errors.append(f"{path}.safety must be an object")
        else:
            for key in ("live_llm_used", "devhub_used", "private_data_used", "official_action_performed"):
                if safety.get(key) is not False:
                    errors.append(f"{path}.safety.{key} must be false")
        consumed = example.get("consumed_input_refs")
        if not isinstance(consumed, Mapping) or not any(_text(item) for item in consumed.values() if isinstance(item, str)):
            errors.append(f"{path}.consumed_input_refs must cite consumed fixture inputs")
        errors.extend(_unsafe_value_errors(example, path))

    errors.extend(_unsafe_value_errors(packet.get("input_refs", {}), "input_refs"))
    return errors


def _input_errors(
    explanation_packet: Mapping[str, Any],
    adapter_outputs: list[Mapping[str, Any]],
    bridge: Mapping[str, Any],
    journal: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    if explanation_packet.get("packet_type") != "ppd.guardrail_to_agent_explanation_packet.v1":
        errors.append("guardrail_to_agent_explanation_packet must be v1 output")
    if bridge.get("bridge_version") != "draft_preview_bridge_v1":
        errors.append("user gap analysis must be draft preview bridge v1 output")
    if journal.get("packet_version") != "action-journal-acceptance-packet-v1":
        errors.append("action journal replay fixture must be action journal acceptance packet v1")
    errors.extend(_unsupported_id_errors(explanation_packet, "guardrail_to_agent_explanation_packet"))
    errors.extend(_unsupported_id_errors(bridge, "user_gap_analysis_to_draft_preview_bridge_v1"))
    if not adapter_outputs:
        errors.append("offline agent readiness adapter v4 outputs are required")
    adapter_kinds = {_text(item.get("example_kind")) for item in adapter_outputs}
    required_adapter_kinds = {
        "missing_information_prompt",
        "stale_or_conflicting_evidence_notice",
        "reversible_draft_preview",
        "blocked_action_explanation",
        "next_safe_read_only_action",
    }
    missing_adapter = sorted(required_adapter_kinds - adapter_kinds)
    if missing_adapter:
        errors.append(f"offline adapter outputs missing example kinds: {missing_adapter}")

    for label, value in (
        ("guardrail_to_agent_explanation_packet", explanation_packet),
        ("offline_agent_readiness_adapter_outputs", adapter_outputs),
        ("user_gap_analysis_to_draft_preview_bridge_v1", bridge),
        ("action_journal_replay_fixture", journal),
    ):
        errors.extend(_unsafe_value_errors(value, label))
    return errors


def _missing_facts_example(
    explanation_packet: Mapping[str, Any],
    adapter_outputs: list[Mapping[str, Any]],
    bridge: Mapping[str, Any],
    journal: Mapping[str, Any],
    citation_ids: list[str],
) -> dict[str, Any]:
    template = _template(explanation_packet, "missing_facts")
    adapter = _adapter(adapter_outputs, "missing_information_prompt")
    prompt_ids = [_text(item.get("prompt_id")) for item in _list_of_mappings(bridge.get("cited_missing_fact_prompts"))]
    missing = _strings(template.get("missing_facts")) + _strings(template.get("missing_documents"))
    response = "I need the missing fixture facts before drafting a PP&D answer: " + ", ".join(missing or prompt_ids)
    response += ". I can ask only for those cited facts and keep the workflow read-only."
    return _example("missing_facts", response, citation_ids, template, adapter, bridge, journal, extra={"missing_items": missing, "bridge_prompt_ids": prompt_ids})


def _stale_conflicting_example(
    explanation_packet: Mapping[str, Any],
    adapter_outputs: list[Mapping[str, Any]],
    bridge: Mapping[str, Any],
    journal: Mapping[str, Any],
    citation_ids: list[str],
) -> dict[str, Any]:
    template = _template(explanation_packet, "stale_conflicting_evidence")
    adapter = _adapter(adapter_outputs, "stale_or_conflicting_evidence_notice")
    notices = [_text(item.get("notice_id")) for item in _list_of_mappings(bridge.get("stale_conflict_notices"))]
    response = "The cited fixtures include stale or conflicting evidence, so I should surface the issue and request refreshed public or user-confirmed facts before relying on the draft."
    return _example("stale_conflicting_evidence", response, citation_ids, template, adapter, bridge, journal, extra={"bridge_notice_ids": notices})


def _reversible_draft_limits_example(
    explanation_packet: Mapping[str, Any],
    adapter_outputs: list[Mapping[str, Any]],
    bridge: Mapping[str, Any],
    journal: Mapping[str, Any],
    citation_ids: list[str],
) -> dict[str, Any]:
    template = _template(explanation_packet, "reversible_draft_limits")
    adapter = _adapter(adapter_outputs, "reversible_draft_preview")
    blockers = [_text(item.get("field_id")) for item in _list_of_mappings(bridge.get("field_level_draft_blockers"))]
    response = "A local draft preview is allowed only as reversible review material. Blocked fields must stay blank or marked unresolved, and record-changing PP&D steps remain out of scope."
    return _example("reversible_draft_limits", response, citation_ids, template, adapter, bridge, journal, extra={"blocked_field_ids": blockers})


def _blocked_official_actions_example(
    explanation_packet: Mapping[str, Any],
    adapter_outputs: list[Mapping[str, Any]],
    bridge: Mapping[str, Any],
    journal: Mapping[str, Any],
    citation_ids: list[str],
) -> dict[str, Any]:
    template = _template(explanation_packet, "blocked_official_actions")
    adapter = _adapter(adapter_outputs, "blocked_action_explanation")
    action_ids = [_text(item.get("action_id")) for item in _list_of_mappings(template.get("actions"))]
    response = "The requested official PP&D action is blocked in this offline packet. I can explain the block and prepare a read-only handoff, but I cannot perform the record-changing step."
    return _example("blocked_official_actions", response, citation_ids, template, adapter, bridge, journal, extra={"blocked_action_ids": action_ids})


def _next_safe_read_only_steps_example(
    explanation_packet: Mapping[str, Any],
    adapter_outputs: list[Mapping[str, Any]],
    bridge: Mapping[str, Any],
    journal: Mapping[str, Any],
    citation_ids: list[str],
) -> dict[str, Any]:
    template = _template(explanation_packet, "next_safe_read_only_actions")
    adapter = _adapter(adapter_outputs, "next_safe_read_only_action")
    actions = [_text(item.get("action_id")) for item in _list_of_mappings(bridge.get("next_safe_read_only_actions"))]
    response = "The next safe step is to compare the committed fixtures, cite the relevant PP&D public guidance, and produce a local read-only readiness note."
    return _example("next_safe_read_only_steps", response, citation_ids, template, adapter, bridge, journal, extra={"read_only_action_ids": actions})


def _example(
    kind: str,
    response: str,
    citation_ids: list[str],
    template: Mapping[str, Any],
    adapter: Mapping[str, Any],
    bridge: Mapping[str, Any],
    journal: Mapping[str, Any],
    *,
    extra: Mapping[str, Any],
) -> dict[str, Any]:
    journal_refs = [_text(event.get("event_id")) for event in _list_of_mappings(journal.get("journal_events"))]
    return {
        "example_kind": kind,
        "final_response": response,
        "citations": sorted(set(citation_ids + _strings(template.get("citation_ids")) + _strings(adapter.get("citations")))),
        "consumed_input_refs": {
            "guardrail_explanation_kind": _text(template.get("kind")),
            "adapter_example_kind": _text(adapter.get("example_kind")),
            "draft_preview_bridge_analysis_id": _text(bridge.get("analysis_id")),
            "action_journal_event_ids": journal_refs,
        },
        "safety": {
            "live_llm_used": False,
            "devhub_used": False,
            "private_data_used": False,
            "official_action_performed": False,
        },
        **dict(extra),
    }


def _citation_ids(
    explanation_packet: Mapping[str, Any],
    bridge: Mapping[str, Any],
    adapter_outputs: list[Mapping[str, Any]],
    journal: Mapping[str, Any],
) -> list[str]:
    ids: set[str] = set()
    for citation in _list_of_mappings(explanation_packet.get("citation_index")):
        ids.add(_text(citation.get("evidence_id")))
    for key in ("cited_missing_fact_prompts", "stale_conflict_notices", "field_level_draft_blockers", "user_review_checkpoints", "next_safe_read_only_actions"):
        for item in _list_of_mappings(bridge.get(key)):
            ids.update(_strings(item.get("citations")))
    for item in adapter_outputs:
        ids.update(_strings(item.get("citations")))
    for event in _list_of_mappings(journal.get("journal_events")):
        ids.add(_text(event.get("event_id")))
    return sorted(item for item in ids if item)


def _template(packet: Mapping[str, Any], kind: str) -> Mapping[str, Any]:
    for item in _list_of_mappings(packet.get("explanation_templates")):
        if item.get("kind") == kind:
            return item
    return {}


def _adapter(outputs: list[Mapping[str, Any]], kind: str) -> Mapping[str, Any]:
    for item in outputs:
        if item.get("example_kind") == kind:
            return item
    return {}


def _required_mapping(packet: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = packet.get(key)
    if not isinstance(value, Mapping):
        raise AgentResponseAcceptancePacketV1Error([f"{key} must be an object"])
    return value


def _required_sequence(packet: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = packet.get(key)
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise AgentResponseAcceptancePacketV1Error([f"{key} must be a list of objects"])
    return value


def _list_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _unsupported_id_errors(value: Mapping[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    process_id = _text(value.get("process_id"))
    if process_id and process_id not in SUPPORTED_PROCESS_IDS:
        errors.append(f"unsupported process_id at {path}.process_id: {process_id}")
    guardrail_bundle_id = _text(value.get("guardrail_bundle_id"))
    if guardrail_bundle_id and guardrail_bundle_id not in SUPPORTED_GUARDRAIL_BUNDLE_IDS:
        errors.append(f"unsupported guardrail_bundle_id at {path}.guardrail_bundle_id: {guardrail_bundle_id}")
    return errors


def _unsafe_value_errors(value: Any, path: str, key_name: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            child_path = f"{path}.{key_text}"
            if normalized_key in _PRIVATE_KEYS and child not in (None, "", [], {}):
                errors.append(f"private data field is not allowed at {child_path}")
            if normalized_key in _RAW_ARTIFACT_KEYS and child not in (None, "", [], {}):
                errors.append(f"raw document, session, or browser artifact is not allowed at {child_path}")
            if normalized_key in _MUTATION_FLAG_KEYS and child not in (False, None, "", [], {}):
                errors.append(f"active prompt, guardrail, source, surface-registry, release-state, or agent-state mutation is not allowed at {child_path}")
            errors.extend(_unsafe_value_errors(child, child_path, normalized_key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_unsafe_value_errors(child, f"{path}[{index}]", key_name))
    elif isinstance(value, str):
        if _LOCAL_PATH_RE.search(value):
            errors.append(f"private local path is not allowed at {path}")
        if _PRIVATE_TEXT_RE.search(value):
            errors.append(f"private or authenticated value text is not allowed at {path}")
        if _UNCITED_TEXT_RE.search(value):
            errors.append(f"uncited response example text is not allowed at {path}")
        if _GUARANTEE_RE.search(value):
            errors.append(f"legal or permitting outcome guarantee is not allowed at {path}")
        if _FINAL_ACTION_RE.search(value):
            errors.append(f"final official action language is not allowed at {path}")
    return errors
