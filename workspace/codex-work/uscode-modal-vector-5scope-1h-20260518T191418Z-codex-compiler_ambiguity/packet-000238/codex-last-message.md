Implemented the modal ambiguity policy update in scope `modal.compiler.ambiguity` with a registry-driven signal-free pair path, and validated it with targeted tests.

Changed files:
- Added `signal_free_adaptive_ambiguity_targets(...)` and wired `supports_signal_free_adaptive_ambiguity_pair(...)` through it in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000238-20260518_194801/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:320).
- Updated adaptive ambiguity evaluation to merge registry policy targets into compiler target evaluation (prevents drift from hard-coded target specs) in [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000238-20260518_194801/ipfs_datasets_py/logic/modal/compiler.py:528).
- Added policy contract tests for required pairs and directionality in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000238-20260518_194801/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:61).

Tests run:
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` (passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy or adaptive_family_margin"` (passed)