"""Fixture-first public recrawl dry-run evidence envelope v2.

The envelope consumes committed public recrawl live-dry-run plan v2 and
post-briefing dry-run authorization ledger v2 fixtures. It emits only cited
metadata observation slots and never crawls, downloads, invokes processors, or
mutates source registries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


PACKET_TYPE = "public-recrawl-dry-run-evidence-envelope"
PACKET_VERSION = "v2"
MODE = "fixture_first_public_recrawl_dry_run_evidence_envelope"

REQUIRED_SOURCE_KEYS = (
    "public_recrawl_live_dry_run_plan_v2",
    "post_briefing_dry_run_authorization_ledger_v2",
)

REQUIRED_SLOT_KINDS = frozenset(
    {
        "seed_url",
        "allowlist_robots_decision",
        "redirect_content_type_hash_placeholder",
        "skip_reason",
        "rate_limit_observation",
        "operator_stop_condition",
        "offline_validation_commands",
        "attestation",
    }
)

REQUIRED_ATTESTATIONS = frozenset(
    {
        "no_live_crawl",
        "no_processor",
        "no_raw_body",
        "no_download",
        "no_source_registry_mutation",
    }
)

_FORBIDDEN_TRUE_KEYS = frozenset(
    {
        "live_crawl_performed",
        "live_network_invoked",
        "processor_invoked",
        "raw_body_persisted",
        "document_downloaded",
        "source_registry_mutated",
        "registry_mutated",
        "download_performed",
    }
)


@dataclass(frozen=True)
class EvidenceEnvelopeValidationResult:
    valid: bool
    errors: tuple[str, ...]


def build_public_recrawl_dry_run_evidence_envelope_v2(source_packets: Mapping[str, Any]) -> dict[str, Any]:
    """Build a cited metadata-only evidence envelope from fixture packets."""

    missing = [key for key in REQUIRED_SOURCE_KEYS if key not in source_packets]
    if missing:
        raise ValueError("missing source packets: " + ", ".join(missing))

    public_plan = _require_mapping(source_packets["public_recrawl_live_dry_run_plan_v2"], "public plan")
    authorization_ledger = _require_mapping(
        source_packets["post_briefing_dry_run_authorization_ledger_v2"],
        "authorization ledger",
    )

    slots: list[dict[str, Any]] = []
    seed_batches = _sequence(public_plan.get("seed_batches"))
    for index, batch_value in enumerate(seed_batches):
        if not isinstance(batch_value, Mapping):
            continue
        source_id = _text(batch_value.get("source_id"), "source-" + str(index + 1))
        seed_url = _text(batch_value.get("seed_url"))
        citations = _citations(batch_value, "public_recrawl_live_dry_run_plan_v2.seed_batches")
        slot_prefix = "slot-" + source_id.replace("_", "-")

        slots.append(
            _slot(
                slot_prefix + "-seed-url",
                "seed_url",
                source_id,
                {"seed_url": seed_url},
                citations,
            )
        )
        slots.append(
            _slot(
                slot_prefix + "-allowlist-robots",
                "allowlist_robots_decision",
                source_id,
                {
                    "selection_basis": _text(batch_value.get("selection_basis")),
                    "robots_decision": dict(batch_value.get("robots_decision", {})) if isinstance(batch_value.get("robots_decision"), Mapping) else {},
                    "allowlist_decision": "selected_from_committed_allowlist_fixture",
                },
                citations + _citations(batch_value.get("robots_decision"), "public_recrawl_live_dry_run_plan_v2.robots_decision"),
            )
        )
        slots.append(
            _slot(
                slot_prefix + "-capture-placeholder",
                "redirect_content_type_hash_placeholder",
                source_id,
                {
                    "requested_url": seed_url,
                    "final_url": None,
                    "redirect_chain": [],
                    "http_status": None,
                    "content_type": _content_type_hint(batch_value),
                    "content_hash": "metadata_only_placeholder_not_captured",
                    "raw_body_persisted": False,
                },
                citations,
            )
        )
        slots.append(
            _slot(
                slot_prefix + "-skip-reason",
                "skip_reason",
                source_id,
                {
                    "skipped_reason": _text(batch_value.get("skipped_reason"), "not_skipped_fixture_selected_for_metadata_observation"),
                    "metadata_capture_only": True,
                },
                citations,
            )
        )
        slots.append(
            _slot(
                slot_prefix + "-rate-limit",
                "rate_limit_observation",
                source_id,
                dict(batch_value.get("rate_limit_decision", {})) if isinstance(batch_value.get("rate_limit_decision"), Mapping) else {},
                citations + _citations(batch_value.get("rate_limit_decision"), "public_recrawl_live_dry_run_plan_v2.rate_limit_decision"),
            )
        )

    stop_citations = _citations(public_plan, "public_recrawl_live_dry_run_plan_v2.operator_stop_conditions") + _citations(
        authorization_ledger,
        "post_briefing_dry_run_authorization_ledger_v2.independent_abort_conditions",
    )
    slots.append(
        _slot(
            "slot-operator-stop-condition",
            "operator_stop_condition",
            "public-recrawl-dry-run",
            {
                "public_plan_stop_conditions": _text_list(public_plan.get("operator_stop_conditions")),
                "ledger_abort_condition_ids": _field_values(authorization_ledger.get("independent_abort_conditions"), "condition_id"),
            },
            stop_citations,
        )
    )
    slots.append(
        _slot(
            "slot-offline-validation-commands",
            "offline_validation_commands",
            "public-recrawl-dry-run",
            {
                "public_plan_commands": _argv_lists(public_plan.get("offline_validation_commands")),
                "authorization_ledger_commands": _argv_lists(authorization_ledger.get("allowed_offline_validation_commands")),
            },
            _citations(public_plan, "public_recrawl_live_dry_run_plan_v2.offline_validation_commands")
            + _citations(authorization_ledger, "post_briefing_dry_run_authorization_ledger_v2.allowed_offline_validation_commands"),
        )
    )

    for attestation_id in sorted(REQUIRED_ATTESTATIONS):
        slots.append(
            _slot(
                "slot-attestation-" + attestation_id.replace("_", "-"),
                "attestation",
                "public-recrawl-dry-run",
                {
                    "attestation_id": attestation_id,
                    "attested": public_plan.get("attestations", {}).get(attestation_id) is True,
                },
                _citations(public_plan, "public_recrawl_live_dry_run_plan_v2.attestations." + attestation_id),
            )
        )

    envelope = {
        "packet_type": PACKET_TYPE,
        "version": PACKET_VERSION,
        "envelope_id": "public-recrawl-dry-run-evidence-envelope-v2-fixture-20260529",
        "mode": MODE,
        "fixture_first": True,
        "metadata_only": True,
        "consumes": [
            _consumed_row("public_recrawl_live_dry_run_plan_v2", public_plan),
            _consumed_row("post_briefing_dry_run_authorization_ledger_v2", authorization_ledger),
        ],
        "observation_slots": slots,
        "attestations": {key: True for key in sorted(REQUIRED_ATTESTATIONS)},
        "side_effects": {
            "live_crawl_performed": False,
            "live_network_invoked": False,
            "processor_invoked": False,
            "raw_body_persisted": False,
            "document_downloaded": False,
            "source_registry_mutated": False,
            "registry_mutated": False,
            "download_performed": False,
        },
    }
    result = validate_public_recrawl_dry_run_evidence_envelope_v2(envelope)
    if not result.valid:
        raise ValueError("invalid public recrawl dry-run evidence envelope v2: " + "; ".join(result.errors))
    return envelope


def validate_public_recrawl_dry_run_evidence_envelope_v2(envelope: Mapping[str, Any]) -> EvidenceEnvelopeValidationResult:
    """Validate the evidence envelope contract without side effects."""

    errors: list[str] = []
    if envelope.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be " + PACKET_TYPE)
    if envelope.get("version") != PACKET_VERSION:
        errors.append("version must be v2")
    if envelope.get("mode") != MODE:
        errors.append("mode must be " + MODE)
    if envelope.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if envelope.get("metadata_only") is not True:
        errors.append("metadata_only must be true")

    consumed_keys = set(_field_values(envelope.get("consumes"), "source_key"))
    for key in REQUIRED_SOURCE_KEYS:
        if key not in consumed_keys:
            errors.append("consumes missing " + key)

    slots = _sequence(envelope.get("observation_slots"))
    if not slots:
        errors.append("observation_slots must be a non-empty list")
    slot_kinds: set[str] = set()
    attested_ids: set[str] = set()
    for index, slot_value in enumerate(slots):
        prefix = "observation_slots[" + str(index) + "]"
        if not isinstance(slot_value, Mapping):
            errors.append(prefix + " must be an object")
            continue
        slot_kind = _text(slot_value.get("slot_kind"))
        slot_kinds.add(slot_kind)
        for field_name in ("slot_id", "slot_kind", "source_id"):
            if not _text(slot_value.get(field_name)):
                errors.append(prefix + "." + field_name + " is required")
        if slot_value.get("metadata_only") is not True:
            errors.append(prefix + ".metadata_only must be true")
        if not _text_list(slot_value.get("citations")):
            errors.append(prefix + ".citations must be non-empty")
        if not isinstance(slot_value.get("observed_value"), Mapping):
            errors.append(prefix + ".observed_value must be an object")
        elif slot_kind == "attestation":
            observed = slot_value["observed_value"]
            attestation_id = _text(observed.get("attestation_id"))
            if attestation_id:
                attested_ids.add(attestation_id)
            if observed.get("attested") is not True:
                errors.append(prefix + ".observed_value.attested must be true")

    missing_slot_kinds = REQUIRED_SLOT_KINDS.difference(slot_kinds)
    if missing_slot_kinds:
        errors.append("missing observation slot kinds: " + ", ".join(sorted(missing_slot_kinds)))
    missing_attestations = REQUIRED_ATTESTATIONS.difference(attested_ids)
    if missing_attestations:
        errors.append("missing attestation slots: " + ", ".join(sorted(missing_attestations)))

    attestations = envelope.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
    else:
        for key in REQUIRED_ATTESTATIONS:
            if attestations.get(key) is not True:
                errors.append("attestations." + key + " must be true")

    _collect_forbidden_true_values(envelope, "envelope", errors)
    return EvidenceEnvelopeValidationResult(valid=not errors, errors=tuple(errors))


def require_valid_public_recrawl_dry_run_evidence_envelope_v2(envelope: Mapping[str, Any]) -> None:
    result = validate_public_recrawl_dry_run_evidence_envelope_v2(envelope)
    if not result.valid:
        raise ValueError("invalid public recrawl dry-run evidence envelope v2: " + "; ".join(result.errors))


def _slot(slot_id: str, slot_kind: str, source_id: str, observed_value: Mapping[str, Any], citations: Sequence[Any]) -> dict[str, Any]:
    return {
        "slot_id": slot_id,
        "slot_kind": slot_kind,
        "source_id": source_id,
        "metadata_only": True,
        "observed_value": dict(observed_value),
        "citations": _dedupe([str(item) for item in citations if str(item).strip()]),
    }


def _consumed_row(source_key: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_key": source_key,
        "packet_id": _packet_id(packet),
        "packet_type": _text(packet.get("packet_type"), _text(packet.get("mode"), "fixture")),
        "metadata_only": True,
        "citations": _citations(packet, source_key),
    }


def _packet_id(packet: Mapping[str, Any]) -> str:
    for key in ("packet_id", "plan_id", "ledger_id", "envelope_id", "id"):
        value = packet.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return "unknown-fixture-packet"


def _citations(value: Any, fallback: str) -> list[str]:
    if isinstance(value, Mapping):
        for key in ("citations", "citation_refs", "source_evidence_ids"):
            items = value.get(key)
            citations = _text_list(items)
            if citations:
                return citations
    return [fallback]


def _content_type_hint(batch: Mapping[str, Any]) -> str | None:
    expected_capture = batch.get("expected_capture")
    if isinstance(expected_capture, Mapping):
        hint = expected_capture.get("content_type_hint")
        if isinstance(hint, str) and hint.strip():
            return hint
    return None


def _argv_lists(value: Any) -> list[list[str]]:
    commands: list[list[str]] = []
    for item in _sequence(value):
        if isinstance(item, list) and all(isinstance(part, str) and part for part in item):
            commands.append(list(item))
    return commands


def _field_values(items: Any, field_name: str) -> list[str]:
    values: list[str] = []
    for item in _sequence(items):
        if isinstance(item, Mapping):
            value = item.get(field_name)
            if isinstance(value, str) and value.strip():
                values.append(value)
    return values


def _collect_forbidden_true_values(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = path + "." + str(key)
            if key in _FORBIDDEN_TRUE_KEYS and child is not False:
                errors.append(child_path + " must be false")
            _collect_forbidden_true_values(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _collect_forbidden_true_values(child, path + "[" + str(index) + "]", errors)


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(label + " must be a mapping")
    return value


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _text_list(value: Any) -> list[str]:
    return [str(item).strip() for item in _sequence(value) if str(item).strip()]


def _dedupe(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


__all__ = [
    "PACKET_TYPE",
    "PACKET_VERSION",
    "REQUIRED_ATTESTATIONS",
    "REQUIRED_SLOT_KINDS",
    "EvidenceEnvelopeValidationResult",
    "build_public_recrawl_dry_run_evidence_envelope_v2",
    "require_valid_public_recrawl_dry_run_evidence_envelope_v2",
    "validate_public_recrawl_dry_run_evidence_envelope_v2",
]
