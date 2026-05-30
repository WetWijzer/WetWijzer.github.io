from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PACKET_TYPE = 'ppd.combined_promotion_rehearsal.v3'
PACKET_VERSION = 3

REQUIRED_ATTESTATIONS = {
    'fixture_first': True,
    'no_live': True,
    'no_auth': True,
    'no_official_action': True,
    'no_active_source_mutation': True,
    'no_active_surface_registry_mutation': True,
    'no_active_registry_mutation': True,
    'no_active_guardrail_mutation': True,
    'no_active_prompt_mutation': True,
    'no_active_monitoring_mutation': True,
    'no_active_release_state_mutation': True,
    'no_active_agent_state_mutation': True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ['python3', '-m', 'py_compile', 'ppd/agent_readiness/combined_promotion_rehearsal_v3.py'],
    ['python3', '-m', 'unittest', 'ppd.tests.test_combined_promotion_rehearsal_v3'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

_PRIVATE_OR_AUTH_KEYS = {
    'access_token', 'auth_state', 'authorization', 'bank_account', 'browser_context', 'card_number',
    'cookie', 'credentials', 'cvv', 'email', 'mfa_code', 'password', 'payment_details', 'phone',
    'private_fact', 'private_value', 'raw_value', 'refresh_token', 'secret', 'session_cookie',
    'session_state', 'ssn', 'token', 'user_input',
}
_RAW_ARTIFACT_KEYS = {
    'browser_artifact', 'crawl_body', 'downloaded_document', 'har', 'har_path', 'pdf_binary',
    'playwright_trace', 'raw_crawl_output', 'raw_download', 'raw_html', 'raw_pdf', 'screenshot',
    'screenshots', 'session_artifact', 'trace', 'trace_path',
}
_LIVE_OR_PROMOTION_KEYS = {
    'browser_execution_complete', 'crawler_execution_complete', 'devhub_execution_complete',
    'execute_live', 'executed_live', 'live_execution', 'live_promotion', 'processor_execution_complete',
    'promoted', 'promotion_complete', 'run_live',
}
_MUTATION_FLAG_KEYS = {
    'active_agent_mutation', 'active_agent_state_mutation', 'active_guardrail_mutation',
    'active_monitoring_mutation', 'active_prompt_mutation', 'active_registry_mutation',
    'active_release_mutation', 'active_release_state_mutation', 'active_source_mutation',
    'active_source_registry_mutation', 'active_surface_mutation', 'active_surface_registry_mutation',
    'agent_state_mutation_enabled', 'apply_to_active_agent_state', 'apply_to_active_guardrails',
    'apply_to_active_monitoring', 'apply_to_active_prompts', 'apply_to_active_registry',
    'apply_to_active_release_state', 'apply_to_active_source_registry', 'apply_to_active_sources',
    'apply_to_active_surface_registry', 'guardrail_mutation_enabled', 'monitoring_mutation_enabled',
    'prompt_mutation_enabled', 'registry_mutation_enabled', 'release_state_mutation_enabled',
    'source_mutation_enabled', 'source_registry_mutation_enabled', 'surface_registry_mutation_enabled',
}
_OUTCOME_GUARANTEE_PHRASES = (
    'approval guaranteed', 'guarantee approval', 'guaranteed permit', 'legal advice',
    'permit will be approved', 'permitting outcome guaranteed', 'will pass inspection',
)
_LIVE_OR_PROMOTION_PHRASES = (
    'applied to production', 'browser automation completed', 'crawler completed', 'devhub run completed',
    'executed against devhub', 'executed live', 'live execution complete', 'live promotion complete',
    'processor completed', 'promoted to active', 'promoted to production',
)
_CONSEQUENTIAL_ACTION_PHRASES = (
    'cancel inspection', 'certify acknowledgement', 'make payment', 'pay fee', 'purchase permit',
    'schedule inspection', 'submit application', 'submit permit', 'upload correction',
    'upload to official record',
)


def load_fixture_packet(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('combined promotion rehearsal v3 fixture must be a JSON object')
    return build_combined_promotion_rehearsal_v3(data)


def build_combined_promotion_rehearsal_v3(input_data: Mapping[str, Any]) -> dict[str, Any]:
    _reject_forbidden_content(input_data)
    source_preview = _mapping(_first_present(input_data, 'public_source_registry_promotion_preview_v3', 'source_registry_promotion_preview_v3', 'source_preview'))
    devhub_preview = _mapping(_first_present(input_data, 'devhub_surface_map_promotion_preview_v3', 'devhub_surface_preview', 'devhub_preview'))
    guardrail_preview = _mapping(_first_present(input_data, 'guardrail_bundle_promotion_preview_v3', 'guardrail_preview'))
    if not source_preview or not devhub_preview or not guardrail_preview:
        raise ValueError('public source registry, DevHub surface-map, and guardrail bundle promotion previews v3 are required')
    source_items = _source_items(source_preview)
    devhub_items = _devhub_items(devhub_preview)
    guardrail_items = _guardrail_items(guardrail_preview)
    if not source_items or not devhub_items or not guardrail_items:
        raise ValueError('each promotion preview must expose at least one patch candidate')
    attestations = dict(REQUIRED_ATTESTATIONS)
    attestations.update(_mapping(input_data.get('attestations')))
    packet = {
        'packet_type': PACKET_TYPE,
        'packet_version': PACKET_VERSION,
        'mode': 'fixture_first_combined_promotion_rehearsal_only',
        'packet_id': str(input_data.get('packet_id', 'combined-promotion-rehearsal-v3')),
        'consumes': {
            'public_source_registry_promotion_preview_v3': str(input_data.get('source_preview_ref', 'public_source_registry_promotion_preview_v3')),
            'devhub_surface_map_promotion_preview_v3': str(input_data.get('devhub_preview_ref', 'devhub_surface_map_promotion_preview_v3')),
            'guardrail_bundle_promotion_preview_v3': str(input_data.get('guardrail_preview_ref', 'guardrail_bundle_promotion_preview_v3')),
        },
        'reviewer_owner_fields': {
            'source_registry_owner': str(input_data.get('source_registry_owner', 'public-source-reviewer')),
            'devhub_surface_map_owner': str(input_data.get('devhub_surface_map_owner', 'devhub-surface-reviewer')),
            'guardrail_bundle_owner': str(input_data.get('guardrail_bundle_owner', 'guardrail-reviewer')),
            'rollback_owner': str(input_data.get('rollback_owner', 'rollback-reviewer')),
        },
        'dependency_ordered_rehearsal_steps': _rehearsal_steps(source_items, devhub_items, guardrail_items),
        'cross_artifact_consistency_checks': _consistency_checks(source_items, devhub_items, guardrail_items),
        'expected_fixture_diffs': _expected_fixture_diffs(source_items, devhub_items, guardrail_items),
        'rollback_verification': _rollback_verification(source_items, devhub_items, guardrail_items),
        'offline_validation_commands': list(OFFLINE_VALIDATION_COMMANDS),
        'attestations': attestations,
        'validation_status': 'ready_for_offline_review',
    }
    require_combined_promotion_rehearsal_v3(packet)
    return packet


def validate_combined_promotion_rehearsal_v3(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get('packet_type') != PACKET_TYPE:
        errors.append(f'packet_type must be {PACKET_TYPE}')
    if packet.get('packet_version') != PACKET_VERSION:
        errors.append('packet_version must be 3')
    if packet.get('mode') != 'fixture_first_combined_promotion_rehearsal_only':
        errors.append('mode must be fixture_first_combined_promotion_rehearsal_only')
    _reject_forbidden_content(packet, errors=errors)
    consumes = _mapping(packet.get('consumes'))
    for key in ('public_source_registry_promotion_preview_v3', 'devhub_surface_map_promotion_preview_v3', 'guardrail_bundle_promotion_preview_v3'):
        if not _text(consumes.get(key)):
            errors.append(f'consumes.{key} must be present')
    owners = _mapping(packet.get('reviewer_owner_fields'))
    for key in ('source_registry_owner', 'devhub_surface_map_owner', 'guardrail_bundle_owner', 'rollback_owner'):
        if not _text(owners.get(key)):
            errors.append(f'reviewer_owner_fields.{key} must be present')
    steps = _dicts(packet.get('dependency_ordered_rehearsal_steps'))
    if not steps:
        errors.append('dependency_ordered_rehearsal_steps must be non-empty')
    seen_steps: set[str] = set()
    for index, step in enumerate(steps):
        step_id = _text(step.get('step_id'))
        if not step_id:
            errors.append(f'dependency_ordered_rehearsal_steps[{index}].step_id must be present')
            continue
        if not _list(step.get('citations')):
            errors.append(f'dependency_ordered_rehearsal_steps[{index}].citations must be non-empty')
        if not _text(step.get('reviewer_owner')):
            errors.append(f'dependency_ordered_rehearsal_steps[{index}].reviewer_owner must be present')
        if step.get('offline_only') is not True:
            errors.append(f'dependency_ordered_rehearsal_steps[{index}].offline_only must be true')
        for dependency in _strings(step.get('depends_on')):
            if dependency not in seen_steps:
                errors.append(f'dependency_ordered_rehearsal_steps[{index}] dependency is missing or out of order: {dependency}')
        seen_steps.add(step_id)
    checks = _dicts(packet.get('cross_artifact_consistency_checks'))
    if not checks:
        errors.append('cross_artifact_consistency_checks must be non-empty')
    for index, check in enumerate(checks):
        if not _text(check.get('check_id')):
            errors.append(f'cross_artifact_consistency_checks[{index}].check_id must be present')
        if check.get('status') != 'pass':
            errors.append(f'cross_artifact_consistency_checks[{index}].status must be pass')
        if not _text(check.get('reviewer_owner')):
            errors.append(f'cross_artifact_consistency_checks[{index}].reviewer_owner must be present')
        if not _list(check.get('citations')):
            errors.append(f'cross_artifact_consistency_checks[{index}].citations must be non-empty')
    diffs = _dicts(packet.get('expected_fixture_diffs'))
    if not diffs:
        errors.append('expected_fixture_diffs must be non-empty')
    diff_ids: set[str] = set()
    for index, diff in enumerate(diffs):
        artifact_id = _text(diff.get('artifact_id'))
        if not artifact_id:
            errors.append(f'expected_fixture_diffs[{index}].artifact_id must be present')
        else:
            diff_ids.add(artifact_id)
        if not _text(diff.get('fixture_path')).startswith('ppd/tests/fixtures/'):
            errors.append(f'expected_fixture_diffs[{index}].fixture_path must stay under ppd/tests/fixtures')
        for key in ('expected_change', 'before_hash', 'after_hash', 'reviewer_owner'):
            if not _text(diff.get(key)):
                errors.append(f'expected_fixture_diffs[{index}].{key} must be present')
        if not _list(diff.get('citations')):
            errors.append(f'expected_fixture_diffs[{index}].citations must be non-empty')
    rollbacks = _dicts(packet.get('rollback_verification'))
    if not rollbacks:
        errors.append('rollback_verification must be non-empty')
    for index, rollback in enumerate(rollbacks):
        artifact_id = _text(rollback.get('artifact_id'))
        if not artifact_id:
            errors.append(f'rollback_verification[{index}].artifact_id must be present')
        elif diff_ids and artifact_id not in diff_ids:
            errors.append(f'rollback_verification[{index}].artifact_id must match an expected fixture diff')
        if not _text(rollback.get('reviewer_owner')):
            errors.append(f'rollback_verification[{index}].reviewer_owner must be present')
        if not _list(rollback.get('citations')):
            errors.append(f'rollback_verification[{index}].citations must be non-empty')
        if rollback.get('requires_manual_confirmation') is not True:
            errors.append(f'rollback_verification[{index}].requires_manual_confirmation must be true')
        if not _list(rollback.get('rollback_commands')):
            errors.append(f'rollback_verification[{index}].rollback_commands must be non-empty')
    commands = packet.get('offline_validation_commands')
    if not isinstance(commands, list) or not commands:
        errors.append('offline_validation_commands must be non-empty')
    else:
        for index, command in enumerate(commands):
            if not _strings(command):
                errors.append(f'offline_validation_commands[{index}] must be a command list')
    attestations = _mapping(packet.get('attestations'))
    for key, expected in REQUIRED_ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            errors.append(f'attestations.{key} must be true')
    return sorted(dict.fromkeys(errors))


def require_combined_promotion_rehearsal_v3(packet: Mapping[str, Any]) -> None:
    errors = validate_combined_promotion_rehearsal_v3(packet)
    if errors:
        raise ValueError('invalid combined promotion rehearsal v3: ' + '; '.join(errors))


def is_combined_promotion_rehearsal_v3_valid(packet: Mapping[str, Any]) -> bool:
    return not validate_combined_promotion_rehearsal_v3(packet)


validate_combined_promotion_rehearsal_packet_v3 = validate_combined_promotion_rehearsal_v3
require_combined_promotion_rehearsal_packet_v3 = require_combined_promotion_rehearsal_v3


def _source_items(preview: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = []
    for index, candidate in enumerate(_dicts(preview.get('patch_candidates'))):
        artifact_id = _text(candidate.get('patch_id') or candidate.get('id') or candidate.get('candidate_id')) or f'source-patch-{index + 1}'
        citations = _list(candidate.get('citations') or candidate.get('source_evidence_ids'))
        if not citations:
            raise ValueError(f'source registry promotion preview candidate lacks citations: {artifact_id}')
        if not _mapping(candidate.get('before_metadata')) or not _mapping(candidate.get('after_metadata')):
            raise ValueError(f'source registry promotion preview candidate lacks before/after metadata: {artifact_id}')
        if not _strings(candidate.get('affected_source_ids')) or not _strings(candidate.get('affected_requirement_ids')):
            raise ValueError(f'source registry promotion preview candidate lacks affected source or requirement ids: {artifact_id}')
        items.append(_item(candidate, artifact_id, 'public_source_registry_preview', citations, 'public-source-reviewer', 'ppd/tests/fixtures/source_registry_promotion_preview_v3/public_source_freshness_watch_plan_v3.json', affected_requirement_ids=_strings(candidate.get('affected_requirement_ids'))))
    return items


def _devhub_items(preview: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = []
    for index, candidate in enumerate(_dicts(preview.get('surface_action_patch_candidates'))):
        artifact_id = _text(candidate.get('candidate_id') or candidate.get('patch_id') or candidate.get('id')) or f'devhub-surface-patch-{index + 1}'
        citations = _list(candidate.get('citations'))
        if not citations:
            raise ValueError(f'DevHub surface-map promotion preview candidate lacks citations: {artifact_id}')
        if any(not _dicts(candidate.get(key)) for key in ('before_surface_rows', 'after_surface_rows', 'before_action_rows', 'after_action_rows', 'selector_confidence_deltas')):
            raise ValueError(f'DevHub surface-map promotion preview candidate lacks before/after rows or selector deltas: {artifact_id}')
        if not _mapping(candidate.get('manual_handoff_disposition')) or not _mapping(candidate.get('redaction_disposition')):
            raise ValueError(f'DevHub surface-map promotion preview candidate lacks manual handoff or redaction disposition: {artifact_id}')
        items.append(_item(candidate, artifact_id, 'devhub_surface_map_preview', citations, 'devhub-surface-reviewer', 'ppd/tests/fixtures/devhub/surface_map_promotion_preview_v3.json'))
    return items


def _guardrail_items(preview: Mapping[str, Any]) -> list[dict[str, Any]]:
    items = []
    for index, candidate in enumerate(_dicts(preview.get('guardrail_fixture_patch_candidates'))):
        artifact_id = _text(candidate.get('candidate_id') or candidate.get('patch_id') or candidate.get('id')) or f'guardrail-patch-{index + 1}'
        citations = _list(candidate.get('citations'))
        if not citations:
            raise ValueError(f'guardrail bundle promotion preview candidate lacks citations: {artifact_id}')
        if not _dicts(candidate.get('before_after_predicate_rows')) or not _dicts(candidate.get('explanation_template_deltas')):
            raise ValueError(f'guardrail bundle promotion preview candidate lacks predicate rows or explanation deltas: {artifact_id}')
        items.append(_item(candidate, artifact_id, 'guardrail_bundle_preview', citations, 'guardrail-reviewer', 'ppd/tests/fixtures/guardrail_bundle_promotion_preview_v3/input_manifest.json', dependency_refs=_strings(candidate.get('dependency_refs'))))
    return items


def _item(candidate: Mapping[str, Any], artifact_id: str, artifact_type: str, citations: list[Any], default_owner: str, default_fixture: str, **extra: Any) -> dict[str, Any]:
    item = {
        'artifact_id': artifact_id,
        'artifact_type': artifact_type,
        'fixture_path': _text(candidate.get('fixture_path'), default_fixture),
        'citations': citations,
        'reviewer_owner': _text(candidate.get('reviewer_owner'), default_owner),
        'before_hash': _text(candidate.get('before_hash'), f'{artifact_type}-before'),
        'after_hash': _text(candidate.get('after_hash'), f'{artifact_type}-after'),
    }
    item.update(extra)
    return item


def _rehearsal_steps(source_items: Sequence[Mapping[str, Any]], devhub_items: Sequence[Mapping[str, Any]], guardrail_items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    source_step_ids = [f"step-source-{item['artifact_id']}" for item in source_items]
    devhub_step_ids = [f"step-devhub-{item['artifact_id']}" for item in devhub_items]
    for item in source_items:
        steps.append(_step(f"step-source-{item['artifact_id']}", item, []))
    for item in devhub_items:
        steps.append(_step(f"step-devhub-{item['artifact_id']}", item, source_step_ids))
    for item in guardrail_items:
        steps.append(_step(f"step-guardrail-{item['artifact_id']}", item, source_step_ids + devhub_step_ids))
    return steps


def _step(step_id: str, item: Mapping[str, Any], depends_on: Sequence[str]) -> dict[str, Any]:
    return {
        'step_id': step_id,
        'artifact_id': item['artifact_id'],
        'artifact_type': item['artifact_type'],
        'depends_on': list(depends_on),
        'citations': list(_list(item.get('citations'))),
        'reviewer_owner': item['reviewer_owner'],
        'offline_only': True,
        'instruction': 'Review committed fixture preview evidence and record reviewer disposition before any later offline rehearsal step.',
    }


def _combined_citations(*groups: Sequence[Mapping[str, Any]]) -> list[Any]:
    citations: list[Any] = []
    for group in groups:
        for item in group:
            citations.extend(_list(item.get('citations')))
    return citations


def _consistency_checks(source_items: Sequence[Mapping[str, Any]], devhub_items: Sequence[Mapping[str, Any]], guardrail_items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    source_requirement_ids = sorted({requirement_id for item in source_items for requirement_id in _strings(item.get('affected_requirement_ids'))})
    return [
        {'check_id': 'combined-preview-presence', 'status': 'pass' if source_items and devhub_items and guardrail_items else 'fail', 'reviewer_owner': 'release-reviewer', 'description': 'Source registry, DevHub surface-map, and guardrail bundle previews are all present.', 'citations': _combined_citations(source_items, devhub_items, guardrail_items)},
        {'check_id': 'source-requirement-coverage', 'status': 'pass' if source_requirement_ids else 'fail', 'reviewer_owner': 'public-source-reviewer', 'description': 'Public source registry preview declares affected requirement ids for downstream review.', 'affected_requirement_ids': source_requirement_ids, 'citations': _combined_citations(source_items)},
        {'check_id': 'devhub-after-source-ordering', 'status': 'pass', 'reviewer_owner': 'devhub-surface-reviewer', 'description': 'DevHub surface-map preview steps depend on public source registry preview steps.', 'citations': _combined_citations(source_items, devhub_items)},
        {'check_id': 'guardrail-after-source-and-devhub-ordering', 'status': 'pass', 'reviewer_owner': 'guardrail-reviewer', 'description': 'Guardrail bundle preview steps depend on source registry and DevHub surface-map preview steps.', 'citations': _combined_citations(source_items, devhub_items, guardrail_items)},
    ]


def _expected_fixture_diffs(source_items: Sequence[Mapping[str, Any]], devhub_items: Sequence[Mapping[str, Any]], guardrail_items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    diffs = []
    for item in list(source_items) + list(devhub_items) + list(guardrail_items):
        fixture_path = _text(item.get('fixture_path'))
        if not fixture_path.startswith('ppd/tests/fixtures/'):
            raise ValueError(f"expected fixture diff must stay under ppd/tests/fixtures: {item['artifact_id']}")
        diffs.append({'artifact_id': item['artifact_id'], 'artifact_type': item['artifact_type'], 'fixture_path': fixture_path, 'expected_change': 'fixture_preview_replacement_only', 'before_hash': item['before_hash'], 'after_hash': item['after_hash'], 'reviewer_owner': item['reviewer_owner'], 'citations': list(_list(item.get('citations')))})
    return diffs


def _rollback_verification(source_items: Sequence[Mapping[str, Any]], devhub_items: Sequence[Mapping[str, Any]], guardrail_items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in list(source_items) + list(devhub_items) + list(guardrail_items):
        rows.append({'artifact_id': item['artifact_id'], 'reviewer_owner': item['reviewer_owner'], 'rollback_commands': [['git', 'diff', '--', item['fixture_path']]], 'expected_result': 'Only fixture preview diffs are present; no live, authenticated, official, registry, or guardrail mutation artifacts are created.', 'requires_manual_confirmation': True, 'citations': list(_list(item.get('citations')))})
    return rows


def _reject_forbidden_content(value: Any, path: str = '$', errors: list[str] | None = None) -> None:
    local_errors: list[str] = [] if errors is None else errors
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace('-', '_')
            child_path = f'{path}.{key}'
            if normalized in _PRIVATE_OR_AUTH_KEYS and _present(child):
                local_errors.append(f'{child_path}: private or authenticated facts are rejected')
            if normalized in _RAW_ARTIFACT_KEYS and _present(child):
                local_errors.append(f'{child_path}: raw crawl/PDF/session/browser artifacts are rejected')
            if normalized in _LIVE_OR_PROMOTION_KEYS and _present(child):
                local_errors.append(f'{child_path}: live execution or promotion claims are rejected')
            if normalized in _MUTATION_FLAG_KEYS and _present(child):
                local_errors.append(f'{child_path}: active registry or guardrail mutation flags are rejected')
            _reject_forbidden_content(child, child_path, local_errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_content(child, f'{path}[{index}]', local_errors)
    elif isinstance(value, str):
        lowered = ' '.join(value.lower().split())
        if any(phrase in lowered for phrase in _OUTCOME_GUARANTEE_PHRASES):
            local_errors.append(f'{path}: legal or permitting outcome guarantees are rejected')
        if any(phrase in lowered for phrase in _LIVE_OR_PROMOTION_PHRASES):
            local_errors.append(f'{path}: live execution or promotion claims are rejected')
        if any(phrase in lowered for phrase in _CONSEQUENTIAL_ACTION_PHRASES):
            local_errors.append(f'{path}: consequential action language is rejected')
    if errors is None and local_errors:
        raise ValueError('; '.join(sorted(dict.fromkeys(local_errors))))


def _first_present(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _dicts(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _strings(value: Any) -> list[str]:
    return [str(item) for item in _list(value) if str(item)]


def _text(value: Any, default: str = '') -> str:
    if isinstance(value, str) and value:
        return value
    return default


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description='Build a fixture-first combined promotion rehearsal v3 packet.')
    parser.add_argument('fixture', type=Path)
    args = parser.parse_args()
    print(json.dumps(load_fixture_packet(args.fixture), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
