# packet-000472

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000472/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000472/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000472-20260519_153850

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-5eb8448439d4ac28` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5eb8448439d4ac28` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.993831777206, "hint_id": "modal-synthesis-43340d7356d26427", "predicted_family": "frame", "priority": 1.143831777206, "sample_id": "us-code-42-629c.-0c65fdd9d705e10f", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.997248992505, "hint_id": "modal-synthesis-890089fea384fa6b", "predicted_family": "frame", "priority": 1.147248992505, "sample_id": "us-code-42-1462 to 1464.-d3f2aa981c9b2a49", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.100948406036, "hint_id": "modal-synthesis-a64be8644014c64e", "predicted_family": "temporal", "priority": 0.250948406036, "sample_id": "us-code-5-3322-9e1940d99b2f959b", "target_family": "conditional_normative"}`
- `program-22f34cab6e6dc67f` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5eb8448439d4ac28` score `0.940304`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.855052736961, "hint_id": "modal-synthesis-49867627ea015580", "predicted_family": "deontic", "priority": 1.005052736961, "sample_id": "us-code-7-7938-2cfe2905ba85c147", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.257220043655, "hint_id": "modal-synthesis-55ee4cf9f9421013", "predicted_family": "deontic", "priority": 0.407220043655, "sample_id": "us-code-16-3839bb-4-2e2cffbbcd871d5d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.963701676952, "hint_id": "modal-synthesis-75697cc69b16ecd7", "predicted_family": "frame", "priority": 1.113701676952, "sample_id": "us-code-49-47145.-6f26cd3923bc5e97", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-bb93041ea9cf4ded", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-43-3206.-3d30a15d59827936", "target_family": "deontic"}`

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
- `program-5eb8448439d4ac28`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5eb8448439d4ac28` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.847343058582`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1462 to 1464.-d3f2aa981c9b2a49, us-code-42-629c.-0c65fdd9d705e10f, us-code-5-3322-9e1940d99b2f959b`
  evidence: `{"family_margin": -0.993831777206, "hint_id": "modal-synthesis-43340d7356d26427", "predicted_family": "frame", "priority": 1.143831777206, "sample_id": "us-code-42-629c.-0c65fdd9d705e10f", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.997248992505, "hint_id": "modal-synthesis-890089fea384fa6b", "predicted_family": "frame", "priority": 1.147248992505, "sample_id": "us-code-42-1462 to 1464.-d3f2aa981c9b2a49", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.100948406036, "hint_id": "modal-synthesis-a64be8644014c64e", "predicted_family": "temporal", "priority": 0.250948406036, "sample_id": "us-code-5-3322-9e1940d99b2f959b", "target_family": "conditional_normative"}`
- `program-22f34cab6e6dc67f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-5eb8448439d4ac28` score `0.940304`
  loss: `autoencoder_residual_cluster` = `0.668993614392`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-47145.-6f26cd3923bc5e97, us-code-7-7938-2cfe2905ba85c147, us-code-16-3839bb-4-2e2cffbbcd871d5d, us-code-43-3206.-3d30a15d59827936`
  evidence: `{"family_margin": -0.855052736961, "hint_id": "modal-synthesis-49867627ea015580", "predicted_family": "deontic", "priority": 1.005052736961, "sample_id": "us-code-7-7938-2cfe2905ba85c147", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.257220043655, "hint_id": "modal-synthesis-55ee4cf9f9421013", "predicted_family": "deontic", "priority": 0.407220043655, "sample_id": "us-code-16-3839bb-4-2e2cffbbcd871d5d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.963701676952, "hint_id": "modal-synthesis-75697cc69b16ecd7", "predicted_family": "frame", "priority": 1.113701676952, "sample_id": "us-code-49-47145.-6f26cd3923bc5e97", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-bb93041ea9cf4ded", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-43-3206.-3d30a15d59827936", "target_family": "deontic"}`
