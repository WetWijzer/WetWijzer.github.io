Implemented a deterministic cue-rule refinement for the modal family confusion pairs by tightening weak-evidence handling in the codec weighting/backfill path.

**Changes made**
- Updated competing-scope backfill thresholds and added an explicit `frame -> conditional_normative` backfill trigger in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000066-20260519_030208/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:392).
- Broadened backfill gating from narrowly phrase-based checks to deterministic scope-evidence booleans (`frame/deontic/temporal/conditional`) in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000066-20260519_030208/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1288).
- Added explicit token-level ambiguity signals:
  - `has_deontic_scope_token`
  - `has_temporal_scope_token`
  in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000066-20260519_030208/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1495).

**Tests added/updated**
- Added conditional→frame weak-evidence backfill test in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000066-20260519_030208/tests/unit_tests/logic/modal/test_modal_codec.py:5990).
- Strengthened deontic→temporal adaptive ambiguity assertions to require non-zero temporal target share and `has_temporal_scope_token` in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000066-20260519_030208/tests/unit_tests/logic/modal/test_modal_codec.py:6010).

**Validation run**
- Passed:
  - `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "backfills_frame_family_for_conditional_scope_with_frame_context or surfaces_deontic_temporal_adaptive_ambiguity or caps_repeated_generic_frame_cues"`
  - `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "adaptive_family_margin or compiled_primary_family or deontic_temporal or frame_conditional or conditional_frame"`
- Unrelated existing failure in untouched registry file:
  - `tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py::test_signal_free_adaptive_ambiguity_targets_are_ordered_and_directional` (expects alethic targets without `frame`, but registry currently includes it).