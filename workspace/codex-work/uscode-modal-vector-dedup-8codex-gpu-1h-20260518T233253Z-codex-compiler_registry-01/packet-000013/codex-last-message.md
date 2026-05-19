Implemented a deterministic modal-family cue refinement focused on `frame/deontic/conditional_normative -> temporal` conflicts.

- Updated [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000013-20260518_234157/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1066):
  - Added `_apply_temporal_scope_competing_bonus` to inject a small temporal weighted count (`1.15`) when:
    - strong temporal scope evidence exists (`date`, temporal scope phrase, or temporal `within` context),
    - no temporal cue was directly extracted,
    - there is competing `conditional_normative`/`deontic`/`frame` cue evidence,
    - and frame-editorial scope is **not** present (guardrail).
  - Wired this into `_weighted_modal_family_counts` in both normal and generic-frame-debias branches.
  - Fixed `ranked_modal_families` to include families introduced by weighted policy (count can be `0` but share can be non-zero), so temporal policy signals are actually rankable.

- Added regression tests in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000013-20260518_234157/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:523):
  - conditional + deadline scope phrase promotes temporal ranking,
  - generic frame + deadline scope phrase promotes temporal ranking,
  - editorial-frame context with effective-date language remains frame-dominant.

Validation run:

1. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "temporal_logits_from_scope_without_temporal_cues or promotes_temporal_ranking or keeps_editorial_frame_ranking_with_effective_date_phrase or debiases_generic_frame_logits_when_temporal_scope_is_present"`  
   - Result: **5 passed**

2. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "surfaces_modal_family_ambiguity_when_cues_overlap or surfaces_primary_family_margin_ambiguity_when_outvoted or surfaces_frame_family_margin_ambiguity_when_outvoted or surfaces_adaptive_family_margin_ambiguity_for_temporal_conflicts"`  
   - Result: **4 passed**