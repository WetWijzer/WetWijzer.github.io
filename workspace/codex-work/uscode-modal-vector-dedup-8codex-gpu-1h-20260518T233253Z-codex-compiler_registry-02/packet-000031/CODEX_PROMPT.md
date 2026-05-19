# packet-000031

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000031/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000031/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000031-20260519_002208

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-bee48d56be4ae3cd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bee48d56be4ae3cd` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.648572010426, "hint_id": "modal-synthesis-5f105f9d01ce5a5c", "predicted_family": "deontic", "priority": 0.898487037775, "sample_id": "us-code-16-6853-8c49fca60b12f72e", "target_family": "temporal", "target_probability": 0.101512962225}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-9ca28924f4db69e1", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-48-870.-e8be30bad4b69fe8", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-f284c4a1382f5f89", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-36-240106-acd9ba631c2f3033", "target_family": "conditional_normative", "target_probability": 0.173819074614}`

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
- TODO count: `1`

## TODOs
- `program-bee48d56be4ae3cd`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bee48d56be4ae3cd` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.751250691698`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-6853-8c49fca60b12f72e, us-code-36-240106-acd9ba631c2f3033, us-code-48-870.-e8be30bad4b69fe8`
  evidence: `{"family_margin": -0.648572010426, "hint_id": "modal-synthesis-5f105f9d01ce5a5c", "predicted_family": "deontic", "priority": 0.898487037775, "sample_id": "us-code-16-6853-8c49fca60b12f72e", "target_family": "temporal", "target_probability": 0.101512962225}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-9ca28924f4db69e1", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-48-870.-e8be30bad4b69fe8", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-f284c4a1382f5f89", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-36-240106-acd9ba631c2f3033", "target_family": "conditional_normative", "target_probability": 0.173819074614}`
