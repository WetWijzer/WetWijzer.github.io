'''Fixture-first guardrail recompile reviewer packet v4.'''

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ppd.agent_readiness.guardrail_bundle_recompile_candidate_v4 import (
    GuardrailBundleRecompileCandidateV4Error,
    REQUIRED_CHANGE_CATEGORIES,
    load_guardrail_bundle_recompile_candidate_v4_manifest,
    require_valid_guardrail_bundle_recompile_candidate_v4,
)

PACKET_TYPE = 'ppd.guardrail_recompile_reviewer_packet.v4'
PACKET_VERSION = 'v4'
MODE = 'fixture_first_guardrail_bundle_recompile_candidate_v4_review_only'
CANDIDATE_TYPE = 'ppd.guardrail_bundle_recompile_candidate.v4'

OFFLINE_VALIDATION_COMMANDS = [
    ['python3', '-m', 'py_compile', 'ppd/agent_readiness/guardrail_recompile_reviewer_packet_v4.py'],
    ['python3', '-m', 'unittest', 'ppd.tests.test_guardrail_recompile_reviewer_packet_v4'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

REQUIRED_ATTESTATIONS = {
    'fixture_first': True,
    'guardrail_bundle_recompile_candidate_v4_fixtures_only': True,
    'review_only': True,
    'inactive_candidate_only': True,
    'deterministic': True,
    'no_active_guardrail_bundle_mutation': True,
    'no_devhub_open': True,
    'no_private_or_session_artifacts': True,
    'no_upload': True,
    'no_submission': True,
    'no_certification': True,
    'no_payment': True,
    'no_scheduling': True,
    'no_legal_or_permitting_guarantee': True,
}

SUMMARY_CATEGORIES = {
    'reversible_action_predicates': 'reversible_action_summaries',
    'exact_confirmation_predicates': 'exact_confirmation_summaries',
    'refused_consequential_action_predicates': 'refused_action_summaries',
}

MUTATION_FLAGS = (
    'active_mutation',
    'active_bundle_mutation',
    'active_guardrail_mutation',
    'active_guardrail_bundle_mutation',
    'active_prompt_mutation',
    'active_process_model_mutation',
    'active_mutation_claim',
    'guardrail_mutation_claim',
    'guardrail_bundle_mutation_claim',
    'guardrails_changed',
    'guardrail_bundles_changed',
    'prompts_changed',
    'process_models_changed',
    'mutates_active_guardrails',
    'updates_active_guardrails',
    'opens_devhub',
    'uses_private_artifacts',
    'uses_session_artifacts',
    'uploads',
    'submits',
    'certifies',
    'pays',
    'schedules',
)

PRIVATE_KEY_FRAGMENTS = (
    'auth_state',
    'browser_state',
    'cookie',
    'credential',
    'har',
    'password',
    'private_artifact',
    'session_file',
    'session_path',
    'session_state',
    'storage_state',
    'trace_file',
)

FORBIDDEN_STRING_FRAGMENTS = (
    'opened devhub',
    'authenticated devhub',
    'live devhub',
    'live crawl',
    'active guardrail mutation',
    'active guardrail bundle mutation',
    'mutated active guardrail',
    'mutates active guardrail',
    'updated active guardrail',
    'updates active guardrail',
    'guardrails changed',
    'submitted permit',
    'official action completed',
    'completed official action',
    'certified acknowledgement',
    'paid fee',
    'payment completed',
    'scheduled inspection',
    'permit will be approved',
    'guarantee approval',
    'legal guarantee',
    'permitting guarantee',
)


@dataclass(frozen=True)
class GuardrailRecompileReviewerPacketV4Result:
    valid: bool
    problems: tuple[str, ...]


class GuardrailRecompileReviewerPacketV4Error(ValueError):
    '''Raised when a guardrail recompile reviewer packet v4 is invalid.'''


def load_guardrail_recompile_reviewer_packet_v4_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    manifest = _load_json_object(manifest_path)
    candidate_ref = _text(manifest.get('guardrail_bundle_recompile_candidate_v4_fixture'))
    if not candidate_ref:
        raise ValueError('manifest must include guardrail_bundle_recompile_candidate_v4_fixture')
    if set(manifest) - {'manifest_id', 'guardrail_bundle_recompile_candidate_v4_fixture'}:
        raise ValueError('manifest may only reference a guardrail bundle recompile candidate v4 fixture')
    candidate = load_guardrail_bundle_recompile_candidate_v4_manifest(manifest_path.parent / candidate_ref)
    return build_guardrail_recompile_reviewer_packet_v4(
        candidate,
        source_manifest_id=_text(manifest.get('manifest_id'), 'inline-guardrail-recompile-reviewer-packet-v4'),
        candidate_fixture_ref=candidate_ref,
    )


def build_guardrail_recompile_reviewer_packet_v4(
    guardrail_bundle_recompile_candidate_v4: Mapping[str, Any],
    source_manifest_id: str = 'inline-fixtures',
    candidate_fixture_ref: str = 'guardrail_bundle_recompile_candidate_v4/input_manifest.json',
) -> dict[str, Any]:
    try:
        require_valid_guardrail_bundle_recompile_candidate_v4(guardrail_bundle_recompile_candidate_v4)
    except GuardrailBundleRecompileCandidateV4Error as exc:
        raise GuardrailRecompileReviewerPacketV4Error(str(exc)) from exc

    candidate_rows = _mapping_sequence(guardrail_bundle_recompile_candidate_v4.get('inactive_deterministic_predicate_changes'))
    reviewer_rows = [_reviewer_row(index, row) for index, row in enumerate(candidate_rows)]
    summaries = _summary_sections(reviewer_rows)
    packet = {
        'packet_type': PACKET_TYPE,
        'packet_version': PACKET_VERSION,
        'mode': MODE,
        'source_manifest_id': source_manifest_id,
        'consumes': {'guardrail_bundle_recompile_candidate_v4_fixture': candidate_fixture_ref},
        'candidate_packet_type': guardrail_bundle_recompile_candidate_v4.get('packet_type'),
        'candidate_guardrail_bundle_ids': list(guardrail_bundle_recompile_candidate_v4.get('candidate_guardrail_bundle_ids', [])),
        'reviewer_predicate_rows': reviewer_rows,
        'cited_process_impact_references': _cited_process_impact_references(reviewer_rows),
        'stale_evidence_stop_gates': _stale_evidence_stop_gates(reviewer_rows),
        'reversible_action_summaries': summaries['reversible_action_summaries'],
        'exact_confirmation_summaries': summaries['exact_confirmation_summaries'],
        'refused_action_summaries': summaries['refused_action_summaries'],
        'unresolved_reviewer_holds': _unresolved_reviewer_holds(guardrail_bundle_recompile_candidate_v4, reviewer_rows),
        'rollback_notes': list(guardrail_bundle_recompile_candidate_v4.get('rollback_notes', [])),
        'validation_status': {
            'status': 'review_packet_validated_offline_only',
            'candidate_validation_status': _mapping(guardrail_bundle_recompile_candidate_v4.get('validation_status')).get('status'),
            'active_bundle_mutation': False,
            'validation_commands': OFFLINE_VALIDATION_COMMANDS,
        },
        'offline_validation_commands': OFFLINE_VALIDATION_COMMANDS,
        'attestations': dict(REQUIRED_ATTESTATIONS),
    }
    require_valid_guardrail_recompile_reviewer_packet_v4(packet)
    return packet


def validate_guardrail_recompile_reviewer_packet_v4(packet: Mapping[str, Any]) -> GuardrailRecompileReviewerPacketV4Result:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return GuardrailRecompileReviewerPacketV4Result(False, ('packet must be an object',))
    if packet.get('packet_type') != PACKET_TYPE:
        problems.append(f'packet_type must be {PACKET_TYPE}')
    if packet.get('packet_version') != PACKET_VERSION:
        problems.append('packet_version must be v4')
    if packet.get('mode') != MODE:
        problems.append(f'mode must be {MODE}')
    if packet.get('candidate_packet_type') != CANDIDATE_TYPE:
        problems.append(f'candidate_packet_type must be {CANDIDATE_TYPE}')
    if not _text(packet.get('source_manifest_id')):
        problems.append('source_manifest_id must be present')
    if not _text_sequence(packet.get('candidate_guardrail_bundle_ids')):
        problems.append('candidate_guardrail_bundle_ids must be non-empty')

    consumes = _mapping(packet.get('consumes'))
    if set(consumes) != {'guardrail_bundle_recompile_candidate_v4_fixture'}:
        problems.append('consumes must contain only guardrail_bundle_recompile_candidate_v4_fixture')
    if not _text(consumes.get('guardrail_bundle_recompile_candidate_v4_fixture')).endswith('.json'):
        problems.append('guardrail_bundle_recompile_candidate_v4_fixture must point to a JSON fixture')

    rows = _mapping_sequence(packet.get('reviewer_predicate_rows'))
    categories = tuple(_text(row.get('category')) for row in rows)
    if categories != REQUIRED_CHANGE_CATEGORIES:
        problems.append('reviewer_predicate_rows must cover candidate categories in deterministic order')
    for index, row in enumerate(rows):
        prefix = f'reviewer_predicate_rows[{index}]'
        if not _text(row.get('reviewer_row_id')):
            problems.append(f'{prefix}.reviewer_row_id must be present')
        if not _text(row.get('candidate_change_id')):
            problems.append(f'{prefix}.candidate_change_id must be present')
        if not _text(row.get('placeholder_guardrail_bundle_id')):
            problems.append(f'{prefix}.placeholder_guardrail_bundle_id must be present')
        if not _text(row.get('placeholder_predicate_slot')):
            problems.append(f'{prefix}.placeholder_predicate_slot must be present')
        if row.get('review_status') != 'pending_human_review':
            problems.append(f'{prefix}.review_status must be pending_human_review')
        if row.get('reviewer_hold_status') != 'unresolved':
            problems.append(f'{prefix}.reviewer_hold_status must be unresolved')
        if not _text(row.get('reviewer_ready_predicate')):
            problems.append(f'{prefix}.reviewer_ready_predicate must be present')
        cited_refs = _mapping_sequence(row.get('cited_process_impact_refs'))
        if not cited_refs:
            problems.append(f'{prefix}.cited_process_impact_refs must be non-empty')
        for ref_index, ref in enumerate(cited_refs):
            ref_prefix = f'{prefix}.cited_process_impact_refs[{ref_index}]'
            if not _text(ref.get('impact_id')):
                problems.append(f'{ref_prefix}.impact_id must be present')
            if not _text(ref.get('process_id')):
                problems.append(f'{ref_prefix}.process_id must be present')
            if not _text_sequence(ref.get('citation_refs')):
                problems.append(f'{ref_prefix}.citation_refs must be non-empty')
        if row.get('process_impact_reference_count') != len(cited_refs):
            problems.append(f'{prefix}.process_impact_reference_count must match cited_process_impact_refs')
        if not _text(row.get('action_boundary_summary')):
            problems.append(f'{prefix}.action_boundary_summary must be present')
        if row.get('active_bundle_mutation') is not False:
            problems.append(f'{prefix}.active_bundle_mutation must be false')
        if not _text(row.get('rollback_note_ref')):
            problems.append(f'{prefix}.rollback_note_ref must be present')

    cited_refs = _mapping_sequence(packet.get('cited_process_impact_references'))
    if not cited_refs:
        problems.append('cited_process_impact_references must be non-empty')
    for index, ref in enumerate(cited_refs):
        prefix = f'cited_process_impact_references[{index}]'
        if not _text(ref.get('impact_id')):
            problems.append(f'{prefix}.impact_id must be present')
        if not _text(ref.get('process_id')):
            problems.append(f'{prefix}.process_id must be present')
        if not _text_sequence(ref.get('citation_refs')):
            problems.append(f'{prefix}.citation_refs must be non-empty')
        if not _text_sequence(ref.get('used_by_reviewer_row_ids')):
            problems.append(f'{prefix}.used_by_reviewer_row_ids must be non-empty')

    stop_gates = _mapping_sequence(packet.get('stale_evidence_stop_gates'))
    if not stop_gates:
        problems.append('stale_evidence_stop_gates must be non-empty')
    for index, gate in enumerate(stop_gates):
        prefix = f'stale_evidence_stop_gates[{index}]'
        if not _text(gate.get('gate_id')):
            problems.append(f'{prefix}.gate_id must be present')
        if gate.get('blocked_until_resolved') is not True:
            problems.append(f'{prefix}.blocked_until_resolved must be true')
        if not _text_sequence(gate.get('reviewer_row_ids')):
            problems.append(f'{prefix}.reviewer_row_ids must be non-empty')
        if not _mapping_sequence(gate.get('cited_process_impact_refs')):
            problems.append(f'{prefix}.cited_process_impact_refs must be non-empty')

    for key in ('reversible_action_summaries', 'exact_confirmation_summaries', 'refused_action_summaries'):
        summaries = _mapping_sequence(packet.get(key))
        if not summaries:
            problems.append(f'{key} must be non-empty')
        for index, summary in enumerate(summaries):
            prefix = f'{key}[{index}]'
            if not _text(summary.get('summary_id')):
                problems.append(f'{prefix}.summary_id must be present')
            if not _text(summary.get('reviewer_row_id')):
                problems.append(f'{prefix}.reviewer_row_id must be present')
            if not _text(summary.get('predicate')):
                problems.append(f'{prefix}.predicate must be present')
            if not _text(summary.get('boundary')):
                problems.append(f'{prefix}.boundary must be present')
            if not _text_sequence(summary.get('citation_refs')):
                problems.append(f'{prefix}.citation_refs must be non-empty')

    holds = _mapping_sequence(packet.get('unresolved_reviewer_holds'))
    if not holds:
        problems.append('unresolved_reviewer_holds must be non-empty')
    for index, hold in enumerate(holds):
        prefix = f'unresolved_reviewer_holds[{index}]'
        if not _text(hold.get('hold_id')):
            problems.append(f'{prefix}.hold_id must be present')
        if hold.get('release_state') != 'held':
            problems.append(f'{prefix}.release_state must be held')

    rollback_notes = _mapping_sequence(packet.get('rollback_notes'))
    if not rollback_notes:
        problems.append('rollback_notes must be non-empty')
    for index, note in enumerate(rollback_notes):
        prefix = f'rollback_notes[{index}]'
        if not _text(note.get('rollback_id')):
            problems.append(f'{prefix}.rollback_id must be present')
        if not _text(note.get('action')):
            problems.append(f'{prefix}.action must be present')
        if not _text(note.get('verification')):
            problems.append(f'{prefix}.verification must be present')

    validation_status = _mapping(packet.get('validation_status'))
    if validation_status.get('status') != 'review_packet_validated_offline_only':
        problems.append('validation_status.status must be review_packet_validated_offline_only')
    if validation_status.get('active_bundle_mutation') is not False:
        problems.append('validation_status.active_bundle_mutation must be false')
    if validation_status.get('validation_commands') != OFFLINE_VALIDATION_COMMANDS:
        problems.append('validation_status.validation_commands must exactly match offline_validation_commands')
    if packet.get('offline_validation_commands') != OFFLINE_VALIDATION_COMMANDS:
        problems.append('offline_validation_commands must exactly match the reviewer packet command bundle')

    attestations = _mapping(packet.get('attestations'))
    for key, expected in REQUIRED_ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            problems.append(f'attestations.{key} must be true')

    _validate_no_forbidden_state(packet, problems)
    return GuardrailRecompileReviewerPacketV4Result(not problems, tuple(problems))


def require_valid_guardrail_recompile_reviewer_packet_v4(packet: Mapping[str, Any]) -> None:
    result = validate_guardrail_recompile_reviewer_packet_v4(packet)
    if not result.valid:
        raise GuardrailRecompileReviewerPacketV4Error('invalid guardrail recompile reviewer packet v4: ' + '; '.join(result.problems))


def _reviewer_row(index: int, candidate_row: Mapping[str, Any]) -> dict[str, Any]:
    category = _text(candidate_row.get('category'))
    cited_refs = _mapping_sequence(candidate_row.get('source_impact_refs'))
    return {
        'reviewer_row_id': f'reviewer-v4-{index + 1:02d}-{category}',
        'candidate_change_id': _text(candidate_row.get('change_id')),
        'category': category,
        'placeholder_guardrail_bundle_id': _text(candidate_row.get('placeholder_guardrail_bundle_id')),
        'placeholder_predicate_slot': _text(candidate_row.get('placeholder_predicate_slot')),
        'reviewer_ready_predicate': _text(candidate_row.get('proposed_inactive_predicate')),
        'cited_process_impact_refs': [
            {
                'impact_id': _text(ref.get('impact_id')),
                'process_id': _text(ref.get('process_id')),
                'citation_refs': _text_sequence(ref.get('citation_refs')),
            }
            for ref in cited_refs
        ],
        'process_impact_reference_count': len(cited_refs),
        'process_impact_reference_status': 'cited_fixture_references_only',
        'review_status': 'pending_human_review',
        'reviewer_hold_status': 'unresolved',
        'action_boundary_summary': _action_boundary_summary(category),
        'active_bundle_mutation': False,
        'rollback_note_ref': _text(candidate_row.get('rollback_note_ref')),
    }


def _cited_process_impact_references(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    references: list[dict[str, Any]] = []
    for row in rows:
        for ref in _mapping_sequence(row.get('cited_process_impact_refs')):
            key = (_text(ref.get('impact_id')), _text(ref.get('process_id')))
            if key in seen:
                continue
            seen.add(key)
            references.append(
                {
                    'impact_id': key[0],
                    'process_id': key[1],
                    'citation_refs': _text_sequence(ref.get('citation_refs')),
                    'used_by_reviewer_row_ids': [
                        _text(other.get('reviewer_row_id'))
                        for other in rows
                        if any(_text(item.get('impact_id')) == key[0] for item in _mapping_sequence(other.get('cited_process_impact_refs')))
                    ],
                }
            )
    return references


def _stale_evidence_stop_gates(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    stale_rows = [row for row in rows if _text(row.get('category')) == 'stale_evidence_block_predicates']
    return [
        {
            'gate_id': 'stop-stale-evidence-reviewer-disposition-required-v4',
            'stop_condition': 'stale_or_conflicting_cited_process_impact_reference',
            'disposition_required': 'human_reviewer_must_resolve_before_activation',
            'blocked_until_resolved': True,
            'reviewer_row_ids': [_text(row.get('reviewer_row_id')) for row in stale_rows],
            'cited_process_impact_refs': [
                ref
                for row in stale_rows
                for ref in _mapping_sequence(row.get('cited_process_impact_refs'))
            ],
        }
    ]


def _summary_sections(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    summaries: dict[str, list[dict[str, Any]]] = {
        'reversible_action_summaries': [],
        'exact_confirmation_summaries': [],
        'refused_action_summaries': [],
    }
    for row in rows:
        target = SUMMARY_CATEGORIES.get(_text(row.get('category')))
        if target is None:
            continue
        summaries[target].append(
            {
                'summary_id': f'summary-{_text(row.get('reviewer_row_id'))}',
                'reviewer_row_id': _text(row.get('reviewer_row_id')),
                'predicate': _text(row.get('reviewer_ready_predicate')),
                'boundary': _text(row.get('action_boundary_summary')),
                'citation_refs': [
                    citation
                    for ref in _mapping_sequence(row.get('cited_process_impact_refs'))
                    for citation in _text_sequence(ref.get('citation_refs'))
                ],
            }
        )
    return summaries


def _unresolved_reviewer_holds(candidate: Mapping[str, Any], rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    holds = [dict(item) for item in _mapping_sequence(candidate.get('reviewer_holds'))]
    holds.append(
        {
            'hold_id': 'hold-reviewer-predicate-row-disposition-v4',
            'reason': 'Reviewer predicate rows remain unresolved until human disposition is recorded in a later promotion task.',
            'release_state': 'held',
            'reviewer_row_ids': [_text(row.get('reviewer_row_id')) for row in rows],
        }
    )
    return holds


def _action_boundary_summary(category: str) -> str:
    mapping = {
        'reversible_action_predicates': 'Reviewer may inspect local draft/read-only predicates only.',
        'exact_confirmation_predicates': 'Reviewer must preserve action-specific exact confirmation before consequential attended handling.',
        'refused_consequential_action_predicates': 'Reviewer must preserve refusal of official action execution.',
        'stale_evidence_block_predicates': 'Reviewer must preserve stop gates for stale or conflicting evidence.',
        'explanation_templates': 'Reviewer must preserve cited fixture provenance and inactive status language.',
        'validation_status': 'Reviewer must preserve offline-only validation status.',
        'reviewer_holds': 'Reviewer hold remains unresolved for this packet.',
        'rollback_notes': 'Rollback is discard-only for this inactive review packet.',
        'offline_validation_commands': 'Reviewer packet exposes only the exact offline command bundle.',
    }
    return mapping.get(category, 'Reviewer disposition required before activation.')


def _validate_no_forbidden_state(value: Any, problems: list[str], path: str = 'packet') -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace('-', '_').replace(' ', '_')
            child_path = f'{path}.{key_text}'
            if normalized in MUTATION_FLAGS and child is not False:
                problems.append(f'{child_path} must be false or absent')
            if any(fragment in normalized for fragment in PRIVATE_KEY_FRAGMENTS):
                problems.append(f'{child_path} must not include private/session/auth artifact keys')
            _validate_no_forbidden_state(child, problems, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _validate_no_forbidden_state(child, problems, f'{path}[{index}]')
    elif isinstance(value, str):
        lowered = value.lower()
        for fragment in FORBIDDEN_STRING_FRAGMENTS:
            if fragment in lowered:
                problems.append(f'{path} must not contain forbidden live, official-action, or guarantee claim: {fragment}')


def _load_json_object(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(loaded, dict):
        raise ValueError(f'{path} must contain a JSON object')
    return loaded


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _text_sequence(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in (_text(item) for item in value) if item]


def _text(value: Any, default: str = '') -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default
