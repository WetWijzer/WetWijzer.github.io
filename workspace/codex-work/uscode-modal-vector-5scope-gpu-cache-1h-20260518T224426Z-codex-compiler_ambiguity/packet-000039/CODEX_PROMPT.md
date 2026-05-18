# packet-000039

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/packet-000039/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/packet-000039/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000039-20260518_230154

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-f15e30eadd5e384c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.906912785226, "hint_id": "modal-synthesis-05c7a4bf2db53255", "predicted_family": "frame", "priority": 1.056912785226, "sample_id": "us-code-42-289c.-57f0e54146415340", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-bec041cde2467cad", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-15-9005-5ad28bbe0beec57b", "target_family": "temporal"}`
- `program-777ae0770cc17138` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `0.987329`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.567455418399, "hint_id": "modal-synthesis-0cf16fa7ac93064e", "predicted_family": "frame", "priority": 0.717455418399, "sample_id": "us-code-10-222b-5a1b27cf9dd7eb34", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.991239825991, "hint_id": "modal-synthesis-e5bf0dc9cfeff71f", "predicted_family": "frame", "priority": 1.141239825991, "sample_id": "us-code-16-231b-2d288b733c8a2e32", "target_family": "deontic"}`
- `program-cf96a0dd0ff10183` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `0.980379`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.337803377474, "hint_id": "modal-synthesis-0c55571b9c60a458", "predicted_family": "deontic", "priority": 0.487803377474, "sample_id": "us-code-26-2207A-7ad298682b335ae1", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999999163045, "hint_id": "modal-synthesis-0e32974ab3058f40", "predicted_family": "deontic", "priority": 1.149999163045, "sample_id": "us-code-47-219.-09b0a2804ba5c011", "target_family": "temporal"}`
- `program-c7f3581c72786815` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `0.976254`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.999528717722, "hint_id": "modal-synthesis-9ad0934632dbb626", "predicted_family": "deontic", "priority": 1.149528717722, "sample_id": "us-code-22-4304-c522266be75990ce", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.302898401435, "hint_id": "modal-synthesis-abdd05e46c9bcdad", "predicted_family": "frame", "priority": 0.452898401435, "sample_id": "us-code-7-1963-566d388fcbdb6135", "target_family": "deontic"}`
- `program-7eeb8ee10b37088e` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `0.974645`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-44ca9b8f1c7e0342", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-35-302-15247e5e5a144013", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.396001780861, "hint_id": "modal-synthesis-6295a7bdc58eb3b5", "predicted_family": "frame", "priority": 0.546001780861, "sample_id": "us-code-33-3853-72da0bb625fa37b5", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.463831688409, "hint_id": "modal-synthesis-8ccdb8558ea76970", "predicted_family": "frame", "priority": 0.613831688409, "sample_id": "us-code-16-3473-d628ecd7a5a5926b", "target_family": "deontic"}`

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

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-f15e30eadd5e384c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.067043995865`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-9005-5ad28bbe0beec57b, us-code-42-289c.-57f0e54146415340`
  evidence: `{"family_margin": -0.906912785226, "hint_id": "modal-synthesis-05c7a4bf2db53255", "predicted_family": "frame", "priority": 1.056912785226, "sample_id": "us-code-42-289c.-57f0e54146415340", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-bec041cde2467cad", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-15-9005-5ad28bbe0beec57b", "target_family": "temporal"}`
- `program-777ae0770cc17138`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `0.987329`
  loss: `autoencoder_residual_cluster` = `0.929347622195`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-16-231b-2d288b733c8a2e32, us-code-10-222b-5a1b27cf9dd7eb34`
  evidence: `{"family_margin": -0.567455418399, "hint_id": "modal-synthesis-0cf16fa7ac93064e", "predicted_family": "frame", "priority": 0.717455418399, "sample_id": "us-code-10-222b-5a1b27cf9dd7eb34", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.991239825991, "hint_id": "modal-synthesis-e5bf0dc9cfeff71f", "predicted_family": "frame", "priority": 1.141239825991, "sample_id": "us-code-16-231b-2d288b733c8a2e32", "target_family": "deontic"}`
- `program-cf96a0dd0ff10183`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `0.980379`
  loss: `autoencoder_residual_cluster` = `0.818901270259`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-47-219.-09b0a2804ba5c011, us-code-26-2207A-7ad298682b335ae1`
  evidence: `{"family_margin": -0.337803377474, "hint_id": "modal-synthesis-0c55571b9c60a458", "predicted_family": "deontic", "priority": 0.487803377474, "sample_id": "us-code-26-2207A-7ad298682b335ae1", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999999163045, "hint_id": "modal-synthesis-0e32974ab3058f40", "predicted_family": "deontic", "priority": 1.149999163045, "sample_id": "us-code-47-219.-09b0a2804ba5c011", "target_family": "temporal"}`
- `program-c7f3581c72786815`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `0.976254`
  loss: `autoencoder_residual_cluster` = `0.801213559578`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-4304-c522266be75990ce, us-code-7-1963-566d388fcbdb6135`
  evidence: `{"family_margin": -0.999528717722, "hint_id": "modal-synthesis-9ad0934632dbb626", "predicted_family": "deontic", "priority": 1.149528717722, "sample_id": "us-code-22-4304-c522266be75990ce", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.302898401435, "hint_id": "modal-synthesis-abdd05e46c9bcdad", "predicted_family": "frame", "priority": 0.452898401435, "sample_id": "us-code-7-1963-566d388fcbdb6135", "target_family": "deontic"}`
- `program-7eeb8ee10b37088e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f15e30eadd5e384c` score `0.974645`
  loss: `autoencoder_residual_cluster` = `0.436611156423`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-16-3473-d628ecd7a5a5926b, us-code-33-3853-72da0bb625fa37b5, us-code-35-302-15247e5e5a144013`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-44ca9b8f1c7e0342", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-35-302-15247e5e5a144013", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.396001780861, "hint_id": "modal-synthesis-6295a7bdc58eb3b5", "predicted_family": "frame", "priority": 0.546001780861, "sample_id": "us-code-33-3853-72da0bb625fa37b5", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.463831688409, "hint_id": "modal-synthesis-8ccdb8558ea76970", "predicted_family": "frame", "priority": 0.613831688409, "sample_id": "us-code-16-3473-d628ecd7a5a5926b", "target_family": "deontic"}`
