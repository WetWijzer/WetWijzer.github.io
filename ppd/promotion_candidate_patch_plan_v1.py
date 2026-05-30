from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence

PLAN_ID = "promotion-candidate-patch-plan-v1"

REQUIRED_INPUTS = {
    "promotion-readiness-checklist-v2",
    "process-model-impact-proposal-v1",
    "guardrail-bundle-impact-proposal-v1",
    "user-gap-analysis-impact-proposal-v1",
    "agent-response-delta-proposal-v1",
}

ACTIVE_MUTATION_SCOPES = {
    "source",
    "document",
    "requirement",
    "process",
    "process_model",
    "guardrail",
    "prompt",
    "release_state",
    "agent_state",
}

PRIVATE_OR_BROWSER_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bauth(?:enticated|entication)?\b",
        r"\bprivate\s+(?:devhub|account|permit|case|session|browser|field|fact|value|upload)s?\b",
        r"\bbrowser\s+(?:artifact|context|profile|session|state)\b",
        r"\bcookie\b",
        r"\bcredential\b",
        r"\bpassword\b",
        r"\bmfa\b",
        r"\bsession\s+(?:artifact|cookie|file|state|storage|token)\b",
        r"\bstorage[_-]?state\b",
        r"\bauth[_-]?state\b",
        r"\bplaywright\s+(?:trace|session|artifact)\b",
        r"\btoken\b",
    )
)

RAW_DATA_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\braw\s+(?:crawl|html|pdf|download|body|data)\b",
        r"\braw[_-]?(?:crawl|html|pdf|download|body|data)\b",
        r"\bcrawl[_-]?(?:dump|output|body)\b",
        r"\bdownloaded\s+(?:data|document|file|pdf)\b",
        r"\bdownloaded[_-]?(?:data|document|file|pdf)\b",
        r"\bpdf\s+(?:binary|download|artifact|dump)\b",
        r"\b\.har\b",
        r"\bhar\s+(?:file|artifact|path)\b",
        r"\bscreenshot\b",
        r"\btrace\.zip\b",
    )
)

OUTCOME_GUARANTEE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bguarantee(?:d|s)?\s+(?:approval|issuance|permit|inspection|compliance|outcome)\b",
        r"\bpermit\s+will\s+be\s+(?:approved|issued|accepted)\b",
        r"\bwill\s+(?:be\s+)?(?:approved|issued|accepted|pass inspection|be compliant)\b",
        r"\bensures?\s+(?:approval|issuance|acceptance|permit|inspection|compliance)\b",
        r"\blegally\s+(?:valid|sufficient|approved|compliant)\b",
        r"\blegal\s+advice\b",
    )
)

CONSEQUENTIAL_ACTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(?:execute|perform|complete|take)\s+(?:the\s+)?(?:official|final|consequential)\s+action\b",
        r"\bclick\s+(?:submit|pay|certify|schedule|cancel|upload)\b",
        r"\bsubmit\s+(?:application|permit|payment|correction|plans?)\b",
        r"\bupload\s+(?:correction|to\s+official\s+record|plans?|document)\b",
        r"\bcertify\s+(?:acknowledgement|and\s+submit)\b",
        r"\bmake\s+(?:payment|official)\b",
        r"\bpay\s+(?:fee|fees|invoice)\b",
        r"\bschedule\s+inspection\b",
        r"\bcancel\s+(?:inspection|permit|application|request)\b",
    )
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    row_id: str | None = None

    def as_dict(self) -> dict[str, str]:
        result = {"code": self.code, "message": self.message}
        if self.row_id is not None:
            result["row_id"] = self.row_id
        return result


class PromotionCandidatePatchPlanV1ValidationError(ValueError):
    def __init__(self, issues: Sequence[ValidationIssue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(f"{issue.code}: {issue.message}" for issue in self.issues)
        super().__init__(detail)


def validate_promotion_candidate_patch_plan_v1(plan: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if plan.get("id") != PLAN_ID:
        issues.append(ValidationIssue("invalid_plan_id", f"id must be {PLAN_ID}"))
    if plan.get("version") != 1:
        issues.append(ValidationIssue("invalid_version", "version must be 1"))
    if plan.get("status") != "inactive_fixture_only":
        issues.append(ValidationIssue("invalid_status", "status must be inactive_fixture_only"))

    consumes = plan.get("consumes")
    if not isinstance(consumes, list) or set(consumes) != REQUIRED_INPUTS:
        issues.append(ValidationIssue("missing_required_inputs", "consumes must list every required promotion candidate patch plan input"))

    gates = plan.get("dependency_gates")
    if not isinstance(gates, list) or not gates:
        issues.append(ValidationIssue("missing_dependency_gates", "dependency_gates must be non-empty"))
        gate_ids: set[str] = set()
    else:
        gate_ids = set()
        for index, gate in enumerate(gates):
            if not isinstance(gate, Mapping):
                issues.append(ValidationIssue("invalid_dependency_gate", f"dependency_gates[{index}] must be an object"))
                continue
            gate_id = _text(gate.get("id"))
            if not gate_id:
                issues.append(ValidationIssue("missing_dependency_gate_id", f"dependency_gates[{index}].id is required"))
            else:
                gate_ids.add(gate_id)
            if not _string_list(gate.get("evidence")):
                issues.append(ValidationIssue("uncited_dependency_gate", f"dependency_gates[{index}].evidence must be non-empty"))

    rows = plan.get("inactive_fixture_update_rows")
    if not isinstance(rows, list) or not rows:
        issues.append(ValidationIssue("missing_patch_rows", "inactive_fixture_update_rows must be non-empty"))
        rows = []

    seen_orders: list[int] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            issues.append(ValidationIssue("invalid_patch_row", f"inactive_fixture_update_rows[{index}] must be an object"))
            continue

        row_id = _text(row.get("id")) or f"index:{index}"
        if not row_id:
            issues.append(ValidationIssue("missing_patch_row_id", "patch row id is required", row_id))
        order = row.get("order")
        if isinstance(order, int):
            seen_orders.append(order)
        else:
            issues.append(ValidationIssue("missing_patch_row_order", "patch row order must be an integer", row_id))

        if not _string_list(row.get("citations")):
            issues.append(ValidationIssue("uncited_patch_row", "patch row citations must be non-empty", row_id))
        if not _text(row.get("affected_fixture_family_id")):
            issues.append(ValidationIssue("missing_affected_fixture_family_id", "patch row must name affected_fixture_family_id", row_id))
        if not _string_list(row.get("dependency_gates")):
            issues.append(ValidationIssue("missing_dependency_gates", "patch row dependency_gates must be non-empty", row_id))
        else:
            for gate_id in row.get("dependency_gates", []):
                if gate_id not in gate_ids:
                    issues.append(ValidationIssue("unknown_dependency_gate", f"dependency gate {gate_id!r} is not declared", row_id))
        if not _text(row.get("reviewer_owner")):
            issues.append(ValidationIssue("missing_reviewer_owner", "patch row reviewer_owner is required", row_id))
        if not _text(row.get("rollback_note")):
            issues.append(ValidationIssue("missing_rollback_note", "patch row rollback_note is required", row_id))
        if row.get("active_mutation") is not False:
            issues.append(ValidationIssue("active_mutation_flag", "patch row active_mutation must be false", row_id))

        issues.extend(_reject_unsafe_content(row, row_id))
        issues.extend(_reject_active_mutation_flags(row, row_id))

    if seen_orders and seen_orders != list(range(1, len(seen_orders) + 1)):
        issues.append(ValidationIssue("invalid_patch_row_order", "patch row orders must be contiguous starting at 1"))

    issues.extend(_reject_unsafe_content(plan, None))
    issues.extend(_reject_active_mutation_flags(plan, None))
    _validate_non_mutation_scope(plan.get("non_mutation_scope"), issues)

    return _dedupe_issues(issues)


def assert_valid_promotion_candidate_patch_plan_v1(plan: Mapping[str, Any]) -> None:
    issues = validate_promotion_candidate_patch_plan_v1(plan)
    if issues:
        raise PromotionCandidatePatchPlanV1ValidationError(issues)


def _validate_non_mutation_scope(value: Any, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, Mapping):
        issues.append(ValidationIssue("missing_non_mutation_scope", "non_mutation_scope must be an object"))
        return
    expected = {
        "active_process_models",
        "active_guardrail_bundles",
        "prompts",
        "release_state",
        "agent_state",
        "live_sources",
        "devhub_artifacts",
    }
    if set(value) != expected:
        issues.append(ValidationIssue("invalid_non_mutation_scope", "non_mutation_scope must enumerate the expected active-state boundaries"))
    for key, flag in value.items():
        if flag is not False:
            issues.append(ValidationIssue("active_mutation_flag", f"non_mutation_scope.{key} must be false"))


def _reject_unsafe_content(value: Any, row_id: str | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    policies = (
        ("private_authenticated_session_or_browser_artifact", PRIVATE_OR_BROWSER_PATTERNS),
        ("raw_crawl_pdf_or_downloaded_data", RAW_DATA_PATTERNS),
        ("legal_or_permitting_outcome_guarantee", OUTCOME_GUARANTEE_PATTERNS),
        ("consequential_action_execution_language", CONSEQUENTIAL_ACTION_PATTERNS),
    )
    for path, text in _walk_strings(value):
        for code, patterns in policies:
            if any(pattern.search(text) for pattern in patterns):
                issues.append(ValidationIssue(code, f"prohibited content at {_format_path(path)}", row_id))
    return issues


def _reject_active_mutation_flags(value: Any, row_id: str | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, leaf in _walk(value):
        key = path[-1].replace("-", "_").lower() if path else ""
        if not _truthy(leaf):
            continue
        if _is_active_mutation_key(key):
            issues.append(ValidationIssue("active_mutation_flag", f"active mutation flag at {_format_path(path)} is not allowed", row_id))
    return issues


def _is_active_mutation_key(key: str) -> bool:
    if key == "active_mutation":
        return True
    for scope in ACTIVE_MUTATION_SCOPES:
        if key in {
            f"active_{scope}",
            f"active_{scope}_mutation",
            f"{scope}_mutation",
            f"{scope}_mutation_enabled",
            f"apply_to_active_{scope}",
            f"mutate_active_{scope}",
        }:
            return True
    return False


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "apply", "enable", "enabled", "mutate", "true", "yes"}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return value is not None


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _walk(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = path + (str(key),)
            yield child_path, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = path + (str(index),)
            yield child_path, child
            yield from _walk(child, child_path)


def _walk_strings(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_strings(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_strings(child, path + (str(index),))


def _format_path(path: tuple[str, ...]) -> str:
    if not path:
        return "$"
    return "$" + "".join(f"[{part!r}]" for part in path)


def _dedupe_issues(issues: Sequence[ValidationIssue]) -> list[ValidationIssue]:
    result: list[ValidationIssue] = []
    seen: set[tuple[str, str | None, str]] = set()
    for issue in issues:
        key = (issue.code, issue.row_id, issue.message)
        if key not in seen:
            seen.add(key)
            result.append(issue)
    return result
