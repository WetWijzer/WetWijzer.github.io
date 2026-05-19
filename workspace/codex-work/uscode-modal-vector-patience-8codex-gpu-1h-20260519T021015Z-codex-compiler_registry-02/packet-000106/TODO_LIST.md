# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-08816e6669195880`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08816e6669195880` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999963297679`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-5-2105-dc9193f5ddf8bbab, us-code-10-7802-e1bc3255fecd6e31`
  evidence: `{"family_margin": -0.999847673458, "hint_id": "modal-synthesis-11f2d69b3882f645", "predicted_family": "frame", "priority": 0.999932739532, "sample_id": "us-code-10-7802-e1bc3255fecd6e31", "target_family": "deontic", "target_probability": 6.7260468e-05}`
  evidence: `{"family_margin": -0.999987711651, "hint_id": "modal-synthesis-3676b26a9b1ae967", "predicted_family": "temporal", "priority": 0.999993855825, "sample_id": "us-code-5-2105-dc9193f5ddf8bbab", "target_family": "conditional_normative", "target_probability": 6.144175e-06}`
- `program-e4c7ee24abd75db4`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08816e6669195880` score `0.993258`
  loss: `autoencoder_residual_cluster` = `0.872661904609`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-3066-23903d581786c56b, us-code-43-856.-bc45718a44cb6ae5`
  evidence: `{"family_margin": -0.430679318188, "hint_id": "modal-synthesis-1486afaefa3f5660", "predicted_family": "temporal", "priority": 0.749354668684, "sample_id": "us-code-43-856.-bc45718a44cb6ae5", "target_family": "deontic", "target_probability": 0.250645331316}`
  evidence: `{"family_margin": -0.982287931766, "hint_id": "modal-synthesis-55198e0e62e33e9e", "predicted_family": "frame", "priority": 0.995969140535, "sample_id": "us-code-10-3066-23903d581786c56b", "target_family": "conditional_normative", "target_probability": 0.004030859465}`
- `program-e02dede8ab8c4e38`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08816e6669195880` score `0.977737`
  loss: `autoencoder_residual_cluster` = `0.802621674291`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-2376-dbe68d9eaadbdf8f, us-code-42-19136.-5be4eec675d8c9df`
  evidence: `{"family_margin": -0.997701026152, "hint_id": "modal-synthesis-e6d2822abfb0d9b4", "predicted_family": "frame", "priority": 0.999908777611, "sample_id": "us-code-22-2376-dbe68d9eaadbdf8f", "target_family": "epistemic", "target_probability": 9.1222389e-05}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-f9f86e81090f7fb3", "predicted_family": "deontic", "priority": 0.605334570972, "sample_id": "us-code-42-19136.-5be4eec675d8c9df", "target_family": "deontic", "target_probability": 0.394665429028}`
- `program-0a2afa3ff8ded8c5`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08816e6669195880` score `0.97529`
  loss: `autoencoder_residual_cluster` = `0.814666354433`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-7-1727a-69bf4e9f23589220, us-code-25-161b-04160365a0fa3962, us-code-2-172-13938aa8cbbab9bb`
  evidence: `{"family_margin": -0.957002846935, "hint_id": "modal-synthesis-4d49977073fa09a0", "predicted_family": "frame", "priority": 0.996472346507, "sample_id": "us-code-7-1727a-69bf4e9f23589220", "target_family": "deontic", "target_probability": 0.003527653493}`
  evidence: `{"family_margin": -0.390318016707, "hint_id": "modal-synthesis-a4d26afb6c818ae1", "predicted_family": "deontic", "priority": 0.772844006005, "sample_id": "us-code-25-161b-04160365a0fa3962", "target_family": "temporal", "target_probability": 0.227155993995}`
  evidence: `{"family_margin": 0.240981950365, "hint_id": "modal-synthesis-ddcc083227796bd6", "predicted_family": "frame", "priority": 0.674682710787, "sample_id": "us-code-2-172-13938aa8cbbab9bb", "target_family": "frame", "target_probability": 0.325317289213}`
- `program-baf6edd307366154`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->dynamic","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08816e6669195880` score `0.967196`
  loss: `autoencoder_residual_cluster` = `0.911140921998`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-31-3512-072f35dad3173e73, us-code-22-286n-402424f4edc189eb, us-code-15-1693e-b7074521c1c5667d`
  evidence: `{"family_margin": -0.988612205682, "hint_id": "modal-synthesis-729c24e7780ddf8b", "predicted_family": "frame", "priority": 0.995943188613, "sample_id": "us-code-22-286n-402424f4edc189eb", "target_family": "deontic", "target_probability": 0.004056811387}`
  evidence: `{"family_margin": -0.99999999959, "hint_id": "modal-synthesis-a7272f120c1668d6", "predicted_family": "temporal", "priority": 0.999999999995, "sample_id": "us-code-31-3512-072f35dad3173e73", "target_family": "deontic", "target_probability": 5e-12}`
  evidence: `{"family_margin": -0.220358909223, "hint_id": "modal-synthesis-fbaaaba1108f1b63", "predicted_family": "deontic", "priority": 0.737479577385, "sample_id": "us-code-15-1693e-b7074521c1c5667d", "target_family": "dynamic", "target_probability": 0.262520422615}`
- `program-5453b5815f408141`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->dynamic","deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-08816e6669195880` score `0.963774`
  loss: `autoencoder_residual_cluster` = `0.889777727303`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-5-6336-01b727a3a3d92fa6, us-code-34-40916-38292e1c50f1b0a2, us-code-10-20217-43a61c94da6a8a5f`
  evidence: `{"family_margin": -0.435322306111, "hint_id": "modal-synthesis-229dc71ec5760927", "predicted_family": "deontic", "priority": 0.901878494309, "sample_id": "us-code-34-40916-38292e1c50f1b0a2", "target_family": "conditional_normative", "target_probability": 0.098121505691}`
  evidence: `{"family_margin": -0.929753832998, "hint_id": "modal-synthesis-e260de2a317690f5", "predicted_family": "conditional_normative", "priority": 0.999151400425, "sample_id": "us-code-5-6336-01b727a3a3d92fa6", "target_family": "dynamic", "target_probability": 0.000848599575}`
  evidence: `{"family_margin": -0.39812025136, "hint_id": "modal-synthesis-f8c7c8cb6ea0c020", "predicted_family": "deontic", "priority": 0.768303287176, "sample_id": "us-code-10-20217-43a61c94da6a8a5f", "target_family": "temporal", "target_probability": 0.231696712824}`
