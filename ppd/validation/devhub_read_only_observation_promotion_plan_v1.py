"""Validation for DevHub read-only observation promotion plan v1.

The validator is intentionally fixture-friendly and side-effect free. It accepts
only redacted, attended, read-only observation plans and rejects evidence or
flags that would imply authenticated private-data capture, browser artifact
persistence, write-capable DevHub actions, or active state mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ValidationFinding:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    findings: tuple[ValidationFinding, ...]


PRIVATE_ACCOUNT_KEYS = frozenset(
    {
        "account_email",
        "account_id",
        "account_number",
        "account_phone",
        "account_username",
        "auth_state",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "devhub_account_value",
        "email",
        "mfa_secret",
        "password",
        "permit_private_value",
        "private_account_value",
        "private_account_values",
        "session_token",
        "storage_state",
        "token",
    }
)

BROWSER_ARTIFACT_TERMS = frozenset(
    {
        ".har",
        ".jpeg",
        ".jpg",
        ".png",
        ".trace",
        ".webm",
        "browser artifact",
        "browser_artifact",
        "har file",
        "har_path",
        "record_video",
        "screenshot",
        "screenshot_path",
        "storage_state",
        "trace file",
        "trace.zip",
        "trace_path",
        "video_path",
    }
)

WRITE_CAPABLE_TERMS = frozenset(
    {
        "attach",
        "cancel",
        "certify",
        "checkout",
        "click submit",
        "enter payment",
        "fill",
        "finalize",
        "pay",
        "payment",
        "press submit",
        "purchase",
        "save draft",
        "schedule",
        "submit",
        "type into",
        "upload",
        "withdraw",
        "write-capable",
        "write_capable",
    }
)

AUTOMATED_ACCOUNT_TERMS = frozenset(
    {
        "automate account creation",
        "automate captcha",
        "automate login",
        "automate mfa",
        "automated account creation",
        "automated captcha",
        "automated login",
        "automated mfa",
        "captcha solver",
        "create account",
        "mfa automation",
        "password recovery",
        "register account",
        "solve captcha",
    }
)

CONSEQUENTIAL_TERMS = frozenset(
    {
        "cancellation",
        "cancel permit",
        "certification",
        "certify acknowledgement",
        "inspection scheduling",
        "make payment",
        "payment",
        "schedule inspection",
        "submit application",
        "submission",
        "upload correction",
        "upload document",
        "upload plans",
    }
)

MUTATION_FLAG_PATHS = (
    ("mutations", "devhub"),
    ("mutations", "surface_registry"),
    ("mutations", "guardrail"),
    ("mutations", "prompt"),
    ("mutations", "release_state"),
    ("mutations", "agent_state"),
    ("mutation_flags", "devhub"),
    ("mutation_flags", "surface_registry"),
    ("mutation_flags", "guardrail"),
    ("mutation_flags", "prompt"),
    ("mutation_flags", "release_state"),
    ("mutation_flags", "agent_state"),
)

REQUIRED_BOOLEAN_FIELDS = (
    ("redaction", "redacts_private_values", True),
    ("redaction", "browser_artifacts_allowed", False),
    ("attendance", "required", True),
    ("attendance", "automated_login_allowed", False),
    ("attendance", "automated_captcha_mfa_allowed", False),
)


def validate_devhub_read_only_observation_promotion_plan_v1(plan: Mapping[str, Any]) -> ValidationResult:
    findings: list[ValidationFinding] = []

    if not isinstance(plan, Mapping):
        return ValidationResult(
            ok=False,
            findings=(
                ValidationFinding(
                    "invalid_plan_type",
                    "$",
                    "promotion plan must be a JSON object",
                ),
            ),
        )

    mode = str(plan.get("mode", "")).strip().lower()
    if mode != "read_only_observation":
        findings.append(
            ValidationFinding(
                "not_read_only_observation",
                "$.mode",
                "DevHub observation promotion must declare mode read_only_observation",
            )
        )

    scope = str(plan.get("scope", "")).strip().lower()
    if scope and scope != "devhub":
        findings.append(
            ValidationFinding(
                "invalid_scope",
                "$.scope",
                "promotion plan v1 is limited to DevHub observations",
            )
        )

    findings.extend(_required_boolean_findings(plan))
    findings.extend(_mutation_flag_findings(plan))
    findings.extend(_recursive_content_findings(plan))
    findings.extend(_action_evidence_findings(plan))

    return ValidationResult(ok=not findings, findings=tuple(findings))


def assert_valid_devhub_read_only_observation_promotion_plan_v1(plan: Mapping[str, Any]) -> None:
    result = validate_devhub_read_only_observation_promotion_plan_v1(plan)
    if not result.ok:
        details = "; ".join(f"{finding.code} at {finding.path}" for finding in result.findings)
        raise ValueError(details)


def _required_boolean_findings(plan: Mapping[str, Any]) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    for first, second, expected in REQUIRED_BOOLEAN_FIELDS:
        actual = _get_path(plan, (first, second))
        if actual is not expected:
            findings.append(
                ValidationFinding(
                    "missing_or_invalid_redaction_attendance_field",
                    f"$.{first}.{second}",
                    f"required field must be {expected!r}",
                )
            )
    return tuple(findings)


def _mutation_flag_findings(plan: Mapping[str, Any]) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    for path in MUTATION_FLAG_PATHS:
        actual = _get_path(plan, path)
        if actual is True:
            findings.append(
                ValidationFinding(
                    "active_mutation_flag",
                    "$" + "".join(f".{part}" for part in path),
                    "read-only observation promotion cannot carry active mutation flags",
                )
            )
    return tuple(findings)


def _recursive_content_findings(plan: Mapping[str, Any]) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    for path, key, value in _walk(plan):
        key_text = str(key).strip().lower() if key is not None else ""
        value_text = str(value).strip().lower() if isinstance(value, str) else ""
        combined = " ".join(part for part in (key_text, value_text) if part)

        if key_text in PRIVATE_ACCOUNT_KEYS:
            findings.append(
                ValidationFinding(
                    "private_account_value",
                    path,
                    "private account values or credential-like fields are not promotion evidence",
                )
            )

        if _contains_any(combined, BROWSER_ARTIFACT_TERMS):
            findings.append(
                ValidationFinding(
                    "browser_artifact",
                    path,
                    "screenshots, traces, HAR files, storage state, and browser artifacts are not allowed",
                )
            )

        if _contains_any(combined, AUTOMATED_ACCOUNT_TERMS):
            findings.append(
                ValidationFinding(
                    "automated_login_or_account_handling",
                    path,
                    "login, CAPTCHA, MFA, account creation, and password recovery must remain attended/manual",
                )
            )

        if _contains_any(combined, CONSEQUENTIAL_TERMS):
            findings.append(
                ValidationFinding(
                    "consequential_action_language",
                    path,
                    "certification, submission, payment, upload, scheduling, and cancellation language is outside read-only observation",
                )
            )

    return tuple(findings)


def _action_evidence_findings(plan: Mapping[str, Any]) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    evidence = plan.get("evidence", [])
    if not isinstance(evidence, Sequence) or isinstance(evidence, (str, bytes)):
        return (
            ValidationFinding(
                "invalid_evidence",
                "$.evidence",
                "evidence must be a list of redacted read-only observation records",
            ),
        )

    for index, item in enumerate(evidence):
        item_path = f"$.evidence[{index}]"
        if not isinstance(item, Mapping):
            findings.append(
                ValidationFinding(
                    "invalid_evidence_item",
                    item_path,
                    "evidence entries must be objects",
                )
            )
            continue

        category = str(item.get("action_category", "")).lower()
        action = str(item.get("action", item.get("observed_action", ""))).lower()
        evidence_type = str(item.get("evidence_type", "")).lower()
        write_capable = item.get("write_capable") is True or item.get("can_write") is True

        if write_capable or category in {"reversible_draft", "consequential_official", "financial", "write_capable"}:
            findings.append(
                ValidationFinding(
                    "write_capable_action_evidence",
                    item_path,
                    "promotion evidence must not include write-capable, reversible draft, official, or financial actions",
                )
            )

        if evidence_type and evidence_type != "redacted_dom_summary":
            findings.append(
                ValidationFinding(
                    "unsupported_evidence_type",
                    f"{item_path}.evidence_type",
                    "only redacted DOM summary evidence is allowed",
                )
            )

        if _contains_any(action, WRITE_CAPABLE_TERMS):
            findings.append(
                ValidationFinding(
                    "write_capable_action_evidence",
                    item_path,
                    "observed action text implies write-capable DevHub behavior",
                )
            )

    return tuple(findings)


def _walk(value: Any, path: str = "$", key: str | None = None) -> Iterable[tuple[str, str | None, Any]]:
    yield path, key, value
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_path = f"{path}.{child_key}"
            yield from _walk(child_value, child_path, str(child_key))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            yield from _walk(child_value, f"{path}[{index}]", None)


def _get_path(mapping: Mapping[str, Any], path: Sequence[str]) -> Any:
    current: Any = mapping
    for part in path:
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)
