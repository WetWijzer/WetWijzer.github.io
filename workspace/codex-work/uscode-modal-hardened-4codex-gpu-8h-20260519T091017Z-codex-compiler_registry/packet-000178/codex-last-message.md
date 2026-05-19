Implemented a registry-scope refinement for modal family cue handling by promoting missing pair policies and adding regressions.

- Updated compiler-required adaptive ambiguity pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000178-20260519_142816/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33):
  - `alethic -> frame`
  - `frame -> dynamic`
  - `hybrid -> frame`
- Updated compiler ambiguity bundle pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000178-20260519_142816/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:152):
  - `hybrid -> frame`
- Added deterministic regression coverage in [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000178-20260519_142816/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:1073) for:
  - `frame -> dynamic` compiler-required policy emission
  - `alethic -> frame` compiler-required policy emission
  - `hybrid -> frame` compiler-required policy emission

Validation run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py`
- Result: `155 passed`