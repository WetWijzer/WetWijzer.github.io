from __future__ import annotations

from ppd.actions import (
    ActionClass,
    ActionKind,
    EXACT_CONFIRMATION_PROMPTS,
    checkpoint_allows,
    classify_action,
    exact_confirmation_matches,
)


def test_read_only_actions_are_allowed_without_confirmation() -> None:
    policy = classify_action("Review fees and payment balance for permit 24-000000")

    assert policy.kind is ActionKind.PAYMENT_REVIEW
    assert policy.action_class is ActionClass.READ_ONLY
    assert policy.exact_confirmation is None
    assert policy.may_execute is True
    assert checkpoint_allows("download permit status") is True


def test_reversible_draft_actions_are_allowed_without_confirmation() -> None:
    policy = classify_action("Prepare and save draft application fields")

    assert policy.kind is ActionKind.REVERSIBLE_DRAFT
    assert policy.action_class is ActionClass.REVERSIBLE_DRAFT
    assert policy.exact_confirmation is None
    assert policy.may_execute is True
    assert exact_confirmation_matches(policy, None) is True


def test_exact_confirmation_required_action_families() -> None:
    examples = [
        ("official upload final plans", ActionKind.OFFICIAL_UPLOAD),
        ("submit permit application", ActionKind.SUBMISSION),
        ("certify contractor statement", ActionKind.CERTIFICATION),
        ("cancel permit request", ActionKind.CANCELLATION),
        ("schedule inspection for tomorrow", ActionKind.INSPECTION_SCHEDULING),
        ("execute payment by card", ActionKind.PAYMENT_EXECUTION),
    ]

    for description, expected_kind in examples:
        policy = classify_action(description)
        assert policy.kind is expected_kind
        assert policy.action_class is ActionClass.EXACT_CONFIRMATION_REQUIRED
        assert policy.exact_confirmation == EXACT_CONFIRMATION_PROMPTS[expected_kind]
        assert policy.may_execute is True
        assert checkpoint_allows(description) is False
        assert checkpoint_allows(description, policy.exact_confirmation) is True


def test_confirmation_must_match_exactly() -> None:
    policy = classify_action("submit permit application")

    assert exact_confirmation_matches(policy, "I confirm this PP&D submission should proceed") is True
    assert exact_confirmation_matches(policy, "i confirm this pp&d submission should proceed") is False
    assert exact_confirmation_matches(policy, " I confirm this PP&D submission should proceed ") is False
    assert exact_confirmation_matches(policy, None) is False


def test_unsupported_handoffs_are_blocked_even_with_confirmation() -> None:
    examples = [
        "solve captcha before login",
        "complete MFA challenge",
        "create DevHub account",
        "reset password for applicant",
        "do something unknown",
    ]

    for description in examples:
        policy = classify_action(description)
        assert policy.kind is ActionKind.UNSUPPORTED_HANDOFF
        assert policy.action_class is ActionClass.UNSUPPORTED_HANDOFF
        assert policy.may_execute is False
        assert checkpoint_allows(description, "I confirm this PP&D submission should proceed") is False
