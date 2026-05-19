Implemented a scoped `compiler_registry` policy refinement by expanding **priority** adaptive-family pairs.

**Changes**
- Added `temporal -> conditional_normative` to `PRIORITY_SIGNAL_FREE_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS` in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000028-20260519_075652/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:182).
- Added `frame -> frame` to the same priority list in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000028-20260519_075652/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:210).
- Updated priority-policy assertions and ordered-target expectations in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000028-20260519_075652/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:195).

**Tests**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` (11 passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "uses_signal_free_pair_policy_for_temporal_conditional_adaptive_ambiguity or surfaces_frame_self_pair_adaptive_ambiguity_for_low_runner_up_margin or treats_zero_margin_frame_temporal_priority_pair_as_outvoted_adaptive_ambiguity"` (3 passed)