Implemented the compiler ambiguity-policy extension for the missing family-pair cases and added regressions.

- Extended adaptive target-family coverage in the compiler for:
  - `frame -> conditional_normative`
  - `frame -> temporal`
  - `conditional_normative -> epistemic`  
  at [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000037-20260518_225133/ipfs_datasets_py/logic/modal/compiler.py:650)

- Added `has_epistemic_cue` ambiguity signal used by the new conditional-normative branch at [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000037-20260518_225133/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1146)

- Added regression tests asserting explicit adaptive pair ambiguities are emitted at [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000037-20260518_225133/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:31) and [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000037-20260518_225133/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:125)

Validation run:
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py`
- Result: `6 passed`