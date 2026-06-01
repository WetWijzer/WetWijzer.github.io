'''Fixture-first post-candidate monitoring outcome packet v1 validation.'''

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any

PACKET_TYPE = 'ppd.post_candidate_monitoring_outcome_packet.v1'
MONITORING_PLAN_PACKET_TYPE = 'ppd.post_candidate_public_refresh_monitoring_plan.v1'
VALIDATION_COMMANDS = [['python3', 'ppd/daemon/ppd_daemon.py', '--self-test']]
_ALLOWED_OUTCOMES = {'pass', 'hold', 'reject'}
_REQUIRED_OUTCOMES = {'pass', 'hold', 'reject'}
_ALLOWED_STALE_SOURCE_REASONS = {
    'changed_required_guidance',
    'fixture_age_exceeds_threshold',
    'linked_reference_gap',
    'missing_required_source',
    'missing_linked_reference',
    'source_hash_changed',
    'source_not_observed_in_fixture',
}

_PRIVATE_FIELD_RE = re.compile(
    r'(auth|browser|cookie|credential|download|har|private|raw|screenshot|session|storage_state|token|trace|warc)',
    re.IGNORECASE,
)
_PRIVATE_TEXT_RE = re.compile(
    r'(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|'
    r'(auth[_ -]?state|browser[_ -]?(profile|state)|cookie|credential|downloaded?[_ -]?(document|file|pdf)|'
    r'har\b|private[_ -]?(file|path|value)|raw[_ -]?(body|capture|crawl|data|download|html|pdf)|'
    r'screenshot|session[_ -]?(state|storage)|storage[_ -]?state|token|trace|warc)',
    re.IGNORECASE,
)
_LIVE_TEXT_RE = re.compile(
    r'\b(live\s+(crawl|crawler|devhub|browser|fetch|monitor|run)|ran\s+(crawl|crawler|devhub|browser|fetch|monitor)|'
    r'opened\s+(devhub|a browser)|accessed\s+devhub|logged\s+in\s+to\s+devhub|clicked\s+devhub|downloaded\s+(a\s+)?document)\b',
    re.IGNORECASE,
)
_OFFICIAL_ACTION_TEXT_RE = re.compile(
    r'\b(official action|submission|upload|certification|payment|inspection scheduling|cancellation)\s+'
    r'(completed|complete|done|performed|executed|submitted|uploaded|certified|paid|scheduled|cancelled)\b|'
    r'\b(completed|performed|executed)\s+(an\s+)?official action\b',
    re.IGNORECASE,
)
_OFFICIAL_ACTION_FIELD_RE = re.compile(
    r'(official.*(complete|completed|performed|executed)|performs_official_actions|submission_completed|upload_completed|payment_completed|inspection_scheduled|certification_completed|cancellation_completed)',
    re.IGNORECASE,
)
_SCHEDULER_FIELD_RE = re.compile(
    r'(scheduler|schedule|cron|job|timer).*(mutation|mutating|update|write|enable|activation|active|change)|'
    r'(mutates|updates|writes|enables|activates|changes).*(scheduler|schedule|cron|job|timer)',
    re.IGNORECASE,
)
_SCHEDULER_TEXT_RE = re.compile(
    r'\b(mutates?|updates?|writes?|enables?|activates?|changes?)\s+(scheduler|schedule|cron|job|timer|scheduler state|schedule state)\b',
    re.IGNORECASE,
)
_ACTIVE_FIELD_RE = re.compile(
    r'(active_)?(source|archive|document|requirement|process|process_model|guardrail|prompt|release|crawler|daemon|scheduler|monitoring).*(mutation|mutating|update|write|promotion|refresh|state)|'
    r'(mutates|updates|promotes|refreshes|writes).*(sources|archives|documents|requirements|processes|guardrails|prompts|releases|crawlers|daemons|monitoring)',
    re.IGNORECASE,
)
_ACTIVE_TEXT_RE = re.compile(
    r'\b(mutates?|updates?|writes?|promotes?|refreshes?|enables?|activates?)\s+(active\s+)?(source|archive|document|requirement|process|process-model|guardrail|prompt|release|crawler|daemon|scheduler|schedule|monitoring)\b',
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PostCandidateMonitoringOutcomePacketV1Result:
    ready: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {'ready': self.ready, 'problems': list(self.problems)}


def validate_post_candidate_monitoring_outcome_packet_v1(packet: Mapping[str, Any]) -> PostCandidateMonitoringOutcomePacketV1Result:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return PostCandidateMonitoringOutcomePacketV1Result(False, ('packet must be an object',))

    if packet.get('packet_type') != PACKET_TYPE:
        problems.append(f'packet_type must be {PACKET_TYPE}')
    if packet.get('validation_commands') != VALIDATION_COMMANDS:
        problems.append('validation_commands must contain only the exact PP&D daemon self-test command')

    plan_ref = packet.get('monitoring_plan_ref')
    plan_packet_id = ''
    if not isinstance(plan_ref, Mapping):
        problems.append('monitoring_plan_ref must be an object')
    else:
        if plan_ref.get('packet_type') != MONITORING_PLAN_PACKET_TYPE:
            problems.append(f'monitoring_plan_ref.packet_type must be {MONITORING_PLAN_PACKET_TYPE}')
        plan_packet_id = _text(plan_ref.get('packet_id'))
        if not plan_packet_id:
            problems.append('monitoring_plan_ref.packet_id must be present')
        if not _text(plan_ref.get('fixture_path')):
            problems.append('monitoring_plan_ref.fixture_path must be present')

    plan_rows = _mapping_sequence(packet.get('synthetic_monitoring_plan_rows'))
    if not plan_rows:
        problems.append('synthetic_monitoring_plan_rows must include synthetic monitoring plan rows')

    plan_check_ids: set[str] = set()
    source_to_checks: dict[str, set[str]] = {}
    for index, row in enumerate(plan_rows):
        path = f'synthetic_monitoring_plan_rows[{index}]'
        check_id = _text(row.get('check_id'))
        if not check_id:
            problems.append(f'{path} lacks check_id')
        else:
            plan_check_ids.add(check_id)
        source_ids = _text_list(row.get('source_evidence_ids'))
        if not source_ids:
            problems.append(f'{path} lacks source_evidence_ids')
        if not _nonempty_mapping(row.get('hold_thresholds')):
            problems.append(f'{path} lacks hold_thresholds')
        if not _has_reviewer_routing(row):
            problems.append(f'{path} lacks reviewer routing')
        for source_id in source_ids:
            source_to_checks.setdefault(source_id, set()).add(check_id)

    outcomes = _mapping_sequence(packet.get('per_anchor_outcomes'))
    if not outcomes:
        problems.append('per_anchor_outcomes must include one outcome row for each synthetic monitoring plan source anchor')

    observed_outcomes: set[str] = set()
    observed_sources: set[str] = set()
    for index, row in enumerate(outcomes):
        path = f'per_anchor_outcomes[{index}]'
        source_id = _text(row.get('source_evidence_id'))
        check_id = _text(row.get('check_id'))
        outcome = _text(row.get('outcome')).lower()
        if not source_id:
            problems.append(f'{path} lacks source_evidence_id')
        elif source_to_checks and source_id not in source_to_checks:
            problems.append(f'{path} references source_evidence_id outside synthetic monitoring plan rows: {source_id}')
        else:
            observed_sources.add(source_id)
        if not check_id:
            problems.append(f'{path} lacks check_id')
        elif plan_check_ids and check_id not in plan_check_ids:
            problems.append(f'{path} references check_id outside synthetic monitoring plan rows: {check_id}')
        elif source_id and source_to_checks and check_id not in source_to_checks.get(source_id, set()):
            problems.append(f'{path} pairs source_evidence_id with a check_id outside its synthetic monitoring plan row')
        if outcome not in _ALLOWED_OUTCOMES:
            problems.append(f'{path} outcome must be one of pass, hold, reject')
        else:
            observed_outcomes.add(outcome)
        reasons = _text_list(row.get('stale_source_reasons'))
        if outcome in {'hold', 'reject'} and not reasons:
            problems.append(f'{path} hold or reject outcome requires stale_source_reasons')
        for reason in reasons:
            if reason not in _ALLOWED_STALE_SOURCE_REASONS:
                problems.append(f'{path} unsupported stale_source_reason: {reason}')
        if not _has_reviewer_routing(row):
            problems.append(f'{path} lacks reviewer routing')
        dependency_refs = _text_list(row.get('dependency_refs'))
        if not dependency_refs:
            problems.append(f'{path} lacks dependency_refs')
        else:
            if plan_packet_id and plan_packet_id not in dependency_refs:
                problems.append(f'{path} dependency_refs must include monitoring plan packet_id')
            if source_id and source_id not in dependency_refs:
                problems.append(f'{path} dependency_refs must include source_evidence_id')

    for source_id in sorted(set(source_to_checks) - observed_sources):
        problems.append(f'missing per-anchor outcome row for source_evidence_id: {source_id}')
    for outcome in sorted(_REQUIRED_OUTCOMES - observed_outcomes):
        problems.append(f'missing per-anchor {outcome} outcome')

    if not _has_reviewer_routing(packet):
        problems.append('packet lacks reviewer routing')

    dependency_refs = _text_list(packet.get('dependency_refs'))
    if not dependency_refs:
        problems.append('packet lacks dependency_refs')
    elif plan_packet_id and plan_packet_id not in dependency_refs:
        problems.append('packet dependency_refs must include monitoring plan packet_id')

    problems.extend(_safety_problems(packet))
    return PostCandidateMonitoringOutcomePacketV1Result(ready=not problems, problems=tuple(problems))


def require_post_candidate_monitoring_outcome_packet_v1(packet: Mapping[str, Any]) -> None:
    result = validate_post_candidate_monitoring_outcome_packet_v1(packet)
    if not result.ready:
        raise ValueError('invalid_post_candidate_monitoring_outcome_packet_v1: ' + '; '.join(result.problems))


def _safety_problems(value: Any, path: str = '$') -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f'{path}.{key}'
            key_text = str(key)
            if _PRIVATE_FIELD_RE.search(key_text) and child not in (None, False, '', [], {}):
                problems.append(f'private, live, raw, browser, or downloaded artifact field is not allowed at {child_path}')
            if _OFFICIAL_ACTION_FIELD_RE.search(key_text) and child is True:
                problems.append(f'official-action completion claim is not allowed at {child_path}')
            if _SCHEDULER_FIELD_RE.search(key_text) and child not in (None, False, '', [], {}):
                problems.append(f'scheduler-state mutation claim is not allowed at {child_path}')
            if _ACTIVE_FIELD_RE.search(key_text) and child is True:
                problems.append(f'active PP&D state mutation flag is not allowed at {child_path}')
            problems.extend(_safety_problems(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            problems.extend(_safety_problems(item, f'{path}[{index}]'))
    elif isinstance(value, str):
        if _PRIVATE_TEXT_RE.search(value):
            problems.append(f'private, live, raw, browser, or downloaded artifact text is not allowed at {path}')
        if _LIVE_TEXT_RE.search(value):
            problems.append(f'live crawl or DevHub claim is not allowed at {path}')
        if _OFFICIAL_ACTION_TEXT_RE.search(value):
            problems.append(f'official-action completion claim is not allowed at {path}')
        if _SCHEDULER_TEXT_RE.search(value):
            problems.append(f'scheduler-state mutation claim is not allowed at {path}')
        if _ACTIVE_TEXT_RE.search(value):
            problems.append(f'active PP&D state mutation claim is not allowed at {path}')
    return problems


def _has_reviewer_routing(value: Mapping[str, Any]) -> bool:
    routing = value.get('reviewer_routing') or value.get('reviewer_route') or value.get('reviewer_owner')
    if isinstance(routing, str):
        return bool(routing.strip())
    if isinstance(routing, Mapping):
        return any(_text(routing.get(key)) for key in ('primary_reviewer', 'reviewer_owner', 'escalation_reviewer', 'route_id'))
    if isinstance(routing, Sequence) and not isinstance(routing, (str, bytes, bytearray)):
        return any(item not in (None, False, '', [], {}) for item in routing)
    return False


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _nonempty_mapping(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value)


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ''
