# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-744d9df1067481c6`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-744d9df1067481c6` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.896870139912`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-38-8163-dc4c9191b09f4a3d, us-code-26-3305-53aaebf91aa3d889, us-code-10-649j-49b85ae09715be03`
  evidence: `{"family_margin": -0.999909204262, "hint_id": "modal-synthesis-58f49b786e6c6874", "predicted_family": "temporal", "priority": 0.999954602131, "sample_id": "us-code-26-3305-53aaebf91aa3d889", "target_family": "deontic", "target_probability": 4.5397869e-05}`
  evidence: `{"family_margin": -0.999664649245, "hint_id": "modal-synthesis-6fe3fa2934c8cd10", "predicted_family": "deontic", "priority": 0.999999999721, "sample_id": "us-code-38-8163-dc4c9191b09f4a3d", "target_family": "conditional_normative", "target_probability": 2.79e-10}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-e3af8ae656851c9a", "predicted_family": "temporal", "priority": 0.690655817884, "sample_id": "us-code-10-649j-49b85ae09715be03", "target_family": "frame", "target_probability": 0.309344182116}`
