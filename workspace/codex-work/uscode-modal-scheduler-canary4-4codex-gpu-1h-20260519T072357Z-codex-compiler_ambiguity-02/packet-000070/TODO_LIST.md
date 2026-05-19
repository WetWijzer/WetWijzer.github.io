# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-0b1628e29cafa227`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-0b1628e29cafa227` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.089708362942`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-10222.-4e5a89f05abf6e43, us-code-12-2121-2f87de947818271b`
  evidence: `{"family_margin": -0.879553798991, "hint_id": "modal-synthesis-a0fa104d0e93a15d", "predicted_family": "temporal", "priority": 1.029553798991, "sample_id": "us-code-12-2121-2f87de947818271b", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999862926894, "hint_id": "modal-synthesis-c776e19c9801b5af", "predicted_family": "temporal", "priority": 1.149862926894, "sample_id": "us-code-42-10222.-4e5a89f05abf6e43", "target_family": "deontic"}`
