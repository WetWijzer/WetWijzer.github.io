'''Fixture-first requirement delta review and formalization gate for PP&D requirements.'''

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

READY_HUMAN_REVIEW_STATUSES = frozenset({'accepted', 'approved', 'reviewed', 'human_reviewed'})
FRESH_CITATION_STATUSES = frozenset({'current', 'fresh', 'verified'})
SUPPORTED_PATH_STATUSES = frozenset({'supported', 'ready', 'validated'})
SUPPORTED_PATH_KINDS = frozenset({
    'public_html_guidance',
    'public_pdf_guidance',
    'public_form_guidance',
    'devhub_public_guidance',
    'devhub_authenticated_observation',
    'official_guardrail_policy',
})

COMPARISON_FIELDS = (
    'source_evidence_ids',
    'requirement_type',
    'subject',
    'action',
    'object',
    'conditions',
    'deadline_or_temporal_scope',
    'permit_types',
    'process_stage',
    'process_ids',
    'affected_process_ids',
    'guardrail_bundle_ids',
    'citations',
    'source_citations',
    'supported_path_taxonomy',
)


@dataclass(frozen=True)
class FormalizationGateResult:
    status: str
    reasons: Tuple[str, ...]
    fresh_citation_ids: Tuple[str, ...]
    supported_path_ids: Tuple[str, ...]

    def as_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status,
            'reasons': list(self.reasons),
            'fresh_citation_ids': list(self.fresh_citation_ids),
            'supported_path_ids': list(self.supported_path_ids),
        }


@dataclass(frozen=True)
class RequirementDelta:
    delta_id: str
    delta_kind: str
    requirement_id: str
    source_id: str
    previous_source_hash: Optional[str]
    current_source_hash: Optional[str]
    previous_requirement_hash: Optional[str]
    current_requirement_hash: Optional[str]
    changed_fields: Tuple[str, ...]
    affected_process_ids: Tuple[str, ...]
    guardrail_bundle_ids: Tuple[str, ...]
    human_review_status: str
    blocked_readiness_status: str
    formalization_gate: FormalizationGateResult
    review_reason: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            'delta_id': self.delta_id,
            'delta_kind': self.delta_kind,
            'requirement_id': self.requirement_id,
            'source_id': self.source_id,
            'previous_source_hash': self.previous_source_hash,
            'current_source_hash': self.current_source_hash,
            'previous_requirement_hash': self.previous_requirement_hash,
            'current_requirement_hash': self.current_requirement_hash,
            'changed_fields': list(self.changed_fields),
            'affected_process_ids': list(self.affected_process_ids),
            'guardrail_bundle_ids': list(self.guardrail_bundle_ids),
            'human_review_status': self.human_review_status,
            'blocked_readiness_status': self.blocked_readiness_status,
            'formalization_gate': self.formalization_gate.as_dict(),
            'review_reason': self.review_reason,
        }


def load_json_snapshot(path: Path) -> Dict[str, Any]:
    with Path(path).open('r', encoding='utf-8') as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError('requirement delta fixtures must be JSON objects')
    return data


def load_requirement_delta_review_queue(previous_path: Path, current_path: Path) -> Dict[str, Any]:
    return build_requirement_delta_review_queue(
        load_json_snapshot(previous_path),
        load_json_snapshot(current_path),
    )


def build_requirement_delta_review_queue(
    previous_snapshot: Mapping[str, Any],
    current_snapshot: Mapping[str, Any],
) -> Dict[str, Any]:
    previous_sources = _source_hashes(previous_snapshot)
    current_sources = _source_hashes(current_snapshot)
    changed_source_hashes = _changed_source_hashes(previous_sources, current_sources)
    changed_source_ids = {record['source_id'] for record in changed_source_hashes}

    previous_requirements = _index_requirements(previous_snapshot)
    current_requirements = _index_requirements(current_snapshot)
    deltas: List[RequirementDelta] = []

    for requirement_id in sorted(set(previous_requirements) | set(current_requirements)):
        previous_requirement = previous_requirements.get(requirement_id)
        current_requirement = current_requirements.get(requirement_id)
        source_ids = _source_ids_for_delta(previous_requirement, current_requirement)
        if not source_ids.intersection(changed_source_ids):
            continue

        if previous_requirement is None:
            delta_kind = 'added'
            changed_fields = ('__added__',)
        elif current_requirement is None:
            delta_kind = 'removed'
            changed_fields = ('__removed__',)
        else:
            changed_fields = _changed_fields(previous_requirement, current_requirement)
            if not changed_fields:
                continue
            delta_kind = 'changed'

        source_id = _primary_source_id(current_requirement, previous_requirement)
        affected_process_ids = _affected_process_ids(previous_requirement, current_requirement)
        guardrail_bundle_ids = _guardrail_bundle_ids(previous_requirement, current_requirement)
        human_review_status = _human_review_status(previous_requirement, current_requirement)
        formalization_gate = _formalization_gate(
            current_requirement=current_requirement,
            previous_requirement=previous_requirement,
            human_review_status=human_review_status,
            affected_process_ids=affected_process_ids,
            guardrail_bundle_ids=guardrail_bundle_ids,
        )
        previous_source_hash = previous_sources.get(source_id)
        current_source_hash = current_sources.get(source_id)

        deltas.append(
            RequirementDelta(
                delta_id='delta:%s:%s:%s' % (delta_kind, source_id, requirement_id),
                delta_kind=delta_kind,
                requirement_id=requirement_id,
                source_id=source_id,
                previous_source_hash=previous_source_hash,
                current_source_hash=current_source_hash,
                previous_requirement_hash=(
                    _requirement_hash(previous_requirement) if previous_requirement is not None else None
                ),
                current_requirement_hash=(
                    _requirement_hash(current_requirement) if current_requirement is not None else None
                ),
                changed_fields=changed_fields,
                affected_process_ids=affected_process_ids,
                guardrail_bundle_ids=guardrail_bundle_ids,
                human_review_status=human_review_status,
                blocked_readiness_status=formalization_gate.status,
                formalization_gate=formalization_gate,
                review_reason=_review_reason(
                    delta_kind,
                    source_id,
                    previous_source_hash,
                    current_source_hash,
                    changed_fields,
                ),
            )
        )

    previous_snapshot_id = str(previous_snapshot.get('snapshot_id', 'previous'))
    current_snapshot_id = str(current_snapshot.get('snapshot_id', 'current'))
    return {
        'queue_id': 'requirement-delta-review:%s:%s' % (previous_snapshot_id, current_snapshot_id),
        'previous_snapshot_id': previous_snapshot_id,
        'current_snapshot_id': current_snapshot_id,
        'changed_source_hashes': changed_source_hashes,
        'delta_count': len(deltas),
        'deltas': [delta.as_dict() for delta in deltas],
    }


def _source_hashes(snapshot: Mapping[str, Any]) -> Dict[str, str]:
    value = snapshot.get('source_hashes', {})
    if not isinstance(value, MappingABC):
        raise ValueError('source_hashes must be an object keyed by source_id')
    return {str(source_id): str(source_hash) for source_id, source_hash in value.items() if source_hash is not None}


def _changed_source_hashes(
    previous_sources: Mapping[str, str],
    current_sources: Mapping[str, str],
) -> List[Dict[str, Optional[str]]]:
    records: List[Dict[str, Optional[str]]] = []
    for source_id in sorted(set(previous_sources) | set(current_sources)):
        previous_hash = previous_sources.get(source_id)
        current_hash = current_sources.get(source_id)
        if previous_hash != current_hash:
            records.append(
                {
                    'source_id': source_id,
                    'previous_hash': previous_hash,
                    'current_hash': current_hash,
                }
            )
    return records


def _index_requirements(snapshot: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    raw_requirements = snapshot.get('synthetic_requirements', [])
    if not isinstance(raw_requirements, list):
        raise ValueError('synthetic_requirements must be a list')

    indexed: Dict[str, Mapping[str, Any]] = {}
    for item in raw_requirements:
        if not isinstance(item, MappingABC):
            raise ValueError('each synthetic requirement must be an object')
        requirement_id = _requirement_id(item)
        if requirement_id in indexed:
            raise ValueError('duplicate synthetic requirement id: %s' % requirement_id)
        indexed[requirement_id] = item
    return indexed


def _requirement_id(requirement: Mapping[str, Any]) -> str:
    value = requirement.get('requirement_id')
    if value in (None, ''):
        raise ValueError('synthetic requirement is missing requirement_id')
    return str(value)


def _source_ids_for_delta(
    previous_requirement: Optional[Mapping[str, Any]],
    current_requirement: Optional[Mapping[str, Any]],
) -> Set[str]:
    source_ids: Set[str] = set()
    for requirement in (previous_requirement, current_requirement):
        if requirement is None:
            continue
        source_id = requirement.get('source_id')
        if source_id not in (None, ''):
            source_ids.add(str(source_id))
    return source_ids


def _primary_source_id(
    current_requirement: Optional[Mapping[str, Any]],
    previous_requirement: Optional[Mapping[str, Any]],
) -> str:
    for requirement in (current_requirement, previous_requirement):
        if requirement is None:
            continue
        source_id = requirement.get('source_id')
        if source_id not in (None, ''):
            return str(source_id)
    return 'unknown-source'


def _requirement_hash(requirement: Mapping[str, Any]) -> str:
    explicit_hash = requirement.get('requirement_hash')
    if explicit_hash not in (None, ''):
        return str(explicit_hash)
    payload = {field: _normalise_for_compare(requirement.get(field)) for field in COMPARISON_FIELDS}
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return 'sha256:%s' % hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def _changed_fields(
    previous_requirement: Mapping[str, Any],
    current_requirement: Mapping[str, Any],
) -> Tuple[str, ...]:
    fields: List[str] = []
    for field in COMPARISON_FIELDS:
        if _normalise_for_compare(previous_requirement.get(field)) != _normalise_for_compare(current_requirement.get(field)):
            fields.append(field)
    if not fields and _requirement_hash(previous_requirement) != _requirement_hash(current_requirement):
        fields.append('requirement_hash')
    return tuple(fields)


def _normalise_for_compare(value: Any) -> Any:
    if isinstance(value, MappingABC):
        return {str(key): _normalise_for_compare(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple, set)):
        normalised = [_normalise_for_compare(item) for item in value]
        return sorted(normalised, key=lambda item: json.dumps(item, sort_keys=True, separators=(',', ':')))
    return value


def _affected_process_ids(
    previous_requirement: Optional[Mapping[str, Any]],
    current_requirement: Optional[Mapping[str, Any]],
) -> Tuple[str, ...]:
    values: List[Any] = []
    for requirement in (previous_requirement, current_requirement):
        if requirement is None:
            continue
        values.extend(_as_list(requirement.get('process_ids')))
        values.extend(_as_list(requirement.get('affected_process_ids')))
    return _clean_strings(values)


def _guardrail_bundle_ids(
    previous_requirement: Optional[Mapping[str, Any]],
    current_requirement: Optional[Mapping[str, Any]],
) -> Tuple[str, ...]:
    values: List[Any] = []
    for requirement in (previous_requirement, current_requirement):
        if requirement is None:
            continue
        values.extend(_as_list(requirement.get('guardrail_bundle_ids')))
    return _clean_strings(values)


def _human_review_status(
    previous_requirement: Optional[Mapping[str, Any]],
    current_requirement: Optional[Mapping[str, Any]],
) -> str:
    if current_requirement is not None:
        value = current_requirement.get('human_review_status')
        return str(value) if value not in (None, '') else 'needs_review'
    if previous_requirement is not None:
        value = previous_requirement.get('removal_human_review_status')
        return str(value) if value not in (None, '') else 'needs_review'
    return 'needs_review'


def _formalization_gate(
    current_requirement: Optional[Mapping[str, Any]],
    previous_requirement: Optional[Mapping[str, Any]],
    human_review_status: str,
    affected_process_ids: Sequence[str],
    guardrail_bundle_ids: Sequence[str],
) -> FormalizationGateResult:
    requirement = current_requirement if current_requirement is not None else previous_requirement
    reasons: List[str] = []

    if human_review_status not in READY_HUMAN_REVIEW_STATUSES:
        reasons.append('pending_human_review')
    if not affected_process_ids:
        reasons.append('missing_affected_process_ids')
    if not guardrail_bundle_ids:
        reasons.append('missing_guardrail_bundle_ids')

    fresh_citation_ids = _fresh_citation_ids(requirement)
    if not fresh_citation_ids:
        reasons.append('missing_fresh_citations')
    elif _has_stale_citation(requirement):
        reasons.append('stale_citations')

    supported_path_ids = _supported_path_ids(requirement)
    if not supported_path_ids:
        reasons.append('missing_supported_path_taxonomy')
    if requirement is not None and bool(requirement.get('unsupported_path')):
        reasons.append('unsupported_requirement_path')

    if reasons:
        return FormalizationGateResult(
            status='blocked_' + reasons[0],
            reasons=tuple(dict.fromkeys(reasons)),
            fresh_citation_ids=fresh_citation_ids,
            supported_path_ids=supported_path_ids,
        )
    return FormalizationGateResult(
        status='ready',
        reasons=(),
        fresh_citation_ids=fresh_citation_ids,
        supported_path_ids=supported_path_ids,
    )


def _fresh_citation_ids(requirement: Optional[Mapping[str, Any]]) -> Tuple[str, ...]:
    citation_ids: List[str] = []
    for citation in _citation_records(requirement):
        citation_id = _citation_id(citation)
        if citation_id and _normalised_status(citation.get('freshness_status')) in FRESH_CITATION_STATUSES:
            citation_ids.append(citation_id)
    return _clean_strings(citation_ids)


def _has_stale_citation(requirement: Optional[Mapping[str, Any]]) -> bool:
    records = _citation_records(requirement)
    if not records:
        return False
    for citation in records:
        if _normalised_status(citation.get('freshness_status')) not in FRESH_CITATION_STATUSES:
            return True
    return False


def _citation_records(requirement: Optional[Mapping[str, Any]]) -> Tuple[Mapping[str, Any], ...]:
    if requirement is None:
        return ()
    records: List[Mapping[str, Any]] = []
    for field in ('citations', 'source_citations', 'citation_spans'):
        for item in _as_list(requirement.get(field)):
            if isinstance(item, MappingABC):
                records.append(item)
    return tuple(records)


def _citation_id(citation: Mapping[str, Any]) -> str:
    for field in ('citation_id', 'evidence_id', 'source_evidence_id', 'id'):
        value = citation.get(field)
        if value not in (None, ''):
            return str(value)
    return ''


def _supported_path_ids(requirement: Optional[Mapping[str, Any]]) -> Tuple[str, ...]:
    if requirement is None:
        return ()
    path_ids: List[str] = []
    for index, item in enumerate(_as_list(requirement.get('supported_path_taxonomy'))):
        if isinstance(item, MappingABC):
            status = _normalised_status(item.get('support_status') or item.get('status'))
            path_kind = _normalised_status(item.get('path_kind') or item.get('kind') or item.get('category'))
            if status in SUPPORTED_PATH_STATUSES and path_kind in SUPPORTED_PATH_KINDS:
                path_ids.append(str(item.get('path_id') or item.get('id') or path_kind))
        else:
            path_kind = _normalised_status(item)
            if path_kind in SUPPORTED_PATH_KINDS:
                path_ids.append('%s[%s]' % (path_kind, index))
    return _clean_strings(path_ids)


def _review_reason(
    delta_kind: str,
    source_id: str,
    previous_source_hash: Optional[str],
    current_source_hash: Optional[str],
    changed_fields: Sequence[str],
) -> str:
    hash_change = '%s -> %s' % (_display_hash(previous_source_hash), _display_hash(current_source_hash))
    reason = '%s requirement from changed source %s (%s)' % (delta_kind, source_id, hash_change)
    if delta_kind == 'changed':
        return '%s; changed_fields=%s' % (reason, ','.join(changed_fields))
    return reason


def _display_hash(value: Optional[str]) -> str:
    return value if value is not None else 'absent'


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _clean_strings(values: Sequence[Any]) -> Tuple[str, ...]:
    cleaned = {str(value) for value in values if value not in (None, '')}
    return tuple(sorted(cleaned))


def _normalised_status(value: Any) -> str:
    if value is None:
        return ''
    return str(value).strip().lower().replace('-', '_').replace(' ', '_')
