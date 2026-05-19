Implemented a compiler-registry policy refinement by promoting recurrent ambiguity pairs into the compiler-required bundle.

- Updated [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000020-20260519_105817/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py#L33):
  - Added compiler-required pairs:
    - `alethic -> temporal`
    - `deontic -> temporal`
    - `frame -> conditional_normative`
    - `frame -> temporal`
- Updated expectations in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000020-20260519_105817/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py#L188) to reflect the expanded compiler-required policy surface and target ordering.

Validation run:
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` -> `15 passed`
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -k "temporal_to_deontic_adaptive_pair or deontic_self_pair"` -> `2 passed, 23 deselected`