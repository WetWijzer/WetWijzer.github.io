from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.contracts.draft_executor_noop_adapter_v2 import (
    CONTRACT_VERSION,
    EXACT_CONFIRMATION_PHRASE,
    FORBIDDEN_LIVE_ACTIONS,
    build_noop_adapter_contract_v2,
    validate_noop_adapter_contract_v2,
)

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'draft_executor_noop_adapter_v2'


def load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding='utf-8'))


def valid_contract() -> dict[str, object]:
    return build_noop_adapter_contract_v2(load_fixture('approved_executor_review_packet_v2.json')).as_dict()


def test_builds_ordered_fixture_first_noop_contract() -> None:
    contract = valid_contract()

    assert contract['contract_version'] == CONTRACT_VERSION
    assert contract['source_packet_id'] == 'approved-review-packet-v2-fixture-001'
    assert contract['adapter_mode'] == 'fixture_first_preview_only_noop'

    examples = contract['synthetic_examples']
    assert [example['order'] for example in examples] == [1, 2, 3]
    assert [example['step_id'] for example in examples] == [
        'collect-fixture-fields',
        'render-preview-summary',
        'journal-redacted-event',
    ]
    assert all(example['adapter_input']['source'] == 'fixture' for example in examples)
    assert all(example['adapter_input']['live_target_allowed'] is False for example in examples)
    assert all(example['adapter_output']['status'] == 'preview_only_noop' for example in examples)
    assert all(example['adapter_output']['live_mutation_performed'] is False for example in examples)


def test_contract_includes_guardrails_evidence_and_offline_validation() -> None:
    contract = valid_contract()

    evidence_ids = contract['required_dry_run_evidence_ids']
    assert evidence_ids == [
        'dry-run-evidence-01-collect-fixture-fields',
        'dry-run-evidence-02-render-preview-summary',
        'dry-run-evidence-03-journal-redacted-event',
    ]
    assert len(contract['noop_execution_markers']) == len(evidence_ids)
    assert all(event['subject'] == 'REDACTED_SYNTHETIC_FIXTURE' for event in contract['redacted_journal_events'])
    assert all(event['result'] == 'NOOP_PREVIEW_ONLY' for event in contract['redacted_journal_events'])
    assert all('no official draft' in item['summary'] for item in contract['preview_only_mutation_summaries'])

    gates = contract['exact_confirmation_refusal_gates']
    assert gates[0]['required_phrase'] == EXACT_CONFIRMATION_PHRASE
    assert 'Refuse' in gates[0]['refusal']
    assert set(contract['forbidden_live_actions']) == set(FORBIDDEN_LIVE_ACTIONS)
    assert ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'] in contract['offline_validation_commands']


@pytest.mark.parametrize(
    'field_name',
    [
        'synthetic_examples',
        'noop_execution_markers',
        'preview_only_mutation_summaries',
        'redacted_journal_events',
        'required_dry_run_evidence_ids',
        'exact_confirmation_refusal_gates',
        'offline_validation_commands',
    ],
)
def test_validation_rejects_missing_required_contract_sections(field_name: str) -> None:
    contract = valid_contract()
    contract[field_name] = []

    with pytest.raises(ValueError, match=field_name):
        validate_noop_adapter_contract_v2(contract)


def test_validation_rejects_adapter_examples_without_noop_marker_or_evidence() -> None:
    contract = valid_contract()
    contract['synthetic_examples'][0]['adapter_output']['noop_marker'] = 'UNKNOWN_MARKER'

    with pytest.raises(ValueError, match='no-op execution marker'):
        validate_noop_adapter_contract_v2(contract)

    contract = valid_contract()
    contract['synthetic_examples'][0]['adapter_output']['dry_run_evidence_id'] = 'UNKNOWN_EVIDENCE'

    with pytest.raises(ValueError, match='dry-run evidence ID'):
        validate_noop_adapter_contract_v2(contract)


@pytest.mark.parametrize(
    ('field_name', 'bad_value', 'message'),
    [
        ('raw_body', 'raw private page value', 'artifact field'),
        ('session_file', '/tmp/devhub-session.json', 'artifact field'),
        ('notes', 'live DevHub execution completed', 'live DevHub execution'),
        ('notes', 'official draft saved', 'official action'),
        ('notes', 'guaranteed permit approval', 'guarantees'),
        ('notes', 'requires Playwright launch before validation', 'Playwright'),
        ('active_prompt_mutation', True, 'active mutation flag'),
        ('guardrail_mutation_active', 'active', 'active mutation flag'),
        ('devhub_surface_mutation', True, 'active mutation flag'),
        ('source_mutation', True, 'active mutation flag'),
        ('contract_mutation', True, 'active mutation flag'),
        ('release_state_mutation', True, 'active mutation flag'),
    ],
)
def test_validation_rejects_forbidden_artifacts_claims_requirements_and_mutation_flags(
    field_name: str,
    bad_value: object,
    message: str,
) -> None:
    contract = valid_contract()
    contract[field_name] = bad_value

    with pytest.raises(ValueError, match=message):
        validate_noop_adapter_contract_v2(contract)


def test_validation_rejects_non_redacted_journal_examples() -> None:
    contract = valid_contract()
    contract['redacted_journal_events'][0] = copy.deepcopy(contract['redacted_journal_events'][0])
    contract['redacted_journal_events'][0]['subject'] = '123 Main St private applicant'

    with pytest.raises(ValueError, match='redacted subjects'):
        validate_noop_adapter_contract_v2(contract)


def test_validation_rejects_preview_summary_without_preview_only_refusal() -> None:
    contract = valid_contract()
    contract['preview_only_mutation_summaries'][0] = {'step_id': 'bad', 'summary': 'Saved official draft.'}

    with pytest.raises(ValueError, match='preview-only'):
        validate_noop_adapter_contract_v2(contract)


def test_validation_rejects_missing_exact_confirmation_phrase() -> None:
    contract = valid_contract()
    contract['exact_confirmation_refusal_gates'][0]['required_phrase'] = 'close enough'

    with pytest.raises(ValueError, match='exact confirmation phrase'):
        validate_noop_adapter_contract_v2(contract)


def test_validation_rejects_missing_daemon_self_test_command() -> None:
    contract = valid_contract()
    contract['offline_validation_commands'] = [['python3', '-m', 'py_compile', 'ppd/contracts/draft_executor_noop_adapter_v2.py']]

    with pytest.raises(ValueError, match='daemon self-test'):
        validate_noop_adapter_contract_v2(contract)


def test_rejects_unapproved_packet() -> None:
    packet = load_fixture('approved_executor_review_packet_v2.json')
    packet['approval_state'] = 'approved_for_live_execution'

    with pytest.raises(ValueError, match='no-op dry-run'):
        build_noop_adapter_contract_v2(packet)


def test_rejects_wrong_packet_version() -> None:
    packet = load_fixture('approved_executor_review_packet_v2.json')
    packet['packet_version'] = 'approved-executor-review-packet-v1'

    with pytest.raises(ValueError, match='approved-executor-review-packet-v2'):
        build_noop_adapter_contract_v2(packet)
