"""Validation for PP&D guardrail bundle promotion preview v3.

The preview validator is intentionally side-effect free. It checks committed,
deterministic preview data before any promotion code is allowed to mutate active
policy state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


REQUIRED_NON_EMPTY_FIELDS = (
    "predicate_patch_candidates",
    "before_predicate_rows",
    "after_predicate_rows",
    "explanation_template_deltas",
    "blocked_action_regression_checks",
    "dependency_order",
    "rollback_checkpoints",
)

PRIVATE_FACT_KEYS = {
    "private_fact",
    "private_facts",
    "authenticated_fact",
    "authenticated_facts",
    "credential",
    "credentials",
    "cookie",
    "cookies",
    "session_token",
    "auth_state",
    "password",
    "payment_detail",
    "payment_details",
}

PRIVATE_FACT_VALUES = (
    "private",
    "authenticated",
    "credential",
    "cookie",
    "session",
    "password",
    "payment detail",
    "card number",
    "devhub_authenticated",
)

RAW_ARTIFACT_TERMS = (
    "raw crawl",
    "raw_crawl",
    "crawl body",
    "warc",
    "har",
    "trace.zip",
    "playwright trace",
    "browser session",
    "session storage",
    "local storage",
    "screenshot",
    "downloaded pdf",
    "raw pdf",
    ".pdf",
    ".har",
    ".warc",
    ".zip",
)

EXECUTION_CLAIM_TERMS = (
    "live llm executed",
    "llm executed",
    "devhub executed",
    "crawler executed",
    "processor executed",
    "ran live crawl",
    "ran the crawler",
    "ran devhub",
    "called devhub",
    "called processor",
    "live processor run",
    "live browser run",
)

OUTCOME_GUARANTEE_TERMS = (
    "will be approved",
    "guaranteed approval",
    "guarantee approval",
    "permit will issue",
    "permit will be issued",
    "legal compliance guaranteed",
    "lawful outcome guaranteed",
    "no legal risk",
)

CONSEQUENTIAL_ACTION_TERMS = (
    "final submission",
    "submit application",
    "submit permit",
    "submitted permit",
    "pay fee",
    "payment submitted",
    "submit payment",
    "final payment",
    "upload correction",
    "uploaded correction",
    "official upload",
    "schedule inspection",
    "scheduled inspection",
    "cancel inspection",
    "cancel permit",
    "certify acknowledgement",
    "certification submitted",
)

MUTATION_FLAG_GROUPS = (
    "guardrail",
    "prompt",
    "source",
    "surface_registry",
    "surface-registry",
    "monitoring",
    "release_state",
    "release-state",
    "agent_state",
    "agent-state",
)

TRUE_STRINGS = {"active", "enabled", "true", "yes", "mutate", "mutation", "write", "promote"}


@dataclass(frozen=True)
class PreviewValidationIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class PreviewValidationResult:
    ok: bool
    issues: tuple[PreviewValidationIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "issues": [
                {"code": issue.code, "path": issue.path, "message": issue.message}
                for issue in self.issues
            ],
        }


def validate_guardrail_bundle_promotion_preview_v3(preview: Mapping[str, Any]) -> PreviewValidationResult:
    """Return validation issues for a guardrail promotion preview v3 payload."""

    issues: list[PreviewValidationIssue] = []

    if preview.get("preview_version") != 3:
        issues.append(
            PreviewValidationIssue(
                "wrong_preview_version",
                "preview_version",
                "Guardrail bundle promotion preview must declare preview_version 3.",
            )
        )

    for field in REQUIRED_NON_EMPTY_FIELDS:
        if _is_empty(preview.get(field)):
            issues.append(
                PreviewValidationIssue(
                    f"missing_{field}",
                    field,
                    f"Promotion preview v3 requires non-empty {field}.",
                )
            )

    _validate_patch_candidate_citations(preview.get("predicate_patch_candidates"), issues)
    _scan_for_private_or_forbidden_content(preview, issues)
    _scan_for_active_mutation_flags(preview, issues)

    return PreviewValidationResult(ok=not issues, issues=tuple(issues))


def assert_guardrail_bundle_promotion_preview_v3(preview: Mapping[str, Any]) -> None:
    """Raise ValueError with stable issue codes when a preview is invalid."""

    result = validate_guardrail_bundle_promotion_preview_v3(preview)
    if result.ok:
        return
    codes = ", ".join(issue.code for issue in result.issues)
    raise ValueError(f"Invalid guardrail bundle promotion preview v3: {codes}")


def _validate_patch_candidate_citations(value: Any, issues: list[PreviewValidationIssue]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return

    for index, candidate in enumerate(value):
        path = f"predicate_patch_candidates[{index}]"
        if not isinstance(candidate, Mapping):
            issues.append(
                PreviewValidationIssue(
                    "predicate_patch_candidate_not_object",
                    path,
                    "Predicate patch candidates must be objects with citations.",
                )
            )
            continue
        citations = candidate.get("citations") or candidate.get("source_evidence_ids")
        if _is_empty(citations):
            issues.append(
                PreviewValidationIssue(
                    "uncited_predicate_patch_candidate",
                    path,
                    "Predicate patch candidates must cite public source evidence.",
                )
            )


def _scan_for_private_or_forbidden_content(value: Any, issues: list[PreviewValidationIssue]) -> None:
    for path, key, leaf in _walk(value):
        key_text = key.lower().replace("-", "_") if key else ""
        leaf_text = str(leaf).lower() if isinstance(leaf, (str, int, float, bool)) else ""

        if key_text in PRIVATE_FACT_KEYS or any(term in leaf_text for term in PRIVATE_FACT_VALUES):
            issues.append(
                PreviewValidationIssue(
                    "private_or_authenticated_fact",
                    path,
                    "Promotion previews must not contain private, authenticated, credential, session, or payment facts.",
                )
            )

        if any(term in leaf_text for term in RAW_ARTIFACT_TERMS):
            issues.append(
                PreviewValidationIssue(
                    "raw_artifact_reference",
                    path,
                    "Promotion previews must not reference raw crawl, PDF, session, browser, trace, HAR, WARC, or screenshot artifacts.",
                )
            )

        if any(term in leaf_text for term in EXECUTION_CLAIM_TERMS):
            issues.append(
                PreviewValidationIssue(
                    "live_execution_claim",
                    path,
                    "Promotion previews must not claim live LLM, DevHub, crawler, browser, or processor execution.",
                )
            )

        if any(term in leaf_text for term in OUTCOME_GUARANTEE_TERMS):
            issues.append(
                PreviewValidationIssue(
                    "outcome_guarantee",
                    path,
                    "Promotion previews must not guarantee legal or permitting outcomes.",
                )
            )

        if any(term in leaf_text for term in CONSEQUENTIAL_ACTION_TERMS):
            issues.append(
                PreviewValidationIssue(
                    "consequential_action_language",
                    path,
                    "Promotion previews must not include final submission, payment, upload, scheduling, cancellation, or certification language.",
                )
            )


def _scan_for_active_mutation_flags(value: Any, issues: list[PreviewValidationIssue]) -> None:
    for path, key, leaf in _walk(value):
        key_text = key.lower() if key else ""
        normalized_key = key_text.replace("_", "-")
        mentions_mutation_group = any(group in key_text or group in normalized_key for group in MUTATION_FLAG_GROUPS)
        mentions_mutation = "mutation" in key_text or "mutate" in key_text or "write" in key_text or "promote" in key_text
        if not mentions_mutation_group or not mentions_mutation:
            continue

        active = leaf is True
        if isinstance(leaf, str):
            active = leaf.strip().lower() in TRUE_STRINGS
        if active:
            issues.append(
                PreviewValidationIssue(
                    "active_mutation_flag",
                    path,
                    "Promotion preview v3 must not contain active guardrail, prompt, source, surface-registry, monitoring, release-state, or agent-state mutation flags.",
                )
            )


def _walk(value: Any, path: str = "", key: str = "") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{path}.{child_key_text}" if path else child_key_text
            yield from _walk(child_value, child_path, child_key_text)
        return

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child_value in enumerate(value):
            child_path = f"{path}[{index}]" if path else f"[{index}]"
            yield from _walk(child_value, child_path, key)
        return

    yield path or "$", key, value


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (str, bytes, bytearray)):
        return len(value.strip()) == 0 if isinstance(value, str) else len(value) == 0
    if isinstance(value, Sequence) or isinstance(value, Mapping):
        return len(value) == 0
    return False
