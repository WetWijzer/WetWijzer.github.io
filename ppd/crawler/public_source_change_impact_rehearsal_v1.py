from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from urllib.parse import parse_qsl, urlparse

PACKET_TYPE = 'ppd_public_source_change_impact_rehearsal'
PACKET_VERSION = '1.0'

_MUTATION_KEYS = {
    'activesourcemutation', 'sourcemutationactive', 'sourcemutationallowed', 'sourceupdated',
    'activerequirementmutation', 'requirementmutationactive', 'requirementmutationallowed', 'requirementupdated',
    'activeprocessmutation', 'processmutationactive', 'processmutationallowed', 'processupdated',
    'activeguardrailmutation', 'guardrailmutationactive', 'guardrailmutationallowed', 'guardrailupdated',
    'activemonitoringmutation', 'monitoringmutationactive', 'monitoringmutationallowed', 'monitoringupdated',
    'activereleasestatemutation', 'releasestatemutationactive', 'releasestatemutationallowed', 'releasestateupdated',
    'activeagentstatemutation', 'agentstatemutationactive', 'agentstatemutationallowed', 'agentstateupdated',
}
_PROCESSOR_KEYS = {'processorcompleted', 'processorcomplete', 'processorruncompleted', 'processorcompletionclaimed'}
_FORBIDDEN_MARKERS = (
    'raw_body', 'raw-body', 'rawbody', '/raw/', 'raw_crawl', 'downloaded_document',
    'downloaded-document', 'downloaded_documents', 'downloaded-documents', '/downloads/',
    'file://', 'warc://', '.warc', 'processor_output', 'processor-output', 'processor_outputs',
)
_PROCESSOR_MARKERS = ('processor completed', 'processor finished', 'processor succeeded', 'processor run completed')
_GUARANTEE_MARKERS = (
    'guarantees approval', 'guaranteed approval', 'will be approved', 'shall be approved',
    'permit will be issued', 'permit shall be issued', 'legal outcome is guaranteed',
    'permitting outcome is guaranteed', 'approval is certain', 'issuance is certain',
)
_AUTH_QUERY_KEYS = {'access_token', 'auth', 'authorization', 'cookie', 'password', 'session', 'token'}
_AUTH_PATH_MARKERS = ('/login', '/signin', '/sign-in', '/auth', '/oauth', '/session')


@dataclass(frozen=True)
class PublicSourceChangeImpactRehearsalValidationResult:
    valid: bool
    errors: tuple[str, ...]


class PublicSourceChangeImpactRehearsalError(ValueError):
    pass


def build_public_source_change_impact_rehearsal_v1() -> dict[str, Any]:
    packet = {
        'packet_type': PACKET_TYPE,
        'packet_version': PACKET_VERSION,
        'packet_id': 'fixture-public-source-change-impact-rehearsal-001',
        'generated_at': '2026-05-30T00:00:00Z',
        'fixture_first': True,
        'rehearsal_only': True,
        'source_mutation_active': False,
        'requirement_mutation_active': False,
        'process_mutation_active': False,
        'guardrail_mutation_active': False,
        'monitoring_mutation_active': False,
        'release_state_mutation_active': False,
        'agent_state_mutation_active': False,
        'source_registry_snapshot': [
            {
                'source_id': 'ppd-submit-plans-online',
                'canonical_url': 'https://www.portland.gov/ppd/get-permit/submit-plans-online',
                'freshness_status': 'fixture_current',
            }
        ],
        'requirement_registry_snapshot': [
            {
                'requirement_id': 'req-single-pdf-process-separate-supporting-documents',
                'source_id': 'ppd-submit-plans-online',
                'requirement_type': 'document_requirement',
            }
        ],
        'impact_rows': [
            {
                'impact_id': 'impact-single-pdf-supporting-documents',
                'source_id': 'ppd-submit-plans-online',
                'affected_requirement_ids': ['req-single-pdf-process-separate-supporting-documents'],
                'impact_summary': 'A public wording change would require human review before guardrail update.',
                'freshness_rationale': 'Fixture freshness is explicit and no live crawl was performed.',
                'change_rationale': 'The rehearsal describes citation-level impact without mutating active artifacts.',
                'citations': [
                    {
                        'source_id': 'ppd-submit-plans-online',
                        'requirement_id': 'req-single-pdf-process-separate-supporting-documents',
                        'public_url': 'https://www.portland.gov/ppd/get-permit/submit-plans-online',
                        'span_ref': 'fixture-span-single-pdf-001',
                        'quoted_or_paraphrased_basis': 'Plans are grouped as one PDF while supporting documents remain separate PDFs.',
                    }
                ],
                'operator_review_required': True,
                'outcome_guarantee_provided': False,
                'processor_completion_claimed': False,
            }
        ],
        'rehearsal_summary': {
            'impact_row_count': 1,
            'source_mutation_active': False,
            'requirement_mutation_active': False,
            'process_mutation_active': False,
            'guardrail_mutation_active': False,
            'monitoring_mutation_active': False,
            'release_state_mutation_active': False,
            'agent_state_mutation_active': False,
        },
    }
    require_valid_public_source_change_impact_rehearsal_v1(packet)
    return packet


def validate_public_source_change_impact_rehearsal_v1(packet: Mapping[str, Any]) -> PublicSourceChangeImpactRehearsalValidationResult:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return PublicSourceChangeImpactRehearsalValidationResult(False, ('packet must be an object',))
    _collect_forbidden_content(packet, '$', errors)
    if packet.get('packet_type') != PACKET_TYPE:
        errors.append('packet_type must be ' + PACKET_TYPE)
    if packet.get('packet_version') != PACKET_VERSION:
        errors.append('packet_version must be ' + PACKET_VERSION)
    if not _text(packet.get('packet_id')):
        errors.append('packet_id is required')
    if not _text(packet.get('generated_at')).endswith('Z'):
        errors.append('generated_at must end in Z')
    for key in ('fixture_first', 'rehearsal_only'):
        if packet.get(key) is not True:
            errors.append(key + ' must be true')
    for key in _top_level_mutation_flags():
        if packet.get(key) is not False:
            errors.append(key + ' must be false')
    source_ids = _registry_ids(packet.get('source_registry_snapshot'), 'source_id', 'source_registry_snapshot', errors)
    requirement_ids = _registry_ids(packet.get('requirement_registry_snapshot'), 'requirement_id', 'requirement_registry_snapshot', errors)
    rows = _require_list(packet.get('impact_rows'), 'impact_rows', errors)
    if not rows:
        errors.append('impact_rows must include at least one row')
    for index, row in enumerate(rows):
        _validate_impact_row(row, index, source_ids, requirement_ids, errors)
    summary = packet.get('rehearsal_summary')
    if not isinstance(summary, Mapping):
        errors.append('rehearsal_summary must be an object')
    else:
        if summary.get('impact_row_count') != len(rows):
            errors.append('rehearsal_summary.impact_row_count must match impact_rows count')
        for key in _top_level_mutation_flags():
            if summary.get(key) is not False:
                errors.append('rehearsal_summary.' + key + ' must be false')
    return PublicSourceChangeImpactRehearsalValidationResult(not errors, tuple(dict.fromkeys(errors)))


def require_valid_public_source_change_impact_rehearsal_v1(packet: Mapping[str, Any]) -> None:
    result = validate_public_source_change_impact_rehearsal_v1(packet)
    if not result.valid:
        raise PublicSourceChangeImpactRehearsalError('; '.join(result.errors))


def _validate_impact_row(row: Any, index: int, source_ids: set[str], requirement_ids: set[str], errors: list[str]) -> None:
    prefix = 'impact_rows[' + str(index) + ']'
    if not isinstance(row, Mapping):
        errors.append(prefix + ' must be an object')
        return
    source_id = _text(row.get('source_id'))
    affected = _text_list(row.get('affected_requirement_ids'))
    citations = _require_list(row.get('citations'), prefix + '.citations', errors)
    for key in ('impact_id', 'impact_summary'):
        if not _text(row.get(key)):
            errors.append(prefix + '.' + key + ' is required')
    if not source_id:
        errors.append(prefix + '.source_id is required')
    elif source_id not in source_ids:
        errors.append(prefix + '.source_id references unknown source_id ' + source_id)
    if not affected:
        errors.append(prefix + '.affected_requirement_ids must not be empty')
    for requirement_id in affected:
        if requirement_id not in requirement_ids:
            errors.append(prefix + '.affected_requirement_ids references unknown requirement_id ' + requirement_id)
    if not _text(row.get('freshness_rationale')):
        errors.append(prefix + '.freshness_rationale is required')
    if not _text(row.get('change_rationale')):
        errors.append(prefix + '.change_rationale is required')
    if not citations:
        errors.append(prefix + '.citations must include at least one cited public source span')
    cited_sources: set[str] = set()
    cited_requirements: set[str] = set()
    for citation_index, citation in enumerate(citations):
        citation_prefix = prefix + '.citations[' + str(citation_index) + ']'
        if not isinstance(citation, Mapping):
            errors.append(citation_prefix + ' must be an object')
            continue
        citation_source = _text(citation.get('source_id'))
        citation_requirement = _text(citation.get('requirement_id'))
        if citation_source not in source_ids:
            errors.append(citation_prefix + '.source_id references unknown source_id ' + (citation_source or ''))
        else:
            cited_sources.add(citation_source)
        if citation_requirement not in requirement_ids:
            errors.append(citation_prefix + '.requirement_id references unknown requirement_id ' + (citation_requirement or ''))
        else:
            cited_requirements.add(citation_requirement)
        for key in ('public_url', 'span_ref', 'quoted_or_paraphrased_basis'):
            if not _text(citation.get(key)):
                errors.append(citation_prefix + '.' + key + ' is required')
    if source_id and source_id not in cited_sources:
        errors.append(prefix + '.citations must cite the row source_id')
    missing = [requirement_id for requirement_id in affected if requirement_id not in cited_requirements]
    if missing:
        errors.append(prefix + '.citations must cite every affected requirement_id: ' + ', '.join(missing))


def _registry_ids(value: Any, id_field: str, field_name: str, errors: list[str]) -> set[str]:
    rows = _require_list(value, field_name, errors)
    ids: set[str] = set()
    if not rows:
        errors.append(field_name + ' must include at least one row')
    for index, row in enumerate(rows):
        prefix = field_name + '[' + str(index) + ']'
        if not isinstance(row, Mapping):
            errors.append(prefix + ' must be an object')
            continue
        identifier = _text(row.get(id_field))
        if not identifier:
            errors.append(prefix + '.' + id_field + ' is required')
        elif identifier in ids:
            errors.append(prefix + '.' + id_field + ' duplicates ' + identifier)
        else:
            ids.add(identifier)
    return ids


def _collect_forbidden_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = _normalized_key(str(key))
            if normalized in _MUTATION_KEYS and child not in (None, '', [], {}, False):
                errors.append(path + '.' + str(key) + ' must be false or empty; rehearsal packets cannot mutate active state')
            if normalized in _PROCESSOR_KEYS and child not in (None, '', [], {}, False):
                errors.append(path + '.' + str(key) + ' must be false or empty; processor completion claims are not allowed')
            _collect_forbidden_content(child, path + '.' + str(key), errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _collect_forbidden_content(child, path + '[' + str(index) + ']', errors)
    elif isinstance(value, str):
        lower = value.lower()
        for marker in _FORBIDDEN_MARKERS:
            if marker in lower:
                errors.append(path + ' contains forbidden raw body, downloaded-document, archive, or processor-output reference ' + marker)
        if any(marker in lower for marker in _PROCESSOR_MARKERS):
            errors.append(path + ' contains a forbidden processor completion claim')
        if any(marker in lower for marker in _GUARANTEE_MARKERS):
            errors.append(path + ' contains a forbidden legal or permitting outcome guarantee')
        if _looks_authenticated_url(value):
            errors.append(path + ' contains an authenticated or credential-bearing URL')


def _looks_authenticated_url(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme not in {'http', 'https'}:
        return False
    if parsed.username or parsed.password:
        return True
    if any(marker in parsed.path.lower() for marker in _AUTH_PATH_MARKERS):
        return True
    query_keys = {key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    return bool(query_keys & _AUTH_QUERY_KEYS)


def _top_level_mutation_flags() -> tuple[str, ...]:
    return (
        'source_mutation_active', 'requirement_mutation_active', 'process_mutation_active',
        'guardrail_mutation_active', 'monitoring_mutation_active', 'release_state_mutation_active',
        'agent_state_mutation_active',
    )


def _require_list(value: Any, field: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(field + ' must be a list')
        return []
    return value


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [_text(row) for row in value if _text(row)]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _normalized_key(value: str) -> str:
    return ''.join(character for character in value.lower() if character.isalnum())


__all__ = [
    'PACKET_TYPE',
    'PACKET_VERSION',
    'PublicSourceChangeImpactRehearsalError',
    'PublicSourceChangeImpactRehearsalValidationResult',
    'build_public_source_change_impact_rehearsal_v1',
    'require_valid_public_source_change_impact_rehearsal_v1',
    'validate_public_source_change_impact_rehearsal_v1',
]
