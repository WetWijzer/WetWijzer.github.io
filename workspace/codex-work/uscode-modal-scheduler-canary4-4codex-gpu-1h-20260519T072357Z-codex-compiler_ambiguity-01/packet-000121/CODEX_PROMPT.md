# packet-000121

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/packet-000121/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/packet-000121/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000121-20260519_082338

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-022a48c93b2ff1d1` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-022a48c93b2ff1d1` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.073728924867, "hint_id": "modal-synthesis-2acb676239b682e6", "predicted_family": "conditional_normative", "priority": 0.223728924867, "sample_id": "us-code-12-4105-36d07b104cbb3372", "target_family": "deontic"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-87d2c49b51e92612", "predicted_family": "temporal", "priority": 1.15, "sample_id": "us-code-28-524-445e0313d6f19fea", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.99922543422, "hint_id": "modal-synthesis-e6c6a75858c518e3", "predicted_family": "frame", "priority": 1.14922543422, "sample_id": "us-code-22-2291n-ac54fa9d2b9461be", "target_family": "deontic"}`
- `program-8bbe16b562fd602e` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-022a48c93b2ff1d1` score `0.967268`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.38106983356, "hint_id": "modal-synthesis-39ac695f1a33ed73", "predicted_family": "deontic", "priority": 0.53106983356, "sample_id": "us-code-22-1643m-5242bf8f9ab76629", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.048490599997, "hint_id": "modal-synthesis-3fabd490c9a0b2ff", "predicted_family": "deontic", "priority": 0.198490599997, "sample_id": "us-code-21-353d-77f856460111b7bd", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.419042466181, "hint_id": "modal-synthesis-63ff7d1fbe8a17cd", "predicted_family": "conditional_normative", "priority": 0.569042466181, "sample_id": "us-code-45-921.-904bab83295f76d1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999994241105, "hint_id": "modal-synthesis-ffb012359ac5250b", "predicted_family": "frame", "priority": 1.149994241105, "sample_id": "us-code-12-1441a-1-044eb239d7ffd95b", "target_family": "conditional_normative"}`

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

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-022a48c93b2ff1d1`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-022a48c93b2ff1d1` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.840984786362`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-28-524-445e0313d6f19fea, us-code-22-2291n-ac54fa9d2b9461be, us-code-12-4105-36d07b104cbb3372`
  evidence: `{"family_margin": -0.073728924867, "hint_id": "modal-synthesis-2acb676239b682e6", "predicted_family": "conditional_normative", "priority": 0.223728924867, "sample_id": "us-code-12-4105-36d07b104cbb3372", "target_family": "deontic"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-87d2c49b51e92612", "predicted_family": "temporal", "priority": 1.15, "sample_id": "us-code-28-524-445e0313d6f19fea", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.99922543422, "hint_id": "modal-synthesis-e6c6a75858c518e3", "predicted_family": "frame", "priority": 1.14922543422, "sample_id": "us-code-22-2291n-ac54fa9d2b9461be", "target_family": "deontic"}`
- `program-8bbe16b562fd602e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-022a48c93b2ff1d1` score `0.967268`
  loss: `autoencoder_residual_cluster` = `0.612149285211`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-1441a-1-044eb239d7ffd95b, us-code-45-921.-904bab83295f76d1, us-code-22-1643m-5242bf8f9ab76629, us-code-21-353d-77f856460111b7bd`
  evidence: `{"family_margin": -0.38106983356, "hint_id": "modal-synthesis-39ac695f1a33ed73", "predicted_family": "deontic", "priority": 0.53106983356, "sample_id": "us-code-22-1643m-5242bf8f9ab76629", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.048490599997, "hint_id": "modal-synthesis-3fabd490c9a0b2ff", "predicted_family": "deontic", "priority": 0.198490599997, "sample_id": "us-code-21-353d-77f856460111b7bd", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.419042466181, "hint_id": "modal-synthesis-63ff7d1fbe8a17cd", "predicted_family": "conditional_normative", "priority": 0.569042466181, "sample_id": "us-code-45-921.-904bab83295f76d1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999994241105, "hint_id": "modal-synthesis-ffb012359ac5250b", "predicted_family": "frame", "priority": 1.149994241105, "sample_id": "us-code-12-1441a-1-044eb239d7ffd95b", "target_family": "conditional_normative"}`
