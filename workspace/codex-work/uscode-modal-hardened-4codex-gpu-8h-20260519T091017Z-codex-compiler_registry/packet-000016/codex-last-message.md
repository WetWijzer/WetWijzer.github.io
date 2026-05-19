Implemented a deterministic cue-rule refinement for `compiler_registry` by hardening generic frame debias behavior in the modal codec.

- Updated [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000016-20260519_101446/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:412):
  - Added `_GENERIC_FRAME_PRESENT_CUE_SCOPE_BONUS_FACTOR` and applied a partial scope boost when non-frame families already have cues under generic-frame debias mode ([spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000016-20260519_101446/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:995)).
  - Refined `_is_generic_frame_cue_debias_context` so frame-scope/editorial phrases no longer block debias when strong competing non-frame evidence exists ([spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000016-20260519_101446/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1738)).

- Added regression coverage in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000016-20260519_101446/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:768) for editorial-frame + deontic-cue competition.

Tests run:
1. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "debiases_generic_frame_logits_in_editorial_scope_with_deontic_cue or debiases_generic_frame_logits_when_deontic_scope_phrase_is_present or soft_caps_repeated_frame_logits_for_temporal_competition"`  
   Result: 3 passed
2. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "surfaces_frame_scope_family_outvote_ambiguity or treats_court_as_frame_scope_ambiguity_signal or surfaces_deontic_scope_family_outvote_ambiguity"`  
   Result: 3 passed
3. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`  
   Result: 13 passed