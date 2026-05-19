Implemented a scoped `compiler_registry` refinement to strengthen deterministic family-cue handling for the packet’s mismatch patterns.

**Changes**
- Added missing adaptive policy pair `conditional_normative -> dynamic` in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000106-20260519_030042/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py).
- Added dynamic-scope signal support for conditional predictions in [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000106-20260519_030042/ipfs_datasets_py/logic/modal/compiler.py).
- Refined weighted cue backfill heuristics in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000106-20260519_030042/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py):
  - conditional-heavy clauses can backfill small `dynamic` evidence when dynamic scope markers exist.
  - dense deontic clauses can backfill small `dynamic` evidence when dynamic scope markers exist.
  - dense temporal clauses can backfill small `conditional_normative` evidence when condition/exception scope markers exist.
- Updated/added unit coverage:
  - [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000106-20260519_030042/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py)
  - [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000106-20260519_030042/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py)
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000106-20260519_030042/tests/unit_tests/logic/modal/test_modal_codec.py)

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → 11 passed.
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "backfills_dynamic_share_for_conditional_scope_with_dynamic_scope_phrase or backfills_dynamic_share_for_dense_deontic_scope_with_dynamic_scope_phrase or backfills_conditional_share_for_dense_temporal_scope_with_condition_clause"` → 3 passed.
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "backfills_ or soft_caps_repeated or debiases_generic_frame or debiases_relational_frame"` → 26 passed.
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "conditional_dynamic_adaptive_ambiguity or conditional_epistemic_adaptive_ambiguity"` → 3 passed.
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_conditional_ or conditional_epistemic_adaptive_ambiguity or frame_epistemic_adaptive_ambiguity or deontic_dynamic_adaptive_ambiguity or temporal_conditional_adaptive_ambiguity"` → 9 passed.

I did not run the full repository test suite.