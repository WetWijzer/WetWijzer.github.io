from __future__ import annotations

import copy
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

JsonObject = dict[str, Any]

PACKET_TYPE = 'ppd.promotion_readiness_checklist.v2'
PACKET_VERSION = 'v2'

CONSUMED_PACKET_KEYS: tuple[str, ...] = (
    'process_model_impact_proposal_v1',
    'guardrail_bundle_impact_proposal_v1',
    'user_gap_analysis_impact_proposal_v1',
    'agent_response_delta_proposal_v1',
    'offline_acceptance_rehearsal_summary_v1',
)

PACKET_LABELS: dict[str, str] = {
    'process_model_impact_proposal_v1': 'process model impact proposal v1',
    'guardrail_bundle_impact_proposal_v1': 'guardrail bundle impact proposal v1',
    'user_gap_analysis_impact_proposal_v1': 'user gap analysis impact proposal v1',
    'agent_response_delta_proposal_v1': 'agent response delta proposal v1',
    'offline_acceptance_rehearsal_summary_v1': 'offline acceptance rehearsal summary v1',
}

DEFAULT_FIXTURE_PATHS: dict[str, str] = {
    'process_model_impact_proposal_v1': 'ppd/tests/fixtures/process_model_impact_proposal_v1/valid_proposal.json',
    'guardrail_bundle_impact_proposal_v1': 'ppd/tests/fixtures/fixture_first_guardrail_bundle_impact_proposal_v1/source_packets.json',
    'user_gap_analysis_impact_proposal_v1': 'ppd/tests/fixtures/user_gap_analysis_impact_proposal_v1/user_gap_analysis.json',
    'agent_response_delta_proposal_v1': 'ppd/tests/fixtures/agent_response_delta_proposal_v1/guarded_agent_response_acceptance_packet_v1.json',
    'offline_acceptance_rehearsal_summary_v1': 'ppd/tests/fixtures/promotion_readiness_checklist_v2/source_packets.json',
}

REQUIRED_ATTESTATIONS: dict[str, bool] = {
    'fixture_first': True,
    'metadata_only': True,
    'no_live_crawl': True,
    'no_devhub': True,
    'no_private_artifact': True,
    'no_official_action': True,
    'no_active_promotion': True,
}

DEFAULT_VALIDATION_COMMANDS: list[list[str]] = [
    ['python3', '-m', 'py_compile', 'ppd/agent_readiness/promotion_readiness_checklist_v2.py'],
    ['python3', '-m', 'pytest', 'ppd/tests/test_promotion_readiness_checklist_v2.py'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

_BLOCKER_ROW_KEYS: tuple[str, ...] = (
    'unresolved_blocker_rows',
    'unresolved_blockers',
    'manual_review_blockers',
    'blockers',
    'unresolved_deferrals',
)

_ROLLBACK_ROW_KEYS: tuple[str, ...] = (
    'rollback_checkpoints',
    'rollback_notes',
    'rollback_verification',
)

_COMMAND_KEYS: tuple[str, ...] = (
    'validation_command_inventory',
    'offline_validation_commands',
    'validation_commands',
    'expected_offline_validation_commands',
)

_FORBIDDEN_ARTIFACT_KEYS: set[str] = {
    'access_token',
    'auth_state',
    'browser_state',
    'cookie',
    'cookies',
    'credentials',
    'devhub_session',
    'downloaded_artifact',
    'downloaded_document',
    'downloaded_pdf',
    'har',
    'local_private_path',
    'password',
    'payment_details',
    'private_artifact',
    'raw_body',
    'raw_crawl_output',
    'raw_download',
    'raw_html',
    'raw_pdf',
    'screenshot',
    'session_artifact',
    'session_state',
    'storage_state',
    'token',
    'trace',
}

_FORBIDDEN_TRUE_KEYS: set[str] = {
    'active_agent_state_mutated',
    'active_document_mutated',
    'active_guardrail_mutated',
    'active_process_mutated',
    'active_promotion',
    'active_prompt_mutated',
    'active_release_state_mutated',
    'active_requirement_mutated',
    'active_source_mutated',
    'active_state_mutated',
    'agent_state_mutated',
    'devhub_execution_performed',
    'document_record_mutated',
    'guardrail_bundle_mutated',
    'live_crawl_executed',
    'live_execution_performed',
    'live_network_called',
    'official_action_performed',
    'process_model_mutated',
    'promotion_executed',
    'prompt_mutated',
    'release_state_mutated',
    'requirement_node_mutated',
    'source_registry_mutated',
}

_FORBIDDEN_TEXT_NEEDLES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ('private_artifact', ('private artifact', 'private applicant', 'applicant-specific', 'case-specific value')),
    ('authenticated_artifact', ('auth state', 'authenticated artifact', 'logged-in page', 'signed-in page')),
    ('session_artifact', ('session cookie', 'storage state', 'access token', 'refresh token', 'credential')),
    ('browser_artifact', ('browser state', 'playwright trace', 'har file', 'screenshot')),
    ('raw_or_download_artifact', ('raw crawl', 'raw html', 'raw body', 'raw pdf', 'downloaded document', 'downloaded data')),
    ('live_execution_or_promotion_claim', ('live execution', 'live crawl executed', 'live run complete', 'promoted to active', 'active promotion complete', 'applied to production', 'promotion executed')),
    ('outcome_guarantee', ('approval guaranteed', 'permit guaranteed', 'will be approved', 'legally compliant', 'no legal risk', 'permit outcome guaranteed')),
    ('consequential_action_execution_language', ('agent will submit', 'automation will submit', 'click submit', 'click pay', 'enter payment', 'execute payment', 'perform upload', 'submit permit', 'upload official')),
)

_MUTATION_WORDS: tuple[str, ...] = (
    'active_source',
    'active_document',
    'active_requirement',
    'active_process',
    'active_guardrail',
    'active_prompt',
    'active_release',
    'active_agent',
    'source_registry_mutat',
    'document_record_mutat',
    'requirement_node_mutat',
    'process_model_mutat',
    'guardrail_bundle_mutat',
    'prompt_mutat',
    'release_state_mutat',
    'agent_state_mutat',
)


class PromotionReadinessChecklistV2Error(ValueError):
    def __init__(self, findings: Iterable[str]) -> None:
        self.findings = tuple(findings)
        super().__init__('invalid promotion readiness checklist v2: ' + '; '.join(self.findings))


def load_json_fixture(path: str | Path) -> JsonObject:
    loaded = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(loaded, dict):
        raise ValueError(f'Expected JSON object fixture at {path}')
    return loaded


def build_from_fixture_path(path: str | Path, *, reviewer_owner: str = 'ppd-promotion-readiness-reviewer') -> JsonObject:
    return build_promotion_readiness_checklist_v2(load_json_fixture(path), reviewer_owner=reviewer_owner)


def build_promotion_readiness_checklist_v2(
    source_packets: Mapping[str, Any],
    *,
    reviewer_owner: str = 'ppd-promotion-readiness-reviewer',
    rollback_note: str = 'Discard this fixture-first checklist and rerun offline validation; active promotion state remains unchanged.',
) -> JsonObject:
    copied_inputs = {key: copy.deepcopy(_required_mapping(source_packets, key)) for key in CONSUMED_PACKET_KEYS}
    consumes = {key: _packet_id(copied_inputs[key], key) for key in CONSUMED_PACKET_KEYS}

    checklist = {
        'packet_type': PACKET_TYPE,
        'packet_version': PACKET_VERSION,
        'checklist_id': 'fixture-first-promotion-readiness-checklist-v2',
        'fixture_first': True,
        'metadata_only': True,
        'consumes': consumes,
        'ordered_readiness_checks': _readiness_checks(copied_inputs, reviewer_owner, rollback_note),
        'unresolved_blocker_rows': _unresolved_blocker_rows(copied_inputs, reviewer_owner, rollback_note),
        'fixture_family_inspection_targets': _fixture_family_inspection_targets(copied_inputs, reviewer_owner),
        'rollback_checkpoints': _rollback_checkpoints(copied_inputs, reviewer_owner, rollback_note),
        'validation_command_inventory': _validation_commands(copied_inputs),
        'attestations': dict(REQUIRED_ATTESTATIONS),
    }
    assert_valid_promotion_readiness_checklist_v2(checklist)
    return checklist


def validate_promotion_readiness_checklist_v2(checklist: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    if not isinstance(checklist, Mapping):
        return ['checklist must be an object']

    if checklist.get('packet_type') != PACKET_TYPE:
        findings.append(f'packet_type must be {PACKET_TYPE}')
    if checklist.get('packet_version') != PACKET_VERSION:
        findings.append('packet_version must be v2')
    if checklist.get('fixture_first') is not True:
        findings.append('fixture_first must be true')
    if checklist.get('metadata_only') is not True:
        findings.append('metadata_only must be true')

    consumes = checklist.get('consumes')
    if not isinstance(consumes, Mapping):
        findings.append('consumes must be an object')
    else:
        for key in CONSUMED_PACKET_KEYS:
            if not _non_empty_text(consumes.get(key)):
                findings.append(f'consumes.{key} is required')

    checks = _mapping_sequence(checklist.get('ordered_readiness_checks'))
    if len(checks) != len(CONSUMED_PACKET_KEYS):
        findings.append('ordered_readiness_checks must contain one cited check per consumed packet')
    expected_order = 1
    seen_check_ids: list[str] = []
    seen_check_sources: set[str] = set()
    for index, row in enumerate(checks):
        prefix = f'ordered_readiness_checks[{index}]'
        check_id = _text(row.get('readiness_check_id'))
        source_packet = _text(row.get('source_packet'))
        if not check_id:
            findings.append(f'{prefix}.readiness_check_id is required')
        if row.get('order') != expected_order:
            findings.append(f'{prefix}.order must be {expected_order}')
        if not _non_empty_string_list(row.get('citations')):
            findings.append(f'{prefix}.citations is required')
        if source_packet not in CONSUMED_PACKET_KEYS:
            findings.append(f'{prefix}.source_packet must name a consumed packet')
        else:
            seen_check_sources.add(source_packet)
        if not _non_empty_text(row.get('required_result')):
            findings.append(f'{prefix}.required_result is required')
        if not _non_empty_text(row.get('reviewer_owner')):
            findings.append(f'{prefix}.reviewer_owner is required')
        if not _non_empty_text(row.get('rollback_note')):
            findings.append(f'{prefix}.rollback_note is required')
        for dependency in _string_list(row.get('depends_on_check_ids')):
            if dependency not in seen_check_ids:
                findings.append(f'{prefix}.depends_on_check_ids contains an out-of-order dependency')
        if check_id:
            seen_check_ids.append(check_id)
        expected_order += 1
    for key in CONSUMED_PACKET_KEYS:
        if key not in seen_check_sources:
            findings.append(f'ordered_readiness_checks missing source_packet {key}')

    blockers = _mapping_sequence(checklist.get('unresolved_blocker_rows'))
    if not blockers:
        findings.append('unresolved_blocker_rows must contain at least one blocker or none-reported row')
    has_blocker_handling = False
    for index, row in enumerate(blockers):
        prefix = f'unresolved_blocker_rows[{index}]'
        status = _text(row.get('status'))
        if not _non_empty_text(row.get('blocker_id')):
            findings.append(f'{prefix}.blocker_id is required')
        if status not in {'unresolved', 'manual_review_required', 'blocked_pending_review', 'none_reported'}:
            findings.append(f'{prefix}.status must be unresolved, manual_review_required, blocked_pending_review, or none_reported')
        else:
            has_blocker_handling = True
        if not _non_empty_text(row.get('summary')):
            findings.append(f'{prefix}.summary is required')
        if not _non_empty_string_list(row.get('citations')):
            findings.append(f'{prefix}.citations is required')
        if not _non_empty_text(row.get('reviewer_owner')):
            findings.append(f'{prefix}.reviewer_owner is required')
        if not _non_empty_text(row.get('rollback_note')):
            findings.append(f'{prefix}.rollback_note is required')
    if not has_blocker_handling:
        findings.append('unresolved_blocker_rows must document unresolved blocker handling')

    targets = _mapping_sequence(checklist.get('fixture_family_inspection_targets'))
    if len(targets) != len(CONSUMED_PACKET_KEYS):
        findings.append('fixture_family_inspection_targets must contain one inspection target per consumed fixture family')
    seen_target_families: set[str] = set()
    for index, row in enumerate(targets):
        prefix = f'fixture_family_inspection_targets[{index}]'
        fixture_family = _text(row.get('fixture_family'))
        if not _non_empty_text(row.get('target_id')):
            findings.append(f'{prefix}.target_id is required')
        if fixture_family not in CONSUMED_PACKET_KEYS:
            findings.append(f'{prefix}.fixture_family must name a consumed fixture family')
        else:
            seen_target_families.add(fixture_family)
        if not _text(row.get('fixture_path')).startswith('ppd/tests/fixtures/'):
            findings.append(f'{prefix}.fixture_path must stay under ppd/tests/fixtures')
        if not _non_empty_string_list(row.get('inspection_focus')):
            findings.append(f'{prefix}.inspection_focus is required')
        if not _non_empty_string_list(row.get('citations')):
            findings.append(f'{prefix}.citations is required')
        if not _non_empty_text(row.get('reviewer_owner')):
            findings.append(f'{prefix}.reviewer_owner is required')
    for key in CONSUMED_PACKET_KEYS:
        if key not in seen_target_families:
            findings.append(f'fixture_family_inspection_targets missing fixture_family {key}')

    rollbacks = _mapping_sequence(checklist.get('rollback_checkpoints'))
    if not rollbacks:
        findings.append('rollback_checkpoints must contain rollback checkpoints')
    has_active_state_checkpoint = False
    for index, row in enumerate(rollbacks):
        prefix = f'rollback_checkpoints[{index}]'
        if not _non_empty_text(row.get('checkpoint_id')):
            findings.append(f'{prefix}.checkpoint_id is required')
        if not _non_empty_text(row.get('rollback_scope')):
            findings.append(f'{prefix}.rollback_scope is required')
        if _text(row.get('checkpoint_status')) not in {'available', 'manual_confirmation_required'}:
            findings.append(f'{prefix}.checkpoint_status must be available or manual_confirmation_required')
        if not _non_empty_string_list(row.get('citations')):
            findings.append(f'{prefix}.citations is required')
        if not _non_empty_text(row.get('reviewer_owner')):
            findings.append(f'{prefix}.reviewer_owner is required')
        if not _non_empty_text(row.get('rollback_note')):
            findings.append(f'{prefix}.rollback_note is required')
        if 'active-state-unchanged' in _text(row.get('checkpoint_id')):
            has_active_state_checkpoint = True
    if not has_active_state_checkpoint:
        findings.append('rollback_checkpoints must include active-state-unchanged checkpoint')

    commands = checklist.get('validation_command_inventory')
    if not isinstance(commands, list) or not commands:
        findings.append('validation_command_inventory must contain commands')
    else:
        normalized_commands: list[list[str]] = []
        for index, command in enumerate(commands):
            if not _non_empty_string_list(command):
                findings.append(f'validation_command_inventory[{index}] must be an argv list of strings')
            else:
                normalized_commands.append([str(part) for part in command])
        if ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'] not in normalized_commands:
            findings.append('validation_command_inventory must include ppd daemon self-test command')

    attestations = checklist.get('attestations')
    if not isinstance(attestations, Mapping):
        findings.append('attestations must be an object')
    else:
        for key, expected in REQUIRED_ATTESTATIONS.items():
            if attestations.get(key) is not expected:
                findings.append(f'attestations.{key} must be {expected}')

    _find_forbidden_content(checklist, '$', findings)
    return sorted(dict.fromkeys(findings))


def assert_valid_promotion_readiness_checklist_v2(checklist: Mapping[str, Any]) -> None:
    findings = validate_promotion_readiness_checklist_v2(checklist)
    if findings:
        raise PromotionReadinessChecklistV2Error(findings)


def _required_mapping(source_packets: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source_packets.get(key)
    if not isinstance(value, Mapping):
        raise PromotionReadinessChecklistV2Error((f'{key} must be an object',))
    findings: list[str] = []
    _find_forbidden_content(value, key, findings)
    if findings:
        raise PromotionReadinessChecklistV2Error(findings)
    return value


def _readiness_checks(source_packets: Mapping[str, Mapping[str, Any]], reviewer_owner: str, rollback_note: str) -> list[JsonObject]:
    checks: list[JsonObject] = []
    previous_check_ids: list[str] = []
    for order, key in enumerate(CONSUMED_PACKET_KEYS, start=1):
        packet = source_packets[key]
        check_id = f'promotion-readiness-v2-{order:02d}-{key}'
        checks.append(
            {
                'readiness_check_id': check_id,
                'order': order,
                'source_packet': key,
                'source_packet_id': _packet_id(packet, key),
                'summary': f'Inspect cited {PACKET_LABELS[key]} evidence before any later promotion decision.',
                'required_result': 'ready_for_manual_offline_review',
                'citations': _collect_citations(packet) or [key],
                'depends_on_check_ids': list(previous_check_ids),
                'reviewer_owner': reviewer_owner,
                'rollback_note': rollback_note,
            }
        )
        previous_check_ids.append(check_id)
    return checks


def _unresolved_blocker_rows(source_packets: Mapping[str, Mapping[str, Any]], reviewer_owner: str, rollback_note: str) -> list[JsonObject]:
    rows: list[JsonObject] = []
    for source_key, packet in source_packets.items():
        for row in _rows_from_keys(packet, _BLOCKER_ROW_KEYS):
            rows.append(
                {
                    'blocker_id': _text(row.get('blocker_id') or row.get('id') or row.get('row_id') or row.get('deferral_id')) or f'{source_key}-blocker-{len(rows) + 1}',
                    'source_packet': source_key,
                    'summary': _text(row.get('summary') or row.get('description') or row.get('reason')) or f'Manual review blocker from {PACKET_LABELS[source_key]}.',
                    'status': _normalize_blocker_status(row.get('status') or row.get('disposition')),
                    'citations': _collect_citations(row) or _collect_citations(packet) or [source_key],
                    'reviewer_owner': _text(row.get('reviewer_owner')) or reviewer_owner,
                    'rollback_note': _text(row.get('rollback_note')) or rollback_note,
                }
            )
    if rows:
        return rows
    return [
        {
            'blocker_id': 'promotion-readiness-v2-no-unresolved-blockers-reported',
            'source_packet': 'promotion_readiness_checklist_v2_builder',
            'summary': 'Consumed fixture packets did not report unresolved blockers; reviewer must still confirm attestations offline.',
            'status': 'none_reported',
            'citations': list(CONSUMED_PACKET_KEYS),
            'reviewer_owner': reviewer_owner,
            'rollback_note': rollback_note,
        }
    ]


def _fixture_family_inspection_targets(source_packets: Mapping[str, Mapping[str, Any]], reviewer_owner: str) -> list[JsonObject]:
    targets: list[JsonObject] = []
    for key, packet in source_packets.items():
        fixture_path = _text(packet.get('fixture_path') or packet.get('source_fixture_path')) or DEFAULT_FIXTURE_PATHS[key]
        targets.append(
            {
                'target_id': f'promotion-readiness-v2-inspect-{key}',
                'fixture_family': key,
                'fixture_path': fixture_path,
                'source_packet_id': _packet_id(packet, key),
                'inspection_focus': _inspection_focus(key),
                'citations': _collect_citations(packet) or [key],
                'reviewer_owner': reviewer_owner,
            }
        )
    return targets


def _rollback_checkpoints(source_packets: Mapping[str, Mapping[str, Any]], reviewer_owner: str, rollback_note: str) -> list[JsonObject]:
    rows: list[JsonObject] = []
    for source_key, packet in source_packets.items():
        source_rows = _rows_from_keys(packet, _ROLLBACK_ROW_KEYS)
        if not source_rows and _non_empty_text(packet.get('rollback_note')):
            source_rows = [{'summary': packet.get('rollback_note'), 'citations': _collect_citations(packet)}]
        for row in source_rows:
            rows.append(
                {
                    'checkpoint_id': _text(row.get('checkpoint_id') or row.get('id') or row.get('row_id')) or f'{source_key}-rollback-{len(rows) + 1}',
                    'source_packet': source_key,
                    'rollback_scope': _text(row.get('rollback_scope') or row.get('summary') or row.get('rollback_note')) or f'Discard fixture output derived from {PACKET_LABELS[source_key]}.',
                    'checkpoint_status': 'manual_confirmation_required',
                    'citations': _collect_citations(row) or _collect_citations(packet) or [source_key],
                    'reviewer_owner': _text(row.get('reviewer_owner')) or reviewer_owner,
                    'rollback_note': rollback_note,
                }
            )
    rows.append(
        {
            'checkpoint_id': 'promotion-readiness-v2-active-state-unchanged',
            'source_packet': 'promotion_readiness_checklist_v2_builder',
            'rollback_scope': 'Confirm no active promotion state was changed by this checklist.',
            'checkpoint_status': 'available',
            'citations': list(CONSUMED_PACKET_KEYS),
            'reviewer_owner': reviewer_owner,
            'rollback_note': rollback_note,
        }
    )
    return rows


def _validation_commands(source_packets: Mapping[str, Mapping[str, Any]]) -> list[list[str]]:
    commands = [list(command) for command in DEFAULT_VALIDATION_COMMANDS]
    for packet in source_packets.values():
        for key in _COMMAND_KEYS:
            for command in _sequence(packet.get(key)):
                if _non_empty_string_list(command):
                    normalized = [str(part) for part in command]
                    if normalized not in commands:
                        commands.append(normalized)
    return commands


def _rows_from_keys(packet: Mapping[str, Any], keys: Sequence[str]) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    for key in keys:
        value = packet.get(key)
        if isinstance(value, Mapping):
            rows.append(value)
        else:
            for item in _sequence(value):
                if isinstance(item, Mapping):
                    rows.append(item)
                elif isinstance(item, str) and item.strip():
                    rows.append({'summary': item})
    return rows


def _inspection_focus(key: str) -> list[str]:
    focus = {
        'process_model_impact_proposal_v1': ['required user facts', 'required documents', 'file rules', 'deadlines', 'action gates'],
        'guardrail_bundle_impact_proposal_v1': ['predicates', 'explanation templates', 'exact confirmation gates', 'refused actions'],
        'user_gap_analysis_impact_proposal_v1': ['missing facts', 'matched documents', 'blocked actions', 'next safe actions'],
        'agent_response_delta_proposal_v1': ['explanations', 'refusals', 'missing information prompts', 'blocked-action outcomes'],
        'offline_acceptance_rehearsal_summary_v1': ['acceptance rows', 'manual review blockers', 'rollback checkpoints', 'validation commands'],
    }
    return focus[key]


def _packet_id(packet: Mapping[str, Any], fallback: str) -> str:
    for key in ('proposal_id', 'packet_id', 'checklist_id', 'summary_id', 'impact_proposal_id'):
        value = packet.get(key)
        if _non_empty_text(value):
            return str(value)
    return fallback


def _normalize_blocker_status(value: Any) -> str:
    status = _text(value).lower()
    if status in {'unresolved', 'manual_review_required', 'blocked_pending_review', 'none_reported'}:
        return status
    if status in {'blocked', 'needs_review', 'review_required', 'manual_review'}:
        return 'manual_review_required'
    return 'unresolved'


def _collect_citations(value: Any) -> list[str]:
    citations: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in {'citations', 'source_evidence_ids', 'fixture_refs', 'source_fixture_refs'}:
                if isinstance(child, Mapping):
                    citations.extend(str(item) for item in child.values() if _non_empty_text(item))
                else:
                    citations.extend(_string_list(child))
            else:
                citations.extend(_collect_citations(child))
    elif isinstance(value, list):
        for item in value:
            citations.extend(_collect_citations(item))
    return _dedupe(citations)


def _find_forbidden_content(value: Any, path: str, findings: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f'{path}.{key}'
            normalized = _normalize_key(key)
            if normalized in _FORBIDDEN_ARTIFACT_KEYS:
                findings.append(f'{child_path}: forbidden_artifact_key')
            if normalized in _FORBIDDEN_TRUE_KEYS and child is True:
                findings.append(f'{child_path}: forbidden_live_official_or_promotion_flag')
            if child is True and not normalized.startswith('no_') and any(word in normalized for word in _MUTATION_WORDS):
                findings.append(f'{child_path}: active_mutation_flag')
            _find_forbidden_content(child, child_path, findings)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _find_forbidden_content(child, f'{path}[{index}]', findings)
    elif isinstance(value, str):
        lowered = value.lower()
        for code, needles in _FORBIDDEN_TEXT_NEEDLES:
            if any(needle in lowered for needle in needles):
                findings.append(f'{path}: {code}')


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace('-', '_').replace(' ', '_')


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    return [item for item in _sequence(value) if isinstance(item, Mapping)]


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if _non_empty_text(item)]
    return []


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_non_empty_text(item) for item in value)


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _dedupe(values: Iterable[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if _non_empty_text(value) and value not in deduped:
            deduped.append(value)
    return deduped


__all__ = [
    'CONSUMED_PACKET_KEYS',
    'DEFAULT_VALIDATION_COMMANDS',
    'PACKET_TYPE',
    'PACKET_VERSION',
    'REQUIRED_ATTESTATIONS',
    'PromotionReadinessChecklistV2Error',
    'assert_valid_promotion_readiness_checklist_v2',
    'build_from_fixture_path',
    'build_promotion_readiness_checklist_v2',
    'load_json_fixture',
    'validate_promotion_readiness_checklist_v2',
]
