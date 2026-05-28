"""Fixture-first source-to-guardrail invalidation packets for PP&D.

The helpers in this module validate curated metadata only. They do not crawl,
regenerate guardrails, mark guardrails current, or persist private DevHub state.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse


REVIEWED_SOURCE_STATUSES = frozenset({"human_reviewed", "reviewed", "approved"})
REVIEWED_FRESHNESS_STATUSES = frozenset(
    {
        "content_hash_changed",
        "changed_requirement_reviewed",
        "reviewed_public_guidance_change",
        "reviewed_public_guidance_hash_change",
    }
)
REVIEWED_CHANGE_KINDS = frozenset(
    {
        "reviewed_public_guidance_hash_change",
        "reviewed_public_guidance_text_change",
        "reviewed_public_pdf_change",
        "reviewed_public_form_change",
    }
)
PUBLIC_SOURCE_HOSTS = frozenset({"www.portland.gov", "www.portlandoregon.gov", "www.portlandmaps.com"})
BLOCKING_CACHE_STATUSES = frozenset(
    {
        "stale_due_to_source_change",
        "blocked_pending_human_review",
        "refresh_required_before_use",
    }
)
NON_CURRENT_GUARDRAIL_STATUSES = frozenset(
    {
        "invalidated_by_source_change",
        "regenerated_pending_human_review",
        "stale_pending_regeneration",
    }
)
PRIVATE_OR_RAW_FIELD_NAMES = frozenset(
    {
        "auth_state",
        "body",
        "content_body",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "document_bytes",
        "download_path",
        "downloadedDocumentPath",
        "downloaded_document",
        "downloaded_document_path",
        "downloaded_path",
        "har",
        "html",
        "local_path",
        "password",
        "payment_details",
        "rawBody",
        "raw_body",
        "raw_crawl_output",
        "raw_html",
        "screenshot",
        "session_state",
        "storage_state",
        "trace",
    }
)
FORBIDDEN_PROMOTION_VALUES = frozenset({"auto", "automatic", "promote_current", "promote_without_review"})
_LOCAL_PATH_PATTERN = re.compile(r"(^|\s)(/home/|/users/|/tmp/|/var/folders/|[a-z]:\\\\users\\\\)", re.IGNORECASE)
_PRIVATE_URL_PATH_PARTS = ("/login", "/signin", "/sign-in", "/account", "/accounts", "/permit/", "/permits/", "/private", "/secure")


@dataclass(frozen=True)
class ReviewedSourceFreshnessChange:
    source_id: str
    canonical_url: str
    previous_freshness_status: str
    reviewed_freshness_status: str
    change_kind: str
    reviewed_at: str
    review_status: str
    reviewer_note: str
    source_evidence_ids: tuple[str, ...]

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.source_id.strip():
            errors.append("source freshness change requires source_id")
        if not _is_safe_public_url(self.canonical_url):
            errors.append("source freshness change canonical_url must be a safe public PP&D source URL")
        if not self.previous_freshness_status.strip():
            errors.append("source freshness change requires previous_freshness_status")
        if self.reviewed_freshness_status not in REVIEWED_FRESHNESS_STATUSES:
            errors.append("source freshness change reviewed_freshness_status must be a reviewed public change status")
        if self.previous_freshness_status == self.reviewed_freshness_status:
            errors.append("source freshness change must alter freshness status")
        if self.change_kind not in REVIEWED_CHANGE_KINDS:
            errors.append("source freshness change kind must be reviewed public evidence, not an invented change")
        if not self.reviewed_at.endswith("Z"):
            errors.append("source freshness change reviewed_at must end in Z")
        if self.review_status not in REVIEWED_SOURCE_STATUSES:
            errors.append("source freshness change must be reviewed before guardrail invalidation")
        if not self.reviewer_note.strip():
            errors.append("source freshness change requires reviewer_note")
        if not self.source_evidence_ids:
            errors.append("source freshness change requires source_evidence_ids")
        return errors


@dataclass(frozen=True)
class AffectedRequirement:
    requirement_id: str
    source_id: str
    process_id: str
    process_stage_id: str
    guardrail_predicate_ids: tuple[str, ...]
    impact_summary: str
    human_review_required: bool = True

    def validate(self, changed_source_id: str) -> list[str]:
        errors: list[str] = []
        if not self.requirement_id.strip():
            errors.append("affected requirement requires requirement_id")
        if self.source_id != changed_source_id:
            errors.append(f"affected requirement {self.requirement_id} must reference changed source")
        if not self.process_id.strip():
            errors.append(f"affected requirement {self.requirement_id} requires process_id")
        if not self.process_stage_id.strip():
            errors.append(f"affected requirement {self.requirement_id} requires process_stage_id")
        if not self.guardrail_predicate_ids:
            errors.append(f"affected requirement {self.requirement_id} requires guardrail predicate ids")
        if not self.impact_summary.strip():
            errors.append(f"affected requirement {self.requirement_id} requires impact_summary")
        if not self.human_review_required:
            errors.append(f"affected requirement {self.requirement_id} must require human review")
        return errors


@dataclass(frozen=True)
class AffectedProcessStage:
    process_id: str
    stage_id: str
    stage_name: str
    affected_requirement_ids: tuple[str, ...]
    invalidation_reason: str

    def validate(self, known_requirement_ids: set[str]) -> list[str]:
        errors: list[str] = []
        if not self.process_id.strip():
            errors.append("affected process stage requires process_id")
        if not self.stage_id.strip():
            errors.append("affected process stage requires stage_id")
        if not self.stage_name.strip():
            errors.append(f"affected process stage {self.stage_id} requires stage_name")
        if not self.affected_requirement_ids:
            errors.append(f"affected process stage {self.stage_id} requires affected_requirement_ids")
        for requirement_id in self.affected_requirement_ids:
            if requirement_id not in known_requirement_ids:
                errors.append(f"affected process stage {self.stage_id} references unknown requirement {requirement_id}")
        if not self.invalidation_reason.strip():
            errors.append(f"affected process stage {self.stage_id} requires invalidation_reason")
        return errors


@dataclass(frozen=True)
class GuardrailPredicateInvalidation:
    predicate_id: str
    guardrail_bundle_id: str
    predicate_kind: str
    affected_requirement_ids: tuple[str, ...]
    source_evidence_ids: tuple[str, ...]
    previous_status: str
    invalidated_status: str
    regenerated_guardrail_status: str

    def validate(self, known_requirement_ids: set[str], known_source_evidence_ids: set[str]) -> list[str]:
        errors: list[str] = []
        if not self.predicate_id.strip():
            errors.append("guardrail predicate invalidation requires predicate_id")
        if not self.guardrail_bundle_id.strip():
            errors.append(f"guardrail predicate {self.predicate_id} requires guardrail_bundle_id")
        if not self.predicate_kind.strip():
            errors.append(f"guardrail predicate {self.predicate_id} requires predicate_kind")
        if not self.affected_requirement_ids:
            errors.append(f"guardrail predicate {self.predicate_id} requires affected_requirement_ids")
        for requirement_id in self.affected_requirement_ids:
            if requirement_id not in known_requirement_ids:
                errors.append(f"guardrail predicate {self.predicate_id} references unknown requirement {requirement_id}")
        if not self.source_evidence_ids:
            errors.append(f"guardrail predicate {self.predicate_id} must cite source_evidence_ids")
        elif not set(self.source_evidence_ids).issubset(known_source_evidence_ids):
            errors.append(f"guardrail predicate {self.predicate_id} cites unknown source_evidence_ids")
        if self.previous_status != "current":
            errors.append(f"guardrail predicate {self.predicate_id} previous_status must be current")
        if self.invalidated_status not in NON_CURRENT_GUARDRAIL_STATUSES:
            errors.append(f"guardrail predicate {self.predicate_id} must be invalidated or pending review")
        if self.regenerated_guardrail_status == "current":
            errors.append(f"guardrail predicate {self.predicate_id} regenerated guardrail must not be current before review")
        if self.regenerated_guardrail_status not in NON_CURRENT_GUARDRAIL_STATUSES:
            errors.append(f"guardrail predicate {self.predicate_id} regenerated status must remain non-current")
        return errors


@dataclass(frozen=True)
class AgentCacheStatus:
    cache_key: str
    consumer: str
    status: str
    stale_reason: str
    blocked_until: str
    affected_guardrail_predicate_ids: tuple[str, ...]

    def validate(self, known_predicate_ids: set[str]) -> list[str]:
        errors: list[str] = []
        if not self.cache_key.strip():
            errors.append("agent cache status requires cache_key")
        if not self.consumer.strip():
            errors.append(f"agent cache status {self.cache_key} requires consumer")
        if self.status == "current":
            errors.append(f"agent cache status {self.cache_key} must not be marked current after source change")
        if self.status not in BLOCKING_CACHE_STATUSES:
            errors.append(f"agent cache status {self.cache_key} must block current use")
        if not self.stale_reason.strip():
            errors.append(f"agent cache status {self.cache_key} requires stale_reason")
        if self.blocked_until != "human_review_resolved":
            errors.append(f"agent cache status {self.cache_key} must block until human review is resolved")
        if not self.affected_guardrail_predicate_ids:
            errors.append(f"agent cache status {self.cache_key} requires affected guardrail predicates")
        for predicate_id in self.affected_guardrail_predicate_ids:
            if predicate_id not in known_predicate_ids:
                errors.append(f"agent cache status {self.cache_key} references unknown predicate {predicate_id}")
        return errors


@dataclass(frozen=True)
class HumanReviewPrompt:
    prompt_id: str
    reviewer_role: str
    prompt: str
    required_resolution: str
    source_id: str
    affected_requirement_ids: tuple[str, ...]
    affected_guardrail_predicate_ids: tuple[str, ...]

    def validate(self, changed_source_id: str, known_requirement_ids: set[str], known_predicate_ids: set[str]) -> list[str]:
        errors: list[str] = []
        if not self.prompt_id.strip():
            errors.append("human review prompt requires prompt_id")
        if not self.reviewer_role.strip():
            errors.append(f"human review prompt {self.prompt_id} requires reviewer_role")
        if not self.prompt.strip():
            errors.append(f"human review prompt {self.prompt_id} requires prompt")
        if self.required_resolution != "review_before_current_guardrail":
            errors.append(f"human review prompt {self.prompt_id} must resolve before current guardrail status")
        if self.source_id != changed_source_id:
            errors.append(f"human review prompt {self.prompt_id} must reference changed source")
        if not self.affected_requirement_ids:
            errors.append(f"human review prompt {self.prompt_id} requires affected requirements")
        for requirement_id in self.affected_requirement_ids:
            if requirement_id not in known_requirement_ids:
                errors.append(f"human review prompt {self.prompt_id} references unknown requirement {requirement_id}")
        if not self.affected_guardrail_predicate_ids:
            errors.append(f"human review prompt {self.prompt_id} requires affected guardrail predicates")
        for predicate_id in self.affected_guardrail_predicate_ids:
            if predicate_id not in known_predicate_ids:
                errors.append(f"human review prompt {self.prompt_id} references unknown predicate {predicate_id}")
        return errors


@dataclass(frozen=True)
class SourceToGuardrailInvalidationPacket:
    packet_id: str
    generated_at: str
    source_change: ReviewedSourceFreshnessChange
    affected_requirements: tuple[AffectedRequirement, ...]
    affected_process_stages: tuple[AffectedProcessStage, ...]
    guardrail_predicate_invalidations: tuple[GuardrailPredicateInvalidation, ...]
    agent_cache_statuses: tuple[AgentCacheStatus, ...]
    human_review_prompts: tuple[HumanReviewPrompt, ...]
    regenerated_guardrails_marked_current: bool = False
    automatic_promotion_requested: bool = False
    safety_notes: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.packet_id.strip():
            errors.append("packet_id is required")
        if not self.generated_at.endswith("Z"):
            errors.append("generated_at must end in Z")
        if self.regenerated_guardrails_marked_current:
            errors.append("regenerated guardrails must not be marked current in an invalidation packet")
        if self.automatic_promotion_requested:
            errors.append("automatic promotion without human review is not allowed")
        if not self.affected_requirements:
            errors.append("packet requires affected requirements")
        if not self.affected_process_stages:
            errors.append("packet requires affected process stages")
        if not self.guardrail_predicate_invalidations:
            errors.append("packet requires guardrail predicate invalidations")
        if not self.agent_cache_statuses:
            errors.append("packet requires agent-facing cache statuses")
        if not self.human_review_prompts:
            errors.append("packet requires human review prompts")
        if not self.safety_notes:
            errors.append("packet requires safety notes")

        errors.extend(self.source_change.validate())
        changed_source_id = self.source_change.source_id
        known_requirement_ids = {item.requirement_id for item in self.affected_requirements}
        known_predicate_ids = {item.predicate_id for item in self.guardrail_predicate_invalidations}
        known_source_evidence_ids = set(self.source_change.source_evidence_ids)

        for requirement in self.affected_requirements:
            errors.extend(requirement.validate(changed_source_id))
        for stage in self.affected_process_stages:
            errors.extend(stage.validate(known_requirement_ids))
        for predicate in self.guardrail_predicate_invalidations:
            errors.extend(predicate.validate(known_requirement_ids, known_source_evidence_ids))
        for status in self.agent_cache_statuses:
            errors.extend(status.validate(known_predicate_ids))
        for prompt in self.human_review_prompts:
            errors.extend(prompt.validate(changed_source_id, known_requirement_ids, known_predicate_ids))
        errors.extend(self._coverage_errors())
        return errors

    def affected_requirement_ids_by_stage(self) -> dict[str, tuple[str, ...]]:
        return {stage.stage_id: stage.affected_requirement_ids for stage in self.affected_process_stages}

    def cache_status_by_predicate(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for cache_status in self.agent_cache_statuses:
            for predicate_id in cache_status.affected_guardrail_predicate_ids:
                result[predicate_id] = cache_status.status
        return result

    def _coverage_errors(self) -> list[str]:
        errors: list[str] = []
        requirement_ids = {item.requirement_id for item in self.affected_requirements}
        stage_requirement_ids = {requirement_id for stage in self.affected_process_stages for requirement_id in stage.affected_requirement_ids}
        predicate_requirement_ids = {
            requirement_id for predicate in self.guardrail_predicate_invalidations for requirement_id in predicate.affected_requirement_ids
        }
        prompt_requirement_ids = {requirement_id for prompt in self.human_review_prompts for requirement_id in prompt.affected_requirement_ids}
        predicate_ids = {item.predicate_id for item in self.guardrail_predicate_invalidations}
        requirement_predicate_ids = {predicate_id for requirement in self.affected_requirements for predicate_id in requirement.guardrail_predicate_ids}
        cache_predicate_ids = {predicate_id for status in self.agent_cache_statuses for predicate_id in status.affected_guardrail_predicate_ids}
        prompt_predicate_ids = {predicate_id for prompt in self.human_review_prompts for predicate_id in prompt.affected_guardrail_predicate_ids}

        for requirement_id in sorted(requirement_ids - stage_requirement_ids):
            errors.append(f"affected requirement {requirement_id} is missing from affected_process_stages")
        for requirement_id in sorted(requirement_ids - predicate_requirement_ids):
            errors.append(f"affected requirement {requirement_id} is missing from guardrail predicate invalidations")
        for requirement_id in sorted(requirement_ids - prompt_requirement_ids):
            errors.append(f"affected requirement {requirement_id} is missing from human review prompts")
        for predicate_id in sorted(requirement_predicate_ids - predicate_ids):
            errors.append(f"affected requirement references missing guardrail predicate {predicate_id}")
        for predicate_id in sorted(predicate_ids - cache_predicate_ids):
            errors.append(f"guardrail predicate {predicate_id} is missing an agent cache status")
        for predicate_id in sorted(predicate_ids - prompt_predicate_ids):
            errors.append(f"guardrail predicate {predicate_id} is missing a human review prompt")
        return errors


def packet_from_dict(data: Mapping[str, Any]) -> SourceToGuardrailInvalidationPacket:
    _reject_private_or_raw_fields(data)
    source_change = _mapping(data, "source_change")
    return SourceToGuardrailInvalidationPacket(
        packet_id=_required_str(data, "packet_id"),
        generated_at=_required_str(data, "generated_at"),
        source_change=ReviewedSourceFreshnessChange(
            source_id=_required_str(source_change, "source_id"),
            canonical_url=_required_str(source_change, "canonical_url"),
            previous_freshness_status=_required_str(source_change, "previous_freshness_status"),
            reviewed_freshness_status=_required_str(source_change, "reviewed_freshness_status"),
            change_kind=_required_str(source_change, "change_kind"),
            reviewed_at=_required_str(source_change, "reviewed_at"),
            review_status=_required_str(source_change, "review_status"),
            reviewer_note=_required_str(source_change, "reviewer_note"),
            source_evidence_ids=_str_tuple(source_change, "source_evidence_ids"),
        ),
        affected_requirements=tuple(_affected_requirement(item) for item in _list(data, "affected_requirements")),
        affected_process_stages=tuple(_affected_process_stage(item) for item in _list(data, "affected_process_stages")),
        guardrail_predicate_invalidations=tuple(
            _guardrail_predicate_invalidation(item) for item in _list(data, "guardrail_predicate_invalidations")
        ),
        agent_cache_statuses=tuple(_agent_cache_status(item) for item in _list(data, "agent_cache_statuses")),
        human_review_prompts=tuple(_human_review_prompt(item) for item in _list(data, "human_review_prompts")),
        regenerated_guardrails_marked_current=_required_bool(data, "regenerated_guardrails_marked_current"),
        automatic_promotion_requested=_optional_bool(data, "automatic_promotion_requested"),
        safety_notes=_str_tuple(data, "safety_notes"),
    )


def load_invalidation_packet(path: Path) -> SourceToGuardrailInvalidationPacket:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("invalidation packet fixture must contain a JSON object")
    return packet_from_dict(parsed)


def _affected_requirement(data: Mapping[str, Any]) -> AffectedRequirement:
    return AffectedRequirement(
        requirement_id=_required_str(data, "requirement_id"),
        source_id=_required_str(data, "source_id"),
        process_id=_required_str(data, "process_id"),
        process_stage_id=_required_str(data, "process_stage_id"),
        guardrail_predicate_ids=_str_tuple(data, "guardrail_predicate_ids"),
        impact_summary=_required_str(data, "impact_summary"),
        human_review_required=_required_bool(data, "human_review_required"),
    )


def _affected_process_stage(data: Mapping[str, Any]) -> AffectedProcessStage:
    return AffectedProcessStage(
        process_id=_required_str(data, "process_id"),
        stage_id=_required_str(data, "stage_id"),
        stage_name=_required_str(data, "stage_name"),
        affected_requirement_ids=_str_tuple(data, "affected_requirement_ids"),
        invalidation_reason=_required_str(data, "invalidation_reason"),
    )


def _guardrail_predicate_invalidation(data: Mapping[str, Any]) -> GuardrailPredicateInvalidation:
    return GuardrailPredicateInvalidation(
        predicate_id=_required_str(data, "predicate_id"),
        guardrail_bundle_id=_required_str(data, "guardrail_bundle_id"),
        predicate_kind=_required_str(data, "predicate_kind"),
        affected_requirement_ids=_str_tuple(data, "affected_requirement_ids"),
        source_evidence_ids=_str_tuple(data, "source_evidence_ids"),
        previous_status=_required_str(data, "previous_status"),
        invalidated_status=_required_str(data, "invalidated_status"),
        regenerated_guardrail_status=_required_str(data, "regenerated_guardrail_status"),
    )


def _agent_cache_status(data: Mapping[str, Any]) -> AgentCacheStatus:
    return AgentCacheStatus(
        cache_key=_required_str(data, "cache_key"),
        consumer=_required_str(data, "consumer"),
        status=_required_str(data, "status"),
        stale_reason=_required_str(data, "stale_reason"),
        blocked_until=_required_str(data, "blocked_until"),
        affected_guardrail_predicate_ids=_str_tuple(data, "affected_guardrail_predicate_ids"),
    )


def _human_review_prompt(data: Mapping[str, Any]) -> HumanReviewPrompt:
    return HumanReviewPrompt(
        prompt_id=_required_str(data, "prompt_id"),
        reviewer_role=_required_str(data, "reviewer_role"),
        prompt=_required_str(data, "prompt"),
        required_resolution=_required_str(data, "required_resolution"),
        source_id=_required_str(data, "source_id"),
        affected_requirement_ids=_str_tuple(data, "affected_requirement_ids"),
        affected_guardrail_predicate_ids=_str_tuple(data, "affected_guardrail_predicate_ids"),
    )


def _reject_private_or_raw_fields(value: Any, path: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text in PRIVATE_OR_RAW_FIELD_NAMES:
                raise ValueError(f"invalidation packet fixture includes forbidden field {key_text!r}")
            if key_text in {"promotion_mode", "promotion_status"} and str(child).lower() in FORBIDDEN_PROMOTION_VALUES:
                raise ValueError("invalidation packet fixture requests automatic promotion without human review")
            _reject_private_or_raw_fields(child, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_private_or_raw_fields(child, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        if "file://" in lowered or "storage_state" in lowered or "trace.zip" in lowered or _LOCAL_PATH_PATTERN.search(value):
            raise ValueError(f"invalidation packet fixture includes forbidden private or downloaded document path at {path}")
        if _looks_private_or_authenticated_url(value):
            raise ValueError(f"invalidation packet fixture includes forbidden private or authenticated URL at {path}")


def _is_safe_public_url(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc not in PUBLIC_SOURCE_HOSTS:
        return False
    return not _path_is_private_or_authenticated(parsed.path)


def _looks_private_or_authenticated_url(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    if parsed.netloc == "devhub.portlandoregon.gov":
        return True
    return _path_is_private_or_authenticated(parsed.path)


def _path_is_private_or_authenticated(path: str) -> bool:
    lowered_path = path.lower()
    return any(part in lowered_path for part in _PRIVATE_URL_PATH_PARTS)


def _required_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_bool(data: Mapping[str, Any], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def _optional_bool(data: Mapping[str, Any], key: str) -> bool:
    value = data.get(key, False)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def _mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"{key} must be an object")
    return value


def _list(data: Mapping[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return value


def _str_tuple(data: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{key} must be a list of non-empty strings")
    return tuple(value)
