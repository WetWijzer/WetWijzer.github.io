Implemented a targeted compiler ambiguity hardening so low-margin adaptive cases reliably emit explicit ambiguity records even when base metadata is under-specified or non-canonical.

**What Changed**
1. In [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000473-20260519_154715/ipfs_datasets_py/logic/modal/compiler.py:592), explicit adaptive backfill now reconstructs deterministic `candidate_ids` from resolved policy families (`[predicted, target]` or `[predicted]` for self-pairs), instead of blindly inheriting possibly empty/partial IDs.
2. Added canonical family normalization and policy-pair resolution helpers in [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000473-20260519_154715/ipfs_datasets_py/logic/modal/compiler.py:694) so values like `ModalLogicFamily.FRAME` / `DEONTIC` normalize to `frame` / `deontic` before explicit ambiguity type derivation.
3. `_derive_explicit_adaptive_ambiguity_type` now uses the shared canonical policy-family resolver for consistent explicit type generation across fallback paths.

**Test Added**
- Added regression test in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000473-20260519_154715/tests/unit_tests/logic/modal/test_modal_codec.py:1850) verifying explicit backfill works from non-canonical policy pair metadata and produces `adaptive_frame_deontic_outvoted_margin_low` with canonical candidate IDs.

**Validation Run**
1. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "canonicalizes_policy_pair_families or backfills_missing_explicit_adaptive_ambiguity_from_base_record or derives_missing_explicit_adaptive_ambiguity_type_from_policy_pair"` → `3 passed`
2. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_conditional or frame_deontic or frame_temporal or temporal_deontic or temporal_conditional or deontic_temporal or deontic_self"` → `24 passed`