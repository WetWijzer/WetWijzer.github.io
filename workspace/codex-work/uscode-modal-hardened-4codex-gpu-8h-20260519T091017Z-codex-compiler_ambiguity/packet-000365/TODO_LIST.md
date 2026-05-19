# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-b047279a97b0c2b5`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b047279a97b0c2b5` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.952438539201`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-26-755-459e8bff6592359e, us-code-16-1404-2a34b181256a4c20, us-code-36-125-1122a4ae451de969`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-08989bc455e142f6", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-36-125-1122a4ae451de969", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.882186283574, "hint_id": "modal-synthesis-be7917887654674e", "predicted_family": "frame", "priority": 1.032186283574, "sample_id": "us-code-16-1404-2a34b181256a4c20", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.919945361726, "hint_id": "modal-synthesis-dcdcf302d3776aac", "predicted_family": "frame", "priority": 1.069945361726, "sample_id": "us-code-26-755-459e8bff6592359e", "target_family": "dynamic"}`
- `program-708b9ec5789942d1`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->frame","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b047279a97b0c2b5` score `0.982764`
  loss: `autoencoder_residual_cluster` = `0.588420551769`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-1070-3a95d3516d947988, us-code-16-1413-6b0a661df8209521, us-code-12-337-b2cb2b5a46e4a975`
  evidence: `{"family_margin": -0.986259707155, "hint_id": "modal-synthesis-16701cf49050b586", "predicted_family": "frame", "priority": 1.136259707155, "sample_id": "us-code-15-1070-3a95d3516d947988", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-485643ffed0d0aef", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-12-337-b2cb2b5a46e4a975", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.329001948153, "hint_id": "modal-synthesis-7778537a68b485a4", "predicted_family": "alethic", "priority": 0.479001948153, "sample_id": "us-code-16-1413-6b0a661df8209521", "target_family": "frame"}`
- `program-1503c2b979b33ad8`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->frame","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b047279a97b0c2b5` score `0.974282`
  loss: `autoencoder_residual_cluster` = `0.689510706277`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-16-824b-ddf0987a8feb3cf5, us-code-42-300gg-cbf171777bfb8c11, us-code-42-17937.-f79f9efdaaa4d382`
  evidence: `{"family_margin": -0.491677371288, "hint_id": "modal-synthesis-11786c16d4c561ee", "predicted_family": "conditional_normative", "priority": 0.641677371288, "sample_id": "us-code-42-300gg-cbf171777bfb8c11", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999000718287, "hint_id": "modal-synthesis-8a8a84f648c8e04c", "predicted_family": "frame", "priority": 1.149000718287, "sample_id": "us-code-16-824b-ddf0987a8feb3cf5", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.127854029255, "hint_id": "modal-synthesis-d32a3a8db8b1f4de", "predicted_family": "temporal", "priority": 0.277854029255, "sample_id": "us-code-42-17937.-f79f9efdaaa4d382", "target_family": "conditional_normative"}`
