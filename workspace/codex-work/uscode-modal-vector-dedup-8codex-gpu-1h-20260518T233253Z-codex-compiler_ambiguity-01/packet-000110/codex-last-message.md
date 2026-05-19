Implemented the compiler ambiguity-policy review with a small deterministic exposure improvement and added evidence-driven regression coverage.

**Changes**
- Added a stable adaptive policy-pair tag (`predicted_family->target_family`) to adaptive ambiguity metadata in both ambiguity paths:
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000110-20260519_002602/ipfs_datasets_py/logic/modal/compiler.py#L719)
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000110-20260519_002602/ipfs_datasets_py/logic/modal/compiler.py#L976)
- Extended frame-pair adaptive ambiguity tests to assert this new explicit pair marker and added a regression test with the TODO evidence margins (`-0.413068740844`, `-0.735177285536`):
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000110-20260519_002602/tests/unit_tests/logic/modal/test_modal_codec.py#L2786)
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000110-20260519_002602/tests/unit_tests/logic/modal/test_modal_codec.py#L2877)
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000110-20260519_002602/tests/unit_tests/logic/modal/test_modal_codec.py#L2889)

**Tests**
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_conditional_adaptive_ambiguity or frame_temporal_adaptive_ambiguity or explicit_frame_policy_pair_ambiguities_for_evidence_margins or zero_margin_frame_temporal_priority_pair"` → 4 passed.
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -k "explicit_frame_to_conditional_and_temporal_adaptive_pairs"` → 1 passed.