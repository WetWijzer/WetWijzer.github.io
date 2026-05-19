# packet-000039

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000039/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000039/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000039-20260519_021343

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-a17ea8aabeb4a43c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a17ea8aabeb4a43c` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999324009529, "hint_id": "modal-synthesis-5e0e061393f0e799", "predicted_family": "frame", "priority": 1.149324009529, "sample_id": "us-code-42-8262g.-4d0259caef5347ae", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.955200085186, "hint_id": "modal-synthesis-6970c95315c4e6e3", "predicted_family": "temporal", "priority": 1.105200085186, "sample_id": "us-code-12-2279aa-2-6a09ee84391e5f19", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.918379271216, "hint_id": "modal-synthesis-f13c1b957308da0f", "predicted_family": "deontic", "priority": 1.068379271216, "sample_id": "us-code-36-904-23d13763f249af22", "target_family": "temporal"}`
- `program-dc1d05cedc81b88d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a17ea8aabeb4a43c` score `0.976818`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.99003245694, "hint_id": "modal-synthesis-6d791ef8dec3d3f0", "predicted_family": "frame", "priority": 1.14003245694, "sample_id": "us-code-22-283k-f4ca00d5aa2cbded", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.030428942315, "hint_id": "modal-synthesis-b2e9af9e5bf5482c", "predicted_family": "frame", "priority": 0.180428942315, "sample_id": "us-code-29-1782-0e521bdf6f8f1e1e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.516670571692, "hint_id": "modal-synthesis-cf896d9a0143327a", "predicted_family": "frame", "priority": 0.666670571692, "sample_id": "us-code-12-1795i-939576470ce39d47", "target_family": "deontic"}`
- `program-9221df5ddb2d818e` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a17ea8aabeb4a43c` score `0.953725`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.938371183949, "hint_id": "modal-synthesis-127cf857587a526b", "predicted_family": "frame", "priority": 1.088371183949, "sample_id": "us-code-28-1873-c9ff189e9971953d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.728575499058, "hint_id": "modal-synthesis-583c42a8d1d4d85b", "predicted_family": "conditional_normative", "priority": 0.878575499058, "sample_id": "us-code-30-878-f6e175862b59fd62", "target_family": "temporal"}`

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
- TODO count: `3`

## TODOs
- `program-a17ea8aabeb4a43c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a17ea8aabeb4a43c` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.10763445531`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-8262g.-4d0259caef5347ae, us-code-12-2279aa-2-6a09ee84391e5f19, us-code-36-904-23d13763f249af22`
  evidence: `{"family_margin": -0.999324009529, "hint_id": "modal-synthesis-5e0e061393f0e799", "predicted_family": "frame", "priority": 1.149324009529, "sample_id": "us-code-42-8262g.-4d0259caef5347ae", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.955200085186, "hint_id": "modal-synthesis-6970c95315c4e6e3", "predicted_family": "temporal", "priority": 1.105200085186, "sample_id": "us-code-12-2279aa-2-6a09ee84391e5f19", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.918379271216, "hint_id": "modal-synthesis-f13c1b957308da0f", "predicted_family": "deontic", "priority": 1.068379271216, "sample_id": "us-code-36-904-23d13763f249af22", "target_family": "temporal"}`
- `program-dc1d05cedc81b88d`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a17ea8aabeb4a43c` score `0.976818`
  loss: `autoencoder_residual_cluster` = `0.662377323649`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-283k-f4ca00d5aa2cbded, us-code-12-1795i-939576470ce39d47, us-code-29-1782-0e521bdf6f8f1e1e`
  evidence: `{"family_margin": -0.99003245694, "hint_id": "modal-synthesis-6d791ef8dec3d3f0", "predicted_family": "frame", "priority": 1.14003245694, "sample_id": "us-code-22-283k-f4ca00d5aa2cbded", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.030428942315, "hint_id": "modal-synthesis-b2e9af9e5bf5482c", "predicted_family": "frame", "priority": 0.180428942315, "sample_id": "us-code-29-1782-0e521bdf6f8f1e1e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.516670571692, "hint_id": "modal-synthesis-cf896d9a0143327a", "predicted_family": "frame", "priority": 0.666670571692, "sample_id": "us-code-12-1795i-939576470ce39d47", "target_family": "deontic"}`
- `program-9221df5ddb2d818e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a17ea8aabeb4a43c` score `0.953725`
  loss: `autoencoder_residual_cluster` = `0.983473341503`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-28-1873-c9ff189e9971953d, us-code-30-878-f6e175862b59fd62`
  evidence: `{"family_margin": -0.938371183949, "hint_id": "modal-synthesis-127cf857587a526b", "predicted_family": "frame", "priority": 1.088371183949, "sample_id": "us-code-28-1873-c9ff189e9971953d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.728575499058, "hint_id": "modal-synthesis-583c42a8d1d4d85b", "predicted_family": "conditional_normative", "priority": 0.878575499058, "sample_id": "us-code-30-878-f6e175862b59fd62", "target_family": "temporal"}`
