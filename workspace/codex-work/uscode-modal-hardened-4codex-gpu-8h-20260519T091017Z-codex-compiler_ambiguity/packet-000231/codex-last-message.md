Implemented the compiler-ambiguity policy update for the `compiler_ambiguity` lane.

**Changes**
- Added `epistemic -> temporal` to compiler-required adaptive ambiguity pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000231-20260519_133440/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py).
- Updated policy expectations in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000231-20260519_133440/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py):
  - `epistemic -> temporal` now expected as supported, priority, and compiler-required.
  - Updated directional target tuples for `epistemic`.
  - Fixed stale duplicate `alethic` priority expectation (`epistemic` duplicate removed).
- Added deterministic compiler regressions in [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000231-20260519_133440/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py):
  - Verifies explicit adaptive ambiguity for `epistemic -> temporal` is emitted as compiler-required even without target evidence.
  - Verifies explicit adaptive ambiguity for `frame -> temporal` is emitted as compiler-required even without target evidence.

**Validation**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py -q` → `16 passed`
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py` → `29 passed`