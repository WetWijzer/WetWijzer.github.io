"""Fixture-first post-run triage packet v2 for PP&D live dry-runs.

This module consumes committed fixture envelopes and produces cited triage
records only. It does not repeat a live run, open DevHub, read auth state,
inspect browser artifacts, perform official actions, or mutate release state.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


PACKET_TYPE = 'live-dry-run-post-run-triage-packet'
PACKET_VERSION = 'v2'
MODE = 'fixture_first_live_dry_run_post_run_triage_only'

REQUIRED_SOURCE_KEYS = (
    'public_recrawl_dry_run_evidence_envelope_v2',
    'attended_devhub_read_only_evidence_envelope_v2',
    'live_dry_run_operator_briefing_packet_v2',
)

REQUIRED_DECISIONS = frozenset({'accepted', 'deferred', 'escalated'})
REQUIRED_ATTESTATIONS = (
    'no_live_repeat',
    'no_auth_state',
    'no_browser_artifact',
    'no_official_action',
    'no_release_state_mutation',
)
_ALLOWED_COMMANDS = (
    ('python3', 'ppd/daemon/ppd_daemon.py', '--self-test'),
    ('python3', '-m', 'py_compile', 'ppd/live_dry_run_post_run_triage_packet_v2.py'),
)

_PRIVATE_OR_AUTH_KEYS = frozenset({
    'account', 'account_id', 'address', 'auth_state', 'authorization', 'cookie', 'cookies',
    'credential', 'credentials', 'email', 'invoice', 'license', 'name', 'password',
    'payment_detail', 'permit_number', 'phone', 'private_fact', 'private_value',
    'raw_authenticated_text', 'raw_authenticated_value', 'secret', 'session_state',
    'storage_state', 'token', 'user',
})
_ARTIFACT_KEYS = frozenset({
    'archive_path', 'browser_artifact', 'browser_profile', 'download_path', 'downloaded_document',
    'har', 'har_file', 'raw_body', 'raw_crawl_output', 'raw_pdf', 'screenshot',
    'screenshot_path', 'session_file', 'trace', 'trace_path',
})
_MUTATION_FLAGS = frozenset({
    'active_agent_state_mutation', 'active_guardrail_mutation', 'active_monitoring_mutation',
    'active_prompt_mutation', 'active_release_state_mutation', 'active_source_mutation',
    'active_surface_registry_mutation', 'agent_state_mutation', 'guardrail_mutation',
    'monitoring_mutation', 'mutates_agent_state', 'mutates_guardrails', 'mutates_monitoring',
    'mutates_prompts', 'mutates_release_state', 'mutates_source_registry',
    'mutates_surface_registry', 'prompt_mutation', 'release_state_mutation',
    'source_registry_mutation', 'surface_registry_mutation',
})
_SAFE_FALSE_KEYS = frozenset({
    'auth_state_created', 'browser_artifact_created', 'document_downloaded', 'live_repeat_performed',
    'official_action_performed', 'processor_invoked', 'raw_body_persisted',
    'release_state_mutated', 'source_registry_mutated',
})
_SAFE_TRUE_ATTESTATIONS = frozenset({
    'no_auth_state', 'no_browser_artifact', 'no_download', 'no_har', 'no_live_crawl',
    'no_live_devhub', 'no_live_execution', 'no_live_repeat', 'no_official_action',
    'no_processor', 'no_raw_body', 'no_release_state_mutation', 'no_screenshot',
    'no_source_registry_mutation', 'no_surface_registry_mutation', 'no_trace',
})


@dataclass(frozen=True)
class TriagePacketValidationResult:
    valid: bool
    errors: tuple[str, ...]


def build_live_dry_run_post_run_triage_packet_v2(source_packets: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic, cited triage packet from fixture source packets."""

    missing = [key for key in REQUIRED_SOURCE_KEYS if key not in source_packets]
    if missing:
        raise ValueError('missing source packets: ' + ', '.join(missing))

    public_envelope = _require_mapping(source_packets['public_recrawl_dry_run_evidence_envelope_v2'], 'public recrawl evidence envelope')
    devhub_envelope = _require_mapping(source_packets['attended_devhub_read_only_evidence_envelope_v2'], 'attended DevHub read-only evidence envelope')
    briefing_packet = _require_mapping(source_packets['live_dry_run_operator_briefing_packet_v2'], 'operator briefing packet')

    observation_decisions = [
        {
            'decision_id': 'accept-public-metadata-only-observations',
            'decision': 'accepted',
            'summary': 'Accept fixture-derived public recrawl metadata-only observations for reviewer triage.',
            'source_observation_refs': _public_slot_refs(public_envelope),
            'citations': _citations(public_envelope, 'public_recrawl_dry_run_evidence_envelope_v2.observation_slots'),
        },
        {
            'decision_id': 'accept-devhub-read-only-observations',
            'decision': 'accepted',
            'summary': 'Accept synthetic attended DevHub read-only observations after redaction checklist review.',
            'source_observation_refs': _devhub_slot_refs(devhub_envelope),
            'citations': _citations(devhub_envelope, 'attended_devhub_read_only_evidence_envelope_v2.observation_slots'),
        },
        {
            'decision_id': 'defer-any-live-repeat',
            'decision': 'deferred',
            'summary': 'Defer any live repeat, authenticated browser replay, or processor run to a separately authorized packet.',
            'source_observation_refs': ['live_dry_run_operator_briefing_packet_v2.independent_stop_conditions'],
            'citations': _citations(briefing_packet, 'live_dry_run_operator_briefing_packet_v2.independent_stop_conditions'),
        },
        {
            'decision_id': 'escalate-boundary-review-to-owner',
            'decision': 'escalated',
            'summary': 'Escalate boundary confirmation and final reviewer-owner acceptance before any downstream promotion decision.',
            'source_observation_refs': ['live_dry_run_operator_briefing_packet_v2.required_human_attendance_checkpoints'],
            'citations': _citations(briefing_packet, 'live_dry_run_operator_briefing_packet_v2.required_human_attendance_checkpoints'),
        },
    ]

    packet = {
        'packet_type': PACKET_TYPE,
        'version': PACKET_VERSION,
        'mode': MODE,
        'packet_id': 'fixture-first-live-dry-run-post-run-triage-packet-v2-20260529',
        'fixture_first': True,
        'consumes': [_consumed_row(key, source_packets[key]) for key in REQUIRED_SOURCE_KEYS],
        'observation_decisions': observation_decisions,
        'incident_summaries': [
            {
                'incident_id': 'incident-summary-no-fixture-incident-reported',
                'status': 'accepted',
                'disposition': 'no_fixture_incident_reported_pending_reviewer_confirmation',
                'summary': 'Fixture inputs report no live incident evidence; retain reviewer confirmation before any repeat run.',
                'citations': _citations(public_envelope, 'public_recrawl_dry_run_evidence_envelope_v2.side_effects')
                + _citations(devhub_envelope, 'attended_devhub_read_only_evidence_envelope_v2.observation_slots.attestations'),
            }
        ],
        'abort_summaries': [
            {
                'abort_id': 'abort-summary-operator-stop-conditions',
                'status': 'escalated_for_reviewer_confirmation',
                'disposition': 'abort_boundaries_remain_required_for_future_runs',
                'summary': 'Operator stop conditions remain binding for any future run; CAPTCHA, MFA, payment, upload, submission, certification, cancellation, auth artifact, or browser artifact prompts require abort.',
                'conditions': _text_list(briefing_packet.get('independent_stop_conditions')),
                'citations': _citations(briefing_packet, 'live_dry_run_operator_briefing_packet_v2.independent_stop_conditions'),
            }
        ],
        'artifact_redaction_review_outcomes': [
            {
                'review_id': 'redaction-public-recrawl-evidence',
                'outcome': 'accepted_metadata_only',
                'summary': 'Public recrawl envelope remains metadata-only with no raw body, download, processor, or source-registry mutation claim.',
                'citations': _citations(public_envelope, 'public_recrawl_dry_run_evidence_envelope_v2.attestations'),
            },
            {
                'review_id': 'redaction-devhub-read-only-evidence',
                'outcome': 'accepted_synthetic_read_only',
                'summary': 'DevHub evidence remains synthetic read-only with no auth state, screenshot, trace, HAR, or surface-registry mutation claim.',
                'citations': _citations(devhub_envelope, 'attended_devhub_read_only_evidence_envelope_v2.observation_slots.redaction_checklist_outcomes'),
            },
            {
                'review_id': 'redaction-operator-briefing',
                'outcome': 'accepted_briefing_only',
                'summary': 'Operator briefing remains derived from fixture packets and does not authorize official actions or release-state mutation.',
                'citations': _citations(briefing_packet, 'live_dry_run_operator_briefing_packet_v2.artifact_redaction_expectations'),
            },
        ],
        'reviewer_owner_fields': {
            'primary_reviewer_owner': 'TBD_PP_D_REVIEWER_OWNER',
            'incident_review_owner': 'TBD_PP_D_INCIDENT_REVIEW_OWNER',
            'artifact_redaction_owner': 'TBD_PP_D_ARTIFACT_REDACTION_OWNER',
            'release_state_owner': 'TBD_PP_D_RELEASE_STATE_OWNER',
            'owner_assignment_status': 'placeholder_required_before_promotion',
            'citations': ['live_dry_run_operator_briefing_packet_v2.required_human_attendance_checkpoints'],
        },
        'offline_validation_commands': [list(command) for command in _ALLOWED_COMMANDS],
        'attestations': {key: True for key in REQUIRED_ATTESTATIONS},
        'side_effects': {
            'live_repeat_performed': False,
            'auth_state_created': False,
            'browser_artifact_created': False,
            'official_action_performed': False,
            'release_state_mutated': False,
        },
        'source_packets': {key: deepcopy(source_packets[key]) for key in REQUIRED_SOURCE_KEYS},
    }
    require_valid_live_dry_run_post_run_triage_packet_v2(packet)
    return packet


def validate_live_dry_run_post_run_triage_packet_v2(packet: Mapping[str, Any]) -> TriagePacketValidationResult:
    errors: list[str] = []
    if packet.get('packet_type') != PACKET_TYPE:
        errors.append('packet_type must be ' + PACKET_TYPE)
    if packet.get('version') != PACKET_VERSION:
        errors.append('version must be v2')
    if packet.get('mode') != MODE:
        errors.append('mode must be ' + MODE)
    if packet.get('fixture_first') is not True:
        errors.append('fixture_first must be true')

    consumed_keys = set(_field_values(packet.get('consumes'), 'source_key'))
    for key in REQUIRED_SOURCE_KEYS:
        if key not in consumed_keys:
            errors.append('consumes missing ' + key)

    _validate_decisions(packet.get('observation_decisions'), errors)
    _validate_review_rows(packet.get('incident_summaries'), 'incident_summaries', True, False, errors)
    _validate_review_rows(packet.get('abort_summaries'), 'abort_summaries', True, False, errors)
    _validate_review_rows(packet.get('artifact_redaction_review_outcomes'), 'artifact_redaction_review_outcomes', False, True, errors)
    _validate_owners(packet.get('reviewer_owner_fields'), errors)
    _validate_commands(packet.get('offline_validation_commands'), errors)
    _validate_attestations(packet.get('attestations'), errors)
    _validate_side_effects(packet.get('side_effects'), errors)
    _scan_unsafe_value(packet, '$', errors)

    return TriagePacketValidationResult(valid=not errors, errors=tuple(dict.fromkeys(errors)))


def require_valid_live_dry_run_post_run_triage_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_live_dry_run_post_run_triage_packet_v2(packet)
    if not result.valid:
        raise ValueError('invalid live dry-run post-run triage packet v2: ' + '; '.join(result.errors))


def _validate_decisions(value: Any, errors: list[str]) -> None:
    decisions = _sequence(value)
    if not decisions:
        errors.append('observation_decisions must be non-empty')
        return
    decision_values: set[str] = set()
    cited_decisions: set[str] = set()
    for index, decision in enumerate(decisions):
        prefix = 'observation_decisions[' + str(index) + ']'
        if not isinstance(decision, Mapping):
            errors.append(prefix + ' must be an object')
            continue
        decision_value = _text(decision.get('decision'))
        decision_values.add(decision_value)
        if decision_value not in REQUIRED_DECISIONS:
            errors.append(prefix + '.decision must be accepted, deferred, or escalated')
        for field_name in ('decision_id', 'summary'):
            if not _text(decision.get(field_name)):
                errors.append(prefix + '.' + field_name + ' is required')
        if not _text_list(decision.get('citations')):
            errors.append(prefix + '.citations must be non-empty')
        elif decision_value in REQUIRED_DECISIONS:
            cited_decisions.add(decision_value)
    missing_decisions = REQUIRED_DECISIONS.difference(decision_values)
    if missing_decisions:
        errors.append('observation_decisions missing statuses: ' + ', '.join(sorted(missing_decisions)))
    uncited_decisions = REQUIRED_DECISIONS.intersection(decision_values).difference(cited_decisions)
    if uncited_decisions:
        errors.append('observation_decisions uncited statuses: ' + ', '.join(sorted(uncited_decisions)))


def _validate_review_rows(value: Any, section: str, require_disposition: bool, require_outcome: bool, errors: list[str]) -> None:
    rows = _sequence(value)
    if not rows:
        errors.append(section + ' must be non-empty')
        return
    for index, row in enumerate(rows):
        prefix = section + '[' + str(index) + ']'
        if not isinstance(row, Mapping):
            errors.append(prefix + ' must be an object')
            continue
        if not _text(row.get('summary')):
            errors.append(prefix + '.summary is required')
        if not _text_list(row.get('citations')):
            errors.append(prefix + '.citations must be non-empty')
        if require_disposition and not any(_text(row.get(name)) for name in ('disposition', 'status', 'outcome')):
            errors.append(prefix + '.disposition or status is required')
        if require_outcome and not _text(row.get('outcome')):
            errors.append(prefix + '.outcome is required')


def _validate_owners(owners: Any, errors: list[str]) -> None:
    if not isinstance(owners, Mapping):
        errors.append('reviewer_owner_fields must be an object')
        return
    for key in ('primary_reviewer_owner', 'incident_review_owner', 'artifact_redaction_owner', 'release_state_owner', 'owner_assignment_status'):
        if not _text(owners.get(key)):
            errors.append('reviewer_owner_fields.' + key + ' is required')
    if not _text_list(owners.get('citations')):
        errors.append('reviewer_owner_fields.citations must be non-empty')


def _validate_commands(value: Any, errors: list[str]) -> None:
    commands = _sequence(value)
    if not commands:
        errors.append('offline_validation_commands must be non-empty')
    for index, command in enumerate(commands):
        if not _argv(command):
            errors.append('offline_validation_commands[' + str(index) + '] must be an argv list')


def _validate_attestations(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append('attestations must be an object')
        return
    for key in REQUIRED_ATTESTATIONS:
        if value.get(key) is not True:
            errors.append('attestations.' + key + ' must be true')


def _validate_side_effects(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append('side_effects must be an object')
        return
    for key in ('live_repeat_performed', 'auth_state_created', 'browser_artifact_created', 'official_action_performed', 'release_state_mutated'):
        if value.get(key) is not False:
            errors.append('side_effects.' + key + ' must be false')


def _scan_unsafe_value(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            child_path = path + '.' + key_text
            if key_lower in _MUTATION_FLAGS and child is True:
                errors.append(child_path + ' must not enable active source, surface-registry, prompt, guardrail, monitoring, release-state, or agent-state mutation')
            if key_lower in _PRIVATE_OR_AUTH_KEYS and child not in (False, None, '') and key_lower not in _SAFE_TRUE_ATTESTATIONS:
                errors.append(child_path + ' must not contain private or authenticated facts')
            if key_lower in _ARTIFACT_KEYS and child not in (False, None, '') and key_lower not in _SAFE_TRUE_ATTESTATIONS:
                errors.append(child_path + ' must not reference raw crawl, PDF, session, or browser artifacts')
            if key_lower in _SAFE_FALSE_KEYS and child is not False:
                errors.append(child_path + ' must remain false')
            if key_lower in _SAFE_TRUE_ATTESTATIONS and child is not True:
                errors.append(child_path + ' must remain true')
            _scan_unsafe_value(child, child_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_unsafe_value(child, path + '[' + str(index) + ']', errors)
    elif isinstance(value, str):
        _scan_unsafe_text(value, path, errors)


def _scan_unsafe_text(value: str, path: str, errors: list[str]) -> None:
    lowered = value.lower()
    safety_context = _safety_context(lowered, path)
    if _contains_any(lowered, ('@', 'password:', 'password=', 'token:', 'token=', 'set-cookie', 'permit number:', 'account number:', 'invoice number:')):
        errors.append(path + ' must not contain private or authenticated facts')
    if _contains_any(lowered, ('private fact', 'private value', 'authenticated value', 'authenticated fact', 'raw authenticated')) and not safety_context:
        errors.append(path + ' must not contain private or authenticated facts')
    if _contains_any(lowered, ('raw crawl output', 'raw pdf', 'raw body', 'downloaded document', 'session file', 'storage state', 'auth state', 'browser artifact', 'screenshot', 'trace.zip', 'har file', '.har')) and not safety_context:
        errors.append(path + ' must not reference raw crawl, PDF, session, or browser artifacts')
    if _contains_any(lowered, ('live execution completed', 'live repeat performed', 'live crawl completed', 'live devhub completed', 'browser automation completed', 'opened live devhub', 'launched live browser')):
        errors.append(path + ' must not claim live execution')
    if _near(lowered, ('automated', 'automate', 'bypass', 'bypassed', 'solve', 'solved', 'entered', 'filled', 'completed'), ('credential', 'password', 'mfa', 'captcha', 'login', 'sign in', 'security prompt', 'one-time code', 'otp')):
        errors.append(path + ' must not contain credential, MFA, or CAPTCHA automation language')
    if _contains_any(lowered, ('approval is guaranteed', 'guaranteed approval', 'permit will be approved', 'permit will issue', 'will be issued', 'will be accepted', 'legal outcome guaranteed', 'permitting outcome guaranteed')):
        errors.append(path + ' must not guarantee legal or permitting outcomes')
    if _contains_any(lowered, ('final submission', 'submitted application', 'submission completed', 'payment completed', 'final payment', 'uploaded to devhub', 'uploaded to official', 'scheduled inspection', 'cancelled permit', 'canceled permit', 'certification completed')) and not safety_context:
        errors.append(path + ' must not contain final submission, payment, upload, scheduling, cancellation, or certification language')
    if _near(lowered, ('mutate', 'mutation', 'write', 'update', 'publish', 'promote', 'activate', 'enable'), ('source registry', 'surface registry', 'prompt', 'guardrail', 'monitoring', 'release state', 'agent state')) and not safety_context:
        errors.append(path + ' must not contain active mutation language')


def _safety_context(lowered: str, path: str) -> bool:
    path_lower = path.lower()
    if 'abort' in path_lower or 'stop_condition' in path_lower or 'redaction' in path_lower or 'attestation' in path_lower or 'artifact_redaction_expectations' in path_lower:
        return True
    return _contains_any(lowered, (' no ', 'no ', 'not ', 'never ', 'without ', 'blocked', 'prohibited', 'must not', 'do not', 'does not', 'absent', 'requires abort', 'require abort', 'stop before'))


def _near(text: str, left_terms: tuple[str, ...], right_terms: tuple[str, ...], window: int = 90) -> bool:
    for left in left_terms:
        start = text.find(left)
        while start != -1:
            fragment = text[max(0, start - window): start + len(left) + window]
            if any(right in fragment for right in right_terms):
                return True
            start = text.find(left, start + 1)
    return False


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _consumed_row(source_key: str, packet: Any) -> dict[str, Any]:
    source_packet = packet if isinstance(packet, Mapping) else {}
    return {
        'source_key': source_key,
        'packet_id': _packet_id(source_packet),
        'packet_type': _text(source_packet.get('packet_type'), _text(source_packet.get('version'), 'fixture')),
        'citations': _citations(source_packet, source_key),
    }


def _packet_id(packet: Mapping[str, Any]) -> str:
    for key in ('packet_id', 'envelope_id', 'ledger_id', 'plan_id', 'id'):
        value = packet.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return 'unknown-fixture-packet'


def _public_slot_refs(envelope: Mapping[str, Any]) -> list[str]:
    refs = []
    for slot in _sequence(envelope.get('observation_slots')):
        if isinstance(slot, Mapping):
            refs.append(_text(slot.get('slot_id'), _text(slot.get('slot_kind'), 'public-observation-slot')))
    return refs or ['public_recrawl_dry_run_evidence_envelope_v2.observation_slots']


def _devhub_slot_refs(envelope: Mapping[str, Any]) -> list[str]:
    slots = envelope.get('observation_slots')
    if isinstance(slots, Mapping):
        return ['attended_devhub_read_only_evidence_envelope_v2.observation_slots.' + str(key) for key in slots]
    return ['attended_devhub_read_only_evidence_envelope_v2.observation_slots']


def _citations(value: Any, fallback: str) -> list[str]:
    if isinstance(value, Mapping):
        for key in ('citations', 'citation_refs', 'source_evidence_ids'):
            citations = _text_list(value.get(key))
            if citations:
                return citations
    return [fallback]


def _field_values(items: Any, field_name: str) -> list[str]:
    values: list[str] = []
    for item in _sequence(items):
        if isinstance(item, Mapping):
            value = item.get(field_name)
            if isinstance(value, str) and value.strip():
                values.append(value.strip())
    return values


def _argv(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(part, str) and part.strip() for part in value)


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(label + ' must be a mapping')
    return value


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _text(value: Any, default: str = '') -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _text_list(value: Any) -> list[str]:
    return [str(item).strip() for item in _sequence(value) if str(item).strip()]


__all__ = [
    'PACKET_TYPE',
    'PACKET_VERSION',
    'REQUIRED_ATTESTATIONS',
    'REQUIRED_DECISIONS',
    'REQUIRED_SOURCE_KEYS',
    'TriagePacketValidationResult',
    'build_live_dry_run_post_run_triage_packet_v2',
    'require_valid_live_dry_run_post_run_triage_packet_v2',
    'validate_live_dry_run_post_run_triage_packet_v2',
]
