"""Deterministic contracts for DevHub post-action hardening reviews.

The review fixture is intentionally commit-safe: it records only redacted,
source-grounded evidence for safe read-only or reversible draft attempts and
explicit refusal evidence for consequential DevHub controls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

REDACTED_VALUE = "[REDACTED]"

SAFE_ACTION_CLASSES = {"safe_read_only", "reversible_draft"}
CONSEQUENTIAL_ACTION_CLASSES = {"consequential_official", "financial", "unsupported_manual_handoff"}
REQUIRED_CONSEQUENTIAL_CONTROLS = {
    "submit_permit_request",
    "certify_acknowledgement",
    "official_upload",
    "purchase_trade_permit",
    "schedule_inspection",
    "cancel_or_withdraw",
    "request_extension_or_reactivation",
    "enter_payment_details",
    "submit_payment",
}
ALLOWED_JOURNAL_EVENT_TYPES = {
    "DevHub attended preflight",
    "DevHub attempted action",
    "post-action hardening review",
    "refused action",
    "completion evidence",
    "manual handoff",
}
FORBIDDEN_BROWSER_ARTIFACT_KEYS = {
    "auth_state",
    "authstate",
    "storage_state",
    "storagestate",
    "cookies",
    "cookie",
    "credential",
    "credentials",
    "password",
    "token",
    "trace",
    "traces",
    "har",
    "screenshot",
    "screenshots",
    "video",
    "videos",
    "download",
    "downloads",
    "raw_crawl_output",
    "rawcrawloutput",
    "session_file",
    "session_path",
    "local_private_path",
}
FORBIDDEN_VALUE_FRAGMENTS = (
    ".auth/",
    "auth-state",
    "storage-state",
    "storageState",
    "trace.zip",
    ".har",
    ".png",
    ".webm",
    "cookies.json",
    "/home/",
    "C:\\\\Users\\",
)


@dataclass(frozen=True)
class AttemptedAction:
    action_id: str
    action_class: str
    journal_event_id: str
    outcome: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.action_id.strip():
            errors.append("attempted action id is required")
        if self.action_class not in SAFE_ACTION_CLASSES:
            errors.append(f"attempted action {self.action_id} must be safe read-only or reversible draft")
        if not self.journal_event_id.strip():
            errors.append(f"attempted action {self.action_id} journal_event_id is required")
        if self.outcome not in {"completed", "no_change", "refused"}:
            errors.append(f"attempted action {self.action_id} outcome is invalid")
        return errors


@dataclass(frozen=True)
class CompletionEvidence:
    evidence_id: str
    action_id: str
    journal_event_id: str
    observed_outcome: str
    source_evidence_ids: tuple[str, ...]
    user_visible_confirmation: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.evidence_id.strip():
            errors.append("completion evidence id is required")
        if not self.action_id.strip():
            errors.append(f"completion evidence {self.evidence_id} action_id is required")
        if not self.journal_event_id.strip():
            errors.append(f"completion evidence {self.evidence_id} journal_event_id is required")
        if not self.observed_outcome.strip():
            errors.append(f"completion evidence {self.evidence_id} observed_outcome is required")
        if not self.source_evidence_ids:
            errors.append(f"completion evidence {self.evidence_id} requires source evidence")
        if not self.user_visible_confirmation.strip():
            errors.append(f"completion evidence {self.evidence_id} requires user-visible confirmation")
        return errors


@dataclass(frozen=True)
class RefusedActionEvidence:
    evidence_id: str
    control_id: str
    action_class: str
    journal_event_id: str
    refusal_reason: str
    required_user_confirmation: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.evidence_id.strip():
            errors.append("refused action evidence id is required")
        if self.control_id not in REQUIRED_CONSEQUENTIAL_CONTROLS:
            errors.append(f"refused control {self.control_id} is not a required consequential control")
        if self.action_class not in CONSEQUENTIAL_ACTION_CLASSES:
            errors.append(f"refused control {self.control_id} must be consequential, financial, or manual handoff")
        if not self.journal_event_id.strip():
            errors.append(f"refused control {self.control_id} journal_event_id is required")
        if not self.refusal_reason.strip():
            errors.append(f"refused control {self.control_id} refusal_reason is required")
        if not self.required_user_confirmation.strip():
            errors.append(f"refused control {self.control_id} required_user_confirmation is required")
        return errors


@dataclass(frozen=True)
class RedactedJournalEvent:
    event_id: str
    event_type: str
    redaction_status: str
    payload: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.event_id.strip():
            errors.append("journal event id is required")
        if self.event_type not in ALLOWED_JOURNAL_EVENT_TYPES:
            errors.append(f"journal event {self.event_id} type is invalid")
        if self.redaction_status != "redacted":
            errors.append(f"journal event {self.event_id} must be redacted")
        errors.extend(_validate_no_private_artifacts(self.payload, f"journal event {self.event_id} payload"))
        return errors


@dataclass(frozen=True)
class DevHubPostActionHardeningReview:
    review_id: str
    review_type: str
    reviewed_at: str
    workflow: str
    attempted_actions: tuple[AttemptedAction, ...]
    completion_evidence: tuple[CompletionEvidence, ...]
    refused_action_evidence: tuple[RefusedActionEvidence, ...]
    journal_events: tuple[RedactedJournalEvent, ...]
    browser_artifacts: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.review_id.strip():
            errors.append("review id is required")
        if self.review_type != "post_action_hardening_review":
            errors.append("review_type must be post_action_hardening_review")
        if not self.reviewed_at.endswith("Z"):
            errors.append("reviewed_at must be a UTC timestamp ending in Z")
        if not self.workflow.strip():
            errors.append("workflow is required")

        for action in self.attempted_actions:
            errors.extend(action.validate())
        for evidence in self.completion_evidence:
            errors.extend(evidence.validate())
        for evidence in self.refused_action_evidence:
            errors.extend(evidence.validate())
        for event in self.journal_events:
            errors.extend(event.validate())

        action_ids = {action.action_id for action in self.attempted_actions}
        completed_action_ids = {action.action_id for action in self.attempted_actions if action.outcome in {"completed", "no_change"}}
        completion_action_ids = {evidence.action_id for evidence in self.completion_evidence}
        missing_completion = completed_action_ids - completion_action_ids
        if missing_completion:
            errors.append("completion evidence missing for actions: " + ", ".join(sorted(missing_completion)))
        unknown_completion = completion_action_ids - action_ids
        if unknown_completion:
            errors.append("completion evidence references unknown actions: " + ", ".join(sorted(unknown_completion)))

        refused_controls = {evidence.control_id for evidence in self.refused_action_evidence}
        missing_controls = REQUIRED_CONSEQUENTIAL_CONTROLS - refused_controls
        if missing_controls:
            errors.append("refused-action evidence missing for controls: " + ", ".join(sorted(missing_controls)))

        journal_ids = {event.event_id for event in self.journal_events}
        referenced_journal_ids = {action.journal_event_id for action in self.attempted_actions}
        referenced_journal_ids.update(evidence.journal_event_id for evidence in self.completion_evidence)
        referenced_journal_ids.update(evidence.journal_event_id for evidence in self.refused_action_evidence)
        missing_journal_ids = referenced_journal_ids - journal_ids
        if missing_journal_ids:
            errors.append("review references missing journal events: " + ", ".join(sorted(missing_journal_ids)))

        errors.extend(_validate_no_private_artifacts(self.browser_artifacts, "browser_artifacts"))
        if self.browser_artifacts:
            errors.append("browser_artifacts must be empty for committed post-action review fixtures")
        return errors


def review_from_dict(data: dict[str, Any]) -> DevHubPostActionHardeningReview:
    return DevHubPostActionHardeningReview(
        review_id=str(data.get("reviewId", "")),
        review_type=str(data.get("reviewType", "")),
        reviewed_at=str(data.get("reviewedAt", "")),
        workflow=str(data.get("workflow", "")),
        attempted_actions=tuple(
            AttemptedAction(
                action_id=str(item.get("actionId", "")),
                action_class=str(item.get("actionClass", "")),
                journal_event_id=str(item.get("journalEventId", "")),
                outcome=str(item.get("outcome", "")),
            )
            for item in data.get("attemptedActions", [])
        ),
        completion_evidence=tuple(
            CompletionEvidence(
                evidence_id=str(item.get("evidenceId", "")),
                action_id=str(item.get("actionId", "")),
                journal_event_id=str(item.get("journalEventId", "")),
                observed_outcome=str(item.get("observedOutcome", "")),
                source_evidence_ids=tuple(str(value) for value in item.get("sourceEvidenceIds", [])),
                user_visible_confirmation=str(item.get("userVisibleConfirmation", "")),
            )
            for item in data.get("completionEvidence", [])
        ),
        refused_action_evidence=tuple(
            RefusedActionEvidence(
                evidence_id=str(item.get("evidenceId", "")),
                control_id=str(item.get("controlId", "")),
                action_class=str(item.get("actionClass", "")),
                journal_event_id=str(item.get("journalEventId", "")),
                refusal_reason=str(item.get("refusalReason", "")),
                required_user_confirmation=str(item.get("requiredUserConfirmation", "")),
            )
            for item in data.get("refusedActionEvidence", [])
        ),
        journal_events=tuple(
            RedactedJournalEvent(
                event_id=str(item.get("eventId", "")),
                event_type=str(item.get("eventType", "")),
                redaction_status=str(item.get("redactionStatus", "")),
                payload=dict(item.get("payload", {})),
            )
            for item in data.get("journalEvents", [])
        ),
        browser_artifacts=dict(data.get("browserArtifacts", {})),
    )


def _validate_no_private_artifacts(value: Any, context: str) -> list[str]:
    errors: list[str] = []
    for path, item in _walk(value):
        if isinstance(item, dict):
            for key in item:
                normalized = str(key).replace("-", "_").lower()
                compact = normalized.replace("_", "")
                if normalized in FORBIDDEN_BROWSER_ARTIFACT_KEYS or compact in FORBIDDEN_BROWSER_ARTIFACT_KEYS:
                    errors.append(f"{context} contains forbidden private browser artifact key at {path}.{key}")
        if isinstance(item, str):
            if item != REDACTED_VALUE:
                for fragment in FORBIDDEN_VALUE_FRAGMENTS:
                    if fragment in item:
                        errors.append(f"{context} contains forbidden private artifact value at {path}")
    return errors


def _walk(value: Any, path: str = "$.") -> Iterable[tuple[str, Any]]:
    yield path.rstrip("."), value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, f"{path}{key}.")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}].")
