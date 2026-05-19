Implemented a focused compiler-ambiguity policy update for the TODO bundle.

- Promoted `deontic->temporal` into the priority adaptive ambiguity pair policy in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000039-20260519_021343/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:124).
- Added deterministic adaptive ambiguity priority metadata in [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000039-20260519_021343/ipfs_datasets_py/logic/modal/compiler.py:721):
  - `adaptive_margin_abs`
  - `adaptive_priority`
  - helper `_adaptive_margin_priority(...)` at [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000039-20260519_021343/ipfs_datasets_py/logic/modal/compiler.py:1073)
- Added/updated tests:
  - Priority registry assertion for `deontic->temporal` in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000039-20260519_021343/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:170)
  - Zero-margin deontic/temporal explicit outvoted ambiguity test in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000039-20260519_021343/tests/unit_tests/logic/modal/test_modal_codec.py:4560)
  - Adaptive priority metadata test with evidence-style frame/deontic margin in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000039-20260519_021343/tests/unit_tests/logic/modal/test_modal_codec.py:4651)

Validation run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` (10 passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py` (143 passed)