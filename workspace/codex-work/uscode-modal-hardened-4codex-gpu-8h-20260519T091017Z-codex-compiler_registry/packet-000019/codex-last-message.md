Implemented a deterministic cue-weighting refinement for `compiler_registry` scope to reduce frame over-dominance when competing modal scope is present.

**Changes**
- Added a moderate frame-competition tier in weighted family backfill constants and logic:
  - [`spacy_modal_codec.py`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000019-20260519_104935/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:434)
  - [`spacy_modal_codec.py`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000019-20260519_104935/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1470)
- New behavior: when frame evidence is moderate (single generic frame cue scenarios), inject small competing support for:
  - `frame -> deontic`
  - `frame -> temporal`
  - `frame -> conditional_normative`
  - `frame -> epistemic`
  while preserving existing stronger backfill paths for higher frame counts.

- Added focused regression tests for these single-frame-cue mixed-scope cases:
  - [`test_spacy_modal_codec.py`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000019-20260519_104935/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:1428)

**Validation**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py` → `101 passed`
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py` → `25 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "recurrent_policy_pairs or compiled_primary_policy_pairs_cover_compiler_ambiguity_bundle or frame_temporal_priority_pair or frame_conditional_priority_pair or temporal_deontic or deontic_temporal or emits_explicit_frame_to_conditional_and_temporal_adaptive_pairs"` → `9 passed`