Implemented a focused compiler-ambiguity policy update for the missing `epistemic->conditional_normative` pair while preserving existing `deontic->deontic` and `frame->temporal` behavior.

**Changes made**
- Added `epistemic->conditional_normative` to adaptive policy tables in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000370-20260519_144650/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:87), including:
  - `COMPILER_REQUIRED_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS`
  - `COMPILER_AMBIGUITY_POLICY_FAMILY_PAIRS`
  - `SIGNAL_FREE_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS`
  - `PRIORITY_SIGNAL_FREE_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS`
- Added a deterministic compiler regression for explicit epistemic→conditional normative ambiguity emission in [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000370-20260519_144650/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:1073).
- Updated registry policy expectation tests for tuple ordering/membership in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000370-20260519_144650/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:225).

**Validation**
- Ran:
  - `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py`
- Result: `49 passed`