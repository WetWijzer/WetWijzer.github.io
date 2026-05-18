Implemented a scoped modal-family cue refinement for the `compiler_registry` lane.

- Expanded registry cue coverage for `epistemic` and `conditional_normative` families in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000111-20260518_193637/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:175).
- Added a temporal disambiguation rule to suppress non-temporal list-intro uses of `following` (`the/these/those/such following ...`) in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000111-20260518_193637/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:221) and [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000111-20260518_193637/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:575).
- Added targeted regressions in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000111-20260518_193637/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:291) for:
  - non-temporal `the following`,
  - `except as provided in` conditional cue extraction,
  - epistemic `knowledge of` / `has reason to believe` cue extraction.

Validation run:

1. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "calendar_month_may or non_deadline_by or deadline_by or following_as_non_temporal or except_as_provided_in or knowledge_and_belief"` → `6 passed`.
2. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "with_respect_to_as_conditional_scope_ambiguity_signal or before_scope_as_temporal_conditional_ambiguity_signal"` → `2 passed`.
3. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → `5 passed`.