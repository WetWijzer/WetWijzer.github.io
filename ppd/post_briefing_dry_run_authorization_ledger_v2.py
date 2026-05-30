"""Fixture-first post-briefing dry-run authorization ledger v2.

The ledger is intentionally offline and side-effect free. It consumes committed
fixture packets and produces reviewer-facing authorization rows without opening
browsers, creating auth state, mutating release state, or treating any dry-run
plan as permission for live execution.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


PACKET_TYPE = "post-briefing-dry-run-authorization-ledger"
PACKET_VERSION = "v2"

REQUIRED_ATTESTATION_IDS = frozenset(
    {
        "no-live-execution",
        "no-auth-state",
        "no-browser-artifact",
        "no-official-action",
        "no-release-state-mutation",
        "no-private-authenticated-facts",
        "no-raw-artifacts",
        "no-credential-automation",
        "no-outcome-guarantees",
        "no-active-mutation-flags",
    }
)

REQUIRED_CONSUMED_KEYS = (
    "live_dry_run_operator_briefing_packet_v2",
    "live_readiness_authorization_checklist_packet_v2",
    "public_live_dry_run_plan_fixture_v2",
    "devhub_live_dry_run_plan_fixture_v2",
)

_REQUIRED_REVIEWER_PLACEHOLDER_IDS = frozenset(
    {"reviewer_name", "reviewer_timestamp_utc", "reviewer_scope_decision"}
)
_REQUIRED_OPERATOR_PLACEHOLDER_IDS = frozenset(
    {"operator_name", "authorization_timestamp_utc", "authorized_scope", "boundary_acknowledgement"}
)

_ALLOWED_OFFLINE_COMMAND_PREFIXES = (
    ("python3", "-m", "pytest", "ppd/tests/test_post_briefing_dry_run_authorization_ledger_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_FORBIDDEN_COMMAND_TOKENS = frozenset(
    {
        "playwright",
        "selenium",
        "puppeteer",
        "chromedriver",
        "geckodriver",
        "browser",
        "crawl",
        "scrape",
        "download",
        "login",
        "signin",
        "storage_state",
        "cookies.json",
        "trace",
        "har",
        "submit",
        "upload",
        "payment",
        "release",
    }
)

_PRIVATE_OR_AUTHENTICATED_FACT_RE = re.compile(
    r"\b(private\s+(fact|value|case|project|upload|document)|authenticated\s+(fact|value|page|record|session)|raw_authenticated_values?|account-scoped\s+fact)\b",
    re.IGNORECASE,
)
_RAW_ARTIFACT_RE = re.compile(
    r"\b(raw\s+(crawl|pdf|download|body|html|response)|storage[_-]?state|cookies?\.json|session\s+file|auth[_-]?state|trace\.zip|\.har\b|har\s+file|screenshot|video\s+recording|browser\s+artifact|downloaded\s+document)\b",
    re.IGNORECASE,
)
_CREDENTIAL_AUTOMATION_RE = re.compile(
    r"\b(automate[sd]?|bypass(?:ed)?|solve[sd]?|handle[sd]?|complete[sd]?|enter(?:ed)?|fill(?:ed)?)\b.{0,80}\b(credential|password|mfa|multi-factor|captcha|security\s+prompt|login|sign\s*in|one-time\s+code|otp)\b|\b(credential|password|mfa|multi-factor|captcha|security\s+prompt|one-time\s+code|otp)\b.{0,80}\b(automate[sd]?|bypass(?:ed)?|solve[sd]?|complete[sd]?|enter(?:ed)?|fill(?:ed)?)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|ensure[sd]?|will\s+(?:be\s+)?(?:approved|issued|permitted|accepted)|approval\s+guarantee|permit\s+will\s+issue|legal\s+outcome)\b",
    re.IGNORECASE,
)
_LIVE_OR_COMPLETION_CLAIM_RE = re.compile(
    r"\b(live\s+(?:crawl|execution|devhub|run)\s+(?:completed|executed|performed|authorized)|(?:completed|executed|performed)\s+(?:the\s+)?(?:live\s+)?(?:crawl|devhub\s+run|browser\s+run)|completion\s+confirmed|marked\s+complete)\b",
    re.IGNORECASE,
)
_FINAL_OFFICIAL_ACTION_RE = re.compile(
    r"\b(final\s+)?(submit(?:ted)?|submission|payment\s+(?:submitted|completed|executed)|paid\s+fees?|upload(?:ed)?\s+(?:to|into)\s+(?:devhub|official|record)|scheduled\s+inspection|cancel(?:led|ed)\s+(?:permit|inspection|application)|certif(?:y|ied)|filed\s+(?:application|permit|request))\b",
    re.IGNORECASE,
)
_NEGATED_SAFETY_RE = re.compile(
    r"\b(no|not|never|without|blocked|prohibited|remain(?:s)?\s+blocked|does\s+not|must\s+not|do\s+not|stop\s+before|abort\s+if|requires?\s+a\s+new)\b",
    re.IGNORECASE,
)
_MUTATION_FLAG_RE = re.compile(
    r"\b(source[_-]?registry|surface[_-]?registry|prompt|guardrail|monitoring|release[_-]?state|agent[_-]?state|active[_-]?source|active[_-]?surface)\b.*\b(mutation|mutate|write|update|refresh|publish|promote|activate|enable)\b|\b(mutation|mutate|write|update|refresh|publish|promote|activate|enable)\b.*\b(source[_-]?registry|surface[_-]?registry|prompt|guardrail|monitoring|release[_-]?state|agent[_-]?state)\b",
    re.IGNORECASE,
)
_MUTATION_KEY_RE = re.compile(
    r"(source_registry|surface_registry|prompt|guardrail|monitoring|release_state|agent_state|active_source|active_surface).*(mutation|mutate|write|update|refresh|publish|promote|activate|enabled|active)",
    re.IGNORECASE,
)


def load_fixture_packet(path: Path) -> dict[str, Any]:
    """Load a JSON fixture packet from a caller-selected path."""

    with path.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    if not isinstance(packet, dict):
        raise ValueError(f"fixture packet must be a JSON object: {path}")
    return packet


def build_post_briefing_dry_run_authorization_ledger_v2(source_packets: Mapping[str, Any]) -> dict[str, Any]:
    """Build a fixture-first dry-run authorization ledger from source packets."""

    missing = [key for key in REQUIRED_CONSUMED_KEYS if key not in source_packets]
    if missing:
        raise ValueError("missing consumed source packets: " + ", ".join(missing))

    briefing = _require_mapping(source_packets["live_dry_run_operator_briefing_packet_v2"], "briefing")
    checklist = _require_mapping(source_packets["live_readiness_authorization_checklist_packet_v2"], "checklist")
    public_plan = _require_mapping(source_packets["public_live_dry_run_plan_fixture_v2"], "public plan")
    devhub_plan = _require_mapping(source_packets["devhub_live_dry_run_plan_fixture_v2"], "DevHub plan")

    ledger = {
        "packet_type": PACKET_TYPE,
        "version": PACKET_VERSION,
        "ledger_id": "post-briefing-dry-run-authorization-ledger-v2-fixture-20260529",
        "mode": "fixture_first_post_briefing_authorization_review",
        "consumes": [
            _consumed_packet_row("live_dry_run_operator_briefing_packet_v2", briefing),
            _consumed_packet_row("live_readiness_authorization_checklist_packet_v2", checklist),
            _consumed_packet_row("public_live_dry_run_plan_fixture_v2", public_plan),
            _consumed_packet_row("devhub_live_dry_run_plan_fixture_v2", devhub_plan),
        ],
        "authorization_rows": _authorization_rows(briefing, checklist, public_plan, devhub_plan),
        "reviewer_signoff_placeholders": _reviewer_signoff_placeholders(),
        "operator_signoff_placeholders": _operator_signoff_placeholders(checklist),
        "scope_limited_dry_run_windows": _scope_limited_windows(public_plan, devhub_plan),
        "independent_abort_conditions": _independent_abort_conditions(briefing, public_plan, devhub_plan),
        "allowed_offline_validation_commands": [
            ["python3", "-m", "pytest", "ppd/tests/test_post_briefing_dry_run_authorization_ledger_v2.py"],
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
        ],
        "attestations": [
            {
                "id": "no-live-execution",
                "status": "attested_in_fixture",
                "statement": "This ledger does not authorize or record live execution.",
            },
            {
                "id": "no-auth-state",
                "status": "attested_in_fixture",
                "statement": "This ledger does not create, read, request, or store authentication state.",
            },
            {
                "id": "no-browser-artifact",
                "status": "attested_in_fixture",
                "statement": "This ledger does not create screenshots, traces, HAR files, recordings, or browser artifacts.",
            },
            {
                "id": "no-official-action",
                "status": "attested_in_fixture",
                "statement": "This ledger does not authorize submission, upload, payment, scheduling, cancellation, certification, or filing.",
            },
            {
                "id": "no-release-state-mutation",
                "status": "attested_in_fixture",
                "statement": "This ledger does not mutate release state, task state, source registries, guardrails, prompts, or monitoring state.",
            },
            {
                "id": "no-private-authenticated-facts",
                "status": "attested_in_fixture",
                "statement": "This ledger contains only committed fixture metadata and no private or authenticated case facts.",
            },
            {
                "id": "no-raw-artifacts",
                "status": "attested_in_fixture",
                "statement": "This ledger contains no raw crawl output, raw PDFs, session files, browser traces, or downloaded documents.",
            },
            {
                "id": "no-credential-automation",
                "status": "attested_in_fixture",
                "statement": "This ledger does not automate credentials, MFA, CAPTCHA, login, or security prompts.",
            },
            {
                "id": "no-outcome-guarantees",
                "status": "attested_in_fixture",
                "statement": "This ledger does not guarantee legal, permitting, approval, issuance, or acceptance outcomes.",
            },
            {
                "id": "no-active-mutation-flags",
                "status": "attested_in_fixture",
                "statement": "This ledger carries no active source, surface-registry, prompt, guardrail, monitoring, release-state, or agent-state mutation flags.",
            },
        ],
    }
    validate_post_briefing_dry_run_authorization_ledger_v2(ledger)
    return ledger


def validate_post_briefing_dry_run_authorization_ledger_v2(ledger: Mapping[str, Any]) -> None:
    """Raise ValueError when a ledger fixture is incomplete or unsafe."""

    errors: list[str] = []
    if ledger.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be post-briefing-dry-run-authorization-ledger")
    if ledger.get("version") != PACKET_VERSION:
        errors.append("version must be v2")
    if ledger.get("mode") != "fixture_first_post_briefing_authorization_review":
        errors.append("mode must remain fixture_first_post_briefing_authorization_review")

    consumed_keys = _field_values(ledger.get("consumes"), "source_key")
    for key in REQUIRED_CONSUMED_KEYS:
        if key not in consumed_keys:
            errors.append(f"consumes missing {key}")

    _validate_authorization_rows(ledger.get("authorization_rows"), errors)
    _validate_signoff_placeholders(ledger.get("reviewer_signoff_placeholders"), "reviewer_signoff_placeholders", errors)
    _validate_signoff_placeholders(ledger.get("operator_signoff_placeholders"), "operator_signoff_placeholders", errors)
    _validate_windows(ledger.get("scope_limited_dry_run_windows"), errors)
    _validate_abort_conditions(ledger.get("independent_abort_conditions"), errors)
    _validate_offline_commands(ledger.get("allowed_offline_validation_commands"), errors)
    _validate_attestations(ledger.get("attestations"), errors)
    _validate_unsafe_content(ledger, errors)

    if errors:
        raise ValueError("invalid post-briefing dry-run authorization ledger v2: " + "; ".join(errors))


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a mapping")
    return value


def _packet_id(packet: Mapping[str, Any]) -> str:
    for key in ("packet_id", "plan_id", "ledger_id", "id"):
        value = packet.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return "unknown-fixture-packet"


def _citations(packet: Mapping[str, Any], fallback: str) -> list[str]:
    for key in ("citations", "citation_refs", "source_evidence_ids", "public_source_ids"):
        value = packet.get(key)
        if isinstance(value, list) and value:
            return [str(item) for item in value]
    return [fallback]


def _consumed_packet_row(source_key: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_key": source_key,
        "packet_id": _packet_id(packet),
        "packet_type": str(packet.get("packet_type", packet.get("mode", "fixture"))),
        "fixture_only": True,
    }


def _authorization_rows(
    briefing: Mapping[str, Any],
    checklist: Mapping[str, Any],
    public_plan: Mapping[str, Any],
    devhub_plan: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "row_id": "row-briefing-go-no-go-reviewed",
            "source_packet_id": _packet_id(briefing),
            "decision": "no_go_pending_reviewer_and_operator_signoff",
            "authorization_effect": "review_only",
            "summary": "Operator briefing is available for cited post-briefing review only.",
            "citations": _citations(briefing, "live dry-run operator briefing packet v2 fixture"),
        },
        {
            "row_id": "row-readiness-checklist-reviewed",
            "source_packet_id": _packet_id(checklist),
            "decision": "no_go_pending_reviewer_and_operator_signoff",
            "authorization_effect": "checklist_review_only",
            "summary": "Readiness checklist prerequisites and blank signoff fields remain reviewer placeholders.",
            "citations": _citations(checklist, "live readiness authorization checklist packet v2 fixture"),
        },
        {
            "row_id": "row-public-plan-window-reviewed",
            "source_packet_id": _packet_id(public_plan),
            "decision": "no_go_live_public_crawl_not_authorized",
            "authorization_effect": "offline_fixture_validation_only",
            "summary": "Public live-dry-run plan fixture may be inspected offline; live crawl and source mutation remain blocked.",
            "citations": _citations(public_plan, "public live dry-run plan fixture v2"),
        },
        {
            "row_id": "row-devhub-plan-window-reviewed",
            "source_packet_id": _packet_id(devhub_plan),
            "decision": "no_go_live_devhub_execution_not_authorized",
            "authorization_effect": "offline_fixture_validation_only",
            "summary": "DevHub live-dry-run plan fixture may be inspected offline; authenticated execution and browser artifacts remain blocked.",
            "citations": _citations(devhub_plan, "DevHub live dry-run plan fixture v2"),
        },
    ]


def _reviewer_signoff_placeholders() -> list[dict[str, Any]]:
    return [
        {
            "field_id": "reviewer_name",
            "role": "ppd_live_readiness_reviewer",
            "blank_value": None,
            "required": True,
            "confirmation_text": "Reviewer confirms cited rows and no-go scope before any separate authorization packet is considered.",
        },
        {
            "field_id": "reviewer_timestamp_utc",
            "role": "ppd_live_readiness_reviewer",
            "blank_value": None,
            "required": True,
            "confirmation_text": "Reviewer timestamp is intentionally blank in the fixture.",
        },
        {
            "field_id": "reviewer_scope_decision",
            "role": "ppd_live_readiness_reviewer",
            "blank_value": None,
            "required": True,
            "confirmation_text": "Reviewer scope decision is intentionally blank and does not authorize live execution.",
        },
    ]


def _operator_signoff_placeholders(checklist: Mapping[str, Any]) -> list[dict[str, Any]]:
    fields = checklist.get("operator_signoff_fields")
    if isinstance(fields, Sequence) and not isinstance(fields, (str, bytes)) and fields:
        placeholders: list[dict[str, Any]] = []
        for item in fields:
            if isinstance(item, Mapping):
                placeholders.append(
                    {
                        "field_id": str(item.get("field_id", "operator_signoff")),
                        "role": "dry_run_operator",
                        "blank_value": None,
                        "required": item.get("required") is True,
                        "confirmation_text": str(item.get("confirmation_text", "Operator signoff remains blank in the fixture.")),
                    }
                )
        if placeholders:
            return placeholders
    return [
        {
            "field_id": "operator_name",
            "role": "dry_run_operator",
            "blank_value": None,
            "required": True,
            "confirmation_text": "Operator signoff remains blank in the fixture.",
        }
    ]


def _scope_limited_windows(public_plan: Mapping[str, Any], devhub_plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "window_id": "public-plan-fixture-window",
            "source_packet_id": _packet_id(public_plan),
            "scope": "offline review of public live-dry-run plan fixture and cited metadata expectations",
            "allowed_start_condition": "reviewer and operator placeholders remain blank until a separate authorization packet exists",
            "allowed_end_condition": "offline fixture validation command completes or any abort condition is encountered",
            "live_execution_allowed": False,
            "citations": _citations(public_plan, "public live dry-run plan fixture v2"),
        },
        {
            "window_id": "devhub-plan-fixture-window",
            "source_packet_id": _packet_id(devhub_plan),
            "scope": "offline review of DevHub read-only live-dry-run plan fixture and safety boundaries",
            "allowed_start_condition": "reviewer and operator placeholders remain blank until a separate authorization packet exists",
            "allowed_end_condition": "offline fixture validation command completes or any abort condition is encountered",
            "live_execution_allowed": False,
            "citations": _citations(devhub_plan, "DevHub live dry-run plan fixture v2"),
        },
    ]


def _independent_abort_conditions(
    briefing: Mapping[str, Any], public_plan: Mapping[str, Any], devhub_plan: Mapping[str, Any]
) -> list[dict[str, Any]]:
    return [
        {
            "condition_id": "abort-if-live-execution-requested",
            "source_packet_ids": [_packet_id(briefing), _packet_id(public_plan), _packet_id(devhub_plan)],
            "trigger": "Any instruction asks the operator or agent to perform a live crawl, live DevHub action, upload, payment, scheduling, cancellation, certification, submission, or filing.",
            "required_response": "Stop and require a new explicit authorization packet.",
            "citations": ["PP&D non-negotiable boundaries fixture policy"],
        },
        {
            "condition_id": "abort-if-auth-state-or-browser-artifact-would-be-created",
            "source_packet_ids": [_packet_id(devhub_plan)],
            "trigger": "Any step would create or store authentication state, screenshots, traces, HAR, recordings, session files, or browser artifacts.",
            "required_response": "Stop and keep the review fixture-only.",
            "citations": _citations(devhub_plan, "DevHub live dry-run plan fixture v2"),
        },
        {
            "condition_id": "abort-if-citation-or-fixture-gap-found",
            "source_packet_ids": [_packet_id(briefing), _packet_id(public_plan), _packet_id(devhub_plan)],
            "trigger": "Any authorization row, dry-run window, or boundary lacks a citation or fixture source.",
            "required_response": "Stop and repair fixtures before review continues.",
            "citations": _citations(briefing, "live dry-run operator briefing packet v2 fixture"),
        },
    ]


def _field_values(items: Any, field_name: str) -> set[str]:
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        return set()
    values: set[str] = set()
    for item in items:
        if isinstance(item, Mapping) and isinstance(item.get(field_name), str):
            values.add(str(item[field_name]))
    return values


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _validate_authorization_rows(rows: Any, errors: list[str]) -> None:
    if not _non_empty_list(rows):
        errors.append("authorization_rows must be a non-empty list")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"authorization_rows[{index}] must be an object")
            continue
        if not str(row.get("row_id", "")).strip():
            errors.append(f"authorization_rows[{index}] missing row_id")
        if not str(row.get("decision", "")).startswith("no_go"):
            errors.append(f"authorization_rows[{index}] decision must remain no_go")
        if row.get("authorization_effect") not in {"review_only", "checklist_review_only", "offline_fixture_validation_only"}:
            errors.append(f"authorization_rows[{index}] has unsupported authorization_effect")
        if not _non_empty_list(row.get("citations")) or not all(str(item).strip() for item in row.get("citations", [])):
            errors.append(f"authorization_rows[{index}] must include citations")
        _validate_text_safety(row, f"authorization_rows[{index}]", errors)


def _validate_signoff_placeholders(items: Any, field_name: str, errors: list[str]) -> None:
    if not _non_empty_list(items):
        errors.append(f"{field_name} must be a non-empty list")
        return
    required_count = 0
    field_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            errors.append(f"{field_name}[{index}] must be an object")
            continue
        field_id = str(item.get("field_id", "")).strip()
        if field_id:
            field_ids.add(field_id)
        else:
            errors.append(f"{field_name}[{index}] missing field_id")
        if item.get("required") is True:
            required_count += 1
        if item.get("blank_value") not in (None, ""):
            errors.append(f"{field_name}[{index}] must keep blank_value empty")
        if not str(item.get("confirmation_text", "")).strip():
            errors.append(f"{field_name}[{index}] missing confirmation_text")
    if required_count == 0:
        errors.append(f"{field_name} must include at least one required placeholder")
    if field_name == "reviewer_signoff_placeholders":
        missing = _REQUIRED_REVIEWER_PLACEHOLDER_IDS.difference(field_ids)
        if missing:
            errors.append("reviewer_signoff_placeholders missing required placeholders: " + ", ".join(sorted(missing)))
    if field_name == "operator_signoff_placeholders":
        missing = _REQUIRED_OPERATOR_PLACEHOLDER_IDS.difference(field_ids)
        if missing:
            errors.append("operator_signoff_placeholders missing required placeholders: " + ", ".join(sorted(missing)))


def _validate_windows(windows: Any, errors: list[str]) -> None:
    if not _non_empty_list(windows):
        errors.append("scope_limited_dry_run_windows must be a non-empty list")
        return
    for index, window in enumerate(windows):
        if not isinstance(window, Mapping):
            errors.append(f"scope_limited_dry_run_windows[{index}] must be an object")
            continue
        if window.get("live_execution_allowed") is not False:
            errors.append(f"scope_limited_dry_run_windows[{index}] must not allow live execution")
        for field_name in ("window_id", "scope", "allowed_start_condition", "allowed_end_condition"):
            if not str(window.get(field_name, "")).strip():
                errors.append(f"scope_limited_dry_run_windows[{index}] missing {field_name}")
        if not _non_empty_list(window.get("citations")):
            errors.append(f"scope_limited_dry_run_windows[{index}] must include citations")
        _validate_text_safety(window, f"scope_limited_dry_run_windows[{index}]", errors)


def _validate_abort_conditions(conditions: Any, errors: list[str]) -> None:
    if not _non_empty_list(conditions):
        errors.append("independent_abort_conditions must be a non-empty list")
        return
    for index, condition in enumerate(conditions):
        if not isinstance(condition, Mapping):
            errors.append(f"independent_abort_conditions[{index}] must be an object")
            continue
        for field_name in ("condition_id", "trigger", "required_response"):
            if not str(condition.get(field_name, "")).strip():
                errors.append(f"independent_abort_conditions[{index}] missing {field_name}")
        if not _non_empty_list(condition.get("citations")):
            errors.append(f"independent_abort_conditions[{index}] must include citations")
        _validate_text_safety(condition, f"independent_abort_conditions[{index}]", errors)


def _validate_offline_commands(commands: Any, errors: list[str]) -> None:
    if not _non_empty_list(commands):
        errors.append("allowed_offline_validation_commands must be a non-empty list")
        return
    for index, command in enumerate(commands):
        if not isinstance(command, list) or not all(isinstance(part, str) and part for part in command):
            errors.append(f"allowed_offline_validation_commands[{index}] must be an argv list of non-empty strings")
            continue
        command_tuple = tuple(command)
        if command_tuple not in _ALLOWED_OFFLINE_COMMAND_PREFIXES:
            errors.append(f"allowed_offline_validation_commands[{index}] is not an allowed offline fixture command")
        lowered_parts = {part.lower() for part in command}
        if lowered_parts.intersection(_FORBIDDEN_COMMAND_TOKENS):
            errors.append(f"allowed_offline_validation_commands[{index}] contains a forbidden live-operation token")


def _validate_attestations(attestations: Any, errors: list[str]) -> None:
    if not _non_empty_list(attestations):
        errors.append("attestations must be a non-empty list")
        return
    attestation_ids = _field_values(attestations, "id")
    missing = REQUIRED_ATTESTATION_IDS.difference(attestation_ids)
    if missing:
        errors.append("missing attestations: " + ", ".join(sorted(missing)))
    for index, attestation in enumerate(attestations):
        if not isinstance(attestation, Mapping):
            errors.append(f"attestations[{index}] must be an object")
            continue
        if attestation.get("status") != "attested_in_fixture":
            errors.append(f"attestations[{index}] must be attested_in_fixture")
        if not str(attestation.get("statement", "")).strip():
            errors.append(f"attestations[{index}] missing statement")


def _validate_unsafe_content(value: Any, errors: list[str]) -> None:
    for path, leaf in _walk(value):
        if isinstance(leaf, str):
            _validate_text_safety(leaf, path, errors)
        elif isinstance(leaf, bool) and leaf is True and _MUTATION_KEY_RE.search(path):
            errors.append(f"{path} contains active source/surface/prompt/guardrail/monitoring/release/agent mutation flag")
        elif isinstance(leaf, str) and leaf.lower() in {"active", "enabled", "true"} and _MUTATION_KEY_RE.search(path):
            errors.append(f"{path} contains active source/surface/prompt/guardrail/monitoring/release/agent mutation flag")


def _validate_text_safety(value: Any, path: str, errors: list[str]) -> None:
    texts = [value] if isinstance(value, str) else [leaf for _, leaf in _walk(value) if isinstance(leaf, str)]
    for text in texts:
        if _PRIVATE_OR_AUTHENTICATED_FACT_RE.search(text) and not _is_negated_safety_text(text):
            errors.append(f"{path} contains private or authenticated fact language")
        if _RAW_ARTIFACT_RE.search(text) and not _is_negated_safety_text(text):
            errors.append(f"{path} contains raw crawl/PDF/session/browser artifact language")
        if _CREDENTIAL_AUTOMATION_RE.search(text) and not _is_negated_safety_text(text):
            errors.append(f"{path} contains credential, MFA, CAPTCHA, or login automation language")
        if _OUTCOME_GUARANTEE_RE.search(text) and not _is_negated_safety_text(text):
            errors.append(f"{path} contains legal or permitting outcome guarantee language")
        if _LIVE_OR_COMPLETION_CLAIM_RE.search(text) and not _is_negated_safety_text(text):
            errors.append(f"{path} contains live execution or completion claim language")
        if _FINAL_OFFICIAL_ACTION_RE.search(text) and not _is_negated_safety_text(text):
            errors.append(f"{path} contains final submission/payment/upload/scheduling/cancellation language")
        if _MUTATION_FLAG_RE.search(text) and not _is_negated_safety_text(text):
            errors.append(f"{path} contains active source/surface/prompt/guardrail/monitoring/release/agent mutation language")


def _is_negated_safety_text(text: str) -> bool:
    return bool(_NEGATED_SAFETY_RE.search(text[:140]))


def _walk(value: Any, prefix: str = "ledger") -> list[tuple[str, Any]]:
    if isinstance(value, Mapping):
        leaves: list[tuple[str, Any]] = []
        for key, child in value.items():
            leaves.extend(_walk(child, f"{prefix}.{key}"))
        return leaves
    if isinstance(value, list):
        leaves = []
        for index, child in enumerate(value):
            leaves.extend(_walk(child, f"{prefix}[{index}]"))
        return leaves
    return [(prefix, value)]


__all__ = [
    "PACKET_TYPE",
    "PACKET_VERSION",
    "REQUIRED_ATTESTATION_IDS",
    "REQUIRED_CONSUMED_KEYS",
    "build_post_briefing_dry_run_authorization_ledger_v2",
    "load_fixture_packet",
    "validate_post_briefing_dry_run_authorization_ledger_v2",
]
