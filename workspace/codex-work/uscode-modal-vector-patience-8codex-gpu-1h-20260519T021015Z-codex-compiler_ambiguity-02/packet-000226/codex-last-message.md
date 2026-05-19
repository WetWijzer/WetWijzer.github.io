Implemented the ambiguity-policy gap for `compiler_ambiguity` by extending the signal-free adaptive family-pair policy and adding regressions.

- Added `conditional_normative -> dynamic` to `SIGNAL_FREE_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS` in [modal_registry.py:83](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000226-20260519_030004/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:83).
- Added regression coverage for explicit ambiguity emission and compiled-primary preservation of that pair in:
  - [test_legal_modal_parser_deterministic_rules.py:310](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000226-20260519_030004/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:310)
  - [test_legal_modal_parser_deterministic_rules.py:682](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000226-20260519_030004/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:682)

Validation run:
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -k "conditional_normative_to_dynamic or preserves_conditional_to_dynamic or frame_to_conditional_and_temporal_adaptive_pairs or explicit_temporal_to_deontic_adaptive_pair"`
- Result: `4 passed, 19 deselected`