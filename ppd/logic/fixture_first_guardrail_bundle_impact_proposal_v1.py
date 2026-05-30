'''Fixture-first guardrail bundle impact proposal v1.'''

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any

from ppd.logic.process_model_impact_proposal_v1 import assert_valid_process_model_impact_proposal_v1
from ppd.validation.requirement_formalization_candidate_packet_v1 import validate_packet as validate_requirement_packet


PACKET_TYPE = 'fixture_first_guardrail_bundle_impact_proposal_v1'
PACKET_MODE = 'proposal_only_no_compile_no_promotion'
REQUIRED_IMPACT_TYPES = (
    'proposed_predicate',
    'explanation_template',
    'exact_confirmation',
    'refused_action',
    'reversible_action',
    'temporal_rule',
)
FALSE_ATTESTATIONS = (
    'mutated_active_guardrail_bundle',
    'compiled_guardrail_bundle',
    'promoted_guardrail_bundle',
    'mutated_active_prompt',
    'mutated_active_process_model',
    'mutated_active_requirement',
    'mutated_release_state',
    'mutated_agent_state',
)
PROHIBITED_KEYS = {
    'active_guardrail_bundle_patch',
    'active_guardrail_bundle_replacement',
    'compiled_guardrail_bundle_path',
    'guardrail_bundle_promotion',
    'prompt_patch',
    'process_model_patch',
    'release_state_patch',
}
PROHIBITED_TEXT = (
    'cookie',
    'password',
    'session token',
    'storage_state',
    'playwright trace',
    'screenshot',
    'har file',
    'raw crawl',
    'raw html',
    'downloaded document',
)


@dataclass(frozen=True)
class GuardrailBundleImpactProposalFinding:
    code: str
    path: str
    message: str


class GuardrailBundleImpactProposalError(ValueError):
    '''Raised when a guardrail bundle impact proposal v1 packet is invalid.'''


def build_guardrail_bundle_impact_proposal_v1(
    process_model_impact_proposal: Mapping[str, Any],
    requirement_formalization_packet: Mapping[str, Any],
    guardrail_bundle_fixtures: Sequence[Mapping[str, Any]],
    *,
    generated_at: str,
    reviewer_owner: str,
) -> dict[str, Any]:
    '''Build a deterministic fixture-first guardrail impact proposal.'''

    assert_valid_process_model_impact_proposal_v1(process_model_impact_proposal)
    requirement_issues = validate_requirement_packet(requirement_formalization_packet)
    if requirement_issues:
        detail = '; '.join(f'{issue.code} at {issue.path}' for issue in requirement_issues)
        raise GuardrailBundleImpactProposalError('invalid requirement formalization packet: ' + detail)
    if not guardrail_bundle_fixtures:
        raise GuardrailBundleImpactProposalError('at least one guardrail bundle fixture is required')

    bundle_ids = sorted({_bundle_id(fixture) for fixture in guardrail_bundle_fixtures})
    process_ids = _process_ids(process_model_impact_proposal)
    requirement_ids = _requirement_ids(process_model_impact_proposal, requirement_formalization_packet)
    evidence_ids = _evidence_ids(process_model_impact_proposal, requirement_formalization_packet, guardrail_bundle_fixtures)
    rows = [_impact_row(kind, bundle_ids, process_ids, requirement_ids, evidence_ids) for kind in REQUIRED_IMPACT_TYPES]
    dependency_order = [
        'validate_process_model_impact_proposal_v1',
        'validate_requirement_formalization_candidate_packet_v1',
        'load_existing_guardrail_bundle_fixtures',
        'review_guardrail_bundle_impact_rows',
        'defer_compile_or_promotion_to_later_human_review',
    ]
    basis = {
        'generated_at': generated_at,
        'reviewer_owner': reviewer_owner,
        'bundle_ids': bundle_ids,
        'process_ids': process_ids,
        'requirement_ids': requirement_ids,
        'rows': rows,
    }
    packet = {
        'packet_type': PACKET_TYPE,
        'packet_id': 'guardrail-bundle-impact-proposal-v1-' + _stable_hash(basis),
        'packet_mode': PACKET_MODE,
        'generated_at': generated_at,
        'review_status': 'draft_requires_human_review',
        'reviewer_owner': reviewer_owner,
        'input_packet_refs': {
            'process_model_impact_proposal_id': str(process_model_impact_proposal.get('proposal_id', '')),
            'requirement_formalization_packet_version': str(requirement_formalization_packet.get('packet_version', '')),
            'guardrail_bundle_fixture_ids': bundle_ids,
        },
        'affected_guardrail_bundle_ids': bundle_ids,
        'affected_process_ids': process_ids,
        'affected_requirement_ids': requirement_ids,
        'dependency_order': dependency_order,
        'impact_rows': rows,
        'rollback_note': 'Discard this proposal packet and keep existing guardrail bundle fixtures unchanged if reviewer approval or citation continuity is missing.',
        'offline_validation_commands': [
            ['python3', '-m', 'pytest', 'ppd/tests/test_fixture_first_guardrail_bundle_impact_proposal_v1.py'],
            ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
        ],
        'no_active_mutation_attestations': {
            'fixture_first': True,
            'proposal_only': True,
            'mutated_active_guardrail_bundle': False,
            'compiled_guardrail_bundle': False,
            'promoted_guardrail_bundle': False,
            'mutated_active_prompt': False,
            'mutated_active_process_model': False,
            'mutated_active_requirement': False,
            'mutated_release_state': False,
            'mutated_agent_state': False,
        },
    }
    require_valid_guardrail_bundle_impact_proposal_v1(packet)
    return packet


def validate_guardrail_bundle_impact_proposal_v1(packet: Mapping[str, Any]) -> list[GuardrailBundleImpactProposalFinding]:
    if not isinstance(packet, Mapping):
        return [GuardrailBundleImpactProposalFinding('invalid_packet', '$', 'packet must be an object')]

    findings: list[GuardrailBundleImpactProposalFinding] = []
    if packet.get('packet_type') != PACKET_TYPE:
        findings.append(GuardrailBundleImpactProposalFinding('invalid_packet_type', '$.packet_type', 'unexpected packet type'))
    if packet.get('packet_mode') != PACKET_MODE:
        findings.append(GuardrailBundleImpactProposalFinding('invalid_packet_mode', '$.packet_mode', 'packet must remain proposal-only'))
    if not _non_empty_text(packet.get('reviewer_owner')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_reviewer_owner', '$.reviewer_owner', 'reviewer owner is required'))
    if not _non_empty_text(packet.get('rollback_note')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_rollback_note', '$.rollback_note', 'rollback note is required'))
    if not _non_empty_sequence(packet.get('affected_guardrail_bundle_ids')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_affected_guardrail_bundle_ids', '$.affected_guardrail_bundle_ids', 'affected guardrail bundle IDs are required'))
    if not _non_empty_sequence(packet.get('dependency_order')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_dependency_order', '$.dependency_order', 'dependency order is required'))
    _validate_offline_commands(packet.get('offline_validation_commands'), findings)
    _validate_attestations(packet.get('no_active_mutation_attestations'), findings)
    _validate_rows(packet.get('impact_rows'), findings)
    _reject_prohibited_content(packet, '$', findings)
    return findings


def require_valid_guardrail_bundle_impact_proposal_v1(packet: Mapping[str, Any]) -> None:
    findings = validate_guardrail_bundle_impact_proposal_v1(packet)
    if findings:
        detail = '; '.join(f'{finding.code} at {finding.path}: {finding.message}' for finding in findings)
        raise GuardrailBundleImpactProposalError('invalid guardrail bundle impact proposal v1: ' + detail)


def finding_codes(findings: Sequence[GuardrailBundleImpactProposalFinding]) -> set[str]:
    return {finding.code for finding in findings}


def _impact_row(kind: str, bundle_ids: Sequence[str], process_ids: Sequence[str], requirement_ids: Sequence[str], evidence_ids: Sequence[str]) -> dict[str, Any]:
    return {
        'row_id': 'gbip-v1-row-' + kind.replace('_', '-'),
        'impact_type': kind,
        'affected_guardrail_bundle_ids': list(bundle_ids),
        'affected_process_ids': list(process_ids),
        'affected_requirement_ids': list(requirement_ids),
        'proposed_change': 'Record a cited candidate ' + kind.replace('_', ' ') + ' impact for reviewer assessment only.',
        'citations': [{'source_evidence_id': source_id, 'quote': ''} for source_id in evidence_ids],
        'source_evidence_ids': list(evidence_ids),
        'activation_allowed': False,
    }


def _validate_rows(rows: Any, findings: list[GuardrailBundleImpactProposalFinding]) -> None:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        findings.append(GuardrailBundleImpactProposalFinding('missing_impact_rows', '$.impact_rows', 'impact rows are required'))
        return
    observed: set[str] = set()
    for index, row in enumerate(rows):
        path = f'$.impact_rows[{index}]'
        if not isinstance(row, Mapping):
            findings.append(GuardrailBundleImpactProposalFinding('impact_row_not_mapping', path, 'impact row must be an object'))
            continue
        kind = str(row.get('impact_type', ''))
        observed.add(kind)
        if kind not in REQUIRED_IMPACT_TYPES:
            findings.append(GuardrailBundleImpactProposalFinding('unknown_impact_type', path + '.impact_type', 'impact type is not part of v1'))
        for field, code in (
            ('affected_guardrail_bundle_ids', 'missing_row_guardrail_bundle_ids'),
            ('affected_process_ids', 'missing_row_process_ids'),
            ('affected_requirement_ids', 'missing_row_requirement_ids'),
        ):
            if not _non_empty_sequence(row.get(field)):
                findings.append(GuardrailBundleImpactProposalFinding(code, path + '.' + field, 'row is missing required links'))
        if not _non_empty_sequence(row.get('citations')) or not _non_empty_sequence(row.get('source_evidence_ids')):
            findings.append(GuardrailBundleImpactProposalFinding('uncited_impact_row', path, 'row must include citations and source evidence IDs'))
        if row.get('activation_allowed') is not False:
            findings.append(GuardrailBundleImpactProposalFinding('activation_not_blocked', path + '.activation_allowed', 'impact rows must not allow activation'))
    missing = sorted(set(REQUIRED_IMPACT_TYPES) - observed)
    if missing:
        findings.append(GuardrailBundleImpactProposalFinding('missing_required_impact_types', '$.impact_rows', 'missing impact types: ' + ', '.join(missing)))


def _validate_attestations(attestations: Any, findings: list[GuardrailBundleImpactProposalFinding]) -> None:
    if not isinstance(attestations, Mapping):
        findings.append(GuardrailBundleImpactProposalFinding('missing_mutation_attestations', '$.no_active_mutation_attestations', 'mutation attestations are required'))
        return
    for key in FALSE_ATTESTATIONS:
        if attestations.get(key) is not False:
            findings.append(GuardrailBundleImpactProposalFinding('attestation_not_false', '$.no_active_mutation_attestations.' + key, 'active mutation flags must be false'))
    if attestations.get('fixture_first') is not True or attestations.get('proposal_only') is not True:
        findings.append(GuardrailBundleImpactProposalFinding('missing_fixture_first_attestation', '$.no_active_mutation_attestations', 'fixture-first proposal-only attestations are required'))


def _validate_offline_commands(commands: Any, findings: list[GuardrailBundleImpactProposalFinding]) -> None:
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes)) or not commands:
        findings.append(GuardrailBundleImpactProposalFinding('missing_offline_validation_commands', '$.offline_validation_commands', 'offline validation commands are required'))
        return
    for index, command in enumerate(commands):
        path = f'$.offline_validation_commands[{index}]'
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes)) or not command:
            findings.append(GuardrailBundleImpactProposalFinding('invalid_offline_validation_command', path, 'command must be an argv list'))
            continue
        text = ' '.join(str(part).lower() for part in command)
        if any(term in text for term in ('curl', 'wget', 'playwright', 'devhub.portlandoregon.gov')):
            findings.append(GuardrailBundleImpactProposalFinding('non_offline_validation_command', path, 'validation command must remain offline'))


def _reject_prohibited_content(value: Any, path: str, findings: list[GuardrailBundleImpactProposalFinding]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = path + '.' + str(key)
            if str(key) in PROHIBITED_KEYS:
                findings.append(GuardrailBundleImpactProposalFinding('active_mutation_output', child_path, 'packet must not include active mutation outputs'))
            _reject_prohibited_content(child, child_path, findings)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _reject_prohibited_content(child, f'{path}[{index}]', findings)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in PROHIBITED_TEXT):
            findings.append(GuardrailBundleImpactProposalFinding('private_or_raw_artifact_reference', path, 'packet must not reference private, browser, session, raw crawl, or downloaded artifacts'))


def _bundle_id(fixture: Mapping[str, Any]) -> str:
    for key in ('guardrail_bundle_id', 'bundle_id', 'fixture_id', 'id'):
        value = fixture.get(key)
        if _non_empty_text(value):
            return str(value)
    raise GuardrailBundleImpactProposalError('guardrail fixture is missing a bundle ID')


def _process_ids(process_packet: Mapping[str, Any]) -> list[str]:
    ids: set[str] = set()
    for row in _mapping_rows(process_packet.get('impact_rows')):
        ids.update(str(item) for item in row.get('affected_process_ids', []) if _non_empty_text(item))
    return sorted(ids)


def _requirement_ids(process_packet: Mapping[str, Any], requirement_packet: Mapping[str, Any]) -> list[str]:
    ids: set[str] = set()
    for row in _mapping_rows(process_packet.get('impact_rows')):
        ids.update(str(item) for item in row.get('affected_requirement_ids', []) if _non_empty_text(item))
    for row in _mapping_rows(requirement_packet.get('candidate_rows')):
        value = row.get('affected_requirement_id')
        if _non_empty_text(value):
            ids.add(str(value))
    return sorted(ids)


def _evidence_ids(process_packet: Mapping[str, Any], requirement_packet: Mapping[str, Any], fixtures: Sequence[Mapping[str, Any]]) -> list[str]:
    ids: set[str] = set()
    for row in _mapping_rows(process_packet.get('impact_rows')):
        ids.update(str(item) for item in row.get('citations', []) if _non_empty_text(item))
    for row in _mapping_rows(requirement_packet.get('candidate_rows')):
        for citation in _mapping_rows(row.get('citations')):
            for key in ('source_id', 'document_id', 'locator'):
                value = citation.get(key)
                if _non_empty_text(value):
                    ids.add(str(value))
    for fixture in fixtures:
        archive = fixture.get('source_archive')
        if isinstance(archive, Mapping):
            for key in ('agency', 'requirement_set', 'archived_as_of'):
                value = archive.get(key)
                if _non_empty_text(value):
                    ids.add('guardrail-fixture:' + str(value).replace(' ', '_'))
    return sorted(ids)


def _mapping_rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) > 0


def _stable_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()[:16]
