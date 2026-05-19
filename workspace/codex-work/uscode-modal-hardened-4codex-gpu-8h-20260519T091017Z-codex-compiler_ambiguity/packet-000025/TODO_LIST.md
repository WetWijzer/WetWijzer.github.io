# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-49e63576cd933d22`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-49e63576cd933d22` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.582182344326`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-38-3111-a39382d1145414b0, us-code-12-3763-952bf7bbbbdbbee0`
  evidence: `{"family_margin": 0.108054513434, "hint_id": "modal-synthesis-08d9ab5380c29f98", "predicted_family": "deontic", "priority": 0.041945486566, "sample_id": "us-code-12-3763-952bf7bbbbdbbee0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.972419202086, "hint_id": "modal-synthesis-da6e0d2e77bd9dd4", "predicted_family": "frame", "priority": 1.122419202086, "sample_id": "us-code-38-3111-a39382d1145414b0", "target_family": "deontic"}`
- `program-081fe78a4dd8bed0`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->conditional_normative","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-49e63576cd933d22` score `0.965205`
  loss: `autoencoder_residual_cluster` = `0.333498990636`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-34-10331-66ac454888513d3f, us-code-7-79b-f8a8eb8272722ef1, us-code-38-3232-49b0f29ef7787714`
  evidence: `{"family_margin": -0.720554053002, "hint_id": "modal-synthesis-73a28dd1695817fe", "predicted_family": "frame", "priority": 0.870554053002, "sample_id": "us-code-34-10331-66ac454888513d3f", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.09238532729, "hint_id": "modal-synthesis-bf7dc01300858f7f", "predicted_family": "conditional_normative", "priority": 0.05761467271, "sample_id": "us-code-38-3232-49b0f29ef7787714", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.077671753804, "hint_id": "modal-synthesis-fa5f6ce9e22b8df7", "predicted_family": "deontic", "priority": 0.072328246196, "sample_id": "us-code-7-79b-f8a8eb8272722ef1", "target_family": "deontic"}`
- `program-a5b3e80ceade040c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-49e63576cd933d22` score `0.925956`
  loss: `autoencoder_residual_cluster` = `0.442801918074`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-35-282-92386f3bda95850c, us-code-42-4056.-a21242e6e0739928, us-code-18-3192-36d4a59ee2eb96c4, us-code-26-5207-2d368b5c166dddab`
  evidence: `{"family_margin": -0.202080983098, "hint_id": "modal-synthesis-869f4f47e80f23e2", "predicted_family": "deontic", "priority": 0.352080983098, "sample_id": "us-code-18-3192-36d4a59ee2eb96c4", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.048044090689, "hint_id": "modal-synthesis-ac904df56fa882b0", "predicted_family": "deontic", "priority": 0.101955909311, "sample_id": "us-code-26-5207-2d368b5c166dddab", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.732565725774, "hint_id": "modal-synthesis-e4683356a01e3e31", "predicted_family": "frame", "priority": 0.882565725774, "sample_id": "us-code-35-282-92386f3bda95850c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.284605054113, "hint_id": "modal-synthesis-e5fd30d8d4f7e681", "predicted_family": "frame", "priority": 0.434605054113, "sample_id": "us-code-42-4056.-a21242e6e0739928", "target_family": "conditional_normative"}`
