# packet-000114

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000114/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000114/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000114-20260518_201151

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-3edc780252faa996` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["hybrid->frame","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-3edc780252faa996` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.999999999646, "hint_id": "modal-synthesis-414ab7e437a28271", "predicted_family": "temporal", "priority": 0.999999999962, "sample_id": "us-code-16-2622-7b3b0068d25f5128", "target_family": "frame", "target_probability": 3.8e-11}`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-f907bf4bec5e18c0", "predicted_family": "hybrid", "priority": 0.912970395775, "sample_id": "us-code-2-60e-3-49bb3eb4baff92b8", "target_family": "frame", "target_probability": 0.087029604225}`
- `program-99e84c977e3e269f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["hybrid->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-3edc780252faa996` score `0.986381`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-5dd819983f3c09f1", "predicted_family": "hybrid", "priority": 0.912970395775, "sample_id": "us-code-36-30104-bb1cedfd16c58ba3", "target_family": "frame", "target_probability": 0.087029604225}`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-7cfad983bf6fb94f", "predicted_family": "hybrid", "priority": 0.912970395775, "sample_id": "us-code-42-5771.-02e64c6fbb913aae", "target_family": "frame", "target_probability": 0.087029604225}`

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

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-3edc780252faa996`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["hybrid->frame","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-3edc780252faa996` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.956485197869`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-2622-7b3b0068d25f5128, us-code-2-60e-3-49bb3eb4baff92b8`
  evidence: `{"family_margin": -0.999999999646, "hint_id": "modal-synthesis-414ab7e437a28271", "predicted_family": "temporal", "priority": 0.999999999962, "sample_id": "us-code-16-2622-7b3b0068d25f5128", "target_family": "frame", "target_probability": 3.8e-11}`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-f907bf4bec5e18c0", "predicted_family": "hybrid", "priority": 0.912970395775, "sample_id": "us-code-2-60e-3-49bb3eb4baff92b8", "target_family": "frame", "target_probability": 0.087029604225}`
- `program-99e84c977e3e269f`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["hybrid->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-3edc780252faa996` score `0.986381`
  loss: `autoencoder_residual_cluster` = `0.912970395775`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-36-30104-bb1cedfd16c58ba3, us-code-42-5771.-02e64c6fbb913aae`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-5dd819983f3c09f1", "predicted_family": "hybrid", "priority": 0.912970395775, "sample_id": "us-code-36-30104-bb1cedfd16c58ba3", "target_family": "frame", "target_probability": 0.087029604225}`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-7cfad983bf6fb94f", "predicted_family": "hybrid", "priority": 0.912970395775, "sample_id": "us-code-42-5771.-02e64c6fbb913aae", "target_family": "frame", "target_probability": 0.087029604225}`
