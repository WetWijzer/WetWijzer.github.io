from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = 'permit_type_coverage_inventory_packet_v2'
PACKET_ID = 'ppd-permit-type-coverage-inventory-packet-v2'
REVIEWER_OWNER = 'PP&D process-model coverage reviewer'

DEFAULT_OFFLINE_VALIDATION_COMMANDS = [
    'python3 -m py_compile ppd/agent_readiness/permit_type_coverage_inventory_packet_v2.py',
    'python3 -m unittest ppd.tests.test_permit_type_coverage_inventory_packet_v2',
    'python3 ppd/daemon/ppd_daemon.py --self-test',
]

NO_ACTION_STATEMENTS = [
    'No live crawl has been performed.',
    'No document download has been performed.',
    'No DevHub page has been opened.',
    'No active process model has been changed.',
    'No guardrail, prompt, source registry, contract, DevHub surface, or release state has been changed.',
]

OFFICIAL_ANCHOR_DERIVED_PERMIT_CATEGORIES = [
    {
        'permit_family_id': 'building',
        'label': 'Building permits',
        'anchor_evidence_refs': ['anchor:ppd-landing:scope', 'anchor:apply-permits:building'],
        'source_evidence_placeholders': ['source-evidence-placeholder:building:official-anchor-derived'],
    },
    {
        'permit_family_id': 'new_single_family_residence_and_detached_adu',
        'label': 'New single-family residence and detached ADU permits',
        'anchor_evidence_refs': ['anchor:devhub-submit-guide:nsfr-adu'],
        'source_evidence_placeholders': ['source-evidence-placeholder:nsfr-adu:official-anchor-derived'],
    },
    {
        'permit_family_id': 'solar',
        'label': 'Solar permits',
        'anchor_evidence_refs': ['anchor:online-tools:solar', 'anchor:devhub-submit-guide:solar'],
        'source_evidence_placeholders': ['source-evidence-placeholder:solar:official-anchor-derived'],
    },
    {
        'permit_family_id': 'fcc_wireless',
        'label': 'FCC wireless permits',
        'anchor_evidence_refs': ['anchor:devhub-submit-guide:fcc-wireless'],
        'source_evidence_placeholders': ['source-evidence-placeholder:fcc-wireless:official-anchor-derived'],
    },
    {
        'permit_family_id': 'demolition',
        'label': 'Demolition permits',
        'anchor_evidence_refs': ['anchor:devhub-submit-guide:demolition'],
        'source_evidence_placeholders': ['source-evidence-placeholder:demolition:official-anchor-derived'],
    },
    {
        'permit_family_id': 'trade',
        'label': 'Standard trade permits',
        'anchor_evidence_refs': ['anchor:online-tools:standard-trade', 'anchor:devhub-faq:standard-permits'],
        'source_evidence_placeholders': ['source-evidence-placeholder:trade:official-anchor-derived'],
    },
    {
        'permit_family_id': 'trade_with_plan_review',
        'label': 'Trade permits with plan review',
        'anchor_evidence_refs': ['anchor:devhub-submit-guide:trade-with-plan-review'],
        'source_evidence_placeholders': ['source-evidence-placeholder:trade-with-plan-review:official-anchor-derived'],
    },
    {
        'permit_family_id': 'sign',
        'label': 'Sign permits',
        'anchor_evidence_refs': ['anchor:devhub-submit-guide:sign'],
        'source_evidence_placeholders': ['source-evidence-placeholder:sign:official-anchor-derived'],
    },
    {
        'permit_family_id': 'urban_forestry',
        'label': 'Urban Forestry requests',
        'anchor_evidence_refs': ['anchor:online-tools:tree-permits', 'anchor:devhub-submit-guide:urban-forestry'],
        'source_evidence_placeholders': ['source-evidence-placeholder:urban-forestry:official-anchor-derived'],
    },
    {
        'permit_family_id': 'public_works',
        'label': 'Public works permits',
        'anchor_evidence_refs': ['anchor:ppd-landing:scope'],
        'source_evidence_placeholders': ['source-evidence-placeholder:public-works:official-anchor-derived'],
    },
    {
        'permit_family_id': 'land_use',
        'label': 'Land use reviews',
        'anchor_evidence_refs': ['anchor:ppd-landing:scope'],
        'source_evidence_placeholders': ['source-evidence-placeholder:land-use:official-anchor-derived'],
    },
    {
        'permit_family_id': 'code_enforcement',
        'label': 'Code enforcement cases',
        'anchor_evidence_refs': ['anchor:ppd-landing:scope'],
        'source_evidence_placeholders': ['source-evidence-placeholder:code-enforcement:official-anchor-derived'],
    },
]

REQUIRED_MODEL_SECTIONS = {
    'eligibility_rules',
    'required_user_facts',
    'required_documents',
    'stages',
    'unsupported_paths',
}

STALE_STATUSES = {'missing', 'stale', 'synthetic_unverified', 'fixture_seed_pending_first_crawl'}
COVERAGE_STATUSES_REQUIRING_REVIEW = {'uncovered', 'weakly_covered'}

ACTIVE_MUTATION_FLAGS = {
    'active_source_mutation',
    'active_requirement_mutation',
    'active_process_model_mutation',
    'active_guardrail_mutation',
    'active_prompt_mutation',
    'active_contract_mutation',
    'active_devhub_surface_mutation',
    'active_release_state_mutation',
    'active_source_registry_mutation',
    'active_surface_registry_mutation',
    'source_registries_changed',
    'requirements_changed',
    'active_process_models_changed',
    'guardrails_changed',
    'prompts_changed',
    'contracts_changed',
    'devhub_surfaces_changed',
    'release_state_changed',
}

PRIVATE_OR_RAW_ARTIFACT_KEYS = {
    'auth_state',
    'browser_session',
    'browser_trace',
    'cookies',
    'downloaded_artifact',
    'downloaded_document',
    'downloaded_file',
    'har',
    'local_storage',
    'playwright_state',
    'private_artifact',
    'raw_artifact',
    'raw_body',
    'raw_document',
    'raw_download',
    'session_storage',
    'screenshot',
    'trace_zip',
}

FORBIDDEN_TEXT_PATTERNS = (
    ('private or session artifact', re.compile(r'\b(?:cookie|auth state|session token|playwright trace|har file|screenshot|raw crawl output|downloaded document)\b', re.IGNORECASE)),
    ('live crawl or DevHub claim', re.compile(r'\b(?:live crawl completed|crawled live|opened devhub|devhub opened|devhub session|authenticated devhub|submitted in devhub|completed in devhub)\b', re.IGNORECASE)),
    ('legal or permitting guarantee', re.compile(r'\b(?:guarantee(?:d|s)? approval|approval is certain|will be approved|legally sufficient|legal advice|permit outcome is assured|permitting guarantee)\b', re.IGNORECASE)),
)


class PermitTypeCoverageInventoryPacketV2Error(ValueError):
    pass


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _text(value: Any, default: str = '') -> str:
    return default if value is None else str(value)


def _records(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, list):
        return [row for row in value if isinstance(row, Mapping)]
    if isinstance(value, Mapping):
        for key in ('records', 'categories', 'permit_categories', 'process_models', 'models'):
            nested = value.get(key)
            if isinstance(nested, list):
                return [row for row in nested if isinstance(row, Mapping)]
    return []


def _category_id(row: Mapping[str, Any]) -> str:
    return _text(row.get('permit_family_id') or row.get('permit_type') or row.get('id'))


def _model_permit_ids(row: Mapping[str, Any]) -> set[str]:
    values = set()
    for key in ('permit_family_id', 'permit_type', 'permit_types', 'covered_permit_families'):
        for value in _as_list(row.get(key)):
            if value:
                values.add(str(value))
    return values


def _model_id(row: Mapping[str, Any], fallback: str) -> str:
    return _text(row.get('process_id') or row.get('model_id') or row.get('id'), fallback)


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def _iter_key_values(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(key, str):
                yield key, item
            yield from _iter_key_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_key_values(item)


def _stale_notes(category: Mapping[str, Any], models: list[Mapping[str, Any]]) -> list[str]:
    notes = []
    freshness_values = []
    for row in [category] + models:
        freshness_values.extend(str(value) for value in _as_list(row.get('freshness_status')) if value)
        freshness_values.extend(str(value) for value in _as_list(row.get('source_freshness_status')) if value)
    if not freshness_values:
        notes.append('Hold for first live source freshness review before active promotion.')
    for value in sorted(set(freshness_values)):
        if value in STALE_STATUSES:
            notes.append('Hold for source freshness status: %s.' % value)
    return notes or ['No stale-source hold identified in fixture; reviewer must confirm before promotion.']


def _unsupported_path_notes(category: Mapping[str, Any], models: list[Mapping[str, Any]]) -> list[str]:
    notes = []
    for row in [category] + models:
        for value in _as_list(row.get('unsupported_paths')):
            if value:
                notes.append(str(value))
        for value in _as_list(row.get('unsupported_path_notes')):
            if value:
                notes.append(str(value))
    return sorted(set(notes)) or ['Unsupported paths not yet modeled; do not assume DevHub coverage for this family.']


def _coverage_status(models: list[Mapping[str, Any]]) -> str:
    if not models:
        return 'uncovered'
    for model in models:
        completeness = set(str(value) for value in _as_list(model.get('modeled_sections')))
        if REQUIRED_MODEL_SECTIONS.issubset(completeness) and model.get('synthetic_only') is not True:
            return 'covered'
    return 'weakly_covered'


def _findings(status: str, models: list[Mapping[str, Any]]) -> list[str]:
    if status == 'uncovered':
        return ['No existing synthetic process model declares coverage for this official anchor-derived permit family.']
    missing_by_model = []
    for index, model in enumerate(models, start=1):
        completeness = set(str(value) for value in _as_list(model.get('modeled_sections')))
        missing = sorted(REQUIRED_MODEL_SECTIONS - completeness)
        if model.get('synthetic_only') is True:
            missing.append('official_source_evidence')
        if missing:
            missing_by_model.append('%s missing %s' % (_model_id(model, 'model-%d' % index), ', '.join(sorted(set(missing)))))
    if status == 'weakly_covered':
        return missing_by_model or ['Existing coverage is fixture-only and needs reviewer confirmation before promotion.']
    return ['At least one synthetic process model has the required fixture sections; reviewer still must confirm official evidence before active promotion.']


def _coverage_mapping(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        'permit_family_id': row['permit_family_id'],
        'process_model_ids': list(row['process_model_ids']),
        'coverage_status': row['coverage_status'],
        'coverage_findings': list(row['coverage_findings']),
    }


def build_permit_type_coverage_inventory_packet_v2(source_inputs: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(source_inputs, Mapping):
        raise TypeError('source_inputs must be an object')
    categories = _records(source_inputs.get('official_anchor_derived_permit_categories')) or OFFICIAL_ANCHOR_DERIVED_PERMIT_CATEGORIES
    models = _records(source_inputs.get('synthetic_process_models'))
    commands = list(source_inputs.get('offline_validation_commands') or DEFAULT_OFFLINE_VALIDATION_COMMANDS)
    reviewer_owner = _text(source_inputs.get('reviewer_owner'), REVIEWER_OWNER)
    rows = []
    priority = {'uncovered': 0, 'weakly_covered': 1, 'covered': 2}
    for category in categories:
        permit_family_id = _category_id(category)
        if not permit_family_id:
            raise PermitTypeCoverageInventoryPacketV2Error('permit category row is missing permit_family_id')
        matching_models = [model for model in models if permit_family_id in _model_permit_ids(model)]
        status = _coverage_status(matching_models)
        process_model_ids = [_model_id(model, 'model-%d' % index) for index, model in enumerate(matching_models, start=1)]
        rows.append({
            'permit_family_id': permit_family_id,
            'label': _text(category.get('label'), permit_family_id.replace('_', ' ').title()),
            'anchor_evidence_refs': [str(value) for value in _as_list(category.get('anchor_evidence_refs'))],
            'process_model_ids': process_model_ids,
            'coverage_status': status,
            'coverage_findings': _findings(status, matching_models),
            'source_evidence_placeholders': [str(value) for value in _as_list(category.get('source_evidence_placeholders'))] or ['source-evidence-placeholder:%s' % permit_family_id],
            'stale_source_hold_notes': _stale_notes(category, matching_models),
            'unsupported_path_notes': _unsupported_path_notes(category, matching_models),
            'reviewer_disposition_placeholder': {
                'owner': reviewer_owner,
                'status': 'pending_review',
                'allowed_values': ['accept_gap', 'needs_fixture_expansion', 'defer_until_recrawl', 'not_applicable'],
                'notes': '',
            },
            'exact_offline_validation_commands': commands,
        })
    rows.sort(key=lambda row: (priority[row['coverage_status']], row['permit_family_id']))
    packet = {
        'schema_version': SCHEMA_VERSION,
        'packet_id': PACKET_ID,
        'fixture_first': True,
        'metadata_only': True,
        'comparison_basis': 'official_anchor_derived_permit_categories_vs_existing_synthetic_process_model_coverage',
        'official_anchor_derived_permit_categories': [dict(category) for category in categories],
        'permit_family_count': len(rows),
        'existing_coverage_mappings': [_coverage_mapping(row) for row in rows],
        'uncovered_or_weakly_covered_permit_families': [row for row in rows if row['coverage_status'] in COVERAGE_STATUSES_REQUIRING_REVIEW],
        'all_permit_family_rows': rows,
        'reviewer_owner': reviewer_owner,
        'exact_offline_validation_commands': commands,
        'attestations': {
            'live_crawl_performed': False,
            'document_download_performed': False,
            'devhub_opened': False,
            'active_source_mutation': False,
            'active_requirement_mutation': False,
            'active_process_model_mutation': False,
            'active_guardrail_mutation': False,
            'active_prompt_mutation': False,
            'active_contract_mutation': False,
            'active_devhub_surface_mutation': False,
            'active_release_state_mutation': False,
            'active_process_models_changed': False,
            'guardrails_changed': False,
            'prompts_changed': False,
            'source_registries_changed': False,
            'contracts_changed': False,
            'devhub_surfaces_changed': False,
            'release_state_changed': False,
        },
        'no_action_statements': list(NO_ACTION_STATEMENTS),
    }
    require_valid_permit_type_coverage_inventory_packet_v2(packet)
    return packet


def validate_permit_type_coverage_inventory_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return ['packet must be an object']
    if packet.get('schema_version') != SCHEMA_VERSION:
        errors.append('schema_version must be %s' % SCHEMA_VERSION)
    if packet.get('packet_id') != PACKET_ID:
        errors.append('packet_id must be %s' % PACKET_ID)
    if packet.get('fixture_first') is not True:
        errors.append('fixture_first must be true')
    if packet.get('metadata_only') is not True:
        errors.append('metadata_only must be true')

    _validate_forbidden_payloads(packet, errors)

    categories = _records(packet.get('official_anchor_derived_permit_categories'))
    if not categories:
        errors.append('official_anchor_derived_permit_categories must include official permit categories')
    category_ids = [_category_id(category) for category in categories]
    if any(not category_id for category_id in category_ids):
        errors.append('official permit categories must include permit_family_id values')
    if len(set(category_ids)) != len(category_ids):
        errors.append('official permit categories must not contain duplicate permit_family_id values')

    rows = _records(packet.get('all_permit_family_rows'))
    if not rows:
        errors.append('all_permit_family_rows must include permit coverage rows')
    row_ids = {_category_id(row) for row in rows}
    missing_rows = sorted(set(category_ids) - row_ids)
    if missing_rows:
        errors.append('all_permit_family_rows is missing rows for: %s' % ', '.join(missing_rows))

    mappings = _records(packet.get('existing_coverage_mappings'))
    if not mappings:
        errors.append('existing_coverage_mappings must include one mapping per official permit category')
    mapping_ids = {_category_id(mapping) for mapping in mappings}
    missing_mappings = sorted(set(category_ids) - mapping_ids)
    if missing_mappings:
        errors.append('existing_coverage_mappings is missing categories: %s' % ', '.join(missing_mappings))

    expected_review_ids = {
        _category_id(row)
        for row in rows
        if str(row.get('coverage_status')) in COVERAGE_STATUSES_REQUIRING_REVIEW
    }
    review_rows = _records(packet.get('uncovered_or_weakly_covered_permit_families'))
    review_ids = {_category_id(row) for row in review_rows}
    if expected_review_ids and not review_rows:
        errors.append('uncovered_or_weakly_covered_permit_families must include uncovered or weakly covered rows')
    missing_review_rows = sorted(expected_review_ids - review_ids)
    if missing_review_rows:
        errors.append('uncovered_or_weakly_covered_permit_families is missing: %s' % ', '.join(missing_review_rows))

    for row in rows:
        row_id = _category_id(row) or 'unknown'
        if row.get('coverage_status') not in {'covered', 'uncovered', 'weakly_covered'}:
            errors.append('coverage row %s has invalid coverage_status' % row_id)
        if not _string_list(row.get('anchor_evidence_refs')):
            errors.append('coverage row %s must include anchor_evidence_refs' % row_id)
        if not _string_list(row.get('coverage_findings')):
            errors.append('coverage row %s must include coverage_findings' % row_id)
        if not _string_list(row.get('source_evidence_placeholders')):
            errors.append('coverage row %s must include source_evidence_placeholders' % row_id)
        if not _string_list(row.get('stale_source_hold_notes')):
            errors.append('coverage row %s must include stale_source_hold_notes' % row_id)
        if not _string_list(row.get('unsupported_path_notes')):
            errors.append('coverage row %s must include unsupported_path_notes' % row_id)
        disposition = row.get('reviewer_disposition_placeholder')
        if not isinstance(disposition, Mapping):
            errors.append('coverage row %s must include reviewer_disposition_placeholder' % row_id)
        else:
            if not disposition.get('owner'):
                errors.append('coverage row %s reviewer disposition must include owner' % row_id)
            if disposition.get('status') != 'pending_review':
                errors.append('coverage row %s reviewer disposition must be pending_review' % row_id)
            if not _string_list(disposition.get('allowed_values')):
                errors.append('coverage row %s reviewer disposition must include allowed_values' % row_id)
        if not _string_list(row.get('exact_offline_validation_commands')):
            errors.append('coverage row %s must include exact_offline_validation_commands' % row_id)

    if not _string_list(packet.get('exact_offline_validation_commands')):
        errors.append('exact_offline_validation_commands must include validation commands')

    attestations = packet.get('attestations')
    if not isinstance(attestations, Mapping):
        errors.append('attestations must be an object')
    else:
        for key in ('live_crawl_performed', 'document_download_performed', 'devhub_opened'):
            if attestations.get(key) is not False:
                errors.append('attestation %s must be false' % key)
        for key in sorted(ACTIVE_MUTATION_FLAGS):
            if key in attestations and attestations.get(key) is not False:
                errors.append('active mutation flag %s must be false' % key)

    if not _string_list(packet.get('no_action_statements')):
        errors.append('no_action_statements must include explicit non-action notes')
    return errors


def require_valid_permit_type_coverage_inventory_packet_v2(packet: Mapping[str, Any]) -> None:
    errors = validate_permit_type_coverage_inventory_packet_v2(packet)
    if errors:
        raise PermitTypeCoverageInventoryPacketV2Error('; '.join(errors))


def _validate_forbidden_payloads(packet: Mapping[str, Any], errors: list[str]) -> None:
    reported: set[str] = set()
    for key, value in _iter_key_values(packet):
        if key in PRIVATE_OR_RAW_ARTIFACT_KEYS:
            reported.add('private/session/browser/raw/downloaded artifacts')
        if key in ACTIVE_MUTATION_FLAGS and value is not False:
            reported.add('active mutation flags')
    for text in _iter_strings(packet):
        for label, pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(text):
                reported.add(label)
    for label in sorted(reported):
        errors.append('permit-type coverage inventory packet must not contain %s' % label)


def render_permit_type_coverage_inventory_packet_v2(packet_or_inputs: Mapping[str, Any]) -> str:
    packet = packet_or_inputs
    if packet.get('schema_version') != SCHEMA_VERSION:
        packet = build_permit_type_coverage_inventory_packet_v2(packet_or_inputs)
    require_valid_permit_type_coverage_inventory_packet_v2(packet)
    lines = ['Permit-Type Coverage Inventory Packet v2']
    lines.append('Permit families: %d' % packet['permit_family_count'])
    lines.append('Uncovered or weakly covered: %d' % len(packet['uncovered_or_weakly_covered_permit_families']))
    for row in packet['uncovered_or_weakly_covered_permit_families']:
        lines.append('- %s: %s' % (row['permit_family_id'], row['coverage_status']))
    lines.append('Exact offline validation commands:')
    lines.extend('- %s' % command for command in packet['exact_offline_validation_commands'])
    lines.append('Explicit non-action statements:')
    lines.extend('- %s' % statement for statement in packet['no_action_statements'])
    return '\n'.join(lines)


build_packet = build_permit_type_coverage_inventory_packet_v2
render_packet = render_permit_type_coverage_inventory_packet_v2
validate_packet = validate_permit_type_coverage_inventory_packet_v2
require_valid_packet = require_valid_permit_type_coverage_inventory_packet_v2


def load_source_inputs(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise TypeError('source inputs fixture must be a JSON object')
    return data


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print('usage: permit_type_coverage_inventory_packet_v2.py SOURCE_INPUTS_JSON', file=sys.stderr)
        return 2
    packet = build_permit_type_coverage_inventory_packet_v2(load_source_inputs(args[0]))
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
