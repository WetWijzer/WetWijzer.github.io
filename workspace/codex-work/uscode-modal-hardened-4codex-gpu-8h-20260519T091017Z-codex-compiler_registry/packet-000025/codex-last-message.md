Implemented the packet with a narrow compiler-registry + cue-rule refinement.

**Changes made**
1. Added `temporal->temporal` to compiler-required adaptive ambiguity pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000025-20260519_115134/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py).
2. Updated statutory/frame cue arbitration in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000025-20260519_115134/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py):
- Tightened frame backfill in statutory contexts so frame is not boosted when explicit conditional/deontic/temporal competing scope is present.
- Increased conditional/deontic statutory competing boosts.
- Added additional temporal boost for statutory frame contexts and deontic+strong-temporal overlap.
3. Updated and extended tests:
- [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000025-20260519_115134/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py)
- [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000025-20260519_115134/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py)

**Tests run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → `15 passed`
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "statutory_frame_context or statutory_as_provided_clause or deontic_scope_boost_for_temporal_competition or temporal_scope_boost_for_statutory_frame_context or reduces_statutory_frame_bias_when_deontic_cue_is_explicit"` → `6 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "recurrent_policy_pairs or compiled_primary_self_pair_adaptive_ambiguity_when_ranking_prefers_temporal"` → `1 passed`