Implemented a scoped `compiler_ambiguity` hardening that addresses policy coverage and a real early-return gap.

**What changed**
- Fixed an early return in the compiler so compiled-primary adaptive ambiguity checks still run even when the ranked/predicted family has no configured target map.
  - This preserves explicit ambiguity surfacing for cases like compiled-primary `conditional_normative->dynamic` in mismatch scenarios.
  - File: [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000022-20260519_093624/ipfs_datasets_py/logic/modal/compiler.py:739)

- Hardened adaptive ambiguity pair policy tables by canonicalizing to ordered-unique pairs and removing a duplicate `conditional_normative->dynamic` entry.
  - File: [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000022-20260519_093624/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:157)

- Updated/added tests:
  - Registry target ordering expectation updated (no duplicate target).
  - New registry regression asserting no repeated signal-free targets.
  - New compiler regression covering the TODO bundle family directions through compiled-primary ambiguity path:
    - `frame->deontic`
    - `deontic->frame`
    - `conditional_normative->dynamic`
    - `frame->temporal`
    - `alethic->conditional_normative`
    - `deontic->deontic`
  - Files: [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000022-20260519_093624/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:160), [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000022-20260519_093624/tests/unit_tests/logic/modal/test_modal_codec.py:11127)

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_adaptive_ambiguity_targets or compiled_primary_policy_pairs_cover_compiler_ambiguity_bundle or frame_deontic or deontic_frame or conditional_normative_dynamic or alethic_conditional_normative or frame_temporal or deontic_deontic"`
- Result: `11 passed, 176 deselected`