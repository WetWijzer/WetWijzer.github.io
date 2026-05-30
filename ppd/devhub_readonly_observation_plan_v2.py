'''Fixture-first attended DevHub read-only observation plan v2.

This module consumes the attended DevHub read-only observation readiness packet v2
and produces an offline-only synthetic observation plan. It never opens DevHub,
creates authentication state, captures screenshots, records traces or HAR files,
changes account data, uploads, submits, pays, schedules, or cancels anything.
'''

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any

from ppd.devhub_attended_readonly_observation_readiness_packet_v2 import (
    require_attended_devhub_readonly_observation_readiness_packet_v2,
)

PLAN_VERSION = 'fixture-first-attended-devhub-readonly-observation-plan-v2'
PLAN_ID = 'fixture-first-attended-devhub-readonly-observation-plan-v2'

ALLOWED_OBSERVATION_FIELDS: list[str] = [
    'page_heading',
    'url_path_pattern',
    'accessible_landmark_roles',
    'visible_link_names',
    'visible_button_names',
    'status_text_labels',
    'validation_message_labels',
    'attachment_list_labels',
    'fee_notice_labels',
    'inspection_result_labels',
    'correction_request_labels',
    'no_private_values_recorded',
]

EXACT_OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ['python3', '-m', 'py_compile', 'ppd/devhub_readonly_observation_plan_v2.py'],
    ['python3', '-m', 'pytest', 'ppd/tests/test_devhub_readonly_observation_plan_v2.py'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

_REQUIRED_PLAN_LISTS = (
    'ordered_synthetic_read_only_surface_rows',
    'manual_login_handoff_reminders',
    'allowed_observation_fields',
    'redaction_review_placeholders',
    'timeout_and_manual_handoff_notes',
    'exact_offline_validation_commands',
)

_REQUIRED_ARTIFACT_ATTESTATIONS = {
    'no_devhub_opened',
    'no_auth_state_created',
    'no_auth_state_read',
    'no_screenshots',
    'no_traces',
    'no_har_files',
    'no_downloads',
    'no_raw_authenticated_capture',
    'no_account_data_changes',
    'no_uploads',
    'no_submissions',
    'no_payments',
    'no_scheduling',
    'no_cancellations',
}

_FORBIDDEN_KEY_RE = re.compile(
    r'(^|_)(auth[_-]?state|cookie|credential|password|token|session[_-]?(path|state|storage|artifact)|screenshot[_-]?(path|file)?|trace[_-]?(path|file)?|har[_-]?(path|file)?|raw[_-]?(html|capture|body|crawl)|downloaded?[_-]?(document|path|file)|private[_-]?(value|path|artifact))(_|$)',
    re.IGNORECASE,
)
_FORBIDDEN_VALUE_RE = re.compile(
    r'(storage[-_]?state\.json|cookies?\.json|trace\.zip|\.har\b|\.png\b|\.jpe?g\b|\.webp\b|file://|/(tmp|home|private|var/folders)/|\\users\\|private session|auth state|browser trace)',
    re.IGNORECASE,
)
_LIVE_ACCESS_RE = re.compile(
    r'\b(opened devhub|live devhub|logged in|authenticated session|manual login completed|observed live|captured live|browser session created)\b',
    re.IGNORECASE,
)
_AUTOMATION_RE = re.compile(
    r'\b(automated|scripted|programmatic|headless|bypass|solve)\b.{0,48}\b(login|sign[- ]?in|mfa|captcha|password|otp|one[- ]?time code|credential)\b|\b(login|sign[- ]?in|mfa|captcha|password|otp|one[- ]?time code|credential)\b.{0,48}\b(automated|scripted|programmatic|headless|bypass|solve)\b',
    re.IGNORECASE,
)
_OFFICIAL_ACTION_RE = re.compile(
    r'\b(submission completed|submitted|paid|payment completed|scheduled|cancelled|canceled|uploaded|certified|purchased|changed account|account changed)\b',
    re.IGNORECASE,
)
_MUTATION_KEY_RE = re.compile(
    r'(^|_)(active|apply|mutate|promote|update|write).*(devhub|surface|source|guardrail|prompt|contract|release|account)(_|$)|(^|_)(devhub|surface|source|guardrail|prompt|contract|release|account).*(active|apply|mutate|promote|update|write)(_|$)',
    re.IGNORECASE,
)
_ACTIVE_VALUES = {'active', 'applied', 'changed', 'enabled', 'true', 'updated', 'yes'}


@dataclass(frozen=True)
class DevhubReadonlyObservationPlanV2ValidationResult:
    valid: bool
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.valid

    def as_dict(self) -> dict[str, Any]:
        return {'valid': self.valid, 'errors': list(self.errors)}


def build_devhub_readonly_observation_plan_v2(readiness_packet: Mapping[str, Any]) -> dict[str, Any]:
    '''Build a deterministic synthetic read-only observation plan from readiness v2.'''

    require_attended_devhub_readonly_observation_readiness_packet_v2(readiness_packet)
    surface_placeholders = _required_list(readiness_packet, 'read_only_surface_observation_placeholders')
    handoffs = _required_list(readiness_packet, 'manual_login_handoff_placeholders')
    redactions = _required_list(readiness_packet, 'redaction_checklist_placeholders')

    plan = {
        'plan_version': PLAN_VERSION,
        'plan_id': PLAN_ID,
        'source_packet_version': readiness_packet.get('packet_version'),
        'source_packet_id': readiness_packet.get('packet_id'),
        'mode': 'fixture_first_synthetic_read_only_observation_plan',
        'devhub_access': 'not_opened',
        'browser_artifacts': 'not_created',
        'official_action_scope': 'blocked',
        'ordered_synthetic_read_only_surface_rows': [
            {
                'order': index,
                'surface_row_id': f'synthetic-readonly-surface-{index}',
                'source_surface_group_id': _required_str(surface, 'surface_group_id'),
                'canonical_hosts': deepcopy(_required_list(surface, 'canonical_hosts')),
                'observation_scope': 'synthetic_read_only_surface_structure_only',
                'allowed_observation_fields': deepcopy(ALLOWED_OBSERVATION_FIELDS),
                'manual_login_required_before_live_use': True,
                'synthetic_status': 'planned_not_observed',
                'read_only_only': True,
                'forbidden_capture_fields': [
                    'credentials',
                    'cookies',
                    'tokens',
                    'auth_state',
                    'private_account_values',
                    'screenshots',
                    'traces',
                    'har_files',
                    'raw_authenticated_html',
                ],
            }
            for index, surface in enumerate(surface_placeholders, start=1)
        ],
        'manual_login_handoff_reminders': [
            {
                'order': index,
                'handoff_id': _required_str(handoff, 'handoff_id'),
                'source_status': _required_str(handoff, 'status'),
                'reminder': 'User attendance is required; credentials, MFA, CAPTCHA, and security prompts remain manual.',
                'automation_allowed': False,
                'credential_storage_allowed': False,
            }
            for index, handoff in enumerate(handoffs, start=1)
        ],
        'allowed_observation_fields': deepcopy(ALLOWED_OBSERVATION_FIELDS),
        'forbidden_browser_artifact_attestations': {
            key: True for key in sorted(_REQUIRED_ARTIFACT_ATTESTATIONS)
        },
        'redaction_review_placeholders': [
            {
                'order': index,
                'redaction_id': _required_str(redaction, 'redaction_id'),
                'source_status': _required_str(redaction, 'status'),
                'reviewer_confirmation': None,
                'expected_disposition': 'confirm_absent_or_redacted_before_acceptance',
            }
            for index, redaction in enumerate(redactions, start=1)
        ],
        'timeout_and_manual_handoff_notes': [
            {
                'order': 1,
                'timeout_id': 'attended-login-timeout',
                'trigger': 'User attendance, sign-in, MFA, CAPTCHA, or security prompt is unavailable.',
                'handoff_required': True,
                'operator_response': 'Stop observation planning and return control to the user.',
            },
            {
                'order': 2,
                'timeout_id': 'consequential-control-encountered',
                'trigger': 'A control would alter official records, money movement, appointments, account settings, or filed materials.',
                'handoff_required': True,
                'operator_response': 'Stop before the control and request a separate confirmed action plan.',
            },
            {
                'order': 3,
                'timeout_id': 'redaction-review-incomplete',
                'trigger': 'A reviewer cannot attest that private values and browser artifacts are absent.',
                'handoff_required': True,
                'operator_response': 'Reject the observation packet until redaction review is complete.',
            },
        ],
        'exact_offline_validation_commands': deepcopy(EXACT_OFFLINE_VALIDATION_COMMANDS),
    }
    require_devhub_readonly_observation_plan_v2(plan)
    return plan


def validate_devhub_readonly_observation_plan_v2(packet: Mapping[str, Any]) -> DevhubReadonlyObservationPlanV2ValidationResult:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return DevhubReadonlyObservationPlanV2ValidationResult(False, ('packet must be an object',))

    if packet.get('plan_version') != PLAN_VERSION:
        errors.append(f'plan_version must be {PLAN_VERSION}')
    if packet.get('mode') != 'fixture_first_synthetic_read_only_observation_plan':
        errors.append('mode must be fixture_first_synthetic_read_only_observation_plan')
    if packet.get('devhub_access') != 'not_opened':
        errors.append('devhub_access must be not_opened')
    if packet.get('browser_artifacts') != 'not_created':
        errors.append('browser_artifacts must be not_created')
    if packet.get('official_action_scope') != 'blocked':
        errors.append('official_action_scope must be blocked')

    for field in _REQUIRED_PLAN_LISTS:
        if not _non_empty_list(packet.get(field)):
            errors.append(f'{field} must be a non-empty list')

    _validate_surface_rows(errors, packet.get('ordered_synthetic_read_only_surface_rows'))
    _validate_manual_handoffs(errors, packet.get('manual_login_handoff_reminders'))
    _validate_allowed_fields(errors, packet.get('allowed_observation_fields'))
    _validate_attestations(errors, packet.get('forbidden_browser_artifact_attestations'))
    _validate_redactions(errors, packet.get('redaction_review_placeholders'))
    _validate_timeout_notes(errors, packet.get('timeout_and_manual_handoff_notes'))
    _validate_commands(errors, packet.get('exact_offline_validation_commands'))
    _validate_recursive_safety(errors, packet)
    return DevhubReadonlyObservationPlanV2ValidationResult(not errors, tuple(errors))


def require_devhub_readonly_observation_plan_v2(packet: Mapping[str, Any]) -> None:
    result = validate_devhub_readonly_observation_plan_v2(packet)
    if not result.valid:
        raise ValueError('invalid DevHub read-only observation plan v2: ' + '; '.join(result.errors))


def _validate_surface_rows(errors: list[str], value: Any) -> None:
    rows = _mapping_sequence(value)
    expected = list(range(1, len(rows) + 1))
    actual = [row.get('order') for row in rows]
    if actual != expected:
        errors.append('ordered_synthetic_read_only_surface_rows must use contiguous order values')
    for index, row in enumerate(rows):
        prefix = f'ordered_synthetic_read_only_surface_rows[{index}]'
        for field in ('surface_row_id', 'source_surface_group_id', 'observation_scope', 'synthetic_status'):
            if not _text(row.get(field)):
                errors.append(f'{prefix}.{field} must be present')
        if row.get('observation_scope') != 'synthetic_read_only_surface_structure_only':
            errors.append(f'{prefix}.observation_scope must be synthetic_read_only_surface_structure_only')
        if row.get('synthetic_status') != 'planned_not_observed':
            errors.append(f'{prefix}.synthetic_status must remain planned_not_observed')
        if row.get('manual_login_required_before_live_use') is not True:
            errors.append(f'{prefix}.manual_login_required_before_live_use must be true')
        if row.get('read_only_only') is not True:
            errors.append(f'{prefix}.read_only_only must be true')
        if _string_list(row.get('allowed_observation_fields')) != set(ALLOWED_OBSERVATION_FIELDS):
            errors.append(f'{prefix}.allowed_observation_fields must match allowed read-only fields')
        if not _string_list(row.get('canonical_hosts')):
            errors.append(f'{prefix}.canonical_hosts must be non-empty')


def _validate_manual_handoffs(errors: list[str], value: Any) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f'manual_login_handoff_reminders[{index}]'
        if not _text(row.get('handoff_id')):
            errors.append(f'{prefix}.handoff_id must be present')
        if row.get('automation_allowed') is not False:
            errors.append(f'{prefix}.automation_allowed must be false')
        if row.get('credential_storage_allowed') is not False:
            errors.append(f'{prefix}.credential_storage_allowed must be false')
        if not _text(row.get('reminder')):
            errors.append(f'{prefix}.reminder must be present')


def _validate_allowed_fields(errors: list[str], value: Any) -> None:
    if _command_like(value):
        errors.append('allowed_observation_fields must be field names, not commands')
    if _string_list(value) != set(ALLOWED_OBSERVATION_FIELDS):
        errors.append('allowed_observation_fields must match the allowed read-only observation field list')


def _validate_attestations(errors: list[str], value: Any) -> None:
    if not isinstance(value, Mapping):
        errors.append('forbidden_browser_artifact_attestations must be an object')
        return
    missing = sorted(key for key in _REQUIRED_ARTIFACT_ATTESTATIONS if value.get(key) is not True)
    if missing:
        errors.append('missing true forbidden browser artifact attestations: ' + ', '.join(missing))


def _validate_redactions(errors: list[str], value: Any) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f'redaction_review_placeholders[{index}]'
        if not _text(row.get('redaction_id')):
            errors.append(f'{prefix}.redaction_id must be present')
        if row.get('reviewer_confirmation') is not None:
            errors.append(f'{prefix}.reviewer_confirmation must remain empty')
        if row.get('expected_disposition') != 'confirm_absent_or_redacted_before_acceptance':
            errors.append(f'{prefix}.expected_disposition must remain confirm_absent_or_redacted_before_acceptance')


def _validate_timeout_notes(errors: list[str], value: Any) -> None:
    for index, row in enumerate(_mapping_sequence(value)):
        prefix = f'timeout_and_manual_handoff_notes[{index}]'
        if not _text(row.get('timeout_id')):
            errors.append(f'{prefix}.timeout_id must be present')
        if row.get('handoff_required') is not True:
            errors.append(f'{prefix}.handoff_required must be true')
        if not _text(row.get('trigger')) or not _text(row.get('operator_response')):
            errors.append(f'{prefix}.trigger and operator_response must be present')


def _validate_commands(errors: list[str], value: Any) -> None:
    commands = _command_sequence(value)
    if commands and commands != EXACT_OFFLINE_VALIDATION_COMMANDS:
        errors.append('exact_offline_validation_commands must match the allowed offline validation commands')


def _validate_recursive_safety(errors: list[str], packet: Mapping[str, Any]) -> None:
    for path, value in _walk(packet):
        key = path.rsplit('.', 1)[-1].split('[', 1)[0]
        normalized_key = key.lower().replace('-', '_')
        if _allowed_attestation_path(path) or _allowed_forbidden_capture_path(path):
            continue
        if _FORBIDDEN_KEY_RE.search(normalized_key) and _truthy_or_text(value):
            errors.append(f'{path} must not include private DevHub session, browser artifact, raw capture, credential, or downloaded material')
        if _MUTATION_KEY_RE.search(normalized_key) and _active_value(value):
            errors.append(f'{path} must not set active DevHub, surface, guardrail, source, prompt, contract, release, or account mutation flags')
        if isinstance(value, str):
            stripped = value.strip()
            if _FORBIDDEN_VALUE_RE.search(stripped):
                errors.append(f'{path} must not reference private DevHub session, browser artifact, raw capture, credential, or downloaded material')
            if _LIVE_ACCESS_RE.search(stripped):
                errors.append(f'{path} must not claim live DevHub access or authenticated observation')
            if _AUTOMATION_RE.search(stripped):
                errors.append(f'{path} must not claim automated login, MFA, CAPTCHA, password, credential, or OTP handling')
            if _OFFICIAL_ACTION_RE.search(stripped):
                errors.append(f'{path} must not claim completed consequential DevHub actions')


def _required_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{key} must be a non-empty string')
    return value


def _required_list(data: Mapping[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f'{key} must be a non-empty list')
    return value


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _command_sequence(value: Any) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    commands: list[list[str]] = []
    for command in value:
        if not isinstance(command, list) or not command:
            return []
        parts: list[str] = []
        for part in command:
            if not isinstance(part, str) or not part:
                return []
            parts.append(part)
        commands.append(parts)
    return commands


def _string_list(value: Any) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return set()
    return {item.strip() for item in value if isinstance(item, str) and item.strip()}


def _command_like(value: Any) -> bool:
    return any(item.startswith('python') or item in {'pytest', 'bash', 'node'} for item in _string_list(value))


def _walk(value: Any, path: str = 'packet') -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            rows.extend(_walk(child, f'{path}.{key}'))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_walk(child, f'{path}[{index}]'))
    return rows


def _allowed_attestation_path(path: str) -> bool:
    return path.startswith('packet.forbidden_browser_artifact_attestations.')


def _allowed_forbidden_capture_path(path: str) -> bool:
    return '.forbidden_capture_fields[' in path


def _active_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in _ACTIVE_VALUES
    return False


def _truthy_or_text(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None


def _text(value: Any) -> str:
    if value is None:
        return ''
    return str(value).strip()
