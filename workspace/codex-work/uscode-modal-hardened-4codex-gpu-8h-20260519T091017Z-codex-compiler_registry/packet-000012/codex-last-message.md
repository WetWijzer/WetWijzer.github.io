Implemented a narrow `compiler_registry` refinement focused on the TODO family conflicts (`frame/temporal/alethic -> deontic`, `frame -> conditional_normative`).

**What changed**
- Added `alethic -> deontic` to priority signal-free adaptive ambiguity pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000012-20260519_093054/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:160).
- Refined scope-based logit boosts in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000012-20260519_093054/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1667):
  - Stronger `conditional_normative` boost when condition/exception scope appears with statutory+frame context.
  - Stronger `deontic` boost when deontic scope appears in statutory+frame, temporal, or alethic competition contexts.
- Updated registry tests for the new priority behavior in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000012-20260519_093054/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:206).
- Added targeted codec tests for the refined boosts in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000012-20260519_093054/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:482).

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` passed.
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py` passed (90 tests).
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_alethic_deontic_adaptive_ambiguity or deontic_epistemic_priority_pair_as_outvoted_adaptive_ambiguity or temporal_alethic_outvoted_margin_low"` passed.