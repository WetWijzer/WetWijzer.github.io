from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "pytest", "ppd/tests/test_post_recompile_agent_readiness_replay_v4.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return data


def build_post_recompile_agent_readiness_replay_v4(
    reviewer_packet_path: Path,
    synthetic_requests_path: Path,
) -> dict[str, Any]:
    reviewer_packet = _load_json(reviewer_packet_path)
    synthetic_requests = _load_json(synthetic_requests_path)

    missing_prompts = list(reviewer_packet.get("missing_information_prompts", []))
    stale_paths = set(reviewer_packet.get("stale_evidence_paths", []))
    blocked_action_rules = reviewer_packet.get("blocked_consequential_or_financial_actions", [])
    explanation_templates = reviewer_packet.get("explanation_templates", {})
    required_template_ids = set(explanation_templates.get("required", []))
    available_template_ids = set(explanation_templates.get("available", []))

    affected_missing_information_prompts: list[dict[str, Any]] = []
    blocked_stale_evidence_paths: list[dict[str, Any]] = []
    blocked_consequential_or_financial_actions: list[dict[str, Any]] = []
    reversible_draft_only_next_actions: list[dict[str, Any]] = []

    for request in synthetic_requests.get("agent_requests", []):
        request_id = request.get("id")
        request_missing = set(request.get("missing_information", []))
        for prompt in missing_prompts:
            prompt_id = prompt.get("id")
            if prompt_id in request_missing:
                affected_missing_information_prompts.append(
                    {
                        "request_id": request_id,
                        "prompt_id": prompt_id,
                        "prompt": prompt.get("prompt"),
                    }
                )

        evidence_path = request.get("evidence_path")
        if evidence_path in stale_paths:
            blocked_stale_evidence_paths.append(
                {
                    "request_id": request_id,
                    "path": evidence_path,
                    "reason": "stale evidence is blocked after guardrail recompile",
                }
            )

        action_kind = request.get("action_kind")
        action_risk = request.get("action_risk")
        if action_risk in {"consequential", "financial"}:
            matching_rule = next(
                (
                    rule for rule in blocked_action_rules
                    if rule.get("action_kind") == action_kind or rule.get("action_risk") == action_risk
                ),
                {},
            )
            blocked_consequential_or_financial_actions.append(
                {
                    "request_id": request_id,
                    "action_kind": action_kind,
                    "action_risk": action_risk,
                    "reason": matching_rule.get("reason", "consequential or financial actions require manual handling"),
                }
            )

        if request.get("draft_only") is True and request.get("reversible") is True:
            reversible_draft_only_next_actions.append(
                {
                    "request_id": request_id,
                    "next_action": request.get("next_action"),
                    "status": "allowed_as_reversible_draft_only",
                }
            )

    return {
        "replay_version": "post_recompile_agent_readiness_replay_v4",
        "source_fixtures": {
            "reviewer_packet": str(reviewer_packet_path),
            "synthetic_requests": str(synthetic_requests_path),
        },
        "affected_missing_information_prompts": affected_missing_information_prompts,
        "blocked_stale_evidence_paths": blocked_stale_evidence_paths,
        "blocked_consequential_or_financial_actions": blocked_consequential_or_financial_actions,
        "reversible_draft_only_next_actions": reversible_draft_only_next_actions,
        "explanation_template_coverage": {
            "required": sorted(required_template_ids),
            "available": sorted(available_template_ids),
            "missing": sorted(required_template_ids - available_template_ids),
            "covered": sorted(required_template_ids & available_template_ids),
        },
        "manual_handoff_reminders": list(reviewer_packet.get("manual_handoff_reminders", [])),
        "rollback_notes": list(reviewer_packet.get("rollback_notes", [])),
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "prohibited_activity_confirmation": {
            "opened_devhub": False,
            "read_private_documents": False,
            "mutated_active_guardrails": False,
            "uploaded_or_submitted": False,
            "paid_or_scheduled": False,
            "made_legal_or_permitting_guarantees": False,
        },
    }


def main() -> None:
    fixture_dir = Path(__file__).parent / "tests" / "fixtures" / "post_recompile_agent_readiness_replay_v4"
    report = build_post_recompile_agent_readiness_replay_v4(
        fixture_dir / "guardrail_recompile_reviewer_packet_v4.json",
        fixture_dir / "synthetic_agent_requests_v4.json",
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
