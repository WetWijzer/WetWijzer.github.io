Implemented a narrow `compiler_ambiguity` policy update so low-margin cases now surface explicit ambiguity for the missing directional families.

**Changes**
- Added `temporal -> epistemic` and `frame -> alethic` to signal-free adaptive ambiguity policy pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000023-20260519_094546/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:115).
- Updated registry assertions for pair coverage and ordered target lists in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000023-20260519_094546/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:138).
- Added compiler regressions that mock low-margin adaptive logits and assert explicit ambiguity emission for:
  - `frame -> alethic`
  - `temporal -> epistemic`
  in [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000023-20260519_094546/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:179).

**Validation**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py`  
  Result: `37 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py`  
  Result: `175 passed`