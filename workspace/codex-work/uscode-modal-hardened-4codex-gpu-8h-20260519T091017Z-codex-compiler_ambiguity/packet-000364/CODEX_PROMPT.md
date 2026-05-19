# packet-000364

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000364/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000364/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000364-20260519_141449

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-88041efa9424279c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-88041efa9424279c` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999658532901, "hint_id": "modal-synthesis-39170cc488ad7698", "predicted_family": "frame", "priority": 1.149658532901, "sample_id": "us-code-22-1475e-bec3039174fdd403", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-7fe1a4cf7f0fff11", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-25-640-83a907ff97a1dbfe", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.909146257792, "hint_id": "modal-synthesis-a00d9db9022d55e8", "predicted_family": "frame", "priority": 1.059146257792, "sample_id": "us-code-10-20252-b0cdb1bc77136b17", "target_family": "temporal"}`
- `program-36767bbee8c8dcc0` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->alethic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-88041efa9424279c` score `0.979947`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.492615934833, "hint_id": "modal-synthesis-134197ee225716be", "predicted_family": "frame", "priority": 0.642615934833, "sample_id": "us-code-36-152302-3067b411c0c3067d", "target_family": "alethic"}`
  evidence: `{"family_margin": -0.902318654676, "hint_id": "modal-synthesis-2e1d0e2d621c9052", "predicted_family": "frame", "priority": 1.052318654676, "sample_id": "us-code-38-4103-444a14e5c270c515", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.351867372331, "hint_id": "modal-synthesis-4cf014049f1c0e37", "predicted_family": "frame", "priority": 0.501867372331, "sample_id": "us-code-20-9165-bf87f59846f54c29", "target_family": "temporal"}`

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
- `program-88041efa9424279c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-88041efa9424279c` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.786268263564`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-1475e-bec3039174fdd403, us-code-10-20252-b0cdb1bc77136b17, us-code-25-640-83a907ff97a1dbfe`
  evidence: `{"family_margin": -0.999658532901, "hint_id": "modal-synthesis-39170cc488ad7698", "predicted_family": "frame", "priority": 1.149658532901, "sample_id": "us-code-22-1475e-bec3039174fdd403", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-7fe1a4cf7f0fff11", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-25-640-83a907ff97a1dbfe", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.909146257792, "hint_id": "modal-synthesis-a00d9db9022d55e8", "predicted_family": "frame", "priority": 1.059146257792, "sample_id": "us-code-10-20252-b0cdb1bc77136b17", "target_family": "temporal"}`
- `program-36767bbee8c8dcc0`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->alethic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-88041efa9424279c` score `0.979947`
  loss: `autoencoder_residual_cluster` = `0.732267320613`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-38-4103-444a14e5c270c515, us-code-36-152302-3067b411c0c3067d, us-code-20-9165-bf87f59846f54c29`
  evidence: `{"family_margin": -0.492615934833, "hint_id": "modal-synthesis-134197ee225716be", "predicted_family": "frame", "priority": 0.642615934833, "sample_id": "us-code-36-152302-3067b411c0c3067d", "target_family": "alethic"}`
  evidence: `{"family_margin": -0.902318654676, "hint_id": "modal-synthesis-2e1d0e2d621c9052", "predicted_family": "frame", "priority": 1.052318654676, "sample_id": "us-code-38-4103-444a14e5c270c515", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.351867372331, "hint_id": "modal-synthesis-4cf014049f1c0e37", "predicted_family": "frame", "priority": 0.501867372331, "sample_id": "us-code-20-9165-bf87f59846f54c29", "target_family": "temporal"}`
