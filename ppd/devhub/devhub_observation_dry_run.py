"""Fixture-first DevHub read-only observation dry-run manifest v1.

This module is intentionally offline-only. It consumes a redacted attended
observation preflight packet and emits ordered synthetic observation steps for
review and validation. It never opens DevHub, drives a browser, or stores live
session artifacts.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

MANIFEST_SCHEMA_VERSION = "devhub_read_only_observation_dry_run_manifest_v1"
PREFLIGHT_SCHEMA_VERSION = "devhub_attended_observation_preflight_packet_v1"

SAFE_READ_ONLY_ACTION_REFS = {
    "view_home": "read_only:view_devhub_home",
    "review_permits_requests": "read_only:review_my_permits_and_requests",
    "review_permit_detail": "read_only:review_permit_detail",
    "review_status_messages": "read_only:review_status_messages",
    "review_fee_notice": "read_only:review_fee_notice_without_payment",
    "review_correction_request": "read_only:review_correction_request_without_upload",
    "review_attachment_list": "read_only:review_attachment_list_without_download",
    "review_inspection_results": "read_only:review_inspection_results_without_scheduling",
}

FORBIDDEN_ARTIFACT_KINDS = (
    "auth_state",
    "browser_profile",
    "cookies",
    "credentials",
    "downloaded_documents",
    "har",
    "private_page_values",
    "raw_authenticated_html",
    "screenshots",
    "session_storage",
    "traces",
)

STOP_CHECKPOINTS = [
    {
        "checkpoint_id": "stop_before_auth_boundary",
        "when": "Any login, MFA, CAPTCHA, account creation, password recovery, or credential prompt is visible.",
        "required_response": "Stop and return manual handoff; do not automate or store credentials/session state.",
    },
    {
        "checkpoint_id": "stop_before_private_value_capture",
        "when": "A page contains account, permit, address, owner, contractor, financial, uploaded-document, or other private values.",
        "required_response": "Capture accessible role/name/state metadata only; redact values and leave reviewer placeholders.",
    },
    {
        "checkpoint_id": "stop_before_reversible_draft_action",
        "when": "The next interaction would type, select, save, stage, upload, or otherwise mutate a draft.",
        "required_response": "Classify as reversible draft, require separate attended plan, and do not execute in this dry run.",
    },
    {
        "checkpoint_id": "stop_before_official_action",
        "when": "The next interaction would submit, certify, pay, purchase, schedule, cancel, withdraw, upload to record, or request official change.",
        "required_response": "Classify as consequential official and refuse automation without explicit separate guardrail flow.",
    },
]

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_observation_dry_run.py"],
]

_REQUIRED_MANIFEST_KEYS = (
    "synthetic_observation_steps",
    "redacted_field_inventory_placeholders",
    "manual_stop_checkpoints",
    "reviewer_observation_placeholders",
    "offline_validation_commands",
)

_REQUIRED_STEP_KEYS = (
    "expected_accessible_role_capture_fields",
    "read_only_action_classification_refs",
    "manual_stop_checkpoint_refs",
    "reviewer_observation_placeholder",
)

_REQUIRED_CAPTURE_KEYS = (
    "field_key",
    "expected_accessible_role",
    "expected_accessible_name",
    "capture_policy",
    "private_value_placeholder",
)

_REQUIRED_REDACTION_KEYS = (
    "field_key",
    "redaction_reason",
    "value_status",
    "stored_value",
)

_REQUIRED_REVIEWER_KEYS = (
    "surface_id",
    "step_id",
    "review_status",
    "reviewer_notes",
)

_REQUIRED_STOP_IDS = tuple(checkpoint["checkpoint_id"] for checkpoint in STOP_CHECKPOINTS)

_PRIVATE_OR_ARTIFACT_KEY_RE = re.compile(
    r"(^|_)(auth|auth_state|browser_profile|browser_state|cookie|cookies|credential|credentials|har|har_path|password|private_page_values|raw_authenticated_html|screen_?shots?|session|session_storage|storage_state|token|trace|traces|trace_path)($|_)",
    re.IGNORECASE,
)

_PRIVATE_VALUE_RE = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|"
    r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b|"
    r"\b\d{3,6}\s+(?:N|NE|NW|S|SE|SW|E|W)\s+[A-Z][A-Z0-9 ]+\b|"
    r"\b(?:permit|invoice|account|license)\s*(?:number|no\.|#)?\s*[:#]\s*[A-Z0-9-]{4,}\b",
    re.IGNORECASE,
)

_ARTIFACT_REFERENCE_RE = re.compile(
    r"\b(stored screenshot|attached screenshot|screenshot path|browser trace|playwright trace|har file|\.har\b|auth state|storage state|session state|cookie jar|cookies\.json|trace\.zip|playwright/.auth)\b",
    re.IGNORECASE,
)

_LIVE_DEVHUB_CLAIM_RE = re.compile(
    r"\b(opened|launched|ran|executed|clicked|filled|captured|stored|navigated|visited)\b.{0,80}\b(live devhub|live browser|playwright|browser session|authenticated devhub)\b|"
    r"\b(live devhub|live browser|playwright|browser session|authenticated devhub)\b.{0,80}\b(opened|launched|ran|executed|clicked|filled|captured|stored|navigated|visited)\b",
    re.IGNORECASE,
)

_CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(click|clicked|continue|continued|execute|executed|fill|filled|press|pressed|select|selected|start|started|trigger|triggered|use|used|enable|enabled|allow|allowed)\b.{0,80}\b(submit|submission|upload|certif|pay|payment|purchase|schedule|cancel|withdraw|reactivat|attach)\b|"
    r"\b(submit|submission|upload|certif|pay|payment|purchase|schedule|cancel|withdraw|reactivat|attach)\b.{0,80}\b(allowed|complete|completed|done|enabled|executed|proceed|started|successful|triggered)\b",
    re.IGNORECASE,
)

_NEGATION_MARKERS = (
    "do not",
    "does not",
    "must not",
    "may not",
    "not allowed",
    "not attach",
    "without",
    "no ",
    "stop before",
    "reject",
    "refuse",
)

_ACTIVE_MUTATION_DOMAINS = (
    "surface",
    "surface_registry",
    "guardrail",
    "prompt",
    "release_state",
    "devhub",
)

_ACTIVE_MUTATION_TERMS = ("active", "mutation", "mutates", "write", "update", "promote", "publish")

_ALLOWED_PROHIBITION_PATH_SUFFIXES = (
    ".forbidden_artifact_kinds",
    ".evidence_policy",
    ".capture_policy",
    ".navigation_policy",
    ".required_response",
)


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from a fixture path."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def validate_preflight_packet(packet: dict[str, Any]) -> None:
    """Validate the narrow preflight packet contract used by this dry run."""
    if packet.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        raise ValueError("Unsupported DevHub attended observation preflight packet schema_version")
    if packet.get("mode") != "offline_fixture_only":
        raise ValueError("Preflight packet must declare offline_fixture_only mode")
    if packet.get("devhub_opened") is not False:
        raise ValueError("Preflight packet must state that DevHub was not opened")
    if packet.get("stores_session_or_browser_artifacts") is not False:
        raise ValueError("Preflight packet must not store session or browser artifacts")

    surfaces = packet.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        raise ValueError("Preflight packet must include at least one surface")

    for index, surface in enumerate(surfaces, start=1):
        if not isinstance(surface, dict):
            raise ValueError(f"Surface {index} must be an object")
        if not surface.get("surface_id"):
            raise ValueError(f"Surface {index} is missing surface_id")
        if surface.get("auth_scope") != "authenticated_attended_redacted":
            raise ValueError(f"Surface {surface.get('surface_id')} must use authenticated_attended_redacted auth_scope")
        actions = surface.get("read_only_action_keys")
        if not isinstance(actions, list) or not actions:
            raise ValueError(f"Surface {surface.get('surface_id')} must include read_only_action_keys")
        unknown = [action for action in actions if action not in SAFE_READ_ONLY_ACTION_REFS]
        if unknown:
            raise ValueError(f"Unknown read-only action keys for {surface.get('surface_id')}: {unknown}")


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    """Reject incomplete or unsafe DevHub read-only observation dry-run manifests."""
    errors: list[str] = []

    if not isinstance(manifest, Mapping):
        raise ValueError("manifest must be a JSON object")

    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(f"schema_version must be {MANIFEST_SCHEMA_VERSION}")
    if manifest.get("mode") != "offline_fixture_only":
        errors.append("mode must be offline_fixture_only")
    for key in (
        "devhub_opened",
        "browser_or_session_artifacts_created",
        "prompt_changes_allowed",
        "official_actions_allowed",
    ):
        if manifest.get(key) is not False:
            errors.append(f"{key} must be false")

    for key in _REQUIRED_MANIFEST_KEYS:
        if key not in manifest:
            errors.append(f"{key} is required")

    _validate_required_manifest_sections(manifest, errors)
    _scan_for_prohibited_content(manifest, "$", errors)

    if errors:
        raise ValueError("invalid DevHub read-only observation dry-run manifest v1: " + "; ".join(errors))


def _validate_required_manifest_sections(manifest: Mapping[str, Any], errors: list[str]) -> None:
    steps = _sequence(manifest.get("synthetic_observation_steps"))
    if not steps:
        errors.append("synthetic_observation_steps must be non-empty")

    redacted_inventory = _sequence(manifest.get("redacted_field_inventory_placeholders"))
    if not redacted_inventory:
        errors.append("redacted_field_inventory_placeholders must be non-empty")

    reviewer_placeholders = _sequence(manifest.get("reviewer_observation_placeholders"))
    if not reviewer_placeholders:
        errors.append("reviewer_observation_placeholders must be non-empty")

    stop_checkpoints = _sequence(manifest.get("manual_stop_checkpoints"))
    stop_ids = [str(_mapping(item).get("checkpoint_id", "")) for item in stop_checkpoints]
    if tuple(stop_ids) != _REQUIRED_STOP_IDS:
        errors.append("manual_stop_checkpoints must include every required checkpoint in order")

    if manifest.get("offline_validation_commands") != OFFLINE_VALIDATION_COMMANDS:
        errors.append("offline_validation_commands must include the expected deterministic validation commands")

    forbidden = set(_sequence(manifest.get("forbidden_artifact_kinds")))
    missing_forbidden = set(FORBIDDEN_ARTIFACT_KINDS) - forbidden
    if missing_forbidden:
        errors.append(f"forbidden_artifact_kinds missing {sorted(missing_forbidden)}")

    capture_field_keys: list[str] = []
    step_refs: list[tuple[str, str]] = []
    for index, raw_step in enumerate(steps):
        step = _mapping(raw_step)
        prefix = f"synthetic_observation_steps[{index}]"
        for key in _REQUIRED_STEP_KEYS:
            if key not in step:
                errors.append(f"{prefix}.{key} is required")

        if step.get("auth_scope") != "authenticated_attended_redacted":
            errors.append(f"{prefix}.auth_scope must be authenticated_attended_redacted")
        if step.get("navigation_policy") != "manual_attended_only_no_browser_launched_by_dry_run":
            errors.append(f"{prefix}.navigation_policy must keep the dry run manual and offline")

        refs = _sequence(step.get("read_only_action_classification_refs"))
        if not refs:
            errors.append(f"{prefix}.read_only_action_classification_refs must be non-empty")
        for ref in refs:
            if not isinstance(ref, str) or not ref.startswith("read_only:"):
                errors.append(f"{prefix}.read_only_action_classification_refs must contain only read_only references")

        if tuple(_sequence(step.get("manual_stop_checkpoint_refs"))) != _REQUIRED_STOP_IDS:
            errors.append(f"{prefix}.manual_stop_checkpoint_refs must include every required stop checkpoint in order")

        captures = _sequence(step.get("expected_accessible_role_capture_fields"))
        if not captures:
            errors.append(f"{prefix}.expected_accessible_role_capture_fields must be non-empty")
        for capture_index, raw_capture in enumerate(captures):
            capture = _mapping(raw_capture)
            capture_prefix = f"{prefix}.expected_accessible_role_capture_fields[{capture_index}]"
            for key in _REQUIRED_CAPTURE_KEYS:
                if not capture.get(key):
                    errors.append(f"{capture_prefix}.{key} is required")
            if capture.get("private_value_placeholder") != "REDACTED_NOT_CAPTURED":
                errors.append(f"{capture_prefix}.private_value_placeholder must be REDACTED_NOT_CAPTURED")
            if capture.get("observed_accessible_role") is not None:
                errors.append(f"{capture_prefix}.observed_accessible_role must remain a placeholder")
            if capture.get("observed_accessible_name") is not None:
                errors.append(f"{capture_prefix}.observed_accessible_name must remain a placeholder")
            if capture.get("observed_state_placeholder") is not None:
                errors.append(f"{capture_prefix}.observed_state_placeholder must remain a placeholder")
            field_key = capture.get("field_key")
            if isinstance(field_key, str):
                capture_field_keys.append(field_key)

        reviewer = _mapping(step.get("reviewer_observation_placeholder"))
        if reviewer.get("observed") is not False:
            errors.append(f"{prefix}.reviewer_observation_placeholder.observed must be false")
        if reviewer.get("reviewer") is not None:
            errors.append(f"{prefix}.reviewer_observation_placeholder.reviewer must remain a placeholder")
        if reviewer.get("observed_at") is not None:
            errors.append(f"{prefix}.reviewer_observation_placeholder.observed_at must remain a placeholder")
        if not reviewer.get("evidence_policy"):
            errors.append(f"{prefix}.reviewer_observation_placeholder.evidence_policy is required")

        surface_id = step.get("surface_id")
        step_id = step.get("step_id")
        if isinstance(surface_id, str) and isinstance(step_id, str):
            step_refs.append((surface_id, step_id))

    inventory_keys: list[str] = []
    for index, raw_item in enumerate(redacted_inventory):
        item = _mapping(raw_item)
        prefix = f"redacted_field_inventory_placeholders[{index}]"
        for key in _REQUIRED_REDACTION_KEYS:
            if key not in item:
                errors.append(f"{prefix}.{key} is required")
        if item.get("value_status") != "placeholder_only_not_observed":
            errors.append(f"{prefix}.value_status must be placeholder_only_not_observed")
        if item.get("stored_value") is not None:
            errors.append(f"{prefix}.stored_value must be null")
        field_key = item.get("field_key")
        if isinstance(field_key, str):
            inventory_keys.append(field_key)

    if capture_field_keys and inventory_keys and sorted(capture_field_keys) != sorted(inventory_keys):
        errors.append("redacted_field_inventory_placeholders must cover every expected accessible capture field")

    reviewer_refs: list[tuple[str, str]] = []
    for index, raw_item in enumerate(reviewer_placeholders):
        item = _mapping(raw_item)
        prefix = f"reviewer_observation_placeholders[{index}]"
        for key in _REQUIRED_REVIEWER_KEYS:
            if key not in item:
                errors.append(f"{prefix}.{key} is required")
        if item.get("review_status") != "not_observed_fixture_placeholder":
            errors.append(f"{prefix}.review_status must be not_observed_fixture_placeholder")
        if item.get("reviewer_notes") is not None:
            errors.append(f"{prefix}.reviewer_notes must remain a placeholder")
        surface_id = item.get("surface_id")
        step_id = item.get("step_id")
        if isinstance(surface_id, str) and isinstance(step_id, str):
            reviewer_refs.append((surface_id, step_id))

    if step_refs and reviewer_refs and step_refs != reviewer_refs:
        errors.append("reviewer_observation_placeholders must match synthetic observation steps in order")


def _field_capture(field: dict[str, Any]) -> dict[str, Any]:
    role = field.get("expected_accessible_role")
    label = field.get("expected_accessible_name")
    if not role or not label:
        raise ValueError("Each expected field must include expected_accessible_role and expected_accessible_name")
    return {
        "field_key": field.get("field_key"),
        "expected_accessible_role": role,
        "expected_accessible_name": label,
        "capture_policy": "record role/name/state only; never record private value",
        "observed_accessible_role": None,
        "observed_accessible_name": None,
        "observed_state_placeholder": None,
        "private_value_placeholder": "REDACTED_NOT_CAPTURED",
        "reviewer_notes": None,
    }


def _redaction_placeholder(field: dict[str, Any]) -> dict[str, Any]:
    return {
        "field_key": field.get("field_key"),
        "redaction_reason": field.get("redaction_reason", "private_or_account_scoped_devhub_value"),
        "value_status": "placeholder_only_not_observed",
        "stored_value": None,
    }


def build_manifest(packet: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic read-only observation dry-run manifest."""
    validate_preflight_packet(packet)

    steps = []
    redacted_inventory = []
    sequence = 1

    for surface in packet["surfaces"]:
        fields = surface.get("expected_accessible_fields", [])
        if not isinstance(fields, list):
            raise ValueError(f"Surface {surface.get('surface_id')} expected_accessible_fields must be a list")

        field_captures = [_field_capture(field) for field in fields]
        redacted_inventory.extend(_redaction_placeholder(field) for field in fields)

        steps.append(
            {
                "step_id": f"synthetic_observation_step_{sequence:02d}",
                "surface_id": surface["surface_id"],
                "surface_label": surface.get("surface_label"),
                "auth_scope": surface["auth_scope"],
                "synthetic_sequence": sequence,
                "navigation_policy": "manual_attended_only_no_browser_launched_by_dry_run",
                "observation_goal": surface.get("observation_goal"),
                "expected_landmarks": deepcopy(surface.get("expected_landmarks", [])),
                "expected_accessible_role_capture_fields": field_captures,
                "read_only_action_classification_refs": [
                    SAFE_READ_ONLY_ACTION_REFS[action_key]
                    for action_key in surface["read_only_action_keys"]
                ],
                "manual_stop_checkpoint_refs": [checkpoint["checkpoint_id"] for checkpoint in STOP_CHECKPOINTS],
                "reviewer_observation_placeholder": {
                    "observed": False,
                    "reviewer": None,
                    "observed_at": None,
                    "notes": None,
                    "evidence_policy": "Do not attach screenshots, traces, HAR files, raw HTML, private values, or downloaded documents.",
                },
            }
        )
        sequence += 1

    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "manifest_id": packet["packet_id"].replace("preflight_packet", "dry_run_manifest"),
        "source_preflight_packet_id": packet["packet_id"],
        "mode": "offline_fixture_only",
        "devhub_opened": False,
        "browser_or_session_artifacts_created": False,
        "prompt_changes_allowed": False,
        "official_actions_allowed": False,
        "forbidden_artifact_kinds": list(FORBIDDEN_ARTIFACT_KINDS),
        "synthetic_observation_steps": steps,
        "redacted_field_inventory_placeholders": redacted_inventory,
        "manual_stop_checkpoints": deepcopy(STOP_CHECKPOINTS),
        "reviewer_observation_placeholders": [
            {
                "surface_id": step["surface_id"],
                "step_id": step["step_id"],
                "review_status": "not_observed_fixture_placeholder",
                "reviewer_notes": None,
            }
            for step in steps
        ],
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
    }
    validate_manifest(manifest)
    return manifest


def manifest_to_json(manifest: dict[str, Any]) -> str:
    """Serialize manifest deterministically for fixture comparison."""
    validate_manifest(manifest)
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def _scan_for_prohibited_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized_key = _normalize_key(key_text)
            if _forbidden_key_present(normalized_key, child, child_path):
                errors.append(f"{child_path} must not contain credentials, session, auth, browser, screenshot, trace, HAR, or private page artifacts")
            if _active_mutation_flag(normalized_key, child):
                errors.append(f"{child_path} must not enable active surface, guardrail, prompt, release-state, or DevHub mutation")
            _scan_for_prohibited_content(child, child_path, errors)
        return

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_for_prohibited_content(child, f"{path}[{index}]", errors)
        return

    if isinstance(value, str):
        _scan_text(value, path, errors)


def _scan_text(value: str, path: str, errors: list[str]) -> None:
    if _is_allowed_prohibition_path(path):
        return
    if _PRIVATE_VALUE_RE.search(value):
        errors.append(f"{path} must not contain private DevHub page values")
    if _ARTIFACT_REFERENCE_RE.search(value):
        errors.append(f"{path} must not reference screenshots, traces, HAR files, auth state, storage state, cookies, or session artifacts")
    if _LIVE_DEVHUB_CLAIM_RE.search(value):
        errors.append(f"{path} must not claim live DevHub access, live browser execution, or authenticated capture")
    if _CONSEQUENTIAL_ACTION_RE.search(value) and not _has_negation_before_match(value, _CONSEQUENTIAL_ACTION_RE):
        errors.append(f"{path} must not enable payment, submission, scheduling, cancellation, certification, upload, or other official action language")


def _forbidden_key_present(normalized_key: str, child: Any, path: str) -> bool:
    if normalized_key in {"forbidden_artifact_kinds", "private_value_placeholder"}:
        return False
    if path.endswith(".evidence_policy") or path.endswith(".redaction_reason") or path.endswith(".capture_policy"):
        return False
    return bool(_PRIVATE_OR_ARTIFACT_KEY_RE.search(normalized_key) and _is_present(child))


def _active_mutation_flag(normalized_key: str, child: Any) -> bool:
    if normalized_key.startswith("no_") or not _is_truthy(child):
        return False
    return any(domain in normalized_key for domain in _ACTIVE_MUTATION_DOMAINS) and any(
        term in normalized_key for term in _ACTIVE_MUTATION_TERMS
    )


def _has_negation_before_match(value: str, pattern: re.Pattern[str]) -> bool:
    match = pattern.search(value)
    if not match:
        return False
    prefix = value[max(0, match.start() - 80) : match.start()].lower()
    return any(marker in prefix for marker in _NEGATION_MARKERS)


def _is_allowed_prohibition_path(path: str) -> bool:
    return any(path.endswith(suffix) for suffix in _ALLOWED_PROHIBITION_PATH_SUFFIXES)


def _is_truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "enabled", "active", "allowed"}
    return False


def _is_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip() not in {"REDACTED_NOT_CAPTURED", "[REDACTED]", "[NOT_STORED]"}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return []


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")
