# packet-000014

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/packet-000014/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/packet-000014/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000014-20260518_234939

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-dc58403bb8e1ee87` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.999999999972, "hint_id": "modal-synthesis-badd1e081a72dd05", "predicted_family": "deontic", "priority": 0.999999999986, "sample_id": "us-code-18-924-b00c213963a376b4", "target_family": "conditional_normative", "target_probability": 1.4e-11}`
  evidence: `{"family_margin": -0.999522018876, "hint_id": "modal-synthesis-c019cc9bc722c162", "predicted_family": "frame", "priority": 0.999928827702, "sample_id": "us-code-42-9412.-43fc03ac808d8959", "target_family": "temporal", "target_probability": 7.1172298e-05}`
- `program-96009eb287e247a4` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.978735`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-53bddda3326e12f9", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-43-581 to 586.-52ff80bb1c895f8d", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-682d04cd919b16cb", "predicted_family": "frame", "priority": 0.851064907891, "sample_id": "us-code-10-3651-3edc53ba6f53b91a", "target_family": "temporal", "target_probability": 0.148935092109}`
- `program-2b9be4e52ea10c03` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.978384`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.99617655974, "hint_id": "modal-synthesis-3967211653f2b715", "predicted_family": "frame", "priority": 0.998167350922, "sample_id": "us-code-43-620a-aeda7cfe888dd871", "target_family": "deontic", "target_probability": 0.001832649078}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-4bbc832aa3639290", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-22-211-ff9a3da00cebbda3", "target_family": "frame", "target_probability": 0.470915888067}`
- `program-9e2d88e33b05c08d` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.976018`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.544325473206, "hint_id": "modal-synthesis-38c4ec159b0989e8", "predicted_family": "frame", "priority": 0.796079064643, "sample_id": "us-code-38-3562-8a247b2f38b8df8e", "target_family": "deontic", "target_probability": 0.203920935357}`
  evidence: `{"family_margin": -0.963558080623, "hint_id": "modal-synthesis-6be8b321384c7b6e", "predicted_family": "deontic", "priority": 0.982022549658, "sample_id": "us-code-22-7901-56b92850b247621c", "target_family": "conditional_normative", "target_probability": 0.017977450342}`
  evidence: `{"family_margin": -0.450804952557, "hint_id": "modal-synthesis-b41f089710cdbff2", "predicted_family": "deontic", "priority": 0.73764201827, "sample_id": "us-code-7-6414-09089729e9ca74c3", "target_family": "temporal", "target_probability": 0.26235798173}`
- `program-31b9fc5717aaf82c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.973504`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.993949619943, "hint_id": "modal-synthesis-14120230e73e5fde", "predicted_family": "deontic", "priority": 0.999092808015, "sample_id": "us-code-10-134-4e0c9f58edfe6a64", "target_family": "temporal", "target_probability": 0.000907191985}`
  evidence: `{"family_margin": -0.96232754892, "hint_id": "modal-synthesis-922a4a83d821bfbd", "predicted_family": "frame", "priority": 0.999349470969, "sample_id": "us-code-16-590n-59122d4701317a4e", "target_family": "temporal", "target_probability": 0.000650529031}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-eb7b1a9b69b398fd", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-12-639-a6faf86b06383bb9", "target_family": "deontic", "target_probability": 0.49609687163}`
- `program-32d0c9a119961a28` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.973287`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.728111222864, "hint_id": "modal-synthesis-769d226499c59308", "predicted_family": "frame", "priority": 0.918866010745, "sample_id": "us-code-2-396-dfc27b68be30b648", "target_family": "deontic", "target_probability": 0.081133989255}`
  evidence: `{"family_margin": -0.999999582303, "hint_id": "modal-synthesis-7ee98f936a68b71e", "predicted_family": "deontic", "priority": 0.999999944117, "sample_id": "us-code-37-307a-bd64425db76c3290", "target_family": "frame", "target_probability": 5.5883e-08}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-be41096359748097", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-42-5654.-da4eaa98895b187f", "target_family": "temporal", "target_probability": 0.008091643722}`

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

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-dc58403bb8e1ee87`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999964413844`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-18-924-b00c213963a376b4, us-code-42-9412.-43fc03ac808d8959`
  evidence: `{"family_margin": -0.999999999972, "hint_id": "modal-synthesis-badd1e081a72dd05", "predicted_family": "deontic", "priority": 0.999999999986, "sample_id": "us-code-18-924-b00c213963a376b4", "target_family": "conditional_normative", "target_probability": 1.4e-11}`
  evidence: `{"family_margin": -0.999522018876, "hint_id": "modal-synthesis-c019cc9bc722c162", "predicted_family": "frame", "priority": 0.999928827702, "sample_id": "us-code-42-9412.-43fc03ac808d8959", "target_family": "temporal", "target_probability": 7.1172298e-05}`
- `program-96009eb287e247a4`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.978735`
  loss: `autoencoder_residual_cluster` = `0.921486632084`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-43-581 to 586.-52ff80bb1c895f8d, us-code-10-3651-3edc53ba6f53b91a`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-53bddda3326e12f9", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-43-581 to 586.-52ff80bb1c895f8d", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-682d04cd919b16cb", "predicted_family": "frame", "priority": 0.851064907891, "sample_id": "us-code-10-3651-3edc53ba6f53b91a", "target_family": "temporal", "target_probability": 0.148935092109}`
- `program-2b9be4e52ea10c03`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.978384`
  loss: `autoencoder_residual_cluster` = `0.763625731428`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-43-620a-aeda7cfe888dd871, us-code-22-211-ff9a3da00cebbda3`
  evidence: `{"family_margin": -0.99617655974, "hint_id": "modal-synthesis-3967211653f2b715", "predicted_family": "frame", "priority": 0.998167350922, "sample_id": "us-code-43-620a-aeda7cfe888dd871", "target_family": "deontic", "target_probability": 0.001832649078}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-4bbc832aa3639290", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-22-211-ff9a3da00cebbda3", "target_family": "frame", "target_probability": 0.470915888067}`
- `program-9e2d88e33b05c08d`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.976018`
  loss: `autoencoder_residual_cluster` = `0.838581210857`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-7901-56b92850b247621c, us-code-38-3562-8a247b2f38b8df8e, us-code-7-6414-09089729e9ca74c3`
  evidence: `{"family_margin": -0.544325473206, "hint_id": "modal-synthesis-38c4ec159b0989e8", "predicted_family": "frame", "priority": 0.796079064643, "sample_id": "us-code-38-3562-8a247b2f38b8df8e", "target_family": "deontic", "target_probability": 0.203920935357}`
  evidence: `{"family_margin": -0.963558080623, "hint_id": "modal-synthesis-6be8b321384c7b6e", "predicted_family": "deontic", "priority": 0.982022549658, "sample_id": "us-code-22-7901-56b92850b247621c", "target_family": "conditional_normative", "target_probability": 0.017977450342}`
  evidence: `{"family_margin": -0.450804952557, "hint_id": "modal-synthesis-b41f089710cdbff2", "predicted_family": "deontic", "priority": 0.73764201827, "sample_id": "us-code-7-6414-09089729e9ca74c3", "target_family": "temporal", "target_probability": 0.26235798173}`
- `program-31b9fc5717aaf82c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.973504`
  loss: `autoencoder_residual_cluster` = `0.834115135785`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-590n-59122d4701317a4e, us-code-10-134-4e0c9f58edfe6a64, us-code-12-639-a6faf86b06383bb9`
  evidence: `{"family_margin": -0.993949619943, "hint_id": "modal-synthesis-14120230e73e5fde", "predicted_family": "deontic", "priority": 0.999092808015, "sample_id": "us-code-10-134-4e0c9f58edfe6a64", "target_family": "temporal", "target_probability": 0.000907191985}`
  evidence: `{"family_margin": -0.96232754892, "hint_id": "modal-synthesis-922a4a83d821bfbd", "predicted_family": "frame", "priority": 0.999349470969, "sample_id": "us-code-16-590n-59122d4701317a4e", "target_family": "temporal", "target_probability": 0.000650529031}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-eb7b1a9b69b398fd", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-12-639-a6faf86b06383bb9", "target_family": "deontic", "target_probability": 0.49609687163}`
- `program-32d0c9a119961a28`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-dc58403bb8e1ee87` score `0.973287`
  loss: `autoencoder_residual_cluster` = `0.970258103713`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-37-307a-bd64425db76c3290, us-code-42-5654.-da4eaa98895b187f, us-code-2-396-dfc27b68be30b648`
  evidence: `{"family_margin": -0.728111222864, "hint_id": "modal-synthesis-769d226499c59308", "predicted_family": "frame", "priority": 0.918866010745, "sample_id": "us-code-2-396-dfc27b68be30b648", "target_family": "deontic", "target_probability": 0.081133989255}`
  evidence: `{"family_margin": -0.999999582303, "hint_id": "modal-synthesis-7ee98f936a68b71e", "predicted_family": "deontic", "priority": 0.999999944117, "sample_id": "us-code-37-307a-bd64425db76c3290", "target_family": "frame", "target_probability": 5.5883e-08}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-be41096359748097", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-42-5654.-da4eaa98895b187f", "target_family": "temporal", "target_probability": 0.008091643722}`
