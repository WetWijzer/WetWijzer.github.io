"""Fixture-first live-readiness gate review packet v2.

This module consumes committed review fixtures only. It does not crawl public
sources, open DevHub, launch a browser, read or write auth state, create browser
artifacts, invoke processors, or perform official PP&D actions. The packet it
builds is a cited preflight-only review artifact for human operators.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.crawler.public_recrawl_operator_packet_v2 import validate_public_recrawl_operator_packet_v2
from ppd.devhub.attended_readonly_runbook_refresh_packet_v2 import (
    validate_devhub_attended_readonly_runbook_refresh_packet_v2,
)
from ppd.release.offline_safe_assist_rc_v2 import validate_release_candidate_packet

REQUIRED_ATTESTATIONS = {
    "no_live_crawl": True,
    "no_live_devhub": True,
    "no_auth_state": True,
    "no_browser_artifact": True,
    "no_official_action": True,
}

MUTATION_FLAGS = {
    "source_mutation_active": False,
    "schedule_mutation_active": False,
    "surface_registry_mutation_active": False,
    "prompt_mutation_active": False,
    "monitoring_mutation_active": False,
    "release_state_mutation_active": False,
    "agent_state_mutation_active": False,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ["python3", "-m", "pytest", "ppd/tests/test_live_readiness_gate_review_packet_v2.py"],
]

DISALLOWED_ACTIONS = [
    "public crawl run",
    "processor invocation",
    "DevHub browser launch",
    "DevHub account-scoped read",
    "identity challenge automation",
    "auth state creation, reading, or storage",
    "browser artifact capture",
    "permit submission",
    "acknowledgement or certification",
    "official attachment",
    "fee payment or purchase",
    "inspection scheduling",
    "permit cancellation or withdrawal",
]

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

BROWSER_OR_SESSION_ARTIFACT_KEYS = {
    "browser_trace",
    "har",
    "screenshot",
    "session_artifact",
    "trace",
    "trace_file",
    "trace_zip",
}

LIVE_ARTIFACT_KEYS = {
    "archive_artifact_ref",
    "crawl_output",
    "downloaded_document",
    "processor_output",
    "raw_body",
    "raw_crawl",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
}

MUTATION_KEYS = set(MUTATION_FLAGS) | {
    "active_agent_state_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_schedule_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation_enabled",
    "apply_schedule_update",
    "commit_to_registry",
    "monitoring_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "schedule_mutation_enabled",
    "source_mutation_enabled",
    "surface_registry_mutation_enabled",
    "write_active_agent_state",
    "write_active_monitoring",
    "write_active_prompt",
    "write_active_release_state",
    "write_active_schedule",
    "write_active_source",
    "write_active_registry",
}

PRIVATE_OR_ARTIFACT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|(^[A-Za-z]:\\Users\\[^\\]+\\)|"
    r"(auth[_-]?state|browser[_-]?state|cookie|credential|har|password|private[_-]?fact|raw[_-]?(body|crawl|html|pdf)|"
    r"session[_-]?(artifact|cookie|state)?|screenshot|secret|storage[_-]?state|token|trace\.(zip|json))",
    re.IGNORECASE,
)

LIVE_EXECUTION_CLAIM_RE = re.compile(
    r"\b("
    r"(performed|completed|executed|ran|started|launched|opened)\s+(a\s+)?(live\s+)?(crawl|devhub|browser|llm|processor)|"
    r"live\s+(crawl|devhub|browser|llm|processor)\s+(completed|executed|ran|succeeded|was\s+performed)|"
    r"called\s+(an?\s+)?llm|used\s+(live\s+)?devhub|used\s+(live\s+)?browser|processor\s+(completed|ran|executed)"
    r")\b",
    re.IGNORECASE,
)

IDENTITY_AUTOMATION_RE = re.compile(
    r"\b("
    r"(automate|automated|bypass|solve|handled|complete|completed)\s+(credentials?|mfa|captcha|login|password)|"
    r"(credentials?|mfa|captcha|login|password)\s+(automation|bypass|solver|handled\s+automatically|completed\s+automatically)"
    r")\b",
    re.IGNORECASE,
)

OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?\s+(approval|issuance|permit|legal|compliance|outcome)|"
    r"(permit|application|inspection|appeal)\s+(will|shall)\s+be\s+(approved|issued|accepted|granted|upheld)|"
    r"legally\s+guaranteed|guaranteed\s+code\s+compliance)\b",
    re.IGNORECASE,
)

OFFICIAL_ACTION_ENABLEMENT_RE = re.compile(
    r"\b("
    r"official\s+action\s+(enabled|allowed|authorized|ready)|"
    r"(submission|certification|upload|payment|purchase|scheduling|cancellation|withdrawal)\s+(enabled|allowed|authorized|ready|complete|completed|succeeded)|"
    r"agent\s+(may|can|is\s+authorized\s+to)\s+(submit|certify|upload|pay|purchase|schedule|cancel|withdraw)|"
    r"(submitted|uploaded|paid|scheduled|cancelled|canceled)\s+(to|in|through|on)\s+(devhub|official|the\s+city|pp&d)"
    r")\b",
    re.IGNORECASE,
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def build_from_fixture_path(path: Path) -> dict[str, Any]:
    fixture = load_json(path)
    return build_live_readiness_gate_review_packet_v2(
        _require_mapping(fixture.get("public_recrawl_operator_packet_v2"), "public_recrawl_operator_packet_v2"),
        _require_mapping(
            fixture.get("devhub_attended_readonly_runbook_refresh_packet_v2"),
            "devhub_attended_readonly_runbook_refresh_packet_v2",
        ),
        _require_mapping(fixture.get("offline_safe_assist_release_candidate_packet_v2"), "offline_safe_assist_release_candidate_packet_v2"),
    )


def build_live_readiness_gate_review_packet_v2(
    public_recrawl_operator_packet_v2: Mapping[str, Any],
    devhub_attended_readonly_runbook_refresh_packet_v2: Mapping[str, Any],
    offline_safe_assist_release_candidate_packet_v2: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic preflight-only live-readiness gate review packet."""

    recrawl_issues = validate_public_recrawl_operator_packet_v2(public_recrawl_operator_packet_v2)
    if recrawl_issues:
        details = "; ".join(f"{issue.code} at {issue.path}" for issue in recrawl_issues)
        raise ValueError("invalid public recrawl operator packet v2: " + details)
    validate_devhub_attended_readonly_runbook_refresh_packet_v2(devhub_attended_readonly_runbook_refresh_packet_v2)
    rc_result = validate_release_candidate_packet(offline_safe_assist_release_candidate_packet_v2)
    if not rc_result.valid:
        raise ValueError("invalid offline safe-assist release candidate packet v2: " + "; ".join(rc_result.problems))

    citations = _source_citations(
        public_recrawl_operator_packet_v2,
        devhub_attended_readonly_runbook_refresh_packet_v2,
        offline_safe_assist_release_candidate_packet_v2,
    )
    packet = {
        "packet_type": "live_readiness_gate_review_packet_v2",
        "packet_version": 2,
        "packet_id": "live-readiness-gate-review-packet-v2-fixture-20260529",
        "mode": "fixture_first_preflight_only_gate_review",
        "consumes": {
            "public_recrawl_operator_packet_v2": _require_string(
                public_recrawl_operator_packet_v2.get("packet_id") or public_recrawl_operator_packet_v2.get("packetId"),
                "public recrawl packet id",
            ),
            "devhub_attended_readonly_runbook_refresh_packet_v2": _require_string(
                devhub_attended_readonly_runbook_refresh_packet_v2.get("packet_id"),
                "DevHub runbook refresh packet id",
            ),
            "offline_safe_assist_release_candidate_packet_v2": _require_string(
                offline_safe_assist_release_candidate_packet_v2.get("packet_id"),
                "offline safe-assist RC packet id",
            ),
        },
        "readiness_decisions": _readiness_decisions(citations),
        "required_human_authorization_checkpoints": _authorization_checkpoints(citations),
        "fixture_gaps": _fixture_gaps(citations),
        "disallowed_live_consequential_actions": _disallowed_actions(citations),
        "reviewer_owner_fields": _reviewer_owner_fields(
            devhub_attended_readonly_runbook_refresh_packet_v2,
            offline_safe_assist_release_candidate_packet_v2,
        ),
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "attestations": dict(REQUIRED_ATTESTATIONS),
        "mutation_flags": dict(MUTATION_FLAGS),
        "validation_status": "preflight_only_pending_human_authorization",
    }
    validate_live_readiness_gate_review_packet_v2(packet)
    return packet


def validate_live_readiness_gate_review_packet_v2(packet: Mapping[str, Any]) -> None:
    if packet.get("packet_type") != "live_readiness_gate_review_packet_v2":
        raise ValueError("unexpected packet_type")
    if packet.get("packet_version") != 2:
        raise ValueError("packet_version must be 2")
    if packet.get("mode") != "fixture_first_preflight_only_gate_review":
        raise ValueError("mode must be fixture_first_preflight_only_gate_review")

    consumes = _require_mapping(packet.get("consumes"), "consumes")
    for key in (
        "public_recrawl_operator_packet_v2",
        "devhub_attended_readonly_runbook_refresh_packet_v2",
        "offline_safe_assist_release_candidate_packet_v2",
    ):
        _require_string(consumes.get(key), f"consumes.{key}")

    for field in (
        "readiness_decisions",
        "required_human_authorization_checkpoints",
        "fixture_gaps",
        "disallowed_live_consequential_actions",
        "offline_validation_commands",
    ):
        if not _require_list(packet.get(field), field):
            raise ValueError(f"{field} must not be empty")

    _validate_cited_entries(packet["readiness_decisions"], "readiness_decisions")
    _validate_cited_entries(packet["required_human_authorization_checkpoints"], "required_human_authorization_checkpoints")
    _validate_cited_entries(packet["fixture_gaps"], "fixture_gaps")
    _validate_cited_entries(packet["disallowed_live_consequential_actions"], "disallowed_live_consequential_actions")

    for decision in packet["readiness_decisions"]:
        decision_map = _require_mapping(decision, "readiness_decisions[]")
        if decision_map.get("preflight_only") is not True:
            raise ValueError("readiness decisions must be preflight_only")
        if decision_map.get("live_execution_allowed") is not False:
            raise ValueError("readiness decisions cannot allow live execution")
        _require_string(decision_map.get("rationale"), "readiness_decisions[].rationale")

    for checkpoint in packet["required_human_authorization_checkpoints"]:
        checkpoint_map = _require_mapping(checkpoint, "required_human_authorization_checkpoints[]")
        if checkpoint_map.get("human_authorization_required") is not True:
            raise ValueError("authorization checkpoints must require human authorization")
        if checkpoint_map.get("agent_may_proceed_without_authorization") is not False:
            raise ValueError("authorization checkpoints cannot allow unattended progression")
        _require_string(checkpoint_map.get("authorization_scope"), "required_human_authorization_checkpoints[].authorization_scope")

    for gap in packet["fixture_gaps"]:
        gap_map = _require_mapping(gap, "fixture_gaps[]")
        if not _require_string(gap_map.get("disposition"), "fixture_gaps[].disposition"):
            raise ValueError("fixture gaps require dispositions")

    attestations = _require_mapping(packet.get("attestations"), "attestations")
    for key, expected in REQUIRED_ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            raise ValueError(f"attestations.{key} must be true")

    mutation_flags = _require_mapping(packet.get("mutation_flags"), "mutation_flags")
    for key, expected in MUTATION_FLAGS.items():
        if mutation_flags.get(key) is not expected:
            raise ValueError(f"mutation_flags.{key} must be false")

    _require_mapping(packet.get("reviewer_owner_fields"), "reviewer_owner_fields")
    _scan_unsafe_content(packet, "$", [])


def _source_citations(
    public_packet: Mapping[str, Any],
    devhub_packet: Mapping[str, Any],
    release_packet: Mapping[str, Any],
) -> dict[str, list[str]]:
    public_id = _require_string(public_packet.get("packet_id") or public_packet.get("packetId"), "public packet id")
    devhub_id = _require_string(devhub_packet.get("packet_id"), "DevHub packet id")
    release_id = _require_string(release_packet.get("packet_id"), "release packet id")
    return {
        "public_recrawl": [f"public_recrawl_operator_packet_v2:{public_id}"],
        "devhub_readonly": [f"devhub_attended_readonly_runbook_refresh_packet_v2:{devhub_id}"],
        "offline_release": [f"offline_safe_assist_release_candidate_packet_v2:{release_id}"],
        "all": [
            f"public_recrawl_operator_packet_v2:{public_id}",
            f"devhub_attended_readonly_runbook_refresh_packet_v2:{devhub_id}",
            f"offline_safe_assist_release_candidate_packet_v2:{release_id}",
        ],
    }


def _readiness_decisions(citations: Mapping[str, list[str]]) -> list[dict[str, Any]]:
    return [
        {
            "decision_id": "public-recrawl-preflight-only",
            "domain": "public_recrawl",
            "decision": "blocked_pending_explicit_public_recrawl_authorization",
            "preflight_only": True,
            "live_execution_allowed": False,
            "rationale": "Public recrawl packet is cited and shape-safe, but network activity remains blocked until a human operator authorizes a specific run.",
            "citations": citations["public_recrawl"],
        },
        {
            "decision_id": "devhub-readonly-preflight-only",
            "domain": "attended_devhub_readonly",
            "decision": "blocked_pending_attended_devhub_authorization",
            "preflight_only": True,
            "live_execution_allowed": False,
            "rationale": "Runbook refresh packet is cited and read-only, but account-scoped access remains blocked until a present human completes sign-in and authorizes observation.",
            "citations": citations["devhub_readonly"],
        },
        {
            "decision_id": "offline-safe-assist-preflight-only",
            "domain": "offline_safe_assist_release_candidate",
            "decision": "blocked_for_live_or_official_actions",
            "preflight_only": True,
            "live_execution_allowed": False,
            "rationale": "Release candidate remains offline-only and cannot be treated as live release, legal advice, or official PP&D action authority.",
            "citations": citations["offline_release"],
        },
    ]


def _authorization_checkpoints(citations: Mapping[str, list[str]]) -> list[dict[str, Any]]:
    return [
        {
            "checkpoint_id": "authorize-specific-public-recrawl-run",
            "required_before": "any network fetch, public recrawl run, or processor handoff",
            "human_authorization_required": True,
            "agent_may_proceed_without_authorization": False,
            "authorization_scope": "named seed batch, allowlist, robots disposition, rate limit, output location, and no-raw-body policy",
            "citations": citations["public_recrawl"],
        },
        {
            "checkpoint_id": "authorize-attended-devhub-readonly-observation",
            "required_before": "any DevHub browser launch, manual sign-in handoff, account-scoped page review, or UI observation",
            "human_authorization_required": True,
            "agent_may_proceed_without_authorization": False,
            "authorization_scope": "user-present sign-in, identity-prompt handoff, redaction rules, and read-only observation bounds",
            "citations": citations["devhub_readonly"],
        },
        {
            "checkpoint_id": "authorize-official-action-separately",
            "required_before": "any submission, certification, attachment, payment, purchase, scheduling, cancellation, withdrawal, extension, or account change",
            "human_authorization_required": True,
            "agent_may_proceed_without_authorization": False,
            "authorization_scope": "action-specific user-visible confirmation after cited facts and post-action review requirements are presented",
            "citations": citations["all"],
        },
    ]


def _fixture_gaps(citations: Mapping[str, list[str]]) -> list[dict[str, Any]]:
    return [
        {
            "gap_id": "no-live-recrawl-result-fixture",
            "domain": "public_recrawl",
            "gap": "No public recrawl result, response body, downloaded document, archive artifact, or processor output is included.",
            "disposition": "acceptable_for_preflight_only_review_must_be_resolved_by_separately_authorized_metadata_only_run",
            "citations": citations["public_recrawl"],
        },
        {
            "gap_id": "no-authenticated-devhub-state-fixture",
            "domain": "attended_devhub_readonly",
            "gap": "No DevHub account state, secrets, private field values, raw account-scoped page values, browser media, or network capture artifacts are included.",
            "disposition": "required_safety_gap_before_any_attended_readonly_observation",
            "citations": citations["devhub_readonly"],
        },
        {
            "gap_id": "no-official-action-authorization-fixture",
            "domain": "official_actions",
            "gap": "No action-specific human authorization exists for official submission, certification, attachment, payment, scheduling, cancellation, or account changes.",
            "disposition": "blocks_all_consequential_actions_until_a_separate_attended_exact_confirmation_checkpoint",
            "citations": citations["offline_release"],
        },
    ]


def _disallowed_actions(citations: Mapping[str, list[str]]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for action in DISALLOWED_ACTIONS:
        actions.append(
            {
                "action_id": "disallow-" + action.lower().replace(",", "").replace(" ", "-"),
                "action": action,
                "allowed_by_this_packet": False,
                "reason": "Live or consequential action is outside fixture-first preflight review scope.",
                "citations": citations["all"],
            }
        )
    return actions


def _reviewer_owner_fields(devhub_packet: Mapping[str, Any], release_packet: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    devhub_fields = devhub_packet.get("reviewer_owner_fields")
    if isinstance(devhub_fields, Mapping):
        merged.update(dict(devhub_fields))
    merged.setdefault("live_readiness_reviewer", "ppd-live-readiness-reviewer")
    merged.setdefault("public_recrawl_owner", "ppd-public-recrawl-operator")
    merged.setdefault("devhub_readonly_owner", "ppd-devhub-attended-operator")
    merged.setdefault("release_candidate_owner", "ppd-offline-release-reviewer")
    merged.setdefault("safety_owner", "ppd-safety-reviewer")
    merged["source_release_packet_id"] = release_packet.get("packet_id")
    return merged


def _validate_cited_entries(entries: list[Any], field: str) -> None:
    for index, entry in enumerate(entries):
        entry_map = _require_mapping(entry, f"{field}[]")
        citations = _require_list(entry_map.get("citations"), f"{field}[{index}].citations")
        if not all(isinstance(citation, str) and citation.strip() for citation in citations):
            raise ValueError(f"{field}[{index}].citations must contain non-empty strings")


def _scan_unsafe_content(value: Any, path: str, findings: list[str]) -> None:
    local_findings = findings
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            child_path = f"{path}.{key_text}"
            if normalized_key in PRIVATE_OR_AUTH_KEYS and child not in (None, "", [], {}):
                local_findings.append(f"private or authenticated fact is not allowed at {child_path}")
            if normalized_key in BROWSER_OR_SESSION_ARTIFACT_KEYS and child not in (None, "", [], {}):
                local_findings.append(f"browser/session artifact reference is not allowed at {child_path}")
            if normalized_key in LIVE_ARTIFACT_KEYS and child not in (None, "", [], {}):
                local_findings.append(f"raw crawl or processor artifact is not allowed at {child_path}")
            if _is_mutation_key(normalized_key) and child is True:
                local_findings.append(f"active mutation flag must be false at {child_path}")
            _scan_unsafe_content(child, child_path, local_findings)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_unsafe_content(child, f"{path}[{index}]", local_findings)
    elif isinstance(value, str):
        if PRIVATE_OR_ARTIFACT_RE.search(value):
            local_findings.append(f"private, authenticated, raw, browser, or session artifact reference is not allowed at {path}")
        if LIVE_EXECUTION_CLAIM_RE.search(value):
            local_findings.append(f"live crawl, DevHub, browser, LLM, or processor execution claim is not allowed at {path}")
        if IDENTITY_AUTOMATION_RE.search(value):
            local_findings.append(f"credential, MFA, CAPTCHA, login, or password automation language is not allowed at {path}")
        if OUTCOME_GUARANTEE_RE.search(value):
            local_findings.append(f"legal or permitting outcome guarantee is not allowed at {path}")
        if OFFICIAL_ACTION_ENABLEMENT_RE.search(value):
            local_findings.append(f"official action enablement language is not allowed at {path}")
    if path == "$" and local_findings:
        raise ValueError("invalid live-readiness gate review packet v2 unsafe content: " + "; ".join(local_findings))


def _is_mutation_key(normalized_key: str) -> bool:
    if normalized_key in MUTATION_KEYS:
        return True
    if normalized_key.endswith("_mutation_active") or normalized_key.endswith("_mutation_enabled"):
        return True
    if normalized_key.startswith("active_") and normalized_key.endswith("_mutation"):
        return True
    return False


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be a mapping")
    return value


def _require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value
