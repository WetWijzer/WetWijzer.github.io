Implemented a deterministic `compiler_ambiguity` policy expansion so low-margin family conflicts now surface explicit adaptive ambiguities for the missing pairs.

**Changes**
- Added signal-free adaptive pair coverage for `deontic -> epistemic` and `conditional_normative -> frame` in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000041-20260518_230952/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33).
- Updated registry policy tests for coverage and directional target ordering in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000041-20260518_230952/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:69).
- Added compiler ambiguity regression tests to ensure explicit adaptive ambiguities are emitted for the two new signal-free pairs:
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000041-20260518_230952/tests/unit_tests/logic/modal/test_modal_codec.py:2851)
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000041-20260518_230952/tests/unit_tests/logic/modal/test_modal_codec.py:3413)

**Validation**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → 9 passed
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_conditional_frame_adaptive_ambiguity or signal_free_pair_policy_for_deontic_epistemic_adaptive_ambiguity"` → 2 passed