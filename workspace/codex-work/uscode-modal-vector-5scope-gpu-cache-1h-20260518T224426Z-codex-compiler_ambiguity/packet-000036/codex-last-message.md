Implemented a narrow compiler-ambiguity policy extension for `frame -> deontic` adaptive conflicts.

- Added `frame -> deontic` to signal-free adaptive ambiguity policy and priority policy in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000036-20260518_224738/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33).
- Extended adaptive ambiguity signal routing for predicted `frame` family to consider deontic scope/cue evidence in [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000036-20260518_224738/ipfs_datasets_py/logic/modal/compiler.py:650).
- Updated registry coverage tests in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000036-20260518_224738/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:69).
- Added a new compiler test for explicit signal-free `adaptive_frame_deontic_outvoted_margin_low` ambiguity in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000036-20260518_224738/tests/unit_tests/logic/modal/test_modal_codec.py:2418).

Validation run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` -> `9 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_frame_deontic_adaptive_ambiguity or signal_free_pair_policy_for_hybrid_frame_adaptive_ambiguity or signal_free_pair_policy_for_deontic_frame_adaptive_ambiguity"` -> `3 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_ and adaptive_ambiguity"` -> `8 passed`