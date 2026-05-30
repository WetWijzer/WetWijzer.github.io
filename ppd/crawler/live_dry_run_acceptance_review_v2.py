"""Validation for live dry-run acceptance review packet v2.

The validator is intentionally conservative: acceptance review packets are
commit-safe evidence artifacts, not execution plans. Any private fact, raw
browser/crawl artifact, live execution claim, consequential action language, or
active mutation flag blocks acceptance.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


_DECISIONS_REQUIRING_RATIONALE = {"accepted", "deferred", "rejected"}
_REVIEW_OUTCOMES = _DECISIONS_REQUIRING_RATIONALE
_MUTATION_SCOPES = {
    "source",
    "source_registry",
    "surface_registry",
    "guardrail",
    "prompt",
    "monitoring",
    "release_state",
    "agent_state",
}
_MUTATION_WORDS = {"active", "enabled", "enable", "mutate", "mutation", "write", "apply", "update", "commit"}
_RAW_ARTIFACT_RE = re.compile(
    r"\b(har|trace(?:\.zip)?|screenshot|video|browser\s+state|storage\s+state|session\s+state|"
    r"cookies?|raw\s+(?:crawl|html|pdf|download|body|response)|warc|crawl\s+output|downloaded\s+pdf)\b",
    re.IGNORECASE,
)
_PRIVATE_FACT_RE = re.compile(
    r"\b(private|authenticated|account-scoped|credential|password|cookie|token|secret|ssn|"
    r"payment\s+detail|permit\s+owner|applicant\s+email|phone\s+number|private\s+upload|"
    r"local\s+private\s+file)\b",
    re.IGNORECASE,
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live\s+execution|executed\s+live|clicked\s+(?:submit|pay|upload|schedule|cancel)|"
    r"submitted\s+to\s+devhub|paid\s+fees?|uploaded\s+corrections?|scheduled\s+inspection|"
    r"cancelled\s+inspection|withdrew\s+permit)\b",
    re.IGNORECASE,
)
_CREDENTIAL_AUTOMATION_RE = re.compile(
    r"\b(automate(?:d|s|ing)?\s+(?:credential|login|password|mfa|captcha|account\s+creation)|"
    r"bypass(?:ed|es|ing)?\s+(?:mfa|captcha|login|access\s+control)|solve(?:d|s|ing)?\s+captcha|"
    r"entered\s+(?:password|mfa|verification\s+code)|created\s+account)\b",
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r"\b(guarantee(?:d|s)?|will\s+be\s+approved|permit\s+approval\s+is\s+assured|"
    r"legal\s+compliance\s+guaranteed|valid\s+as\s+legal\s+advice|entitled\s+to\s+issuance)\b",
    re.IGNORECASE,
)
_FINAL_ACTION_RE = re.compile(
    r"\b(final\s+(?:submit|submission|payment|upload|schedule|scheduling|cancel|cancellation)|"
    r"submit(?:ted|s|ting)?\s+(?:application|permit|payment|fee|plans?|correction)|"
    r"pay(?:s|ing|ment)?\s+(?:fee|invoice|balance)|upload(?:ed|s|ing)?\s+(?:plans?|corrections?|documents?)|"
    r"schedule(?:d|s|ing)?\s+inspection|cancel(?:led|s|ing)?\s+(?:inspection|permit|request))\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PacketViolation:
    code: str
    path: str
    message: str


def validate_acceptance_review_packet_v2(packet: Mapping[str, Any]) -> list[PacketViolation]:
    """Return blocking validation violations for a packet-v2 review artifact."""

    violations: list[PacketViolation] = []
    if not isinstance(packet, Mapping):
        return [PacketViolation("invalid_packet", "$", "packet must be a mapping")]

    _validate_observation_decisions(packet, violations)
    _validate_review_outcome_rationales(packet, violations)
    _validate_reviewer_owners(packet, violations)
    _validate_incident_and_abort_dispositions(packet, violations)
    _validate_mutation_flags(packet, violations)
    _validate_forbidden_language(packet, violations)
    return violations


def assert_acceptance_review_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when packet-v2 validation finds any blocker."""

    violations = validate_acceptance_review_packet_v2(packet)
    if violations:
        details = "; ".join(f"{item.code} at {item.path}" for item in violations)
        raise ValueError(f"live dry-run acceptance review packet v2 rejected: {details}")


def packet_v2_is_accepted(packet: Mapping[str, Any]) -> bool:
    return not validate_acceptance_review_packet_v2(packet)


def _validate_observation_decisions(packet: Mapping[str, Any], violations: list[PacketViolation]) -> None:
    observations = _as_sequence(packet.get("observation_decisions"))
    for index, observation in enumerate(observations):
        path = f"$.observation_decisions[{index}]"
        if not isinstance(observation, Mapping):
            violations.append(PacketViolation("invalid_observation_decision", path, "observation decision must be a mapping"))
            continue
        decision = _normalized(observation.get("decision"))
        if decision and not _has_citation(observation):
            violations.append(PacketViolation("uncited_observation_decision", path, "observation decision must cite public evidence"))
        if decision in _DECISIONS_REQUIRING_RATIONALE and not _has_text(observation.get("rationale")):
            violations.append(PacketViolation("missing_observation_rationale", f"{path}.rationale", "accepted/deferred/rejected observation decisions require rationale"))


def _validate_review_outcome_rationales(packet: Mapping[str, Any], violations: list[PacketViolation]) -> None:
    review_items = _as_sequence(packet.get("review_decisions")) + _as_sequence(packet.get("acceptance_decisions"))
    for index, item in enumerate(review_items):
        path = f"$.review_decisions[{index}]"
        if not isinstance(item, Mapping):
            violations.append(PacketViolation("invalid_review_decision", path, "review decision must be a mapping"))
            continue
        outcome = _normalized(item.get("decision") or item.get("outcome") or item.get("status"))
        if outcome in _REVIEW_OUTCOMES and not _has_text(item.get("rationale")):
            violations.append(PacketViolation("missing_review_rationale", f"{path}.rationale", "accepted/deferred/rejected review decisions require rationale"))

    for outcome in sorted(_REVIEW_OUTCOMES):
        key = f"{outcome}_rationale"
        if outcome == _normalized(packet.get("decision") or packet.get("outcome") or packet.get("status")) and not _has_text(packet.get(key) or packet.get("rationale")):
            violations.append(PacketViolation("missing_packet_rationale", f"$.{key}", "packet-level accepted/deferred/rejected outcome requires rationale"))


def _validate_reviewer_owners(packet: Mapping[str, Any], violations: list[PacketViolation]) -> None:
    owners = packet.get("reviewer_owners") or packet.get("reviewers") or packet.get("owners")
    if not _as_sequence(owners):
        violations.append(PacketViolation("missing_reviewer_owner", "$.reviewer_owners", "at least one reviewer owner is required"))
        return
    for index, owner in enumerate(_as_sequence(owners)):
        if isinstance(owner, Mapping):
            if not (_has_text(owner.get("owner")) or _has_text(owner.get("name")) or _has_text(owner.get("id"))):
                violations.append(PacketViolation("missing_reviewer_owner", f"$.reviewer_owners[{index}]", "reviewer owner entry must name an owner"))
        elif not _has_text(owner):
            violations.append(PacketViolation("missing_reviewer_owner", f"$.reviewer_owners[{index}]", "reviewer owner entry must be non-empty"))


def _validate_incident_and_abort_dispositions(packet: Mapping[str, Any], violations: list[PacketViolation]) -> None:
    unresolved = {"", "open", "unresolved", "pending", "todo", "unknown", "none"}
    for field in ("incident_dispositions", "abort_dispositions"):
        for index, item in enumerate(_as_sequence(packet.get(field))):
            path = f"$.{field}[{index}]"
            if isinstance(item, Mapping):
                disposition = _normalized(item.get("disposition") or item.get("status") or item.get("resolution"))
            else:
                disposition = _normalized(item)
            if disposition in unresolved:
                violations.append(PacketViolation("unresolved_disposition", path, "incident and abort dispositions must be resolved"))


def _validate_mutation_flags(packet: Mapping[str, Any], violations: list[PacketViolation]) -> None:
    flags = packet.get("mutation_flags") or packet.get("state_mutation_flags") or packet.get("active_mutation_flags")
    for index, flag in enumerate(_as_sequence(flags)):
        path = f"$.mutation_flags[{index}]"
        if isinstance(flag, Mapping):
            scope = _normalized(flag.get("scope") or flag.get("target") or flag.get("name"))
            active = bool(flag.get("active") or flag.get("enabled") or flag.get("mutates") or flag.get("write_enabled"))
            text = " ".join(str(value) for value in flag.values())
        else:
            scope = _normalized(flag)
            active = any(word in scope for word in _MUTATION_WORDS)
            text = str(flag)
        if _mentions_mutation_scope(scope) and active:
            violations.append(PacketViolation("active_mutation_flag", path, "review packet must not carry active registry, guardrail, prompt, monitoring, release, or agent-state mutation flags"))
        elif _mentions_mutation_scope(text) and any(word in _normalized(text) for word in _MUTATION_WORDS):
            violations.append(PacketViolation("active_mutation_flag", path, "review packet must not describe active state mutation"))


def _validate_forbidden_language(packet: Mapping[str, Any], violations: list[PacketViolation]) -> None:
    checks = (
        ("private_or_authenticated_fact", _PRIVATE_FACT_RE, "private or authenticated facts are not allowed"),
        ("raw_artifact_reference", _RAW_ARTIFACT_RE, "raw crawl, PDF, session, or browser artifacts are not allowed"),
        ("live_execution_claim", _LIVE_EXECUTION_RE, "live execution claims are not allowed in dry-run acceptance"),
        ("credential_or_challenge_automation", _CREDENTIAL_AUTOMATION_RE, "credential, MFA, CAPTCHA, or account automation language is not allowed"),
        ("legal_or_permitting_guarantee", _GUARANTEE_RE, "legal or permitting outcome guarantees are not allowed"),
        ("final_consequential_action", _FINAL_ACTION_RE, "final submission/payment/upload/scheduling/cancellation language is not allowed"),
    )
    for path, value in _walk_strings(packet):
        for code, pattern, message in checks:
            if pattern.search(value):
                violations.append(PacketViolation(code, path, message))


def _walk_strings(value: Any, path: str = "$", seen: set[int] | None = None) -> Iterable[tuple[str, str]]:
    if seen is None:
        seen = set()
    value_id = id(value)
    if value_id in seen:
        return
    if isinstance(value, str):
        yield path, value
        return
    if isinstance(value, Mapping):
        seen.add(value_id)
        for key, item in value.items():
            yield from _walk_strings(item, f"{path}.{key}", seen)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        seen.add(value_id)
        for index, item in enumerate(value):
            yield from _walk_strings(item, f"{path}[{index}]", seen)


def _as_sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_citation(item: Mapping[str, Any]) -> bool:
    for key in ("citations", "source_evidence_ids", "evidence", "public_source_citations"):
        value = item.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) > 0:
            return True
        if _has_text(value):
            return True
    return False


def _normalized(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _mentions_mutation_scope(value: Any) -> bool:
    normalized = _normalized(value)
    return any(scope in normalized for scope in _MUTATION_SCOPES)
