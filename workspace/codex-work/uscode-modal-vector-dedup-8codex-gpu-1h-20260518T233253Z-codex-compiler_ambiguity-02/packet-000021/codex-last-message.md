Implemented the packet as a targeted ambiguity-policy review by adding missing regression coverage for the requested pair directions.

**Edits**
- Added `deontic -> conditional_normative` explicit adaptive-pair assertion in [test_legal_modal_parser_deterministic_rules.py:182](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000021-20260518_234607/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:182).
- Added `temporal -> deontic` explicit adaptive-pair assertion in [test_legal_modal_parser_deterministic_rules.py:198](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000021-20260518_234607/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:198).

**Validation**
- Ran:
  - `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py`
- Result: `11 passed`.