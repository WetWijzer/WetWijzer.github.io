'''Validation for commit-safe DevHub recorder surface-state packets.

The recorder may describe a DevHub surface, but committed packets must not
contain browser/session artifacts, private authenticated values, raw page dumps,
or claims that consequential actions were automated.
'''

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


MIN_SELECTOR_CONFIDENCE = 0.75

_FORBIDDEN_KEY_TOKENS = (
    'browser_state',
    'storage_state',
    'local_storage',
    'session_storage',
    'cookie',
    'cookies',
    'credential',
    'credentials',
    'password',
    'passwd',
    'secret',
    'token',
    'access_token',
    'refresh_token',
    'id_token',
    'authorization',
    'auth_header',
    'screenshot',
    'screenshots',
    'trace',
    'traces',
    'har',
    'har_data',
)

_PRIVATE_FIELD_KEY_TOKENS = (
    'applicant',
    'owner',
    'email',
    'phone',
    'address',
    'ssn',
    'ein',
    'tax_id',
    'license',
    'payment',
    'card',
    'routing',
    'account_number',
    'permit_number',
    'application_number',
    'case_number',
    'ivr',
)

_PRIVATE_VALUE_KEYS = {
    'value',
    'raw_value',
    'current_value',
    'input_value',
    'private_value',
    'selected_option',
    'sample_file_name',
}

_PRIVATE_DESCRIPTOR_KEYS = {
    'name',
    'field_id',
    'label',
    'label_text',
    'label_id',
    'accessible_name',
    'control_id',
    'message_id',
    'linked_label_id',
}

_RAW_TEXT_KEYS = (
    'raw_text',
    'raw_authenticated_text',
    'authenticated_text',
    'body_text',
    'inner_text',
    'page_text',
    'text_dump',
    'raw_dump',
    'html_dump',
    'dom_dump',
)

_FORBIDDEN_AUTOMATION_ACTIONS = (
    'login',
    'log in',
    'sign in',
    'signin',
    'mfa',
    'multi factor',
    'multifactor',
    'captcha',
    'upload',
    'submit',
    'submission',
    'payment',
    'pay fee',
    'paid',
    'cancellation',
    'cancel',
    'cancelled',
    'scheduling',
    'schedule',
    'scheduled',
)

_AUTOMATION_CLAIM_TERMS = (
    'automated',
    'auto completed',
    'completed by agent',
    'performed by agent',
    'clicked by agent',
    'filled by agent',
    'executed by agent',
    'without user',
    'unattended',
)

_REDACTED_TEXT_VALUES = {
    '',
    '[redacted]',
    'redacted',
    '***',
    '[private]',
    '[private redacted]',
    '[redacted_private_value]',
}

_ALLOWED_URL_HOSTS = {
    'devhub.portlandoregon.gov',
    'www.portland.gov',
    'www.portlandoregon.gov',
    'www.portlandmaps.com',
}


@dataclass(frozen=True)
class SurfaceStatePacketValidationResult:
    '''Result returned by validate_surface_state_packet.'''

    accepted: bool
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.accepted

    def as_dict(self) -> dict[str, Any]:
        return {'accepted': self.accepted, 'ok': self.accepted, 'errors': list(self.errors)}


SurfaceStatePacketValidation = SurfaceStatePacketValidationResult


def validate_surface_state_packet(packet: Mapping[str, Any]) -> SurfaceStatePacketValidationResult:
    '''Validate that a DevHub recorder packet is safe to commit.'''

    if not isinstance(packet, Mapping):
        return SurfaceStatePacketValidationResult(False, ('packet must be a mapping',))

    errors: list[str] = []

    if not _has_redaction_policy(_first_present(packet, ('redaction_policy', 'privacy.redaction_policy'))):
        errors.append('redaction_policy is required and must be non-empty')

    url_pattern = _first_present(packet, ('url_pattern', 'surface.url_pattern'))
    if not _is_actionable_url_pattern(url_pattern):
        errors.append('url_pattern must be a concrete HTTPS DevHub or Portland public URL pattern')

    for path, key, value in _walk_mapping(packet):
        if _path_is_under_redaction_policy(path):
            continue

        normalized_key = _normalize_key(key)

        if _matches_any_token(normalized_key, _FORBIDDEN_KEY_TOKENS):
            if value is not False:
                errors.append(f'{path} is forbidden browser/session/authentication artifact data')
            continue

        if _matches_any_token(normalized_key, _RAW_TEXT_KEYS):
            errors.append(f'{path} is a forbidden raw authenticated text or DOM dump')
            continue

        if _matches_any_token(normalized_key, _PRIVATE_FIELD_KEY_TOKENS) and not _is_redacted_value(value):
            errors.append(f'{path} contains an unredacted private field value')

        if normalized_key in {'selector_confidence', 'confidence'} and not _has_selector_confidence(value):
            errors.append(f'{path} must be at least {MIN_SELECTOR_CONFIDENCE}')

        if _contains_forbidden_automation_claim(value):
            errors.append(f'{path} claims a prohibited DevHub action was automated')

    errors.extend(_private_value_violations(packet))
    return SurfaceStatePacketValidationResult(len(errors) == 0, tuple(dict.fromkeys(errors)))


def validate_surface_state_packet_file(path: str | Path) -> SurfaceStatePacketValidationResult:
    with Path(path).open(encoding='utf-8') as packet_file:
        data = json.load(packet_file)
    if not isinstance(data, Mapping):
        return SurfaceStatePacketValidationResult(False, ('packet must be a mapping',))
    return validate_surface_state_packet(data)


def assert_valid_surface_state_packet(packet: Mapping[str, Any]) -> None:
    '''Raise ValueError when a packet is not commit-safe.'''

    result = validate_surface_state_packet(packet)
    if not result.accepted:
        raise ValueError('invalid DevHub surface-state packet: ' + '; '.join(result.errors))


def _first_present(packet: Mapping[str, Any], dotted_paths: Iterable[str]) -> Any:
    for dotted_path in dotted_paths:
        current: Any = packet
        found = True
        for part in dotted_path.split('.'):
            if not isinstance(current, Mapping) or part not in current:
                found = False
                break
            current = current[part]
        if found:
            return current
    return None


def _has_redaction_policy(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, (list, tuple, set)):
        return bool(value)
    return False


def _has_selector_confidence(value: Any) -> bool:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return False
    return numeric_value >= MIN_SELECTOR_CONFIDENCE


def _is_actionable_url_pattern(value: Any) -> bool:
    if not isinstance(value, str):
        return False

    pattern = value.strip()
    if not pattern or pattern.lower() in {'*', '.*', 'http*', 'https*', 'about:blank'}:
        return False

    parsed = urlparse(pattern.replace('*', ''))
    return parsed.scheme == 'https' and parsed.hostname in _ALLOWED_URL_HOSTS and bool(parsed.path)


def _walk_mapping(value: Any, path: str = '$') -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f'{path}.{key_text}'
            yield child_path, key_text, child
            yield from _walk_mapping(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_mapping(child, f'{path}[{index}]')


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace('-', '_').replace(' ', '_')


def _normalize_text(value: Any) -> str:
    return ' '.join(str(value).lower().replace('_', ' ').replace('-', ' ').split())


def _matches_any_token(normalized_key: str, tokens: Iterable[str]) -> bool:
    return any(token == normalized_key or token in normalized_key for token in tokens)


def _is_redacted_value(value: Any) -> bool:
    if isinstance(value, Mapping):
        return all(_is_redacted_value(child) for child in value.values())
    if isinstance(value, list):
        return all(_is_redacted_value(child) for child in value)
    if isinstance(value, str):
        return value.strip().lower() in _REDACTED_TEXT_VALUES
    return value is None


def _contains_forbidden_automation_claim(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_contains_forbidden_automation_claim(child) for child in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_automation_claim(child) for child in value)
    if not isinstance(value, str):
        return False

    text = _normalize_text(value)
    has_forbidden_action = any(action in text for action in _FORBIDDEN_AUTOMATION_ACTIONS)
    has_automation_claim = any(term in text for term in _AUTOMATION_CLAIM_TERMS)
    return has_forbidden_action and has_automation_claim


def _path_is_under_redaction_policy(path: str) -> bool:
    return '.redaction_policy.' in path or path.endswith('.redaction_policy')


def _private_value_violations(value: Any, path: str = '$') -> list[str]:
    violations: list[str] = []
    if isinstance(value, Mapping):
        descriptor_text = ' '.join(
            _normalize_text(child)
            for key, child in value.items()
            if _normalize_key(str(key)) in _PRIVATE_DESCRIPTOR_KEYS and isinstance(child, str)
        )
        describes_private_field = any(token.replace('_', ' ') in descriptor_text for token in _PRIVATE_FIELD_KEY_TOKENS)
        if describes_private_field:
            for key, child in value.items():
                normalized_key = _normalize_key(str(key))
                if normalized_key in _PRIVATE_VALUE_KEYS and not _is_redacted_value(child):
                    violations.append(f'{path}.{key} contains an unredacted private field value')

        for key, child in value.items():
            violations.extend(_private_value_violations(child, f'{path}.{key}'))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            violations.extend(_private_value_violations(child, f'{path}[{index}]'))
    return violations


__all__ = [
    'MIN_SELECTOR_CONFIDENCE',
    'SurfaceStatePacketValidation',
    'SurfaceStatePacketValidationResult',
    'assert_valid_surface_state_packet',
    'validate_surface_state_packet',
    'validate_surface_state_packet_file',
]
