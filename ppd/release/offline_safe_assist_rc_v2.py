"""Build and validate an offline safe-assist release candidate packet.

The builder is intentionally fixture-first: it reads only local JSON files supplied by
PP&D tests or an offline validation run and emits a deterministic packet. It never
opens DevHub, crawls public sources, calls an LLM, invokes processors, or mutates
release state.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_FIXTURES = {
    "prompt_refresh_release_handoff": "prompt_refresh_release_handoff_v2.json",
    "draft_preview_agent_handoff_acceptance": "draft_preview_agent_handoff_acceptance_packet_v2.json",
    "guardrail_refresh_regression_matrix": "guardrail_refresh_regression_matrix_v2.json",
    "surface_registry_refresh_acceptance": "surface_registry_refresh_acceptance_packet_v2.json",
    "release_rollback_readiness": "release_rollback_readiness_fixtures_v2.json",
}

ATTESTATIONS = {
    "no_live_release": True,
    "no_live_devhub": True,
    "no_llm": True,
    "no_crawler": True,
    "no_processor": True,
    "no_release_state_mutation": True,
}

MUTATION_FLAGS = {
    "source_mutation_active": False,
    "process_mutation_active": False,
    "guardrail_mutation_active": False,
    "surface_registry_mutation_active": False,
    "prompt_mutation_active": False,
    "monitoring_mutation_active": False,
    "release_state_mutation_active": False,
    "agent_state_mutation_active": False,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ["python3", "-m", "pytest", "ppd/tests/test_offline_safe_assist_rc_v2.py"],
]

CONSEQUENTIAL_ACTION_KEYWORDS = (
    "submit",
    "certify",
    "upload",
    "payment",
    "pay",
    "schedule",
    "cancel",
    "withdraw",
    "purchase",
    "official attach",
    "release",
)

REQUIRED_GATE_KEYWORDS = (
    "submit",
    "certify",
    "upload",
    "payment",
    "pay",
    "schedule",
    "cancel",
    "withdraw",
    "purchase",
)

PRIVATE_OR_AUTH_KEYS = {
    "access_token",
    "auth",
    "auth_state",
    "authenticated_fact",
    "browser_state",
    "card_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "cvv",
    "devhub_session",
    "email",
    "field_value",
    "local_path",
    "password",
    "payment_details",
    "phone",
    "private_fact",
    "private_value",
    "raw_value",
    "refresh_token",
    "session",
    "session_cookie",
    "session_state",
    "ssn",
    "token",
    "user_input",
    "value",
}

RAW_ARTIFACT_KEYS = {
    "archive_artifact_ref",
    "browser_trace",
    "crawl_output",
    "downloaded_document",
    "har",
    "pdf_artifact",
    "pdf_download",
    "raw_body",
    "raw_crawl",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "session_artifact",
    "trace",
}

MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation_active",
    "apply_update",
    "commit_to_registry",
    "guardrail_mutation_active",
    "monitoring_mutation_active",
    "mutate_agent_state",
    "mutate_guardrail_bundle",
    "mutate_monitoring",
    "mutate_process_model",
    "mutate_prompt",
    "mutate_release_state",
    "mutate_source",
    "mutate_surface_registry",
    "process_mutation_active",
    "prompt_mutation_active",
    "release_state_mutation_active",
    "source_mutation_active",
    "surface_registry_mutation_active",
    "write_active_guardrail",
    "write_active_process",
    "write_active_prompt",
    "write_active_registry",
}

RAW_OR_PRIVATE_ARTIFACT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|(^[A-Za-z]:\\Users\\[^\\]+\\)|"
    r"(auth[_-]?state|browser[_-]?state|cookie|credential|har|password|private[_-]?fact|raw[_-]?(body|crawl|html|pdf)|"
    r"session[_-]?(artifact|state)?|screenshot|secret|storage[_-]?state|token|trace\.zip|warc)",
    re.IGNORECASE,
)

LIVE_EXECUTION_CLAIM_RE = re.compile(
    r"\b(live\s+(release|devhub|browser|llm|crawl|crawler|processor|execution)|"
    r"opened\s+(a\s+)?browser|launched\s+devhub|ran\s+(the\s+)?(crawler|processor|llm)|"
    r"executed\s+(the\s+)?(release|devhub|browser|crawler|processor)|called\s+(an\s+)?llm)\b",
    re.IGNORECASE,
)

OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?\s+(approval|issuance|permit|legal|compliance|outcome)|"
    r"(permit|application|inspection|appeal)\s+(will|shall)\s+be\s+(approved|issued|accepted|granted|upheld)|"
    r"legally\s+guaranteed|guaranteed\s+code\s+compliance)\b",
    re.IGNORECASE,
)

FINAL_ACTION_LANGUAGE_RE = re.compile(
    r"\b(final\s+(submit|submission|payment|upload|schedule|scheduling|cancellation)\s+(complete|completed|enabled|executed|performed|ready)|"
    r"(submitted|uploaded|paid|scheduled|cancelled|canceled)\s+(to|in|through|on)\s+(devhub|official|the\s+city|pp&d)|"
    r"(payment|submission|upload|scheduling|cancellation)\s+(has\s+)?(completed|executed|succeeded|been\s+performed))\b",
    re.IGNORECASE,
)

OFFLINE_COMMAND_BLOCKLIST = (
    "browser",
    "crawl",
    "crawler",
    "devhub",
    "download",
    "llm",
    "playwright",
    "processor",
    "release-live",
)


@dataclass(frozen=True)
class ReleaseCandidateValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return loaded


def load_release_candidate_fixtures(fixture_dir: Path) -> dict[str, dict[str, Any]]:
    """Load the five required offline release candidate source fixtures."""

    fixtures: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for fixture_name, filename in REQUIRED_FIXTURES.items():
        path = fixture_dir / filename
        if not path.exists():
            missing.append(filename)
            continue
        fixtures[fixture_name] = _load_json(path)
    if missing:
        raise FileNotFoundError("missing offline RC fixture(s): " + ", ".join(sorted(missing)))
    return fixtures


def _fixture_citation(fixture_name: str, fixture: dict[str, Any]) -> str:
    packet_id = str(fixture.get("packet_id") or fixture.get("fixture_id") or fixture_name)
    version = str(fixture.get("version") or "v2")
    return f"{fixture_name}:{packet_id}:{version}"


def _citations(fixtures: dict[str, dict[str, Any]], names: list[str]) -> list[str]:
    return [_fixture_citation(name, fixtures[name]) for name in names]


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _collect_guardrail_gates(fixtures: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    matrix = fixtures["guardrail_refresh_regression_matrix"]
    surface = fixtures["surface_registry_refresh_acceptance"]
    draft = fixtures["draft_preview_agent_handoff_acceptance"]

    gate_names: set[str] = set()
    for item in _as_string_list(matrix.get("blocked_action_gates")):
        gate_names.add(item)
    for action in _as_string_list(surface.get("requires_exact_confirmation")):
        gate_names.add(action)
    for action in _as_string_list(draft.get("blocked_consequential_actions")):
        gate_names.add(action)

    for action in _as_string_list(surface.get("actions")):
        lowered = action.lower()
        if any(keyword in lowered for keyword in CONSEQUENTIAL_ACTION_KEYWORDS):
            gate_names.add(action)

    return [
        {
            "gate_id": "blocked-" + name.lower().replace(" ", "-").replace("/", "-"),
            "action": name,
            "status": "blocked_until_user_attended_exact_confirmation",
            "citations": _citations(
                fixtures,
                [
                    "guardrail_refresh_regression_matrix",
                    "surface_registry_refresh_acceptance",
                    "draft_preview_agent_handoff_acceptance",
                ],
            ),
        }
        for name in sorted(gate_names)
    ]


def _safe_rollback_block_ids(value: Any) -> list[str]:
    block_ids: list[str] = []
    for index, item in enumerate(_as_string_list(value)):
        normalized = re.sub(r"[^a-z0-9]+", "-", item.lower()).strip("-")
        if not normalized:
            normalized = f"rollback-block-{index}"
        block_ids.append(normalized)
    return block_ids


def _build_notes(fixtures: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    prompt = fixtures["prompt_refresh_release_handoff"]
    draft = fixtures["draft_preview_agent_handoff_acceptance"]
    matrix = fixtures["guardrail_refresh_regression_matrix"]
    surface = fixtures["surface_registry_refresh_acceptance"]
    rollback = fixtures["release_rollback_readiness"]

    return {
        "candidate_source_notes": {
            "summary": "Candidate is sourced only from committed offline PP&D fixtures.",
            "accepted_sources": _as_string_list(prompt.get("accepted_source_packets"))
            + _as_string_list(draft.get("accepted_source_packets")),
            "citations": _citations(fixtures, ["prompt_refresh_release_handoff", "draft_preview_agent_handoff_acceptance"]),
        },
        "candidate_process_notes": {
            "summary": "Draft-preview assistance remains limited to reversible local preview and user-visible gap analysis.",
            "accepted_processes": _as_string_list(draft.get("accepted_processes")),
            "blocked_processes": _as_string_list(draft.get("blocked_consequential_actions")),
            "citations": _citations(fixtures, ["draft_preview_agent_handoff_acceptance"]),
        },
        "candidate_guardrail_notes": {
            "summary": "Regression matrix gates consequential actions and requires attended exact confirmation.",
            "passed_regressions": _as_string_list(matrix.get("passed_regressions")),
            "blocked_action_gates": _as_string_list(matrix.get("blocked_action_gates")),
            "citations": _citations(fixtures, ["guardrail_refresh_regression_matrix"]),
        },
        "candidate_surface_notes": {
            "summary": "Surface registry compatibility is accepted only for offline safe-read and reversible-draft surfaces.",
            "accepted_surfaces": _as_string_list(surface.get("accepted_surfaces")),
            "requires_exact_confirmation": _as_string_list(surface.get("requires_exact_confirmation")),
            "citations": _citations(fixtures, ["surface_registry_refresh_acceptance"]),
        },
        "candidate_prompt_compatibility_notes": {
            "summary": "Prompt refresh handoff is compatible with offline validation mode that disables generated completions.",
            "compatible_prompt_packets": _as_string_list(prompt.get("compatible_prompt_packets")),
            "required_prompt_constraints": _as_string_list(prompt.get("required_constraints")),
            "citations": _citations(fixtures, ["prompt_refresh_release_handoff"]),
        },
        "candidate_rollback_notes": {
            "summary": "Rollback is prerequisite-gated and must remain offline until explicit operator authorization exists.",
            "rollback_prerequisites": _as_string_list(rollback.get("rollback_prerequisites")),
            "rollback_block_ids": _safe_rollback_block_ids(rollback.get("rollback_blocks")),
            "citations": _citations(fixtures, ["release_rollback_readiness"]),
        },
    }


def build_release_candidate_packet(fixture_dir: Path) -> dict[str, Any]:
    """Return a deterministic offline safe-assist release candidate packet v2."""

    fixtures = load_release_candidate_fixtures(fixture_dir)
    packet = {
        "packet_id": "offline-safe-assist-release-candidate-packet-v2",
        "packet_version": "v2",
        "mode": "fixture_first_offline_validation",
        "candidate_status": "release_candidate_blocked_for_live_release",
        "fixture_inputs": {
            name: {
                "filename": REQUIRED_FIXTURES[name],
                "citation": _fixture_citation(name, fixture),
            }
            for name, fixture in sorted(fixtures.items())
        },
        "notes": _build_notes(fixtures),
        "blocked_consequential_action_gates": _collect_guardrail_gates(fixtures),
        "rollback_prerequisites": _as_string_list(
            fixtures["release_rollback_readiness"].get("rollback_prerequisites")
        ),
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "attestations": ATTESTATIONS,
        "mutation_flags": MUTATION_FLAGS,
    }
    assert_valid_release_candidate_packet(packet)
    return packet


def validate_release_candidate_packet(packet: Mapping[str, Any]) -> ReleaseCandidateValidationResult:
    """Validate that an offline safe-assist RC packet is cited and side-effect-free."""

    problems: list[str] = []
    _scan_unsafe(packet, "$", problems)

    if packet.get("packet_id") != "offline-safe-assist-release-candidate-packet-v2":
        problems.append("packet_id must be offline-safe-assist-release-candidate-packet-v2")
    if packet.get("packet_version") != "v2":
        problems.append("packet_version must be v2")
    if packet.get("mode") != "fixture_first_offline_validation":
        problems.append("mode must be fixture_first_offline_validation")

    fixture_inputs = _mapping(packet.get("fixture_inputs"))
    for fixture_name in REQUIRED_FIXTURES:
        fixture_input = _mapping(fixture_inputs.get(fixture_name))
        if not fixture_input.get("citation"):
            problems.append(f"fixture_inputs.{fixture_name} lacks citation")

    notes = _mapping(packet.get("notes"))
    if not notes:
        problems.append("notes must be present")
    for note_name, note_value in notes.items():
        note = _mapping(note_value)
        citations = _string_sequence(note.get("citations"))
        if not citations:
            if "compatibility" in str(note_name).lower():
                problems.append(f"uncited compatibility note: {note_name}")
            else:
                problems.append(f"uncited release candidate note: {note_name}")

    gates = list(_mapping_sequence(packet.get("blocked_consequential_action_gates")))
    if not gates:
        problems.append("blocked_consequential_action_gates must be present")
    gate_actions = [str(gate.get("action") or "").lower() for gate in gates]
    for keyword in REQUIRED_GATE_KEYWORDS:
        if not any(keyword in action for action in gate_actions):
            problems.append(f"missing blocked-action gate for {keyword}")
    for index, gate in enumerate(gates):
        if gate.get("status") != "blocked_until_user_attended_exact_confirmation":
            problems.append(f"blocked_consequential_action_gates[{index}] must remain blocked until attended exact confirmation")
        if not _string_sequence(gate.get("citations")):
            problems.append(f"blocked_consequential_action_gates[{index}] lacks citations")

    rollback_prerequisites = _string_sequence(packet.get("rollback_prerequisites"))
    if not rollback_prerequisites:
        problems.append("rollback_prerequisites must be present")

    commands = list(_command_sequence(packet.get("offline_validation_commands")))
    if not commands:
        problems.append("offline_validation_commands must be present")
    for index, command in enumerate(commands):
        lowered_command = " ".join(command).lower()
        if any(blocked in lowered_command for blocked in OFFLINE_COMMAND_BLOCKLIST):
            problems.append(f"offline_validation_commands[{index}] invokes non-offline capability")

    attestations = _mapping(packet.get("attestations"))
    for key, expected in ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            problems.append(f"attestations.{key} must be true")

    mutation_flags = _mapping(packet.get("mutation_flags"))
    for key, expected in MUTATION_FLAGS.items():
        if mutation_flags.get(key) is not expected:
            problems.append(f"mutation_flags.{key} must be false")

    return ReleaseCandidateValidationResult(valid=not problems, problems=tuple(problems))


def assert_valid_release_candidate_packet(packet: Mapping[str, Any]) -> None:
    result = validate_release_candidate_packet(packet)
    if not result.valid:
        raise ValueError("invalid_offline_safe_assist_release_candidate_packet_v2: " + "; ".join(result.problems))


def build_release_candidate_packet_json(fixture_dir: Path) -> str:
    """Serialize the offline packet with stable key ordering for fixture assertions."""

    return json.dumps(build_release_candidate_packet(fixture_dir), indent=2, sort_keys=True) + "\n"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _string_sequence(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item) for item in value if str(item)]
    return []


def _command_sequence(value: Any) -> list[list[str]]:
    commands: list[list[str]] = []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return commands
    for item in value:
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            command = [str(part) for part in item if str(part)]
            if command:
                commands.append(command)
    return commands


def _scan_unsafe(value: Any, path: str, problems: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            child_path = f"{path}.{key_text}"
            if normalized_key in PRIVATE_OR_AUTH_KEYS and child not in (None, "", [], {}):
                problems.append(f"private or authenticated fact is not allowed at {child_path}")
            if normalized_key in RAW_ARTIFACT_KEYS and child not in (None, "", [], {}):
                problems.append(f"raw crawl, PDF, browser, or session artifact is not allowed at {child_path}")
            if _is_mutation_key(normalized_key) and child is True:
                problems.append(f"active mutation flag must be false at {child_path}")
            _scan_unsafe(child, child_path, problems)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_unsafe(child, f"{path}[{index}]", problems)
    elif isinstance(value, str):
        if RAW_OR_PRIVATE_ARTIFACT_RE.search(value):
            problems.append(f"raw, private, authenticated, browser, or session artifact reference is not allowed at {path}")
        if LIVE_EXECUTION_CLAIM_RE.search(value):
            problems.append(f"live release, DevHub, browser, LLM, crawler, or processor execution claim is not allowed at {path}")
        if OUTCOME_GUARANTEE_RE.search(value):
            problems.append(f"legal or permitting outcome guarantee is not allowed at {path}")
        if not _is_blocked_gate_action_path(path) and FINAL_ACTION_LANGUAGE_RE.search(value):
            problems.append(f"final submission, payment, upload, scheduling, or cancellation language is not allowed at {path}")


def _is_mutation_key(normalized_key: str) -> bool:
    if normalized_key in MUTATION_KEYS:
        return True
    if normalized_key.endswith("_mutation_active") or normalized_key.endswith("_mutation_enabled"):
        return True
    if normalized_key.startswith("active_") and normalized_key.endswith("_mutation"):
        return True
    return False


def _is_blocked_gate_action_path(path: str) -> bool:
    return "blocked_consequential_action_gates[" in path and path.endswith(".action")
