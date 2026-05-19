Implemented a deterministic modal-family cue refinement across the compiler-registry lane, focused on the reported confusion pairs.

Changes made:
- Expanded registry cue terms in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000065-20260519_025345/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:311):
1. Deontic cues: added `is required to`, `requirement that`, `requirements for`, `is prohibited from`, `unlawful`.
2. Temporal cues: added `effective on`, `during the pendency of`, `period beginning on`, `period ending on`.
3. Conditional cues: added `as provided in`.
- Added conditional scope phrase support for `as provided in` in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000065-20260519_025345/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:33).
- Added a targeted frame→conditional competing-scope backfill path in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000065-20260519_025345/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1298) for mixed clauses with statutory/conditional scope but no conditional cue spans.

Tests updated:
- Registry cue expectations in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000065-20260519_025345/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:25).
- Added codec tests for new cues/backfill in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000065-20260519_025345/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:1014).
- Adjusted compiler expectation for `as provided in` target-share behavior in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000065-20260519_025345/tests/unit_tests/logic/modal/test_modal_codec.py:6039).

Validation run:
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` -> 10 passed
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "..."` -> 7 passed
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "..."` -> 6 passed