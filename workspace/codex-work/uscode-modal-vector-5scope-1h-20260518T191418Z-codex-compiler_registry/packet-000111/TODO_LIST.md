# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-cf8b7ab670ac7a3c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["temporal->conditional_normative","temporal->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-cf8b7ab670ac7a3c` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.961510966542`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-7-1631-2e645b217b50b0bc, us-code-31-5312-039372e5e9300b7d, us-code-43-270-9753303f57791aad`
  evidence: `{"family_margin": -0.999999999976, "hint_id": "modal-synthesis-219dd78588234f67", "predicted_family": "temporal", "priority": 0.999999999995, "sample_id": "us-code-31-5312-039372e5e9300b7d", "target_family": "conditional_normative", "target_probability": 5e-12}`
  evidence: `{"family_margin": -0.737725781832, "hint_id": "modal-synthesis-dfc7b4dbba5a2824", "predicted_family": "temporal", "priority": 0.884532899632, "sample_id": "us-code-43-270-9753303f57791aad", "target_family": "conditional_normative", "target_probability": 0.115467100368}`
  evidence: `{"family_margin": -0.999999999986, "hint_id": "modal-synthesis-f55db941552930d4", "predicted_family": "temporal", "priority": 1.0, "sample_id": "us-code-7-1631-2e645b217b50b0bc", "target_family": "epistemic", "target_probability": 0.0}`
