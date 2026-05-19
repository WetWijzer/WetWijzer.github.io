Implemented a deterministic cue-weight rebalancing for `compiler_registry` scope focused on deontic over-dominance in mixed-family clauses.

**Code changes**
- Expanded generic frame cues used by debiasing in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000022-20260518_235953/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py#L361) to include `"administered by"`, `"is a"`, and `"part of"`.
- Refined weighted-family counting in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000022-20260518_235953/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py#L1096):
  - kept generic frame debias path,
  - extended deontic soft-cap competition detection to include `conditional_normative` and `epistemic`,
  - made the deontic cap stricter when multiple competing channels are present,
  - added a conditional soft-cap when deontic force is also present ([spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000022-20260518_235953/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py#L1131)).

**Tests added**
- Added two targeted regression tests in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000022-20260518_235953/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py#L587):
  - deontic soft-cap with conditional competition,
  - conditional soft-cap with deontic competition.

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "soft_caps_repeated_deontic_logits_for_conditional_competition or soft_caps_repeated_conditional_logits_for_deontic_competition or soft_caps_repeated_deontic_logits_for_temporal_competition or soft_caps_repeated_deontic_logits_for_frame_competition"` (4 passed)
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py` (47 passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "deontic_temporal_adaptive_ambiguity or deontic_conditional_adaptive_ambiguity or deontic_frame_adaptive_ambiguity or surfaces_temporal_scope_family_outvote_ambiguity or surfaces_frame_scope_family_outvote_ambiguity or surfaces_conditional_scope_family_outvote_ambiguity"` (8 passed)