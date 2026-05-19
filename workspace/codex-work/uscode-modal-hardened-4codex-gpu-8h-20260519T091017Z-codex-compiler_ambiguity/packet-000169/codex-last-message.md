Implemented a narrow compiler-ambiguity policy hardening for the requested family pairs.

- Added `epistemic -> deontic` to compiler-required adaptive ambiguity pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000169-20260519_123909/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:75).
- Added regression coverage to ensure explicit adaptive ambiguity for `epistemic -> deontic` is marked compiler-required in [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000169-20260519_123909/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:904).

Validation run:

- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py`
- Result: `27 passed`