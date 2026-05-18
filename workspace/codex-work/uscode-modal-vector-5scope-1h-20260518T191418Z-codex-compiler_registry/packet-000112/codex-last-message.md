Implemented a focused compiler-registry cue refinement for the targeted family-confusion pairs.

Changed:
- Added higher-signal temporal and conditional-normative cue terms in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000112-20260518_194814/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:196).
- Added a temporal `within` context gate (time-like vs structural/jurisdictional) in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000112-20260518_194814/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:628).
- Added high-precision editorial/codification frame cue injection for encoder-side frame evidence in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000112-20260518_194814/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:670).
- Added registry tests in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000112-20260518_194814/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:33).
- Added modal codec behavior tests in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000112-20260518_194814/tests/unit_tests/logic/modal/test_modal_codec.py:556).

Validation run:
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py tests/unit_tests/logic/modal/test_modal_codec.py -k "...selected..."` -> 9 passed.
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_legal_modal_parser.py -k "codification_fallback_for_known_zero_formula_case or treats_may_date_literals_as_temporal_context_for_7_7913"` -> 2 passed.
