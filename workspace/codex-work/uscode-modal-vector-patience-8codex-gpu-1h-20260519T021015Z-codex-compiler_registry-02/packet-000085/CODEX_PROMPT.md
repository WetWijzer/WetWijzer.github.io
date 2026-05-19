# packet-000085

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/packet-000085/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/packet-000085/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000085-20260519_023119

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-9cbd139527a004b6` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->epistemic","conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.526872655614, "hint_id": "modal-synthesis-782f30150b914d42", "predicted_family": "frame", "priority": 0.995401876812, "sample_id": "us-code-20-3261-ea1591f1a07c9688", "target_family": "temporal", "target_probability": 0.004598123188}`
  evidence: `{"family_margin": -0.959954072958, "hint_id": "modal-synthesis-9227b731c8ca5951", "predicted_family": "conditional_normative", "priority": 0.982089790928, "sample_id": "us-code-20-1228c-c9995833bca47965", "target_family": "temporal", "target_probability": 0.017910209072}`
  evidence: `{"family_margin": -0.926239302123, "hint_id": "modal-synthesis-f335b14e820ff0be", "predicted_family": "conditional_normative", "priority": 0.999885678881, "sample_id": "us-code-5-6120-d6895339c5166af1", "target_family": "epistemic", "target_probability": 0.000114321119}`
- `program-21094a49ef1511ce` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->epistemic","deontic->frame","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.958978`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.590749662423, "hint_id": "modal-synthesis-79674014df8034a9", "predicted_family": "deontic", "priority": 0.965602383716, "sample_id": "us-code-42-300x-68c9c55c8a163c4d", "target_family": "frame", "target_probability": 0.034397616284}`
  evidence: `{"family_margin": -0.24602509287, "hint_id": "modal-synthesis-87ab1b497f39145b", "predicted_family": "conditional_normative", "priority": 0.856819126644, "sample_id": "us-code-16-450rr-5e94cfe81f6a5af1", "target_family": "epistemic", "target_probability": 0.143180873356}`
  evidence: `{"family_margin": -0.411885467434, "hint_id": "modal-synthesis-b84ecf1c3707a511", "predicted_family": "temporal", "priority": 0.760292252056, "sample_id": "us-code-25-181-b1aaf50455600eea", "target_family": "deontic", "target_probability": 0.239707747944}`
  evidence: `{"family_margin": -0.23602129703, "hint_id": "modal-synthesis-e4364c2320b7d696", "predicted_family": "frame", "priority": 0.636174567276, "sample_id": "us-code-18-3101-b020ea24c0c5ac85", "target_family": "temporal", "target_probability": 0.363825432724}`
- `program-ad38db7630564c44` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->dynamic","frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.954491`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.521443876084, "hint_id": "modal-synthesis-b018e0639299e085", "predicted_family": "alethic", "priority": 0.918384833689, "sample_id": "us-code-31-1531-68d5886a05c9885e", "target_family": "dynamic", "target_probability": 0.081615166311}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-e32a026fc1f057ed", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-20-2701-dd44f5dab9f1f127", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-fa3199eb6008873d", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-48-225.-05e380cce1a2872a", "target_family": "frame", "target_probability": 0.470915888067}`
- `program-e5c32ea3557dfb76` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->epistemic","frame->deontic","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.944596`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.861810021407, "hint_id": "modal-synthesis-6d29000f1ca1be76", "predicted_family": "temporal", "priority": 0.990465236862, "sample_id": "us-code-19-58b-d71e91a159ddef89", "target_family": "deontic", "target_probability": 0.009534763138}`
  evidence: `{"family_margin": -0.78969827777, "hint_id": "modal-synthesis-92fee0fd7d213989", "predicted_family": "frame", "priority": 0.912003318214, "sample_id": "us-code-30-2005-fb3e3d49bf0e1ddc", "target_family": "deontic", "target_probability": 0.087996681786}`
  evidence: `{"family_margin": -0.999954636578, "hint_id": "modal-synthesis-9f96d15b1cb27ba2", "predicted_family": "temporal", "priority": 0.999977455577, "sample_id": "us-code-20-1070d-2-28da4a8db201b083", "target_family": "frame", "target_probability": 2.2544423e-05}`
  evidence: `{"family_margin": -0.717202017907, "hint_id": "modal-synthesis-b075c24c2278a251", "predicted_family": "conditional_normative", "priority": 0.9999674376, "sample_id": "us-code-20-1234a-c0c9de2e60efc6b2", "target_family": "epistemic", "target_probability": 3.25624e-05}`
- `program-717fb0ff7e214a4c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->conditional_normative","frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.94134`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-7d33e207d1142152", "predicted_family": "frame", "priority": 0.833356638801, "sample_id": "us-code-36-20701-06bfdca7ebd52e4e", "target_family": "conditional_normative", "target_probability": 0.166643361199}`
  evidence: `{"family_margin": -0.605924338763, "hint_id": "modal-synthesis-7ef8e9b34d47fba2", "predicted_family": "frame", "priority": 0.823838220946, "sample_id": "us-code-30-186-07b06415e721dc2e", "target_family": "deontic", "target_probability": 0.176161779054}`
  evidence: `{"family_margin": 0.181415197012, "hint_id": "modal-synthesis-d266da2d3221d148", "predicted_family": "frame", "priority": 0.571173346654, "sample_id": "us-code-12-967-25a0a18721eb0a89", "target_family": "frame", "target_probability": 0.428826653346}`
  evidence: `{"family_margin": -0.39528005226, "hint_id": "modal-synthesis-fa90936854b846cf", "predicted_family": "deontic", "priority": 0.947885638523, "sample_id": "us-code-16-1423c-ada47c1062b73ed9", "target_family": "frame", "target_probability": 0.052114361477}`
- `program-26ca05595d7136b2` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.940086`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-5253dc62b76c3fb2", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-24-167-90fb69c7c9243a71", "target_family": "deontic", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": -0.772850545631, "hint_id": "modal-synthesis-6f33c8fc59012610", "predicted_family": "frame", "priority": 0.913880673864, "sample_id": "us-code-42-12212.-0d5fd6dec3abed58", "target_family": "deontic", "target_probability": 0.086119326136}`
  evidence: `{"family_margin": -0.994208040832, "hint_id": "modal-synthesis-84a803bd493df2ff", "predicted_family": "frame", "priority": 0.997523070135, "sample_id": "us-code-15-717s-9032e2706b24e7d3", "target_family": "deontic", "target_probability": 0.002476929865}`

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
- TODO count: `6`

## TODOs
- `program-9cbd139527a004b6`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->epistemic","conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.99245911554`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-5-6120-d6895339c5166af1, us-code-20-3261-ea1591f1a07c9688, us-code-20-1228c-c9995833bca47965`
  evidence: `{"family_margin": -0.526872655614, "hint_id": "modal-synthesis-782f30150b914d42", "predicted_family": "frame", "priority": 0.995401876812, "sample_id": "us-code-20-3261-ea1591f1a07c9688", "target_family": "temporal", "target_probability": 0.004598123188}`
  evidence: `{"family_margin": -0.959954072958, "hint_id": "modal-synthesis-9227b731c8ca5951", "predicted_family": "conditional_normative", "priority": 0.982089790928, "sample_id": "us-code-20-1228c-c9995833bca47965", "target_family": "temporal", "target_probability": 0.017910209072}`
  evidence: `{"family_margin": -0.926239302123, "hint_id": "modal-synthesis-f335b14e820ff0be", "predicted_family": "conditional_normative", "priority": 0.999885678881, "sample_id": "us-code-5-6120-d6895339c5166af1", "target_family": "epistemic", "target_probability": 0.000114321119}`
- `program-21094a49ef1511ce`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->epistemic","deontic->frame","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.958978`
  loss: `autoencoder_residual_cluster` = `0.804722082423`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-300x-68c9c55c8a163c4d, us-code-16-450rr-5e94cfe81f6a5af1, us-code-25-181-b1aaf50455600eea, us-code-18-3101-b020ea24c0c5ac85`
  evidence: `{"family_margin": -0.590749662423, "hint_id": "modal-synthesis-79674014df8034a9", "predicted_family": "deontic", "priority": 0.965602383716, "sample_id": "us-code-42-300x-68c9c55c8a163c4d", "target_family": "frame", "target_probability": 0.034397616284}`
  evidence: `{"family_margin": -0.24602509287, "hint_id": "modal-synthesis-87ab1b497f39145b", "predicted_family": "conditional_normative", "priority": 0.856819126644, "sample_id": "us-code-16-450rr-5e94cfe81f6a5af1", "target_family": "epistemic", "target_probability": 0.143180873356}`
  evidence: `{"family_margin": -0.411885467434, "hint_id": "modal-synthesis-b84ecf1c3707a511", "predicted_family": "temporal", "priority": 0.760292252056, "sample_id": "us-code-25-181-b1aaf50455600eea", "target_family": "deontic", "target_probability": 0.239707747944}`
  evidence: `{"family_margin": -0.23602129703, "hint_id": "modal-synthesis-e4364c2320b7d696", "predicted_family": "frame", "priority": 0.636174567276, "sample_id": "us-code-18-3101-b020ea24c0c5ac85", "target_family": "temporal", "target_probability": 0.363825432724}`
- `program-ad38db7630564c44`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->dynamic","frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.954491`
  loss: `autoencoder_residual_cluster` = `0.8131257673`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-20-2701-dd44f5dab9f1f127, us-code-31-1531-68d5886a05c9885e, us-code-48-225.-05e380cce1a2872a`
  evidence: `{"family_margin": -0.521443876084, "hint_id": "modal-synthesis-b018e0639299e085", "predicted_family": "alethic", "priority": 0.918384833689, "sample_id": "us-code-31-1531-68d5886a05c9885e", "target_family": "dynamic", "target_probability": 0.081615166311}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-e32a026fc1f057ed", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-20-2701-dd44f5dab9f1f127", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-fa3199eb6008873d", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-48-225.-05e380cce1a2872a", "target_family": "frame", "target_probability": 0.470915888067}`
- `program-e5c32ea3557dfb76`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->epistemic","frame->deontic","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.944596`
  loss: `autoencoder_residual_cluster` = `0.975603362063`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-20-1070d-2-28da4a8db201b083, us-code-20-1234a-c0c9de2e60efc6b2, us-code-19-58b-d71e91a159ddef89, us-code-30-2005-fb3e3d49bf0e1ddc`
  evidence: `{"family_margin": -0.861810021407, "hint_id": "modal-synthesis-6d29000f1ca1be76", "predicted_family": "temporal", "priority": 0.990465236862, "sample_id": "us-code-19-58b-d71e91a159ddef89", "target_family": "deontic", "target_probability": 0.009534763138}`
  evidence: `{"family_margin": -0.78969827777, "hint_id": "modal-synthesis-92fee0fd7d213989", "predicted_family": "frame", "priority": 0.912003318214, "sample_id": "us-code-30-2005-fb3e3d49bf0e1ddc", "target_family": "deontic", "target_probability": 0.087996681786}`
  evidence: `{"family_margin": -0.999954636578, "hint_id": "modal-synthesis-9f96d15b1cb27ba2", "predicted_family": "temporal", "priority": 0.999977455577, "sample_id": "us-code-20-1070d-2-28da4a8db201b083", "target_family": "frame", "target_probability": 2.2544423e-05}`
  evidence: `{"family_margin": -0.717202017907, "hint_id": "modal-synthesis-b075c24c2278a251", "predicted_family": "conditional_normative", "priority": 0.9999674376, "sample_id": "us-code-20-1234a-c0c9de2e60efc6b2", "target_family": "epistemic", "target_probability": 3.25624e-05}`
- `program-717fb0ff7e214a4c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->conditional_normative","frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.94134`
  loss: `autoencoder_residual_cluster` = `0.794063461231`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-1423c-ada47c1062b73ed9, us-code-36-20701-06bfdca7ebd52e4e, us-code-30-186-07b06415e721dc2e, us-code-12-967-25a0a18721eb0a89`
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-7d33e207d1142152", "predicted_family": "frame", "priority": 0.833356638801, "sample_id": "us-code-36-20701-06bfdca7ebd52e4e", "target_family": "conditional_normative", "target_probability": 0.166643361199}`
  evidence: `{"family_margin": -0.605924338763, "hint_id": "modal-synthesis-7ef8e9b34d47fba2", "predicted_family": "frame", "priority": 0.823838220946, "sample_id": "us-code-30-186-07b06415e721dc2e", "target_family": "deontic", "target_probability": 0.176161779054}`
  evidence: `{"family_margin": 0.181415197012, "hint_id": "modal-synthesis-d266da2d3221d148", "predicted_family": "frame", "priority": 0.571173346654, "sample_id": "us-code-12-967-25a0a18721eb0a89", "target_family": "frame", "target_probability": 0.428826653346}`
  evidence: `{"family_margin": -0.39528005226, "hint_id": "modal-synthesis-fa90936854b846cf", "predicted_family": "deontic", "priority": 0.947885638523, "sample_id": "us-code-16-1423c-ada47c1062b73ed9", "target_family": "frame", "target_probability": 0.052114361477}`
- `program-26ca05595d7136b2`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9cbd139527a004b6` score `0.940086`
  loss: `autoencoder_residual_cluster` = `0.80510229079`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-717s-9032e2706b24e7d3, us-code-42-12212.-0d5fd6dec3abed58, us-code-24-167-90fb69c7c9243a71`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-5253dc62b76c3fb2", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-24-167-90fb69c7c9243a71", "target_family": "deontic", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": -0.772850545631, "hint_id": "modal-synthesis-6f33c8fc59012610", "predicted_family": "frame", "priority": 0.913880673864, "sample_id": "us-code-42-12212.-0d5fd6dec3abed58", "target_family": "deontic", "target_probability": 0.086119326136}`
  evidence: `{"family_margin": -0.994208040832, "hint_id": "modal-synthesis-84a803bd493df2ff", "predicted_family": "frame", "priority": 0.997523070135, "sample_id": "us-code-15-717s-9032e2706b24e7d3", "target_family": "deontic", "target_probability": 0.002476929865}`
