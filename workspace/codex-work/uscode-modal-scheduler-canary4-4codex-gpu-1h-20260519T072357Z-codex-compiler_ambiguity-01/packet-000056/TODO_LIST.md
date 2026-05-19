# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-67b723f029d915e2`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-67b723f029d915e2` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.096532467859`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-8923-4e8593b0f4be2a6e, us-code-42-1320f-07052df5d560afd3, us-code-50-2812.-45bb894590c6de66, us-code-42-18921.-1a6cf6239ba6e28f`
  evidence: `{"family_margin": -0.999983420438, "hint_id": "modal-synthesis-8ef5cadc46ef24ad", "predicted_family": "temporal", "priority": 1.149983420438, "sample_id": "us-code-42-1320f-07052df5d560afd3", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999999928453, "hint_id": "modal-synthesis-cf220b04cda3692c", "predicted_family": "temporal", "priority": 1.149999928453, "sample_id": "us-code-22-8923-4e8593b0f4be2a6e", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-d47612d44edbaeba", "predicted_family": "frame", "priority": 0.982441698483, "sample_id": "us-code-42-18921.-1a6cf6239ba6e28f", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.953704824062, "hint_id": "modal-synthesis-fa7b4aa73bce74ac", "predicted_family": "frame", "priority": 1.103704824062, "sample_id": "us-code-50-2812.-45bb894590c6de66", "target_family": "temporal"}`
- `program-c34efcbaffb2153f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-67b723f029d915e2` score `0.968876`
  loss: `autoencoder_residual_cluster` = `0.857096545244`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-16-410i-fc1cbdffd88df051, us-code-48-2196.-8730b7fd1745de7d, us-code-21-355d-0d0fb4408e391f8e`
  evidence: `{"family_margin": -0.701346671703, "hint_id": "modal-synthesis-4bd5767c317ce846", "predicted_family": "deontic", "priority": 0.851346671703, "sample_id": "us-code-48-2196.-8730b7fd1745de7d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.994891566401, "hint_id": "modal-synthesis-85dc5227265c9cc4", "predicted_family": "temporal", "priority": 1.144891566401, "sample_id": "us-code-16-410i-fc1cbdffd88df051", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.425051397629, "hint_id": "modal-synthesis-ec0f3ea9ad9f44ff", "predicted_family": "frame", "priority": 0.575051397629, "sample_id": "us-code-21-355d-0d0fb4408e391f8e", "target_family": "deontic"}`
- `program-aa947fcba6069fe6`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-67b723f029d915e2` score `0.9603`
  loss: `autoencoder_residual_cluster` = `0.570748049629`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-7-2711-bec4d4accafea1c8, us-code-2-2004-dbec00be9ce2b094, us-code-7-2008h-442c926fd17c2cba`
  evidence: `{"family_margin": -0.797754639875, "hint_id": "modal-synthesis-c150f16e253f1fb7", "predicted_family": "frame", "priority": 0.947754639875, "sample_id": "us-code-7-2711-bec4d4accafea1c8", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.539445116728, "hint_id": "modal-synthesis-dfcd0dfd392cb45a", "predicted_family": "deontic", "priority": 0.689445116728, "sample_id": "us-code-2-2004-dbec00be9ce2b094", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.074955607715, "hint_id": "modal-synthesis-ffbf00960a4806bf", "predicted_family": "deontic", "priority": 0.075044392285, "sample_id": "us-code-7-2008h-442c926fd17c2cba", "target_family": "deontic"}`
- `program-3d95473be1d2f600`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-67b723f029d915e2` score `0.959238`
  loss: `autoencoder_residual_cluster` = `0.814958798268`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-2364-b6943513a5a5417e, us-code-22-10421-88b9bc7813665dc2, us-code-42-5117aa to 5117aa-9b79308d5d7d47fc`
  evidence: `{"family_margin": -0.999456079449, "hint_id": "modal-synthesis-5eeb7f8017a73441", "predicted_family": "frame", "priority": 1.149456079449, "sample_id": "us-code-22-2364-b6943513a5a5417e", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.199221055742, "hint_id": "modal-synthesis-7b213722a6382f37", "predicted_family": "frame", "priority": 0.349221055742, "sample_id": "us-code-42-5117aa to 5117aa-9b79308d5d7d47fc", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.796199259613, "hint_id": "modal-synthesis-d91eee0e79f3794a", "predicted_family": "deontic", "priority": 0.946199259613, "sample_id": "us-code-22-10421-88b9bc7813665dc2", "target_family": "dynamic"}`
- `program-9516fcdfee5b5cea`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-67b723f029d915e2` score `0.950314`
  loss: `autoencoder_residual_cluster` = `0.955309051799`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-18-2232-d79e57e648a5300a, us-code-19-1319-4a008bf97b1ec553`
  evidence: `{"family_margin": -0.927756191866, "hint_id": "modal-synthesis-61d8754576ba5397", "predicted_family": "frame", "priority": 1.077756191866, "sample_id": "us-code-18-2232-d79e57e648a5300a", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.682861911733, "hint_id": "modal-synthesis-f7ee0571861c326a", "predicted_family": "conditional_normative", "priority": 0.832861911733, "sample_id": "us-code-19-1319-4a008bf97b1ec553", "target_family": "deontic"}`
