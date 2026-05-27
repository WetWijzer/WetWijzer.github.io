from pathlib import Path

from ppd.logic.requirement_delta_review import build_requirement_delta_review_queue, load_json_snapshot


FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'requirement_delta_review' / 'source_hash_delta_case.json'


def _queue_for_case(name: str) -> dict:
    fixture = load_json_snapshot(FIXTURE_PATH)
    for case in fixture['cases']:
        if case['name'] == name:
            return build_requirement_delta_review_queue(
                case['previous_snapshot'],
                case['current_snapshot'],
            )
    raise AssertionError('missing fixture case %s' % name)


def _delta_by_requirement(queue: dict) -> dict:
    return {delta['requirement_id']: delta for delta in queue['deltas']}


def test_changed_requirement_can_be_ready_only_after_formalization_gate_passes():
    queue = _queue_for_case('formalization-gate-deltas')
    deltas = _delta_by_requirement(queue)

    ready_delta = deltas['REQ-READY-CHANGED']

    assert ready_delta['blocked_readiness_status'] == 'ready'
    assert ready_delta['formalization_gate'] == {
        'status': 'ready',
        'reasons': [],
        'fresh_citation_ids': ['cite-ready-current'],
        'supported_path_ids': ['path-public-html'],
    }
    assert ready_delta['affected_process_ids'] == ['process-building-permit']
    assert ready_delta['guardrail_bundle_ids'] == ['guardrail-building-permit']


def test_formalization_gate_blocks_missing_review_citations_taxonomy_and_mappings():
    queue = _queue_for_case('formalization-gate-deltas')
    deltas = _delta_by_requirement(queue)

    assert deltas['REQ-PENDING-REVIEW']['formalization_gate']['reasons'] == ['pending_human_review']
    assert deltas['REQ-STALE-CITATION']['formalization_gate']['reasons'] == ['stale_citations']
    assert deltas['REQ-MISSING-TAXONOMY']['formalization_gate']['reasons'] == ['missing_supported_path_taxonomy']
    assert deltas['REQ-MISSING-MAPPINGS']['formalization_gate']['reasons'] == [
        'missing_affected_process_ids',
        'missing_guardrail_bundle_ids',
    ]

    for requirement_id in (
        'REQ-PENDING-REVIEW',
        'REQ-STALE-CITATION',
        'REQ-MISSING-TAXONOMY',
        'REQ-MISSING-MAPPINGS',
    ):
        assert deltas[requirement_id]['blocked_readiness_status'].startswith('blocked_')


def test_unchanged_source_requirement_edit_is_ignored():
    queue = _queue_for_case('unchanged-source-requirement-edit-is-ignored')

    assert queue['changed_source_hashes'] == []
    assert queue['delta_count'] == 0
    assert queue['deltas'] == []
