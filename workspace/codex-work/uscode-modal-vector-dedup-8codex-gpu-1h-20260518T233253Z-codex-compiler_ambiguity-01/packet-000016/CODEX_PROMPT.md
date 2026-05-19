# packet-000016

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/packet-000016/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/packet-000016/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000016-20260518_235621

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-4f03b38585accbbd` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f03b38585accbbd` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-0e6230cd1e08c6bf", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-19-4204-56dfc3aa09064923", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999974756549, "hint_id": "modal-synthesis-723f1d50b5d02105", "predicted_family": "deontic", "priority": 1.149974756549, "sample_id": "us-code-42-2000a-a72598b7e52c6ff1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999794724519, "hint_id": "modal-synthesis-989451ff9037536a", "predicted_family": "deontic", "priority": 1.149794724519, "sample_id": "us-code-42-254c-cff7c0b338926702", "target_family": "temporal"}`
- `program-516a54cfec6deb85` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f03b38585accbbd` score `0.985225`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-2f2f543807e70041", "predicted_family": "frame", "priority": 0.730200369329, "sample_id": "us-code-16-1444-b4ceb64e9f14f67c", "target_family": "deontic"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-4c753c104bf591db", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-15-2063-a311159029e92eb8", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.522862570721, "hint_id": "modal-synthesis-4fdb1b1bb3e3beec", "predicted_family": "conditional_normative", "priority": 0.672862570721, "sample_id": "us-code-42-15002.-1b888a13a1154232", "target_family": "temporal"}`
- `program-127f2c9067014635` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->frame","deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f03b38585accbbd` score `0.984153`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.994157979433, "hint_id": "modal-synthesis-617eaad4158de829", "predicted_family": "deontic", "priority": 1.144157979433, "sample_id": "us-code-14-3739-9876992d772d0081", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999663046469, "hint_id": "modal-synthesis-7c1d55949cc83db7", "predicted_family": "deontic", "priority": 1.149663046469, "sample_id": "us-code-7-203-e7b6091da8305ac1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.982007836763, "hint_id": "modal-synthesis-8af644edee341b09", "predicted_family": "conditional_normative", "priority": 1.132007836763, "sample_id": "us-code-42-4016.-01f4e3fc11a0dfef", "target_family": "frame"}`
- `program-43f6185f6b9f6949` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f03b38585accbbd` score `0.968407`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-85158184b704a068", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-19-1367-79cb0669f05d3ba1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999829776053, "hint_id": "modal-synthesis-a2a1144daafb94af", "predicted_family": "deontic", "priority": 1.149829776053, "sample_id": "us-code-26-7608-17fabfe2c7a775c1", "target_family": "frame"}`

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
- TODO count: `4`

## TODOs
- `program-4f03b38585accbbd`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f03b38585accbbd` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.149923160356`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-19-4204-56dfc3aa09064923, us-code-42-2000a-a72598b7e52c6ff1, us-code-42-254c-cff7c0b338926702`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-0e6230cd1e08c6bf", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-19-4204-56dfc3aa09064923", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999974756549, "hint_id": "modal-synthesis-723f1d50b5d02105", "predicted_family": "deontic", "priority": 1.149974756549, "sample_id": "us-code-42-2000a-a72598b7e52c6ff1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999794724519, "hint_id": "modal-synthesis-989451ff9037536a", "predicted_family": "deontic", "priority": 1.149794724519, "sample_id": "us-code-42-254c-cff7c0b338926702", "target_family": "temporal"}`
- `program-516a54cfec6deb85`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f03b38585accbbd` score `0.985225`
  loss: `autoencoder_residual_cluster` = `0.851020980017`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-2063-a311159029e92eb8, us-code-16-1444-b4ceb64e9f14f67c, us-code-42-15002.-1b888a13a1154232`
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-2f2f543807e70041", "predicted_family": "frame", "priority": 0.730200369329, "sample_id": "us-code-16-1444-b4ceb64e9f14f67c", "target_family": "deontic"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-4c753c104bf591db", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-15-2063-a311159029e92eb8", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.522862570721, "hint_id": "modal-synthesis-4fdb1b1bb3e3beec", "predicted_family": "conditional_normative", "priority": 0.672862570721, "sample_id": "us-code-42-15002.-1b888a13a1154232", "target_family": "temporal"}`
- `program-127f2c9067014635`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->frame","deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f03b38585accbbd` score `0.984153`
  loss: `autoencoder_residual_cluster` = `1.141942954222`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-7-203-e7b6091da8305ac1, us-code-14-3739-9876992d772d0081, us-code-42-4016.-01f4e3fc11a0dfef`
  evidence: `{"family_margin": -0.994157979433, "hint_id": "modal-synthesis-617eaad4158de829", "predicted_family": "deontic", "priority": 1.144157979433, "sample_id": "us-code-14-3739-9876992d772d0081", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999663046469, "hint_id": "modal-synthesis-7c1d55949cc83db7", "predicted_family": "deontic", "priority": 1.149663046469, "sample_id": "us-code-7-203-e7b6091da8305ac1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.982007836763, "hint_id": "modal-synthesis-8af644edee341b09", "predicted_family": "conditional_normative", "priority": 1.132007836763, "sample_id": "us-code-42-4016.-01f4e3fc11a0dfef", "target_family": "frame"}`
- `program-43f6185f6b9f6949`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f03b38585accbbd` score `0.968407`
  loss: `autoencoder_residual_cluster` = `0.649914888026`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-26-7608-17fabfe2c7a775c1, us-code-19-1367-79cb0669f05d3ba1`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-85158184b704a068", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-19-1367-79cb0669f05d3ba1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999829776053, "hint_id": "modal-synthesis-a2a1144daafb94af", "predicted_family": "deontic", "priority": 1.149829776053, "sample_id": "us-code-26-7608-17fabfe2c7a775c1", "target_family": "frame"}`
