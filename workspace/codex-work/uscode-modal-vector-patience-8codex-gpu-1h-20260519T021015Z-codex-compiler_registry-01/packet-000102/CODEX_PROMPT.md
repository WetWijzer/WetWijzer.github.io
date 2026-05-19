# packet-000102

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000102/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000102/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000102-20260519_031330

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e33f32b7dbb12e8f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e33f32b7dbb12e8f` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.848890749741, "hint_id": "modal-synthesis-62ae8a4efff7f361", "predicted_family": "temporal", "priority": 0.955521777922, "sample_id": "us-code-20-806-b393baca996842b5", "target_family": "deontic", "target_probability": 0.044478222078}`
  evidence: `{"family_margin": -0.814531998077, "hint_id": "modal-synthesis-a0d46f8461636298", "predicted_family": "frame", "priority": 0.952677707098, "sample_id": "us-code-38-1720I-3410e13660f6b6a4", "target_family": "deontic", "target_probability": 0.047322292902}`
  evidence: `{"family_margin": -0.941090534922, "hint_id": "modal-synthesis-a6a45b6964189d34", "predicted_family": "frame", "priority": 0.990510177762, "sample_id": "us-code-12-1816-c0b440c716f086be", "target_family": "deontic", "target_probability": 0.009489822238}`

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

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-e33f32b7dbb12e8f`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e33f32b7dbb12e8f` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.966236554261`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-1816-c0b440c716f086be, us-code-20-806-b393baca996842b5, us-code-38-1720I-3410e13660f6b6a4`
  evidence: `{"family_margin": -0.848890749741, "hint_id": "modal-synthesis-62ae8a4efff7f361", "predicted_family": "temporal", "priority": 0.955521777922, "sample_id": "us-code-20-806-b393baca996842b5", "target_family": "deontic", "target_probability": 0.044478222078}`
  evidence: `{"family_margin": -0.814531998077, "hint_id": "modal-synthesis-a0d46f8461636298", "predicted_family": "frame", "priority": 0.952677707098, "sample_id": "us-code-38-1720I-3410e13660f6b6a4", "target_family": "deontic", "target_probability": 0.047322292902}`
  evidence: `{"family_margin": -0.941090534922, "hint_id": "modal-synthesis-a6a45b6964189d34", "predicted_family": "frame", "priority": 0.990510177762, "sample_id": "us-code-12-1816-c0b440c716f086be", "target_family": "deontic", "target_probability": 0.009489822238}`
