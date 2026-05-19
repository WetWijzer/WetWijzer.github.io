Implemented a focused modal ambiguity policy hardening in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000019-20260519_091202/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:111) and [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000019-20260519_091202/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:198):

- Removed `temporal -> alethic` from both:
1. `SIGNAL_FREE_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS`
2. `PRIORITY_SIGNAL_FREE_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS`

This keeps the packet-targeted policy pairs intact (`frame->deontic`, `frame->temporal`, `deontic->conditional_normative`, `deontic->deontic`) while tightening temporal ambiguity targets to the expected directional contract.

Validation run:
1. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py -q` → `11 passed`
2. `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -q` → `23 passed`
3. Direct runtime check confirmed required packet pairs still return `True` via `supports_signal_free_adaptive_ambiguity_pair`.