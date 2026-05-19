Implemented a deterministic modal-family cue-rule refinement focused on family-pair competition and backfill evidence.

- Updated [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000107-20260519_030924/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:383):
  - Added `_CONDITIONAL_COMPETING_SCOPE_SOFT_CAP`.
  - Expanded deontic soft-cap competition to include epistemic signals/cues.
  - Added `_apply_conditional_competing_scope_soft_cap` into weighted-family scoring.
  - Relaxed strict gating for existing conditional/frame backfills to allow scope-token-driven support (not just phrase-level/statutory triggers).
  - Added new deterministic backfills for `frame->conditional_normative` and `temporal->frame`.
- Added targeted regression tests in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000107-20260519_030924/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:839) covering:
  - deontic vs epistemic competition soft-cap,
  - conditional soft-cap under deontic competition,
  - token-driven conditional/deontic/temporal/frame backfills for the problematic pair directions.

Tests run and passing:
1. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "epistemic_competition or soft_caps_repeated_conditional_logits or backfills_deontic_share_for_conditional_scope_with_deontic_tokens or backfills_temporal_share_for_conditional_scope_with_temporal_tokens or backfills_conditional_share_for_frame_scope_with_statutory_condition_reference or backfills_deontic_share_for_frame_scope_with_deontic_tokens or backfills_temporal_share_for_frame_scope_with_temporal_tokens or backfills_frame_share_for_dense_temporal_scope_with_frame_context"` (8 passed)
2. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py` (80 passed)
3. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "surfaces_temporal_conditional_family_outvote_ambiguity or surfaces_temporal_frame_family_outvote_ambiguity or surfaces_temporal_scope_family_outvote_ambiguity or surfaces_frame_scope_family_outvote_ambiguity or surfaces_conditional_scope_family_outvote_ambiguity or surfaces_deontic_scope_family_outvote_ambiguity"` (6 passed)