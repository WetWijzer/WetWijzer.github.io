# packet-000168

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000168/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000168/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000168-20260519_123248

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-6800653849d07aa4` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6800653849d07aa4` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.357341769641, "hint_id": "modal-synthesis-5db5ca6404d9424a", "predicted_family": "temporal", "priority": 0.507341769641, "sample_id": "us-code-18-3489-81809bc90814bded", "target_family": "frame"}`
  evidence: `{"family_margin": -0.547477688285, "hint_id": "modal-synthesis-d975f71086e17d31", "predicted_family": "frame", "priority": 0.697477688285, "sample_id": "us-code-10-4008-1c09570d8ea648df", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.386346721929, "hint_id": "modal-synthesis-ef7115046276b5d2", "predicted_family": "temporal", "priority": 0.536346721929, "sample_id": "us-code-25-891-0d1251f72c528faf", "target_family": "deontic"}`
- `program-9ba579d7346b7a0f` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->alethic","frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6800653849d07aa4` score `0.990359`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-a8c353d7407d1934", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-29-1871-44485ec98810815a", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997162187617, "hint_id": "modal-synthesis-b929465822cfacc2", "predicted_family": "frame", "priority": 1.147162187617, "sample_id": "us-code-12-1715r-858d530b59362134", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-dc448da412a4aded", "predicted_family": "frame", "priority": 0.33771949257, "sample_id": "us-code-41-8506-7ecc8f89ca8b7ea9", "target_family": "alethic"}`
- `program-e9c97c0d76924c22` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6800653849d07aa4` score `0.975422`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.039660871697, "hint_id": "modal-synthesis-9a35cd4917d35b23", "predicted_family": "frame", "priority": 0.189660871697, "sample_id": "us-code-2-179p-0b9707e3aa4d8ab7", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.045940952004, "hint_id": "modal-synthesis-baed8fce6fe2918c", "predicted_family": "frame", "priority": 0.104059047996, "sample_id": "us-code-36-120104-69020357dc29b55a", "target_family": "frame"}`

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
- TODO count: `3`

## TODOs
- `program-6800653849d07aa4`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6800653849d07aa4` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.580388726618`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-4008-1c09570d8ea648df, us-code-25-891-0d1251f72c528faf, us-code-18-3489-81809bc90814bded`
  evidence: `{"family_margin": -0.357341769641, "hint_id": "modal-synthesis-5db5ca6404d9424a", "predicted_family": "temporal", "priority": 0.507341769641, "sample_id": "us-code-18-3489-81809bc90814bded", "target_family": "frame"}`
  evidence: `{"family_margin": -0.547477688285, "hint_id": "modal-synthesis-d975f71086e17d31", "predicted_family": "frame", "priority": 0.697477688285, "sample_id": "us-code-10-4008-1c09570d8ea648df", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.386346721929, "hint_id": "modal-synthesis-ef7115046276b5d2", "predicted_family": "temporal", "priority": 0.536346721929, "sample_id": "us-code-25-891-0d1251f72c528faf", "target_family": "deontic"}`
- `program-9ba579d7346b7a0f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->alethic","frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6800653849d07aa4` score `0.990359`
  loss: `autoencoder_residual_cluster` = `0.544960560062`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-1715r-858d530b59362134, us-code-41-8506-7ecc8f89ca8b7ea9, us-code-29-1871-44485ec98810815a`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-a8c353d7407d1934", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-29-1871-44485ec98810815a", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997162187617, "hint_id": "modal-synthesis-b929465822cfacc2", "predicted_family": "frame", "priority": 1.147162187617, "sample_id": "us-code-12-1715r-858d530b59362134", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-dc448da412a4aded", "predicted_family": "frame", "priority": 0.33771949257, "sample_id": "us-code-41-8506-7ecc8f89ca8b7ea9", "target_family": "alethic"}`
- `program-e9c97c0d76924c22`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6800653849d07aa4` score `0.975422`
  loss: `autoencoder_residual_cluster` = `0.146859959846`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-2-179p-0b9707e3aa4d8ab7, us-code-36-120104-69020357dc29b55a`
  evidence: `{"family_margin": -0.039660871697, "hint_id": "modal-synthesis-9a35cd4917d35b23", "predicted_family": "frame", "priority": 0.189660871697, "sample_id": "us-code-2-179p-0b9707e3aa4d8ab7", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.045940952004, "hint_id": "modal-synthesis-baed8fce6fe2918c", "predicted_family": "frame", "priority": 0.104059047996, "sample_id": "us-code-36-120104-69020357dc29b55a", "target_family": "frame"}`
