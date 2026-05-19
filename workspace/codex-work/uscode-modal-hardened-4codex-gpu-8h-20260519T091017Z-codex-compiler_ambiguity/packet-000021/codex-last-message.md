Implemented a targeted compiler ambiguity-policy hardening for cue-aware family competition.

**Changes**
- Updated adaptive target-signal mapping so `deontic -> epistemic` treats epistemic cues as direct target evidence, and `temporal -> deontic` accepts cue-only deontic evidence:
  - [compiler.py#L1005](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000021-20260519_093008/ipfs_datasets_py/logic/modal/compiler.py#L1005)
- Hardened deontic target-family outvote checks to recognize `has_deontic_cue` in addition to `has_deontic_scope`:
  - [compiler.py#L1678](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000021-20260519_093008/ipfs_datasets_py/logic/modal/compiler.py#L1678)
  - [compiler.py#L1784](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000021-20260519_093008/ipfs_datasets_py/logic/modal/compiler.py#L1784)

**Tests Added**
- Added regression tests for cue-only signaling paths:
  - `temporal -> deontic` adaptive ambiguity cue evidence:
    - [test_modal_codec.py#L2266](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000021-20260519_093008/tests/unit_tests/logic/modal/test_modal_codec.py#L2266)
  - `deontic -> epistemic` adaptive ambiguity cue evidence:
    - [test_modal_codec.py#L6874](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000021-20260519_093008/tests/unit_tests/logic/modal/test_modal_codec.py#L6874)

**Validation**
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "temporal_deontic_adaptive_ambiguity or deontic_epistemic_adaptive_ambiguity"` passed (`4 passed`).
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "deontic_scope or temporal_deontic"` passed (`5 passed`).