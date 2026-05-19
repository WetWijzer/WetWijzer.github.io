# packet-000021

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000021/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000021/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000021-20260518_235032

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-0f987b439016d0a8` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-0f987b439016d0a8` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.999752379489, "hint_id": "modal-synthesis-0be6de141b91b260", "predicted_family": "temporal", "priority": 0.999876605527, "sample_id": "us-code-11-1121-6a8c23d4a586d504", "target_family": "deontic", "target_probability": 0.000123394473}`
  evidence: `{"family_margin": -0.37838315063, "hint_id": "modal-synthesis-43ae97bb543ef3b2", "predicted_family": "deontic", "priority": 0.779789820061, "sample_id": "us-code-33-3029-bf3535c0ce8ad1ed", "target_family": "temporal", "target_probability": 0.220210179939}`
  evidence: `{"family_margin": -0.999936187516, "hint_id": "modal-synthesis-abadc8299c78dba3", "predicted_family": "deontic", "priority": 0.999999887472, "sample_id": "us-code-33-414-265961b5912a94f4", "target_family": "temporal", "target_probability": 1.12528e-07}`
  evidence: `{"family_margin": -0.999999999995, "hint_id": "modal-synthesis-c028df6df7265040", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-20-1099d-1a13f73711413296", "target_family": "frame", "target_probability": 0.0}`
- `program-a4bb3c3a33f8eb9c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-0f987b439016d0a8` score `0.920606`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.430679318188, "hint_id": "modal-synthesis-dd725bba12f48d0c", "predicted_family": "deontic", "priority": 0.749354668684, "sample_id": "us-code-15-80b-19-2610eb398736664d", "target_family": "conditional_normative", "target_probability": 0.250645331316}`
  evidence: `{"family_margin": -0.04007547842, "hint_id": "modal-synthesis-e662d76cfd494cad", "predicted_family": "frame", "priority": 0.618949048341, "sample_id": "us-code-20-107e-1-43ac50498bf68122", "target_family": "conditional_normative", "target_probability": 0.381050951659}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.


## Execution Instructions
Work only inside the packet worktree.
Your worktree edits may be applied back to the source checkout and validated automatically when this packet finishes.
Do not create changes.patch or other patch artifact files; leave source and test edits directly in the worktree.
Treat the packet's program_synthesis_scope metadata as the AST/write-scope boundary; keep edits inside that lane unless a test requires a small adjacent change.
When multiple TODOs are present, treat their semantic_bundle_key or vector_bundle metadata as evidence for one generalized compiler/decompiler/frame improvement over one-off sample fixes.
Implement a narrow deterministic parser, IR, decoder, or frame-logic improvement for the claimed TODOs.
Prefer explainable compiler/decompiler code over learned weights when the TODO concerns modal or frame semantics.
Use local repository files and tests only; do not use web search for this packet.
Run the smallest relevant tests you can before finishing.
Leave unrelated files alone.

## Claimed Autoencoder TODO List
# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-0f987b439016d0a8`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-0f987b439016d0a8` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.944916578265`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-20-1099d-1a13f73711413296, us-code-33-414-265961b5912a94f4, us-code-11-1121-6a8c23d4a586d504, us-code-33-3029-bf3535c0ce8ad1ed`
  evidence: `{"family_margin": -0.999752379489, "hint_id": "modal-synthesis-0be6de141b91b260", "predicted_family": "temporal", "priority": 0.999876605527, "sample_id": "us-code-11-1121-6a8c23d4a586d504", "target_family": "deontic", "target_probability": 0.000123394473}`
  evidence: `{"family_margin": -0.37838315063, "hint_id": "modal-synthesis-43ae97bb543ef3b2", "predicted_family": "deontic", "priority": 0.779789820061, "sample_id": "us-code-33-3029-bf3535c0ce8ad1ed", "target_family": "temporal", "target_probability": 0.220210179939}`
  evidence: `{"family_margin": -0.999936187516, "hint_id": "modal-synthesis-abadc8299c78dba3", "predicted_family": "deontic", "priority": 0.999999887472, "sample_id": "us-code-33-414-265961b5912a94f4", "target_family": "temporal", "target_probability": 1.12528e-07}`
  evidence: `{"family_margin": -0.999999999995, "hint_id": "modal-synthesis-c028df6df7265040", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-20-1099d-1a13f73711413296", "target_family": "frame", "target_probability": 0.0}`
- `program-a4bb3c3a33f8eb9c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-0f987b439016d0a8` score `0.920606`
  loss: `autoencoder_residual_cluster` = `0.684151858512`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-80b-19-2610eb398736664d, us-code-20-107e-1-43ac50498bf68122`
  evidence: `{"family_margin": -0.430679318188, "hint_id": "modal-synthesis-dd725bba12f48d0c", "predicted_family": "deontic", "priority": 0.749354668684, "sample_id": "us-code-15-80b-19-2610eb398736664d", "target_family": "conditional_normative", "target_probability": 0.250645331316}`
  evidence: `{"family_margin": -0.04007547842, "hint_id": "modal-synthesis-e662d76cfd494cad", "predicted_family": "frame", "priority": 0.618949048341, "sample_id": "us-code-20-107e-1-43ac50498bf68122", "target_family": "conditional_normative", "target_probability": 0.381050951659}`
