Implemented the ambiguity-policy hardening by promoting `deontic->temporal` into the compiler-required adaptive pair bundle and updating focused regression coverage.

**Changes**
- Added `("deontic", "temporal")` to compiler-required adaptive ambiguity policy pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000113-20260519_113146/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:58).
- Updated compiler-required registry expectations in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000113-20260519_113146/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:188) to include this pair and assert it is `True`.
- Added a required-bundle deontic/temporal explicit-ambiguity scenario (with the packet-aligned margin/priority values) in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000113-20260519_113146/tests/unit_tests/logic/modal/test_modal_codec.py:12184).

**Validation**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py tests/unit_tests/logic/modal/test_modal_codec.py -k "required_margin_bundle_pairs or compiler_required_adaptive_ambiguity_bundle_covers_deontic_conflict_pairs or compiler_required_adaptive_ambiguity_pairs_are_covered_by_both_policies"`  
  Result: `3 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_deontic or frame_epistemic or deontic_temporal or deontic_self_pair"`  
  Result: `13 passed`