Implemented a generalized modal-family cue reweighting update focused on repeated-cue dominance under competing scope evidence.

Changed files:
- [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000040-20260519_022609/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:383)
- [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000040-20260519_022609/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:755)

What I changed:
- Added deterministic soft caps for repeated `temporal`, `conditional_normative`, and `frame` cue counts when competing modal scope is present.
- Kept existing generic frame debias behavior, but now consistently apply cross-family competing-scope caps in `_weighted_modal_family_counts`.
- Added 3 regression tests covering:
  - temporal soft-cap under deontic competition,
  - conditional soft-cap under temporal competition,
  - frame soft-cap under competing scope.

Tests run (all passed):
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "soft_caps_repeated"`
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py`
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py`