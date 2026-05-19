# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-21dd5ab24b63f841`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-21dd5ab24b63f841` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.102458143142`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-26-4974-eb27ca6aad760516, us-code-21-1524-aa19993e5da9d029`
  evidence: `{"family_margin": -0.980030610883, "hint_id": "modal-synthesis-0a297800499b7027", "predicted_family": "deontic", "priority": 1.130030610883, "sample_id": "us-code-26-4974-eb27ca6aad760516", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.924885675401, "hint_id": "modal-synthesis-e9080344d115feab", "predicted_family": "frame", "priority": 1.074885675401, "sample_id": "us-code-21-1524-aa19993e5da9d029", "target_family": "deontic"}`
