Implemented a narrow compiler-registry cue-rule refinement to reduce false `frame` dominance in mixed-scope clauses.

**Changes**
- Expanded generic frame cue debias terms so relational/frame-structure phrases are treated as weak frame evidence when competing scope is present.
- Updated [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000015-20260519_000042/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py#L361): added `administered by`, `is a`, and `part of` to `_GENERIC_FRAME_CUE_TERMS`.
- Added regression coverage in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000015-20260519_000042/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py#L501):
  - deontic force beats relational frame cues in mixed clauses.
  - temporal scope beats relational frame cues in mixed clauses.

**Validation**
- Ran:
  - `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "generic_frame or relational_frame or deontic_scope_phrase or temporal_scope_is_present"`
  - `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_scope_family_outvote or deontic_frame or deontic_temporal or temporal_scope_family_outvote_ambiguity or frame_family_margin_ambiguity_when_outvoted or under_this_section_as_deontic_frame_adaptive_signal"`
- Result: all selected tests passed (`7 passed` and `8 passed`).