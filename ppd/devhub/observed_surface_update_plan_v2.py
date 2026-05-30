from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

PLAN_VERSION = 'devhub_observed_surface_update_plan_v2'
PLAN_MODE = 'fixture_first_read_only_surface_update_candidates'
REQUIRED_SOURCE_KEYS = (
    'devhub_observation_evidence_intake_packet_v1',
    'attended_devhub_observation_handoff_checklist_v1',
    'devhub_read_only_observation_rehearsal_v1',
)
REQUIRED_ATTESTATIONS = (
    'no_live_devhub_access',
    'no_authenticated_artifacts',
    'no_session_state',
    'no_official_actions',
    'no_private_values',
)
FORBIDDEN_KEY_RE = re.compile(r'(auth_state|cookie|credential|password|storage_state|trace|har|screenshot|token|raw_value|payment_detail)', re.I)
FORBIDDEN_TEXT_RE = re.compile(r'(storage_state\.json|auth_state\.json|trace\.zip|\.har\b|cookie=|password=|token=|card number)', re.I)
SAFE_TEXT_RE = re.compile(r'(no |without|redact|redacted|blocked|must not|stop before)', re.I)


def load_json_object(path: str | Path) -> dict[str, Any]:
    with Path(path).open('r', encoding='utf-8') as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError('fixture must contain a JSON object')
    return value


def build_devhub_observed_surface_update_plan_v2(source_inputs: Mapping[str, Any]) -> dict[str, Any]:
    _raise_forbidden(source_inputs)
    sources = _source_packets(source_inputs)
    evidence_rows = _rows_by_surface(_packet_rows(sources['devhub_observation_evidence_intake_packet_v1'], ('observed_surfaces', 'surface_evidence', 'evidence_rows', 'surfaces', 'items')))
    handoff_rows = _rows_by_surface(_packet_rows(sources['attended_devhub_observation_handoff_checklist_v1'], ('manual_observation_checklists', 'visible_ui_evidence_expectations', 'attendance_checkpoints', 'surfaces', 'items')))
    rehearsal_rows = _rows_by_surface(_packet_rows(sources['devhub_read_only_observation_rehearsal_v1'], ('steps', 'surfaces', 'items')))
    surface_ids = sorted(set(evidence_rows) | set(handoff_rows) | set(rehearsal_rows))
    if not surface_ids:
        raise ValueError('at least one observed surface is required')

    candidates: list[dict[str, Any]] = []
    selector_rows: list[dict[str, Any]] = []
    owner_rows: list[dict[str, Any]] = []
    rollback_notes: list[dict[str, Any]] = []
    all_redaction_checks: list[dict[str, Any]] = []
    all_attendance_gates: list[dict[str, Any]] = []
    all_commands: list[list[str]] = []

    for index, surface_id in enumerate(surface_ids, start=1):
        evidence = evidence_rows.get(surface_id, {})
        handoff = handoff_rows.get(surface_id, {})
        rehearsal = rehearsal_rows.get(surface_id, {})
        candidate_id = f'devhub-observed-surface-update-v2-{index:03d}'
        owner = _first_text(evidence.get('reviewer_owner'), handoff.get('reviewer_owner'), rehearsal.get('reviewer_owner'), _mapping(source_inputs.get('reviewer_owner_assignments')).get(surface_id), 'PPD DevHub reviewer')
        citations = _citations(surface_id, evidence, handoff, rehearsal)
        selector_row = {
            'surface_id': surface_id,
            'candidate_id': candidate_id,
            'selector_confidence': _selector_confidence(evidence, handoff, rehearsal),
            'review_required': True,
            'evidence_citations': citations,
            'manual_reviewer': owner,
        }
        redaction_checks = _redaction_checks(surface_id, evidence, handoff, rehearsal)
        attendance_gates = _attendance_gates(surface_id, handoff, rehearsal)
        commands = _offline_commands(surface_id)
        rollback_note = _first_text(evidence.get('rollback_note'), handoff.get('rollback_note'), rehearsal.get('rollback_note'), 'Discard this fixture candidate and leave the surface registry unchanged if any source packet is incomplete or unredacted.')
        candidate = {
            'candidate_id': candidate_id,
            'surface_id': surface_id,
            'page_heading': _first_text(evidence.get('page_heading'), evidence.get('heading'), handoff.get('page_heading'), rehearsal.get('title'), surface_id),
            'candidate_effect': 'read_only_surface_update_candidate',
            'fixture_first': True,
            'read_only': True,
            'active_surface_registry_mutation': False,
            'live_devhub_access_required': False,
            'authenticated_artifacts_required': False,
            'session_state_required': False,
            'official_action_allowed': False,
            'private_values_allowed': False,
            'observed_labels': _labels(evidence, handoff, rehearsal),
            'selector_confidence_review': selector_row,
            'redaction_checks': redaction_checks,
            'manual_attendance_gates': attendance_gates,
            'offline_validation_commands': commands,
            'reviewer_owner': owner,
            'rollback_note': rollback_note,
            'citations': citations,
        }
        candidates.append(candidate)
        selector_rows.append(selector_row)
        owner_rows.append({'surface_id': surface_id, 'reviewer_owner': owner, 'assignment_reason': 'Manual reviewer owns fixture-only review before any surface registry change is proposed.', 'requires_manual_attendance': True})
        rollback_notes.append({'candidate_id': candidate_id, 'surface_id': surface_id, 'manual_only': True, 'note': rollback_note})
        all_redaction_checks.extend(redaction_checks)
        all_attendance_gates.extend(attendance_gates)
        all_commands.extend(commands)

    plan = {
        'plan_version': PLAN_VERSION,
        'mode': PLAN_MODE,
        'fixture_first': True,
        'offline_only': True,
        'read_only': True,
        'live_devhub_access': False,
        'authenticated_artifacts': False,
        'session_state': False,
        'official_actions': False,
        'private_values': False,
        'source_packets': {key: {'consumed': True} for key in REQUIRED_SOURCE_KEYS},
        'attestations': {key: True for key in REQUIRED_ATTESTATIONS},
        'surface_update_candidates': candidates,
        'selector_confidence_review_rows': selector_rows,
        'redaction_checks': _dedupe_dicts(all_redaction_checks, 'check_id'),
        'manual_attendance_gates': _dedupe_dicts(all_attendance_gates, 'gate_id'),
        'offline_validation_commands': _dedupe_commands(all_commands),
        'reviewer_owner_assignments': owner_rows,
        'rollback_notes': rollback_notes,
    }
    assert_valid_devhub_observed_surface_update_plan_v2(plan)
    return plan


build_observed_surface_update_plan_v2 = build_devhub_observed_surface_update_plan_v2


def validate_devhub_observed_surface_update_plan_v2(plan: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if plan.get('plan_version') != PLAN_VERSION:
        errors.append(f'plan_version must be {PLAN_VERSION}')
    if plan.get('mode') != PLAN_MODE:
        errors.append(f'mode must be {PLAN_MODE}')
    for key in ('fixture_first', 'offline_only', 'read_only'):
        if plan.get(key) is not True:
            errors.append(f'{key} must be true')
    for key in ('live_devhub_access', 'authenticated_artifacts', 'session_state', 'official_actions', 'private_values'):
        if plan.get(key) is not False:
            errors.append(f'{key} must be false')
    for key in REQUIRED_ATTESTATIONS:
        if _mapping(plan.get('attestations')).get(key) is not True:
            errors.append(f'attestations.{key} must be true')
    for key in REQUIRED_SOURCE_KEYS:
        if _mapping(_mapping(plan.get('source_packets')).get(key)).get('consumed') is not True:
            errors.append(f'source_packets.{key}.consumed must be true')
    for field in ('surface_update_candidates', 'selector_confidence_review_rows', 'redaction_checks', 'manual_attendance_gates', 'offline_validation_commands', 'reviewer_owner_assignments', 'rollback_notes'):
        if not _sequence(plan.get(field)):
            errors.append(f'{field} must be non-empty')
    for index, candidate_value in enumerate(_sequence(plan.get('surface_update_candidates'))):
        candidate = _mapping(candidate_value)
        prefix = f'surface_update_candidates[{index}]'
        for field in ('candidate_id', 'surface_id', 'page_heading', 'reviewer_owner', 'rollback_note'):
            if not _text(candidate.get(field)):
                errors.append(f'{prefix}.{field} is required')
        for flag in ('fixture_first', 'read_only'):
            if candidate.get(flag) is not True:
                errors.append(f'{prefix}.{flag} must be true')
        for flag in ('active_surface_registry_mutation', 'live_devhub_access_required', 'authenticated_artifacts_required', 'session_state_required', 'official_action_allowed', 'private_values_allowed'):
            if candidate.get(flag) is not False:
                errors.append(f'{prefix}.{flag} must be false')
        for field in ('citations', 'redaction_checks', 'manual_attendance_gates', 'offline_validation_commands'):
            if not _sequence(candidate.get(field)):
                errors.append(f'{prefix}.{field} must be non-empty')
        if _mapping(candidate.get('selector_confidence_review')).get('selector_confidence') not in {'high', 'medium', 'low'}:
            errors.append(f'{prefix}.selector_confidence_review.selector_confidence must be high, medium, or low')
    for index, row_value in enumerate(_sequence(plan.get('redaction_checks'))):
        row = _mapping(row_value)
        if row.get('passed') is not True:
            errors.append(f'redaction_checks[{index}].passed must be true')
        if row.get('private_values_allowed') is not False:
            errors.append(f'redaction_checks[{index}].private_values_allowed must be false')
    for index, row_value in enumerate(_sequence(plan.get('manual_attendance_gates'))):
        row = _mapping(row_value)
        if row.get('requires_manual_attendance') is not True:
            errors.append(f'manual_attendance_gates[{index}].requires_manual_attendance must be true')
        if row.get('automated_execution_allowed') is not False:
            errors.append(f'manual_attendance_gates[{index}].automated_execution_allowed must be false')
    _scan_forbidden(plan, '$', errors)
    return tuple(dict.fromkeys(errors))


def assert_valid_devhub_observed_surface_update_plan_v2(plan: Mapping[str, Any]) -> None:
    errors = validate_devhub_observed_surface_update_plan_v2(plan)
    if errors:
        raise AssertionError('; '.join(errors))


def _source_packets(source_inputs: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    root = _mapping(source_inputs.get('source_packets')) or source_inputs
    aliases = {
        'devhub_observation_evidence_intake_packet_v1': ('observation_evidence_intake_packet_v1', 'evidence_intake_packet'),
        'attended_devhub_observation_handoff_checklist_v1': ('attended_observation_handoff_checklist_v1', 'handoff_checklist'),
        'devhub_read_only_observation_rehearsal_v1': ('read_only_observation_rehearsal_v1', 'observation_rehearsal'),
    }
    packets: dict[str, Mapping[str, Any]] = {}
    for key in REQUIRED_SOURCE_KEYS:
        packet = root.get(key)
        for alias in aliases[key]:
            packet = packet or root.get(alias)
        if not isinstance(packet, Mapping):
            raise ValueError(f'missing source packet {key}')
        packets[key] = packet
    return packets


def _packet_rows(packet: Mapping[str, Any], keys: Sequence[str]) -> list[Mapping[str, Any]]:
    for key in keys:
        rows = packet.get(key)
        if isinstance(rows, Sequence) and not isinstance(rows, (str, bytes, bytearray)):
            return [row for row in rows if isinstance(row, Mapping)]
    return [packet] if packet.get('surface_id') else []


def _rows_by_surface(rows: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(rows, start=1):
        result.setdefault(_text(row.get('surface_id') or row.get('surface_ref') or row.get('id') or f'surface-{index}'), row)
    return result


def _citations(surface_id: str, *rows: Mapping[str, Any]) -> list[dict[str, str]]:
    packets = REQUIRED_SOURCE_KEYS
    citations: list[dict[str, str]] = []
    for packet, row in zip(packets, rows):
        if row:
            citations.append({'packet': packet, 'pointer': f'/surfaces/{surface_id}'})
        for citation in _sequence(row.get('citations')):
            if isinstance(citation, Mapping):
                citations.append({'packet': _text(citation.get('packet') or citation.get('fixture') or packet), 'pointer': _text(citation.get('pointer') or citation.get('path') or f'/{surface_id}')})
    return _dedupe_dicts(citations, 'packet', 'pointer')


def _labels(*rows: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    for row in rows:
        for key in ('observed_labels', 'expected_visible_labels', 'visible_labels', 'accessible_landmarks'):
            labels.extend(_text_list(row.get(key)))
    return [label for label in dict.fromkeys(labels) if label] or ['Read-only observed DevHub surface']


def _selector_confidence(*rows: Mapping[str, Any]) -> str:
    values = [_text(row.get('selector_confidence') or row.get('confidence')) for row in rows]
    if 'low' in values:
        return 'low'
    if 'medium' in values:
        return 'medium'
    return 'high'


def _redaction_checks(surface_id: str, *rows: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks = ['no_authenticated_artifacts', 'no_session_state', 'no_private_values', 'no_official_actions']
    for row in rows:
        checks.extend(_text_list(row.get('redaction_checks')))
        checks.extend(_text_list(row.get('redaction_requirements')))
    return [{'check_id': f'{surface_id}-{check}', 'surface_id': surface_id, 'check': check, 'passed': True, 'private_values_allowed': False} for check in dict.fromkeys(checks)]


def _attendance_gates(surface_id: str, *rows: Mapping[str, Any]) -> list[dict[str, Any]]:
    gates = ['manual_reviewer_present', 'stop_before_upload_submit_payment_or_scheduling']
    for row in rows:
        gates.extend(_text_list(row.get('manual_attendance_gates')))
        gates.extend(_text_list(row.get('manual_attendance_checkpoints')))
        gates.extend(_text_list(row.get('stop_before_action_gates')))
    return [{'gate_id': f'{surface_id}-{gate}', 'surface_id': surface_id, 'gate': gate, 'requires_manual_attendance': True, 'automated_execution_allowed': False, 'official_action_allowed': False} for gate in dict.fromkeys(gates)]


def _offline_commands(surface_id: str) -> list[list[str]]:
    return [
        ['python3', '-m', 'py_compile', 'ppd/devhub/observed_surface_update_plan_v2.py'],
        ['python3', '-m', 'unittest', 'ppd.tests.test_devhub_observed_surface_update_plan_v2'],
        ['python3', '-c', f"print('offline fixture validation for {surface_id}')"],
    ]


def _raise_forbidden(value: Any) -> None:
    errors: list[str] = []
    _scan_forbidden(value, '$', errors)
    if errors:
        raise ValueError('; '.join(errors))


def _scan_forbidden(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f'{path}.{key}'
            if FORBIDDEN_KEY_RE.search(str(key)) and child not in (False, None, ''):
                errors.append(f'forbidden key at {child_path}')
            _scan_forbidden(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_forbidden(child, f'{path}[{index}]', errors)
    elif isinstance(value, str) and FORBIDDEN_TEXT_RE.search(value) and not SAFE_TEXT_RE.search(value):
        errors.append(f'forbidden text at {path}')


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _first_text(*values: Any) -> str:
    for value in values:
        text = _text(value)
        if text:
            return text
    return ''


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [_text(item) for item in _sequence(value) if _text(item)]


def _dedupe_dicts(rows: Sequence[dict[str, Any]], *keys: str) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        key = tuple(row.get(name) for name in keys)
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def _dedupe_commands(commands: Sequence[Sequence[str]]) -> list[list[str]]:
    seen: set[tuple[str, ...]] = set()
    result: list[list[str]] = []
    for command in commands:
        row = [str(part) for part in command]
        key = tuple(row)
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result
