# packet-000210

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000210/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000210/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000210-20260519_131953

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-31ccc1a3b33c4cf9` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","alethic->epistemic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-31ccc1a3b33c4cf9` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.601340220277, "hint_id": "modal-synthesis-053f894067ea75fb", "predicted_family": "frame", "priority": 0.751340220277, "sample_id": "us-code-7-1637b-770ebbeb9330c4fd", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.896839706151, "hint_id": "modal-synthesis-34277d6f81384843", "predicted_family": "alethic", "priority": 1.046839706151, "sample_id": "us-code-42-247b-6963b9eb980a0dcf", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.326486646276, "hint_id": "modal-synthesis-858e295710f8f835", "predicted_family": "alethic", "priority": 0.476486646276, "sample_id": "us-code-20-4011-f7a21f791039ec23", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.963149640055, "hint_id": "modal-synthesis-af5531092ec22610", "predicted_family": "frame", "priority": 1.113149640055, "sample_id": "us-code-49-10901.-36145fd5d606aea9", "target_family": "deontic"}`
- `program-9f168e3188dd1bbd` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-31ccc1a3b33c4cf9` score `0.969036`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.132081408712, "hint_id": "modal-synthesis-49b4e5a5c76baf40", "predicted_family": "conditional_normative", "priority": 0.282081408712, "sample_id": "us-code-12-4586-94f51ab219e6e58d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.823537218695, "hint_id": "modal-synthesis-6fbe5cdf79aeea6c", "predicted_family": "frame", "priority": 0.973537218695, "sample_id": "us-code-16-698n-c9d56fba5f06bc9d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.963281367381, "hint_id": "modal-synthesis-f01f2cf7cb1305a1", "predicted_family": "frame", "priority": 1.113281367381, "sample_id": "us-code-15-6612-47fab61cbad1138a", "target_family": "conditional_normative"}`

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
- `program-31ccc1a3b33c4cf9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","alethic->epistemic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-31ccc1a3b33c4cf9` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.84695405319`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-10901.-36145fd5d606aea9, us-code-42-247b-6963b9eb980a0dcf, us-code-7-1637b-770ebbeb9330c4fd, us-code-20-4011-f7a21f791039ec23`
  evidence: `{"family_margin": -0.601340220277, "hint_id": "modal-synthesis-053f894067ea75fb", "predicted_family": "frame", "priority": 0.751340220277, "sample_id": "us-code-7-1637b-770ebbeb9330c4fd", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.896839706151, "hint_id": "modal-synthesis-34277d6f81384843", "predicted_family": "alethic", "priority": 1.046839706151, "sample_id": "us-code-42-247b-6963b9eb980a0dcf", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.326486646276, "hint_id": "modal-synthesis-858e295710f8f835", "predicted_family": "alethic", "priority": 0.476486646276, "sample_id": "us-code-20-4011-f7a21f791039ec23", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.963149640055, "hint_id": "modal-synthesis-af5531092ec22610", "predicted_family": "frame", "priority": 1.113149640055, "sample_id": "us-code-49-10901.-36145fd5d606aea9", "target_family": "deontic"}`
- `program-9f168e3188dd1bbd`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-31ccc1a3b33c4cf9` score `0.969036`
  loss: `autoencoder_residual_cluster` = `0.789633331596`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-6612-47fab61cbad1138a, us-code-16-698n-c9d56fba5f06bc9d, us-code-12-4586-94f51ab219e6e58d`
  evidence: `{"family_margin": -0.132081408712, "hint_id": "modal-synthesis-49b4e5a5c76baf40", "predicted_family": "conditional_normative", "priority": 0.282081408712, "sample_id": "us-code-12-4586-94f51ab219e6e58d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.823537218695, "hint_id": "modal-synthesis-6fbe5cdf79aeea6c", "predicted_family": "frame", "priority": 0.973537218695, "sample_id": "us-code-16-698n-c9d56fba5f06bc9d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.963281367381, "hint_id": "modal-synthesis-f01f2cf7cb1305a1", "predicted_family": "frame", "priority": 1.113281367381, "sample_id": "us-code-15-6612-47fab61cbad1138a", "target_family": "conditional_normative"}`
