Implemented a narrow `compiler_registry` refinement for adaptive modal-family cue handling.

- Updated [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000030-20260519_124207/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py):
  - Added `epistemic -> deontic` to `COMPILER_REQUIRED_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS`.
  - Added explicit `frame -> frame` in `PRIORITY_SIGNAL_FREE_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS` so frame self-pair handling is prioritized deterministically.
- Updated [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000030-20260519_124207/ipfs_datasets_py/logic/modal/compiler.py):
  - Added an epistemic-family target-signal rule so `predicted=epistemic` can explicitly pick up deontic signal evidence.
- Updated registry and compiler regression tests:
  - [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000030-20260519_124207/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py)
  - [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000030-20260519_124207/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py)
  - Added new assertions/tests for compiler-required `epistemic -> deontic` and low-margin `frame -> frame` explicit pair emission.

Tests run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py -q` -> `16 passed`
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -q` -> `28 passed`