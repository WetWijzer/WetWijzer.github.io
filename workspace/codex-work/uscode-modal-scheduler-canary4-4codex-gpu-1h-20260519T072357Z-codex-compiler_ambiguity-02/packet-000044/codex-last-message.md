Implemented the compiler ambiguity-policy update for the `compiler_ambiguity` scope.

- Added `frame -> dynamic` to the signal-free adaptive ambiguity pair policy so close-margin frame/dynamic conflicts now always emit explicit adaptive ambiguity: [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000044-20260519_074109/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:143).
- Extended frame-family lexical target mapping to include dynamic scope/cue evidence in adaptive ambiguity targeting: [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000044-20260519_074109/ipfs_datasets_py/logic/modal/compiler.py:953).
- Updated registry tests for the new pair and ordering: [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000044-20260519_074109/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:137).
- Added a focused compiler test proving explicit `adaptive_frame_dynamic_outvoted_margin_low` emission under signal-free policy conditions: [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000044-20260519_074109/tests/unit_tests/logic/modal/test_modal_codec.py:3175).

Tests run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` -> `11 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_dynamic_adaptive_ambiguity"` -> `1 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_frame"` -> `5 passed`