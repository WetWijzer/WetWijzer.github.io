# packet-000065

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000065/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/packet-000065/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000065-20260519_025345

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-5c90599b77c1b484` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5c90599b77c1b484` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.996964123361, "hint_id": "modal-synthesis-49451289e81526f8", "predicted_family": "conditional_normative", "priority": 0.999943660133, "sample_id": "us-code-12-4903-c51b25897c2970fa", "target_family": "deontic", "target_probability": 5.6339867e-05}`
  evidence: `{"family_margin": -0.992795485564, "hint_id": "modal-synthesis-a1ddacad1d54ddf5", "predicted_family": "temporal", "priority": 0.999774584604, "sample_id": "us-code-42-10905.-8d64d69700c2a65f", "target_family": "deontic", "target_probability": 0.000225415396}`
  evidence: `{"family_margin": -0.996101512482, "hint_id": "modal-synthesis-d62b80d082e62720", "predicted_family": "frame", "priority": 0.999326639923, "sample_id": "us-code-42-19038.-c2a8a75459132351", "target_family": "conditional_normative", "target_probability": 0.000673360077}`
- `program-d1e0789cd1f60b69` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5c90599b77c1b484` score `0.986374`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.993897627543, "hint_id": "modal-synthesis-ab0ad5c6c2c0384f", "predicted_family": "frame", "priority": 0.999957075933, "sample_id": "us-code-42-4369.-7326d01e59fb968d", "target_family": "temporal", "target_probability": 4.2924067e-05}`
  evidence: `{"family_margin": -0.401650452649, "hint_id": "modal-synthesis-da693c2c8b6d575f", "predicted_family": "conditional_normative", "priority": 0.73412818631, "sample_id": "us-code-16-460ccc-2-50d796783c99a93f", "target_family": "deontic", "target_probability": 0.26587181369}`
  evidence: `{"family_margin": -0.699184261763, "hint_id": "modal-synthesis-fbf855ab4459409e", "predicted_family": "deontic", "priority": 0.883469289706, "sample_id": "us-code-22-2719c-3a5433eebe61d2d1", "target_family": "temporal", "target_probability": 0.116530710294}`

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
- `program-5c90599b77c1b484`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5c90599b77c1b484` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.99968162822`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-4903-c51b25897c2970fa, us-code-42-10905.-8d64d69700c2a65f, us-code-42-19038.-c2a8a75459132351`
  evidence: `{"family_margin": -0.996964123361, "hint_id": "modal-synthesis-49451289e81526f8", "predicted_family": "conditional_normative", "priority": 0.999943660133, "sample_id": "us-code-12-4903-c51b25897c2970fa", "target_family": "deontic", "target_probability": 5.6339867e-05}`
  evidence: `{"family_margin": -0.992795485564, "hint_id": "modal-synthesis-a1ddacad1d54ddf5", "predicted_family": "temporal", "priority": 0.999774584604, "sample_id": "us-code-42-10905.-8d64d69700c2a65f", "target_family": "deontic", "target_probability": 0.000225415396}`
  evidence: `{"family_margin": -0.996101512482, "hint_id": "modal-synthesis-d62b80d082e62720", "predicted_family": "frame", "priority": 0.999326639923, "sample_id": "us-code-42-19038.-c2a8a75459132351", "target_family": "conditional_normative", "target_probability": 0.000673360077}`
- `program-d1e0789cd1f60b69`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5c90599b77c1b484` score `0.986374`
  loss: `autoencoder_residual_cluster` = `0.872518183983`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-4369.-7326d01e59fb968d, us-code-22-2719c-3a5433eebe61d2d1, us-code-16-460ccc-2-50d796783c99a93f`
  evidence: `{"family_margin": -0.993897627543, "hint_id": "modal-synthesis-ab0ad5c6c2c0384f", "predicted_family": "frame", "priority": 0.999957075933, "sample_id": "us-code-42-4369.-7326d01e59fb968d", "target_family": "temporal", "target_probability": 4.2924067e-05}`
  evidence: `{"family_margin": -0.401650452649, "hint_id": "modal-synthesis-da693c2c8b6d575f", "predicted_family": "conditional_normative", "priority": 0.73412818631, "sample_id": "us-code-16-460ccc-2-50d796783c99a93f", "target_family": "deontic", "target_probability": 0.26587181369}`
  evidence: `{"family_margin": -0.699184261763, "hint_id": "modal-synthesis-fbf855ab4459409e", "predicted_family": "deontic", "priority": 0.883469289706, "sample_id": "us-code-22-2719c-3a5433eebe61d2d1", "target_family": "temporal", "target_probability": 0.116530710294}`
