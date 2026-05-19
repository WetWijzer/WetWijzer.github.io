# packet-000055

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/packet-000055/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/packet-000055/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000055-20260519_074633

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-ef3bce8f7e726f6c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ef3bce8f7e726f6c` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.924813751676, "hint_id": "modal-synthesis-873509de2bd95e2b", "predicted_family": "frame", "priority": 1.074813751676, "sample_id": "us-code-10-2686-307cb92f2d3705e2", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.92479320096, "hint_id": "modal-synthesis-8ecce9f196f1d9cb", "predicted_family": "frame", "priority": 1.07479320096, "sample_id": "us-code-48-1401 to 1401e.-1dadd607f4660f80", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.908038226995, "hint_id": "modal-synthesis-99ae65567b395bfa", "predicted_family": "frame", "priority": 1.058038226995, "sample_id": "us-code-31-752-e21314fdb8298fb0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.949451098605, "hint_id": "modal-synthesis-e86ddb268f7bad65", "predicted_family": "temporal", "priority": 1.099451098605, "sample_id": "us-code-38-7315-c771bec603cdd386", "target_family": "frame"}`
- `program-8add50634446eca3` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ef3bce8f7e726f6c` score `0.971619`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-2184e577a53731d4", "predicted_family": "temporal", "priority": 1.15, "sample_id": "us-code-33-1285-0f09f4e18c1d7f89", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999999696178, "hint_id": "modal-synthesis-a337ace7048f62fd", "predicted_family": "temporal", "priority": 1.149999696178, "sample_id": "us-code-33-1445-5a47b1c625b0b326", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-a7bf4031e744aef6", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-16-460fff-2-b3e50a7dd666fabf", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.981256325663, "hint_id": "modal-synthesis-bc1d88ceb4760d46", "predicted_family": "frame", "priority": 1.131256325663, "sample_id": "us-code-49-5901.-00792fcbc2b1263f", "target_family": "conditional_normative"}`
- `program-8badb741abc40abe` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["temporal->conditional_normative","temporal->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ef3bce8f7e726f6c` score `0.956295`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.057221302216, "hint_id": "modal-synthesis-44ad284f3ff64a41", "predicted_family": "temporal", "priority": 0.092778697784, "sample_id": "us-code-10-4652-4b570702787c893f", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.068489551327, "hint_id": "modal-synthesis-9c7c1baa2f6d9655", "predicted_family": "temporal", "priority": 0.218489551327, "sample_id": "us-code-12-214a-71d543320eec73fc", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.558201193929, "hint_id": "modal-synthesis-b4cca8bc77c6284b", "predicted_family": "temporal", "priority": 0.708201193929, "sample_id": "us-code-50-3734.-53bf86760d22cdad", "target_family": "conditional_normative"}`
- `program-38994efc19c677f0` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ef3bce8f7e726f6c` score `0.930766`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.998647484376, "hint_id": "modal-synthesis-7aa2884ea9dc279d", "predicted_family": "alethic", "priority": 1.148647484376, "sample_id": "us-code-5-5702-300a57e6beeea23d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.560778212654, "hint_id": "modal-synthesis-91db40b7f1973818", "predicted_family": "temporal", "priority": 0.710778212654, "sample_id": "us-code-19-273-7820f6e8db339143", "target_family": "deontic"}`

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
- TODO count: `4`

## TODOs
- `program-ef3bce8f7e726f6c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ef3bce8f7e726f6c` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.076774069559`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-38-7315-c771bec603cdd386, us-code-10-2686-307cb92f2d3705e2, us-code-48-1401 to 1401e.-1dadd607f4660f80, us-code-31-752-e21314fdb8298fb0`
  evidence: `{"family_margin": -0.924813751676, "hint_id": "modal-synthesis-873509de2bd95e2b", "predicted_family": "frame", "priority": 1.074813751676, "sample_id": "us-code-10-2686-307cb92f2d3705e2", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.92479320096, "hint_id": "modal-synthesis-8ecce9f196f1d9cb", "predicted_family": "frame", "priority": 1.07479320096, "sample_id": "us-code-48-1401 to 1401e.-1dadd607f4660f80", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.908038226995, "hint_id": "modal-synthesis-99ae65567b395bfa", "predicted_family": "frame", "priority": 1.058038226995, "sample_id": "us-code-31-752-e21314fdb8298fb0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.949451098605, "hint_id": "modal-synthesis-e86ddb268f7bad65", "predicted_family": "temporal", "priority": 1.099451098605, "sample_id": "us-code-38-7315-c771bec603cdd386", "target_family": "frame"}`
- `program-8add50634446eca3`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ef3bce8f7e726f6c` score `0.971619`
  loss: `autoencoder_residual_cluster` = `0.89531400546`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-33-1285-0f09f4e18c1d7f89, us-code-33-1445-5a47b1c625b0b326, us-code-49-5901.-00792fcbc2b1263f, us-code-16-460fff-2-b3e50a7dd666fabf`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-2184e577a53731d4", "predicted_family": "temporal", "priority": 1.15, "sample_id": "us-code-33-1285-0f09f4e18c1d7f89", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999999696178, "hint_id": "modal-synthesis-a337ace7048f62fd", "predicted_family": "temporal", "priority": 1.149999696178, "sample_id": "us-code-33-1445-5a47b1c625b0b326", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-a7bf4031e744aef6", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-16-460fff-2-b3e50a7dd666fabf", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.981256325663, "hint_id": "modal-synthesis-bc1d88ceb4760d46", "predicted_family": "frame", "priority": 1.131256325663, "sample_id": "us-code-49-5901.-00792fcbc2b1263f", "target_family": "conditional_normative"}`
- `program-8badb741abc40abe`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["temporal->conditional_normative","temporal->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ef3bce8f7e726f6c` score `0.956295`
  loss: `autoencoder_residual_cluster` = `0.33982314768`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-50-3734.-53bf86760d22cdad, us-code-12-214a-71d543320eec73fc, us-code-10-4652-4b570702787c893f`
  evidence: `{"family_margin": 0.057221302216, "hint_id": "modal-synthesis-44ad284f3ff64a41", "predicted_family": "temporal", "priority": 0.092778697784, "sample_id": "us-code-10-4652-4b570702787c893f", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.068489551327, "hint_id": "modal-synthesis-9c7c1baa2f6d9655", "predicted_family": "temporal", "priority": 0.218489551327, "sample_id": "us-code-12-214a-71d543320eec73fc", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.558201193929, "hint_id": "modal-synthesis-b4cca8bc77c6284b", "predicted_family": "temporal", "priority": 0.708201193929, "sample_id": "us-code-50-3734.-53bf86760d22cdad", "target_family": "conditional_normative"}`
- `program-38994efc19c677f0`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ef3bce8f7e726f6c` score `0.930766`
  loss: `autoencoder_residual_cluster` = `0.929712848515`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-5-5702-300a57e6beeea23d, us-code-19-273-7820f6e8db339143`
  evidence: `{"family_margin": -0.998647484376, "hint_id": "modal-synthesis-7aa2884ea9dc279d", "predicted_family": "alethic", "priority": 1.148647484376, "sample_id": "us-code-5-5702-300a57e6beeea23d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.560778212654, "hint_id": "modal-synthesis-91db40b7f1973818", "predicted_family": "temporal", "priority": 0.710778212654, "sample_id": "us-code-19-273-7820f6e8db339143", "target_family": "deontic"}`
