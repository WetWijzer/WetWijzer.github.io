# packet-000171

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/packet-000171/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/packet-000171/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000171-20260519_002941

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-5993fda4a993add6` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5993fda4a993add6` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-1bfa8403c3bb2bb0", "predicted_family": "frame", "priority": 0.831268688955, "sample_id": "us-code-42-14101.-a5beabd50f2754c9", "target_family": "deontic", "target_probability": 0.168731311045}`
  evidence: `{"family_margin": -0.224993730737, "hint_id": "modal-synthesis-74367943cee3c2db", "predicted_family": "frame", "priority": 0.653173495461, "sample_id": "us-code-33-1107-bb564d15a0040608", "target_family": "deontic", "target_probability": 0.346826504539}`
  evidence: `{"family_margin": -0.981612997966, "hint_id": "modal-synthesis-de62869ebd7211b3", "predicted_family": "frame", "priority": 0.998194143259, "sample_id": "us-code-20-7351d-4e93e049fc664c18", "target_family": "conditional_normative", "target_probability": 0.001805856741}`

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
- `program-5993fda4a993add6`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5993fda4a993add6` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.827545442558`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-20-7351d-4e93e049fc664c18, us-code-42-14101.-a5beabd50f2754c9, us-code-33-1107-bb564d15a0040608`
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-1bfa8403c3bb2bb0", "predicted_family": "frame", "priority": 0.831268688955, "sample_id": "us-code-42-14101.-a5beabd50f2754c9", "target_family": "deontic", "target_probability": 0.168731311045}`
  evidence: `{"family_margin": -0.224993730737, "hint_id": "modal-synthesis-74367943cee3c2db", "predicted_family": "frame", "priority": 0.653173495461, "sample_id": "us-code-33-1107-bb564d15a0040608", "target_family": "deontic", "target_probability": 0.346826504539}`
  evidence: `{"family_margin": -0.981612997966, "hint_id": "modal-synthesis-de62869ebd7211b3", "predicted_family": "frame", "priority": 0.998194143259, "sample_id": "us-code-20-7351d-4e93e049fc664c18", "target_family": "conditional_normative", "target_probability": 0.001805856741}`
