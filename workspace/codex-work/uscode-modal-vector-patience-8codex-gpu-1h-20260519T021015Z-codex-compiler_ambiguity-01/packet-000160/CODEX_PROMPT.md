# packet-000160

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000160/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000160/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000160-20260519_031122

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-543878e6c857b3e5` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","conditional_normative->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-543878e6c857b3e5` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-3d9f0d29bde43a15", "predicted_family": "conditional_normative", "priority": 1.15, "sample_id": "us-code-43-1629c.-fc78c6059bfddd73", "target_family": "deontic"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-df9c4307a8a71c5a", "predicted_family": "conditional_normative", "priority": 1.15, "sample_id": "us-code-45-1203.-a58696791a840de6", "target_family": "frame"}`
- `program-75966b8c15a49807` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-543878e6c857b3e5` score `0.972857`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.814531998077, "hint_id": "modal-synthesis-200511c705653a1e", "predicted_family": "frame", "priority": 0.964531998077, "sample_id": "us-code-38-1720I-3410e13660f6b6a4", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.941090534922, "hint_id": "modal-synthesis-7d6a24787c812583", "predicted_family": "frame", "priority": 1.091090534922, "sample_id": "us-code-12-1816-c0b440c716f086be", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.848890749741, "hint_id": "modal-synthesis-e3bb5fda120df586", "predicted_family": "temporal", "priority": 0.998890749741, "sample_id": "us-code-20-806-b393baca996842b5", "target_family": "deontic"}`

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

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-543878e6c857b3e5`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","conditional_normative->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-543878e6c857b3e5` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.15`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-43-1629c.-fc78c6059bfddd73, us-code-45-1203.-a58696791a840de6`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-3d9f0d29bde43a15", "predicted_family": "conditional_normative", "priority": 1.15, "sample_id": "us-code-43-1629c.-fc78c6059bfddd73", "target_family": "deontic"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-df9c4307a8a71c5a", "predicted_family": "conditional_normative", "priority": 1.15, "sample_id": "us-code-45-1203.-a58696791a840de6", "target_family": "frame"}`
- `program-75966b8c15a49807`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-543878e6c857b3e5` score `0.972857`
  loss: `autoencoder_residual_cluster` = `1.018171094247`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-1816-c0b440c716f086be, us-code-20-806-b393baca996842b5, us-code-38-1720I-3410e13660f6b6a4`
  evidence: `{"family_margin": -0.814531998077, "hint_id": "modal-synthesis-200511c705653a1e", "predicted_family": "frame", "priority": 0.964531998077, "sample_id": "us-code-38-1720I-3410e13660f6b6a4", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.941090534922, "hint_id": "modal-synthesis-7d6a24787c812583", "predicted_family": "frame", "priority": 1.091090534922, "sample_id": "us-code-12-1816-c0b440c716f086be", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.848890749741, "hint_id": "modal-synthesis-e3bb5fda120df586", "predicted_family": "temporal", "priority": 0.998890749741, "sample_id": "us-code-20-806-b393baca996842b5", "target_family": "deontic"}`
