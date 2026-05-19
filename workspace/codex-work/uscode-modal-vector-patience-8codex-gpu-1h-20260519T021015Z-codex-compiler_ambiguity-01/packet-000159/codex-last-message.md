Implemented a narrow `compiler_ambiguity` improvement in compiled-primary adaptive handling so explicit ambiguities are surfaced when there is real competing evidence, even for non-signal-free policy pairs.

**What changed**
1. Expanded compiled-primary target enumeration to include its own signal-derived target families before policy-table targets, so directional ambiguity checks cover evidence-backed competitors deterministically.  
[compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000159-20260519_030302/ipfs_datasets_py/logic/modal/compiler.py#L829)

2. Fixed compiled-primary gating logic: previously it hard-required signal-free policy membership; now it emits when `(has_target_signal_evidence) OR (signal-free policy applies)`, matching the main adaptive path semantics.  
[compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000159-20260519_030302/ipfs_datasets_py/logic/modal/compiler.py#L1007)

3. Added regression coverage for compiled-primary evidence-backed ambiguity emission (`deontic -> alethic`) to lock the new behavior and metadata contract.  
[test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000159-20260519_030302/tests/unit_tests/logic/modal/test_modal_codec.py#L2194)

**Tests run**
1. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "compiled_primary_deontic_alethic or compiled_primary_deontic_conditional_policy_ambiguity_when_cues_predict_temporal or uses_compiled_family_as_adaptive_ambiguity_signal"`  
Result: `3 passed`.

2. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_temporal_deontic_adaptive_ambiguity or signal_free_pair_policy_for_frame_deontic_adaptive_ambiguity or signal_free_pair_policy_for_frame_conditional_adaptive_ambiguity or signal_free_pair_policy_for_frame_temporal_adaptive_ambiguity or signal_free_pair_policy_for_conditional_temporal_adaptive_ambiguity or signal_free_pair_policy_for_conditional_deontic_adaptive_ambiguity or signal_free_pair_policy_for_conditional_frame_adaptive_ambiguity or surfaces_compiled_primary_deontic_conditional_policy_ambiguity_when_cues_predict_temporal or compiled_primary_deontic_alethic"`  
Result: `9 passed`.

3. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`  
Result: `1 failing` (`alethic` target ordering assertion), in an unchanged file.