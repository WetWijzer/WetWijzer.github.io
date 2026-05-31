from __future__ import annotations

from typing import Any, Mapping

PACKET_TYPE = "ppd.reversible_draft_executor_dry_run_contract.v2"
CONTRACT_VERSION = 2
EXACT_CONFIRMATION_PHRASE = "I confirm this is a preview-only dry run and no official PP&D action will be taken."

REQUIRED_CONSEQUENTIAL_EXAMPLES = frozenset({
    "fill_live_form",
    "save_official_draft",
    "upload_file",
    "submit_application",
    "certify_application",
    "pay_fee",
    "schedule_inspection",
    "cancel_request",
    "change_account",
    "activate_release_state",
})

REQUIRED_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/devhub/reversible_draft_contract_v2.py"),
    ("python3", "-m", "unittest", "ppd.tests.test_reversible_draft_contract_v2"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

MUTATION_FLAGS = (
    "active_prompt_mutated",
    "active_guardrail_mutated",
    "active_devhub_surface_mutated",
    "active_source_mutated",
    "active_contract_mutated",
    "active_release_state_mutated",
)

FORBIDDEN_TEXT = (
    "browser trace",
    "browser_trace",
    "downloaded artifact",
    "downloaded_artifact",
    "downloads/",
    "/tmp/",
    "/home/",
    "session cookie",
    "session_cookie",
    "sessionstorage",
    "localstorage",
    "raw devhub",
    "raw_devhub",
    "raw user",
    "raw_user",
    "private artifact",
    "private_artifact",
    "private document",
    "private_document",
    "screenshot",
    "playwright trace",
    "opened live devhub",
    "executed in devhub",
    "filled live form",
    "live devhub execution",
    "saved official draft",
    "official draft saved",
    "submitted application",
    "application submitted",
    "certified application",
    "uploaded file",
    "paid fee",
    "permit approved",
    "approval guaranteed",
    "guaranteed approval",
    "legal guarantee",
    "permitting guarantee",
)


class ReversibleDraftContractV2ValidationError(ValueError):
    pass


def validate_reversible_draft_contract_v2(packet: Mapping[str, Any]) -> list[str]:
    issues: list[str] = []
    if not isinstance(packet, Mapping):
        return ["packet must be a mapping"]
    if packet.get("packet_type") != PACKET_TYPE:
        issues.append("packet_type must identify reversible draft executor dry-run contract v2")
    if packet.get("contract_version") != CONTRACT_VERSION:
        issues.append("contract_version must be 2")

    rows = packet.get("request_response_rows")
    if not isinstance(rows, list) or not rows:
        issues.append("request_response_rows must contain at least one request/response row")
    else:
        for index, row in enumerate(rows):
            _validate_row(row, index, issues)

    examples = packet.get("refused_consequential_action_examples")
    example_set = set(examples) if isinstance(examples, list) else set()
    if not REQUIRED_CONSEQUENTIAL_EXAMPLES.issubset(example_set):
        missing = sorted(REQUIRED_CONSEQUENTIAL_EXAMPLES - example_set)
        issues.append("refused_consequential_action_examples missing required examples: " + ", ".join(missing))

    commands = _normalize_commands(packet.get("validation_commands"))
    for command in REQUIRED_VALIDATION_COMMANDS:
        if command not in commands:
            issues.append("validation_commands missing required command: " + " ".join(command))

    flags = packet.get("active_mutation_flags")
    if not isinstance(flags, Mapping):
        issues.append("active_mutation_flags must be present")
    else:
        for flag in MUTATION_FLAGS:
            if flags.get(flag) is not False:
                issues.append(f"active_mutation_flags.{flag} must be false")

    _scan(packet, "$", issues)
    return issues


def assert_valid_reversible_draft_contract_v2(packet: Mapping[str, Any]) -> None:
    issues = validate_reversible_draft_contract_v2(packet)
    if issues:
        raise ReversibleDraftContractV2ValidationError("; ".join(issues))


def _validate_row(row: Any, index: int, issues: list[str]) -> None:
    path = f"request_response_rows[{index}]"
    if not isinstance(row, Mapping):
        issues.append(f"{path} must be a mapping")
        return
    for field in ("row_id", "request", "response", "preview_only_field_mapping_requirements", "user_fact_traces", "source_evidence_traces", "selector_confidence_placeholder", "exact_confirmation_stop_gate"):
        if field not in row:
            issues.append(f"{path}.{field} is required")

    request = row.get("request")
    response = row.get("response")
    if not isinstance(request, Mapping) or request.get("preview_only") is not True:
        issues.append(f"{path}.request.preview_only must be true")
    if not isinstance(response, Mapping):
        issues.append(f"{path}.response must be a mapping")
    else:
        if response.get("preview_only") is not True:
            issues.append(f"{path}.response.preview_only must be true")
        if response.get("executed_devhub_actions") not in ([], (), None):
            issues.append(f"{path}.response.executed_devhub_actions must be empty")
        if response.get("saved_official_draft") not in (False, None):
            issues.append(f"{path}.response.saved_official_draft must be false")
        if response.get("submitted") not in (False, None):
            issues.append(f"{path}.response.submitted must be false")

    mappings = row.get("preview_only_field_mapping_requirements")
    if not isinstance(mappings, list) or not mappings:
        issues.append(f"{path}.preview_only_field_mapping_requirements must be a non-empty list")
    else:
        for mapping_index, mapping in enumerate(mappings):
            item_path = f"{path}.preview_only_field_mapping_requirements[{mapping_index}]"
            if not isinstance(mapping, Mapping):
                issues.append(f"{item_path} must be a mapping")
                continue
            if mapping.get("preview_only") is not True:
                issues.append(f"{item_path}.preview_only must be true")
            if not _text(mapping.get("field_key")):
                issues.append(f"{item_path}.field_key is required")
            if not _text(mapping.get("value_placeholder")):
                issues.append(f"{item_path}.value_placeholder is required")

    _trace_list(row.get("user_fact_traces"), f"{path}.user_fact_traces", "user_fact", issues)
    _trace_list(row.get("source_evidence_traces"), f"{path}.source_evidence_traces", "source_evidence", issues)

    selector = row.get("selector_confidence_placeholder")
    if not isinstance(selector, Mapping) or selector.get("placeholder") is not True or selector.get("value") is not None:
        issues.append(f"{path}.selector_confidence_placeholder must be placeholder=true with value=null")

    gate = row.get("exact_confirmation_stop_gate")
    if not isinstance(gate, Mapping):
        issues.append(f"{path}.exact_confirmation_stop_gate must be a mapping")
    else:
        if gate.get("requires_exact_confirmation") is not True:
            issues.append(f"{path}.exact_confirmation_stop_gate.requires_exact_confirmation must be true")
        if gate.get("confirmation_phrase") != EXACT_CONFIRMATION_PHRASE:
            issues.append(f"{path}.exact_confirmation_stop_gate.confirmation_phrase must match the exact dry-run phrase")


def _trace_list(value: Any, path: str, kind: str, issues: list[str]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(f"{path} must contain at least one trace")
        return
    for index, trace in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(trace, Mapping):
            issues.append(f"{item_path} must be a mapping")
            continue
        if trace.get("trace_kind") != kind:
            issues.append(f"{item_path}.trace_kind must be {kind}")
        if not _text(trace.get("placeholder_id")):
            issues.append(f"{item_path}.placeholder_id is required")


def _scan(value: Any, path: str, issues: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_text = str(key).lower()
            if (key_text in MUTATION_FLAGS or key_text.endswith("mutation_flag")) and child is not False:
                issues.append(f"{child_path} must be false")
            _scan(child, child_path, issues)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan(child, f"{path}[{index}]", issues)
    elif isinstance(value, str):
        lowered = value.lower()
        for marker in FORBIDDEN_TEXT:
            if marker in lowered:
                issues.append(f"{path} contains forbidden dry-run contract content: {marker}")


def _normalize_commands(commands: Any) -> set[tuple[str, ...]]:
    if not isinstance(commands, list):
        return set()
    return {tuple(command) for command in commands if isinstance(command, list) and all(isinstance(part, str) for part in command)}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
