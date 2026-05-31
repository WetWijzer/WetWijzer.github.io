from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from typing import Any

_FIXTURE_DIR = Path(__file__).parent / 'fixtures'
_MATRIX_PATH = _FIXTURE_DIR / 'reversible_draft_action_readiness_matrix_v2.json'
_SURFACE_REVIEWER_PATH = _FIXTURE_DIR / 'devhub_read_only_surface_map_reviewer_packet_v2_valid.json'
_READ_ONLY_CLASSIFICATION_PATH = _FIXTURE_DIR / 'devhub' / 'read_only_observation_action_classification_v1.json'
_PLAYWRIGHT_CLASSIFICATION_PATH = _FIXTURE_DIR / 'devhub' / 'action_classification_playwright.json'

_ALLOWED_CONSEQUENTIAL_PATHS = (
    'exact_confirmation_stop_gates',
    'blocked_consequential_action_examples',
    'synthetic_reversible_draft_scenarios',
)
_REQUIRED_NONEMPTY_SECTIONS = (
    'synthetic_reversible_draft_scenarios',
    'required_user_fact_placeholders',
    'source_evidence_placeholders',
    'preview_only_field_mapping_placeholders',
    'exact_confirmation_stop_gates',
    'blocked_consequential_action_examples',
    'offline_validation_commands',
)
_FORBIDDEN_LIVE_TERMS = (
    'automated login',
    'automated mfa',
    'browser trace',
    'downloaded document',
    'private session',
    'raw crawl',
    'screenshot',
    'storage-state',
)
_FORBIDDEN_ARTIFACT_TERMS = (
    'private session',
    'session artifact',
    'browser artifact',
    'browser trace',
    'raw crawl',
    'downloaded document',
    'storage-state',
    'screenshot',
)
_FORBIDDEN_CLAIM_TERMS = (
    'live devhub execution completed',
    'live devhub execution ran',
    'live devhub run completed',
    'official action completed',
    'official actions completed',
    'official-action completion',
    'permit will issue',
    'will be approved',
    'guarantee',
    'guaranteed',
    'legally sufficient',
)
_MUTATION_FLAG_NAMES = {
    'active_prompt_mutation',
    'active_guardrail_mutation',
    'active_devhub_surface_mutation',
    'active_surface_mutation',
    'active_source_mutation',
    'active_contract_mutation',
    'active_release_state_mutation',
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _walk_strings(value: Any, path: str = '') -> list[tuple[str, str]]:
    if isinstance(value, dict):
        return [item for key, child in value.items() for item in _walk_strings(child, f'{path}.{key}' if path else str(key))]
    if isinstance(value, list):
        return [item for index, child in enumerate(value) for item in _walk_strings(child, f'{path}[{index}]')]
    if isinstance(value, str):
        return [(path, value)]
    return []


def _walk_key_values(value: Any, path: str = '') -> list[tuple[str, str, Any]]:
    if isinstance(value, dict):
        rows: list[tuple[str, str, Any]] = []
        for key, child in value.items():
            child_path = f'{path}.{key}' if path else str(key)
            rows.append((child_path, str(key), child))
            rows.extend(_walk_key_values(child, child_path))
        return rows
    if isinstance(value, list):
        return [item for index, child in enumerate(value) for item in _walk_key_values(child, f'{path}[{index}]')]
    return []


def _validate_matrix(matrix: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    for section in _REQUIRED_NONEMPTY_SECTIONS:
        if not matrix.get(section):
            issues.append(f'missing or empty {section}')

    if matrix.get('live_devhub_access_allowed') is not False:
        issues.append('live_devhub_access_allowed must be false')

    if not any(s.get('classification') == 'reversible_draft_edit' for s in matrix.get('synthetic_reversible_draft_scenarios', [])):
        issues.append('missing reversible draft scenario')

    for fact in matrix.get('required_user_fact_placeholders', []):
        if not str(fact.get('placeholder', '')).startswith('placeholder:') or fact.get('actual_user_value') is not None:
            issues.append('required user facts must stay placeholder-only')

    for evidence in matrix.get('source_evidence_placeholders', []):
        if not str(evidence.get('placeholder', '')).startswith('placeholder:') or evidence.get('live_url_fetched') is not False:
            issues.append('source evidence must stay placeholder-only')

    for mapping in matrix.get('preview_only_field_mapping_placeholders', []):
        if mapping.get('preview_only') is not True:
            issues.append('field mapping must be preview-only')
        if mapping.get('writes_devhub_state') is not False or mapping.get('saves_official_draft') is not False:
            issues.append('field mapping must not write DevHub or official draft state')

    for gate in matrix.get('exact_confirmation_stop_gates', []):
        if gate.get('exact_confirmation_required') is not True or gate.get('allowed_without_exact_confirmation') is not False:
            issues.append('exact confirmation stop gate must fail closed')
        if not str(gate.get('exact_confirmation_text', '')).startswith('EXACT_CONFIRMATION_REQUIRED:'):
            issues.append('exact confirmation stop gate must name the required text')

    for example in matrix.get('blocked_consequential_action_examples', []):
        if example.get('blocked') is not True:
            issues.append('blocked consequential action examples must remain blocked')

    commands = matrix.get('offline_validation_commands', [])
    if ['python3', '-m', 'unittest', 'ppd.tests.test_reversible_draft_action_readiness_matrix_v2'] not in commands:
        issues.append('missing targeted offline validation command')
    if ['python3', '-m', 'unittest', 'discover', '-s', 'ppd/tests', '-p', 'test_*.py'] not in commands:
        issues.append('missing discovery offline validation command')

    for path, key, child in _walk_key_values(matrix):
        if key in _MUTATION_FLAG_NAMES and child is not False:
            issues.append(f'active mutation flag must be false at {path}')

    for path, text in _walk_strings(matrix):
        lowered = text.lower()
        if any(term in lowered for term in _FORBIDDEN_ARTIFACT_TERMS):
            issues.append(f'private/session/browser/raw/downloaded artifact reference at {path}')
        if any(term in lowered for term in _FORBIDDEN_CLAIM_TERMS):
            issues.append(f'forbidden live, official completion, or guarantee claim at {path}')

    return issues


class ReversibleDraftActionReadinessMatrixV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix = _load(_MATRIX_PATH)
        self.surface_reviewer = _load(_SURFACE_REVIEWER_PATH)
        self.read_only_actions = _load(_READ_ONLY_CLASSIFICATION_PATH)
        self.playwright_actions = _load(_PLAYWRIGHT_CLASSIFICATION_PATH)

    def test_matrix_references_existing_approved_read_only_surface_rows(self) -> None:
        approved_rows = {
            row['candidate_row_id']: row
            for row in self.surface_reviewer['candidate_rows']
            if row.get('review_status') == 'human_reviewed'
        }

        self.assertTrue(self.matrix['fixture_first'])
        self.assertFalse(self.matrix['live_devhub_access_allowed'])
        for row in self.matrix['approved_surface_rows']:
            source = approved_rows[row['candidate_row_id']]
            self.assertEqual(row['surface_id'], source['surface_id'])
            self.assertEqual(row['redaction_acceptance_ref'], source['redaction_acceptance_ref'])
            self.assertTrue(set(row['observation_trace_ids']).issubset(source['observation_trace_ids']))
            self.assertTrue(set(row['blocked_action_confirmation_ids']).issubset(source['blocked_action_confirmation_ids']))

    def test_scenarios_are_ordered_and_consume_existing_action_classification_fixtures(self) -> None:
        read_only_ids = {action['action_id'] for action in self.read_only_actions['actions']}
        playwright_ids = {action['id'] for action in self.playwright_actions['mockedFormInteractions']}
        known_action_ids = read_only_ids | playwright_ids

        scenarios = self.matrix['synthetic_reversible_draft_scenarios']
        self.assertEqual([scenario['order'] for scenario in scenarios], [1, 2, 3, 4])
        for scenario in scenarios:
            self.assertIn(scenario['action_fixture_id'], known_action_ids)
            self.assertTrue(scenario['synthetic_only'])

        self.assertEqual(scenarios[0]['classification'], 'read_only_observation')
        self.assertEqual(scenarios[1]['classification'], 'reversible_draft_edit')
        self.assertEqual(scenarios[2]['classification'], 'consequential')
        self.assertEqual(scenarios[3]['classification'], 'financial')

    def test_placeholders_are_required_and_preview_only(self) -> None:
        for fact in self.matrix['required_user_fact_placeholders']:
            self.assertTrue(fact['placeholder'].startswith('placeholder:'))
            self.assertIsNone(fact['actual_user_value'])

        for evidence in self.matrix['source_evidence_placeholders']:
            self.assertTrue(evidence['placeholder'].startswith('placeholder:'))
            self.assertFalse(evidence['live_url_fetched'])

        for mapping in self.matrix['preview_only_field_mapping_placeholders']:
            self.assertTrue(mapping['target_field_placeholder'].startswith('placeholder:'))
            self.assertTrue(mapping['preview_only'])
            self.assertFalse(mapping['writes_devhub_state'])
            self.assertFalse(mapping['saves_official_draft'])

    def test_exact_confirmation_stop_gates_and_blocked_examples_fail_closed(self) -> None:
        for gate in self.matrix['exact_confirmation_stop_gates']:
            self.assertIn(gate['classification'], {'consequential', 'financial'})
            self.assertTrue(gate['exact_confirmation_required'])
            self.assertFalse(gate['allowed_without_exact_confirmation'])
            self.assertTrue(gate['exact_confirmation_text'].startswith('EXACT_CONFIRMATION_REQUIRED:'))

        for example in self.matrix['blocked_consequential_action_examples']:
            self.assertTrue(example['blocked'])
            self.assertIn('official', example['reason'].lower() + ' official')

    def test_offline_validation_commands_are_exact_and_non_live(self) -> None:
        commands = self.matrix['offline_validation_commands']
        self.assertIn(['python3', '-m', 'unittest', 'ppd.tests.test_reversible_draft_action_readiness_matrix_v2'], commands)
        self.assertIn(['python3', '-m', 'unittest', 'discover', '-s', 'ppd/tests', '-p', 'test_*.py'], commands)
        for command in commands:
            joined = ' '.join(command).lower()
            self.assertNotIn('curl', joined)
            self.assertNotIn('playwright', joined)
            self.assertNotIn('devhub', joined.replace('test_reversible_draft_action_readiness_matrix_v2', ''))

    def test_forbidden_live_artifacts_and_mutations_are_absent(self) -> None:
        attestations = self.matrix['prohibition_attestations']
        self.assertTrue(attestations)
        self.assertTrue(all(value is False for value in attestations.values()))
        self.assertEqual([], _validate_matrix(self.matrix))

        for path, text in _walk_strings(self.matrix):
            lowered = text.lower()
            for term in _FORBIDDEN_LIVE_TERMS:
                self.assertNotIn(term, lowered, path)
            if any(word in lowered for word in ('submit', 'certify', 'pay', 'schedule', 'cancel', 'upload', 'save')):
                self.assertTrue(path.startswith(_ALLOWED_CONSEQUENTIAL_PATHS), path)

    def test_validator_rejects_missing_required_sections_and_draft_scenario(self) -> None:
        for section in _REQUIRED_NONEMPTY_SECTIONS:
            with self.subTest(section=section):
                candidate = copy.deepcopy(self.matrix)
                candidate[section] = []
                self.assertTrue(any(section in issue for issue in _validate_matrix(candidate)))

        candidate = copy.deepcopy(self.matrix)
        candidate['synthetic_reversible_draft_scenarios'] = [
            scenario for scenario in candidate['synthetic_reversible_draft_scenarios']
            if scenario['classification'] != 'reversible_draft_edit'
        ]
        self.assertTrue(any('missing reversible draft scenario' in issue for issue in _validate_matrix(candidate)))

    def test_validator_rejects_broken_placeholders_mappings_gates_examples_and_commands(self) -> None:
        cases = (
            ('required_user_fact_placeholders', 'actual_user_value', 'unredacted user fact', 'placeholder-only'),
            ('source_evidence_placeholders', 'live_url_fetched', True, 'placeholder-only'),
            ('preview_only_field_mapping_placeholders', 'writes_devhub_state', True, 'must not write'),
            ('exact_confirmation_stop_gates', 'allowed_without_exact_confirmation', True, 'fail closed'),
            ('blocked_consequential_action_examples', 'blocked', False, 'must remain blocked'),
        )
        for section, key, value, expected in cases:
            with self.subTest(section=section, key=key):
                candidate = copy.deepcopy(self.matrix)
                candidate[section][0][key] = value
                self.assertTrue(any(expected in issue for issue in _validate_matrix(candidate)))

        candidate = copy.deepcopy(self.matrix)
        candidate['offline_validation_commands'] = []
        self.assertTrue(any('offline validation command' in issue for issue in _validate_matrix(candidate)))

    def test_validator_rejects_artifacts_claims_guarantees_and_active_mutations(self) -> None:
        cases = (
            ('artifact', lambda m: m.update({'operator_note': 'private session browser artifact raw crawl downloaded document'}), 'artifact'),
            ('live', lambda m: m.update({'operator_note': 'live DevHub execution completed'}), 'forbidden live'),
            ('official', lambda m: m.update({'operator_note': 'official action completed'}), 'official completion'),
            ('guarantee', lambda m: m.update({'operator_note': 'permit will issue and approval is guaranteed'}), 'guarantee'),
        )
        for label, mutate, expected in cases:
            with self.subTest(label=label):
                candidate = copy.deepcopy(self.matrix)
                mutate(candidate)
                self.assertTrue(any(expected in issue for issue in _validate_matrix(candidate)))

        for flag_name in _MUTATION_FLAG_NAMES:
            with self.subTest(flag_name=flag_name):
                candidate = copy.deepcopy(self.matrix)
                candidate[flag_name] = True
                self.assertTrue(any('active mutation flag' in issue for issue in _validate_matrix(candidate)))


if __name__ == '__main__':
    unittest.main()
