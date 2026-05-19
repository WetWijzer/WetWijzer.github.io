# packet-000030

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000030/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000030/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000030-20260519_103006

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-bda34d047f48bc68` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-bda34d047f48bc68` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.994033783251, "hint_id": "modal-synthesis-0559fce116704ded", "predicted_family": "frame", "priority": 1.144033783251, "sample_id": "us-code-26-585-a91fbae7f3fcdcb3", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.544360096723, "hint_id": "modal-synthesis-6890cf1255040f0a", "predicted_family": "deontic", "priority": 0.694360096723, "sample_id": "us-code-5-6120-d6895339c5166af1", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.330135897918, "hint_id": "modal-synthesis-7d562bd196d38f5c", "predicted_family": "frame", "priority": 0.480135897918, "sample_id": "us-code-11-1224-68dfb0ff97792385", "target_family": "temporal"}`
- `program-1fdf3657635dedc6` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-bda34d047f48bc68` score `0.991301`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.412883618814, "hint_id": "modal-synthesis-0529bdfdb7fbf539", "predicted_family": "frame", "priority": 0.562883618814, "sample_id": "us-code-6-321g-944711e1e1604509", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-9558cc784085d86a", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-10-643-acdbe7fe682498df", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-99606e0f08a79d8f", "predicted_family": "frame", "priority": 0.737469961488, "sample_id": "us-code-42-14664.-32b9d5a819faf0f3", "target_family": "deontic"}`

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
- `program-bda34d047f48bc68`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-bda34d047f48bc68` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.772843259297`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-26-585-a91fbae7f3fcdcb3, us-code-5-6120-d6895339c5166af1, us-code-11-1224-68dfb0ff97792385`
  evidence: `{"family_margin": -0.994033783251, "hint_id": "modal-synthesis-0559fce116704ded", "predicted_family": "frame", "priority": 1.144033783251, "sample_id": "us-code-26-585-a91fbae7f3fcdcb3", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.544360096723, "hint_id": "modal-synthesis-6890cf1255040f0a", "predicted_family": "deontic", "priority": 0.694360096723, "sample_id": "us-code-5-6120-d6895339c5166af1", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.330135897918, "hint_id": "modal-synthesis-7d562bd196d38f5c", "predicted_family": "frame", "priority": 0.480135897918, "sample_id": "us-code-11-1224-68dfb0ff97792385", "target_family": "temporal"}`
- `program-1fdf3657635dedc6`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-bda34d047f48bc68` score `0.991301`
  loss: `autoencoder_residual_cluster` = `0.483451193434`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-14664.-32b9d5a819faf0f3, us-code-6-321g-944711e1e1604509, us-code-10-643-acdbe7fe682498df`
  evidence: `{"family_margin": -0.412883618814, "hint_id": "modal-synthesis-0529bdfdb7fbf539", "predicted_family": "frame", "priority": 0.562883618814, "sample_id": "us-code-6-321g-944711e1e1604509", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-9558cc784085d86a", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-10-643-acdbe7fe682498df", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-99606e0f08a79d8f", "predicted_family": "frame", "priority": 0.737469961488, "sample_id": "us-code-42-14664.-32b9d5a819faf0f3", "target_family": "deontic"}`
