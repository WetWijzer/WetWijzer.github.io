# packet-000030

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000030/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000030/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000030-20260519_124207

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-7a9a1e331cc810e0` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.988612205682, "hint_id": "modal-synthesis-6a7053dffa1acc3c", "predicted_family": "frame", "priority": 0.995943188613, "sample_id": "us-code-40-6501-21da81a17feed968", "target_family": "conditional_normative", "target_probability": 0.004056811387}`
  evidence: `{"family_margin": -0.98096669603, "hint_id": "modal-synthesis-930622c812c7071d", "predicted_family": "frame", "priority": 0.995078848226, "sample_id": "us-code-12-5537-d5683383f045327e", "target_family": "epistemic", "target_probability": 0.004921151774}`
- `program-f45add3c325e87f3` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `0.974701`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.357341769641, "hint_id": "modal-synthesis-0f5f23dcc608ae76", "predicted_family": "temporal", "priority": 0.94406970856, "sample_id": "us-code-18-3489-81809bc90814bded", "target_family": "frame", "target_probability": 0.05593029144}`
  evidence: `{"family_margin": -0.386346721929, "hint_id": "modal-synthesis-cc294162383e8d94", "predicted_family": "temporal", "priority": 0.775155207062, "sample_id": "us-code-25-891-0d1251f72c528faf", "target_family": "deontic", "target_probability": 0.224844792938}`
  evidence: `{"family_margin": -0.547477688285, "hint_id": "modal-synthesis-fdac54d78f56e155", "predicted_family": "frame", "priority": 0.921838801059, "sample_id": "us-code-10-4008-1c09570d8ea648df", "target_family": "conditional_normative", "target_probability": 0.078161198941}`
- `program-111fa90fddceb6dd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["epistemic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `0.964155`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-0098ef02bf967227", "predicted_family": "epistemic", "priority": 0.700906819869, "sample_id": "us-code-16-1311-014f0ec1c47a5cce", "target_family": "deontic", "target_probability": 0.299093180131}`
  evidence: `{"family_margin": -0.960878504821, "hint_id": "modal-synthesis-3037109010bced1c", "predicted_family": "frame", "priority": 0.983852949754, "sample_id": "us-code-42-248a.-9261c2a788f1cbcf", "target_family": "deontic", "target_probability": 0.016147050246}`
  evidence: `{"family_margin": -0.972358698454, "hint_id": "modal-synthesis-a47dd340db0b0610", "predicted_family": "frame", "priority": 0.995380091479, "sample_id": "us-code-10-862-40c2d7c8f9a77d41", "target_family": "temporal", "target_probability": 0.004619908521}`
- `program-a27caf8582d3a3cd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `0.950781`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.039660871697, "hint_id": "modal-synthesis-37d1d621e1bb672f", "predicted_family": "frame", "priority": 0.570075628173, "sample_id": "us-code-2-179p-0b9707e3aa4d8ab7", "target_family": "deontic", "target_probability": 0.429924371827}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-5d5947f9879e3846", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-33-552-47f45acf7cf9d152", "target_family": "deontic", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": 0.045940952004, "hint_id": "modal-synthesis-67743b71b9d31d72", "predicted_family": "frame", "priority": 0.670182463971, "sample_id": "us-code-36-120104-69020357dc29b55a", "target_family": "frame", "target_probability": 0.329817536029}`
- `program-5b4b03686feee693` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `0.903044`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.676448880695, "hint_id": "modal-synthesis-03f874009e036d3e", "predicted_family": "deontic", "priority": 0.972713206719, "sample_id": "us-code-15-1847-830b651eb663dca8", "target_family": "temporal", "target_probability": 0.027286793281}`
  evidence: `{"family_margin": -0.17371933462, "hint_id": "modal-synthesis-530ed62536385c9e", "predicted_family": "frame", "priority": 0.732212673661, "sample_id": "us-code-34-12404-4c3ffacca50adfcf", "target_family": "temporal", "target_probability": 0.267787326339}`
  evidence: `{"family_margin": 0.178075660767, "hint_id": "modal-synthesis-7c6139b1095790d4", "predicted_family": "temporal", "priority": 0.627421095769, "sample_id": "us-code-7-8201-3aa281595960fc6a", "target_family": "temporal", "target_probability": 0.372578904231}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-9e4055b1bf5f1d72", "predicted_family": "deontic", "priority": 0.532843141424, "sample_id": "us-code-7-7424-e7673f78fca9418a", "target_family": "deontic", "target_probability": 0.467156858576}`

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
- TODO count: `5`

## TODOs
- `program-7a9a1e331cc810e0`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.995511018419`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-40-6501-21da81a17feed968, us-code-12-5537-d5683383f045327e`
  evidence: `{"family_margin": -0.988612205682, "hint_id": "modal-synthesis-6a7053dffa1acc3c", "predicted_family": "frame", "priority": 0.995943188613, "sample_id": "us-code-40-6501-21da81a17feed968", "target_family": "conditional_normative", "target_probability": 0.004056811387}`
  evidence: `{"family_margin": -0.98096669603, "hint_id": "modal-synthesis-930622c812c7071d", "predicted_family": "frame", "priority": 0.995078848226, "sample_id": "us-code-12-5537-d5683383f045327e", "target_family": "epistemic", "target_probability": 0.004921151774}`
- `program-f45add3c325e87f3`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `0.974701`
  loss: `autoencoder_residual_cluster` = `0.880354572227`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-18-3489-81809bc90814bded, us-code-10-4008-1c09570d8ea648df, us-code-25-891-0d1251f72c528faf`
  evidence: `{"family_margin": -0.357341769641, "hint_id": "modal-synthesis-0f5f23dcc608ae76", "predicted_family": "temporal", "priority": 0.94406970856, "sample_id": "us-code-18-3489-81809bc90814bded", "target_family": "frame", "target_probability": 0.05593029144}`
  evidence: `{"family_margin": -0.386346721929, "hint_id": "modal-synthesis-cc294162383e8d94", "predicted_family": "temporal", "priority": 0.775155207062, "sample_id": "us-code-25-891-0d1251f72c528faf", "target_family": "deontic", "target_probability": 0.224844792938}`
  evidence: `{"family_margin": -0.547477688285, "hint_id": "modal-synthesis-fdac54d78f56e155", "predicted_family": "frame", "priority": 0.921838801059, "sample_id": "us-code-10-4008-1c09570d8ea648df", "target_family": "conditional_normative", "target_probability": 0.078161198941}`
- `program-111fa90fddceb6dd`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["epistemic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `0.964155`
  loss: `autoencoder_residual_cluster` = `0.893379953701`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-862-40c2d7c8f9a77d41, us-code-42-248a.-9261c2a788f1cbcf, us-code-16-1311-014f0ec1c47a5cce`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-0098ef02bf967227", "predicted_family": "epistemic", "priority": 0.700906819869, "sample_id": "us-code-16-1311-014f0ec1c47a5cce", "target_family": "deontic", "target_probability": 0.299093180131}`
  evidence: `{"family_margin": -0.960878504821, "hint_id": "modal-synthesis-3037109010bced1c", "predicted_family": "frame", "priority": 0.983852949754, "sample_id": "us-code-42-248a.-9261c2a788f1cbcf", "target_family": "deontic", "target_probability": 0.016147050246}`
  evidence: `{"family_margin": -0.972358698454, "hint_id": "modal-synthesis-a47dd340db0b0610", "predicted_family": "frame", "priority": 0.995380091479, "sample_id": "us-code-10-862-40c2d7c8f9a77d41", "target_family": "temporal", "target_probability": 0.004619908521}`
- `program-a27caf8582d3a3cd`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `0.950781`
  loss: `autoencoder_residual_cluster` = `0.581387073505`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-36-120104-69020357dc29b55a, us-code-2-179p-0b9707e3aa4d8ab7, us-code-33-552-47f45acf7cf9d152`
  evidence: `{"family_margin": -0.039660871697, "hint_id": "modal-synthesis-37d1d621e1bb672f", "predicted_family": "frame", "priority": 0.570075628173, "sample_id": "us-code-2-179p-0b9707e3aa4d8ab7", "target_family": "deontic", "target_probability": 0.429924371827}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-5d5947f9879e3846", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-33-552-47f45acf7cf9d152", "target_family": "deontic", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": 0.045940952004, "hint_id": "modal-synthesis-67743b71b9d31d72", "predicted_family": "frame", "priority": 0.670182463971, "sample_id": "us-code-36-120104-69020357dc29b55a", "target_family": "frame", "target_probability": 0.329817536029}`
- `program-5b4b03686feee693`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-7a9a1e331cc810e0` score `0.903044`
  loss: `autoencoder_residual_cluster` = `0.716297529393`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-1847-830b651eb663dca8, us-code-34-12404-4c3ffacca50adfcf, us-code-7-8201-3aa281595960fc6a, us-code-7-7424-e7673f78fca9418a`
  evidence: `{"family_margin": -0.676448880695, "hint_id": "modal-synthesis-03f874009e036d3e", "predicted_family": "deontic", "priority": 0.972713206719, "sample_id": "us-code-15-1847-830b651eb663dca8", "target_family": "temporal", "target_probability": 0.027286793281}`
  evidence: `{"family_margin": -0.17371933462, "hint_id": "modal-synthesis-530ed62536385c9e", "predicted_family": "frame", "priority": 0.732212673661, "sample_id": "us-code-34-12404-4c3ffacca50adfcf", "target_family": "temporal", "target_probability": 0.267787326339}`
  evidence: `{"family_margin": 0.178075660767, "hint_id": "modal-synthesis-7c6139b1095790d4", "predicted_family": "temporal", "priority": 0.627421095769, "sample_id": "us-code-7-8201-3aa281595960fc6a", "target_family": "temporal", "target_probability": 0.372578904231}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-9e4055b1bf5f1d72", "predicted_family": "deontic", "priority": 0.532843141424, "sample_id": "us-code-7-7424-e7673f78fca9418a", "target_family": "deontic", "target_probability": 0.467156858576}`
