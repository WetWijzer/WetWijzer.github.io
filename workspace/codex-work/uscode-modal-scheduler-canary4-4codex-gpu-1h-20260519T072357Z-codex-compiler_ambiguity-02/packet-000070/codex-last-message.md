Implemented a targeted compiler ambiguity update for the temporal policy pairs and validated it.

**Changes**
- Added a deterministic `priority` metadata alias (same value as `adaptive_priority`) for adaptive ambiguity records, including:
  - ranked/adaptive predicted-family path
  - compiled-primary competing-family path
  - compiled-primary self-pair path  
  File refs:
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000070-20260519_082800/ipfs_datasets_py/logic/modal/compiler.py:815)
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000070-20260519_082800/ipfs_datasets_py/logic/modal/compiler.py:1184)
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000070-20260519_082800/ipfs_datasets_py/logic/modal/compiler.py:1322)

- Added regression coverage for the exact temporal policy evidence margins:
  - `temporal -> conditional_normative` with margin `-0.879553798991` and priority `1.029553798991`
  - `temporal -> deontic` with margin `-0.999862926894` and priority `1.149862926894`
  - Confirms explicit ambiguity types are emitted and `priority == adaptive_priority`.  
  File ref:
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000070-20260519_082800/tests/unit_tests/logic/modal/test_modal_codec.py:6163)

**Tests run**
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "adaptive_priority_metadata_for_frame_deontic_policy_margin or emits_priority_alias_for_temporal_signal_free_policy_pairs or uses_signal_free_pair_policy_for_temporal_deontic_adaptive_ambiguity or uses_signal_free_pair_policy_for_temporal_conditional_adaptive_ambiguity"`
- Result: `4 passed`