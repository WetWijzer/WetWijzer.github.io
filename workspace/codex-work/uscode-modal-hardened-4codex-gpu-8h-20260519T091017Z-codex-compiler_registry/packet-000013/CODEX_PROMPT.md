# packet-000013

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000013/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000013/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000013-20260519_094048

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-5f82ac2780f5dcd2` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.999856812397, "hint_id": "modal-synthesis-43f4982843d421e6", "predicted_family": "frame", "priority": 0.999987628694, "sample_id": "us-code-19-4584-b1c82116f196949b", "target_family": "temporal", "target_probability": 1.2371306e-05}`
  evidence: `{"family_margin": -0.995479656744, "hint_id": "modal-synthesis-93ad9e5038abf075", "predicted_family": "frame", "priority": 0.997978447765, "sample_id": "us-code-22-2370c-ecf99a4ce73acee6", "target_family": "temporal", "target_probability": 0.002021552235}`
- `program-aa18bf01c7a3234e` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.992893`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-1687715b971a9eae", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-10-2401a-ba138e3bdf2c6cc9", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": 0.181415197012, "hint_id": "modal-synthesis-8c8339dae19abcb5", "predicted_family": "frame", "priority": 0.571173346654, "sample_id": "us-code-19-1521-fc2b97217173a2ac", "target_family": "frame", "target_probability": 0.428826653346}`
- `program-8fea422b994b4b6b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.988768`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.475806685034, "hint_id": "modal-synthesis-754e05d1f2419378", "predicted_family": "frame", "priority": 0.9899670098, "sample_id": "us-code-22-2701-9339678f754757c1", "target_family": "epistemic", "target_probability": 0.0100329902}`
  evidence: `{"family_margin": -0.890473622324, "hint_id": "modal-synthesis-e7e0815a1a9a43a4", "predicted_family": "frame", "priority": 0.981858244056, "sample_id": "us-code-43-942-923f98d291d0a371", "target_family": "temporal", "target_probability": 0.018141755944}`
- `program-ae1d809bc22cbf8c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.980038`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.039721031037, "hint_id": "modal-synthesis-8d94b25431b45a81", "predicted_family": "frame", "priority": 0.523082848923, "sample_id": "us-code-42-17825.-eabe147e0629bb60", "target_family": "temporal", "target_probability": 0.476917151077}`
  evidence: `{"family_margin": -0.538411662487, "hint_id": "modal-synthesis-a638f19ced29033d", "predicted_family": "conditional_normative", "priority": 0.989385338127, "sample_id": "us-code-21-1602-97330a80c926f542", "target_family": "dynamic", "target_probability": 0.010614661873}`
- `program-9b36855d9816bc99` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->alethic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.97906`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.879491493241, "hint_id": "modal-synthesis-0288bda861f3c9f9", "predicted_family": "frame", "priority": 0.954119862665, "sample_id": "us-code-49-41310.-d010484de13ae8d0", "target_family": "deontic", "target_probability": 0.045880137335}`
  evidence: `{"family_margin": -0.739578936711, "hint_id": "modal-synthesis-7a452b35f86859de", "predicted_family": "frame", "priority": 0.989826945868, "sample_id": "us-code-29-3221-a5a6deb63d139047", "target_family": "alethic", "target_probability": 0.010173054132}`
- `program-8675c1cb295d37a6` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal","temporal->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.973393`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.240981950365, "hint_id": "modal-synthesis-1e17f08821c8fdc4", "predicted_family": "frame", "priority": 0.915664661152, "sample_id": "us-code-42-3271.-bbdebdd3b4a07703", "target_family": "temporal", "target_probability": 0.084335338848}`
  evidence: `{"family_margin": -0.65257734715, "hint_id": "modal-synthesis-2c9106935491e865", "predicted_family": "frame", "priority": 0.986239575159, "sample_id": "us-code-10-467-2e5d5d26ed55812b", "target_family": "conditional_normative", "target_probability": 0.013760424841}`
  evidence: `{"family_margin": -0.327726688886, "hint_id": "modal-synthesis-ab901eeae950bf26", "predicted_family": "temporal", "priority": 0.809270700849, "sample_id": "us-code-16-6551-10034197b0128141", "target_family": "epistemic", "target_probability": 0.190729299151}`

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
- TODO count: `6`

## TODOs
- `program-5f82ac2780f5dcd2`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.998983038229`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-19-4584-b1c82116f196949b, us-code-22-2370c-ecf99a4ce73acee6`
  evidence: `{"family_margin": -0.999856812397, "hint_id": "modal-synthesis-43f4982843d421e6", "predicted_family": "frame", "priority": 0.999987628694, "sample_id": "us-code-19-4584-b1c82116f196949b", "target_family": "temporal", "target_probability": 1.2371306e-05}`
  evidence: `{"family_margin": -0.995479656744, "hint_id": "modal-synthesis-93ad9e5038abf075", "predicted_family": "frame", "priority": 0.997978447765, "sample_id": "us-code-22-2370c-ecf99a4ce73acee6", "target_family": "temporal", "target_probability": 0.002021552235}`
- `program-aa18bf01c7a3234e`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.992893`
  loss: `autoencoder_residual_cluster` = `0.781540851466`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-2401a-ba138e3bdf2c6cc9, us-code-19-1521-fc2b97217173a2ac`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-1687715b971a9eae", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-10-2401a-ba138e3bdf2c6cc9", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": 0.181415197012, "hint_id": "modal-synthesis-8c8339dae19abcb5", "predicted_family": "frame", "priority": 0.571173346654, "sample_id": "us-code-19-1521-fc2b97217173a2ac", "target_family": "frame", "target_probability": 0.428826653346}`
- `program-8fea422b994b4b6b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.988768`
  loss: `autoencoder_residual_cluster` = `0.985912626928`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-2701-9339678f754757c1, us-code-43-942-923f98d291d0a371`
  evidence: `{"family_margin": -0.475806685034, "hint_id": "modal-synthesis-754e05d1f2419378", "predicted_family": "frame", "priority": 0.9899670098, "sample_id": "us-code-22-2701-9339678f754757c1", "target_family": "epistemic", "target_probability": 0.0100329902}`
  evidence: `{"family_margin": -0.890473622324, "hint_id": "modal-synthesis-e7e0815a1a9a43a4", "predicted_family": "frame", "priority": 0.981858244056, "sample_id": "us-code-43-942-923f98d291d0a371", "target_family": "temporal", "target_probability": 0.018141755944}`
- `program-ae1d809bc22cbf8c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.980038`
  loss: `autoencoder_residual_cluster` = `0.756234093525`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-21-1602-97330a80c926f542, us-code-42-17825.-eabe147e0629bb60`
  evidence: `{"family_margin": -0.039721031037, "hint_id": "modal-synthesis-8d94b25431b45a81", "predicted_family": "frame", "priority": 0.523082848923, "sample_id": "us-code-42-17825.-eabe147e0629bb60", "target_family": "temporal", "target_probability": 0.476917151077}`
  evidence: `{"family_margin": -0.538411662487, "hint_id": "modal-synthesis-a638f19ced29033d", "predicted_family": "conditional_normative", "priority": 0.989385338127, "sample_id": "us-code-21-1602-97330a80c926f542", "target_family": "dynamic", "target_probability": 0.010614661873}`
- `program-9b36855d9816bc99`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->alethic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.97906`
  loss: `autoencoder_residual_cluster` = `0.971973404267`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-29-3221-a5a6deb63d139047, us-code-49-41310.-d010484de13ae8d0`
  evidence: `{"family_margin": -0.879491493241, "hint_id": "modal-synthesis-0288bda861f3c9f9", "predicted_family": "frame", "priority": 0.954119862665, "sample_id": "us-code-49-41310.-d010484de13ae8d0", "target_family": "deontic", "target_probability": 0.045880137335}`
  evidence: `{"family_margin": -0.739578936711, "hint_id": "modal-synthesis-7a452b35f86859de", "predicted_family": "frame", "priority": 0.989826945868, "sample_id": "us-code-29-3221-a5a6deb63d139047", "target_family": "alethic", "target_probability": 0.010173054132}`
- `program-8675c1cb295d37a6`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal","temporal->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5f82ac2780f5dcd2` score `0.973393`
  loss: `autoencoder_residual_cluster` = `0.903724979053`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-467-2e5d5d26ed55812b, us-code-42-3271.-bbdebdd3b4a07703, us-code-16-6551-10034197b0128141`
  evidence: `{"family_margin": -0.240981950365, "hint_id": "modal-synthesis-1e17f08821c8fdc4", "predicted_family": "frame", "priority": 0.915664661152, "sample_id": "us-code-42-3271.-bbdebdd3b4a07703", "target_family": "temporal", "target_probability": 0.084335338848}`
  evidence: `{"family_margin": -0.65257734715, "hint_id": "modal-synthesis-2c9106935491e865", "predicted_family": "frame", "priority": 0.986239575159, "sample_id": "us-code-10-467-2e5d5d26ed55812b", "target_family": "conditional_normative", "target_probability": 0.013760424841}`
  evidence: `{"family_margin": -0.327726688886, "hint_id": "modal-synthesis-ab901eeae950bf26", "predicted_family": "temporal", "priority": 0.809270700849, "sample_id": "us-code-16-6551-10034197b0128141", "target_family": "epistemic", "target_probability": 0.190729299151}`
