# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-4df0eae96dd0c894`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-4df0eae96dd0c894` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.545117870471`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-4307-d8adf804365b9891, us-code-46-2104.-968c80c773abaeae`
  evidence: `{"family_margin": 0.296787504955, "hint_id": "modal-synthesis-231ee99eca5ffc3c", "predicted_family": "deontic", "priority": 0.530489080271, "sample_id": "us-code-46-2104.-968c80c773abaeae", "target_family": "deontic", "target_probability": 0.469510919729}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-97a87b2f12d2967e", "predicted_family": "temporal", "priority": 0.559746660672, "sample_id": "us-code-12-4307-d8adf804365b9891", "target_family": "deontic", "target_probability": 0.440253339328}`
