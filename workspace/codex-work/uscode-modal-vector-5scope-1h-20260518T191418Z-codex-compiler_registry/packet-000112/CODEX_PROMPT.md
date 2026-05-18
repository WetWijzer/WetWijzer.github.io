# packet-000112

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000112/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000112/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000112-20260518_194814

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-8f01678b0e6f23fe` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8f01678b0e6f23fe` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.730558609294, "hint_id": "modal-synthesis-1cf117575c480741", "predicted_family": "temporal", "priority": 0.999754842648, "sample_id": "us-code-54-101511.-54b6ccb5549961cf", "target_family": "frame", "target_probability": 0.000245157352}`
  evidence: `{"family_margin": -0.999753080179, "hint_id": "modal-synthesis-6ce331f266d23305", "predicted_family": "temporal", "priority": 0.99987660544, "sample_id": "us-code-38-7310A-219731bd25fca43f", "target_family": "deontic", "target_probability": 0.00012339456}`
  evidence: `{"family_margin": -0.880797076722, "hint_id": "modal-synthesis-91be68b6f69bb9bc", "predicted_family": "deontic", "priority": 0.999999999332, "sample_id": "us-code-26-646-0cfbbfe0c86b90ae", "target_family": "conditional_normative", "target_probability": 6.68e-10}`
  evidence: `{"family_margin": -0.904857016623, "hint_id": "modal-synthesis-e44a55a7d10fd601", "predicted_family": "temporal", "priority": 0.952589386389, "sample_id": "us-code-22-2779a-2f9baaa9ac52eacf", "target_family": "deontic", "target_probability": 0.047410613611}`
- `program-193dfffc965b9daa` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8f01678b0e6f23fe` score `0.968027`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-7a44869955382114", "predicted_family": "temporal", "priority": 0.523775425532, "sample_id": "us-code-2-1516-e49d03132a8b32ab", "target_family": "deontic", "target_probability": 0.476224574468}`
  evidence: `{"family_margin": -0.714386779384, "hint_id": "modal-synthesis-a3ed16f455aaf322", "predicted_family": "deontic", "priority": 0.96256920713, "sample_id": "us-code-7-8758-6c50bb2c1676bbf9", "target_family": "frame", "target_probability": 0.03743079287}`
  evidence: `{"family_margin": -0.732922273587, "hint_id": "modal-synthesis-b83f8fec8e6ef4d3", "predicted_family": "deontic", "priority": 0.885284733419, "sample_id": "us-code-5-8464a-7b232fae83466b72", "target_family": "temporal", "target_probability": 0.114715266581}`
- `program-03869f6b572db7e7` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["hybrid->frame","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8f01678b0e6f23fe` score `0.927755`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-816a025ed3c39d63", "predicted_family": "hybrid", "priority": 0.912970395775, "sample_id": "us-code-29-1662-e7516434dca445ba", "target_family": "frame", "target_probability": 0.087029604225}`
  evidence: `{"family_margin": -0.99962738107, "hint_id": "modal-synthesis-93cd2d70f88926c5", "predicted_family": "temporal", "priority": 0.999983304244, "sample_id": "us-code-34-11294-0a6981caa505e06b", "target_family": "frame", "target_probability": 1.6695756e-05}`
  evidence: `{"family_margin": -0.458673661066, "hint_id": "modal-synthesis-d0e1896b68bc79de", "predicted_family": "temporal", "priority": 0.975967474066, "sample_id": "us-code-16-831r-67ffc5b229e2bd75", "target_family": "frame", "target_probability": 0.024032525934}`

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
- TODO count: `3`

## TODOs
- `program-8f01678b0e6f23fe`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8f01678b0e6f23fe` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.988055208452`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-26-646-0cfbbfe0c86b90ae, us-code-38-7310A-219731bd25fca43f, us-code-54-101511.-54b6ccb5549961cf, us-code-22-2779a-2f9baaa9ac52eacf`
  evidence: `{"family_margin": -0.730558609294, "hint_id": "modal-synthesis-1cf117575c480741", "predicted_family": "temporal", "priority": 0.999754842648, "sample_id": "us-code-54-101511.-54b6ccb5549961cf", "target_family": "frame", "target_probability": 0.000245157352}`
  evidence: `{"family_margin": -0.999753080179, "hint_id": "modal-synthesis-6ce331f266d23305", "predicted_family": "temporal", "priority": 0.99987660544, "sample_id": "us-code-38-7310A-219731bd25fca43f", "target_family": "deontic", "target_probability": 0.00012339456}`
  evidence: `{"family_margin": -0.880797076722, "hint_id": "modal-synthesis-91be68b6f69bb9bc", "predicted_family": "deontic", "priority": 0.999999999332, "sample_id": "us-code-26-646-0cfbbfe0c86b90ae", "target_family": "conditional_normative", "target_probability": 6.68e-10}`
  evidence: `{"family_margin": -0.904857016623, "hint_id": "modal-synthesis-e44a55a7d10fd601", "predicted_family": "temporal", "priority": 0.952589386389, "sample_id": "us-code-22-2779a-2f9baaa9ac52eacf", "target_family": "deontic", "target_probability": 0.047410613611}`
- `program-193dfffc965b9daa`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8f01678b0e6f23fe` score `0.968027`
  loss: `autoencoder_residual_cluster` = `0.790543122027`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-7-8758-6c50bb2c1676bbf9, us-code-5-8464a-7b232fae83466b72, us-code-2-1516-e49d03132a8b32ab`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-7a44869955382114", "predicted_family": "temporal", "priority": 0.523775425532, "sample_id": "us-code-2-1516-e49d03132a8b32ab", "target_family": "deontic", "target_probability": 0.476224574468}`
  evidence: `{"family_margin": -0.714386779384, "hint_id": "modal-synthesis-a3ed16f455aaf322", "predicted_family": "deontic", "priority": 0.96256920713, "sample_id": "us-code-7-8758-6c50bb2c1676bbf9", "target_family": "frame", "target_probability": 0.03743079287}`
  evidence: `{"family_margin": -0.732922273587, "hint_id": "modal-synthesis-b83f8fec8e6ef4d3", "predicted_family": "deontic", "priority": 0.885284733419, "sample_id": "us-code-5-8464a-7b232fae83466b72", "target_family": "temporal", "target_probability": 0.114715266581}`
- `program-03869f6b572db7e7`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["hybrid->frame","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8f01678b0e6f23fe` score `0.927755`
  loss: `autoencoder_residual_cluster` = `0.962973724695`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-34-11294-0a6981caa505e06b, us-code-16-831r-67ffc5b229e2bd75, us-code-29-1662-e7516434dca445ba`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-816a025ed3c39d63", "predicted_family": "hybrid", "priority": 0.912970395775, "sample_id": "us-code-29-1662-e7516434dca445ba", "target_family": "frame", "target_probability": 0.087029604225}`
  evidence: `{"family_margin": -0.99962738107, "hint_id": "modal-synthesis-93cd2d70f88926c5", "predicted_family": "temporal", "priority": 0.999983304244, "sample_id": "us-code-34-11294-0a6981caa505e06b", "target_family": "frame", "target_probability": 1.6695756e-05}`
  evidence: `{"family_margin": -0.458673661066, "hint_id": "modal-synthesis-d0e1896b68bc79de", "predicted_family": "temporal", "priority": 0.975967474066, "sample_id": "us-code-16-831r-67ffc5b229e2bd75", "target_family": "frame", "target_probability": 0.024032525934}`
