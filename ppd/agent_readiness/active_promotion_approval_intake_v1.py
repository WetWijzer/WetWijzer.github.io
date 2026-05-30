from __future__ import annotations

from typing import Any, Mapping

SOURCE_PACKET_TYPE = 'ppd.active_promotion_preflight_gate.v1'
PACKET_TYPE = 'ppd.active_promotion_approval_intake.v1'

_EXPECTED_NONMUTATION_FLAGS = (
    'fixture_promotion_applied',
    'fixture_mutated',
    'active_artifacts_mutated',
    'active_artifact_mutation_requested',
    'prompts_changed',
    'prompt_mutation_requested',
    'release_state_updated',
    'release_state_mutation_requested',
    'agent_state_updated',
    'agent_state_mutation_requested',
    'live_sources_crawled',
    'devhub_accessed',
    'official_actions_performed',
)

_REQUIRED_INTAKE_ROW_FIELDS = {
    'reviewer_decision_rows': (
        'row_id',
        'source_decision',
        'reviewer_decision_placeholder',
        'evidence_placeholder',
        'carry_forward_reason',
    ),
    'approval_evidence_placeholders': (
        'approval_id',
        'required_actor',
        'approval_status',
        'evidence_reference_placeholder',
    ),
    'unresolved_blocker_carry_forward': (
        'blocker_id',
        'blocked_surface',
        'carry_forward_status',
        'clearance_evidence_placeholder',
    ),
    'rollback_readiness_acknowledgements': (
        'acknowledgement_id',
        'source_status',
        'reviewer_acknowledgement_placeholder',
        'summary',
    ),
    'validation_replay_acknowledgements': (
        'check_id',
        'source_status',
        'reviewer_acknowledgement_placeholder',
    ),
    'no_go_reason_placeholders': (
        'reason_id',
        'source_row_id',
        'reason_placeholder',
        'evidence_placeholder',
    ),
}

_REQUIRED_SOURCE_SECTIONS = (
    'final_go_no_go_rows',
    'human_approval_placeholders',
    'active_mutation_blocker_inventory',
    'validation_replay_checklist',
    'rollback_readiness_summary',
)

_FORBIDDEN_TEXT = (
    'live execution',
    'live crawl executed',
    'live source crawled',
    'promoted to active',
    'promotion executed',
    'promotion complete',
    'release complete',
    'release is complete',
    'devhub session',
    'authenticated session',
    'private session',
    'session cookie',
    'browser state',
    'storage state',
    'screenshot',
    'screenshots',
    'har file',
    '.har',
    'trace file',
    'trace.zip',
    'auth file',
    'auth state',
    'raw crawl',
    'raw html',
    'raw pdf',
    'downloaded document',
    'downloaded data',
    'approval guaranteed',
    'guaranteed approval',
    'permit guaranteed',
    'guaranteed permit',
    'permitting outcome guaranteed',
    'legal outcome guaranteed',
    'legal advice',
    'agent will submit',
    'agent will certify',
    'agent will upload',
    'agent will pay',
    'click submit',
    'certify acknowledgement',
    'enter payment',
    'final payment',
    'official upload',
    'schedule inspection',
    'cancel permit',
)

_FORBIDDEN_KEYS = {
    'auth',
    'auth_file',
    'auth_state',
    'authenticated_artifact',
    'browser_artifact',
    'browser_state',
    'cookie',
    'cookies',
    'credentials',
    'devhub_session',
    'downloaded_data',
    'downloaded_document',
    'har',
    'har_file',
    'password',
    'private_artifact',
    'raw_body',
    'raw_crawl',
    'raw_download',
    'raw_html',
    'raw_pdf',
    'screenshot',
    'screenshots',
    'session',
    'session_artifact',
    'storage_state',
    'token',
    'trace',
    'trace_file',
}

_MUTATION_DOMAINS = (
    'active_artifact',
    'active_artifacts',
    'prompt',
    'prompts',
    'release_state',
    'fixture',
    'fixtures',
    'agent_state',
)

_MUTATION_TERMS = (
    'mutated',
    'mutation',
    'changed',
    'updated',
    'applied',
    'requested',
)


class ActivePromotionApprovalIntakeV1Error(ValueError):
    def __init__(self, problems: tuple[str, ...]) -> None:
        self.problems = problems
        super().__init__('invalid active promotion approval intake v1: ' + '; '.join(problems))


def build_active_promotion_approval_intake_v1(preflight_packet: Mapping[str, Any]) -> dict[str, Any]:
    source_result = validate_active_promotion_approval_intake_source_v1(preflight_packet)
    if not source_result['valid']:
        raise ActivePromotionApprovalIntakeV1Error(tuple(source_result['problems']))

    source_id = _text(preflight_packet.get('packet_id'), 'active-preflight-gate-v1')
    decision_rows = _decision_rows(preflight_packet.get('final_go_no_go_rows'))
    blockers = _blocker_rows(preflight_packet.get('active_mutation_blocker_inventory'))
    packet = {
        'packet_type': PACKET_TYPE,
        'packet_id': 'active-promotion-approval-intake-for-' + source_id,
        'source_packet': {
            'packet_type': SOURCE_PACKET_TYPE,
            'packet_id': source_id,
            'fixture_first': True,
        },
        'reviewer_decision_rows': decision_rows,
        'approval_evidence_placeholders': _approval_rows(preflight_packet.get('human_approval_placeholders')),
        'unresolved_blocker_carry_forward': blockers,
        'rollback_readiness_acknowledgements': _rollback_rows(preflight_packet.get('rollback_readiness_summary')),
        'validation_replay_acknowledgements': _validation_rows(preflight_packet.get('validation_replay_checklist')),
        'no_go_reason_placeholders': _no_go_rows(decision_rows, blockers),
        'nonmutation_acknowledgements': {key: False for key in _EXPECTED_NONMUTATION_FLAGS},
        'intake_status': 'pending_reviewer_decisions',
    }
    intake_result = validate_active_promotion_approval_intake_v1(packet)
    if not intake_result['valid']:
        raise ActivePromotionApprovalIntakeV1Error(tuple(intake_result['problems']))
    return packet


def validate_active_promotion_approval_intake_source_v1(packet: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return {'valid': False, 'problems': ['source_packet_must_be_object']}
    if packet.get('packet_type') != SOURCE_PACKET_TYPE:
        problems.append('source_packet_type_must_be_active_promotion_preflight_gate_v1')
    for key in _REQUIRED_SOURCE_SECTIONS:
        if not packet.get(key):
            problems.append('source_missing_' + key)
    _scan(packet, '$', problems)
    return _result(problems)


def validate_active_promotion_approval_intake_v1(packet: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return {'valid': False, 'problems': ['packet_must_be_object']}
    if packet.get('packet_type') != PACKET_TYPE:
        problems.append('invalid_packet_type')
    for section, required_fields in _REQUIRED_INTAKE_ROW_FIELDS.items():
        _validate_required_rows(packet, section, required_fields, problems)
    _validate_nonmutation_flags(packet.get('nonmutation_acknowledgements'), problems)
    _scan(packet, '$', problems)
    return _result(problems)


def require_active_promotion_approval_intake_v1_valid(packet: Mapping[str, Any]) -> None:
    result = validate_active_promotion_approval_intake_v1(packet)
    if not result['valid']:
        raise ActivePromotionApprovalIntakeV1Error(tuple(result['problems']))


def _validate_required_rows(
    packet: Mapping[str, Any],
    section: str,
    required_fields: tuple[str, ...],
    problems: list[str],
) -> None:
    rows = packet.get(section)
    if not isinstance(rows, list) or not rows:
        problems.append('missing_' + section)
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            problems.append(f'{section}[{index}]:row_must_be_object')
            continue
        for field in required_fields:
            if not _has_text(row.get(field)):
                problems.append(f'{section}[{index}]:missing_{field}')


def _validate_nonmutation_flags(flags: Any, problems: list[str]) -> None:
    if not isinstance(flags, Mapping):
        problems.append('missing_nonmutation_acknowledgements')
        return
    for key in _EXPECTED_NONMUTATION_FLAGS:
        if key not in flags:
            problems.append('missing_nonmutation_acknowledgement:' + key)
        elif flags.get(key) is not False:
            problems.append('nonmutation_acknowledgement_must_be_false:' + key)
    for key, value in flags.items():
        if value is not False:
            problems.append('nonmutation_acknowledgement_must_be_false:' + str(key))


def _decision_rows(rows: Any) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    if not isinstance(rows, list):
        return output
    for index, row in enumerate(rows, start=1):
        if isinstance(row, Mapping):
            output.append({
                'order': index,
                'row_id': _text(row.get('row_id'), f'reviewer-decision-row-{index:03d}'),
                'source_decision': _text(row.get('decision'), 'pending_reviewer_decision'),
                'reviewer_decision_placeholder': 'pending_human_reviewer_decision',
                'evidence_placeholder': 'pending_reviewer_evidence_reference',
                'carry_forward_reason': _text(row.get('reason') or row.get('rationale'), 'pending reviewer rationale'),
            })
    return output


def _approval_rows(rows: Any) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    if not isinstance(rows, list):
        return output
    for index, row in enumerate(rows, start=1):
        if isinstance(row, Mapping):
            output.append({
                'order': index,
                'approval_id': _text(row.get('placeholder_id') or row.get('approval_id'), f'approval-evidence-{index:03d}'),
                'required_actor': _text(row.get('required_actor'), 'human_reviewer'),
                'approval_status': 'pending_evidence',
                'evidence_reference_placeholder': 'pending_signed_review_record',
            })
    return output


def _blocker_rows(rows: Any) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    if not isinstance(rows, list):
        return output
    for index, row in enumerate(rows, start=1):
        if isinstance(row, Mapping):
            output.append({
                'order': index,
                'blocker_id': _text(row.get('blocker_id'), f'unresolved-blocker-{index:03d}'),
                'blocked_surface': _text(row.get('blocked_surface') or row.get('blocked_action'), 'active promotion boundary'),
                'carry_forward_status': 'unresolved_pending_reviewer_clearance',
                'clearance_evidence_placeholder': 'pending_blocker_clearance_record',
            })
    return output


def _rollback_rows(summary: Any) -> list[dict[str, Any]]:
    source_status = 'missing'
    summary_text = 'Rollback readiness summary was not supplied.'
    if isinstance(summary, Mapping):
        source_status = _text(summary.get('status'), 'pending_review')
        summary_text = _text(summary.get('summary'), 'Rollback readiness requires reviewer acknowledgement.')
    return [{
        'acknowledgement_id': 'rollback-readiness-acknowledgement-001',
        'source_status': source_status,
        'reviewer_acknowledgement_placeholder': 'pending_rollback_owner_acknowledgement',
        'summary': summary_text,
    }]


def _validation_rows(rows: Any) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    if not isinstance(rows, list):
        return output
    for index, row in enumerate(rows, start=1):
        if isinstance(row, Mapping):
            output.append({
                'order': index,
                'check_id': _text(row.get('check_id'), f'validation-replay-{index:03d}'),
                'source_status': _text(row.get('status'), 'pending_offline_replay'),
                'reviewer_acknowledgement_placeholder': 'pending_validation_replay_acknowledgement',
            })
    return output


def _no_go_rows(decision_rows: list[dict[str, Any]], blockers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in decision_rows:
        decision = str(row.get('source_decision', '')).lower()
        if 'no_go' in decision or 'blocked' in decision:
            output.append({
                'reason_id': f"no-go-reason-{int(row['order']):03d}",
                'source_row_id': str(row['row_id']),
                'reason_placeholder': 'pending_reviewer_no_go_reason',
                'evidence_placeholder': 'pending_no_go_evidence_reference',
            })
    if not output:
        output.append({
            'reason_id': 'no-go-reason-001',
            'source_row_id': 'none_reported_by_source_preflight',
            'reason_placeholder': 'pending_reviewer_no_go_reason_if_any',
            'evidence_placeholder': 'pending_no_go_evidence_reference_if_any',
        })
    for blocker in blockers:
        output.append({
            'reason_id': f"no-go-blocker-{int(blocker['order']):03d}",
            'source_row_id': str(blocker['blocker_id']),
            'reason_placeholder': 'pending_blocker_no_go_reason',
            'evidence_placeholder': 'pending_blocker_evidence_reference',
        })
    return output


def _scan(value: Any, path: str, problems: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = _normalize_key(key)
            child_path = path + '.' + str(key)
            if normalized in _FORBIDDEN_KEYS:
                problems.append(child_path + ':forbidden_artifact_key')
            if child is True and _is_forbidden_mutation_flag(normalized):
                problems.append(child_path + ':forbidden_mutation_flag')
            _scan(child, child_path, problems)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan(child, f'{path}[{index}]', problems)
    elif isinstance(value, str):
        lowered = value.lower()
        for needle in _FORBIDDEN_TEXT:
            if needle in lowered:
                problems.append(path + ':forbidden_text:' + needle)


def _is_forbidden_mutation_flag(normalized_key: str) -> bool:
    return any(domain in normalized_key for domain in _MUTATION_DOMAINS) and any(
        term in normalized_key for term in _MUTATION_TERMS
    )


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace('-', '_').replace(' ', '_')


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _text(value: Any, fallback: str) -> str:
    if _has_text(value):
        return value.strip()
    return fallback


def _result(problems: list[str]) -> dict[str, Any]:
    unique = list(dict.fromkeys(sorted(problems)))
    return {'valid': not unique, 'problems': unique}


__all__ = [
    'ActivePromotionApprovalIntakeV1Error',
    'PACKET_TYPE',
    'SOURCE_PACKET_TYPE',
    'build_active_promotion_approval_intake_v1',
    'require_active_promotion_approval_intake_v1_valid',
    'validate_active_promotion_approval_intake_source_v1',
    'validate_active_promotion_approval_intake_v1',
]
