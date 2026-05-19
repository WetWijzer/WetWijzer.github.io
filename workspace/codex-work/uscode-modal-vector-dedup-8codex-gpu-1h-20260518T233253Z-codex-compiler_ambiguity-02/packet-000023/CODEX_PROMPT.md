# packet-000023

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000023/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000023/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000023-20260518_235759

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-53c805b1cb6ff288` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-53c805b1cb6ff288` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-1e0a221d645ee593", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-42-5197d.-e1e709b02810fccb", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.817187532537, "hint_id": "modal-synthesis-b2bdef96d566b847", "predicted_family": "frame", "priority": 0.967187532537, "sample_id": "us-code-25-4305-d7950dea3143e948", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.992411701483, "hint_id": "modal-synthesis-ca21e0152dbcac04", "predicted_family": "frame", "priority": 1.142411701483, "sample_id": "us-code-38-1720B-c75bc7ca7346dec7", "target_family": "deontic"}`
- `program-4c7369ec9d147f16` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-53c805b1cb6ff288` score `0.979186`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-3e1212c1cd9e8083", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-22-266a-6fea26e1a0b4c9d8", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999999686486, "hint_id": "modal-synthesis-67f278060b3cfa84", "predicted_family": "deontic", "priority": 1.149999686486, "sample_id": "us-code-42-1962d-68a2d7727b46b5ff", "target_family": "epistemic"}`

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
- `program-53c805b1cb6ff288`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-53c805b1cb6ff288` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.954927735441`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-38-1720B-c75bc7ca7346dec7, us-code-25-4305-d7950dea3143e948, us-code-42-5197d.-e1e709b02810fccb`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-1e0a221d645ee593", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-42-5197d.-e1e709b02810fccb", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.817187532537, "hint_id": "modal-synthesis-b2bdef96d566b847", "predicted_family": "frame", "priority": 0.967187532537, "sample_id": "us-code-25-4305-d7950dea3143e948", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.992411701483, "hint_id": "modal-synthesis-ca21e0152dbcac04", "predicted_family": "frame", "priority": 1.142411701483, "sample_id": "us-code-38-1720B-c75bc7ca7346dec7", "target_family": "deontic"}`
- `program-4c7369ec9d147f16`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-53c805b1cb6ff288` score `0.979186`
  loss: `autoencoder_residual_cluster` = `0.952591829394`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1962d-68a2d7727b46b5ff, us-code-22-266a-6fea26e1a0b4c9d8`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-3e1212c1cd9e8083", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-22-266a-6fea26e1a0b4c9d8", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999999686486, "hint_id": "modal-synthesis-67f278060b3cfa84", "predicted_family": "deontic", "priority": 1.149999686486, "sample_id": "us-code-42-1962d-68a2d7727b46b5ff", "target_family": "epistemic"}`
