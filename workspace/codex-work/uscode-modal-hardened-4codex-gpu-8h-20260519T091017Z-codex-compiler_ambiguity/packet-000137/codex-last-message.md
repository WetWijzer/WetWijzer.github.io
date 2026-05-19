Implemented the ambiguity-policy hardening for the requested family pairs.

**Changes**
- Promoted `alethic->conditional_normative` into the compiler-required adaptive ambiguity bundle so it is treated as a required explicit ambiguity path (same class as `deontic->frame`): [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000137-20260519_120243/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33).
- Updated registry tests to assert the new required pair membership, directional target ordering, and pair predicate checks: [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000137-20260519_120243/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:188).
- Expanded required-margin compiler ambiguity scenarios with explicit evidence-style cases for:
  - `alethic->conditional_normative` (`family_margin = -0.999999586886`)
  - `deontic->frame` (`family_margin = -0.555974845748`)  
  in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000137-20260519_120243/tests/unit_tests/logic/modal/test_modal_codec.py:12177).

**Tests run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "compiled_primary_policy_pairs_cover_compiler_ambiguity_bundle"`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_alethic_conditional_adaptive_ambiguity or signal_free_pair_policy_for_deontic_frame_adaptive_ambiguity or emits_explicit_ambiguity_for_required_margin_bundle_pairs"`

All passed.