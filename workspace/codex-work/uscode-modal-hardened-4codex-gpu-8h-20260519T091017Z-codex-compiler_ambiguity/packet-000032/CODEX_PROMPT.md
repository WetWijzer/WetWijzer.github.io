# packet-000032

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000032/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000032/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000032-20260519_104258

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-f65ac49d55175ec9` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f65ac49d55175ec9` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.241161539133, "hint_id": "modal-synthesis-3489b7252ca6a15a", "predicted_family": "temporal", "priority": 0.391161539133, "sample_id": "us-code-22-1642c-08c79f76662ee13b", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.031704643574, "hint_id": "modal-synthesis-4bef07d88171660e", "predicted_family": "deontic", "priority": 0.118295356426, "sample_id": "us-code-50-2425.-47b48c36c06bff21", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999966368036, "hint_id": "modal-synthesis-d0c7bf1b10a972af", "predicted_family": "frame", "priority": 1.149966368036, "sample_id": "us-code-15-637-0720c1c2250fc9b4", "target_family": "deontic"}`

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
- `program-f65ac49d55175ec9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f65ac49d55175ec9` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.553141087865`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-637-0720c1c2250fc9b4, us-code-22-1642c-08c79f76662ee13b, us-code-50-2425.-47b48c36c06bff21`
  evidence: `{"family_margin": -0.241161539133, "hint_id": "modal-synthesis-3489b7252ca6a15a", "predicted_family": "temporal", "priority": 0.391161539133, "sample_id": "us-code-22-1642c-08c79f76662ee13b", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.031704643574, "hint_id": "modal-synthesis-4bef07d88171660e", "predicted_family": "deontic", "priority": 0.118295356426, "sample_id": "us-code-50-2425.-47b48c36c06bff21", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999966368036, "hint_id": "modal-synthesis-d0c7bf1b10a972af", "predicted_family": "frame", "priority": 1.149966368036, "sample_id": "us-code-15-637-0720c1c2250fc9b4", "target_family": "deontic"}`
