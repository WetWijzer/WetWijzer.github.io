Implemented a focused policy hardening test for this ambiguity bundle.

- Added `test_modal_compiler_emits_explicit_frame_bundle_ambiguities_for_autoencoder_margins` in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000170-20260519_124412/tests/unit_tests/logic/modal/test_modal_codec.py:6029).
- The new test locks the two packet evidence pairs:
  - `frame -> conditional_normative` with margin `-0.988612205682` and priority `1.138612205682`
  - `frame -> epistemic` with margin `-0.98096669603` and priority `1.13096669603`
- It asserts both base (`adaptive_family_margin_low`) and explicit ambiguity types are emitted and marked compiler-required.

Validation run:
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py::test_modal_compiler_emits_explicit_frame_bundle_ambiguities_for_autoencoder_margins tests/unit_tests/logic/modal/test_modal_codec.py::test_modal_compiler_uses_signal_free_pair_policy_for_frame_epistemic_adaptive_ambiguity tests/unit_tests/logic/modal/test_modal_codec.py::test_modal_compiler_treats_zero_margin_frame_epistemic_priority_pair_as_outvoted_adaptive_ambiguity`
- Result: `3 passed`