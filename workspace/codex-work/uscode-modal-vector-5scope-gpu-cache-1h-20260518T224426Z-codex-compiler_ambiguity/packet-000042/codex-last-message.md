Implemented a focused `modal.compiler.ambiguity` policy update and added regressions for the packet pair-bundles.

- Added signal-free policy coverage for `deontic->deontic` in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000042-20260518_231303/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33).
- Updated adaptive ambiguity emission to allow self-pair explicit ambiguity only when the predicted family’s lead over runner-up is within the adaptive threshold (prevents always-on self-noise), and added runner-up metadata for explainability in [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000042-20260518_231303/ipfs_datasets_py/logic/modal/compiler.py:607).
- Expanded deterministic regressions to lock explicit adaptive pairs for:
  - `frame->conditional_normative`, `frame->temporal`, `frame->deontic`
  - `deontic->frame`, `deontic->temporal`
  - `conditional_normative->frame`
  - `deontic->deontic` low-margin self pair  
  in [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000042-20260518_231303/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:125).

Validation run:

- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py` → `9 passed`