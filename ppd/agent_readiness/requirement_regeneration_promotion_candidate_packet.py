from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_TYPE = 'ppd.requirement_regeneration_promotion_candidate_packet.v1'

_FALSE_POLICY_KEYS = {
    'uses_live_extraction',
    'invokes_live_crawlers',
    'invokes_processors',
    'invokes_devhub',
    'mutates_active_artifacts',
    'writes_active_state',
    'reads_private_case_files',
    'persists_raw_crawl_output',
    'mutates_active_requirements',
    'mutates_active_processes',
    'mutates_active_process_models',
    'mutates_active_guardrails',
    'mutates_active_guardrail_bundles',
    'mutates_active_prompts',
    'mutates_release_state',
    'mutates_active_release_state',
    'writes_requirement_state',
    'writes_process_state',
    'writes_guardrail_state',
    'writes_prompt_state',
    'writes_release_state',
    'promotes_to_active',
    'publishes_release_state',
}

_REQUIRED_ATTESTATIONS = {
    'no-live-extraction',
    'no-processor-invocation',
    'no-active-artifact-mutation',
    'no-outcome-guarantees',
}

_PRIVATE_KEY_MARKERS = (
    'auth_state',
    'browser_state',
    'case_fact_value',
    'credential',
    'cookie',
    'password',
    'payment_detail',
    'private_case',
    'private_fact',
    'private_file',
    'private_path',
    'private_value',
    'secret',
    'session_state',
    'storage_state',
    'token',
)

_PRIVATE_VALUE_MARKERS = (
    'bearer ',
    'applicant private',
    'private parcel fact',
    'private case fact',
    '-----begin ',
    'sk-',
)

_RAW_KEY_MARKERS = (
    'archive_ref',
    'archive_path',
    'archive_url',
    'download_ref',
    'download_path',
    'download_url',
    'downloaded_document',
    'raw_archive',
    'raw_body',
    'raw_crawl',
    'raw_download',
    'raw_html',
    'raw_pdf',
    'warc',
    'har',
    'screenshot',
    'trace_zip',
)

_RAW_VALUE_MARKERS = (
    'file://',
    '/tmp/',
    '/var/folders/',
    '/private/',
    '/home/',
    '/users/',
    '/raw/',
    '/download/',
    '/downloads/',
    '/archive/',
    '/archives/',
    '.warc',
    'raw_body',
    'raw body',
    'archive.warc',
    'trace.zip',
)

_LIVE_CLAIM_MARKERS = (
    'live extraction',
    'live crawler',
    'live crawl',
    'live processor',
    'processor executed',
    'processor ran',
    'devhub executed',
    'submitted to devhub',
    'uploaded to devhub',
    'paid fees',
    'scheduled inspection',
    'certified application',
)

_OUTCOME_GUARANTEE_MARKERS = (
    'guaranteed approval',
    'approval guaranteed',
    'will be approved',
    'permit will be issued',
    'permit will be approved',
    'legally sufficient',
    'compliance guaranteed',
    'outcome guaranteed',
    'guarantees approval',
    'guarantee approval',
    'automatic approval',
)

_MUTATION_SCOPE_MARKERS = (
    'active_artifact',
    'active_requirement',
    'active_process',
    'active_guardrail',
    'active_prompt',
    'release_state',
)

_MUTATION_ACTION_MARKERS = (
    'mutate',
    'mutation',
    'write',
    'promote',
    'promotion',
    'publish',
    'replace',
)


@dataclass(frozen=True)
class RequirementRegenerationPromotionCandidateValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {'valid': self.valid, 'problems': list(self.problems)}


def build_requirement_regeneration_promotion_candidate_packet(
    requirement_regeneration_rehearsal_tranche_packet: Mapping[str, Any],
    requirement_rerun_disposition_packet: Mapping[str, Any],
    process_model_impact_review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    rehearsal_id = _packet_id(requirement_regeneration_rehearsal_tranche_packet, 'requirement-regeneration-rehearsal-tranche')
    rerun_id = _packet_id(requirement_rerun_disposition_packet, 'requirement-rerun-disposition')
    impact_id = _packet_id(process_model_impact_review_packet, 'process-model-impact-review')
    evidence_ids = _packet_evidence_ids(
        requirement_regeneration_rehearsal_tranche_packet,
        requirement_rerun_disposition_packet,
        process_model_impact_review_packet,
    )

    packet = {
        'packet_type': PACKET_TYPE,
        'packet_id': 'fixture-first-requirement-regeneration-promotion-candidate-packet',
        'fixture_only': True,
        'candidate_status': 'candidate_deltas_not_promoted',
        'source_packet_ids': {
            'requirement_regeneration_rehearsal_tranche_packet': rehearsal_id,
            'requirement_rerun_disposition_packet': rerun_id,
            'process_model_impact_review_packet': impact_id,
        },
        'promotion_policy': _promotion_policy(),
        'candidate_requirement_deltas': _requirement_deltas(requirement_regeneration_rehearsal_tranche_packet, requirement_rerun_disposition_packet, evidence_ids),
        'candidate_process_deltas': _process_deltas(process_model_impact_review_packet, evidence_ids),
        'candidate_guardrail_deltas': _guardrail_deltas(process_model_impact_review_packet, requirement_rerun_disposition_packet, evidence_ids),
        'rollback_notes': _rollback_notes(requirement_rerun_disposition_packet, process_model_impact_review_packet, evidence_ids),
        'reviewer_owner_fields': _reviewer_owner_fields(evidence_ids),
        'expected_offline_validation_commands': [
            ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
            ['python3', '-m', 'unittest', 'ppd.tests.test_requirement_regeneration_promotion_candidate_packet'],
        ],
        'attestations': _attestations(evidence_ids),
    }
    assert_valid_requirement_regeneration_promotion_candidate_packet(packet)
    return packet


def validate_requirement_regeneration_promotion_candidate_packet(packet: Mapping[str, Any]) -> RequirementRegenerationPromotionCandidateValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return RequirementRegenerationPromotionCandidateValidationResult(False, ('packet must be an object',))

    if packet.get('packet_type') != PACKET_TYPE:
        problems.append('packet_type must be ppd.requirement_regeneration_promotion_candidate_packet.v1')
    if packet.get('fixture_only') is not True:
        problems.append('fixture_only must be true')
    if packet.get('candidate_status') != 'candidate_deltas_not_promoted':
        problems.append('candidate_status must keep deltas unpromoted')

    source_packet_ids = packet.get('source_packet_ids') if isinstance(packet.get('source_packet_ids'), Mapping) else {}
    for key in ('requirement_regeneration_rehearsal_tranche_packet', 'requirement_rerun_disposition_packet', 'process_model_impact_review_packet'):
        if not source_packet_ids.get(key):
            problems.append(f'source_packet_ids.{key} is required')

    policy = packet.get('promotion_policy') if isinstance(packet.get('promotion_policy'), Mapping) else {}
    if policy.get('fixtures_only') is not True:
        problems.append('promotion_policy.fixtures_only must be true')
    for key in sorted(_FALSE_POLICY_KEYS):
        if policy.get(key) is not False:
            problems.append(f'promotion_policy.{key} must remain offline and false')

    _validate_delta_section(problems, packet, 'candidate_requirement_deltas', ('requirement_id', 'affected_requirement_ids'), 'requirement')
    _validate_delta_section(problems, packet, 'candidate_process_deltas', ('process_id', 'affected_process_ids'), 'process')
    _validate_delta_section(problems, packet, 'candidate_guardrail_deltas', ('guardrail_id', 'guardrail_bundle_id', 'affected_guardrail_ids'), 'guardrail')

    rollback_notes = packet.get('rollback_notes')
    if not isinstance(rollback_notes, list) or not rollback_notes:
        problems.append('rollback_notes must be a non-empty list')
    for index, note in enumerate(_mapping_sequence(rollback_notes)):
        if not note.get('rollback_note_id'):
            problems.append(f'rollback_notes[{index}] lacks rollback_note_id')
        if not _string_list(note.get('source_evidence_ids')):
            problems.append(f'rollback_notes[{index}] lacks source_evidence_ids')

    owners = packet.get('reviewer_owner_fields')
    if not isinstance(owners, list) or not owners:
        problems.append('reviewer_owner_fields must be a non-empty list')
    for index, owner in enumerate(_mapping_sequence(owners)):
        if not owner.get('reviewer_owner_id'):
            problems.append(f'reviewer_owner_fields[{index}] lacks reviewer_owner_id')
        if not owner.get('role'):
            problems.append(f'reviewer_owner_fields[{index}] lacks role')
        if owner.get('approval_status') != 'pending_human_review':
            problems.append(f'reviewer_owner_fields[{index}] must be pending_human_review')
        if not _string_list(owner.get('source_evidence_ids')):
            problems.append(f'reviewer_owner_fields[{index}] lacks source_evidence_ids')

    commands = packet.get('expected_offline_validation_commands')
    if not isinstance(commands, list) or not commands:
        problems.append('expected_offline_validation_commands must be a non-empty list')
    for index, command in enumerate(commands if isinstance(commands, list) else []):
        if not _string_list(command):
            problems.append(f'expected_offline_validation_commands[{index}] must be a list of strings')
        elif _command_mentions_live_or_processor(command):
            problems.append(f'expected_offline_validation_commands[{index}] must remain offline and must not invoke processors, downloads, archives, DevHub, or live extraction')

    attestations = _mapping_sequence(packet.get('attestations'))
    attestation_ids = {str(item.get('attestation_id')) for item in attestations}
    for required in sorted(_REQUIRED_ATTESTATIONS):
        if required not in attestation_ids:
            problems.append(f'attestations must include {required}')
    for index, attestation in enumerate(attestations):
        if attestation.get('attested') is not True:
            problems.append(f'attestations[{index}] must be attested')
        if not _string_list(attestation.get('source_evidence_ids')):
            problems.append(f'attestations[{index}] lacks source_evidence_ids')

    problems.extend(_recursive_safety_problems(packet))
    return RequirementRegenerationPromotionCandidateValidationResult(valid=not problems, problems=tuple(_dedupe(problems)))


def assert_valid_requirement_regeneration_promotion_candidate_packet(packet: Mapping[str, Any]) -> None:
    result = validate_requirement_regeneration_promotion_candidate_packet(packet)
    if not result.valid:
        raise ValueError('invalid_requirement_regeneration_promotion_candidate_packet: ' + '; '.join(result.problems))


def _promotion_policy() -> dict[str, bool]:
    policy = {key: False for key in sorted(_FALSE_POLICY_KEYS)}
    policy['fixtures_only'] = True
    return policy


def _attestations(evidence_ids: list[str]) -> list[dict[str, Any]]:
    return [
        {
            'attestation_id': 'no-live-extraction',
            'attested': True,
            'summary': 'The candidate is derived from committed fixtures and does not perform live requirement extraction or public crawling.',
            'source_evidence_ids': evidence_ids,
        },
        {
            'attestation_id': 'no-processor-invocation',
            'attested': True,
            'summary': 'The candidate does not invoke archival, extraction, or processor-suite workers.',
            'source_evidence_ids': evidence_ids,
        },
        {
            'attestation_id': 'no-active-artifact-mutation',
            'attested': True,
            'summary': 'The candidate does not mutate active requirement, process, guardrail, prompt, release, or ledger artifacts.',
            'source_evidence_ids': evidence_ids,
        },
        {
            'attestation_id': 'no-outcome-guarantees',
            'attested': True,
            'summary': 'The candidate records review deltas only and does not guarantee legal, permitting, approval, issuance, or compliance outcomes.',
            'source_evidence_ids': evidence_ids,
        },
    ]


def _validate_delta_section(problems: list[str], packet: Mapping[str, Any], key: str, id_keys: tuple[str, ...], label: str) -> None:
    section = packet.get(key)
    if not isinstance(section, list) or not section:
        problems.append(f'{key} must be a non-empty list')
    for index, item in enumerate(_mapping_sequence(section)):
        if not item.get('delta_id'):
            problems.append(f'{key}[{index}] lacks delta_id')
        if item.get('status') != 'candidate_only':
            problems.append(f'{key}[{index}] must be candidate_only')
        if not _has_affected_id(item, id_keys):
            problems.append(f'{key}[{index}] lacks affected {label} id')
        if not _string_list(item.get('source_evidence_ids')):
            problems.append(f'{key}[{index}] lacks source_evidence_ids')
        if not _string_list(item.get('source_packet_refs')):
            problems.append(f'{key}[{index}] lacks source_packet_refs')


def _has_affected_id(item: Mapping[str, Any], keys: tuple[str, ...]) -> bool:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return True
        if _string_list(value):
            return True
    return False


def _requirement_deltas(rehearsal: Mapping[str, Any], rerun: Mapping[str, Any], evidence_ids: list[str]) -> list[dict[str, Any]]:
    source_items = _mapping_sequence(rehearsal.get('candidate_requirement_deltas')) or _mapping_sequence(rehearsal.get('requirement_delta_candidates'))
    disposition_by_id = {str(item.get('delta_id') or item.get('requirement_delta_id')): item for item in _mapping_sequence(rerun.get('rerun_dispositions'))}
    if not source_items:
        source_items = ({'delta_id': 'requirement-regeneration-delta', 'summary': 'Regenerated requirement candidates require promotion review.'},)
    deltas: list[dict[str, Any]] = []
    for index, item in enumerate(source_items, start=1):
        delta_id = str(item.get('delta_id') or item.get('requirement_delta_id') or f'requirement-delta-{index:03d}')
        requirement_id = str(item.get('requirement_id') or delta_id)
        disposition = disposition_by_id.get(delta_id, {})
        deltas.append(
            {
                'delta_id': delta_id,
                'status': 'candidate_only',
                'requirement_id': requirement_id,
                'affected_requirement_ids': [requirement_id],
                'delta_type': item.get('delta_type', 'requirement_update'),
                'summary': item.get('summary', 'Candidate requirement delta from regeneration rehearsal.'),
                'rerun_disposition': disposition.get('disposition', rerun.get('overall_disposition', 'requires_review')),
                'source_packet_refs': ['requirement_regeneration_rehearsal_tranche_packet', 'requirement_rerun_disposition_packet'],
                'source_evidence_ids': _item_evidence(item, disposition, evidence_ids),
            }
        )
    return deltas


def _process_deltas(impact: Mapping[str, Any], evidence_ids: list[str]) -> list[dict[str, Any]]:
    source_items = _mapping_sequence(impact.get('candidate_process_deltas')) or _mapping_sequence(impact.get('process_model_impacts'))
    if not source_items:
        source_items = ({'delta_id': 'process-model-impact-delta', 'summary': 'Process model review requires candidate update assessment.'},)
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(source_items, start=1):
        process_id = str(item.get('process_id') or 'ppd-process-model')
        rows.append(
            {
                'delta_id': str(item.get('delta_id') or item.get('impact_id') or f'process-delta-{index:03d}'),
                'status': 'candidate_only',
                'process_id': process_id,
                'affected_process_ids': [process_id],
                'delta_type': item.get('delta_type', 'process_model_update'),
                'summary': item.get('summary', 'Candidate process delta from impact review.'),
                'source_packet_refs': ['process_model_impact_review_packet'],
                'source_evidence_ids': _item_evidence(item, {}, evidence_ids),
            }
        )
    return rows


def _guardrail_deltas(impact: Mapping[str, Any], rerun: Mapping[str, Any], evidence_ids: list[str]) -> list[dict[str, Any]]:
    source_items = _mapping_sequence(impact.get('candidate_guardrail_deltas')) or _mapping_sequence(impact.get('guardrail_delta_candidates'))
    if not source_items:
        source_items = ({'delta_id': 'guardrail-regeneration-delta', 'summary': 'Guardrail bundle requires candidate review after requirement regeneration.'},)
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(source_items, start=1):
        guardrail_id = str(item.get('guardrail_id') or item.get('guardrail_bundle_id') or 'ppd-guardrail-bundle')
        rows.append(
            {
                'delta_id': str(item.get('delta_id') or item.get('guardrail_delta_id') or f'guardrail-delta-{index:03d}'),
                'status': 'candidate_only',
                'guardrail_bundle_id': guardrail_id,
                'affected_guardrail_ids': [guardrail_id],
                'delta_type': item.get('delta_type', 'guardrail_update'),
                'summary': item.get('summary', 'Candidate guardrail delta from impact review.'),
                'rerun_disposition': rerun.get('overall_disposition', 'requires_review'),
                'source_packet_refs': ['process_model_impact_review_packet', 'requirement_rerun_disposition_packet'],
                'source_evidence_ids': _item_evidence(item, rerun, evidence_ids),
            }
        )
    return rows


def _rollback_notes(rerun: Mapping[str, Any], impact: Mapping[str, Any], evidence_ids: list[str]) -> list[dict[str, Any]]:
    notes = _mapping_sequence(rerun.get('rollback_notes')) or _mapping_sequence(impact.get('rollback_notes'))
    if not notes:
        notes = ({'rollback_note_id': 'rollback-to-current-fixture-baseline', 'summary': 'Discard candidate deltas and retain the current committed fixture baseline if reviewer approval is withheld.'},)
    return [
        {
            'rollback_note_id': str(item.get('rollback_note_id') or item.get('note_id') or f'rollback-note-{index:03d}'),
            'summary': item.get('summary', 'Discard candidate deltas and keep the current fixture baseline.'),
            'source_packet_refs': ['requirement_rerun_disposition_packet', 'process_model_impact_review_packet'],
            'source_evidence_ids': _item_evidence(item, rerun, evidence_ids),
        }
        for index, item in enumerate(notes, start=1)
    ]


def _reviewer_owner_fields(evidence_ids: list[str]) -> list[dict[str, Any]]:
    return [
        {'reviewer_owner_id': 'requirement-owner', 'role': 'requirement_delta_reviewer', 'approval_status': 'pending_human_review', 'source_evidence_ids': evidence_ids},
        {'reviewer_owner_id': 'process-model-owner', 'role': 'process_model_reviewer', 'approval_status': 'pending_human_review', 'source_evidence_ids': evidence_ids},
        {'reviewer_owner_id': 'guardrail-owner', 'role': 'guardrail_reviewer', 'approval_status': 'pending_human_review', 'source_evidence_ids': evidence_ids},
    ]


def _packet_id(packet: Mapping[str, Any], fallback: str) -> str:
    return str(packet.get('packet_id') or packet.get('id') or fallback)


def _packet_evidence_ids(*packets: Mapping[str, Any]) -> list[str]:
    evidence: list[str] = []
    for packet in packets:
        for key in ('source_evidence_ids', 'evidence_ids'):
            value = packet.get(key)
            if isinstance(value, list):
                evidence.extend(str(item) for item in value if item)
        packet_id = packet.get('packet_id') or packet.get('id')
        if packet_id:
            evidence.append(str(packet_id))
    return _dedupe(evidence) or ['fixture-source-packet-evidence']


def _item_evidence(primary: Mapping[str, Any], secondary: Mapping[str, Any], fallback: list[str]) -> list[str]:
    evidence: list[str] = []
    for item in (primary, secondary):
        for key in ('source_evidence_ids', 'evidence_ids'):
            value = item.get(key)
            if isinstance(value, list):
                evidence.extend(str(entry) for entry in value if entry)
    return _dedupe(evidence) or list(fallback)


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def _command_mentions_live_or_processor(command: Sequence[str]) -> bool:
    joined = ' '.join(command).lower()
    forbidden = (' live_public_scrape', ' live_public_preflight', 'processor', 'devhub', 'crawl --live', '--live', 'playwright', 'download', 'archive')
    return any(marker in joined for marker in forbidden)


def _recursive_safety_problems(value: Any, path: str = 'packet') -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            normalized = _normalize(key_text)
            next_path = f'{path}.{key_text}'
            if key_text in _FALSE_POLICY_KEYS and nested is not False:
                problems.append(f'{next_path} must remain offline and false')
            if _active_mutation_key(normalized) and nested not in (False, None, '', [], {}):
                problems.append(f'{next_path} must not enable active requirement, process, guardrail, prompt, or release-state mutation')
            if _contains_any(normalized, _PRIVATE_KEY_MARKERS) and nested not in (False, None, '', [], {}):
                problems.append(f'{next_path} references private case facts, credentials, sessions, or runtime-only material')
            if _contains_any(normalized, _RAW_KEY_MARKERS) and nested not in (False, None, '', [], {}):
                problems.append(f'{next_path} references raw body, download, archive, trace, screenshot, HAR, or WARC material')
            problems.extend(_recursive_safety_problems(nested, next_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, nested in enumerate(value):
            problems.extend(_recursive_safety_problems(nested, f'{path}[{index}]'))
    elif isinstance(value, str):
        normalized_value = _normalize(value)
        lower_value = value.lower()
        if _contains_any(normalized_value, _PRIVATE_KEY_MARKERS) or _contains_any(lower_value, _PRIVATE_VALUE_MARKERS):
            problems.append(f'{path} references private case facts, credentials, sessions, or runtime-only material')
        if _contains_any(lower_value, _RAW_VALUE_MARKERS):
            problems.append(f'{path} references raw body, download, archive, trace, screenshot, HAR, or WARC material')
        if _contains_any(lower_value, _LIVE_CLAIM_MARKERS):
            problems.append(f'{path} claims live extraction, processor execution, DevHub execution, or consequential live action')
        if _contains_any(lower_value, _OUTCOME_GUARANTEE_MARKERS):
            problems.append(f'{path} claims a legal or permitting outcome guarantee')
    return problems


def _active_mutation_key(normalized_key: str) -> bool:
    return _contains_any(normalized_key, _MUTATION_SCOPE_MARKERS) and _contains_any(normalized_key, _MUTATION_ACTION_MARKERS)


def _contains_any(value: str, markers: Sequence[str]) -> bool:
    return any(marker in value for marker in markers)


def _normalize(value: str) -> str:
    return value.lower().replace('-', '_').replace(' ', '_')


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped
