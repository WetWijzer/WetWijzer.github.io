# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-ca60bc32beb0e885`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","conditional_normative->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ca60bc32beb0e885` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.145644237353`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-7-7b-3-8ae854fe9f3e72d9, us-code-26-894-74fa7b27a39e8036, us-code-16-8463-6556ccc2ee90b2bd`
  evidence: `{"family_margin": -0.990305853512, "hint_id": "modal-synthesis-207d5cf88db611c2", "predicted_family": "conditional_normative", "priority": 1.140305853512, "sample_id": "us-code-16-8463-6556ccc2ee90b2bd", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999997217738, "hint_id": "modal-synthesis-a7962287383214f6", "predicted_family": "conditional_normative", "priority": 1.149997217738, "sample_id": "us-code-7-7b-3-8ae854fe9f3e72d9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.996629640808, "hint_id": "modal-synthesis-e5a68eb4a4830010", "predicted_family": "conditional_normative", "priority": 1.146629640808, "sample_id": "us-code-26-894-74fa7b27a39e8036", "target_family": "temporal"}`
- `program-6bc69c5543e56f11`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ca60bc32beb0e885` score `0.977347`
  loss: `autoencoder_residual_cluster` = `1.116884575628`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1856e.-b5d3bae319ef5cae, us-code-42-288-8070914136da917f`
  evidence: `{"family_margin": -0.988557778739, "hint_id": "modal-synthesis-5fc7f13b0c374eed", "predicted_family": "frame", "priority": 1.138557778739, "sample_id": "us-code-42-1856e.-b5d3bae319ef5cae", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.945211372516, "hint_id": "modal-synthesis-746b19f514bfc91a", "predicted_family": "conditional_normative", "priority": 1.095211372516, "sample_id": "us-code-42-288-8070914136da917f", "target_family": "deontic"}`
- `program-068e259b4e9df818`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ca60bc32beb0e885` score `0.966543`
  loss: `autoencoder_residual_cluster` = `0.921230461421`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-6-621-3530d5bd78adaaad, us-code-12-1735f-19-cf4e11a49208d46c`
  evidence: `{"family_margin": -0.542828048963, "hint_id": "modal-synthesis-99c982d61777745a", "predicted_family": "frame", "priority": 0.692828048963, "sample_id": "us-code-12-1735f-19-cf4e11a49208d46c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999632873878, "hint_id": "modal-synthesis-9a7c4b3a0e08173a", "predicted_family": "temporal", "priority": 1.149632873878, "sample_id": "us-code-6-621-3530d5bd78adaaad", "target_family": "frame"}`
