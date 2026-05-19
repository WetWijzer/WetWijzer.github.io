Implemented a narrow compiler ambiguity-policy improvement for this packet.

**What changed**
- Updated adaptive ambiguity emission logic so `adaptive_logits` ambiguities are emitted when either:
  1. adaptive top family differs from ranked-cue top family, **or**
  2. adaptive top-vs-runner-up margin is low (`<= modal_adaptive_family_margin`), even if top family is the same.
- Added helper for deterministic top-two margin calculation.

Code refs:
- [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000125-20260519_024721/ipfs_datasets_py/logic/modal/compiler.py:274)
- [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000125-20260519_024721/ipfs_datasets_py/logic/modal/compiler.py:448)

**Regression test added**
- New test ensures same-top/low-margin adaptive logits still produce explicit pair ambiguity (`deontic -> frame`) with `adaptive_predicted_family_source == "adaptive_logits"`.

Code ref:
- [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000125-20260519_024721/tests/unit_tests/logic/modal/test_modal_codec.py:1786)

**Validation run**
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "adaptive_logits_ambiguity_for_same_top_low_margin or surfaces_adaptive_family_margin_ambiguity_for_temporal_conflicts or uses_compiled_family_as_adaptive_ambiguity_signal"` → 3 passed
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_deontic or frame_conditional or frame_temporal or deontic_frame or deontic_conditional or conditional_deontic or conditional_temporal"` → 17 passed