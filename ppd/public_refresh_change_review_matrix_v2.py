"""Fixture-first public refresh change-review matrix v2.

This module consumes a metadata-only public refresh observation plan v2 fixture
and emits ordered synthetic review rows. It does not fetch live sources, persist
raw bodies, download PDFs, mutate active source registries, or update formal
guardrails.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from urllib.parse import parse_qsl, urlparse


_ALLOWED_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)
_ALLOWED_STATUSES = frozenset({"changed", "unchanged", "skipped", "stale_source"})
_STATUS_ORDER = {"changed": 0, "unchanged": 1, "skipped": 2, "stale_source": 3}
_PRIVATE_QUERY_KEYS = frozenset(
    {
        "access_token",
        "api_key",
        "auth",
        "code",
        "cookie",
        "key",
        "password",
        "session",
        "sessionid",
        "sig",
        "signature",
        "state",
        "token",
    }
)
_RAW_OR_PRIVATE_KEYS = frozenset(
    {
        "auth_state",
        "body",
        "browser_context",
        "content",
        "cookies",
        "credential",
        "credentials",
        "download_path",
        "downloaded_pdf",
        "file_path",
        "har",
        "html",
        "local_path",
        "password",
        "pdf_bytes",
        "pdf_path",
        "raw",
        "raw_body",
        "raw_html",
        "raw_pdf",
        "response_body",
        "screenshot",
        "session",
        "session_state",
        "text",
        "trace",
    }
)
_ACTIVE_MUTATION_KEYS = frozenset(
    {
        "active_guardrail_bundle_changed",
        "active_guardrail_mutation",
        "active_process_model_changed",
        "active_process_mutation",
        "active_prompt_changed",
        "active_prompt_mutation",
        "active_release_state_changed",
        "active_release_state_mutation",
        "active_requirement_registry_changed",
        "active_requirement_mutation",
        "active_source_mutation",
        "active_source_registry_changed",
        "formal_guardrails_updated",
        "guardrail_bundle_updated",
        "process_model_updated",
        "prompt_updated",
        "release_state_updated",
        "requirement_registry_updated",
        "source_registry_updated",
    }
)
_LIVE_CRAWL_CLAIMS = frozenset(
    {
        "captured live source",
        "fetched live",
        "live crawl completed",
        "live source fetch completed",
        "network crawl completed",
        "recrawled live",
    }
)
_CONSEQUENTIAL_ACTION_LANGUAGE = frozenset(
    {
        "cancelled permit",
        "certified acknowledgement",
        "official record updated",
        "paid fee",
        "purchased permit",
        "scheduled inspection",
        "submitted permit",
        "uploaded correction",
    }
)
_LEGAL_OR_PERMITTING_GUARANTEES = frozenset(
    {
        "approval guaranteed",
        "guarantee",
        "guaranteed",
        "legal advice",
        "legally sufficient",
        "permit will be approved",
        "will be issued",
    }
)
_DEFAULT_REVIEWER_DISPOSITION_PLACEHOLDERS = {
    "changed": "reviewer_disposition_pending_changed_requirement_review",
    "unchanged": "reviewer_disposition_pending_no_change_confirmation",
    "skipped": "reviewer_disposition_pending_skip_reason_acceptance",
    "stale_source": "reviewer_disposition_pending_recrawl_deferral_review",
}
_DEFAULT_RECRAWL_DEFERRAL_REASONS = {
    "changed": "not_deferred_change_requires_human_review_before_promotion",
    "unchanged": "not_deferred_fixture_indicates_no_source_hash_change",
    "skipped": "deferred_by_fixture_skip_policy",
    "stale_source": "deferred_until_public_source_can_be_recrawled_offline_first",
}
_OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/public_refresh_change_review_matrix_v2.py"),
    ("python3", "-m", "py_compile", "ppd/tests/test_public_refresh_change_review_matrix_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_public_refresh_change_review_matrix_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)


class PublicRefreshChangeReviewMatrixV2Error(ValueError):
    """Raised when an offline observation fixture is unsafe or incomplete."""


@dataclass(frozen=True)
class PlaceholderLink:
    link_id: str
    target_id: str
    placeholder_href: str
    review_status: str = "placeholder_pending_human_review"

    def to_dict(self) -> dict[str, str]:
        return {
            "link_id": self.link_id,
            "target_id": self.target_id,
            "placeholder_href": self.placeholder_href,
            "review_status": self.review_status,
        }


@dataclass(frozen=True)
class PublicRefreshChangeReviewRowV2:
    row_id: str
    row_order: int
    disposition_bucket: str
    observation_id: str
    source_id: str
    source_title: str
    public_url: str
    change_summary: str
    affected_requirement_links: tuple[PlaceholderLink, ...]
    affected_guardrail_links: tuple[PlaceholderLink, ...]
    reviewer_disposition_placeholder: str
    recrawl_deferral_reason: str
    exact_offline_validation_commands: tuple[tuple[str, ...], ...]
    live_source_fetch_performed: bool = False
    raw_body_persisted: bool = False
    pdf_downloaded: bool = False
    active_source_registry_changed: bool = False
    formal_guardrails_updated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "row_order": self.row_order,
            "disposition_bucket": self.disposition_bucket,
            "observation_id": self.observation_id,
            "source_id": self.source_id,
            "source_title": self.source_title,
            "public_url": self.public_url,
            "change_summary": self.change_summary,
            "affected_requirement_links": [link.to_dict() for link in self.affected_requirement_links],
            "affected_guardrail_links": [link.to_dict() for link in self.affected_guardrail_links],
            "reviewer_disposition_placeholder": self.reviewer_disposition_placeholder,
            "recrawl_deferral_reason": self.recrawl_deferral_reason,
            "exact_offline_validation_commands": [list(command) for command in self.exact_offline_validation_commands],
            "live_source_fetch_performed": self.live_source_fetch_performed,
            "raw_body_persisted": self.raw_body_persisted,
            "pdf_downloaded": self.pdf_downloaded,
            "active_source_registry_changed": self.active_source_registry_changed,
            "formal_guardrails_updated": self.formal_guardrails_updated,
        }


@dataclass(frozen=True)
class PublicRefreshChangeReviewMatrixV2:
    matrix_id: str
    source_plan_id: str
    plan_version: str
    rows: tuple[PublicRefreshChangeReviewRowV2, ...]
    exact_offline_validation_commands: tuple[tuple[str, ...], ...]
    live_source_fetch_performed: bool = False
    raw_body_persisted: bool = False
    pdf_downloaded: bool = False
    active_source_registry_changed: bool = False
    formal_guardrails_updated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "matrix_id": self.matrix_id,
            "source_plan_id": self.source_plan_id,
            "plan_version": self.plan_version,
            "rows": [row.to_dict() for row in self.rows],
            "exact_offline_validation_commands": [list(command) for command in self.exact_offline_validation_commands],
            "live_source_fetch_performed": self.live_source_fetch_performed,
            "raw_body_persisted": self.raw_body_persisted,
            "pdf_downloaded": self.pdf_downloaded,
            "active_source_registry_changed": self.active_source_registry_changed,
            "formal_guardrails_updated": self.formal_guardrails_updated,
        }


def build_public_refresh_change_review_matrix_v2(plan: Mapping[str, Any]) -> PublicRefreshChangeReviewMatrixV2:
    """Build deterministic synthetic review rows from an observation plan v2 fixture."""

    _reject_raw_or_private_fields(plan)
    _reject_unsafe_text(plan)
    _reject_active_mutation_flags(plan)
    _require_false(plan, "live_source_fetch_performed")
    _require_false(plan, "raw_body_persisted")
    _require_false(plan, "pdf_downloaded")
    _require_false(plan, "active_source_registry_changed")
    _require_false(plan, "formal_guardrails_updated")

    plan_version = _required_text(plan, "plan_version")
    if plan_version != "public_refresh_observation_plan_v2":
        raise PublicRefreshChangeReviewMatrixV2Error("plan_version must be public_refresh_observation_plan_v2")
    if _required_text(plan, "capture_mode") != "fixture_first_offline":
        raise PublicRefreshChangeReviewMatrixV2Error("capture_mode must be fixture_first_offline")

    source_plan_id = _required_text(plan, "plan_id")
    validation_commands = _commands(plan.get("exact_offline_validation_commands"))
    observations = _sequence_of_mappings(plan.get("observations"), "observations")
    rows: list[PublicRefreshChangeReviewRowV2] = []

    for observation in observations:
        status = _required_text(observation, "status")
        if status not in _ALLOWED_STATUSES:
            raise PublicRefreshChangeReviewMatrixV2Error(f"unsupported observation status: {status}")
        observation_id = _required_text(observation, "observation_id")
        source_id = _required_text(observation, "source_id")
        public_url = _public_url(_required_text(observation, "public_url"), observation_id)
        requirement_ids = tuple(sorted(_string_sequence(observation.get("affected_requirement_ids"), "affected_requirement_ids")))
        guardrail_ids = tuple(sorted(_string_sequence(observation.get("affected_guardrail_ids"), "affected_guardrail_ids")))
        _require_placeholder_ids(requirement_ids, "placeholder-req-", observation_id, "affected_requirement_ids")
        _require_placeholder_ids(guardrail_ids, "placeholder-guardrail-", observation_id, "affected_guardrail_ids")
        if not requirement_ids:
            raise PublicRefreshChangeReviewMatrixV2Error(f"{observation_id} must include affected_requirement_ids")
        if not guardrail_ids:
            raise PublicRefreshChangeReviewMatrixV2Error(f"{observation_id} must include affected_guardrail_ids")

        reviewer_disposition_placeholder = _required_text(observation, "reviewer_disposition_placeholder")
        recrawl_deferral_reason = _required_text(observation, "recrawl_deferral_reason")
        if reviewer_disposition_placeholder == _DEFAULT_REVIEWER_DISPOSITION_PLACEHOLDERS[status]:
            reviewer_disposition_placeholder = reviewer_disposition_placeholder
        if recrawl_deferral_reason == _DEFAULT_RECRAWL_DEFERRAL_REASONS[status]:
            recrawl_deferral_reason = recrawl_deferral_reason

        rows.append(
            PublicRefreshChangeReviewRowV2(
                row_id=f"matrix-v2-{status}-{source_id}-{observation_id}",
                row_order=0,
                disposition_bucket=status,
                observation_id=observation_id,
                source_id=source_id,
                source_title=_required_text(observation, "source_title"),
                public_url=public_url,
                change_summary=_required_text(observation, "change_summary"),
                affected_requirement_links=_placeholder_links("requirement", observation_id, requirement_ids),
                affected_guardrail_links=_placeholder_links("guardrail", observation_id, guardrail_ids),
                reviewer_disposition_placeholder=reviewer_disposition_placeholder,
                recrawl_deferral_reason=recrawl_deferral_reason,
                exact_offline_validation_commands=validation_commands,
            )
        )

    observed_statuses = {row.disposition_bucket for row in rows}
    if observed_statuses != _ALLOWED_STATUSES:
        missing = sorted(_ALLOWED_STATUSES - observed_statuses, key=lambda item: _STATUS_ORDER[item])
        raise PublicRefreshChangeReviewMatrixV2Error(
            "review rows must cover changed, unchanged, skipped, and stale_source; missing: " + ", ".join(missing)
        )

    ordered_rows = []
    for row_order, row in enumerate(sorted(rows, key=lambda item: (_STATUS_ORDER[item.disposition_bucket], item.source_id, item.observation_id)), start=1):
        ordered_rows.append(
            PublicRefreshChangeReviewRowV2(
                row_id=row.row_id,
                row_order=row_order,
                disposition_bucket=row.disposition_bucket,
                observation_id=row.observation_id,
                source_id=row.source_id,
                source_title=row.source_title,
                public_url=row.public_url,
                change_summary=row.change_summary,
                affected_requirement_links=row.affected_requirement_links,
                affected_guardrail_links=row.affected_guardrail_links,
                reviewer_disposition_placeholder=row.reviewer_disposition_placeholder,
                recrawl_deferral_reason=row.recrawl_deferral_reason,
                exact_offline_validation_commands=row.exact_offline_validation_commands,
            )
        )

    return PublicRefreshChangeReviewMatrixV2(
        matrix_id=f"public-refresh-change-review-matrix-v2-{source_plan_id}",
        source_plan_id=source_plan_id,
        plan_version=plan_version,
        rows=tuple(ordered_rows),
        exact_offline_validation_commands=validation_commands,
    )


def _placeholder_links(kind: str, observation_id: str, target_ids: Sequence[str]) -> tuple[PlaceholderLink, ...]:
    return tuple(
        PlaceholderLink(
            link_id=f"placeholder-{kind}-{observation_id}-{target_id}",
            target_id=target_id,
            placeholder_href=f"ppd://placeholder/{kind}/{target_id}",
        )
        for target_id in target_ids
    )


def _reject_raw_or_private_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in _RAW_OR_PRIVATE_KEYS:
                raise PublicRefreshChangeReviewMatrixV2Error(f"raw or private field is not allowed at {path}.{key}")
            _reject_raw_or_private_fields(child, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_raw_or_private_fields(child, f"{path}[{index}]")


def _reject_active_mutation_flags(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in _ACTIVE_MUTATION_KEYS and child is not False:
                raise PublicRefreshChangeReviewMatrixV2Error(f"active mutation flag must be false at {path}.{key}")
            _reject_active_mutation_flags(child, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_active_mutation_flags(child, f"{path}[{index}]")


def _reject_unsafe_text(value: Any, path: str = "$") -> None:
    if isinstance(value, str):
        lowered = value.lower()
        for phrase in _LIVE_CRAWL_CLAIMS:
            if phrase in lowered:
                raise PublicRefreshChangeReviewMatrixV2Error(f"live crawl claim is not allowed at {path}")
        for phrase in _CONSEQUENTIAL_ACTION_LANGUAGE:
            if phrase in lowered:
                raise PublicRefreshChangeReviewMatrixV2Error(f"consequential official action language is not allowed at {path}")
        for phrase in _LEGAL_OR_PERMITTING_GUARANTEES:
            if phrase in lowered:
                raise PublicRefreshChangeReviewMatrixV2Error(f"legal or permitting guarantee is not allowed at {path}")
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_unsafe_text(child, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_unsafe_text(child, f"{path}[{index}]")


def _require_false(plan: Mapping[str, Any], key: str) -> None:
    if plan.get(key) is not False:
        raise PublicRefreshChangeReviewMatrixV2Error(f"{key} must be false")


def _required_text(value: Mapping[str, Any], key: str) -> str:
    child = value.get(key)
    if not isinstance(child, str) or not child.strip():
        raise PublicRefreshChangeReviewMatrixV2Error(f"{key} must be a non-empty string")
    return child.strip()


def _sequence_of_mappings(value: Any, key: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise PublicRefreshChangeReviewMatrixV2Error(f"{key} must be a list of objects")
    if not all(isinstance(item, Mapping) for item in value):
        raise PublicRefreshChangeReviewMatrixV2Error(f"{key} must be a list of objects")
    return tuple(value)


def _string_sequence(value: Any, key: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise PublicRefreshChangeReviewMatrixV2Error(f"{key} must be a list of strings")
    result = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise PublicRefreshChangeReviewMatrixV2Error(f"{key} must be a list of non-empty strings")
        result.append(item.strip())
    return tuple(result)


def _require_placeholder_ids(values: Sequence[str], prefix: str, observation_id: str, key: str) -> None:
    for value in values:
        if not value.startswith(prefix):
            raise PublicRefreshChangeReviewMatrixV2Error(f"{observation_id} {key} must contain placeholder ids")


def _commands(value: Any) -> tuple[tuple[str, ...], ...]:
    if value is None:
        raise PublicRefreshChangeReviewMatrixV2Error("exact_offline_validation_commands must be provided")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise PublicRefreshChangeReviewMatrixV2Error("exact_offline_validation_commands must be a list of command arrays")
    commands = []
    for command in value:
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes, bytearray)):
            raise PublicRefreshChangeReviewMatrixV2Error("each validation command must be an array")
        parsed = []
        for part in command:
            if not isinstance(part, str) or not part.strip():
                raise PublicRefreshChangeReviewMatrixV2Error("validation command parts must be non-empty strings")
            parsed.append(part.strip())
        if not parsed:
            raise PublicRefreshChangeReviewMatrixV2Error("validation command must not be empty")
        commands.append(tuple(parsed))
    parsed_commands = tuple(commands)
    if not parsed_commands:
        raise PublicRefreshChangeReviewMatrixV2Error("exact_offline_validation_commands must not be empty")
    if not set(_OFFLINE_VALIDATION_COMMANDS).issubset(set(parsed_commands)):
        raise PublicRefreshChangeReviewMatrixV2Error("exact_offline_validation_commands must include the public refresh matrix offline checks")
    return parsed_commands


def _public_url(url: str, observation_id: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise PublicRefreshChangeReviewMatrixV2Error(f"{observation_id} public_url must use HTTPS")
    if parsed.username or parsed.password:
        raise PublicRefreshChangeReviewMatrixV2Error(f"{observation_id} public_url must not include credentials")
    if parsed.hostname not in _ALLOWED_HOSTS:
        raise PublicRefreshChangeReviewMatrixV2Error(f"{observation_id} public_url is outside the PP&D public allowlist")
    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & _PRIVATE_QUERY_KEYS:
        raise PublicRefreshChangeReviewMatrixV2Error(f"{observation_id} public_url contains private query parameters")
    return url
