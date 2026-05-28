"""Validation for PP&D process-model assembly packets.

The validator is intentionally side-effect free and accepts plain dictionaries or
small dataclass-like objects so assembly code can run it before promoting a
packet into a compiled process model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Iterable, Mapping, Sequence


CONSEQUENTIAL_STAGE_TERMS = (
    "acknowledgement",
    "cancel",
    "certification",
    "correction upload",
    "fee payment",
    "inspection scheduling",
    "payment",
    "schedule inspection",
    "submission",
    "submit",
    "upload corrections",
    "upload staging",
)

EVIDENCE_DATE_FIELDS = (
    "last_seen_at",
    "captured_at",
    "capture_finished_at",
    "verified_at",
    "last_verified_at",
    "updated_at",
)


@dataclass(frozen=True)
class ValidationIssue:
    """A deterministic validation issue emitted for an assembly packet."""

    code: str
    message: str
    path: str


@dataclass(frozen=True)
class ValidationResult:
    """Validation result for a process-model assembly packet."""

    ok: bool
    issues: tuple[ValidationIssue, ...]

    def raise_for_issues(self) -> None:
        if self.issues:
            joined = "; ".join(f"{issue.code} at {issue.path}" for issue in self.issues)
            raise ValueError(joined)


def validate_process_model_assembly_packet(
    packet: Any,
    *,
    max_evidence_age_days: int = 90,
    now: datetime | date | None = None,
) -> ValidationResult:
    """Validate a process-model assembly packet before promotion.

    The checks cover the hard process-model safety invariants used by PP&D:
    every requirement must cite known source evidence, every stage must be
    evidenced, unsupported paths must be represented, file and document rules
    must carry citations, consequential stages must have action gates, evidence
    must be fresh, and asserted guardrail bundle IDs must resolve to compiled
    predicates.
    """

    current_date = _coerce_date(now) or datetime.now(timezone.utc).date()
    issues: list[ValidationIssue] = []

    process_model = _get(packet, "process_model", None) or _get(packet, "process", None) or packet
    requirements = _as_sequence(
        _get(packet, "requirements", None)
        or _get(packet, "requirement_nodes", None)
        or _get(process_model, "requirements", None)
    )
    stages = _as_sequence(_get(process_model, "stages", None))
    file_rules = _as_sequence(_get(process_model, "file_rules", None))
    document_rules = _as_sequence(
        _get(process_model, "required_documents", None)
        or _get(process_model, "document_rules", None)
    )

    evidence_items = _collect_evidence_items(packet, process_model)
    known_evidence_ids = {evidence_id for evidence_id, _item in evidence_items if evidence_id}

    for index, requirement in enumerate(requirements):
        cited_ids = _citation_ids(requirement)
        requirement_id = _get(requirement, "requirement_id", None) or _get(requirement, "id", None) or str(index)
        path = f"requirements[{index}]"
        if not cited_ids:
            issues.append(
                ValidationIssue(
                    "orphan_requirement",
                    f"Requirement {requirement_id} has no source evidence citation.",
                    path,
                )
            )
        elif known_evidence_ids and not cited_ids.intersection(known_evidence_ids):
            issues.append(
                ValidationIssue(
                    "orphan_requirement",
                    f"Requirement {requirement_id} cites evidence not present in the packet.",
                    path,
                )
            )

    for index, stage in enumerate(stages):
        stage_name = str(_get(stage, "stage", None) or _get(stage, "name", None) or _get(stage, "process_stage", None) or index)
        path = f"process_model.stages[{index}]"
        if not _citation_ids(stage):
            issues.append(
                ValidationIssue(
                    "stage_without_evidence",
                    f"Stage {stage_name} has no source evidence citation.",
                    path,
                )
            )
        if _is_consequential_stage(stage) and not _has_action_gate(stage):
            issues.append(
                ValidationIssue(
                    "consequential_stage_without_action_gate",
                    f"Consequential stage {stage_name} has no action gate.",
                    path,
                )
            )

    unsupported_paths = _as_sequence(_get(process_model, "unsupported_paths", None))
    if not unsupported_paths:
        issues.append(
            ValidationIssue(
                "missing_unsupported_path_handling",
                "Process model must identify unsupported paths or explicitly document that none are known.",
                "process_model.unsupported_paths",
            )
        )

    _validate_rule_citations(issues, file_rules, "file_rule_without_citation", "process_model.file_rules")
    _validate_rule_citations(
        issues,
        document_rules,
        "document_rule_without_citation",
        "process_model.required_documents",
    )
    _validate_evidence_freshness(issues, evidence_items, current_date, max_evidence_age_days)
    _validate_guardrail_bundles(issues, packet, process_model)

    return ValidationResult(ok=not issues, issues=tuple(issues))


def assert_valid_process_model_assembly_packet(packet: Any, **kwargs: Any) -> None:
    """Raise ValueError when a process-model assembly packet is invalid."""

    validate_process_model_assembly_packet(packet, **kwargs).raise_for_issues()


def _get(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(key, default)
    return getattr(value, key, default)


def _as_sequence(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        return (value,)
    if isinstance(value, Mapping):
        return tuple(value.values())
    if isinstance(value, Sequence):
        return tuple(value)
    return (value,)


def _collect_evidence_items(packet: Any, process_model: Any) -> tuple[tuple[str | None, Any], ...]:
    raw_sources = (
        _get(packet, "source_evidence", None)
        or _get(packet, "source_evidence_items", None)
        or _get(packet, "evidence", None)
        or _get(process_model, "source_evidence", None)
        or _get(process_model, "evidence", None)
    )
    items: list[tuple[str | None, Any]] = []
    if isinstance(raw_sources, Mapping):
        for key, item in raw_sources.items():
            evidence_id = _get(item, "source_evidence_id", None) or _get(item, "evidence_id", None) or _get(item, "id", None) or str(key)
            items.append((str(evidence_id), item))
    else:
        for item in _as_sequence(raw_sources):
            evidence_id = _get(item, "source_evidence_id", None) or _get(item, "evidence_id", None) or _get(item, "id", None)
            items.append((str(evidence_id) if evidence_id is not None else None, item))
    return tuple(items)


def _citation_ids(value: Any) -> set[str]:
    citations: set[str] = set()
    for field in (
        "source_evidence_ids",
        "evidence_ids",
        "citation_ids",
        "citations",
        "source_ids",
        "document_rule_citations",
        "file_rule_citations",
    ):
        raw = _get(value, field, None)
        for item in _as_sequence(raw):
            if isinstance(item, Mapping):
                citation_id = item.get("source_evidence_id") or item.get("evidence_id") or item.get("id")
                if citation_id:
                    citations.add(str(citation_id))
            elif item is not None:
                citations.add(str(item))
    return citations


def _validate_rule_citations(
    issues: list[ValidationIssue],
    rules: Iterable[Any],
    code: str,
    base_path: str,
) -> None:
    for index, rule in enumerate(rules):
        if not _citation_ids(rule):
            label = _get(rule, "rule_id", None) or _get(rule, "document_id", None) or _get(rule, "name", None) or index
            issues.append(
                ValidationIssue(
                    code,
                    f"Rule {label} has no source citation.",
                    f"{base_path}[{index}]",
                )
            )


def _is_consequential_stage(stage: Any) -> bool:
    text_parts = [
        _get(stage, "stage", None),
        _get(stage, "name", None),
        _get(stage, "process_stage", None),
        _get(stage, "action", None),
        _get(stage, "description", None),
    ]
    text = " ".join(str(part).lower() for part in text_parts if part is not None)
    return any(term in text for term in CONSEQUENTIAL_STAGE_TERMS)


def _has_action_gate(stage: Any) -> bool:
    gate_fields = (
        "action_gate",
        "action_gate_id",
        "action_gates",
        "required_confirmations",
        "exact_confirmation_predicates",
        "requires_exact_confirmation",
    )
    for field in gate_fields:
        value = _get(stage, field, None)
        if value is True:
            return True
        if isinstance(value, str) and value.strip():
            return True
        if _as_sequence(value):
            return True
    return False


def _validate_evidence_freshness(
    issues: list[ValidationIssue],
    evidence_items: Iterable[tuple[str | None, Any]],
    current_date: date,
    max_evidence_age_days: int,
) -> None:
    for index, (evidence_id, evidence) in enumerate(evidence_items):
        evidence_date = None
        for field in EVIDENCE_DATE_FIELDS:
            evidence_date = _coerce_date(_get(evidence, field, None))
            if evidence_date is not None:
                break
        if evidence_date is None:
            continue
        age_days = (current_date - evidence_date).days
        if age_days > max_evidence_age_days:
            label = evidence_id or str(index)
            issues.append(
                ValidationIssue(
                    "stale_source_evidence",
                    f"Source evidence {label} is {age_days} days old.",
                    f"source_evidence[{index}]",
                )
            )


def _validate_guardrail_bundles(issues: list[ValidationIssue], packet: Any, process_model: Any) -> None:
    asserted_ids = set()
    raw_id = _get(process_model, "guardrail_bundle_id", None)
    if raw_id:
        asserted_ids.add(str(raw_id))
    for item in _as_sequence(_get(process_model, "guardrail_bundle_ids", None)):
        if item:
            asserted_ids.add(str(item))
    if not asserted_ids:
        return

    bundles_by_id: dict[str, Any] = {}
    raw_bundles = _get(packet, "guardrail_bundles", None) or _get(packet, "compiled_guardrail_bundles", None)
    if isinstance(raw_bundles, Mapping):
        for key, bundle in raw_bundles.items():
            bundle_id = _get(bundle, "guardrail_bundle_id", None) or _get(bundle, "id", None) or key
            bundles_by_id[str(bundle_id)] = bundle
    else:
        for bundle in _as_sequence(raw_bundles):
            bundle_id = _get(bundle, "guardrail_bundle_id", None) or _get(bundle, "id", None)
            if bundle_id:
                bundles_by_id[str(bundle_id)] = bundle

    for bundle_id in sorted(asserted_ids):
        bundle = bundles_by_id.get(bundle_id)
        if bundle is None:
            issues.append(
                ValidationIssue(
                    "guardrail_bundle_without_compiled_predicates",
                    f"Guardrail bundle {bundle_id} is asserted but no compiled bundle is present.",
                    "process_model.guardrail_bundle_id",
                )
            )
            continue
        predicate_fields = (
            "compiled_predicates",
            "deterministic_predicates",
            "reversible_action_predicates",
            "exact_confirmation_predicates",
            "refused_action_predicates",
        )
        if not any(_as_sequence(_get(bundle, field, None)) for field in predicate_fields):
            issues.append(
                ValidationIssue(
                    "guardrail_bundle_without_compiled_predicates",
                    f"Guardrail bundle {bundle_id} has no compiled predicates.",
                    f"guardrail_bundles.{bundle_id}",
                )
            )


def _coerce_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(text).date()
        except ValueError:
            try:
                return date.fromisoformat(text[:10])
            except ValueError:
                return None
    return None
