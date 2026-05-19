# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary-4codex-gpu-1h-20260519T070521Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary-4codex-gpu-1h-20260519T070521Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-cde7c6fa532afc39`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-cde7c6fa532afc39` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.821465926406`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-1701n-d5261eaa493e6a84, us-code-42-4605.-29cc70ba62a178ae, us-code-18-916-51fd9502f8c0a2b2, us-code-16-1308-abd943b2f56da332`
  evidence: `{"family_margin": -0.960500743312, "hint_id": "modal-synthesis-0c94a6bded7ea7b4", "predicted_family": "frame", "priority": 1.110500743312, "sample_id": "us-code-42-4605.-29cc70ba62a178ae", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.728111222864, "hint_id": "modal-synthesis-55a8dae2765c2465", "predicted_family": "frame", "priority": 0.878111222864, "sample_id": "us-code-18-916-51fd9502f8c0a2b2", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.997251739449, "hint_id": "modal-synthesis-79629f11aa914337", "predicted_family": "frame", "priority": 1.147251739449, "sample_id": "us-code-12-1701n-d5261eaa493e6a84", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-ea877e22f60ae1a9", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-16-1308-abd943b2f56da332", "target_family": "deontic"}`
- `program-59e492f3bb582a6e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-cde7c6fa532afc39` score `0.974758`
  loss: `autoencoder_residual_cluster` = `0.614899328641`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-2219d-4c93c712377e3662, us-code-25-3108-80189a70ec32b32b, us-code-15-1003-94a25e7ba0ef87b3`
  evidence: `{"family_margin": -0.040322877786, "hint_id": "modal-synthesis-1d8155a3588d1710", "predicted_family": "frame", "priority": 0.190322877786, "sample_id": "us-code-15-1003-94a25e7ba0ef87b3", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.646904964415, "hint_id": "modal-synthesis-46993c23ff1fd246", "predicted_family": "deontic", "priority": 0.796904964415, "sample_id": "us-code-25-3108-80189a70ec32b32b", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.707470143722, "hint_id": "modal-synthesis-be043e70cd2175e7", "predicted_family": "frame", "priority": 0.857470143722, "sample_id": "us-code-12-2219d-4c93c712377e3662", "target_family": "temporal"}`
- `program-157d3481feee2e43`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-cde7c6fa532afc39` score `0.938437`
  loss: `autoencoder_residual_cluster` = `0.536867809515`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-7384e.-9dcc1c37a78a0e47, us-code-42-12651c.-6aceb771e77734f8`
  evidence: `{"family_margin": -0.660823382102, "hint_id": "modal-synthesis-063adb80de6a2db3", "predicted_family": "frame", "priority": 0.810823382102, "sample_id": "us-code-42-7384e.-9dcc1c37a78a0e47", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.112912236929, "hint_id": "modal-synthesis-62d89df10991a21d", "predicted_family": "frame", "priority": 0.262912236929, "sample_id": "us-code-42-12651c.-6aceb771e77734f8", "target_family": "deontic"}`
