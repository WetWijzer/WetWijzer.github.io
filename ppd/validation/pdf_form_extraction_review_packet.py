from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

SUPPORTED_FIELD_TYPES = frozenset({'text', 'textarea', 'checkbox', 'radio', 'select', 'dropdown', 'date', 'number', 'currency', 'email', 'phone', 'signature', 'certification', 'calculated', 'label'})
PRIVATE_VALUE_KEYS = frozenset({'account_number', 'auth_state', 'card_number', 'cookie', 'cookies', 'cvv', 'known_value', 'password', 'payment_details', 'private_value', 'raw_value', 'routing_number', 'session_state', 'ssn', 'storage_state', 'token'})
PDF_BINARY_KEYS = frozenset({'binary', 'content_bytes', 'file_bytes', 'pdf_binary', 'pdf_bytes', 'raw_pdf', 'raw_pdf_bytes'})
RAW_OCR_IMAGE_KEYS = frozenset({'image_bytes', 'ocr_image', 'ocr_images', 'page_image', 'page_images', 'raw_ocr_image', 'raw_ocr_images', 'screenshot', 'screenshots'})
PATH_KEYS = frozenset({'download_path', 'downloaded_file', 'downloaded_file_path', 'file_path', 'local_path', 'path', 'source_path'})
COMPLETION_CLAIM_KEYS = frozenset({'certification_complete', 'certification_completed', 'certified', 'claim_complete', 'completion_claim', 'is_complete', 'signed', 'signature_complete', 'signature_completed'})
COMPLETION_CLAIM_VALUES = frozenset({'certification complete', 'certified', 'complete', 'completed', 'signed', 'signature complete'})
PRIVATE_STRING_MARKERS = ('/data/private/', '/devhub/.auth/', '/devhub/downloads/', '/devhub/screenshots/', '/devhub/traces/', '.har', 'auth-state', 'bearer ', 'card_number', 'cookie=', 'cvv', 'password=', 'routing_number', 'storage-state', 'token=', 'trace.zip')


@dataclass(frozen=True)
class PdfFormExtractionReviewFinding:
    code: str
    field_id: str
    path: str
    message: str


@dataclass(frozen=True)
class PdfFormExtractionReviewValidation:
    ok: bool
    findings: tuple[PdfFormExtractionReviewFinding, ...]


class PdfFormExtractionReviewPacketError(ValueError):
    def __init__(self, findings: Sequence[PdfFormExtractionReviewFinding]) -> None:
        self.findings = tuple(findings)
        codes = ', '.join(finding.code for finding in self.findings)
        super().__init__(f'pdf/form extraction review packet rejected: {codes}')


def validate_pdf_form_extraction_review_packet(packet: Mapping[str, object], *, supported_field_types: Iterable[str] = SUPPORTED_FIELD_TYPES) -> PdfFormExtractionReviewValidation:
    findings: list[PdfFormExtractionReviewFinding] = []
    supported_types = {_text(item).lower() for item in supported_field_types if _text(item)}
    findings.extend(_packet_privacy_findings(packet))

    for index, field in enumerate(_fields(packet)):
        path = f'$.fields[{index}]'
        field_id = _field_id(field)
        field_type = _text(field.get('field_type') or field.get('type')).lower()
        if not field_type or field_type not in supported_types:
            findings.append(PdfFormExtractionReviewFinding('unsupported_field_type', field_id, path, 'form fields must use a supported deterministic extraction field type'))
        if not (_has_page_anchor(field) or _has_citation_anchor(field)):
            findings.append(PdfFormExtractionReviewFinding('field_without_page_or_citation_anchor', field_id, path, 'form fields must include a page anchor or a citation/source anchor'))
        if _unmarked_ocr_text(field):
            findings.append(PdfFormExtractionReviewFinding('unmarked_ocr_derived_text', field_id, path, 'OCR-derived field text must be explicitly marked with confidence and review status'))
        if _signature_or_certification_completion_claim(field):
            findings.append(PdfFormExtractionReviewFinding('signature_or_certification_completion_claim', field_id, path, 'review packets may identify signature/certification blocks but must not claim they are complete'))

    for index, text_item in enumerate(_text_items(packet)):
        if _unmarked_ocr_text(text_item):
            findings.append(PdfFormExtractionReviewFinding('unmarked_ocr_derived_text', _field_id(text_item), f'$.text_items[{index}]', 'OCR-derived text segments must be explicitly marked with confidence and review status'))

    return PdfFormExtractionReviewValidation(ok=not findings, findings=tuple(findings))


def require_pdf_form_extraction_review_packet(packet: Mapping[str, object], *, supported_field_types: Iterable[str] = SUPPORTED_FIELD_TYPES) -> None:
    result = validate_pdf_form_extraction_review_packet(packet, supported_field_types=supported_field_types)
    if result.findings:
        raise PdfFormExtractionReviewPacketError(result.findings)


def _fields(packet: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    value = packet.get('fields') or packet.get('form_fields') or packet.get('pdf_fields')
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _text_items(packet: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    value = packet.get('text_items') or packet.get('text_segments') or packet.get('page_text')
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _field_id(field: Mapping[str, object]) -> str:
    return _text(field.get('field_id') or field.get('id') or field.get('name')) or 'packet'


def _text(value: object) -> str:
    if value is None:
        return ''
    return str(value).strip()


def _sequence(value: object) -> tuple[object, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes, bytearray)):
        return (value,) if _text(value) else ()
    if isinstance(value, Sequence):
        return tuple(item for item in value if _text(item) or isinstance(item, Mapping))
    return (value,) if _text(value) else ()


def _has_page_anchor(field: Mapping[str, object]) -> bool:
    page_value = field.get('page') or field.get('page_number') or field.get('pageNumber') or field.get('page_index')
    if page_value is None:
        return False
    try:
        return int(page_value) >= 0
    except (TypeError, ValueError):
        return bool(_text(page_value))


def _has_citation_anchor(field: Mapping[str, object]) -> bool:
    if _sequence(field.get('source_evidence_ids') or field.get('sourceEvidenceIds')):
        return True
    for key in ('citation', 'citation_anchor', 'citation_spans', 'citations', 'source_anchor', 'source_evidence'):
        value = field.get(key)
        if isinstance(value, Mapping):
            return True
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            if any(isinstance(item, Mapping) or _text(item) for item in value):
                return True
        if _text(value):
            return True
    return False


def _unmarked_ocr_text(item: Mapping[str, object]) -> bool:
    method = _text(item.get('extraction_method') or item.get('source') or item.get('text_source')).lower()
    has_ocr_key = any(_normalize_key(str(key)) in {'ocr_text', 'ocr_excerpt'} for key in item)
    derived = item.get('ocr_derived') is True or item.get('derived_from_ocr') is True or method == 'ocr' or has_ocr_key
    if not derived:
        return False
    confidence_present = item.get('ocr_confidence') is not None or item.get('confidence') is not None
    review_status = _text(item.get('human_review_status') or item.get('review_status'))
    marked = (item.get('ocr_derived') is True or item.get('derived_from_ocr') is True) and confidence_present and bool(review_status)
    return not marked


def _signature_or_certification_completion_claim(field: Mapping[str, object]) -> bool:
    field_type = _text(field.get('field_type') or field.get('type')).lower()
    field_name = _text(field.get('name') or field.get('label') or field.get('field_id') or field.get('id')).lower()
    is_target = field_type in {'signature', 'certification'} or 'signature' in field_name or 'certification' in field_name
    if not is_target:
        return False
    for key, value in field.items():
        normalized_key = _normalize_key(str(key))
        if normalized_key in COMPLETION_CLAIM_KEYS and _truthy_claim(value):
            return True
        if normalized_key in {'value', 'status', 'claim'} and _text(value).lower() in COMPLETION_CLAIM_VALUES:
            return True
    return False


def _truthy_claim(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return _text(value).lower() in COMPLETION_CLAIM_VALUES


def _packet_privacy_findings(value: object, path: str = '$', field_id: str = 'packet') -> tuple[PdfFormExtractionReviewFinding, ...]:
    findings: list[PdfFormExtractionReviewFinding] = []
    if isinstance(value, Mapping):
        current_field_id = _field_id(value) if any(key in value for key in ('field_id', 'id', 'name')) else field_id
        for key, child in value.items():
            key_text = str(key)
            normalized_key = _normalize_key(key_text)
            child_path = f'{path}.{key_text}'
            if normalized_key in PDF_BINARY_KEYS or _looks_like_pdf_binary(child):
                findings.append(PdfFormExtractionReviewFinding('pdf_binary_present', current_field_id, child_path, 'review packets must not include PDF binaries or raw PDF bytes'))
            if normalized_key in RAW_OCR_IMAGE_KEYS or _looks_like_raw_image(child):
                findings.append(PdfFormExtractionReviewFinding('raw_ocr_image_present', current_field_id, child_path, 'review packets must not include raw OCR images or screenshots'))
            if normalized_key in PATH_KEYS and _looks_like_downloaded_path(child):
                findings.append(PdfFormExtractionReviewFinding('downloaded_file_path_present', current_field_id, child_path, 'review packets must not include downloaded local file paths'))
            if normalized_key in PRIVATE_VALUE_KEYS:
                findings.append(PdfFormExtractionReviewFinding('private_value_present', current_field_id, child_path, 'review packets must not include private values or runtime secrets'))
            findings.extend(_packet_privacy_findings(child, child_path, current_field_id))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            findings.extend(_packet_privacy_findings(child, f'{path}[{index}]', field_id))
    elif isinstance(value, (bytes, bytearray)):
        if bytes(value).startswith(b'%PDF-'):
            findings.append(PdfFormExtractionReviewFinding('pdf_binary_present', field_id, path, 'review packets must not include PDF binaries'))
    elif isinstance(value, str):
        lowered = value.lower()
        if lowered.lstrip().startswith('%pdf-'):
            findings.append(PdfFormExtractionReviewFinding('pdf_binary_present', field_id, path, 'review packets must not include PDF binaries'))
        if lowered.startswith('data:image/'):
            findings.append(PdfFormExtractionReviewFinding('raw_ocr_image_present', field_id, path, 'review packets must not include raw OCR images'))
        if any(marker in lowered for marker in PRIVATE_STRING_MARKERS):
            findings.append(PdfFormExtractionReviewFinding('private_value_present', field_id, path, 'review packets must not include private values or runtime artifacts'))
    return tuple(findings)


def _looks_like_pdf_binary(value: object) -> bool:
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).startswith(b'%PDF-')
    if isinstance(value, str):
        return value.lstrip().startswith('%PDF-')
    return False


def _looks_like_raw_image(value: object) -> bool:
    return isinstance(value, str) and value.lower().startswith('data:image/')


def _looks_like_downloaded_path(value: object) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip().lower()
    if not text or text.startswith('http://') or text.startswith('https://'):
        return False
    return text.startswith('/') or ':\\' in text or 'downloads' in text or text.endswith('.pdf')


def _normalize_key(value: str) -> str:
    chars: list[str] = []
    for character in value:
        if character.isalnum():
            chars.append(character.lower())
        else:
            chars.append('_')
    normalized = ''.join(chars)
    while '__' in normalized:
        normalized = normalized.replace('__', '_')
    return normalized.strip('_')


validate_packet = validate_pdf_form_extraction_review_packet
require_packet = require_pdf_form_extraction_review_packet

__all__ = ['PDF_BINARY_KEYS', 'PRIVATE_VALUE_KEYS', 'RAW_OCR_IMAGE_KEYS', 'SUPPORTED_FIELD_TYPES', 'PdfFormExtractionReviewFinding', 'PdfFormExtractionReviewPacketError', 'PdfFormExtractionReviewValidation', 'require_packet', 'require_pdf_form_extraction_review_packet', 'validate_packet', 'validate_pdf_form_extraction_review_packet']
