Implemented the `compiler_ambiguity` policy gap by making compiled-primary adaptive ambiguity emit explicit self-pair ambiguities (notably `deontic->deontic`) when margins are low/outvoted.

Changes made:
- Updated compiled-primary target generation to include policy-declared self-pairs so they are not skipped.
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000100-20260519_081416/ipfs_datasets_py/logic/modal/compiler.py:840)
- Updated compiled-primary adaptive ambiguity builder to handle self-pairs explicitly:
  - `is_self_pair=True` metadata
  - single-family `candidate_ids` for self-pairs
  - runner-up computation from ranking for meaningful margin
  - explicit self-pair messaging and explicit ambiguity type emission
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000100-20260519_081416/ipfs_datasets_py/logic/modal/compiler.py:1018)
- Added regression test for compiled-primary `deontic->deontic` ambiguity when ranking prefers temporal.
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000100-20260519_081416/tests/unit_tests/logic/modal/test_modal_codec.py:2194)
- Added registry coverage assertion for `supports_signal_free_adaptive_ambiguity_pair("deontic", "deontic")`.
  - [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000100-20260519_081416/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:110)

Tests run:
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "compiled_primary_deontic_self_pair_adaptive_ambiguity_when_ranking_prefers_temporal or compiled_primary_deontic_conditional_policy_ambiguity_when_cues_predict_temporal"` passed.
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "compiled_primary or deontic_self_pair"` passed.
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py -k signal_free_adaptive_ambiguity_pair_policy_covers_required_bundle_pairs` passed.