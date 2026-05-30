from pathlib import Path

import pytest

from ppd.devhub_surface_map_promotion_preview_v3 import build_preview_from_files

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'devhub_surface_map_promotion_preview_v3'


def test_preview_builds_cited_patch_candidates_without_live_artifacts() -> None:
    preview = build_preview_from_files(
        FIXTURE_DIR / 'attended_review_disposition_summary_v3.json',
        FIXTURE_DIR / 'inactive_devhub_surface_fixture_migration_packet_v2.json',
    )

    assert preview['preview_version'] == 'devhub_surface_map_promotion_preview_v3'
    assert preview['mode'] == 'fixture_first_offline_preview'
    assert preview['attestations'] == {
        'no_live_devhub': True,
        'no_auth_state': True,
        'no_screenshot': True,
        'no_trace': True,
        'no_har': True,
        'no_active_surface_registry_mutation': True,
    }

    candidates = {candidate['surface_id']: candidate for candidate in preview['candidates']}
    assert set(candidates) == {'devhub-permit-search', 'devhub-record-detail'}

    search = candidates['devhub-permit-search']
    assert search['fixture_patch_candidate']['operation'] == 'replace_inactive_surface'
    assert search['selector_confidence_delta'] == {'before': 0.62, 'after': 0.86, 'delta': 0.24}
    assert len(search['synthetic_action_rows']['before']) == 1
    assert len(search['synthetic_action_rows']['after']) == 2
    assert search['manual_handoff_disposition'] == 'not_required'
    assert search['redaction_disposition'] == 'redact_fixture_account_hint'
    assert search['dependency_order'][0] == 'redact_fixture_account_hint'
    assert 'fixture://inactive-packet-v2/devhub-permit-search#surface' in search['citations']
    assert 'review://summary-v3/devhub-permit-search#redaction' in search['citations']

    detail = candidates['devhub-record-detail']
    assert detail['manual_handoff_disposition'] == 'required_selector_review'
    assert detail['redaction_disposition'] == 'not_required'
    assert detail['selector_confidence_delta']['delta'] == 0.27
    assert detail['dependency_order'][0] == 'manual_selector_review'
    assert detail['rollback_checkpoints'] == ['restore previous record_detail fixture', 'retain manual handoff note']

    assert ['python3', '-m', 'pytest', 'ppd/tests/test_devhub_surface_map_promotion_preview_v3.py'] in preview['offline_validation_commands']


def test_preview_rejects_missing_offline_attestation() -> None:
    from ppd.devhub_surface_map_promotion_preview_v3 import build_preview, load_json

    summary = load_json(FIXTURE_DIR / 'attended_review_disposition_summary_v3.json')
    packet = load_json(FIXTURE_DIR / 'inactive_devhub_surface_fixture_migration_packet_v2.json')
    packet['attestations']['no_har'] = False

    with pytest.raises(ValueError, match='no_har'):
        build_preview(summary, packet)
