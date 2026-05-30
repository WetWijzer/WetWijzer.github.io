from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ppd.agent_readiness.human_review_disposition_summary_v2 import (
    build_human_review_disposition_summary_v2_from_fixture,
    validate_human_review_disposition_summary_v2,
)
from ppd.refresh_implementation_proposal_v2 import (
    build_refresh_implementation_proposal_v2_from_files,
    validate_refresh_implementation_proposal_v2,
)

PLAN_TYPE = 'ppd.implementation_patch_staging_plan.v2'
PLAN_VERSION = 2

REQUIRED_ATTESTATIONS = {
    'no_live_crawl': True,
    'no_devhub': True,
    'no_processor': True,
    'no_registry_mutation': True,
    'no_guardrail_mutation': True,
    'no_prompt_mutation': True,
    'no_release_state_mutation': True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ['python3', '-m', 'py_compile', 'ppd/implementation_patch_staging_plan_v2.py'],
    ['python3', '-m', 'pytest', 'ppd/tests/test_implementation_patch_staging_plan_v2.py'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

DEPENDENCY_ORDER = [
    'validate-consumed-disposition-summary-v2',
    'validate-consumed-refresh-implementation-proposal-v2',
    'stage-source-patch-candidates',
    'stage-surface-patch-candidates',
    'stage-guardrail-patch-candidates',
    'fixture-migration-review',
    'rollback-checkpoint-review',
    'offline-validation-review',
]

_FORBIDDEN_KEYS = {
    'auth_state', 'browser_artifact', 'browser_state', 'cookies', 'crawl_artifact',
    'crawl_output', 'devhub_session', 'downloaded_document', 'har', 'password',
    'payment_details', 'pdf_artifact', 'private_fact', 'private_path', 'raw_body',
    'raw_crawl', 'raw_download', 'raw_html', 'raw_pdf', 'screenshot',
    'session_artifact', 'session_state', 'storage_state', 'token', 'trace',
}

_MUTATION_KEYS = {
    'active_guardrail', 'active_guardrail_mutation', 'active_prompt',
    'active_prompt_mutation', 'active_registry', 'active_registry_mutation',
    'active_release_state', 'active_release_state_mutation', 'active_source',
    'active_source_mutation', 'active_surface_registry',
    'active_surface_registry_mutation', 'guardrail_mutation_enabled',
    'prompt_mutation_enabled', 'registry_mutation_enabled',
    'release_state_mutation_enabled', 'source_mutation_enabled',
    'surface_registry_mutation_enabled',
}

_FORBIDDEN_TEXT = (
    'live crawl completed', 'live crawler completed', 'live devhub',
    'live browser', 'opened devhub', 'logged into devhub', 'ran processor',
    'processor completed', 'registry updated', 'guardrail updated',
    'prompt updated', 'release state updated', 'guaranteed approval',
    'permit will be approved', 'submit application', 'upload corrections',
    'schedule inspection', 'certify acknowledgement', 'purchase permit',
    'submit payment', 'raw crawl', 'raw pdf', 'raw html', 'browser artifact',
    'session artifact', 'downloaded document',
)


@dataclass(frozen=True)
class ImplementationPatchStagingPlanV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'expected JSON object at {path}')
    return data


def build_implementation_patch_staging_plan_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    fixture = load_json(fixture_path)
    base = fixture_path.parent
    disposition = build_human_review_disposition_summary_v2_from_fixture(base / _required_text(fixture, 'human_review_disposition_summary_fixture'))
    proposal = build_refresh_implementation_proposal_v2_from_files(
        base / _required_text(fixture, 'public_source_observation_refresh_candidate_v2_fixture'),
        base / _required_text(fixture, 'devhub_read_only_surface_observation_refresh_candidate_v2_fixture'),
        base / _required_text(fixture, 'post_dry_run_guardrail_impact_review_v2_fixture'),
    )
    return build_implementation_patch_staging_plan_v2(disposition, proposal)


def build_implementation_patch_staging_plan_v2(disposition_summary_v2: Mapping[str, Any], refresh_implementation_proposal_v2: Mapping[str, Any]) -> dict[str, Any]:
    disposition_result = validate_human_review_disposition_summary_v2(disposition_summary_v2)
    if not disposition_result.ok:
        raise ValueError('invalid human review disposition summary v2: ' + '; '.join(disposition_result.errors))
    proposal = dict(refresh_implementation_proposal_v2)
    proposal_result = validate_refresh_implementation_proposal_v2(proposal)
    if not proposal_result.ok:
        raise ValueError('invalid refresh implementation proposal v2: ' + '; '.join(proposal_result.errors))

    source_candidates = _candidates(proposal.get('proposed_source_patch_rows'), 'source', disposition_summary_v2)
    surface_candidates = _candidates(proposal.get('proposed_surface_patch_rows'), 'surface', disposition_summary_v2)
    guardrail_candidates = _candidates(proposal.get('proposed_guardrail_patch_rows'), 'guardrail', disposition_summary_v2)
    all_candidates = source_candidates + surface_candidates + guardrail_candidates
    plan = {
        'plan_type': PLAN_TYPE,
        'plan_version': PLAN_VERSION,
        'mode': 'fixture_first_offline_inactive_patch_staging_plan_v2',
        'consumes': {
            'human_review_disposition_summary_v2': _text(disposition_summary_v2.get('packet_type')),
            'refresh_implementation_proposal_v2': _text(proposal.get('proposal_version')),
        },
        'dependency_ordering': _dependency_rows(all_candidates),
        'inactive_source_patch_candidates': source_candidates,
        'inactive_surface_patch_candidates': surface_candidates,
        'inactive_guardrail_patch_candidates': guardrail_candidates,
        'reviewer_owner_fields': _owner_rows(all_candidates),
        'fixture_migration_notes': _fixture_migration_notes(disposition_summary_v2, proposal),
        'rollback_checkpoints': _rollback_checkpoints(all_candidates),
        'offline_validation_commands': list(OFFLINE_VALIDATION_COMMANDS),
        'attestations': dict(REQUIRED_ATTESTATIONS),
        'staging_status': 'inactive_fixture_first_patch_candidates_only',
    }
    require_implementation_patch_staging_plan_v2(plan)
    return plan


def validate_implementation_patch_staging_plan_v2(plan: Mapping[str, Any]) -> ImplementationPatchStagingPlanV2ValidationResult:
    errors: list[str] = []
    if plan.get('plan_type') != PLAN_TYPE:
        errors.append(f'plan_type must be {PLAN_TYPE}')
    if plan.get('plan_version') != PLAN_VERSION:
        errors.append('plan_version must be 2')
    if plan.get('mode') != 'fixture_first_offline_inactive_patch_staging_plan_v2':
        errors.append('mode must be fixture_first_offline_inactive_patch_staging_plan_v2')
    consumes = _mapping(plan.get('consumes'))
    if consumes.get('human_review_disposition_summary_v2') != 'ppd.human_review_disposition_summary.v2':
        errors.append('consumes.human_review_disposition_summary_v2 must reference human review disposition summary v2')
    if consumes.get('refresh_implementation_proposal_v2') != 'refresh_implementation_proposal_v2':
        errors.append('consumes.refresh_implementation_proposal_v2 must reference refresh implementation proposal v2')
    dependency_ids = _validate_dependency_ordering(errors, plan.get('dependency_ordering'))
    candidates = []
    candidates += _validate_candidates(errors, plan.get('inactive_source_patch_candidates'), 'inactive_source_patch_candidates', 'source', dependency_ids)
    candidates += _validate_candidates(errors, plan.get('inactive_surface_patch_candidates'), 'inactive_surface_patch_candidates', 'surface', dependency_ids)
    candidates += _validate_candidates(errors, plan.get('inactive_guardrail_patch_candidates'), 'inactive_guardrail_patch_candidates', 'guardrail', dependency_ids)
    if not candidates:
        errors.append('at least one inactive patch candidate must be present')
    _validate_owner_rows(errors, plan.get('reviewer_owner_fields'))
    _validate_note_rows(errors, plan.get('fixture_migration_notes'), 'fixture_migration_notes', 'migration_note_id')
    _validate_note_rows(errors, plan.get('rollback_checkpoints'), 'rollback_checkpoints', 'checkpoint_id')
    if not _sequence(plan.get('offline_validation_commands')):
        errors.append('offline_validation_commands must be non-empty')
    for index, command in enumerate(_sequence(plan.get('offline_validation_commands'))):
        if not _string_list(command):
            errors.append(f'offline_validation_commands[{index}] must be a command list')
    if plan.get('attestations') != REQUIRED_ATTESTATIONS:
        errors.append('attestations must preserve no-live/no-DevHub/no-processor/no-mutation staging guardrails')
    if _text(plan.get('staging_status')) != 'inactive_fixture_first_patch_candidates_only':
        errors.append('staging_status must be inactive_fixture_first_patch_candidates_only')
    _reject_unsafe_content(plan, '$', errors)
    return ImplementationPatchStagingPlanV2ValidationResult(not errors, tuple(errors))


def require_implementation_patch_staging_plan_v2(plan: Mapping[str, Any]) -> None:
    result = validate_implementation_patch_staging_plan_v2(plan)
    if not result.ok:
        raise ValueError('invalid implementation patch staging plan v2: ' + '; '.join(result.errors))


def _candidates(rows_value: Any, kind: str, disposition: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    disposition_citations = _accepted_disposition_citations(disposition)
    stage = f'stage-{kind}-patch-candidates'
    if kind == 'guardrail':
        stage = 'stage-guardrail-patch-candidates'
    for index, row in enumerate(_mapping_sequence(rows_value), start=1):
        target_id = _target_id(row, kind)
        rows.append({
            'candidate_id': f'inactive-{kind}-{index:02d}-{_slug(target_id)}',
            'candidate_kind': kind,
            'source_proposal_patch_id': _text(row.get('patch_id')),
            'target_id': target_id,
            'inactive': True,
            'ordered_after': ['validate-consumed-refresh-implementation-proposal-v2', stage],
            'reviewer_owner': _text(row.get('reviewer_owner')) or _default_owner(kind),
            'fixture_migration_note': 'Keep as a committed fixture-derived inactive candidate; do not migrate into active registries, guardrails, prompts, or release state in this staging step.',
            'rollback_checkpoint': 'Remove this inactive candidate row and rerun offline validation; no active PP&D state is changed.',
            'citations': _citation_list(row.get('citations')) + disposition_citations,
        })
    return rows


def _dependency_rows(candidates: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    citations = _derived_citations(candidates)
    return [{'dependency_id': value, 'after': DEPENDENCY_ORDER[:index], 'citations': citations} for index, value in enumerate(DEPENDENCY_ORDER)]


def _owner_rows(candidates: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    seen = set()
    for candidate in candidates:
        owner = _text(candidate.get('reviewer_owner'))
        scope = _text(candidate.get('candidate_kind'))
        key = (owner, scope)
        if owner and key not in seen:
            seen.add(key)
            rows.append({'owner_field_id': f'owner-{_slug(owner)}-{scope}', 'reviewer_owner': owner, 'candidate_scope': scope, 'citations': _citation_list(candidate.get('citations'))})
    return rows


def _fixture_migration_notes(disposition: Mapping[str, Any], proposal: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {'migration_note_id': 'consume-refresh-proposal-fixtures-only', 'summary': 'Stage candidates from refresh implementation proposal fixture rows only; active PP&D artifacts remain unchanged.', 'citations': _derived_citations(_mapping_sequence(proposal.get('rollback_notes')))},
        {'migration_note_id': 'carry-disposition-review-evidence', 'summary': 'Carry reviewer disposition evidence into inactive candidate rows for later owner review and fixture migration.', 'citations': _derived_citations(_mapping_sequence(disposition.get('checklist_decisions')))},
    ]


def _rollback_checkpoints(candidates: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [{'checkpoint_id': 'discard-inactive-staging-plan', 'summary': 'Delete the staging plan artifact and rerun fixture validations; consumed fixtures remain unchanged.', 'citations': _derived_citations(candidates)}]
    for kind in ('source', 'surface', 'guardrail'):
        kind_rows = [row for row in candidates if row.get('candidate_kind') == kind]
        rows.append({'checkpoint_id': f'discard-inactive-{kind}-candidates', 'summary': f'Discard inactive {kind} candidates before any active-state implementation proposal.', 'citations': _derived_citations(kind_rows)})
    return rows


def _validate_dependency_ordering(errors: list[str], value: Any) -> set[str]:
    rows = _mapping_sequence(value)
    ids = [_text(row.get('dependency_id')) for row in rows]
    if not rows:
        errors.append('dependency_ordering must be non-empty')
        return set()
    if ids != DEPENDENCY_ORDER:
        errors.append('dependency_ordering must preserve consumed validation, source, surface, guardrail, fixture migration, rollback, and offline validation order')
    for index, row in enumerate(rows):
        if not _text(row.get('dependency_id')):
            errors.append(f'dependency_ordering[{index}].dependency_id must be present')
        if not isinstance(row.get('after'), list):
            errors.append(f'dependency_ordering[{index}].after must be a list')
        if not _mapping_sequence(row.get('citations')):
            errors.append(f'dependency_ordering[{index}].citations must be non-empty')
    return set(ids)


def _validate_candidates(errors: list[str], value: Any, field: str, kind: str, dependency_ids: set[str]) -> list[Mapping[str, Any]]:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append(f'{field} must be non-empty')
        return []
    for index, row in enumerate(rows):
        if _text(row.get('candidate_kind')) != kind:
            errors.append(f'{field}[{index}].candidate_kind must be {kind}')
        for key in ('candidate_id', 'source_proposal_patch_id', 'target_id', 'reviewer_owner', 'fixture_migration_note', 'rollback_checkpoint'):
            if not _text(row.get(key)):
                errors.append(f'{field}[{index}].{key} must be present')
        if row.get('inactive') is not True:
            errors.append(f'{field}[{index}].inactive must be true')
        if not _mapping_sequence(row.get('citations')):
            errors.append(f'{field}[{index}].citations must be non-empty')
        ordered_after = _string_list(row.get('ordered_after'))
        if not ordered_after:
            errors.append(f'{field}[{index}].ordered_after must be non-empty')
        for dependency in ordered_after:
            if dependency not in dependency_ids:
                errors.append(f'{field}[{index}].ordered_after references unknown dependency')
    return list(rows)


def _validate_owner_rows(errors: list[str], value: Any) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append('reviewer_owner_fields must be non-empty')
        return
    for index, row in enumerate(rows):
        for key in ('owner_field_id', 'reviewer_owner', 'candidate_scope'):
            if not _text(row.get(key)):
                errors.append(f'reviewer_owner_fields[{index}].{key} must be present')
        if not _mapping_sequence(row.get('citations')):
            errors.append(f'reviewer_owner_fields[{index}].citations must be non-empty')


def _validate_note_rows(errors: list[str], value: Any, field: str, id_key: str) -> None:
    rows = _mapping_sequence(value)
    if not rows:
        errors.append(f'{field} must be non-empty')
        return
    for index, row in enumerate(rows):
        if not _text(row.get(id_key)):
            errors.append(f'{field}[{index}].{id_key} must be present')
        if not _text(row.get('summary')):
            errors.append(f'{field}[{index}].summary must be present')
        if not _mapping_sequence(row.get('citations')):
            errors.append(f'{field}[{index}].citations must be non-empty')


def _target_id(row: Mapping[str, Any], kind: str) -> str:
    if kind == 'source':
        return _text(row.get('source_id')) or _text(row.get('target_id'))
    if kind == 'surface':
        return _text(row.get('surface_id')) or _text(row.get('target_id'))
    return _text(row.get('guardrail_bundle_id')) or _text(row.get('decision_id')) or _text(row.get('action_id')) or _text(row.get('target_id'))


def _accepted_disposition_citations(disposition: Mapping[str, Any]) -> list[dict[str, Any]]:
    citations = []
    for row in _mapping_sequence(disposition.get('checklist_decisions')):
        if _text(row.get('decision')) == 'accepted':
            citations.extend(_citation_list(row.get('citations')))
    return citations or [{'packet_field': 'human_review_disposition_summary_v2.checklist_decisions'}]


def _reject_unsafe_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower().replace('-', '_')
            child_path = f'{path}.{key}'
            if normalized in _FORBIDDEN_KEYS and child not in (None, '', [], {}):
                errors.append(f'{child_path} is not allowed in implementation patch staging plan v2')
            if normalized in _MUTATION_KEYS and _is_active_flag(child):
                errors.append(f'{child_path} declares active source, surface-registry, guardrail, prompt, or release-state mutation')
            _reject_unsafe_content(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f'{path}[{index}]', errors)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in _FORBIDDEN_TEXT):
            errors.append(f'{path} contains unsafe live, artifact, mutation, outcome, or official-action language')


def _is_active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {'true', 'enabled', 'active', 'yes'}
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False


def _citation_list(value: Any) -> list[dict[str, Any]]:
    rows = [dict(item) for item in _mapping_sequence(value)]
    return rows or [{'packet_field': 'derived_from_consumed_fixture'}]


def _derived_citations(rows: Any) -> list[dict[str, Any]]:
    citations = []
    for row in _mapping_sequence(rows):
        citations.extend(_citation_list(row.get('citations')))
    return citations or [{'packet_field': 'derived_from_consumed_fixture'}]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list) else ()


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    return tuple(item for item in _sequence(value) if isinstance(item, Mapping))


def _string_list(value: Any) -> list[str]:
    return [item for item in _sequence(value) if isinstance(item, str) and item]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = _text(mapping.get(key))
    if not value:
        raise ValueError(f'fixture must provide {key}')
    return value


def _default_owner(kind: str) -> str:
    return 'ppd-guardrail-reviewer' if kind == 'guardrail' else 'ppd-reviewer-unassigned'


def _slug(value: str) -> str:
    cleaned = ''.join(char.lower() if char.isalnum() else '-' for char in value)
    return '-'.join(part for part in cleaned.split('-') if part) or 'item'
