Implemented a deterministic cue-weighting refinement for the modal compiler registry lane.

**Code changes**
- Added deontic-competition handling to frame soft-capping so dense frame cues are softened when strong deontic evidence is present:
  - [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000107-20260519_131306/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py#L1532)
- Added temporal-competition handling to alethic soft-capping so repeated alethic cues don’t drown temporal evidence:
  - [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000107-20260519_131306/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py#L1579)
- Strengthened temporal-dominant `temporal->frame` backfill when explicit frame-scope/statutory markers exist:
  - [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000107-20260519_131306/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py#L2141)

**New regression tests**
- Added frame-vs-deontic soft-cap regression:
  - [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000107-20260519_131306/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py#L1803)
- Added alethic-vs-temporal soft-cap regression:
  - [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000107-20260519_131306/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py#L1888)

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py` → `115 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "caps_repeated_generic_frame_cues_against_deontic_scope or caps_repeated_generic_frame_cues_against_conditional_scope or upgrades_generic_frame_temporal_scope_backfill_floor or upgrades_generic_frame_deontic_scope_backfill_floor or upgrades_generic_frame_conditional_and_temporal_backfill_floor"` → `5 passed`