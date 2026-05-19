# packet-000069

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000069/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000069/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000069-20260519_081847

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-3e3c26921daa7306` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-3e3c26921daa7306` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.682556350277, "hint_id": "modal-synthesis-046c5c022883d966", "predicted_family": "frame", "priority": 0.832556350277, "sample_id": "us-code-26-139-82a119f84c138de9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.996115322895, "hint_id": "modal-synthesis-16ed5f401bf541d1", "predicted_family": "frame", "priority": 1.146115322895, "sample_id": "us-code-18-2390-2ec34985c23a201f", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.411051110913, "hint_id": "modal-synthesis-a1f0e6aad9e45a67", "predicted_family": "frame", "priority": 0.561051110913, "sample_id": "us-code-52-21002.-d05dd94e9769439a", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.645620261067, "hint_id": "modal-synthesis-b5c665234a20dbbd", "predicted_family": "deontic", "priority": 0.795620261067, "sample_id": "us-code-42-19120.-538c8ab76679781a", "target_family": "temporal"}`
- `program-53c32308be28e666` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-3e3c26921daa7306` score `0.965563`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.871848671962, "hint_id": "modal-synthesis-2f0b1d171413bf6f", "predicted_family": "frame", "priority": 1.021848671962, "sample_id": "us-code-38-7405-5a48188b1b79bce0", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.139673778321, "hint_id": "modal-synthesis-be315e46ed6a19bb", "predicted_family": "deontic", "priority": 0.010326221679, "sample_id": "us-code-16-450e-1-c701fe3463da7053", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999537374177, "hint_id": "modal-synthesis-ccd29659c2430a53", "predicted_family": "temporal", "priority": 1.149537374177, "sample_id": "us-code-20-9133-1be94617ef12a512", "target_family": "conditional_normative"}`

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
- TODO count: `2`

## TODOs
- `program-3e3c26921daa7306`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-3e3c26921daa7306` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.833835761288`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-18-2390-2ec34985c23a201f, us-code-26-139-82a119f84c138de9, us-code-42-19120.-538c8ab76679781a, us-code-52-21002.-d05dd94e9769439a`
  evidence: `{"family_margin": -0.682556350277, "hint_id": "modal-synthesis-046c5c022883d966", "predicted_family": "frame", "priority": 0.832556350277, "sample_id": "us-code-26-139-82a119f84c138de9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.996115322895, "hint_id": "modal-synthesis-16ed5f401bf541d1", "predicted_family": "frame", "priority": 1.146115322895, "sample_id": "us-code-18-2390-2ec34985c23a201f", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.411051110913, "hint_id": "modal-synthesis-a1f0e6aad9e45a67", "predicted_family": "frame", "priority": 0.561051110913, "sample_id": "us-code-52-21002.-d05dd94e9769439a", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.645620261067, "hint_id": "modal-synthesis-b5c665234a20dbbd", "predicted_family": "deontic", "priority": 0.795620261067, "sample_id": "us-code-42-19120.-538c8ab76679781a", "target_family": "temporal"}`
- `program-53c32308be28e666`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-3e3c26921daa7306` score `0.965563`
  loss: `autoencoder_residual_cluster` = `0.727237422606`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-20-9133-1be94617ef12a512, us-code-38-7405-5a48188b1b79bce0, us-code-16-450e-1-c701fe3463da7053`
  evidence: `{"family_margin": -0.871848671962, "hint_id": "modal-synthesis-2f0b1d171413bf6f", "predicted_family": "frame", "priority": 1.021848671962, "sample_id": "us-code-38-7405-5a48188b1b79bce0", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.139673778321, "hint_id": "modal-synthesis-be315e46ed6a19bb", "predicted_family": "deontic", "priority": 0.010326221679, "sample_id": "us-code-16-450e-1-c701fe3463da7053", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999537374177, "hint_id": "modal-synthesis-ccd29659c2430a53", "predicted_family": "temporal", "priority": 1.149537374177, "sample_id": "us-code-20-9133-1be94617ef12a512", "target_family": "conditional_normative"}`
