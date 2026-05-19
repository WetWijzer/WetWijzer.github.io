Implemented a focused compiler-registry cue refinement in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000030-20260519_081236/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:391):

- Added calibrated backfill floors for ambiguous family pairs:
  - `frame -> deontic/temporal` in non-editorial frame context (`_FRAME_COMPETING_SCOPE_BACKFILL_WEIGHT`).
  - Sparse `deontic <-> temporal` cross-scope conflicts (`_SPARSE_CROSS_SCOPE_BACKFILL_WEIGHT`).
- Wired new deterministic passes into `_weighted_modal_family_counts` so they run after existing soft-cap/backfill logic.
- Added helper functions:
  - `_apply_frame_competing_scope_backfill` ([spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000030-20260519_081236/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1509))
  - `_apply_sparse_cross_scope_backfill` ([spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000030-20260519_081236/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1545))

Added targeted coverage in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000030-20260519_081236/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:566):

- Stronger non-editorial `frame -> deontic` share support.
- Stronger non-editorial `frame -> temporal` share support.
- Sparse `deontic -> temporal` backfill under temporal scope phrase.
- Sparse `temporal -> deontic` backfill under deontic scope phrase.

Validation run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` -> 11 passed
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py` -> 84 passed
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "surfaces_deontic_temporal_adaptive_ambiguity or treats_under_this_section_as_deontic_frame_adaptive_signal or treats_transferred_as_frame_scope_ambiguity_signal or uses_bm25_frame_support_for_temporal_adaptive_frame_ambiguity or caps_repeated_generic_frame_cues_against_deontic_scope or caps_repeated_generic_frame_cues_against_conditional_scope"` -> 6 passed