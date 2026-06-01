# Activation Checklist V4

Status: inactive and disabled. This artifact is for read-only validation only.

## Smoke Replay Reference

- Smoke replay fixture: `ppd/tests/fixtures/activation_checklist_v4/replay-placeholder.json`
- Replay evidence remains deterministic and contains no private DevHub values.

## Reviewer-Controlled Activation Prerequisites

- Reviewer-controlled activation prerequisites are not satisfied.
- Reviewer must confirm public-source scope, fixture-only smoke replay, and no write-capable DevHub session state.

## Signoff Placeholders

| Role | Sign-off placeholder | State |
| --- | --- | --- |
| Source reviewer | TBD | not signed |
| Guardrail reviewer | TBD | not signed |
| Activation reviewer | TBD | not signed |

## Source Freshness Hold Clearance Criteria

- Source freshness hold clearance criteria require current official PP&D source hashes, freshness report review, and reviewer approval before any activation decision.
- If source freshness is stale, changed, or unknown, the hold remains uncleared.

## Rollback Checkpoint Rows

| Checkpoint row | Rollback trigger | Required reviewer action |
| --- | --- | --- |
| pre-activation fixture replay | replay mismatch | keep inactive and file validation note |
| source freshness review | stale official source | keep hold active and recrawl public sources |
| post-activation smoke checks | smoke check failure | disable activation and restore previous read-only state |

## Post-Activation Smoke Checks

- Post-activation smoke checks must verify read-only guardrails, refusal of official actions, and fixture replay consistency.
- These checks are placeholders and do not authorize activation.

## Agent Notification Notes

- Agent notification notes must state that activation remains inactive until reviewer signoff and source freshness hold clearance are recorded.
- Agents must continue refusing official PP&D submissions, uploads, payments, scheduling, cancellation, certification, or legal guarantees.

## Validation Commands

- `python3 ppd/daemon/ppd_daemon.py --self-test`
