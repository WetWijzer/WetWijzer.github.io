Implemented the packet by hardening deterministic modal-family cue rules in the compiler-registry lane.

- Added required adaptive ambiguity pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000021-20260519_110738/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py#L33): `alethic->deontic`, `deontic->temporal`, `epistemic->deontic`.
- Added moderate non-frame competing-scope backfill thresholds and weight in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000021-20260519_110738/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py#L427).
- Extended `_apply_competing_scope_backfill(...)` with deterministic moderate-signal branches for:
  - `deontic -> conditional_normative`
  - `deontic -> temporal`
  - `temporal -> deontic`
  - `temporal -> conditional_normative`
  - `epistemic -> deontic`
  - `alethic -> deontic`
  in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000021-20260519_110738/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py#L1475).
- Updated registry assertions in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000021-20260519_110738/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py#L188).
- Added focused codec tests for all new moderate/backfill paths in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000021-20260519_110738/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py#L1888).

Validation run:
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`
- Result: `122 passed`