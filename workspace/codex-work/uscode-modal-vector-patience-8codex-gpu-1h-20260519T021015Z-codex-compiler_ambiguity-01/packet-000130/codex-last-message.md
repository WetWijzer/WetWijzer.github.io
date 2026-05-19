Implemented a deterministic ambiguity-policy ordering improvement so priority adaptive family pairs are surfaced first and remain directional.

**Changes**
- Added `priority_signal_free_adaptive_ambiguity_targets(...)` in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000130-20260519_025345/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py).
- Updated [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000130-20260519_025345/ipfs_datasets_py/logic/modal/compiler.py) to:
  - Order adaptive target-family evaluation with priority pairs first via `_ordered_adaptive_target_families(...)`.
  - Build compiled-primary competing targets with priority targets first, then remaining declared policy targets (deduped, deterministic).
- Added registry coverage test for the new priority-target helper in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000130-20260519_025345/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py).
- Added compiler ordering test in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000130-20260519_025345/tests/unit_tests/logic/modal/test_modal_codec.py).

**Tests run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "orders_priority_adaptive_targets or signal_free_pair_policy_for_conditional_deontic_adaptive_ambiguity or signal_free_pair_policy_for_temporal_deontic_adaptive_ambiguity or signal_free_pair_policy_for_temporal_frame_adaptive_ambiguity"`
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py tests/unit_tests/logic/modal/test_modal_codec.py -k "adaptive_family_margin_low or priority_signal_free_adaptive_targets or orders_priority_adaptive_targets or signal_free_pair_policy_for_temporal_deontic_adaptive_ambiguity or signal_free_pair_policy_for_conditional_deontic_adaptive_ambiguity or signal_free_pair_policy_for_temporal_frame_adaptive_ambiguity"`

All passed.