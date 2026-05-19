Implemented a deterministic `compiler_registry` cue refinement focused on the requested family-confusion patterns by strengthening explicit lexical evidence for `deontic`, `conditional_normative`, and `temporal`.

Updated:
- [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000029-20260519_080348/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:349)
- [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000029-20260519_080348/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:33)
- [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000029-20260519_080348/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:36)
- [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000029-20260519_080348/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:1422)

Key changes:
- Added stronger deontic cues: `required to`, `is required to`, `shall not`, `is prohibited from`, `unlawful to`, `liable for`.
- Added stronger conditional cues for statutory scoping: `subject to subsection/section/...`, `under regulations prescribed by/under`, `except as provided under`.
- Added stronger temporal enactment/effective-date cues: `after the date of enactment`, `on the date of enactment`, `effective upon enactment`, etc.
- Synced spaCy scope-phrase/scope-token detectors with the expanded cue vocab so adaptive scope/backfill logic sees the same evidence.
- Added focused tests for the new cue families and phrase extraction paths.

Tests run:
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py -k "deontic_profile_has_expected_operators_and_serial_semantics or conditional_profile_includes_terms_and_conditions_cues or temporal_profile_includes_deadline_and_calendar_scope_cues"` -> passed (3).
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "temporal_scope_cues_from_deadline_phrases or temporal_scope_cues_from_enactment_phrases or deontic_obligation_phrase_cue or deontic_prohibition_cues_from_shall_not_and_unlawful_to or conditional_scope_cues_from_statutory_phrases or conditional_cue_except_as_provided_by or conditional_scope_cues_from_subject_to_subsection_and_regulations"` -> passed (7).
- Full `test_modal_registry.py` run shows one existing unrelated assertion mismatch in `test_priority_signal_free_adaptive_targets_are_ordered_directional_subsets` (temporal priority tuple expectation).