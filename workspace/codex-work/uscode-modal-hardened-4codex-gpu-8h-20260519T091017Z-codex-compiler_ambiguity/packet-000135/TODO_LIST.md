# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-e7832b3b76d0f638`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e7832b3b76d0f638` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.779725597449`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-300j-51e286d3b4f6aa47, us-code-42-8321.-18cda303b32a8b79, us-code-42-5161.-8dac7a75a629d81d, us-code-7-2209c-9e364338270ca36c`
  evidence: `{"family_margin": -0.858265621341, "hint_id": "modal-synthesis-8a93b3095d2e654f", "predicted_family": "frame", "priority": 1.008265621341, "sample_id": "us-code-42-300j-51e286d3b4f6aa47", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.339465897704, "hint_id": "modal-synthesis-c42519d0c121b27b", "predicted_family": "deontic", "priority": 0.489465897704, "sample_id": "us-code-7-2209c-9e364338270ca36c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.8417531115, "hint_id": "modal-synthesis-d7d62e195c47d93a", "predicted_family": "frame", "priority": 0.9917531115, "sample_id": "us-code-42-8321.-18cda303b32a8b79", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.479417759252, "hint_id": "modal-synthesis-efcb4ec9f9213317", "predicted_family": "frame", "priority": 0.629417759252, "sample_id": "us-code-42-5161.-8dac7a75a629d81d", "target_family": "conditional_normative"}`
