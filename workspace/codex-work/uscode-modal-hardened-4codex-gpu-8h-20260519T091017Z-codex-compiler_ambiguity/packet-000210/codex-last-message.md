Implemented a targeted compiler-ambiguity policy hardening for the TODO bundle.

**What I changed**
1. Promoted `alethic->epistemic` into compiler-required adaptive ambiguity policy pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000210-20260519_131953/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py).
2. Updated registry policy tests to reflect the expanded required/priority pair expectations in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000210-20260519_131953/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py).
3. Extended modal compiler ambiguity tests to explicitly cover the added alethic-epistemic required path and additional TODO evidence margins in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000210-20260519_131953/tests/unit_tests/logic/modal/test_modal_codec.py).

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` -> **16 passed**
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "recurrent_policy_pairs or required_margin_bundle_pairs or todo_evidence_margin_pairs"` -> **3 passed**