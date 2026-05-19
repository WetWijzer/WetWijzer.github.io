Implemented a focused compiler-registry refinement for adaptive modal family cue conflicts.

**Changes**
- Added missing signal-free adaptive policy pair `alethic->dynamic` in the registry pair table.
  - [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000085-20260519_023119/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33)
- Generalized compiled-primary adaptive pair handling to use directional policy targets from the registry (instead of hardcoded per-family subsets), while excluding self-pairs.
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000085-20260519_023119/ipfs_datasets_py/logic/modal/compiler.py:805)
- Refined adaptive target-signal mapping:
  - `temporal -> deontic` now considers `has_deontic_cue` in addition to scope.
  - `conditional_normative` now maps target signals for `temporal` and `frame`.
  - `alethic` now maps target signal for `dynamic`.
  - Removed duplicated `alethic` branch.
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000085-20260519_023119/ipfs_datasets_py/logic/modal/compiler.py:839)

**Tests updated**
- Registry expectations updated for `alethic->dynamic`.
  - [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000085-20260519_023119/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:84)
- Added new modal-compiler test for signal-free `alethic->dynamic` adaptive ambiguity.
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000085-20260519_023119/tests/unit_tests/logic/modal/test_modal_codec.py:5084)

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → 10 passed
- Targeted modal codec/registry slice (10 selected tests) → 10 passed
- Extra targeted adaptive checks (2 selected tests) → 2 passed