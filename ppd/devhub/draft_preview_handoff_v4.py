"""Validation for reversible draft preview handoff packet v4.

The packet is intentionally narrow: it may describe local, reversible preview
field proposals, but it must not carry private artifacts, raw documents,
consequential action language, or mutation flags for PP&D stateful systems.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence


PACKET_VERSION = "reversible_draft_preview_handoff_packet_v4"

_PRIVATE_PATH_RE = re.compile(
    r"(?i)(?:file://|(?:^|[\s:=\"'])/(?:home|users|var/folders|tmp|private|mnt|volumes)/|[a-z]:\\\\|[a-z]:/)"
)
_RAW_PDF_RE = re.compile(r"(?i)(?:raw[_ -]?pdf|application/pdf|%pdf-|\.pdf(?:$|[?#\s]))")
_UPLOAD_STAGING_RE = re.compile(r"(?i)\b(?:upload(?:ed|ing)?|attach(?:ed|ment|ing)?|staging|stage\s+file|correction\s+upload)\b")
_CONSEQUENTIAL_ACTION_RE = re.compile(
    r"(?i)\b(?:certif(?:y|ies|ied|ication)|acknowledg(?:e|ement)|submit(?:ted|ting)?|submission|payment|pay\s+fee|fee\s+payment|schedule(?:d|s|ing)?|inspection\s+schedule|cancel(?:ed|led|ing|lation)?|withdraw(?:al|n)?|purchase(?:d|s|ing)?)\b"
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"(?i)\b(?:guarantee(?:d|s)?|will\s+(?:be\s+)?(?:approve(?:d)?|issue(?:d)?|pass(?:ed)?|permit(?:ted)?)|approval\s+(?:is|will\s+be)\s+guaranteed|permit\s+(?:is|will\s+be)\s+approved|legally\s+(?:sufficient|valid|approved)|no\s+risk\s+of\s+denial)\b"
)

_MUTATION_DOMAINS = (
    "devhub",
    "source",
    "surface_registry",
    "surface-registry",
    "guardrail",
    "prompt",
    "release_state",
    "release-state",
    "agent_state",
    "agent-state",
)
_MUTATION_WORD_RE = re.compile(r"(?i)(?:mutat|write|commit|persist|publish|deploy|activate|update|delete|enable|disable)")


@dataclass(frozen=True)
class PacketValidationResult:
    """Structured validation result for handoff packet checks."""

    ok: bool
    errors: tuple[str, ...]

    def require_ok(self) -> None:
        if not self.ok:
            raise ValueError("; ".join(self.errors))


def validate_reversible_draft_preview_handoff_packet_v4(packet: Mapping[str, Any]) -> PacketValidationResult:
    """Validate a reversible draft preview handoff packet v4.

    The validator is pure and deterministic. It checks only committed packet
    content and fixture facts supplied inside the packet; it never opens local
    files, crawls public pages, or touches DevHub state.
    """

    errors: list[str] = []

    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be reversible_draft_preview_handoff_packet_v4")

    citations = _citation_ids(packet.get("citations"))
    fixture_facts = _fixture_fact_values(packet.get("fixture_facts"))
    proposals = packet.get("draft_field_proposals")

    if not isinstance(proposals, list) or not proposals:
        errors.append("draft_field_proposals must be a non-empty list")
    else:
        for index, proposal in enumerate(proposals):
            _validate_proposal(index, proposal, citations, fixture_facts, errors)

    checkpoints = packet.get("user_review_checkpoints")
    if not isinstance(checkpoints, list) or not checkpoints:
        errors.append("user_review_checkpoints must be a non-empty list")
    else:
        required_checkpoint_kinds = {"review_draft_values", "confirm_no_official_action"}
        present = {
            str(item.get("kind"))
            for item in checkpoints
            if isinstance(item, Mapping) and item.get("required") is True
        }
        missing = sorted(required_checkpoint_kinds - present)
        if missing:
            errors.append("user_review_checkpoints missing required kinds: " + ", ".join(missing))

    if _has_matching_string(packet, _PRIVATE_PATH_RE):
        errors.append("packet must not contain private local paths")
    if _has_matching_string(packet, _RAW_PDF_RE):
        errors.append("packet must not contain raw PDFs or PDF file references")
    if _has_matching_string(packet, _UPLOAD_STAGING_RE):
        errors.append("packet must not contain upload staging or attachment language")
    if _has_matching_string(packet, _CONSEQUENTIAL_ACTION_RE):
        errors.append("packet must not contain certification, submission, payment, scheduling, cancellation, or purchase language")
    if _has_matching_string(packet, _OUTCOME_GUARANTEE_RE):
        errors.append("packet must not contain legal or permitting outcome guarantees")

    mutation_paths = _active_mutation_paths(packet)
    if mutation_paths:
        errors.append("packet must not contain active mutation flags: " + ", ".join(mutation_paths))

    return PacketValidationResult(ok=not errors, errors=tuple(errors))


def assert_valid_reversible_draft_preview_handoff_packet_v4(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a packet is not valid."""

    validate_reversible_draft_preview_handoff_packet_v4(packet).require_ok()


def _validate_proposal(
    index: int,
    proposal: Any,
    citation_ids: set[str],
    fixture_fact_values: set[str],
    errors: list[str],
) -> None:
    label = f"draft_field_proposals[{index}]"
    if not isinstance(proposal, Mapping):
        errors.append(f"{label} must be an object")
        return

    field_id = proposal.get("field_id")
    if not isinstance(field_id, str) or not field_id.strip():
        errors.append(f"{label}.field_id must be a non-empty string")

    value = proposal.get("proposed_value")
    if not _is_scalar_value(value):
        errors.append(f"{label}.proposed_value must be a scalar fixture-grounded value")
    elif _normalize_fact_value(value) not in fixture_fact_values:
        errors.append(f"{label}.proposed_value is not grounded in fixture_facts")

    proposal_citations = proposal.get("citation_ids")
    if not isinstance(proposal_citations, list) or not proposal_citations:
        errors.append(f"{label}.citation_ids must cite source evidence")
        return

    unknown = sorted(str(citation) for citation in proposal_citations if str(citation) not in citation_ids)
    if unknown:
        errors.append(f"{label}.citation_ids contains unknown citations: " + ", ".join(unknown))


def _citation_ids(citations: Any) -> set[str]:
    if not isinstance(citations, list):
        return set()
    ids: set[str] = set()
    for citation in citations:
        if isinstance(citation, Mapping) and isinstance(citation.get("citation_id"), str):
            ids.add(citation["citation_id"])
    return ids


def _fixture_fact_values(facts: Any) -> set[str]:
    values: set[str] = set()
    if isinstance(facts, Mapping):
        iterable: Iterable[Any] = facts.values()
    elif isinstance(facts, list):
        iterable = facts
    else:
        return values

    for item in iterable:
        if isinstance(item, Mapping) and "value" in item:
            values.add(_normalize_fact_value(item["value"]))
        elif _is_scalar_value(item):
            values.add(_normalize_fact_value(item))
    return values


def _normalize_fact_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def _is_scalar_value(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) and not isinstance(value, bool) or isinstance(value, bool)


def _has_matching_string(value: Any, pattern: re.Pattern[str]) -> bool:
    if isinstance(value, str):
        return bool(pattern.search(value))
    if isinstance(value, Mapping):
        return any(_has_matching_string(key, pattern) or _has_matching_string(child, pattern) for key, child in value.items())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_has_matching_string(child, pattern) for child in value)
    return False


def _active_mutation_paths(value: Any, path: str = "packet") -> list[str]:
    paths: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            normalized = key_text.lower().replace(" ", "_")
            mentions_domain = any(domain in normalized for domain in _MUTATION_DOMAINS)
            mentions_mutation = bool(_MUTATION_WORD_RE.search(normalized))
            if mentions_domain and mentions_mutation and _is_active_flag(child):
                paths.append(child_path)
            paths.extend(_active_mutation_paths(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            paths.extend(_active_mutation_paths(child, f"{path}[{index}]"))
    return paths


def _is_active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "enabled", "true", "yes", "write", "mutate", "commit", "persist"}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, Mapping):
        enabled = value.get("enabled", value.get("active", value.get("allowed")))
        return _is_active_flag(enabled)
    return False


__all__ = [
    "PACKET_VERSION",
    "PacketValidationResult",
    "assert_valid_reversible_draft_preview_handoff_packet_v4",
    "validate_reversible_draft_preview_handoff_packet_v4",
]
