# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-2e29db4d0d826d98`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->dynamic","frame->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2e29db4d0d826d98` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.926902023744`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-5-6339-2bc797bee283b898, us-code-20-80e-6f0a800587a2c144, us-code-16-450cc-1-ea8ceb5d23d67cf1, us-code-20-192-5ed09069c63138ac`
  evidence: `{"family_margin": -0.804383280095, "hint_id": "modal-synthesis-05717597d0f51d1e", "predicted_family": "frame", "priority": 0.962053725409, "sample_id": "us-code-20-80e-6f0a800587a2c144", "target_family": "epistemic", "target_probability": 0.037946274591}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-77553c27a761c011", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-20-192-5ed09069c63138ac", "target_family": "deontic", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.997295894855, "hint_id": "modal-synthesis-bc8a1b0bc8746d05", "predicted_family": "deontic", "priority": 0.99966533223, "sample_id": "us-code-5-6339-2bc797bee283b898", "target_family": "dynamic", "target_probability": 0.00033466777}`
  evidence: `{"family_margin": -0.720554053002, "hint_id": "modal-synthesis-ed485c1475a9c3d5", "predicted_family": "frame", "priority": 0.91970811195, "sample_id": "us-code-16-450cc-1-ea8ceb5d23d67cf1", "target_family": "deontic", "target_probability": 0.08029188805}`
- `program-85c40fddfac6bc98`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["epistemic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2e29db4d0d826d98` score `0.966916`
  loss: `autoencoder_residual_cluster` = `0.875368652943`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-30-22-41b0706c6dfe0563, us-code-10-2452-9f8cf05c0b023e33, us-code-2-1612-e16ee1803f4650eb`
  evidence: `{"family_margin": -0.968177985389, "hint_id": "modal-synthesis-146192c7f5eeb792", "predicted_family": "frame", "priority": 0.999582784843, "sample_id": "us-code-30-22-41b0706c6dfe0563", "target_family": "temporal", "target_probability": 0.000417215157}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-8a7ca58b78c1ef57", "predicted_family": "epistemic", "priority": 0.658902128264, "sample_id": "us-code-2-1612-e16ee1803f4650eb", "target_family": "epistemic", "target_probability": 0.341097871736}`
  evidence: `{"family_margin": -0.845499941677, "hint_id": "modal-synthesis-e031bfb6e7d0b39d", "predicted_family": "frame", "priority": 0.967621045722, "sample_id": "us-code-10-2452-9f8cf05c0b023e33", "target_family": "deontic", "target_probability": 0.032378954278}`
