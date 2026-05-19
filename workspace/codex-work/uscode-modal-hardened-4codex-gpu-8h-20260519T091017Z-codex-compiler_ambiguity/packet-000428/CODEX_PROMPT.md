# packet-000428

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000428/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000428/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000428-20260519_152147

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-7ebe6d569fc90257` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-7ebe6d569fc90257` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.230774719777, "hint_id": "modal-synthesis-0cdac334515214ac", "predicted_family": "deontic", "priority": 0.380774719777, "sample_id": "us-code-38-2102A-088b75a4bc313043", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999908583756, "hint_id": "modal-synthesis-36b00cb4cba16cf7", "predicted_family": "frame", "priority": 1.149908583756, "sample_id": "us-code-42-3535.-739d47b019f8aeeb", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.733153662417, "hint_id": "modal-synthesis-6dc8183cdc524ff8", "predicted_family": "deontic", "priority": 0.883153662417, "sample_id": "us-code-7-4801-315be0aeb7c40c29", "target_family": "epistemic"}`

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

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-7ebe6d569fc90257`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-7ebe6d569fc90257` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.804612321983`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-3535.-739d47b019f8aeeb, us-code-7-4801-315be0aeb7c40c29, us-code-38-2102A-088b75a4bc313043`
  evidence: `{"family_margin": -0.230774719777, "hint_id": "modal-synthesis-0cdac334515214ac", "predicted_family": "deontic", "priority": 0.380774719777, "sample_id": "us-code-38-2102A-088b75a4bc313043", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999908583756, "hint_id": "modal-synthesis-36b00cb4cba16cf7", "predicted_family": "frame", "priority": 1.149908583756, "sample_id": "us-code-42-3535.-739d47b019f8aeeb", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.733153662417, "hint_id": "modal-synthesis-6dc8183cdc524ff8", "predicted_family": "deontic", "priority": 0.883153662417, "sample_id": "us-code-7-4801-315be0aeb7c40c29", "target_family": "epistemic"}`
