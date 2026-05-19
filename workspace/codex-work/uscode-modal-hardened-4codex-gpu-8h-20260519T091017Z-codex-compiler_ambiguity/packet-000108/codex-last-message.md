Implemented a deterministic `modal.compiler.ambiguity` policy update by promoting recurrent low-margin pairs into the compiler-required bundle, so they always surface explicit adaptive ambiguities with compiler-required metadata.

**Changes**
- Updated compiler-required adaptive pair policy in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000108-20260519_111337/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py):
  - Added `alethic->temporal`
  - Added `conditional_normative->deontic`
  - Added `frame->epistemic`
- Expanded registry policy coverage assertions in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000108-20260519_111337/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py) to reflect new required targets/order and directional checks.
- Extended required-margin compiler ambiguity scenarios in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000108-20260519_111337/tests/unit_tests/logic/modal/test_modal_codec.py) with explicit evidence-style cases for:
  - `alethic->temporal`
  - `conditional_normative->deontic`
  - `frame->epistemic`

**Validation**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` passed (`15 passed`).
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k test_modal_compiler_emits_explicit_ambiguity_for_required_margin_bundle_pairs` passed (`1 passed`).
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_alethic_temporal_adaptive_ambiguity or signal_free_pair_policy_for_frame_epistemic_adaptive_ambiguity or signal_free_pair_policy_for_conditional_deontic_adaptive_ambiguity"` passed (`3 passed`).
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -k "explicit_deontic_to_conditional_normative_adaptive_pair or explicit_conditional_normative_to_deontic_adaptive_pair or explicit_temporal_to_deontic_adaptive_pair"` passed (`3 passed`).