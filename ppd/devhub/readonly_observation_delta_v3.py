'''Fixture-first DevHub read-only observation delta packet v3.'''

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import re
from typing import Any

SCHEMA_VERSION = 'devhub_readonly_observation_delta_packet_v3'
SOURCE_SCHEMA_VERSION = 'devhub_readonly_observation_notes_v3'
GENERATED_AT = '1970-01-01T00:00:00Z'

OFFLINE_VALIDATION_COMMANDS = [
    ['python3', '-m', 'py_compile', 'ppd/devhub/readonly_observation_delta_v3.py'],
    ['python3', '-m', 'pytest', 'ppd/tests/test_devhub_readonly_observation_delta_v3.py'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

PROHIBITED_KEYS = frozenset({
    'auth_artifact', 'auth_state', 'authenticated_value', 'browser_artifact',
    'browser_state', 'cookie', 'cookies', 'credential', 'credentials', 'download',
    'downloaded_document', 'downloads', 'har', 'har_data', 'har_file', 'password',
    'payment', 'private_file', 'private_page_value', 'raw_authenticated_text',
    'raw_authenticated_value', 'raw_crawl_output', 'screenshot', 'screenshots',
    'session', 'session_file', 'storage_state', 'trace', 'trace_file', 'trace_path',
    'traces', 'upload', 'uploads',
})
ACTIVE_MUTATION_KEYS = frozenset({
    'active_contract_mutation', 'active_devhub_surface_mutation',
    'active_guardrail_mutation', 'active_process_model_mutation',
    'active_prompt_mutation', 'active_release_state_mutation',
    'active_source_mutation', 'active_source_registry_mutation',
    'contract_mutation_enabled', 'devhub_surface_mutation_enabled',
    'guardrail_mutation_enabled', 'process_model_mutation_enabled',
    'prompt_mutation_enabled', 'release_state_mutation_enabled',
    'source_mutation_enabled', 'source_registry_mutation_enabled',
})
EMAIL_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.IGNORECASE)
PHONE_RE = re.compile(r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b')
PERMIT_RE = re.compile(r'\b\d{2}-\d{6}-\d{3}-\d{2}-[A-Z]{2}\b')
PRIVATE_TEXT_RE = re.compile(
    r'\b(password|bearer\s+[a-z0-9._-]+|token=|cookie=|storage state|auth state|'
    r'session file|browser state|trace\.zip|\.har|har data|screenshot|screen capture)\b',
    re.IGNORECASE,
)
UNSAFE_ACTION_RE = re.compile(
    r'\b(submit|certify|upload|pay|purchase|schedule|cancel|create account|bypass mfa|solve captcha)\b',
    re.IGNORECASE,
)
LIVE_AUTHENTICATED_CLAIM_RE = re.compile(
    r'\b(live authenticated|authenticated devhub session|opened devhub|logged in|signed in|real account|'
    r'live browser|captured authenticated|observed in devhub today)\b',
    re.IGNORECASE,
)
OFFICIAL_COMPLETION_RE = re.compile(
    r'\b(official action completed|submission completed|submitted successfully|payment completed|'
    r'inspection scheduled|upload completed|certification completed|permit issued|approved by pp&d)\b',
    re.IGNORECASE,
)
LEGAL_GUARANTEE_RE = re.compile(
    r'\b(legally sufficient|legal guarantee|guaranteed approval|permit guaranteed|permitting guarantee|'
    r'will be approved|complies with all codes|no reviewer can reject)\b',
    re.IGNORECASE,
)
NEGATED_BOUNDARY_RE = re.compile(r'\b(no|not|do not|must not|never|abort|manual only|refuse|blocked|without)\b', re.IGNORECASE)


class ReadOnlyObservationDeltaV3Error(ValueError):
    '''Raised when a v3 read-only observation delta packet is unsafe.'''


def build_readonly_observation_delta_packet_v3(source_packet: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_source_observation_notes_v3(source_packet)
    if errors:
        raise ReadOnlyObservationDeltaV3Error('source observation notes rejected: ' + ', '.join(errors))

    deltas: list[dict[str, Any]] = []
    selectors: list[dict[str, Any]] = []
    validations: list[dict[str, Any]] = []
    aborts: list[dict[str, Any]] = []
    holds: list[dict[str, Any]] = []
    for surface_index, observation in enumerate(_seq(source_packet.get('observations'))):
        assert isinstance(observation, Mapping)
        sid = _slug(observation.get('surface_id'), f'surface-{surface_index + 1}')
        deltas.append(_surface_delta(sid, observation))
        selectors.extend(_selector_rows(sid, observation))
        validations.extend(_note_rows('validation', sid, observation, 'validation_notes', 'message'))
        aborts.extend(_note_rows('abort', sid, observation, 'abort_notes', 'condition'))
        holds.extend(_note_rows('hold', sid, observation, 'reviewer_notes', 'reason'))

    packet = {
        'schema_version': SCHEMA_VERSION,
        'delta_packet_id': f"readonly-observation-delta-v3-{source_packet['packet_id']}",
        'source_packet': {
            'schema_version': source_packet.get('schema_version'),
            'packet_id': source_packet.get('packet_id'),
            'synthetic_fixture_only': True,
            'authorized_read_only_observation': True,
        },
        'mode': 'offline_fixture_inactive_delta',
        'generated_at': GENERATED_AT,
        'surface_map_candidate_deltas': deltas,
        'selector_confidence_rows': selectors,
        'validation_message_rows': validations,
        'abort_condition_rows': aborts,
        'reviewer_hold_rows': holds,
        'redaction_attestations': [
            'Synthetic notes were redacted before candidate delta assembly.',
            'No screenshots, traces, HAR, auth state, cookies, raw crawl output, uploads, submissions, payments, schedules, cancellations, or browser state are stored.',
            'Rows are inactive reviewer candidates only and do not mutate active DevHub surfaces or release state.',
        ],
        'validation_commands': deepcopy(OFFLINE_VALIDATION_COMMANDS),
    }
    assert_readonly_observation_delta_packet_v3(packet)
    return packet


def validate_source_observation_notes_v3(source_packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(source_packet, Mapping):
        return ['source_packet_not_object']
    if source_packet.get('schema_version') != SOURCE_SCHEMA_VERSION:
        errors.append('unsupported_source_schema_version')
    if not source_packet.get('synthetic_fixture_only'):
        errors.append('source_not_synthetic_fixture_only')
    if not source_packet.get('authorized_read_only_observation'):
        errors.append('missing_read_only_authorization')
    if source_packet.get('mode') != 'offline_fixture_read_only_notes':
        errors.append('missing_offline_read_only_mode')
    if not _text(source_packet.get('packet_id')):
        errors.append('missing_packet_id')
    observations = _seq(source_packet.get('observations'))
    if not observations:
        errors.append('missing_observations')
    for index, observation in enumerate(observations):
        errors.extend(_validate_observation(index, observation))
    errors.extend(_shared_safety_errors(source_packet))
    return sorted(set(errors))


def validate_readonly_observation_delta_packet_v3(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ['packet_not_object']
    if packet.get('schema_version') != SCHEMA_VERSION:
        errors.append('unsupported_schema_version')
    if not _seq(packet.get('surface_map_candidate_deltas')):
        errors.append('missing_redacted_surface_rows')
    if not _seq(packet.get('selector_confidence_rows')):
        errors.append('missing_selector_confidence_rows')
    if not _seq(packet.get('validation_message_rows')):
        errors.append('missing_validation_message_rows')
    if not _seq(packet.get('abort_condition_rows')):
        errors.append('missing_abort_condition_rows')
    if not _seq(packet.get('reviewer_hold_rows')):
        errors.append('missing_reviewer_hold_rows')
    if not _seq(packet.get('redaction_attestations')):
        errors.append('missing_redaction_attestations')
    if not _seq(packet.get('validation_commands')):
        errors.append('missing_validation_commands')
    if packet.get('validation_commands') != OFFLINE_VALIDATION_COMMANDS:
        errors.append('validation_commands_not_exact')
    errors.extend(_validate_surface_rows(packet))
    errors.extend(_validate_candidate_rows('selector_confidence_rows', packet.get('selector_confidence_rows')))
    errors.extend(_validate_candidate_rows('validation_message_rows', packet.get('validation_message_rows')))
    errors.extend(_validate_candidate_rows('abort_condition_rows', packet.get('abort_condition_rows')))
    errors.extend(_validate_candidate_rows('reviewer_hold_rows', packet.get('reviewer_hold_rows')))
    errors.extend(_shared_safety_errors(packet))
    return sorted(set(errors))


def assert_readonly_observation_delta_packet_v3(packet: Mapping[str, Any]) -> None:
    errors = validate_readonly_observation_delta_packet_v3(packet)
    if errors:
        raise ReadOnlyObservationDeltaV3Error('delta packet rejected: ' + ', '.join(errors))


def _validate_observation(index: int, observation: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(observation, Mapping):
        return [f'observation_{index}_not_object']
    for key in ('surface_id', 'url_pattern', 'page_heading'):
        if not _text(observation.get(key)):
            errors.append(f'observation_{index}_missing_{key}')
    for key in ('observed_fields', 'validation_notes', 'abort_notes', 'reviewer_notes'):
        if not _seq(observation.get(key)):
            errors.append(f'observation_{index}_missing_{key}')
    for field_index, field in enumerate(_seq(observation.get('observed_fields'))):
        if not isinstance(field, Mapping):
            errors.append(f'observation_{index}_field_{field_index}_not_object')
            continue
        for key in ('field_id', 'label', 'selector_hint', 'confidence'):
            if key not in field:
                errors.append(f'observation_{index}_field_{field_index}_missing_{key}')
    return errors


def _validate_surface_rows(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(_seq(packet.get('surface_map_candidate_deltas'))):
        if not isinstance(row, Mapping):
            errors.append(f'surface_row_{index}_not_object')
            continue
        if row.get('activation_state') != 'inactive_reviewer_candidate_delta':
            errors.append('surface_delta_not_inactive')
        if row.get('redacted') is not True:
            errors.append('surface_delta_not_marked_redacted')
        if row.get('candidate_only') is not True:
            errors.append('surface_delta_not_candidate_only')
        if row.get('requires_attendance') is not True:
            errors.append('surface_delta_missing_attendance_requirement')
        if row.get('requires_exact_confirmation') is not True:
            errors.append('surface_delta_missing_exact_confirmation_requirement')
        for key in ('field_candidate_ids', 'validation_message_row_ids', 'abort_condition_row_ids', 'reviewer_hold_row_ids'):
            if not _seq(row.get(key)):
                errors.append(f'surface_delta_missing_{key}')
    return errors


def _validate_candidate_rows(name: str, rows: Any) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(_seq(rows)):
        if not isinstance(row, Mapping):
            errors.append(f'{name}_{index}_not_object')
            continue
        if row.get('candidate_only') is not True:
            errors.append(f'{name}_not_candidate_only')
        if not _text(row.get('surface_id')):
            errors.append(f'{name}_missing_surface_id')
    return errors


def _surface_delta(sid: str, observation: Mapping[str, Any]) -> dict[str, Any]:
    fields = _seq(observation.get('observed_fields'))
    return {
        'delta_id': f'delta-v3-{sid}',
        'surface_id': _redact(observation.get('surface_id')),
        'activation_state': 'inactive_reviewer_candidate_delta',
        'auth_scope': 'authenticated_read_only_observation_notes',
        'url_pattern': _redact(observation.get('url_pattern')),
        'page_heading': _redact(observation.get('page_heading')),
        'accessible_landmarks': [_redact(item) for item in _seq(observation.get('landmark_notes'))],
        'field_candidate_ids': [f"selector-v3-{sid}-{_slug(field.get('field_id') if isinstance(field, Mapping) else None, str(i + 1))}" for i, field in enumerate(fields)],
        'validation_message_row_ids': [f'validation-v3-{sid}-{i + 1}' for i, _ in enumerate(_seq(observation.get('validation_notes')))],
        'abort_condition_row_ids': [f'abort-v3-{sid}-{i + 1}' for i, _ in enumerate(_seq(observation.get('abort_notes')))],
        'reviewer_hold_row_ids': [f'hold-v3-{sid}-{i + 1}' for i, _ in enumerate(_seq(observation.get('reviewer_notes')))],
        'requires_attendance': True,
        'requires_exact_confirmation': True,
        'redacted': True,
        'candidate_only': True,
    }


def _selector_rows(sid: str, observation: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, field in enumerate(_seq(observation.get('observed_fields'))):
        if not isinstance(field, Mapping):
            continue
        confidence = field.get('confidence')
        field_slug = _slug(field.get('field_id'), str(index + 1))
        rows.append({
            'row_id': f'selector-v3-{sid}-{field_slug}',
            'surface_id': _redact(observation.get('surface_id')),
            'field_id': _redact(field.get('field_id')),
            'label': _redact(field.get('label')),
            'selector_hint': _redact(field.get('selector_hint')),
            'confidence': confidence if isinstance(confidence, (int, float)) else 0.0,
            'confidence_basis': _redact(field.get('note', 'synthetic authorized read-only observation note')),
            'candidate_only': True,
        })
    return rows


def _note_rows(prefix: str, sid: str, observation: Mapping[str, Any], source_key: str, text_key: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, note in enumerate(_seq(observation.get(source_key))):
        row = {
            'row_id': f'{prefix}-v3-{sid}-{index + 1}',
            'surface_id': _redact(observation.get('surface_id')),
            text_key: _redact(note),
            'candidate_only': True,
        }
        if prefix == 'abort':
            row['action'] = 'abort_and_request_human_review'
        if prefix == 'hold':
            row['disposition'] = 'hold_for_reviewer_before_any_promotion'
        if prefix == 'validation':
            row['redacted'] = True
        rows.append(row)
    return rows


def _shared_safety_errors(value: Any) -> list[str]:
    errors: list[str] = []
    if _contains_prohibited_key(value):
        errors.append('prohibited_private_or_browser_artifact_key')
    if _contains_private_text(value):
        errors.append('prohibited_private_or_browser_artifact_text')
    if _contains_unapproved_action_claim(value):
        errors.append('unapproved_consequential_action_claim')
    if _contains_live_authenticated_claim(value):
        errors.append('live_authenticated_devhub_claim')
    if _contains_official_completion_claim(value):
        errors.append('official_action_completion_claim')
    if _contains_legal_or_permitting_guarantee(value):
        errors.append('legal_or_permitting_guarantee')
    if _contains_active_mutation_flag(value):
        errors.append('active_mutation_flag')
    return errors


def _redact(value: Any) -> str:
    text = '' if value is None else str(value)
    text = EMAIL_RE.sub('[redacted-email]', text)
    text = PHONE_RE.sub('[redacted-phone]', text)
    return PERMIT_RE.sub('[redacted-permit-id]', text)


def _contains_prohibited_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower().replace('-', '_') in PROHIBITED_KEYS:
                return True
            if _contains_prohibited_key(child):
                return True
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_prohibited_key(item) for item in value)
    return False


def _contains_private_text(value: Any) -> bool:
    return _contains_matching_text(value, PRIVATE_TEXT_RE, require_unnegated=True)


def _contains_unapproved_action_claim(value: Any) -> bool:
    return _contains_matching_text(value, UNSAFE_ACTION_RE, require_unnegated=True)


def _contains_live_authenticated_claim(value: Any) -> bool:
    return _contains_matching_text(value, LIVE_AUTHENTICATED_CLAIM_RE, require_unnegated=True)


def _contains_official_completion_claim(value: Any) -> bool:
    return _contains_matching_text(value, OFFICIAL_COMPLETION_RE, require_unnegated=True)


def _contains_legal_or_permitting_guarantee(value: Any) -> bool:
    return _contains_matching_text(value, LEGAL_GUARANTEE_RE, require_unnegated=True)


def _contains_matching_text(value: Any, pattern: re.Pattern[str], *, require_unnegated: bool) -> bool:
    if isinstance(value, Mapping):
        return any(_contains_matching_text(child, pattern, require_unnegated=require_unnegated) for child in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_matching_text(item, pattern, require_unnegated=require_unnegated) for item in value)
    if isinstance(value, str):
        return bool(pattern.search(value) and (not require_unnegated or not NEGATED_BOUNDARY_RE.search(value)))
    return False


def _contains_active_mutation_flag(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower().replace('-', '_') in ACTIVE_MUTATION_KEYS and child:
                return True
            if _contains_active_mutation_flag(child):
                return True
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_active_mutation_flag(item) for item in value)
    return False


def _seq(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _slug(value: Any, fallback: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', str(value or fallback).lower()).strip('-')
    return slug or fallback
