# packet-000026

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000026/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000026/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000026-20260519_072617

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-4facf832cf7a0b43` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4facf832cf7a0b43` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.449666884353, "hint_id": "modal-synthesis-31afcfb976279aa9", "predicted_family": "frame", "priority": 0.599666884353, "sample_id": "us-code-29-794c-686bfc4da3dd44d6", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.94805249433, "hint_id": "modal-synthesis-fa22da49cd4eb4fc", "predicted_family": "frame", "priority": 1.09805249433, "sample_id": "us-code-38-1722A-36a73cb7e6dbf73e", "target_family": "conditional_normative"}`
- `program-e86fa2e59aa8b93e` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4facf832cf7a0b43` score `0.957905`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.059733617643, "hint_id": "modal-synthesis-6942aa9e98b35adf", "predicted_family": "deontic", "priority": 0.090266382357, "sample_id": "us-code-15-278g-2-a465705dc02eccad", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.88083267146, "hint_id": "modal-synthesis-a2efb4d5855b34d1", "predicted_family": "temporal", "priority": 1.03083267146, "sample_id": "us-code-46-53111.-d55f3d8fd634aec0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.626923020311, "hint_id": "modal-synthesis-fa7f5d3c0ab59a95", "predicted_family": "deontic", "priority": 0.776923020311, "sample_id": "us-code-43-618d.-4e9855b3ebb224b2", "target_family": "conditional_normative"}`
- `program-87c9d01fa292c075` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4facf832cf7a0b43` score `0.949627`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-0e7821495f5c3dee", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-14-2738-a8d887e67903d179", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.437373806715, "hint_id": "modal-synthesis-146be897379f2019", "predicted_family": "frame", "priority": 0.587373806715, "sample_id": "us-code-22-3145-1a5a37638bc87aa3", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.941680926619, "hint_id": "modal-synthesis-357dcdb216ad0fb2", "predicted_family": "frame", "priority": 1.091680926619, "sample_id": "us-code-49-13904.-4e1b7e85f94fb3a8", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.158692188725, "hint_id": "modal-synthesis-9c193cd2334be9c2", "predicted_family": "frame", "priority": 0.308692188725, "sample_id": "us-code-28-107-589461080f66274a", "target_family": "deontic"}`

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
- TODO count: `3`

## TODOs
- `program-4facf832cf7a0b43`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4facf832cf7a0b43` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.848859689342`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-38-1722A-36a73cb7e6dbf73e, us-code-29-794c-686bfc4da3dd44d6`
  evidence: `{"family_margin": -0.449666884353, "hint_id": "modal-synthesis-31afcfb976279aa9", "predicted_family": "frame", "priority": 0.599666884353, "sample_id": "us-code-29-794c-686bfc4da3dd44d6", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.94805249433, "hint_id": "modal-synthesis-fa22da49cd4eb4fc", "predicted_family": "frame", "priority": 1.09805249433, "sample_id": "us-code-38-1722A-36a73cb7e6dbf73e", "target_family": "conditional_normative"}`
- `program-e86fa2e59aa8b93e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4facf832cf7a0b43` score `0.957905`
  loss: `autoencoder_residual_cluster` = `0.632674024709`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-46-53111.-d55f3d8fd634aec0, us-code-43-618d.-4e9855b3ebb224b2, us-code-15-278g-2-a465705dc02eccad`
  evidence: `{"family_margin": 0.059733617643, "hint_id": "modal-synthesis-6942aa9e98b35adf", "predicted_family": "deontic", "priority": 0.090266382357, "sample_id": "us-code-15-278g-2-a465705dc02eccad", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.88083267146, "hint_id": "modal-synthesis-a2efb4d5855b34d1", "predicted_family": "temporal", "priority": 1.03083267146, "sample_id": "us-code-46-53111.-d55f3d8fd634aec0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.626923020311, "hint_id": "modal-synthesis-fa7f5d3c0ab59a95", "predicted_family": "deontic", "priority": 0.776923020311, "sample_id": "us-code-43-618d.-4e9855b3ebb224b2", "target_family": "conditional_normative"}`
- `program-87c9d01fa292c075`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4facf832cf7a0b43` score `0.949627`
  loss: `autoencoder_residual_cluster` = `0.664073151111`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-13904.-4e1b7e85f94fb3a8, us-code-14-2738-a8d887e67903d179, us-code-22-3145-1a5a37638bc87aa3, us-code-28-107-589461080f66274a`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-0e7821495f5c3dee", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-14-2738-a8d887e67903d179", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.437373806715, "hint_id": "modal-synthesis-146be897379f2019", "predicted_family": "frame", "priority": 0.587373806715, "sample_id": "us-code-22-3145-1a5a37638bc87aa3", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.941680926619, "hint_id": "modal-synthesis-357dcdb216ad0fb2", "predicted_family": "frame", "priority": 1.091680926619, "sample_id": "us-code-49-13904.-4e1b7e85f94fb3a8", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.158692188725, "hint_id": "modal-synthesis-9c193cd2334be9c2", "predicted_family": "frame", "priority": 0.308692188725, "sample_id": "us-code-28-107-589461080f66274a", "target_family": "deontic"}`
