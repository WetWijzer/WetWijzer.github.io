"""Source-backed contract for attended Playwright and PDF draft work."""

from __future__ import annotations


def playwright_pdf_contract() -> dict[str, object]:
    return {
        "capability": "attended_draft_automation",
        "allowedActions": [
            "manual_login_handoff",
            "journal_replay",
            "reversible_draft_field_fill",
            "local_pdf_preview_fill",
        ],
        "blockedActions": [
            "official_upload",
            "permit_submission",
            "certification",
            "fee_payment",
            "account_security_transition",
            "inspection_scheduling",
        ],
        "requiresHumanAttendanceBeforeBrowserUse": True,
        "exactConfirmationBeforeOfficialAction": True,
    }
