from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PREVIEW_VERSION = 'inactive_fixture_promotion_application_preview_v1'


def load_json(path: Path) -> dict[str, Any]:
    with path.open('r', encoding='utf-8') as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f'expected JSON object at {path}')
    return value


def build_application_preview_from_files(plan_path: Path, inactive_families_path: Path) -> dict[str, Any]:
    return build_application_preview(load_json(plan_path), load_json(inactive_families_path))


def build_application_preview(plan: dict[str, Any], inactive_families: dict[str, Any]) -> dict[str, Any]:
    families_by_id = _index_families(inactive_families)
    rows = [_preview_row(row, plan, families_by_id) for row in _as_list(plan.get('affected_fixture_family_rows'))]
    rows = sorted(rows, key=lambda row: (row['file_scope'], row['family_id']))
    return {
        'preview_version': PREVIEW_VERSION,
        'source_plan_id': str(plan.get('artifact_id', 'unknown_plan')),
        'source_plan_version': plan.get('version', 'unknown'),
        'source_fixture_inventory_id': str(inactive_families.get('inventory_id', 'unknown_inventory')),
        'file_scoped_fixture_previews': rows,
        'citation_preservation_checks': [row['citation_preservation_check'] for row in rows],
        'blocked_row_explanations': [
            {'family_id': row['family_id'], 'file_scope': row['file_scope'], 'reasons': row['blocked_reasons']}
            for row in rows
            if row['blocked_reasons']
        ],
        'validation_replay_inventory': {
            'command_count': len(_validation_commands(plan)),
            'commands': _validation_commands(plan),
            'replay_mode': 'offline_fixture_only',
            'blocked_behaviors': sorted(_strings(plan.get('blocked_validation_behaviors'))),
        },
        'reviewer_signoff_placeholders': [
            {
                'family_id': row['family_id'],
                'file_scope': row['file_scope'],
                'reviewer_owner': row['reviewer_owner'],
                'decision': 'pending',
                'reviewed_at': '',
                'notes': '',
            }
            for row in rows
        ],
        'rollback_notes': _rollback_notes(plan),
        'side_effects': {
            'fixture_changes_applied': False,
            'active_artifacts_mutated': False,
            'prompts_changed': False,
            'live_sources_crawled': False,
            'devhub_accessed': False,
            'official_actions_performed': False,
        },
    }


def _preview_row(row: Any, plan: dict[str, Any], families_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(row, dict):
        row = {}
    family_id = str(row.get('family_id', ''))
    family = families_by_id.get(family_id)
    before = _snapshot(family)
    citations = _citations(row, family, plan)
    blocked_reasons = _blocked_reasons(row, family, before, citations)
    status = 'blocked' if blocked_reasons else 'ready_for_review'
    after = {
        'exists': before['exists'],
        'would_apply_fixture_change': False,
        'would_remain_inactive_fixture_only': status == 'ready_for_review',
        'file_scope': str(row.get('target_fixture_area', '')),
        'planned_allowed_operations': sorted(_strings(row.get('allowed_operations'))),
        'fixture_ids': before['fixture_ids'],
        'content_hashes': before['content_hashes'],
        'citations': citations,
    }
    return {
        'family_id': family_id,
        'file_scope': str(row.get('target_fixture_area', '')),
        'source_input': str(row.get('source_input', '')),
        'reviewer_owner': str(row.get('reviewer_owner', '')),
        'preview_status': status,
        'blocked_reasons': blocked_reasons,
        'before_fixture': before,
        'after_fixture_preview': after,
        'citation_preservation_check': {
            'family_id': family_id,
            'file_scope': str(row.get('target_fixture_area', '')),
            'before_citations': before['citations'],
            'after_citations': citations,
            'preserved': bool(before['citations']) and set(before['citations']).issubset(set(citations)),
            'missing_citations': sorted(set(before['citations']) - set(citations)),
        },
    }


def _snapshot(family: dict[str, Any] | None) -> dict[str, Any]:
    if family is None:
        return {'exists': False, 'fixture_count': 0, 'fixture_ids': [], 'file_paths': [], 'content_hashes': [], 'citations': [], 'all_rows_inactive': False}
    fixtures = sorted(
        [fixture for fixture in _as_list(family.get('fixtures')) if isinstance(fixture, dict)],
        key=lambda fixture: str(fixture.get('fixture_id', '')),
    )
    citations = set(_strings(family.get('citations')))
    for fixture in fixtures:
        citations.update(_strings(fixture.get('citations')))
    return {
        'exists': True,
        'fixture_count': len(fixtures),
        'fixture_ids': [str(fixture.get('fixture_id', '')) for fixture in fixtures],
        'file_paths': sorted(str(fixture.get('file_path', '')) for fixture in fixtures if fixture.get('file_path')),
        'content_hashes': sorted(str(fixture.get('content_hash', '')) for fixture in fixtures if fixture.get('content_hash')),
        'citations': sorted(citations),
        'all_rows_inactive': all(fixture.get('active') is False for fixture in fixtures) if fixtures else False,
    }


def _citations(row: dict[str, Any], family: dict[str, Any] | None, plan: dict[str, Any]) -> list[str]:
    citations = set(_strings(row.get('citations')))
    if family is not None:
        citations.update(_strings(family.get('citations')))
        for fixture in _as_list(family.get('fixtures')):
            if isinstance(fixture, dict):
                citations.update(_strings(fixture.get('citations')))
    for step in _as_list(plan.get('ordered_application_steps')):
        if isinstance(step, dict):
            citations.update(_strings(step.get('citations')))
    return sorted(citations)


def _blocked_reasons(row: dict[str, Any], family: dict[str, Any] | None, before: dict[str, Any], citations: list[str]) -> list[str]:
    reasons = []
    target = str(row.get('target_fixture_area', ''))
    if family is None:
        reasons.append('fixture_family_missing')
    if target and not target.startswith('ppd/tests/fixtures/'):
        reasons.append('target_path_outside_ppd_tests_fixtures')
    if not str(row.get('reviewer_owner', '')):
        reasons.append('reviewer_owner_missing')
    if not str(row.get('review_focus', '')):
        reasons.append('review_focus_missing')
    if not before['citations']:
        reasons.append('before_fixture_citations_missing')
    if not citations:
        reasons.append('preview_citations_missing')
    if before['exists'] and not before['all_rows_inactive']:
        reasons.append('fixture_family_contains_active_row')
    if family is not None:
        reasons.extend(f'family_validation_error:{error}' for error in _strings(family.get('validation_errors')))
    return sorted(reasons)


def _rollback_notes(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            'checkpoint_id': str(checkpoint.get('checkpoint_id', '')),
            'restore_scope': str(checkpoint.get('restore_scope', '')),
            'trigger_conditions': sorted(_strings(checkpoint.get('trigger_conditions'))),
            'activation_status': 'not_activated_preview_only',
        }
        for checkpoint in _as_list(plan.get('rollback_checkpoints'))
        if isinstance(checkpoint, dict)
    ]


def _validation_commands(plan: dict[str, Any]) -> list[Any]:
    return [command for command in _as_list(plan.get('exact_offline_validation_commands')) if isinstance(command, list)]


def _index_families(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    families = {}
    for family in _as_list(inventory.get('inactive_fixture_families')):
        if isinstance(family, dict) and family.get('family_id'):
            families[str(family.get('family_id'))] = family
    return families


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError('expected list')
    return value


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]
