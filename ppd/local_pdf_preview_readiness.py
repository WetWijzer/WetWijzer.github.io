"""Fail-closed validation for local PDF preview readiness packets."""

from __future__ import annotations

import base64
from datetime import date, datetime, timezone
from typing import Any, Mapping


class LocalPdfPreviewReadinessError(ValueError):
    """Raised when a local PDF preview readiness packet is unsafe."""


_PRIVATE_KEY_PARTS = (
    'password', 'passwd', 'passphrase', 'token', 'secret', 'api_key', 'apikey',
    'session', 'cookie', 'credential', 'ssn', 'social_security', 'dob',
    'date_of_birth', 'card', 'cvv', 'cvc', 'routing', 'account_number', 'payment',
)
_PDF_BINARY_KEYS = {
    'pdf_bytes', 'pdf_binary', 'binary_pdf', 'pdf_content', 'pdf_base64',
    'content_base64', 'write_pdf', 'write_pdf_binary', 'output_pdf_path', 'local_pdf_path',
}
_COMPLETE_VALUES = {'complete', 'completed', 'ready', 'true', 'yes', 'signed', 'submitted', 'certified'}


def validate_local_pdf_preview_readiness_packet(
    packet: Mapping[str, Any], *, now: date | datetime | None = None, max_evidence_age_days: int = 120
) -> list[str]:
    """Return deterministic rejection reasons for an unsafe readiness packet."""

    if not isinstance(packet, Mapping):
        return ['packet must be an object']

    today = _as_date(now or datetime.now(timezone.utc))
    errors: list[str] = []

    if packet.get('packet_type') != 'local_pdf_preview_readiness':
        errors.append('packet_type must be local_pdf_preview_readiness')
    if packet.get('preview_only') is not True:
        errors.append('preview_only must be true')
    if packet.get('writes_pdf_binary') not in (None, False):
        errors.append('packet must not attempt to write PDF binaries')

    previews = packet.get('previews')
    if not isinstance(previews, list) or not previews:
        errors.append('packet must include at least one local preview')
    else:
        for index, preview in enumerate(previews):
            errors.extend(_preview_errors(preview, index))

    evidence_ids, evidence_errors = _evidence_errors(packet.get('source_evidence'), today, max_evidence_age_days)
    errors.extend(evidence_errors)
    errors.extend(_field_mapping_errors(packet.get('field_mappings'), evidence_ids))
    errors.extend(_blocked_field_errors(packet.get('blocked_fields'), evidence_ids))
    errors.extend(_recursive_safety_errors(packet))

    return sorted(dict.fromkeys(errors))


def require_local_pdf_preview_readiness_packet(
    packet: Mapping[str, Any], *, now: date | datetime | None = None, max_evidence_age_days: int = 120
) -> None:
    errors = validate_local_pdf_preview_readiness_packet(packet, now=now, max_evidence_age_days=max_evidence_age_days)
    if errors:
        raise LocalPdfPreviewReadinessError('; '.join(errors))


def _preview_errors(preview: Any, index: int) -> list[str]:
    if not isinstance(preview, Mapping):
        return [f'previews[{index}] must be an object']
    errors: list[str] = []
    if not preview.get('preview_id'):
        errors.append(f'previews[{index}] is missing preview_id')
    if preview.get('rendered') is not True:
        errors.append(f'previews[{index}] must be rendered')
    if preview.get('metadata_only') is not True:
        errors.append(f'previews[{index}] must be metadata_only')
    if preview.get('contains_pdf_binary') not in (None, False):
        errors.append(f'previews[{index}] must not contain PDF binary data')
    return errors


def _evidence_errors(evidence: Any, today: date, max_age_days: int) -> tuple[set[str], list[str]]:
    if not isinstance(evidence, list) or not evidence:
        return set(), ['source_evidence must include at least one cited item']

    ids: set[str] = set()
    errors: list[str] = []
    for index, item in enumerate(evidence):
        if not isinstance(item, Mapping):
            errors.append(f'source_evidence[{index}] must be an object')
            continue
        evidence_id = item.get('evidence_id')
        if not isinstance(evidence_id, str) or not evidence_id:
            errors.append(f'source_evidence[{index}] is missing evidence_id')
        elif evidence_id in ids:
            errors.append(f'duplicate evidence_id: {evidence_id}')
        else:
            ids.add(evidence_id)
        url = item.get('url')
        if not isinstance(url, str) or not url.startswith('https://www.portland.gov/'):
            errors.append(f'source_evidence[{index}] must cite a Portland public URL')
        observed_on = _parse_date(item.get('observed_on') or item.get('checked_on'))
        if observed_on is None:
            errors.append(f'source_evidence[{index}] must include observed_on')
        elif (today - observed_on).days > max_age_days:
            errors.append(f'source_evidence[{index}] is stale')
    return ids, errors


def _field_mapping_errors(mappings: Any, evidence_ids: set[str]) -> list[str]:
    if not isinstance(mappings, list) or not mappings:
        return ['field_mappings must include at least one cited mapping']

    errors: list[str] = []
    for index, mapping in enumerate(mappings):
        if not isinstance(mapping, Mapping):
            errors.append(f'field_mappings[{index}] must be an object')
            continue
        field_name = str(mapping.get('pdf_field_name') or mapping.get('field_name') or '')
        citations = mapping.get('source_evidence_ids')
        if not isinstance(citations, list) or not citations:
            errors.append(f'field mapping {field_name or index} must cite source_evidence_ids')
        else:
            unknown = sorted(set(citations) - evidence_ids)
            if unknown:
                errors.append(f'field mapping {field_name or index} cites unknown evidence: {unknown}')
        if _is_certification_or_submission(field_name):
            value = str(mapping.get('value') or mapping.get('status') or '').lower()
            if value in _COMPLETE_VALUES or mapping.get('complete') is True or mapping.get('may_autofill') is True:
                errors.append(f'field mapping {field_name} must not mark certification or submission complete')
    return errors


def _blocked_field_errors(blocked_fields: Any, evidence_ids: set[str]) -> list[str]:
    if blocked_fields is None:
        return []
    if not isinstance(blocked_fields, list):
        return ['blocked_fields must be a list when present']

    errors: list[str] = []
    for index, field in enumerate(blocked_fields):
        if not isinstance(field, Mapping):
            errors.append(f'blocked_fields[{index}] must be an object')
            continue
        name = str(field.get('pdf_field_name') or field.get('field_name') or index)
        citations = field.get('source_evidence_ids') or field.get('requirement_trace_ids')
        if not isinstance(citations, list) or not citations:
            errors.append(f'blocked field {name} must cite source evidence')
        elif sorted(set(citations) - evidence_ids):
            errors.append(f'blocked field {name} cites unknown evidence')
        if _is_certification_or_submission(name) and field.get('complete') is True:
            errors.append(f'blocked field {name} must not be complete')
    return errors


def _recursive_safety_errors(value: Any, path: str = 'packet') -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f'{path}.{key_text}'
            normalized_key = key_text.lower().replace('-', '_')
            if any(part in normalized_key for part in _PRIVATE_KEY_PARTS):
                errors.append(f'private or credential key is not allowed: {child_path}')
            if normalized_key in _PDF_BINARY_KEYS:
                errors.append(f'PDF binary write field is not allowed: {child_path}')
            errors.extend(_recursive_safety_errors(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_recursive_safety_errors(child, f'{path}[{index}]'))
    elif isinstance(value, str):
        if _looks_private(value):
            errors.append(f'private value is not allowed: {path}')
        if _looks_local_path(value):
            errors.append(f'local private path is not allowed: {path}')
        if _looks_pdf_binary(value):
            errors.append(f'PDF binary content is not allowed: {path}')
    return errors


def _looks_private(value: str) -> bool:
    compact_digits = ''.join(ch for ch in value if ch.isdigit())
    if '@' in value and '.' in value.split('@')[-1]:
        return True
    if len(compact_digits) in range(13, 20):
        return True
    if len(compact_digits) == 9 and ('-' in value or 'routing' in value.lower()):
        return True
    return False


def _looks_local_path(value: str) -> bool:
    if value.startswith(('file://', '/Users/', '/home/', '/var/folders/', '/tmp/')):
        return True
    return len(value) > 2 and value[1] == ':' and (value[2] == '/' or ord(value[2]) == 92)


def _looks_pdf_binary(value: str) -> bool:
    stripped = value.strip()
    if stripped.startswith('%PDF-'):
        return True
    try:
        decoded = base64.b64decode(stripped, validate=True)
    except Exception:
        return False
    return decoded.startswith(b'%PDF-')


def _is_certification_or_submission(field_name: str) -> bool:
    lower = field_name.lower()
    return 'certif' in lower or 'signature' in lower or 'submit' in lower or 'submission' in lower


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _as_date(value: date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    return value
