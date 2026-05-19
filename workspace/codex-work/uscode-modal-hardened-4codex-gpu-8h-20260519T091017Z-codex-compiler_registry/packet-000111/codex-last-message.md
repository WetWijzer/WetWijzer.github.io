Implemented a targeted modal family cue-rule refinement for the compiler registry path.

- Updated cue profiles in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000111-20260519_135222/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:515):
  - Removed `cannot` from alethic cues.
  - Added stronger deontic obligation/prohibition cues (including penalty/sanction phrases and `shall not`/`cannot`/`unlawful`).
  - Added epistemic deemed-style cues (`deemed`, `deemed to`, `is deemed`, etc.).

- Updated scope/backfill behavior in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000111-20260519_135222/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:76):
  - Reclassified `cannot` as deontic scope token (and removed it from alethic scope tokens).
  - Relaxed weak-count gates so conditional->deontic and frame->epistemic backfill can trigger when target evidence is weak (not only exactly zero).

- Added regressions in [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000111-20260519_135222/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:1044):
  - `cannot` resolves as deontic prohibition cue.
  - `subject to civil penalties` is captured as deontic cue.
  - deemed-phrases are captured as epistemic cues.

Validation run:
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py`
- Result: `32 passed`