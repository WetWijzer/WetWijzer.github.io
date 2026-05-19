Implemented a focused `compiler_ambiguity` hardening in the modal compiler by unifying policy-pair expansion so all adaptive paths consume the same ordered family-pair policy set.

**What changed**
- Added a single ordered policy target helper: `_ordered_policy_target_families(...)`.
- Reused that helper in:
  - ranked adaptive target seeding,
  - compiled-primary competing-target expansion,
  - ordered adaptive target construction.
- This removes drift between code paths and keeps explicit ambiguity surfacing consistent for policy pairs like:
  - `alethic -> conditional_normative`
  - `alethic -> deontic`
  - `deontic -> conditional_normative`
  - `frame -> temporal`

File:
- [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000401-20260519_151123/ipfs_datasets_py/logic/modal/compiler.py#L1062)

**Validation run**
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "ordered_adaptive_target_families or compiler_ambiguity_pairs_when_other_target_tables_are_sparse or compiled_primary_policy_pairs_cover_compiler_ambiguity_bundle or uses_signal_free_pair_policy_for_alethic_deontic_adaptive_ambiguity or uses_signal_free_pair_policy_for_alethic_conditional_adaptive_ambiguity or uses_signal_free_pair_policy_for_frame_temporal_adaptive_ambiguity or uses_signal_free_pair_policy_for_deontic_conditional_adaptive_ambiguity"` → 6 passed
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "adaptive and (signal_free_pair_policy or compiler_ambiguity or compiled_primary_policy or ordered_adaptive_target_families)"` → 27 passed
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → 19 passed