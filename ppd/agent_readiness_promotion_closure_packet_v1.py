"""Fixture-first agent readiness promotion closure packet v1.

This module turns an active promotion application manifest and a guarded
post-promotion replay ledger into a reviewer-facing closure packet. It is
pure and deterministic: it does not apply promotion changes, touch release
state, crawl sources, or perform authenticated actions.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

Packet = Dict[str, Any]
JsonMap = Mapping[str, Any]


PACKET_VERSION = "agent_readiness_promotion_closure_packet_v1"
_ALLOWED_DECISIONS = {"ready_for_reviewer_signoff", "no_go"}
_SIDE_EFFECT_FLAGS = (
    "promotion_changes_applied",
    "prompts_changed",
    "active_artifacts_mutated",
    "release_state_updated",
    "live_sources_crawled",
    "devhub_accessed",
    "official_actions_performed",
)
_PRIVATE_KEY_RE = re.compile(
    r"(^|_)(access_token|auth|authenticated|browser|captcha|cookie|credential|devhub_session|download|downloaded|har|mfa|password|payment|private|raw|screenshot|session|storage_state|token|trace|warc)(_|$)",
    re.IGNORECASE,
)
_MUTATION_KEY_RE = re.compile(
    r"(active_.*mutation|active_.*mutated|agent_state_.*mutation|artifact_.*mutation|fixture_.*mutation|prompt_.*mutation|prompt_changes?|release_state_.*mutation|release_state_updated|fixture_changes_applied|promotion_executed|release_executed|release_complete)",
    re.IGNORECASE,
)
_UNSAFE_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"(auth file|auth state|authenticated artifact|browser artifact|browser state|cookie|credential|devhub session|downloaded data|downloaded document|downloaded file|har file|password|private artifact|raw crawl|raw data|raw download|raw html|raw pdf|screenshot|session state|storage state|token|trace file|warc)|"
    r"\b(live crawl|live devhub|live browser|live execution|executed live|opened devhub|promotion completed|promotion complete|promotion applied|promoted to active|release state updated|release completed|release complete|released to production|official action performed)\b|"
    r"\b(permit will be approved|approval guaranteed|legal outcome guaranteed|permitting outcome guaranteed|guaranteed approval|guaranteed permit|legal advice|legally sufficient|no risk of denial)\b|"
    r"\b(pay(?:ment)?|submit(?:ted|s|ting)?|submission|schedule(?:d|s|ing)?|cancel(?:led|s|ing|ation)?|certif(?:y|ies|ied|ication)|upload(?:ed|s|ing)?)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ClosurePacketValidationResult:
    """Deterministic validation result for closure packet v1."""

    ok: bool
    errors: Tuple[str, ...]

    @property
    def valid(self) -> bool:
        return self.ok


def build_closure_packet(
    application_manifest: JsonMap,
    replay_ledger: JsonMap,
    *,
    generated_at: str = "2026-05-30T00:00:00Z",
) -> Packet:
    """Build an ordered closure packet from deterministic fixture inputs."""

    manifest_id = str(application_manifest.get("manifest_id", "unknown_manifest"))
    ledger_id = str(replay_ledger.get("ledger_id", "unknown_ledger"))
    application_rows = _as_list(application_manifest.get("applications"))
    replay_rows = _as_list(replay_ledger.get("replay_results"))
    replay_by_id = {str(row.get("application_id")): row for row in replay_rows}

    decision_rows: List[Dict[str, Any]] = []
    unresolved_mismatches: List[Dict[str, Any]] = []
    rollback_confirmations: List[Dict[str, Any]] = []
    no_go_reasons: List[Dict[str, Any]] = []

    for index, app in enumerate(application_rows, start=1):
        application_id = str(app.get("application_id", f"application_{index}"))
        expected_status = str(app.get("expected_replay_status", "passed"))
        replay = replay_by_id.get(application_id, {})
        replay_status = str(replay.get("status", "missing"))
        evidence_ids = _unique_strings(app.get("required_evidence_ids"))
        observed_evidence_ids = _unique_strings(replay.get("evidence_ids"))
        missing_evidence = [item for item in evidence_ids if item not in observed_evidence_ids]
        mismatch_codes = _unique_strings(replay.get("mismatch_codes"))
        rollback = _normalize_confirmation(app.get("rollback_readiness"))

        status_matches = replay_status == expected_status
        evidence_complete = not missing_evidence
        rollback_ready = rollback["confirmed"] is True
        no_go = replay_status in {"failed", "missing"} or not status_matches or not evidence_complete or mismatch_codes or not rollback_ready
        decision = "no_go" if no_go else "ready_for_reviewer_signoff"

        row = {
            "order": index,
            "application_id": application_id,
            "promotion_target": str(app.get("promotion_target", "unspecified")),
            "requested_action": str(app.get("requested_action", "promotion_review")),
            "expected_replay_status": expected_status,
            "observed_replay_status": replay_status,
            "decision": decision,
            "evidence_ids_required": evidence_ids,
            "evidence_ids_observed": observed_evidence_ids,
            "missing_evidence_ids": missing_evidence,
            "mismatch_codes": mismatch_codes,
            "no_go_reason_codes": _no_go_reason_codes(status_matches, evidence_complete, mismatch_codes, rollback_ready, replay_status),
            "citations": _closure_citations(manifest_id, ledger_id, application_id),
            "reviewer_signoff": {
                "reviewer": "",
                "decision": "",
                "signed_at": "",
                "notes": "",
            },
        }
        decision_rows.append(row)

        rollback_confirmations.append(
            {
                "application_id": application_id,
                "confirmed": rollback_ready,
                "method": rollback["method"],
                "evidence_id": rollback["evidence_id"],
            }
        )

        if row["mismatch_codes"] or row["missing_evidence_ids"] or replay_status == "missing":
            unresolved_mismatches.append(
                {
                    "application_id": application_id,
                    "observed_replay_status": replay_status,
                    "mismatch_codes": row["mismatch_codes"],
                    "missing_evidence_ids": row["missing_evidence_ids"],
                }
            )

        if row["no_go_reason_codes"]:
            no_go_reasons.append(
                {
                    "application_id": application_id,
                    "reason_codes": row["no_go_reason_codes"],
                }
            )

    replay_application_ids = {str(row.get("application_id")) for row in replay_rows}
    manifest_application_ids = {str(row.get("application_id")) for row in application_rows}
    for orphan_id in sorted(replay_application_ids - manifest_application_ids):
        unresolved_mismatches.append(
            {
                "application_id": orphan_id,
                "observed_replay_status": str(replay_by_id[orphan_id].get("status", "unknown")),
                "mismatch_codes": ["replay_result_without_manifest_application"],
                "missing_evidence_ids": [],
            }
        )
        no_go_reasons.append(
            {
                "application_id": orphan_id,
                "reason_codes": ["replay_result_without_manifest_application"],
            }
        )

    packet = {
        "packet_version": PACKET_VERSION,
        "generated_at": _normalize_timestamp(generated_at),
        "source_manifest_id": manifest_id,
        "source_replay_ledger_id": ledger_id,
        "mode": "fixture_first_no_promotion_side_effects",
        "decision_rows": decision_rows,
        "evidence_coverage_summary": _evidence_summary(decision_rows, manifest_id, ledger_id),
        "unresolved_mismatch_inventory": unresolved_mismatches,
        "reviewer_signoff_placeholders": [
            {
                "application_id": row["application_id"],
                "reviewer": "",
                "decision": "",
                "signed_at": "",
                "notes": "",
            }
            for row in decision_rows
        ],
        "rollback_readiness_confirmations": rollback_confirmations,
        "no_go_reasons": no_go_reasons,
        "side_effects": {
            "promotion_changes_applied": False,
            "prompts_changed": False,
            "active_artifacts_mutated": False,
            "release_state_updated": False,
            "live_sources_crawled": False,
            "devhub_accessed": False,
            "official_actions_performed": False,
        },
    }
    require_valid_closure_packet(packet)
    return packet


def validate_closure_packet(packet: Mapping[str, Any]) -> ClosurePacketValidationResult:
    """Validate closure packet v1 shape and fail-closed safety boundaries."""

    errors: List[str] = []
    if not isinstance(packet, Mapping):
        return ClosurePacketValidationResult(False, ("packet must be a mapping",))

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append(f"packet_version must be {PACKET_VERSION}")
    if not _text(packet.get("source_manifest_id")):
        errors.append("source_manifest_id must be present")
    if not _text(packet.get("source_replay_ledger_id")):
        errors.append("source_replay_ledger_id must be present")

    decision_rows = _mapping_sequence(packet.get("decision_rows"))
    if not decision_rows:
        errors.append("decision_rows must contain closure decision rows")
    if [row.get("order") for row in decision_rows] != list(range(1, len(decision_rows) + 1)):
        errors.append("decision_rows must be sequentially ordered from 1")

    no_go_by_application = {
        _text(row.get("application_id")): _string_list(row.get("reason_codes"))
        for row in _mapping_sequence(packet.get("no_go_reasons"))
    }
    for index, row in enumerate(decision_rows):
        path = f"decision_rows[{index}]"
        application_id = _text(row.get("application_id"))
        if not application_id:
            errors.append(f"{path}.application_id must be present")
        if _text(row.get("decision")) not in _ALLOWED_DECISIONS:
            errors.append(f"{path}.decision must be one of {sorted(_ALLOWED_DECISIONS)}")
        if not _string_list(row.get("evidence_ids_required")):
            errors.append(f"{path}.evidence_ids_required must be a non-empty list of evidence ids")
        if not isinstance(row.get("missing_evidence_ids"), Sequence) or isinstance(row.get("missing_evidence_ids"), (str, bytes, bytearray)):
            errors.append(f"{path}.missing_evidence_ids must be a list")
        if not isinstance(row.get("mismatch_codes"), Sequence) or isinstance(row.get("mismatch_codes"), (str, bytes, bytearray)):
            errors.append(f"{path}.mismatch_codes must be a list")
        if not _citation_list(row.get("citations")):
            errors.append(f"{path}.citations must be non-empty")
        signoff = _mapping(row.get("reviewer_signoff"))
        for field in ("reviewer", "decision", "signed_at", "notes"):
            if field not in signoff:
                errors.append(f"{path}.reviewer_signoff.{field} placeholder must be present")
        if _text(row.get("decision")) == "no_go" and not _string_list(row.get("no_go_reason_codes")):
            errors.append(f"{path}.no_go_reason_codes must explain no_go decisions")
        if _text(row.get("decision")) == "no_go" and application_id and not no_go_by_application.get(application_id):
            errors.append(f"no_go_reasons must include reason_codes for {application_id}")

    summary = _mapping(packet.get("evidence_coverage_summary"))
    if not summary:
        errors.append("evidence_coverage_summary must be present")
    else:
        if not _citation_list(summary.get("citations")):
            errors.append("evidence_coverage_summary.citations must be non-empty")
        for field in (
            "applications_total",
            "applications_ready_for_signoff",
            "applications_no_go",
            "required_evidence_count",
            "observed_evidence_count",
            "covered_required_evidence_count",
            "missing_evidence_count",
            "coverage_ratio",
        ):
            if field not in summary:
                errors.append(f"evidence_coverage_summary.{field} must be present")

    if not _is_sequence(packet.get("unresolved_mismatch_inventory")):
        errors.append("unresolved_mismatch_inventory must be present as a list")
    if not _mapping_sequence(packet.get("reviewer_signoff_placeholders")):
        errors.append("reviewer_signoff_placeholders must be a non-empty list")
    else:
        for index, placeholder in enumerate(_mapping_sequence(packet.get("reviewer_signoff_placeholders"))):
            for field in ("application_id", "reviewer", "decision", "signed_at", "notes"):
                if field not in placeholder:
                    errors.append(f"reviewer_signoff_placeholders[{index}].{field} must be present")
    if not _mapping_sequence(packet.get("rollback_readiness_confirmations")):
        errors.append("rollback_readiness_confirmations must be a non-empty list")
    else:
        for index, confirmation in enumerate(_mapping_sequence(packet.get("rollback_readiness_confirmations"))):
            if not _text(confirmation.get("application_id")):
                errors.append(f"rollback_readiness_confirmations[{index}].application_id must be present")
            if not isinstance(confirmation.get("confirmed"), bool):
                errors.append(f"rollback_readiness_confirmations[{index}].confirmed must be boolean")
            if not _text(confirmation.get("method")):
                errors.append(f"rollback_readiness_confirmations[{index}].method must be present")
            if not _text(confirmation.get("evidence_id")):
                errors.append(f"rollback_readiness_confirmations[{index}].evidence_id must be present")
    if not _is_sequence(packet.get("no_go_reasons")):
        errors.append("no_go_reasons must be present as a list")
    else:
        for index, reason in enumerate(_mapping_sequence(packet.get("no_go_reasons"))):
            if not _text(reason.get("application_id")):
                errors.append(f"no_go_reasons[{index}].application_id must be present")
            if not _string_list(reason.get("reason_codes")):
                errors.append(f"no_go_reasons[{index}].reason_codes must be non-empty")

    side_effects = _mapping(packet.get("side_effects"))
    if not side_effects:
        errors.append("side_effects must be present")
    for flag in _SIDE_EFFECT_FLAGS:
        if side_effects.get(flag) is not False:
            errors.append(f"side_effects.{flag} must be false")

    _scan_unsafe(packet, "packet", errors)
    return ClosurePacketValidationResult(not errors, tuple(errors))


def require_valid_closure_packet(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a closure packet fails validation."""

    result = validate_closure_packet(packet)
    if not result.ok:
        raise ValueError("invalid agent readiness promotion closure packet v1: " + "; ".join(result.errors))


def _as_list(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [deepcopy(item) for item in value if isinstance(item, dict)]


def _unique_strings(value: Any) -> List[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    seen = set()
    result: List[str] = []
    for item in value:
        text = str(item)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _normalize_confirmation(value: Any) -> Dict[str, Any]:
    if not isinstance(value, Mapping):
        return {"confirmed": False, "method": "", "evidence_id": ""}
    return {
        "confirmed": bool(value.get("confirmed")),
        "method": str(value.get("method", "")),
        "evidence_id": str(value.get("evidence_id", "")),
    }


def _no_go_reason_codes(
    status_matches: bool,
    evidence_complete: bool,
    mismatch_codes: Sequence[str],
    rollback_ready: bool,
    replay_status: str,
) -> List[str]:
    reasons: List[str] = []
    if replay_status == "missing":
        reasons.append("missing_replay_result")
    if not status_matches:
        reasons.append("unexpected_replay_status")
    if not evidence_complete:
        reasons.append("required_evidence_missing")
    if mismatch_codes:
        reasons.append("unresolved_replay_mismatch")
    if not rollback_ready:
        reasons.append("rollback_readiness_unconfirmed")
    return reasons


def _evidence_summary(decision_rows: Iterable[Mapping[str, Any]], manifest_id: str, ledger_id: str) -> Dict[str, Any]:
    rows = list(decision_rows)
    required: List[str] = []
    observed: List[str] = []
    missing: List[str] = []
    for row in rows:
        required.extend(_unique_strings(row.get("evidence_ids_required")))
        observed.extend(_unique_strings(row.get("evidence_ids_observed")))
        missing.extend(_unique_strings(row.get("missing_evidence_ids")))

    required_unique = sorted(set(required))
    observed_unique = sorted(set(observed))
    missing_unique = sorted(set(missing))
    covered_count = len([item for item in required_unique if item in observed_unique])
    total_required = len(required_unique)

    return {
        "applications_total": len(rows),
        "applications_ready_for_signoff": len([row for row in rows if row.get("decision") == "ready_for_reviewer_signoff"]),
        "applications_no_go": len([row for row in rows if row.get("decision") == "no_go"]),
        "required_evidence_count": total_required,
        "observed_evidence_count": len(observed_unique),
        "covered_required_evidence_count": covered_count,
        "missing_evidence_count": len(missing_unique),
        "coverage_ratio": 1.0 if total_required == 0 else covered_count / total_required,
        "missing_evidence_ids": missing_unique,
        "citations": [
            {"packet": manifest_id, "section": "applications.required_evidence_ids"},
            {"packet": ledger_id, "section": "replay_results.evidence_ids"},
        ],
    }


def _closure_citations(manifest_id: str, ledger_id: str, application_id: str) -> List[Dict[str, str]]:
    return [
        {"packet": manifest_id, "application_id": application_id},
        {"packet": ledger_id, "application_id": application_id},
    ]


def _normalize_timestamp(value: str) -> str:
    if value.endswith("Z"):
        return value
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _scan_unsafe(value: Any, path: str, errors: List[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_").replace(" ", "_")
            child_path = f"{path}.{key_text}"
            if _PRIVATE_KEY_RE.search(normalized) and _truthy(child):
                errors.append(f"{child_path} contains private, authenticated, session, browser, screenshot, trace, HAR, auth, raw, or downloaded artifact data")
            if _MUTATION_KEY_RE.search(normalized) and _truthy(child):
                errors.append(f"{child_path} is an active artifact, prompt, release-state, fixture, or agent-state mutation flag")
            _scan_unsafe(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_unsafe(child, f"{path}[{index}]", errors)
    elif isinstance(value, str) and _UNSAFE_TEXT_RE.search(value):
        errors.append(f"{path} contains unsafe artifact, live execution, release/promotion claim, outcome guarantee, or consequential action language")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> List[Mapping[str, Any]]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _string_list(value: Any) -> List[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item) for item in value if str(item).strip()]
    return []


def _citation_list(value: Any) -> List[Any]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping) or (isinstance(item, str) and item.strip())]
    return []


def _truthy(value: Any) -> bool:
    if value in (None, False, ""):
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and not value:
        return False
    if isinstance(value, Mapping) and not value:
        return False
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


__all__ = [
    "ClosurePacketValidationResult",
    "PACKET_VERSION",
    "build_closure_packet",
    "require_valid_closure_packet",
    "validate_closure_packet",
]
