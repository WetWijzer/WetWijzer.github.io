# packet-000401

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000401/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000401/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000401-20260519_151123

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-0e50a26962c02625` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-0e50a26962c02625` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.99993840758, "hint_id": "modal-synthesis-42ce633e8fae8d32", "predicted_family": "alethic", "priority": 1.14993840758, "sample_id": "us-code-43-1606.-83d1d5ae16abd934", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.975049399881, "hint_id": "modal-synthesis-a948854f5b1e668b", "predicted_family": "frame", "priority": 1.125049399881, "sample_id": "us-code-6-643-d2f444bfd0b4972c", "target_family": "temporal"}`
- `program-04bad4d7efb0e3ce` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-0e50a26962c02625` score `0.96945`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.341249605235, "hint_id": "modal-synthesis-8e794222f12c71fd", "predicted_family": "frame", "priority": 0.491249605235, "sample_id": "us-code-16-539o-897733ba41e32ea2", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.707285876684, "hint_id": "modal-synthesis-d7c7183e0a5935c3", "predicted_family": "deontic", "priority": 0.857285876684, "sample_id": "us-code-5-5926-04ed56c4405105b0", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.142093573089, "hint_id": "modal-synthesis-d7caf8c183c73cda", "predicted_family": "alethic", "priority": 0.292093573089, "sample_id": "us-code-22-4505-791882220c69dc3d", "target_family": "deontic"}`

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
- TODO count: `2`

## TODOs
- `program-0e50a26962c02625`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-0e50a26962c02625` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.137493903731`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-43-1606.-83d1d5ae16abd934, us-code-6-643-d2f444bfd0b4972c`
  evidence: `{"family_margin": -0.99993840758, "hint_id": "modal-synthesis-42ce633e8fae8d32", "predicted_family": "alethic", "priority": 1.14993840758, "sample_id": "us-code-43-1606.-83d1d5ae16abd934", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.975049399881, "hint_id": "modal-synthesis-a948854f5b1e668b", "predicted_family": "frame", "priority": 1.125049399881, "sample_id": "us-code-6-643-d2f444bfd0b4972c", "target_family": "temporal"}`
- `program-04bad4d7efb0e3ce`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-0e50a26962c02625` score `0.96945`
  loss: `autoencoder_residual_cluster` = `0.546876351669`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-5-5926-04ed56c4405105b0, us-code-16-539o-897733ba41e32ea2, us-code-22-4505-791882220c69dc3d`
  evidence: `{"family_margin": -0.341249605235, "hint_id": "modal-synthesis-8e794222f12c71fd", "predicted_family": "frame", "priority": 0.491249605235, "sample_id": "us-code-16-539o-897733ba41e32ea2", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.707285876684, "hint_id": "modal-synthesis-d7c7183e0a5935c3", "predicted_family": "deontic", "priority": 0.857285876684, "sample_id": "us-code-5-5926-04ed56c4405105b0", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.142093573089, "hint_id": "modal-synthesis-d7caf8c183c73cda", "predicted_family": "alethic", "priority": 0.292093573089, "sample_id": "us-code-22-4505-791882220c69dc3d", "target_family": "deontic"}`
