# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-e90be5f04af3c0d7`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e90be5f04af3c0d7` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.721152083382`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1395w-5efce1b44ff160c2, us-code-42-247b-c7ce522c2799052d`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-26dd623398f423c9", "predicted_family": "deontic", "priority": 0.532843141424, "sample_id": "us-code-42-247b-c7ce522c2799052d", "target_family": "deontic", "target_probability": 0.467156858576}`
  evidence: `{"family_margin": -0.812513277874, "hint_id": "modal-synthesis-4cb36802fc545782", "predicted_family": "frame", "priority": 0.90946102534, "sample_id": "us-code-42-1395w-5efce1b44ff160c2", "target_family": "deontic", "target_probability": 0.09053897466}`
