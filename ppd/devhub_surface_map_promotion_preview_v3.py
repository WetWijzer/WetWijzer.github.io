from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_ATTESTATIONS = {
    'no_live_devhub': True,
    'no_auth_state': True,
    'no_screenshot': True,
    'no_trace': True,
    'no_har': True,
    'no_active_surface_registry_mutation': True,
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open('r', encoding='utf-8') as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f'{path} must contain a JSON object')
    return data


def build_preview(attended_review_summary: dict[str, Any], migration_packet: dict[str, Any]) -> dict[str, Any]:
    attestations = migration_packet.get('attestations', {})
    missing = [name for name, value in REQUIRED_ATTESTATIONS.items() if attestations.get(name) is not value]
    if missing:
        raise ValueError('migration packet is missing offline attestations: ' + ', '.join(sorted(missing)))

    dispositions = {
        item['surface_id']: item
        for item in attended_review_summary.get('surface_dispositions', [])
    }

    candidates: list[dict[str, Any]] = []
    for surface in migration_packet.get('inactive_surfaces', []):
        surface_id = surface['surface_id']
        disposition = dispositions.get(surface_id, {})
        before_actions = surface.get('synthetic_actions_before', [])
        after_actions = surface.get('synthetic_actions_after', [])
        before_confidence = float(surface.get('selector_confidence_before', 0.0))
        after_confidence = float(surface.get('selector_confidence_after', before_confidence))
        citations = list(dict.fromkeys(surface.get('citations', []) + disposition.get('citations', [])))

        candidates.append({
            'surface_id': surface_id,
            'surface_name': surface.get('surface_name', surface_id),
            'promotion_state': 'preview_only',
            'citations': citations,
            'fixture_patch_candidate': {
                'target_fixture': surface['target_fixture'],
                'operation': 'replace_inactive_surface',
                'source_packet': migration_packet['packet_id'],
                'review_summary': attended_review_summary['summary_id'],
            },
            'synthetic_action_rows': {
                'before': before_actions,
                'after': after_actions,
            },
            'selector_confidence_delta': {
                'before': before_confidence,
                'after': after_confidence,
                'delta': round(after_confidence - before_confidence, 4),
            },
            'manual_handoff_disposition': disposition.get('manual_handoff_disposition', 'not_required'),
            'redaction_disposition': disposition.get('redaction_disposition', 'not_required'),
            'dependency_order': surface.get('dependency_order', []),
            'rollback_checkpoints': surface.get('rollback_checkpoints', []),
        })

    return {
        'preview_version': 'devhub_surface_map_promotion_preview_v3',
        'mode': 'fixture_first_offline_preview',
        'inputs': {
            'attended_review_summary': attended_review_summary['summary_id'],
            'migration_packet': migration_packet['packet_id'],
        },
        'candidates': candidates,
        'offline_validation_commands': [
            ['python3', '-m', 'pytest', 'ppd/tests/test_devhub_surface_map_promotion_preview_v3.py'],
            ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
        ],
        'attestations': REQUIRED_ATTESTATIONS.copy(),
    }


def build_preview_from_files(attended_review_summary_path: Path, migration_packet_path: Path) -> dict[str, Any]:
    return build_preview(load_json(attended_review_summary_path), load_json(migration_packet_path))
