Implemented a generalized `ir_decompiler` slot refinement focused on count/rank structure and typed IR parity.

- Added numeric signature slots for document-level modal family counts in the decompiler (`modal_family_count_value_*` and `modal_family_count_<family>_*`) in [decompiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000035-20260518_231644/ipfs_datasets_py/logic/modal/decompiler.py:1115).
- Added richer frame-candidate rank slot emission in the decompiler (`frame_candidate_rank_*` numeric signatures and typed slots for `frame_candidate_ranked`) in [decompiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000035-20260518_231644/ipfs_datasets_py/logic/modal/decompiler.py:2253).
- Added matching numeric signatures for document-level modal family counts in IR triples in [codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000035-20260518_231644/ipfs_datasets_py/logic/modal/codec.py:3233).
- Added ranked frame-candidate triple predicates and typed/rank signatures (`candidate_ontology_frame_rank*`, `candidate_ontology_frame_ranked*`) in [codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000035-20260518_231644/ipfs_datasets_py/logic/modal/codec.py:872).
- Extended assertions for these new slots/triples in [test_ir_decompiler_slots.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000035-20260518_231644/ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py:2686).

Tests run:

1. `pytest -q ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py -k "document_modal_family_count_slots or derives_modal_family_count_slots_from_formulas or infers_selected_frame_and_candidates_from_metadata"`  
   Result: `5 passed`
2. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "selected_frame_modal_family_count_slots or surfaces_ranked_frame_candidate_slots"`  
   Result: `2 passed`